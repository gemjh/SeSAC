# ===== inference.py =====
import os
import numpy as np
import librosa
import torch
import tensorflow as tf
from transformers import WhisperProcessor, WhisperForConditionalGeneration

# MPS dtype 호환성 문제 해결을 위한 환경 변수 설정
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

# torch dtype을 float32로 설정
torch.set_default_dtype(torch.float32)


# =========================
# 고정 파라미터 (학습 때와 동일)
# =========================
SAMPLE_RATE = 16000
N_MELS = 128
MAX_TOKEN_LENGTH = 256
NUM_PROMPTS = 5
THRESHOLD_INIT = 0.50

# 문항별 정답 사전 (학습 때 사용한 것과 동일해야 함)
PROMPT_ANSWERS = {
    0: {"덥다": 2, "뜨겁다": 2, "뜨거워": 2, "곱다": 1, "따뜻하다": 1, "섭다": 1},
    1: {"작다": 2, "조그맣다": 2, "짝다": 2, "쪼그마해요": 2, "작습(니다)": 2, "적다": 1},
    2: {"곱다": 2, "오는 말이 곱다": 2, "돕다": 1, "봅다": 1, "겁다": 1, "좋다": 1, "홉다": 1},
    3: {"달다": 2, "달달하다": 2, "달라": 1, "달음니다": 1},
    4: {"지운다": 2, "지우다": 2, "지워": 2, "지웠다": 2, "지우다딴다": 1}
}
# 전역 어휘/인덱스/가중치
all_words = sorted({w for mp in PROMPT_ANSWERS.values() for w in mp.keys()})
WORD2IDX = {w: i for i, w in enumerate(all_words)}
idx2word = all_words
NUM_LABELS = len(all_words)
WORD_WEIGHTS = np.zeros(NUM_LABELS, dtype=np.int32)
for pid in range(NUM_PROMPTS):
    for w, sc in PROMPT_ANSWERS[pid].items():
        WORD_WEIGHTS[WORD2IDX[w]] = int(sc)

# 문항별 후보 마스크 (PxM)
PROMPT_MASKS = np.zeros((NUM_PROMPTS, NUM_LABELS), dtype=np.int32)
for pid in range(NUM_PROMPTS):
    for w in PROMPT_ANSWERS[pid].keys():
        PROMPT_MASKS[pid, WORD2IDX[w]] = 1
PROMPT_MASKS_BOOL = PROMPT_MASKS.astype(bool)

# === 네가 방금 튜닝해서 출력한 임계값 그대로 사용 (원하면 바꿔도 됨) ===
THR_BY_PROMPT_DEFAULT = {0: 0.20, 1: 0.08, 2: 0.48, 3: 0.58, 4: 0.32}

# =========================
# Whisper 준비 (토큰 추출용)
# =========================
def _pick_device():
    # MPS의 torch.isin Long dtype 호환성 문제로 CPU 사용 강제
    return torch.device("cpu")

_device = _pick_device()
processor = WhisperProcessor.from_pretrained("openai/whisper-small")
whisper_model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-small").to(_device)
whisper_model.eval()
forced_ids = processor.get_decoder_prompt_ids(language="ko", task="transcribe")

# PAD_ID (학습 때와 동일 로직)
_vocab_ids = list(processor.tokenizer.get_vocab().values())
BASE_VOCAB = max(_vocab_ids) + 1
PAD_ID = BASE_VOCAB  # 패딩 토큰ID

# =========================
# 커스텀 레이어 (저장된 모델 로드시 필요)
# =========================
@tf.keras.utils.register_keras_serializable()
class BuildCrossAttnMask(tf.keras.layers.Layer):
    def call(self, inputs):
        q, token_mask = inputs          # q: (B,T,256), token_mask: (B,L) 0/1
        m = tf.cast(token_mask, tf.bool)  # (B,L)
        m = tf.expand_dims(m, axis=1)     # (B,1,L)
        T = tf.shape(q)[1]                # 동적 T
        m = tf.tile(m, [1, T, 1])         # (B,T,L)
        return m

# =========================
# 전처리 유틸
# =========================
def _load_wav_to_mel(wav_path: str):
    y, sr = librosa.load(wav_path, sr=SAMPLE_RATE, mono=True)
    mel = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=N_MELS)
    mel_db = librosa.power_to_db(mel, ref=np.max)          # (128, T)
    mel_db = np.expand_dims(mel_db, axis=-1)               # (128, T, 1)
    return mel_db

@torch.no_grad()
def _extract_token_ids_and_mask_from_wav(wav_path: str):
    speech_array, _ = librosa.load(wav_path, sr=SAMPLE_RATE, mono=True)
    inputs = processor(speech_array, sampling_rate=SAMPLE_RATE, return_tensors="pt")
    input_features = inputs.input_features.to(_device)
    pred = whisper_model.generate(
        input_features,
        forced_decoder_ids=forced_ids,
        do_sample=False,
        max_new_tokens=MAX_TOKEN_LENGTH
    )
    token_ids = pred[0].cpu().numpy().astype(np.int32)
    L = token_ids.shape[0]
    if L < MAX_TOKEN_LENGTH:
        pad_len = MAX_TOKEN_LENGTH - L
        mask = np.concatenate([np.ones(L, np.int32), np.zeros(pad_len, np.int32)], axis=0)
        token_ids = np.concatenate([token_ids, np.full(pad_len, PAD_ID, np.int32)], axis=0)
    else:
        token_ids = token_ids[:MAX_TOKEN_LENGTH]
        mask = np.ones(MAX_TOKEN_LENGTH, np.int32)
    if mask.sum() == 0:
        mask[0] = 1
    return token_ids, mask

def _pad_mel_batch(mel_list):
    max_t = max(m.shape[1] for m in mel_list)
    out = []
    for m in mel_list:
        pad_t = max_t - m.shape[1]
        if pad_t > 0:
            m = np.pad(m, ((0,0),(0,pad_t),(0,0)), mode='constant', constant_values=0.0)
        out.append(m)
    return np.stack(out, axis=0)

# =========================
# 선택 규칙 (임계값 넘는 후보들 중 Top-1, 없으면 0점)
# =========================
def _pick_one_above_threshold(probs, pid, thresholds_by_prompt):
    """
    probs: (M,) 시그모이드 확률
    pid:   문항 ID (0~4)
    반환: (best_word|None, score(int:0/1/2), conf(float))
    """
    mask = PROMPT_MASKS_BOOL[pid]
    t = float(thresholds_by_prompt.get(pid, THRESHOLD_INIT))
    valid_idx = np.where(mask & (probs > t))[0]
    if valid_idx.size == 0:
        return None, 0, 0.0
    best_idx = valid_idx[int(np.argmax(probs[valid_idx]))]
    best_word = idx2word[best_idx]
    score = int(WORD_WEIGHTS[best_idx])   # 1 또는 2
    conf = float(probs[best_idx])
    return best_word, score, conf

# =========================
# 추론 클래스
# =========================
class GuessEndInferencer:

    def __init__(self, model_path: str, thresholds_by_prompt=None):
        # compile=False로 로드 (커스텀 로스 필요 없음)
        self.model = tf.keras.models.load_model(model_path, compile=False)
        self.thresholds = thresholds_by_prompt or THR_BY_PROMPT_DEFAULT
        print('-----------------\n\n\n 시작 -----------------\n\n\n')
    def predict(self, wav_path: str, prompt_id: int):
        """
        반환: (best_word | None, score:int(0/1/2), conf:float, probs:np.ndarray(M,))
        """
        print('-----------------predict:\n\n\n', wav_path,prompt_id, '-----------------\n\n\n')
        mel = _load_wav_to_mel(wav_path)
        tok_ids, tok_msk = _extract_token_ids_and_mask_from_wav(wav_path)
        # 배치화
        mel_b = _pad_mel_batch([mel])         # (1,128,T,1)
        tok_b = np.expand_dims(tok_ids, 0)    # (1,L)
        msk_b = np.expand_dims(tok_msk, 0)    # (1,L)
        pid_b = np.array([prompt_id], dtype=np.int32)  # (1,)

        probs = self.model.predict([mel_b, tok_b, msk_b, pid_b], verbose=0)[0].astype('float')  # (M,)
        best_word, score, conf = _pick_one_above_threshold(probs, prompt_id, self.thresholds)
        return best_word, score, conf, probs

    def predict_guess_end(self, wav_path: str, prompt_id: int) -> int:
        """
        점수만 반환(0/1/2)
        """
        _, score, _, _ = self.predict(wav_path, prompt_id)
        return score

# =========================
# 사용 예시
# =========================
# infer = GuessEndInferencer("guess_end_model.keras")  # 경로 맞춰서
# s = infer.predict_guess_end("/path/to/p_1_1.wav", prompt_id=0)
# print("score =", s)
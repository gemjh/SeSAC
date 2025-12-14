import os
import numpy as np
import tensorflow as tf
import librosa
import torch
from transformers import WhisperProcessor, WhisperForConditionalGeneration

# =========================================================
# Config
# =========================================================
SAMPLE_RATE = 16000
N_MELS = 128
MAX_TOKEN_LENGTH = 256
NUM_PROMPTS = 5
MODEL_PATH = os.path.join(os.path.dirname(__file__), "guess_end_model.keras")  # 재헌님 여기 수정해주세요

# ---------------------------------------------------------
# 문항별 정답 후보
# ---------------------------------------------------------
PROMPT_ANSWERS = {
    0: {"덥다", "뜨겁다", "뜨거워", "곱다", "따뜻하다", "섭다"},
    1: {"작다", "조그맣다", "짝다", "쪼그마해요", "작습(니다)", "적다"},
    2: {"곱다", "오는 말이 곱다", "돕다", "봅다", "겁다", "좋다", "홉다"},
    3: {"달다", "달달하다", "달라", "달음니다"},
    4: {"지운다", "지우다", "지워", "지웠다", "지우다딴다"},
}

# =========================================================
# 커스텀 레이어 (저장된 모델 로드시 필요)
# =========================================================
@tf.keras.utils.register_keras_serializable()
class BuildCrossAttnMask(tf.keras.layers.Layer):
    def call(self, inputs):
        q, token_mask = inputs              # q: (B,T,256), token_mask: (B,L) 0/1
        m = tf.cast(token_mask, tf.bool)    # (B,L) -> bool
        m = tf.expand_dims(m, axis=1)       # (B,1,L)
        T = tf.shape(q)[1]                  # 동적 T
        m = tf.tile(m, [1, T, 1])           # (B,T,L)
        return m

# =========================================================
# Whisper
# =========================================================
device = torch.device ("cuda" if torch.cuda.is_available() else "cpu")

processor = WhisperProcessor.from_pretrained("openai/whisper-small")
whisper_model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-small").to(device)
whisper_model.eval()
forced_ids = processor.get_decoder_prompt_ids(language="ko", task="transcribe")

# PAD_ID 계산 
_vocab_ids = list(processor.tokenizer.get_vocab().values())
BASE_VOCAB = max(_vocab_ids) + 1
PAD_ID     = BASE_VOCAB

# =========================================================
# 전처리 유틸
# =========================================================
def wav_to_mel(wav_path: str, sr=SAMPLE_RATE, n_mels=N_MELS):
    y, _ = librosa.load(wav_path, sr=sr, mono=True)
    mel = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=n_mels)
    mel_db = librosa.power_to_db(mel, ref=np.max)
    mel_db = np.expand_dims(mel_db, axis=-1)  # (128, T, 1)
    return mel_db

@torch.no_grad()
def wav_to_tokens_and_mask(wav_path: str, sr=SAMPLE_RATE):
    if not os.path.exists(wav_path):
        raise FileNotFoundError(f"WAV not found: {wav_path}")
    y, _ = librosa.load(wav_path, sr=sr, mono=True)
    inputs = processor(y, sampling_rate=sr, return_tensors="pt")
    input_features = inputs.input_features.to(device)
    pred_ids = whisper_model.generate(
        input_features,
        forced_decoder_ids=forced_ids,
        do_sample=False,
        max_new_tokens=MAX_TOKEN_LENGTH,
    )
    token_ids = pred_ids[0].cpu().numpy().astype(np.int32)
    token_len = token_ids.shape[0]
    if token_len < MAX_TOKEN_LENGTH: 
        pad_len = MAX_TOKEN_LENGTH - token_len         
        token_mask = np.concatenate(
            [np.ones(token_len, np.int32), np.zeros(pad_len, np.int32)], axis=0)
        token_ids = np.concatenate([token_ids, np.full(pad_len, PAD_ID, np.int32)], axis=0)
    else:
        token_ids  = token_ids[:MAX_TOKEN_LENGTH]
        token_mask = np.ones(MAX_TOKEN_LENGTH, np.int32)

    if token_mask.sum() == 0:
        token_mask[0] = 1
    return token_ids, token_mask

def pad_mels(mel_list):
    max_time = max(m.shape[1] for m in mel_list)
    batch = np.zeros((len(mel_list), N_MELS, max_time, 1), dtype=np.float32)
    for i, mel in enumerate(mel_list):
        batch[i, :, :mel.shape[1], :] = mel
    return batch

# 문항별 단어 마스크 생성 (NUM_LABELS = 전체 단어 수)
all_words  = sorted({w for ws_set in PROMPT_ANSWERS.values() for w in ws_set})
WORD2IDX   = {w: i for i, w in enumerate(all_words)}
NUM_LABELS = len(all_words)

PROMPT_MASKS = np.zeros((NUM_PROMPTS, NUM_LABELS), dtype=np.float32)
for pid in range(NUM_PROMPTS):
    for w in PROMPT_ANSWERS[pid]:
        PROMPT_MASKS[pid, WORD2IDX[w]] = 1.0

# =========================================================
# 모델 로딩 (한 번만 로드해서 캐시)
# =========================================================
_MODEL = None
def _load_model(model_path=MODEL_PATH):
    global _MODEL
    if _MODEL is None:
        _MODEL = tf.keras.models.load_model(model_path, custom_objects={"BuildCrossAttnMask": BuildCrossAttnMask})
    return _MODEL

# =========================================================
#  wav_path: 파일 경로 # prompt_id: 0~4 (0=1번 문항)
# =========================================================
def predict_guess_end_score(wav_path: str, prompt_id: int, model_path: str = MODEL_PATH, return_probs: bool = False):
    if not (0 <= int(prompt_id) <= 4):
        raise ValueError(f"prompt_id must be in 0..4, got {prompt_id}") 

    model = _load_model(model_path)

    # 전처리
    mel = wav_to_mel(wav_path)
    tok_ids, tok_msk = wav_to_tokens_and_mask(wav_path)

    mel_b = pad_mels([mel])                            
    tok_b = tok_ids[None, :].astype(np.int32)           
    msk_b = tok_msk[None, :].astype(np.int32)          
    pid_b = np.array([prompt_id], dtype=np.int32)       
    sw_b = PROMPT_MASKS[prompt_id][None, :].astype(np.float32)  

    # 예측
    probs = model.predict([mel_b, tok_b, msk_b, pid_b, sw_b], verbose=0)[0] 
    score = int(np.argmax(probs))  # 0/1/2

    return score

# =========================================================
# 사용 예시
# =========================================================
# pred_score = predict_guess_end_score(wav_path, prompt_id)
# print(f"Predicted score = {pred_score}")
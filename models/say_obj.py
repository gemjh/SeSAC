import numpy as np
import librosa
import tensorflow as tf
import torch
import os
from transformers import WhisperProcessor, WhisperForConditionalGeneration

# ====== 하이퍼파라미터 ======
SAMPLE_RATE = 16000
N_MELS = 128
MAX_TOKEN_LENGTH = 512
TEMPERATURE = 0
MODEL_PATH = os.path.join(os.path.dirname(__file__), "say_obj_model.keras")  # 재헌님 여기 수정해주세요

# ====== 전역 캐시 ======
_MODEL = None
_WHISPER = None
_PROCESSOR = None

# ====== 디바이스 ======
_DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def _load_model(model_path=MODEL_PATH):
    global _MODEL
    if _MODEL is None:
        _MODEL = tf.keras.models.load_model(model_path)
    return _MODEL

def _load_whisper():
    global _WHISPER, _PROCESSOR
    if _WHISPER is None or _PROCESSOR is None:
        _PROCESSOR = WhisperProcessor.from_pretrained("openai/whisper-small")
        _WHISPER = WhisperForConditionalGeneration.from_pretrained(
            "openai/whisper-small"
        ).to(_DEVICE)
    return _WHISPER, _PROCESSOR

# ====== 전처리 ======
def _wav_to_mel(wav_path, sr=SAMPLE_RATE, n_mels=N_MELS):
    y, _ = librosa.load(wav_path, sr=sr)
    mel = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=n_mels)
    mel_db = librosa.power_to_db(mel, ref=np.max)
    mel_db = mel_db[..., np.newaxis]  # (128, T, 1)
    return mel_db.astype(np.float32)

def _wav_to_token_ids(wav_path, sr=SAMPLE_RATE):
    whisper, processor = _load_whisper()
    y, _ = librosa.load(wav_path, sr=sr)
    inputs = processor(y, sampling_rate=sr, return_tensors="pt")
    input_features = inputs.input_features.to(_DEVICE)

    forced_ids = processor.get_decoder_prompt_ids(language="ko", task="transcribe")

    with torch.no_grad():
        pred_ids = whisper.generate(
            input_features,
            forced_decoder_ids=forced_ids,
            temperature=TEMPERATURE
        )
    token_ids = pred_ids[0].cpu().tolist()
    if len(token_ids) < MAX_TOKEN_LENGTH:
        token_ids += [0] * (MAX_TOKEN_LENGTH - len(token_ids))
    else:
        token_ids = token_ids[:MAX_TOKEN_LENGTH]
    return np.array(token_ids, dtype=np.int32)

# =========================================================
#  예측함수 # rainbow_wav: 무지개(6) 파일 경로 # swing_wav: 그네(9) 파일 경로
# =========================================================
def predict_say_object_total(rainbow_wav, swing_wav, model_path=MODEL_PATH):
    model = _load_model(model_path)

    mel_r = _wav_to_mel(rainbow_wav)[np.newaxis, ...]
    mel_s = _wav_to_mel(swing_wav)[np.newaxis, ...]
    tok_r = _wav_to_token_ids(rainbow_wav)[np.newaxis, :]
    tok_s = _wav_to_token_ids(swing_wav)[np.newaxis, :]

    y_hat = model.predict(
        {"mel_rainbow": mel_r, "tok_rainbow": tok_r,
         "mel_swing": mel_s,   "tok_swing": tok_s},
        verbose=0
    )
    score = float(y_hat[0, 0] * 20.0)
    return max(0.0, min(20.0, score))

# =========================================================
# 사용 예시
# =========================================================
# predict_say_object_total(rainbow_wav, swing_wav)
# print(f"예측 총점: {score:.2f}")

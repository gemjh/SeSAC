# ========== 라이브러리 Import ==========
import numpy as np
import librosa
import tensorflow as tf
from tensorflow.keras.models import load_model
from transformers import WhisperProcessor, WhisperForConditionalGeneration
import torch
import os
# ========== 하이퍼파라미터 설정 ==========
SAMPLE_RATE   = 16000    # librosa.load
N_MELS        = 128      # mel-spectrogram
TOKEN_SEQ_LEN = 512      # Whisper 토큰 길이
TEMPERATURE = 0
MODEL_PATH = os.path.join(os.path.dirname(__file__), "say_obj_model.keras")

# 저장된 Keras 모델 불러오기
model = load_model(MODEL_PATH)

# 저장된 가중치 불러오기
W_PATH = os.path.join(os.path.dirname(__file__), "say_obj_weights.npy")

w = np.load(W_PATH)     # [w_r, w_s, w_rs, b]

# ========== Whisper 모델 초기화 ==========
device = "cuda" if torch.cuda.is_available() else "cpu"  
processor = WhisperProcessor.from_pretrained("openai/whisper-base") 
whisper_model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-base").to(device)

# ========== 오디오 파일을 Mel-Spectrogram으로 변환 ==========
def wav_to_mel(wav_path, sr=SAMPLE_RATE, n_mels=N_MELS):
    y, _ = librosa.load(wav_path, sr=sr)                                          # 오디오 파일 로드 (sr로 리샘플링)
    mel = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=n_mels)               # Mel-Spectrogram 추출
    mel_db = librosa.power_to_db(mel, ref=np.max)                                 # dB 단위로 변환 (정규화 효과)
    mel_db = mel_db[..., np.newaxis]                                              # 차원 추가 → (n_mels, time, 1)
    return mel_db.astype(np.float32)                                              # float32로 캐스팅해서 반환

# ========== 오디오 파일을 Whisper Token ID로 변환 ==========
def wav_to_token_ids(wav_path, sr=SAMPLE_RATE, seq_len=TOKEN_SEQ_LEN):
    y, _ = librosa.load(wav_path, sr=sr)                                          # 오디오 로드
    inputs = processor(y, sampling_rate=sr, return_tensors="pt")                  # Whisper Processor로 전처리
    input_features = inputs.input_features.to(device)                             # Whisper 입력 포맷 (Device 할당)
    pred_ids = whisper_model.generate(input_features, temperature=TEMPERATURE)    # Whisper로 Token ID 예측
    token_ids = pred_ids[0].cpu().tolist()                                        # 결과를 CPU로 옮기고 list로 변환

    if len(token_ids) < seq_len:                        # Token이 부족하면
        token_ids += [0] * (seq_len - len(token_ids))   # Padding
    else:                                               # 넘치면 자르기
        print(f"Token sequence length {len(token_ids)} exceeds allowed maximum {seq_len}.")  
        token_ids = token_ids[:seq_len]                 

    return np.array(token_ids, dtype=np.int32)          # numpy array로 반환

# ========== 변환된 Mel-Spectrogram, Whisper Token ID로 점수 예측(0~1) ==========
def predict_score(wav_path):
    mel = wav_to_mel(wav_path)                          # (128, time, 1)
    token_ids = wav_to_token_ids(wav_path)              # (TOKEN_SEQ_LEN,)

    mel_in = mel[np.newaxis, ...]                       # (1, 128, time, 1)
    token_in = token_ids[np.newaxis, :]                 # (1, TOKEN_SEQ_LEN)

    pred = model.predict({'mel_input': mel_in, 'token_input': token_in}, verbose=0)

    return float(pred[0, 0])

# ========== total 점수 예측 ==========
def predict_total_say_obj(rainbow_wav_path, swing_wav_path):
    # 무지개, 그네 음성파일에 대한 점수 예측(0~1)
    r_pred = predict_score(rainbow_wav_path)
    s_pred = predict_score(swing_wav_path)
    # 상호작용 결합(0~1)
    fused = w[0]*r_pred + w[1]*s_pred + w[2]*(r_pred*s_pred) + w[3]
    fused = float(np.clip(fused, 0.0, 1.0))
    # 총점(0~20)
    total_score_pred = round(fused * 20.0)
    return total_score_pred

# 사용 예:
say_obj_score = predict_total_say_obj(
    "/Volumes/SSAM/project/files/upload/1001/CLAP_A/5/p_6_0.wav", "/Volumes/SSAM/project/files/upload/1001/CLAP_A/5/p_9_0.wav"
)
print(say_obj_score)
import numpy as np
import librosa
import tensorflow as tf
from tensorflow.keras.layers import (
    Input, Permute, Reshape, Bidirectional, LSTM,
    Dropout, Embedding, Dense, MultiHeadAttention
)
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from transformers import WhisperProcessor, WhisperForConditionalGeneration
from tensorflow.keras.models import load_model
import torch
import os

# ========== 설정 ==========
SAMPLE_RATE = 16000
N_MELS = 128
TOKEN_SEQ_LEN = 128
VOCAB_SIZE = 51865
EMBED_DIM = 64
LSTM_UNITS = 64
DROPOUT = 0.3
LR = 1e-4
EPOCHS = 30
BATCH_SIZE = 2
TEMPERATURE = 0

# ===== Whisper 초기화 =====
device = "cuda" if torch.cuda.is_available() else "cpu"
processor = WhisperProcessor.from_pretrained("openai/whisper-base")
whisper_model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-base").to(device)


# ========== 함수 정의 ==========
def wav_to_mel(wav_path, sr=SAMPLE_RATE, n_mels=N_MELS):
    y, _ = librosa.load(wav_path, sr=sr)
    mel = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=n_mels)
    mel_db = librosa.power_to_db(mel, ref=np.max)
    mel_db = mel_db[..., np.newaxis]  # (n_mels, time, 1)
    return mel_db.astype(np.float32)

def wav_to_token_ids(wav_path, sr=SAMPLE_RATE, seq_len=TOKEN_SEQ_LEN):
    y, _ = librosa.load(wav_path, sr=sr)
    inputs = processor(y, sampling_rate=sr, return_tensors="pt")
    input_features = inputs.input_features.to(device)
    pred_ids = whisper_model.generate(input_features, temperature=TEMPERATURE)
    token_ids = pred_ids[0].cpu().tolist()
    if len(token_ids) < seq_len:
        token_ids += [0] * (seq_len - len(token_ids))
    else:
        token_ids = token_ids[:seq_len]
    return np.array(token_ids, dtype=np.int32)

def prepare_wave(wav_path):
    # wave 파일을 변환

    mel_list, token_list, label_list = [], [], []

    wav_src = wav_path
    
    mel_list, token_list, label_list = [], [], []

    for path in wav_src:
        mel = wav_to_mel(path)  # (128, time, 1)
        token_ids = wav_to_token_ids(path)  # (128,)
        mel_list.append(mel)
        token_list.append(token_ids)
        #label_list.append([label])
        

    # 패딩을 위해 최대 time 계산
    #max_time = max(m.shape[1] for m in mel_list)
    max_time = 473

    # mel padding (batch, 128, max_time, 1)
    mel_batch = np.zeros((len(mel_list), N_MELS, max_time, 1), dtype=np.float32)
    for i, mel in enumerate(mel_list):
        mel_batch[i, :, :mel.shape[1], :] = mel

    token_batch = np.stack(token_list)  # (batch, 128)
    #label_batch = np.array(label_list, dtype=np.float32)  # (batch, 1)

    return mel_batch, token_batch

def predict_score(wav_path):
    mel_batch, token_batch = prepare_wave(wav_path)
    model_path = os.path.join(os.path.dirname(__file__), 'model_ltn_rpt.keras')
    print(f"모델 경로: {model_path}")
    print(f"파일 존재 여부: {os.path.exists(model_path)}")
    model = load_model(model_path)

    # ========== 예측 ==========
    preds = model.predict({'mel_input': mel_batch, 'token_input': token_batch})

    point = [2.0, 2.0, 2.0, 4.0, 6.0, 8.0, 8.0, 10.0, 14.0, 12.0]
    score = 0.0
    for i, p in enumerate(preds):
        # print(f"[{i}] Predicted: {p[0]:.4f}, score : {p[0]*point[i%10]:.1f} ({point[i%10]:.1f})")
        score += p[0]*point[i]

    return int(score)

# 사용 예 :
# wav_path = []
# wav_path.append(r'C:\Users\joon0\edu\31_Project\Data\clap_data\4053\CLAP_A\3\p_1_0.wav')
# wav_path.append(r'C:\Users\joon0\edu\31_Project\Data\clap_data\4053\CLAP_A\3\p_2_0.wav')
# wav_path.append(r'C:\Users\joon0\edu\31_Project\Data\clap_data\4053\CLAP_A\3\p_3_0.wav')
# wav_path.append(r'C:\Users\joon0\edu\31_Project\Data\clap_data\4053\CLAP_A\3\p_4_0.wav')
# wav_path.append(r'C:\Users\joon0\edu\31_Project\Data\clap_data\4053\CLAP_A\3\p_5_0.wav')
# wav_path.append(r'C:\Users\joon0\edu\31_Project\Data\clap_data\4053\CLAP_A\3\p_6_0.wav')
# wav_path.append(r'C:\Users\joon0\edu\31_Project\Data\clap_data\4053\CLAP_A\3\p_7_0.wav')
# wav_path.append(r'C:\Users\joon0\edu\31_Project\Data\clap_data\4053\CLAP_A\3\p_8_0.wav')
# wav_path.append(r'C:\Users\joon0\edu\31_Project\Data\clap_data\4053\CLAP_A\3\p_9_1.wav')
# wav_path.append(r'C:\Users\joon0\edu\31_Project\Data\clap_data\4053\CLAP_A\3\p_10_1.wav')

# score = predict_score(wav_path)
# print(score)
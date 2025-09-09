# 데이터를 60개의 블럭으로 구분하여 train/test로 분리

import numpy as np
import librosa
import tensorflow as tf
from tensorflow.keras.layers import (
    Input, Permute, Reshape, Bidirectional, LSTM,
    Dropout, Embedding, Dense, MultiHeadAttention, GlobalAveragePooling1D
)
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping
from transformers import WhisperProcessor, WhisperForConditionalGeneration
import torch
import random
from tqdm import tqdm
from dotenv import load_dotenv
from pathlib import Path
import os
import sys

root_path = Path(__file__).parent.parent
db_path = os.path.join(root_path, 'db', 'src')
sys.path.append(db_path)

import model_comm as mc

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
BATCH_SIZE = 4
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

# ========== 환경설정정보 불러오기 ==========
env_path = r"..\.env"
load_dotenv(dotenv_path=env_path)

# ========== base_path 지정==========
base_path = os.getenv("base_path")
base_path += r"\files\upload" # upload 폴더 지정

# ========== 데이터 준비 ==========
msg, ret = mc.get_file_lst('CLAP_A', 'LTN_RPT')

wav_label_pairs = []
for i in range(len(ret)):
    t = (os.path.join(base_path, f"{ret.loc[i, 'Path']}".replace('/', '\\'), f"{ret.loc[i, 'File Name']}"), int(ret.loc[i, 'Score(Refer)'])/int(ret.loc[i, 'Score(Alloc)']))
    wav_label_pairs.append(t)
print(len(wav_label_pairs))

# bloack으로 나누어 train/test로 데이터 나누기
blocks = [wav_label_pairs[i*10:(i+1)*10] for i in range(60)]

random.seed(42)
random.shuffle(blocks)

# 분할 (예: 70% train, 30% test)
train_blocks = blocks[:42]  # 42개 데이터셋
test_blocks = blocks[42:]   # 18개 데이터셋

train_data = [item for block in train_blocks for item in block]
test_data = [item for block in test_blocks for item in block]

print("train_data 갯수 : ", len(train_data))
print("test_data 갯수 : ", len(test_data))

mel_list, token_list, label_list = [], [], []

for path, label in tqdm(train_data, desc="Processing audio files", total=len(train_data)):
    mel = wav_to_mel(path)  # (128, time, 1)
    token_ids = wav_to_token_ids(path)  # (128,)
    mel_list.append(mel)
    token_list.append(token_ids)
    label_list.append([label])
    
# 패딩을 위해 최대 time 계산
max_time = max(m.shape[1] for m in mel_list)

# mel padding (batch, 128, max_time, 1)
mel_batch = np.zeros((len(mel_list), N_MELS, max_time, 1), dtype=np.float32)
for i, mel in enumerate(mel_list):
    mel_batch[i, :, :mel.shape[1], :] = mel

token_batch = np.stack(token_list)  # (batch, 128)
label_batch = np.array(label_list, dtype=np.float32)  # (batch, 1)

# ========== 모델 정의 ==========
mel_input_layer = Input(shape=(N_MELS, None, 1), name='mel_input')  # (batch, 128, time, 1)
x1 = Permute((2, 1, 3))(mel_input_layer)  # (batch, time, 128, 1)
x1 = Reshape((-1, N_MELS))(x1)  # (batch, time, 128)
x1 = Bidirectional(LSTM(LSTM_UNITS, return_sequences=True))(x1)
x1 = Dropout(DROPOUT)(x1)

token_input_layer = Input(shape=(TOKEN_SEQ_LEN,), name='token_input')
x2 = Embedding(input_dim=VOCAB_SIZE, output_dim=EMBED_DIM, mask_zero=True)(token_input_layer)
x2 = Bidirectional(LSTM(LSTM_UNITS, return_sequences=True))(x2)
x2 = Dropout(DROPOUT)(x2)

# Cross Attention using MultiHeadAttention
cross_attention_layer = MultiHeadAttention(num_heads=4, key_dim=64)
x = cross_attention_layer(query=x1, value=x2, key=x2)  # (batch, time_mel, features)

x = GlobalAveragePooling1D()(x) # Global Average Pooling over time
x = Dropout(DROPOUT)(x)

output = Dense(1, activation='sigmoid')(x)

model = Model(inputs=[mel_input_layer, token_input_layer], outputs=output)
model.compile(optimizer=Adam(LR), loss='mse', metrics=['mae'])
model.summary()


# ========== 모델 학습 ==========
early_stop = EarlyStopping(
    monitor='loss',      # 모니터할 지표 (예: 'val_accuracy'도 가능)
    patience=3,              # 개선되지 않아도 기다릴 에포크 수
    restore_best_weights=True  # 가장 성능 좋았던 모델 가중치 복원
)

model.fit(
    {'mel_input': mel_batch, 'token_input': token_batch},
    label_batch,
    epochs=EPOCHS,
    batch_size=BATCH_SIZE,
    callbacks=[early_stop]
)

# ========== 예측 ==========
y_mel_list, y_token_list, y_label_list = [], [], []

for path, label in tqdm(test_data, desc="Processing audio files", total=len(test_data)):
    mel = wav_to_mel(path)  # (128, time, 1)
    token_ids = wav_to_token_ids(path)  # (128,)
    y_mel_list.append(mel)
    y_token_list.append(token_ids)
    y_label_list.append([label])

# mel padding (batch, 128, max_time, 1)
y_mel_batch = np.zeros((len(y_mel_list), N_MELS, max_time, 1), dtype=np.float32)
for i, mel in enumerate(y_mel_list):
    y_mel_batch[i, :, :mel.shape[1], :] = mel

y_token_batch = np.stack(y_token_list)  # (batch, 128)
y_label_batch = np.array(y_label_list, dtype=np.float32)  # (batch, 1)

preds = model.predict({'mel_input': y_mel_batch, 'token_input': y_token_batch})
for i, (p, l) in enumerate(zip(preds, y_label_list)):
    print(f"[{i}] Label: {l[0]}, Predicted: {p[0]:.4f}")

# 학습된 모델 정보 저장 
# model.save('model_ltn_rpt.keras')
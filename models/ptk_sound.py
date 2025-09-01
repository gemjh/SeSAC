import os
from tensorflow.keras.models import load_model
import librosa
import numpy as np

MODEL_PATH_WHOLE = os.path.join(os.path.dirname(__file__), "ptk_model.keras")
model_whole = load_model(MODEL_PATH_WHOLE)

MODEL_PATH_EACH = os.path.join(os.path.dirname(__file__), "teo_model.keras")
model_each = load_model(MODEL_PATH_EACH)


# ========== 데이터 전처리 함수 ==========
def audio_preprocess(wav, sr=16000, n_mels=128):
  ori_y1, sr1 = librosa.load(wav, sr=sr)
  mel_spec1 = librosa.feature.melspectrogram(y=ori_y1, sr=sr1, n_mels=n_mels)
  mel_db1 = librosa.power_to_db(mel_spec1, ref=np.max)
  length = mel_db1.shape[1]
  if length > 312:
    length = 312
  with open(wav, 'rb') as f:
    wav_data = f.read()
  bytes_per_sample = 2
  duration = len(wav_data) / (sr * bytes_per_sample)

  return mel_db1, round(duration,3), length

def wav_padding(wav, wav_max_len=312):
  pad_width = wav_max_len - wav.shape[1]
  if pad_width > 0:
    padded = np.pad(wav, pad_width=((0,0),(0,pad_width)), mode='constant', constant_values=-80)
  elif pad_width == 0:
    padded = wav
  elif pad_width < 0:
    padded =wav[:,:wav_max_len]
  return padded

def x_data_preprocess(x, sr=16000, n_mels=80):
  temp_wav_list = []
  temp_wav_length_list = []
  if isinstance(x,(list,np.ndarray)):
    for path in x:
      temp_wav_data, temp_wav_length = audio_preprocess(path,sr,n_mels)
      temp_pad_wav_data = wav_padding(temp_wav_data)
      temp_wav_list.append(temp_pad_wav_data)
      temp_wav_length_list.append(temp_wav_length)

    temp_x_padded_data = np.array(temp_wav_list)
    temp_x_data = np.transpose(temp_x_padded_data, (0, 2, 1))
    temp_x_data_length = np.array(temp_wav_length_list)
    return temp_x_data, temp_x_data_length
  elif isinstance(x,str):
    temp_wav_data, temp_x_data_length = audio_preprocess(x,sr,n_mels)
    temp_x_data = wav_padding(temp_wav_data)
    return temp_x_data, temp_x_data_length
    
def pred_preprocess(wav_path, sr=16000, n_mels=128):
  pred_,_,_ = audio_preprocess(wav_path, sr=sr, n_mels=n_mels)
  pad_pred_ = wav_padding(pred_)
  x_padded_pred_data = np.stack([pad_pred_])
  pred_audio_transposed = np.transpose(x_padded_pred_data, (0, 2, 1))
  x_pred_data = np.expand_dims(pred_audio_transposed, axis=-1)
  return x_pred_data

"""## 단일 음정(퍼퍼퍼) """
def ptk_each(filepath):
    ptk_x_data=pred_preprocess(filepath)
    pred = model_each.predict(ptk_x_data)
    return np.round(pred[0][0],2)


"""## 전체 음정(퍼터커) """
def ptk_whole(filepath):
    ptk_x_data=pred_preprocess(filepath)
    pred = model_whole.predict(ptk_x_data)
    return np.round(pred[0][0],2)


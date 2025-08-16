import numpy as np
import tensorflow as tf
import librosa
import os


# audio 파일 -> 멜변환, audio time_step
def audio_preprocess(wav, sr=16000, n_mels=128):
  ori_y1, sr1 = librosa.load(wav, sr=sr)
  mel_spec1 = librosa.feature.melspectrogram(y=ori_y1, sr=sr1, n_mels=n_mels)
  mel_db1 = librosa.power_to_db(mel_spec1, ref=np.max)
  with open(wav, 'rb') as f:
    wav_data = f.read()
  bytes_per_sample = 2
  duration = len(wav_data) / (sr * bytes_per_sample)

  return mel_db1, round(duration, 3), mel_db1.shape[1]

def wav_padding(wav, wav_max_len=312):
  pad_width = wav_max_len - wav.shape[1]  # 얼마나 채워야 하는지
  if pad_width > 0:
      # 오른쪽(열 끝)에 0을 채움: ((행 시작, 행 끝), (열 시작, 열 끝))
      padded = np.pad(wav, pad_width=((0, 0), (0, pad_width)), mode='constant', constant_values=-80)
  else:
      padded = wav  # 이미 가장 김
  return padded

def hardtanh(x, min_val=-20.0, max_val=20.0):
    return tf.clip_by_value(x, min_val, max_val)

def pred_preprocess(wav_path, sr=16000, n_mels=128):
  pred_wav = wav_path
  pred_,_,_ = audio_preprocess(pred_wav,sr,n_mels)
  padd_pred = wav_padding(pred_)
  x_padded_pred_data = np.stack([padd_pred])
  pred_audio_transposed = np.transpose(x_padded_pred_data, (0, 2, 1))
  x_pred_data = np.expand_dims(pred_audio_transposed, axis=-1)
  return x_pred_data

# model_path = 'C:/Users/eunhy/KoSp_tf_CLAP_D.keras'

def hardtanh(x, min_val=-20.0, max_val=20.0):
    return tf.clip_by_value(x, min_val, max_val)


# print(f'{model_path} Load')

def main(wav_path):
    pred_model = tf.keras.models.load_model(os.path.join(os.path.dirname(__file__),'KoSp_tf_CLAP_D.keras'),
      custom_objects={
          "hardtanh": hardtanh,
          'CTC': tf.keras.losses.CTC()
          }
    )
    # wav_path = 'C:/Users/eunhy/1001_p_4_0.wav'
    x_pred_data = pred_preprocess(wav_path,n_mels=80)
    pred_y = pred_model.predict(x_pred_data)
    print(f"녹음파일의 예상 점수는 {np.argmax(pred_y)}점 입니다.")
    return np.argmax(pred_y)

# main()
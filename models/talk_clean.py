from tensorflow.keras import layers
import numpy as np
import tensorflow as tf
import librosa
import os

# from ui.utils.env_utils import model_common_path
model_path = os.path.join(os.path.dirname(__file__), "KoSp_tf_CLAP_D.keras")

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
  elif pad_width == 0:
    padded = wav
  elif pad_width < 0:
    padded = wav[:,:wav_max_len]
  return padded

def hardtanh(x, min_val=-20.0, max_val=20.0):
    return tf.clip_by_value(x, min_val, max_val)

@tf.keras.utils.register_keras_serializable(package="mask")
class SequenceMask(layers.Layer):
    def call(self, inputs):
        is_padding = tf.reduce_all(tf.equal(inputs, -80.0), axis=[-1,-2])
        is_valid = tf.logical_not(is_padding)
        lengths = tf.reduce_sum(tf.cast(is_valid, tf.int32), axis=-1)
        lengths = tf.math.floordiv(lengths,2)
        return tf.sequence_mask(lengths, maxlen=78)

@tf.keras.utils.register_keras_serializable(package="masking")
def make_attn_mask(masks):
    qmask, kmask = masks
    qmask = tf.keras.ops.expand_dims(qmask, 2)
    kmask = tf.keras.ops.expand_dims(kmask, 1)
    return tf.keras.ops.logical_and(qmask, kmask)

def pred_preprocess(wav_path, sr=16000, n_mels=128):
  pred_wav = wav_path
  pred_,_,_ = audio_preprocess(pred_wav,sr,n_mels)
  padd_pred = wav_padding(pred_)
  x_padded_pred_data = np.stack([padd_pred])
  pred_audio_transposed = np.transpose(x_padded_pred_data, (0, 2, 1))
  x_pred_data = np.expand_dims(pred_audio_transposed, axis=-1)
  return x_pred_data

sub_x_list = [np.array([1, 7, 34, 21, 54, 2, 0, 0, 0, 0, 0, 0]),
np.array([1, 32, 42, 10, 42, 2, 0, 0, 0, 0, 0, 0]),
np.array([1, 4, 54, 31, 34, 2, 0, 0, 0, 0, 0, 0]),
np.array([1, 24, 47, 4, 34, 21, 2, 0, 0, 0, 0, 0]),
np.array([1, 4, 34, 26, 50, 2, 0, 0, 0, 0, 0, 0]),
np.array([1, 20, 42, 4, 54, 2, 0, 0, 0, 0, 0, 0]),
np.array([1, 30, 34, 12, 2, 0, 0, 0, 0, 0, 0, 0]),
np.array([1, 5, 42, 26, 29, 54, 2, 0, 0, 0, 0, 0]),
np.array([1, 10, 44, 27, 54, 2, 0, 0, 0, 0, 0, 0]),
np.array([1, 31, 35, 4, 24, 54, 2, 0, 0, 0, 0, 0]),
np.array([1, 33, 42, 20, 54, 2, 0, 0, 0, 0, 0, 0]),
np.array([1, 21, 54, 33, 35, 26, 4, 54, 2, 0, 0, 0]),
np.array([1, 12, 39, 20, 42, 7, 2, 0, 0, 0, 0, 0]),
np.array([1, 27, 47, 24, 34, 4, 54, 2, 0, 0, 0, 0]),
np.array([1, 28, 34, 20, 22, 42, 26, 2, 0, 0, 0, 0]),
np.array([1, 22, 34, 12, 10, 35, 2, 0, 0, 0, 0, 0]),
np.array([1, 21, 34, 30, 50, 2, 0, 0, 0, 0, 0, 0]),
np.array([1, 25, 52, 12, 39, 4, 54, 31, 42, 26, 2, 0]),
np.array([1, 26, 42, 24, 4, 38, 12, 26, 54, 2, 0, 0]),
np.array([1, 29, 35, 4, 27, 34, 26, 2, 0, 0, 0, 0]),
np.array([1, 11, 38, 4, 4, 47, 4, 2, 0, 0, 0, 0]),
np.array([1, 21, 34, 4, 47, 7, 54, 2, 0, 0, 0, 0]),
np.array([1, 26, 40, 12, 24, 45, 2, 0, 0, 0, 0, 0]),
np.array([1, 21, 34, 26, 32, 35, 2, 0, 0, 0, 0, 0]),
np.array([1, 26, 38, 12, 26, 52, 20, 2, 0, 0, 0, 0])]

sub_x = np.array(sub_x_list, dtype=np.int32)

sub_x_dict = {}

for i, x in enumerate(sub_x_list):
  sub_x_dict[i] = x

score = {'1':3, '2':2, '3':1, '4':2, '5':2, '6':3, '7':2, '8':2, '9':2, '10':3,
         '11':2, '12':1, '13':3, '14':2, '15':2, '16':2, '17':2, '18':1, '19':2, '20':3,
         '21':3, '22':3, '23':1, '24':1, '25':2}

def main(wav_path):
  total_score = 0
  for path in wav_path:
    if "p_" in path:
      num = path.split('p_')[1].split('_')[0]
      sub_x_data = sub_x_dict[int(num)-1]
    else:
      return f"파일 Path가 올바르지 않습니다. (path: {path})"
  
    # 모델 로드 - name_scope 스택 오류 방지를 위한 세션 초기화 추가 - 2025.08.26
    tf.keras.backend.clear_session()
    pred_model = tf.keras.models.load_model(model_path,
      custom_objects={
        "hardtanh": hardtanh,
        "SequenceMask": SequenceMask,
        "make_attn_mask": make_attn_mask,
        'CTC': tf.keras.losses.CTC()
        }
    )
    
    try:
      # path = 'C:/Users/eunhy/1001_p_4_0.wav'
      x_pred_data = pred_preprocess(path,n_mels=80)
      pred_y = pred_model.predict([x_pred_data,np.expand_dims(sub_x_data,axis=0)])
      total_score += np.round(pred_y[0][0]*score[num],0)
    finally:
      # ============================================================================
      # 메모리 관리 개선 - 2025.08.22 추가
      # 메모리 누수 방지를 위한 모델 정리
      # 예측 완료 후 모델을 메모리에서 완전히 제거하여 다음 모델 로드가 제대로 작동하도록 함
      # TensorFlow 세션도 함께 초기화하여 GPU/CPU 메모리 확보
      # ============================================================================
      try:
          if 'pred_model' in locals():
              del pred_model
      except:
          pass
      tf.keras.backend.clear_session()

  print(f"녹음파일의 예상 점수는 {total_score}점 입니다.")
  return total_score

# main()
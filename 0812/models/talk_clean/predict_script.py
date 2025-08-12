#!/usr/bin/env python3
import sys
import os

# 환경변수 설정 - Arrow 충돌 방지
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"
os.environ["ARROW_PRE_1_0_METADATA_VERSION"] = "1"
os.environ["ARROW_LIBHDFS3_DIR"] = ""
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

import numpy as np
import librosa
import tensorflow as tf

# TensorFlow 로그 레벨 설정
tf.get_logger().setLevel('ERROR')

def hardtanh(x, min_val=-20.0, max_val=20.0):
    return tf.clip_by_value(x, min_val, max_val)

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
    pad_width = wav_max_len - wav.shape[1]
    if pad_width > 0:
        padded = np.pad(wav, pad_width=((0, 0), (0, pad_width)), mode='constant', constant_values=-80)
    else:
        padded = wav
    return padded

def pred_preprocess(wav_path, sr=16000, n_mels=128):
    pred_wav = wav_path
    pred_, _, _ = audio_preprocess(pred_wav, sr, n_mels)
    padd_pred = wav_padding(pred_)
    x_padded_pred_data = np.stack([padd_pred])
    pred_audio_transposed = np.transpose(x_padded_pred_data, (0, 2, 1))
    x_pred_data = np.expand_dims(pred_audio_transposed, axis=-1)
    return x_pred_data

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python predict_script.py <wav_file_path>")
        sys.exit(1)
    
    wav_path = sys.argv[1]
    current_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(current_dir, 'KoSp_tf_CLAP_D.keras')
    
    try:
        pred_model = tf.keras.models.load_model(
            model_path,
            custom_objects={
                "hardtanh": hardtanh,
                'CTC': tf.keras.losses.CTC()
            }
        )
        x_pred_data = pred_preprocess(wav_path, n_mels=80)
        pred_y = pred_model.predict(x_pred_data)
        result = np.argmax(pred_y)
        print(result)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
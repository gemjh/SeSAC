#!/usr/bin/env python3
import sys
import os

# 환경변수 설정 - Protobuf 및 mutex 문제 해결
import warnings
warnings.filterwarnings("ignore")

os.environ.update({
    "TF_CPP_MIN_LOG_LEVEL": "3",
    "PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION": "python",
    "PROTOBUF_PYTHON_IMPLEMENTATION": "python",
    "ARROW_PRE_1_0_METADATA_VERSION": "1",
    "ARROW_LIBHDFS3_DIR": "",
    "OMP_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "VECLIB_MAXIMUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
    "TF_FORCE_GPU_ALLOW_GROWTH": "true",
    "TF_ENABLE_ONEDNN_OPTS": "0",
    "CUDA_VISIBLE_DEVICES": "-1",
    "GRPC_VERBOSITY": "ERROR",
    "GRPC_TRACE": "",
    "TF_DISABLE_MKL": "1",
    "TF_DISABLE_NUMA": "1"
})

import numpy as np
import librosa
import tensorflow as tf

# TensorFlow 로그 레벨 설정 및 GPU 비활성화
tf.get_logger().setLevel('ERROR')

# 메모리 증가 설정 (GPU가 있을 경우에만)
try:
    gpus = tf.config.experimental.list_physical_devices('GPU')
    if gpus:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
except:
    pass

# GPU 완전 비활성화
tf.config.set_visible_devices([], 'GPU')

# TensorFlow 스레드 설정 (에러 처리 추가)
try:
    tf.config.threading.set_inter_op_parallelism_threads(1)
    tf.config.threading.set_intra_op_parallelism_threads(1)
except:
    pass

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
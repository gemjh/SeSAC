# 단일음정 유지 능력 평가를 위한 SPICE 기반 코드

import tensorflow_hub as hub
import tensorflow as tf
import numpy as np
import librosa
import matplotlib.pyplot as plt
import os

filepath = "project/spice/0_아/e_1_1.wav"
analyze_pitch_stability(filepath)

# 1. 오디오 로드
def load_audio(filepath, target_sr=16000):
    audio, sr = librosa.load(filepath, sr=target_sr)
    audio = audio / np.max(np.abs(audio))  # normalize to [-1, 1]
    return audio, sr

# 2. SPICE 모델 로드 및 피치 예측
def estimate_pitch(audio):
    # 1. hub에서 링크로 가져오기
    model = hub.load("https://tfhub.dev/google/spice/2")
    # 2. tensorflow에서 로드하기
    # model=tf.saved_model.load('model')
    output = model.signatures["serving_default"](tf.constant(audio, tf.float32))
    pitch = output["pitch"].numpy().flatten()
    confidence = (1 - output["uncertainty"]).numpy().flatten()
    return pitch, confidence

# 3. 유효한 피치 (confidence >= 0.9)만 필터링
def filter_pitch(pitch, confidence, threshold=0.9):
    return [p if c >= threshold else 0 for p, c in zip(pitch, confidence)]

# 4. 이동 표준편차 계산
def moving_std(seq, win=5):
    padded = np.pad(seq, (win//2,), mode='edge')
    return [np.std(padded[i:i+win]) for i in range(len(seq))]

# 5. 단일음정 구간 판별 및 평가
def evaluate_pitch_stability(filtered_pitch, std_threshold=1.5, fps=100):
    pitch_std = moving_std(filtered_pitch, win=5)
    mono_flags = [s < std_threshold and p > 0 for s, p in zip(pitch_std, filtered_pitch)]
    mono_duration = sum(mono_flags) / fps  # 초 단위
    total_duration = len(filtered_pitch) / fps
    stable_ratio = mono_duration / total_duration if total_duration > 0 else 0
    return stable_ratio, mono_duration, total_duration, mono_flags

# 6. 전체 파이프라인 함수
def analyze_pitch_stability(filepath):
    audio, sr = load_audio(filepath)
    pitch, confidence = estimate_pitch(audio)
    filtered_pitch = filter_pitch(pitch, confidence)
    stable_ratio, mono_duration, total_duration, mono_flags = evaluate_pitch_stability(filtered_pitch)

    print(f"총 길이: {total_duration:.2f}s")
    print(f"단일음정 유지 시간: {mono_duration:.2f}s")
    print(f"안정성 비율: {stable_ratio:.2%}")

    # 시각화
    plt.figure(figsize=(12, 4))
    plt.plot(filtered_pitch, label='Filtered Pitch (Hz)')
    plt.plot(moving_std(filtered_pitch), label='Moving Std')
    plt.axhline(y=1.5, color='r', linestyle='--', label='Threshold')
    plt.legend()
    plt.title("Pitch Stability Analysis")
    plt.show()

    return stable_ratio

# 7. 사용 예
# filepath = "your_audio.wav"
# analyze_pitch_stability(filepath)

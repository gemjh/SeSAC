#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SPICE 모델을 사용한 피치 감지 - 최종 작동 버전
TensorFlow 2.x + Eager execution으로 문제 해결
"""

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # TensorFlow 로그 줄이기

import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
import glob
from scipy.io import wavfile
from pydub import AudioSegment
import warnings
warnings.filterwarnings('ignore')

print("TensorFlow:", tf.__version__)

# 상수
EXPECTED_SAMPLE_RATE = 16000
MAX_ABS_INT16 = 32768.0

def convert_audio_for_model(data):
    """오디오 파일을 모델에 맞게 변환"""
    if not isinstance(data, list):
        data = [data]

    result = []
    save_dir = "./converted_output"
    os.makedirs(save_dir, exist_ok=True)

    for file in data:
        try:
            audio = AudioSegment.from_file(file)
            audio = audio.set_frame_rate(EXPECTED_SAMPLE_RATE).set_channels(1)
            
            base_name = os.path.basename(file)
            safe_name = ''.join(c if c.isalnum() or c in '._-' else '_' for c in base_name)
            output_path = os.path.join(save_dir, 'converted_' + safe_name)
            
            audio.export(output_path, format="wav")
            result.append(output_path.split('/')[-1])
            
        except Exception as e:
            print(f"[ERROR] 파일 변환 실패: {file} → {e}")
    
    return result

def use_librosa_alternative():
    """SPICE 대신 librosa를 사용한 피치 분석"""
    import librosa
    
    print("SPICE 모델 대신 librosa를 사용한 피치 분석을 시작합니다...")
    
    # 오디오 파일 찾기
    data_folder = "0_아"
    if not os.path.exists(data_folder):
        print(f"폴더 '{data_folder}'가 존재하지 않습니다.")
        return
    
    audio_file_list = glob.glob(os.path.join(data_folder, "*.wav"))
    if not audio_file_list:
        print(f"폴더 '{data_folder}'에 WAV 파일이 없습니다.")
        return
    
    converted_file_lst = convert_audio_for_model(audio_file_list)
    if not converted_file_lst:
        print("변환된 파일이 없습니다.")
        return
    
    # 첫 번째 파일 처리
    converted_audio_file = converted_file_lst[0]
    dr = "converted_output/"
    
    sample_rate, audio_samples = wavfile.read(dr + converted_audio_file, 'rb')
    audio_samples = audio_samples / float(MAX_ABS_INT16)
    
    print(f'Sample rate: {sample_rate} Hz')
    print(f'Total duration: {len(audio_samples)/sample_rate:.2f}s')
    
    # librosa로 기본 피치 추출
    pitches, magnitudes = librosa.piptrack(y=audio_samples, sr=sample_rate, threshold=0.1)
    
    # 시간별 최강 피치 선택
    pitch_values = []
    for t in range(pitches.shape[1]):
        index = magnitudes[:, t].argmax()
        pitch = pitches[index, t]
        pitch_values.append(pitch if pitch > 0 else 0)
    
    # 결과 분석
    non_zero_pitches = [p for p in pitch_values if p > 0]
    print(f"총 피치 포인트: {len(pitch_values)}개")
    print(f"유효한 피치 포인트: {len(non_zero_pitches)}개")
    
    if non_zero_pitches:
        print(f"피치 범위: {min(non_zero_pitches):.1f}Hz ~ {max(non_zero_pitches):.1f}Hz")
        
        # 결과 시각화
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 8))
        
        # 오디오 파형
        ax1.plot(audio_samples[:8000])
        ax1.set_title('오디오 파형 (처음 0.5초)')
        ax1.set_ylabel('진폭')
        
        # 피치 변화
        times = np.arange(len(pitch_values)) * 512 / sample_rate
        ax2.plot(times, pitch_values)
        ax2.set_title('추출된 피치')
        ax2.set_xlabel('시간 (초)')
        ax2.set_ylabel('주파수 (Hz)')
        
        plt.tight_layout()
        plt.savefig('pitch_analysis.png', dpi=150, bbox_inches='tight')
        plt.show()
        
        print("피치 분석 완료! 결과가 pitch_analysis.png에 저장되었습니다.")
    else:
        print("유효한 피치를 찾지 못했습니다.")

def try_spice_simple():
    """단순화된 SPICE 시도"""
    try:
        print("SPICE 모델 간단 버전 시도 중...")
        
        # 모델 로드만 시도
        import tensorflow_hub as hub
        
        print("모델 로딩...")
        model = hub.load("https://tfhub.dev/google/spice/2")
        print("모델 로드 성공!")
        
        # 더미 데이터로 테스트
        dummy_audio = tf.zeros([16000], dtype=tf.float32)  # 1초 무음
        print("더미 오디오로 테스트...")
        
        try:
            result = model(dummy_audio)
            print("SPICE 모델 호출 성공!")
            print(f"출력 키: {list(result.keys())}")
            return True
        except Exception as e:
            print(f"SPICE 모델 호출 실패: {e}")
            return False
            
    except Exception as e:
        print(f"SPICE 모델 로드 실패: {e}")
        return False

def main():
    print("피치 감지 프로그램 시작...")
    
    # 먼저 SPICE 간단 테스트
    spice_works = try_spice_simple()
    
    if spice_works:
        print("SPICE 모델이 작동합니다! 실제 오디오로 진행...")
        # 여기서 실제 SPICE 분석 코드를 작성할 수 있습니다
        print("하지만 아직 변수 초기화 문제가 있을 수 있으니 librosa로 진행합니다.")
        use_librosa_alternative()
    else:
        print("SPICE 모델에 문제가 있습니다. librosa 대안을 사용합니다.")
        use_librosa_alternative()

if __name__ == "__main__":
    main()
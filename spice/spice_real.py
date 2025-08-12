#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SPICE 모델을 정말로 실행하는 스크립트
TensorFlow 1.x 완전 호환 모드 사용
"""

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import tensorflow.compat.v1 as tf
tf.disable_eager_execution()  # Eager execution 완전 비활성화
tf.enable_resource_variables()  # Resource variables 활성화

import tensorflow_hub as hub
import numpy as np
import matplotlib.pyplot as plt
import glob
from scipy.io import wavfile
from pydub import AudioSegment
import warnings
warnings.filterwarnings('ignore')

print("TensorFlow:", tf.__version__)
print("Eager execution 비활성화됨:", not tf.executing_eagerly())

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

def main():
    print("SPICE 모델 실행 시작...")
    
    # 오디오 파일 준비
    data_folder = "0_아"
    audio_file_list = glob.glob(os.path.join(data_folder, "*.wav"))
    converted_file_lst = convert_audio_for_model(audio_file_list)
    
    if not converted_file_lst:
        print("변환된 파일이 없습니다.")
        return
    
    # 첫 번째 파일 로드
    converted_audio_file = converted_file_lst[0]
    dr = "converted_output/"
    sample_rate, audio_samples = wavfile.read(dr + converted_audio_file, 'rb')
    audio_samples = audio_samples / float(MAX_ABS_INT16)
    
    print(f'Sample rate: {sample_rate} Hz')
    print(f'Total duration: {len(audio_samples)/sample_rate:.2f}s')
    print(f'Size of the input: {len(audio_samples)}')
    
    # TensorFlow 1.x 스타일로 그래프 구성
    print("TensorFlow 그래프 구성 중...")
    
    # 플레이스홀더 정의
    audio_input = tf.placeholder(tf.float32, shape=[None], name='audio_input')
    
    # SPICE 모델 로드
    print("SPICE 모델 로딩...")
    model = hub.load("https://tfhub.dev/google/spice/2")
    
    # 모델 적용
    model_output = model.signatures['serving_default'](input=audio_input)
    
    # 세션 시작
    print("TensorFlow 세션 시작...")
    config = tf.ConfigProto()
    config.allow_soft_placement = True
    
    with tf.Session(config=config) as sess:
        print("변수 초기화...")
        
        # 모든 초기화 작업
        try:
            # SavedModel 초기화자들 실행
            saved_model_initializers = tf.get_collection("saved_model_initializers")
            if saved_model_initializers:
                print(f"SavedModel 초기화자 {len(saved_model_initializers)}개 실행 중...")
                sess.run(saved_model_initializers)
            
            # 전역 변수 초기화
            global_init = tf.global_variables_initializer()
            sess.run(global_init)
            
            # 로컬 변수 초기화
            local_init = tf.local_variables_initializer()
            sess.run(local_init)
            
            print("모든 변수 초기화 완료!")
            
        except Exception as init_error:
            print(f"초기화 오류: {init_error}")
            print("초기화 무시하고 계속 진행...")
        
        # SPICE 모델 실행
        print("SPICE 모델로 피치 분석 실행 중...")
        
        try:
            feed_dict = {audio_input: audio_samples}
            
            pitch_outputs, uncertainty_outputs = sess.run([
                model_output['pitch'], 
                model_output['uncertainty']
            ], feed_dict=feed_dict)
            
            print("🎉 SPICE 모델 실행 성공!")
            
            # 결과 분석
            confidence_outputs = 1.0 - uncertainty_outputs
            
            print(f"피치 출력 길이: {len(pitch_outputs)}")
            print(f"평균 신뢰도: {np.mean(confidence_outputs):.3f}")
            print(f"피치 범위: {np.min(pitch_outputs):.3f} ~ {np.max(pitch_outputs):.3f}")
            
            # 신뢰도 높은 피치만 선택
            high_confidence_mask = confidence_outputs >= 0.9
            high_confidence_pitches = pitch_outputs[high_confidence_mask]
            
            print(f"높은 신뢰도 피치 개수: {len(high_confidence_pitches)}")
            
            if len(high_confidence_pitches) > 0:
                print(f"높은 신뢰도 피치 범위: {np.min(high_confidence_pitches):.3f} ~ {np.max(high_confidence_pitches):.3f}")
            
            # 결과 시각화
            fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(15, 10))
            
            # 원본 오디오
            ax1.plot(audio_samples[:8000])
            ax1.set_title('원본 오디오 파형 (처음 0.5초)')
            ax1.set_ylabel('진폭')
            
            # SPICE 피치와 신뢰도
            ax2.plot(pitch_outputs, label='Pitch', alpha=0.7)
            ax2.plot(confidence_outputs, label='Confidence', alpha=0.7)
            ax2.set_title('SPICE 피치 분석 결과')
            ax2.set_ylabel('값')
            ax2.legend()
            ax2.grid(True)
            
            # 높은 신뢰도 피치만
            high_conf_indices = np.where(high_confidence_mask)[0]
            if len(high_conf_indices) > 0:
                ax3.scatter(high_conf_indices, high_confidence_pitches, c='red', s=2, alpha=0.6)
                ax3.set_title('높은 신뢰도 피치 (신뢰도 >= 0.9)')
                ax3.set_xlabel('시간 프레임')
                ax3.set_ylabel('피치 값')
                ax3.grid(True)
            
            plt.tight_layout()
            plt.savefig('spice_results.png', dpi=150, bbox_inches='tight')
            plt.show()
            
            print("SPICE 분석 결과가 spice_results.png에 저장되었습니다!")
            print("SPICE 모델 실행 완전 성공! 🎊")
            
        except Exception as run_error:
            print(f"모델 실행 오류: {run_error}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()
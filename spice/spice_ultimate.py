#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SPICE 모델 최종 실행 시도 - 강제 TensorFlow 2.x 호환
"""

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import warnings
warnings.filterwarnings(action='ignore')
import tensorflow as tf
import tensorflow_hub as hub
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

def main():
    print("🚀 SPICE 모델 최종 실행 시도...")
    
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
    
    # SPICE 모델 강제 실행 시도
    print("🎯 SPICE 모델 로딩...")
    
    try:
        # 모델 로드 및 초기화 시도
        # model = hub.load("https://tfhub.dev/google/spice/2")
        model=tf.saved_model.load('model')

        print("✅ 모델 로드 성공!")
        
        # 오디오 텐서 준비
        audio_tensor = tf.constant(audio_samples, dtype=tf.float32)
        print(f"오디오 텐서 준비 완료: {audio_tensor.shape}")
        
        # 다양한 방법으로 모델 실행 시도
        print("🔄 모델 실행 시도 중...")
        
        # 방법 1: 직접 실행 (변수 초기화 무시)
        try:
            print("방법 1: 직접 실행 시도...")
            
            # 그래프 모드로 실행
            @tf.function
            def run_spice(audio_input):  
                try:
                    return model.signatures['serving_default'](input=audio_input)
                except Exception as e:
                    print(f"Serving default 실패: {e}")
                    # 다른 시그니처 시도
                    sigs = list(model.signatures.keys())
                    if sigs:
                        return model.signatures[sigs[0]](audio_input)
                    else:
                        # 직접 모델 호출
                        return model(audio_input)
            
            model_output = run_spice(audio_tensor)
            
            print("🎉 SPICE 모델 실행 성공!")
            
            # 결과 처리
            if isinstance(model_output, dict):
                pitch_outputs = model_output.get('pitch', None)
                uncertainty_outputs = model_output.get('uncertainty', None)
                
                if pitch_outputs is not None and uncertainty_outputs is not None:
                    pitch_values = pitch_outputs.numpy()
                    uncertainty_values = uncertainty_outputs.numpy()
                    confidence_values = 1.0 - uncertainty_values
                    
                    print(f"✨ 피치 분석 완료!")
                    print(f"피치 포인트 수: {len(pitch_values)}")
                    print(f"평균 신뢰도: {np.mean(confidence_values):.3f}")
                    print(f"피치 범위: {np.min(pitch_values):.3f} ~ {np.max(pitch_values):.3f}")
                    
                    # 높은 신뢰도 피치만 선택
                    high_confidence_mask = confidence_values >= 0.9
                    high_confidence_pitches = pitch_values[high_confidence_mask]
                    
                    print(f"높은 신뢰도 피치: {len(high_confidence_pitches)}개")
                    
                    # 결과 시각화
                    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(15, 10))
                    
                    # 원본 오디오 파형
                    ax1.plot(audio_samples[:8000])
                    ax1.set_title('원본 오디오 파형 (처음 0.5초)')
                    ax1.set_ylabel('진폭')
                    ax1.grid(True)
                    
                    # SPICE 피치와 신뢰도
                    ax2.plot(pitch_values, label='SPICE Pitch', alpha=0.8, color='blue')
                    ax2.plot(confidence_values, label='Confidence', alpha=0.8, color='red')
                    ax2.set_title('SPICE 피치 분석 결과')
                    ax2.set_ylabel('값')
                    ax2.legend()
                    ax2.grid(True)
                    
                    # 높은 신뢰도 피치
                    if len(high_confidence_pitches) > 0:
                        high_conf_indices = np.where(high_confidence_mask)[0]
                        ax3.scatter(high_conf_indices, high_confidence_pitches, 
                                  c='red', s=3, alpha=0.7)
                        ax3.set_title(f'높은 신뢰도 피치 (신뢰도 >= 0.9) - {len(high_confidence_pitches)}개')
                        ax3.set_xlabel('시간 프레임')
                        ax3.set_ylabel('피치 값')
                        ax3.grid(True)
                        
                        print(f"높은 신뢰도 피치 범위: {np.min(high_confidence_pitches):.3f} ~ {np.max(high_confidence_pitches):.3f}")
                    
                    plt.tight_layout()
                    plt.savefig('spice_success_results.png', dpi=150, bbox_inches='tight')
                    plt.show()
                    
                    print("🎊 SPICE 모델 완전 실행 성공!")
                    print("📊 결과가 spice_success_results.png에 저장되었습니다!")
                    
                    return True
                else:
                    print("❌ 모델 출력에서 pitch/uncertainty를 찾을 수 없습니다.")
                    print(f"출력 키: {list(model_output.keys())}")
            else:
                print("❌ 모델 출력이 예상과 다릅니다.")
                print(f"출력 타입: {type(model_output)}")
                
        except Exception as e:
            print(f"❌ 방법 1 실패: {e}")
            
            # 방법 2: 무음 데이터로 "워밍업" 후 실제 데이터 실행
            try:
                print("방법 2: 모델 워밍업 후 실행...")
                
                # 짧은 무음으로 모델 워밍업
                dummy_audio = tf.zeros([1000], dtype=tf.float32)
                _ = model.signatures['serving_default'](input=dummy_audio)
                
                # 실제 오디오로 실행
                model_output = model.signatures['serving_default'](input=audio_tensor)
                print("🎉 워밍업 방법 성공!")
                
            except Exception as e2:
                print(f"❌ 방법 2도 실패: {e2}")
                print("😞 모든 시도가 실패했습니다.")
                return False
                
    except Exception as load_error:
        print(f"❌ 모델 로드 실패: {load_error}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🏆 SPICE 모델 실행 완전 성공!")
    else:
        print("\n💔 SPICE 모델 실행 실패")
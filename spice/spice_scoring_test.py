#!/usr/bin/env python3
"""
SPICE 기반 단일음정 유지 능력 평가 코드 (.py 버전)
노트북에서 Python 스크립트로 변환 - 자동 conda 환경 활성화
"""
# 임시로 파일 경로 설정
filepath = "/Users/kimberlyjojohirn/Downloads/SeSAC/project/spice/0_아/e_1_1.wav"
import sys
import subprocess
import os

def activate_conda_environment():
    """conda SeSAC 환경 자동 활성화"""
    try:
        # 현재 Python 실행 경로 확인
        current_python = sys.executable
        print(f"현재 Python 경로: {current_python}")
        
        # SeSAC 환경 경로 확인
        if 'SeSAC' not in current_python:
            print("SeSAC 환경이 아닙니다. 자동으로 SeSAC 환경에서 재실행합니다...")
            
            # conda 환경 경로 찾기 (일반적인 경로들)
            possible_conda_paths = [
                os.path.expanduser("~/opt/anaconda3"),
                os.path.expanduser("~/miniconda3"), 
                os.path.expanduser("~/anaconda3"),
                "/opt/anaconda3",
                "/opt/miniconda3"
            ]
            
            sesac_python = None
            for conda_base in possible_conda_paths:
                test_path = os.path.join(conda_base, "envs", "SeSAC", "bin", "python")
                if os.path.exists(test_path):
                    sesac_python = test_path
                    break
            
            if sesac_python:
                print(f"SeSAC 환경에서 재실행: {sesac_python}")
                # 현재 스크립트를 SeSAC 환경에서 재실행
                subprocess.run([sesac_python, __file__] + sys.argv[1:])
                sys.exit(0)
            else:
                print("❌ SeSAC conda 환경을 찾을 수 없습니다.")
                print("다음 명령으로 수동 실행하세요:")
                print("conda activate SeSAC && python spice_scoring_test.py")
                sys.exit(1)
        else:
            print("✅ SeSAC 환경이 활성화되어 있습니다.")
            
    except Exception as e:
        print(f"환경 확인 중 오류 발생: {e}")

# conda 환경 자동 활성화 실행
activate_conda_environment()

# 필요한 라이브러리 import

import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
import librosa
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

def setup_tensorflow():
    """TensorFlow 환경 설정"""
    # 스레드 수 제한으로 안정성 향상
    tf.config.threading.set_intra_op_parallelism_threads(1)
    tf.config.threading.set_inter_op_parallelism_threads(1)
    
    # GPU 설정 (오류 무시)
    try:
        gpus = tf.config.experimental.list_physical_devices('GPU')
        if gpus:
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
    except:
        pass
    
    tf.config.run_functions_eagerly(False)

def clear_tfhub_cache():
    """TensorFlow Hub 캐시 클리어"""
    import tempfile
    import shutil
    
    try:
        cache_dir = os.path.join(tempfile.gettempdir(), 'tfhub_modules')
        if os.path.exists(cache_dir):
            shutil.rmtree(cache_dir)
            print("TensorFlow Hub 캐시 클리어 완료")
    except Exception as e:
        pass

def load_audio(filepath, sample_rate=16000):
    """오디오 파일을 로드하고 정규화"""
    audio, sr = librosa.load(filepath, sr=sample_rate)
    if np.max(np.abs(audio)) > 0:
        audio = audio / np.max(np.abs(audio))
    return audio, sr

def estimate_pitch_spice_only(audio, sr=16000):
    """SPICE 모델을 사용한 피치 추정"""
    try:
        print("SPICE 모델 로딩 중...")
        tf.keras.backend.clear_session()
        
        with tf.device('/CPU:0'):
            model = hub.load("https://tfhub.dev/google/spice/2")
        
        print("SPICE 모델 로드 완료")
        
        if np.max(np.abs(audio)) == 0:
            raise ValueError("오디오에 신호가 없습니다")
        
        audio_tensor = tf.convert_to_tensor(audio, dtype=tf.float32)
        
        with tf.device('/CPU:0'):
            signature_keys = list(model.signatures.keys())
            
            # 모델 워밍업
            dummy_audio = tf.zeros([1000], dtype=tf.float32)
            try:
                _ = model.signatures["serving_default"](dummy_audio)
                print("모델 워밍업 완료")
            except Exception as warmup_error:
                pass
            
            # 실제 모델 실행
            print("SPICE 모델 실행 중...")
            outputs = model.signatures["serving_default"](audio_tensor)
            
            pitch = outputs["pitch"].numpy().flatten()
            uncertainty = outputs["uncertainty"].numpy().flatten()
            confidence = 1.0 - uncertainty
        
        print(f"SPICE 모델 실행 완료: {len(pitch)}개 프레임")
        return pitch, confidence
        
    except Exception as e:
        print(f"SPICE 모델 실행 실패: {e}")
        raise e

def filter_pitch(pitch, confidence, threshold=0.7):
    """신뢰도가 높은 피치만 필터링"""
    filtered = [p if c >= threshold else 0 for p, c in zip(pitch, confidence)]
    valid_count = sum(1 for p in filtered if p > 0)
    return filtered

def moving_std(seq, win=5):
    """이동 윈도우 표준편차 계산"""
    if len(seq) == 0:
        return []
    
    padded = np.pad(seq, (win//2,), mode='edge')
    std_values = []
    
    for i in range(len(seq)):
        window = padded[i:i+win]
        valid_values = window[window > 0]
        if len(valid_values) > 1:
            std_values.append(np.std(valid_values))
        else:
            std_values.append(0.0)
    
    return std_values

def evaluate_pitch_stability(filtered_pitch, std_threshold=1.5, actual_duration=None):
    """피치 안정성 평가"""
    if len(filtered_pitch) == 0:
        return 0, 0, 0, []
    
    pitch_std = moving_std(filtered_pitch, win=5)
    mono_flags = [s < std_threshold and p > 0 for s, p in zip(pitch_std, filtered_pitch)]
    
    if actual_duration is not None:
        actual_fps = len(filtered_pitch) / actual_duration
        mono_duration = sum(mono_flags) / actual_fps
        total_duration = actual_duration
    else:
        mono_duration = sum(mono_flags) / 100
        total_duration = len(filtered_pitch) / 100
    
    stable_ratio = mono_duration / total_duration if total_duration > 0 else 0
    
    return stable_ratio, mono_duration, total_duration, mono_flags

def analyze_pitch_stability(filepath, std_threshold=1.5, confidence_threshold=0.7, window_size=5):
    """SPICE 전용 피치 안정성 분석 파이프라인"""
    print(f"현재 설정: std_threshold={std_threshold}, confidence_threshold={confidence_threshold}, window_size={window_size}")
    try:
        # 1. 오디오 로드
        audio, sr = load_audio(filepath)
        actual_duration = len(audio) / sr
        
        # 2. SPICE로 피치 추정
        pitch, confidence = estimate_pitch_spice_only(audio, sr)
        
        # 3. 피치 필터링
        filtered_pitch = filter_pitch(pitch, confidence, threshold=confidence_threshold)
        
        # 4. 안정성 평가
        def custom_moving_std(seq, win):
            if len(seq) == 0:
                return []
            padded = np.pad(seq, (win//2,), mode='edge')
            std_values = []
            for i in range(len(seq)):
                window = padded[i:i+win]
                valid_values = window[window > 0]
                if len(valid_values) > 1:
                    std_values.append(np.std(valid_values))
                else:
                    std_values.append(0.0)
            return std_values
        
        pitch_std = custom_moving_std(filtered_pitch, window_size)
        mono_flags = [s < std_threshold and p > 0 for s, p in zip(pitch_std, filtered_pitch)]
        
        # 5. 결과 계산
        actual_fps = len(filtered_pitch) / actual_duration
        mono_duration = sum(mono_flags) / actual_fps
        # stable_ratio = mono_duration / actual_duration
        
        print(f"\n=== 분석 결과 ===")
        print(f"총 오디오 길이: {actual_duration:.2f}초")
        print(f"단일음정 시간: {mono_duration:.2f}초")
        
        deactivate_conda_environment()

        return mono_duration
        
    except Exception as e:
        print(f"분석 실패: {e}")
        raise e

# def test_basic_functions():
#     """기본 함수들 테스트"""
#     print("기본 함수 테스트 시작")
    
#     try:
#         # 이동 표준편차 함수 테스트
#         def moving_std(seq, win=5):
#             if len(seq) == 0:
#                 return []
#             padded = np.pad(seq, (win//2,), mode='edge')
#             std_values = []
#             for i in range(len(seq)):
#                 window = padded[i:i+win]
#                 valid_values = window[window > 0]
#                 if len(valid_values) > 1:
#                     std_values.append(np.std(valid_values))
#                 else:
#                     std_values.append(0.0)
#             return std_values
        
#         test_data = [1, 2, 3, 2, 1, 0, 1, 2, 3]
#         result = moving_std(test_data)
        
#         # 필터링 함수 테스트
#         def filter_pitch(pitch, confidence, threshold=0.7):
#             filtered = [p if c >= threshold else 0 for p, c in zip(pitch, confidence)]
#             return filtered
        
#         test_pitch = [100, 200, 300, 400]
#         test_conf = [0.8, 0.6, 0.9, 0.5]
#         filtered = filter_pitch(test_pitch, test_conf)        
#         return True
        
#     except Exception as e:
#         print(f"❌ 기본 함수 테스트 실패: {e}")
#         return False



# def test_audio_loading():
#     """오디오 로딩 테스트"""
#     print("오디오 로딩 테스트 시작")
    
#     try:
#         if os.path.exists(filepath):
#             audio, sr = librosa.load(filepath, sr=16000)
#             print(f"✓ 오디오 로드 성공: {len(audio)/sr:.2f}초, {sr}Hz")
            
#             # 간단한 피치 분석 (librosa 사용)
#             pitches, magnitudes = librosa.piptrack(y=audio, sr=sr, threshold=0.1)
#             print(f"✓ 피치 분석 성공: {pitches.shape}")
            
#             # 통계 정보
#             non_zero_pitches = pitches[pitches > 0]
#             if len(non_zero_pitches) > 0:
#                 print(f"✓ 유효 피치: {len(non_zero_pitches)}개, 범위: {non_zero_pitches.min():.1f}~{non_zero_pitches.max():.1f}Hz")
            
#             return True
#         else:
#             print(f"❌ 파일 없음: {filepath}")
#             return False
            
#     except Exception as e:
#         print(f"❌ 오디오 테스트 실패: {e}")
#         return False

# def simple_test():
#     """전체 테스트 실행"""    
#     tests = [
#         ("기본 함수", test_basic_functions),
#         ("오디오 로딩", test_audio_loading)
#     ]
    
#     results = []
#     for test_name, test_func in tests:
#         print(f"\n{test_name} 테스트:")
#         print("-" * 30)
#         success = test_func()
#         results.append((test_name, success))
    
#     return all(success for _, success in results)

def deactivate_conda_environment():
    """conda 환경 종료"""
    try:
        current_python = sys.executable
        if 'SeSAC' in current_python:
            print("\n📤 SeSAC 가상환경을 종료합니다...")
            print("스크립트 실행이 완료되어 자동으로 환경이 종료됩니다.")
            # 스크립트 종료와 함께 자동으로 환경이 비활성화됨
        else:
            print("기본 Python 환경입니다.")
    except Exception as e:
        print(f"환경 종료 중 오류: {e}")

def main():
    """메인 실행 함수"""
    print("SPICE 피치 분석 스크립트 시작")
    
    # conda 환경 활성화
    activate_conda_environment()
    
    try:
        # SPICE 분석 실행
        result = analyze_pitch_stability(filepath)
        
        print(f"\n✅ 분석 완료!")
        print(f"단일음정 유지 시간: {result:.2f}초")
        
        # 성공 시 환경 종료 메시지
        deactivate_conda_environment()
        
        return True
        
    except Exception as e:
        print(f"❌ 분석 실패: {e}")
        return False

if __name__ == "__main__":
    main()
import sys
import os
# 필요한 라이브러리 import
try:
    import tensorflow as tf
    import tensorflow_hub as hub
    import numpy as np
    import librosa
    import warnings
    warnings.filterwarnings('ignore')
    
    print("✅ 모든 라이브러리 import 완료")
    
except ImportError as e:
    print(f"❌ 라이브러리 import 실패: {e}")
    print("필요한 라이브러리를 설치하세요.")
    sys.exit(1)

def setup_tensorflow():
    """TensorFlow 환경 설정"""
    # 스레드 수 제한으로 안정성 향상 (이미 초기화된 경우 스킵)
    try:
        tf.config.threading.set_intra_op_parallelism_threads(1)
        tf.config.threading.set_inter_op_parallelism_threads(1)
    except RuntimeError:
        pass  # 이미 초기화된 경우 무시
    
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
        
        try:
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
            
            return pitch, confidence
            
        finally:
            # ============================================================================
            # 메모리 정리 - 2025.08.22 추가
            # SPICE 모델 사용 완료 후 메모리에서 제거하여 메모리 누수 방지
            # ============================================================================
            del model
            tf.keras.backend.clear_session()
            print("SPICE 모델 메모리 정리 완료")
        
    except Exception as e:
        print(f"SPICE 모델 실행 실패: {e}")
        raise e

def filter_pitch(pitch, confidence, threshold=0.7):
    """신뢰도가 높은 피치만 필터링"""
    filtered = [p if c >= threshold else 0 for p, c in zip(pitch, confidence)]
    valid_count = sum(1 for p in filtered if p > 0)
    return filtered

# def moving_std(seq, win=5):
#     """이동 윈도우 표준편차 계산"""
#     if len(seq) == 0:
#         return []
    
#     padded = np.pad(seq, (win//2,), mode='edge')
#     std_values = []
    
#     for i in range(len(seq)):
#         window = padded[i:i+win]
#         valid_values = window[window > 0]
#         if len(valid_values) > 1:
#             std_values.append(np.std(valid_values))
#         else:
#             std_values.append(0.0)
    
#     return std_values

def analyze_pitch_stability(filepath, std_threshold=.5, confidence_threshold=0.1, window_size=9):
    """SPICE 전용 피치 안정성 분석 파이프라인"""
    print(f"------------------------------------------------------------------------\n\n\n현재 설정: std_threshold = {std_threshold}, confidence_threshold = {confidence_threshold}, window_size = {window_size} \n\n\n------------------------------------------------------------------------")

    try:
        # TensorFlow 설정
        setup_tensorflow()
        
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

        return mono_duration
        
    except Exception as e:
        print(f"분석 실패: {e}")
        raise e


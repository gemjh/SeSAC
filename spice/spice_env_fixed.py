#!/usr/bin/env python3
"""
SPICE 기반 단일음정 유지 능력 평가 코드
TensorFlow Metal plugin 오류 해결을 위한 개선된 버전
"""
import sys
import subprocess
import os

# Metal plugin 비활성화를 위한 환경변수들
os.environ['DISABLE_MLCOMPUTE'] = '1'
os.environ['TF_METAL'] = '0'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['CUDA_VISIBLE_DEVICES'] = ''  # GPU 완전 비활성화

def fix_tensorflow_metal():
    """TensorFlow Metal plugin 문제 해결"""
    try:
        # Metal plugin 파일을 임시로 이름 변경
        import glob
        metal_plugins = glob.glob(os.path.expanduser("~/opt/anaconda3/envs/SeSAC/lib/python3.9/site-packages/tensorflow-plugins/libmetal_plugin.dylib*"))
        
        for plugin in metal_plugins:
            backup_name = plugin + ".backup"
            if not os.path.exists(backup_name):
                try:
                    os.rename(plugin, backup_name)
                    print(f"Metal plugin 임시 비활성화: {plugin}")
                except:
                    pass
    except Exception as e:
        print(f"Metal plugin 처리 중 오류 (무시): {e}")

def find_conda_base():
    """conda 설치 경로 찾기"""
    possible_conda_paths = [
        os.path.expanduser("~/opt/anaconda3"),
        os.path.expanduser("~/miniconda3"), 
        os.path.expanduser("~/anaconda3"),
        "/opt/anaconda3",
        "/opt/miniconda3"
    ]
    
    for conda_base in possible_conda_paths:
        if os.path.exists(os.path.join(conda_base, "bin", "conda")):
            return conda_base
    
    return None

def activate_conda_environment():
    """conda SeSAC 환경 자동 활성화"""
    try:
        current_python = sys.executable
        print(f"현재 Python 경로: {current_python}")
        
        if 'SeSAC' not in current_python:
            print("SeSAC 환경이 아닙니다.")
            conda_base = find_conda_base()
            if not conda_base:
                print("❌ conda가 설치되어 있지 않습니다.")
                sys.exit(1)
            
            sesac_python = os.path.join(conda_base, "envs", "SeSAC", "bin", "python")
            
            if not os.path.exists(sesac_python):
                print("❌ SeSAC 환경이 존재하지 않습니다.")
                sys.exit(1)
            
            print(f"SeSAC 환경에서 재실행: {sesac_python}")
            subprocess.run([sesac_python, __file__] + sys.argv[1:])
            sys.exit(0)
        else:
            print("✅ SeSAC 환경이 활성화되어 있습니다.")
            
    except Exception as e:
        print(f"환경 확인 중 오류 발생: {e}")
        sys.exit(1)

# 환경 활성화 및 Metal plugin 문제 해결
activate_conda_environment()
fix_tensorflow_metal()

# 필요한 라이브러리 import
try:
    # TensorFlow import를 별도의 함수로 분리
    def import_tensorflow():
        try:
            import tensorflow as tf
            # CPU만 사용하도록 강제 설정
            tf.config.set_visible_devices([], 'GPU')
            tf.config.threading.set_intra_op_parallelism_threads(1)
            tf.config.threading.set_inter_op_parallelism_threads(1)
            return tf
        except Exception as e:
            print(f"TensorFlow import 실패, CPU 전용으로 재시도: {e}")
            # 환경변수 추가 설정
            os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
            import tensorflow as tf
            return tf
    
    tf = import_tensorflow()
    import tensorflow_hub as hub
    import numpy as np
    import librosa
    
    print("✅ 모든 라이브러리 import 완료")
    
except ImportError as e:
    print(f"❌ 라이브러리 import 실패: {e}")
    print("tensorflow-metal을 제거해보세요: pip uninstall tensorflow-metal")
    sys.exit(1)
except Exception as e:
    print(f"❌ TensorFlow 초기화 실패: {e}")
    print("새로운 conda 환경을 생성하는 것을 권장합니다.")
    sys.exit(1)

# 파일 경로 설정
filepath = "/Volumes/SSAM/project/spice/0_아/p_1_1.wav"

def load_audio(filepath, sample_rate=16000):
    """오디오 파일을 로드하고 정규화"""
    if not os.path.exists(filepath):
        print(f"❌ 오디오 파일이 존재하지 않습니다: {filepath}")
        return None, None
    
    try:
        audio, sr = librosa.load(filepath, sr=sample_rate)
        if np.max(np.abs(audio)) > 0:
            audio = audio / np.max(np.abs(audio))
        return audio, sr
    except Exception as e:
        print(f"❌ 오디오 로드 실패: {e}")
        return None, None

def estimate_pitch_spice_only(audio, sr=16000):
    """SPICE 모델을 사용한 피치 추정 (CPU 전용)"""
    try:
        print("SPICE 모델 로딩 중...")
        tf.keras.backend.clear_session()
        
        # CPU 전용으로 강제 설정
        with tf.device('/CPU:0'):
            model = hub.load("https://tfhub.dev/google/spice/2")
        
        print("SPICE 모델 로드 완료")
        
        if np.max(np.abs(audio)) == 0:
            raise ValueError("오디오에 신호가 없습니다")
        
        audio_tensor = tf.convert_to_tensor(audio, dtype=tf.float32)
        
        with tf.device('/CPU:0'):
            # 모델 워밍업
            dummy_audio = tf.zeros([1000], dtype=tf.float32)
            try:
                _ = model.signatures["serving_default"](dummy_audio)
                print("모델 워밍업 완료")
            except Exception:
                pass
            
            # 실제 모델 실행
            print("SPICE 모델 실행 중...")
            outputs = model.signatures["serving_default"](audio_tensor)
            
            pitch = outputs["pitch"].numpy().flatten()
            uncertainty = outputs["uncertainty"].numpy().flatten()
            confidence = 1.0 - uncertainty
        
        return pitch, confidence
        
    except Exception as e:
        print(f"SPICE 모델 실행 실패: {e}")
        raise e

def filter_pitch(pitch, confidence, threshold=0.4):
    """신뢰도가 높은 피치만 필터링"""
    filtered = [p if c >= threshold else 0 for p, c in zip(pitch, confidence)]
    return filtered

def analyze_pitch_stability(filepath, std_threshold=1.5, confidence_threshold=0.4, window_size=5):
    """SPICE 전용 피치 안정성 분석"""
    print(f"현재 설정: std_threshold={std_threshold}, confidence_threshold={confidence_threshold}, window_size={window_size}")

    try:
        # 1. 오디오 로드
        audio, sr = load_audio(filepath)
        if audio is None:
            return None
        
        actual_duration = len(audio) / sr
        print(f"오디오 길이: {actual_duration:.2f}초")
        
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
        return None

def main():
    """메인 실행 함수"""
    print("SPICE 피치 분석 스크립트 시작 (CPU 전용 버전)")
    
    try:
        result = analyze_pitch_stability(filepath)
        
        if result is not None:
            print(f"\n✅ 분석 완료!")
            print(f"단일음정 유지 시간: {result:.2f}초")
            return result
        else:
            print("❌ 분석 실패")
            return False
        
    except Exception as e:
        print(f"❌ 메인 실행 실패: {e}")
        return False

if __name__ == "__main__":
    main()
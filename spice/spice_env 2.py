#!/usr/bin/env python3
"""
SPICE 기반 단일음정 유지 능력 평가 코드 (.py 버전)
노트북에서 Python 스크립트로 변환 - 자동 conda 환경 활성화
TensorFlow Metal 오류 해결 버전
"""

import sys
import subprocess
import os

# 임시로 파일 경로 설정
script_dir = os.path.dirname(os.path.abspath(__file__))
filepath = os.path.join(script_dir, "0_아/p_1_1.wav")

# TensorFlow Metal 비활성화 (import 전에 설정)
os.environ['DISABLE_MLCOMPUTE'] = '1'
os.environ['TF_METAL'] = '0'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

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


def create_environment(env_name="SeSAC", python_version=3.9):
    """conda 환경 자동 생성"""
    print("환경이 없습니다. 자동으로 생성합니다...")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    conda_base = find_conda_base()
    if not conda_base:
        print("❌ conda가 설치되어 있지 않습니다.")
        print("https://docs.conda.io/en/latest/miniconda.html 에서 miniconda를 설치하세요.")
        return False
    
    conda_cmd = os.path.join(conda_base, "bin", "conda")
    
    try:
        # 환경 생성 (env_name: 환경이름)
        subprocess.run(
            ["conda", "create", "-n", env_name, f"python={python_version}", "pip", "-y"],check=True,
            capture_output=True,
            text=True,
            cwd=script_dir
        )

        # pip 경로 찾기
        env_pip = os.path.join(conda_base, "envs", env_name, "bin", "pip")
        
        print("📚 필수 라이브러리 설치 중...")
        # requirements.txt 파일을 사용해서 설치
        requirements_path = os.path.join(script_dir, "requirements.txt")
        if os.path.exists(requirements_path):
            print("requirements.txt에서 패키지 설치 중...")
            subprocess.run([env_pip, "install", "-r", requirements_path], check=True, capture_output=True, text=True)
        else:
            print("requirements.txt를 찾을 수 없어서 기본 패키지만 설치합니다.")
            libraries = ["tensorflow", "tensorflow_hub", "numpy", "librosa", "matplotlib"]
            for lib in libraries:
                print(f"Installing {lib}...")
                subprocess.run([env_pip, "install", lib], check=True, capture_output=True, text=True)
        
        print("생성 완료")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 환경 생성 실패: {e}")
        return False
    except Exception as e:
        print(f"❌ 예상치 못한 오류: {e}")
        return False

def activate_conda_environment():
    """conda SeSAC 환경 자동 활성화 또는 생성"""
    try:
        # 현재 Python 실행 경로 확인
        current_python = sys.executable
        print(f"현재 Python 경로: {current_python}")
        
        # SeSAC 환경 경로 확인
        if 'SeSAC' not in current_python:
            print("SeSAC 환경이 아닙니다.")
            
            conda_base = find_conda_base()
            if not conda_base:
                print("❌ conda가 설치되어 있지 않습니다.")
                sys.exit(1)
            
            sesac_python = os.path.join(conda_base, "envs", "SeSAC", "bin", "python")
            
            # SeSAC 환경이 있는지 확인
            if not os.path.exists(sesac_python):
                # SeSAC 환경이 없으면 생성
                if not create_environment("SeSAC"):
                    print("환경 생성에 실패했습니다.")
                    sys.exit(1)
            
            print(f"SeSAC 환경에서 재실행: {sesac_python}")
            # 현재 스크립트를 SeSAC 환경에서 재실행
            subprocess.run([sesac_python, __file__] + sys.argv[1:])
            sys.exit(0)
        else:
            print("✅ SeSAC 환경이 활성화되어 있습니다.")
            
    except Exception as e:
        print(f"환경 확인 중 오류 발생: {e}")
        sys.exit(1)

def delete_conda_environment(env_name=''):
    """conda 환경 삭제"""
    try:
        conda_base = find_conda_base()
        conda_cmd = os.path.join(conda_base, "bin", "conda")
        subprocess.run([conda_cmd, "remove", "-n", env_name, "--all", "-y"], 
                        check=True, capture_output=True, text=True)  
        print("삭제 완료")
    except Exception as e:
        print(f"환경 삭제 중 오류 발생: {e}")
        sys.exit(1)

# conda 환경 자동 활성화 실행
activate_conda_environment()

def install_missing_packages_from_requirements():
    """requirements.txt를 사용해 누락된 패키지 자동 설치"""
    try:
        # 기본적인 패키지들 먼저 테스트
        import tensorflow as tf
        import tensorflow_hub as hub
        import numpy as np
        import librosa
        import matplotlib.pyplot as plt
        return True
    except ImportError as e:
        print(f"📦 누락된 패키지 발견: {e}")
        print("requirements.txt에서 자동 설치합니다...")
        
        # 현재 conda 환경의 pip 찾기
        current_python = sys.executable
        pip_path = current_python.replace('python', 'pip')
        
        # requirements.txt 경로
        script_dir = os.path.dirname(os.path.abspath(__file__))
        requirements_path = os.path.join(script_dir, "requirements.txt")
        
        if os.path.exists(requirements_path):
            try:
                subprocess.run([pip_path, 'install', '-r', requirements_path], 
                             check=True, capture_output=True, text=True)
                print("✅ requirements.txt에서 패키지 설치 완료")
                return True
            except subprocess.CalledProcessError as e:
                print(f"❌ 패키지 설치 실패: {e}")
                return False
        else:
            print("❌ requirements.txt 파일을 찾을 수 없습니다.")
            return False

# 누락된 패키지 자동 설치
if not install_missing_packages_from_requirements():
    print("패키지 설치에 실패했습니다. 수동으로 설치해주세요.")
    sys.exit(1)

# 필요한 라이브러리 import
try:
    import tensorflow as tf
    import tensorflow_hub as hub
    import numpy as np
    import librosa
    import matplotlib.pyplot as plt
    import warnings
    warnings.filterwarnings('ignore')
    
    print("✅ 모든 라이브러리 import 완료")
    
except ImportError as e:
    print(f"❌ 라이브러리 import 실패: {e}")
    print("수동으로 패키지를 설치해주세요.")
    sys.exit(1)

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

def analyze_pitch_stability(filepath, std_threshold=1.5, confidence_threshold=0.4, window_size=5):
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

def main():
    """메인 실행 함수"""
    print("SPICE 피치 분석 스크립트 시작 (Metal 비활성화 버전)")
    
    try:
        # SPICE 분석 실행
        result = analyze_pitch_stability(filepath)

        print(f"\n✅ 분석 완료!")
        print(f"단일음정 유지 시간: {result:.2f}초")
        
        return result
        
    except Exception as e:
        print(f"❌ 분석 실패: {e}")
        return False

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
SPICE 기반 단일음정 유지 능력 평가 코드 (.py 버전)
노트북에서 Python 스크립트로 변환 - 자동 conda 환경 활성화
TensorFlow Metal 오류 해결 버전
"""
import sys
import subprocess
import os

from sympy.logic import true

# 임시로 파일 경로 설정
# script_dir = os.path.dirname(os.path.abspath(__file__))
# filepath = os.path.join(script_dir, "p_1_1.wav")


if sys.platform.startswith('win'):
    WINOS=True
    print("현재 운영체제는 윈도우입니다.")
else: WINOS = False


# TensorFlow 설정 (import 전에 설정)
os.environ['DISABLE_MLCOMPUTE'] = '1'
os.environ['TF_METAL'] = '0'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TF_NUM_INTEROP_THREADS'] = '1'
os.environ['TF_NUM_INTRAOP_THREADS'] = '1'

def find_conda_base():
    """conda 설치 경로 찾기"""
    possible_conda_paths = [
        os.path.expanduser("~/opt/anaconda3"),
        os.path.expanduser("~/miniconda3"), 
        os.path.expanduser("~/anaconda3"),
        "/opt/anaconda3",
        "/opt/miniconda3"
    ]

    if WINOS:
        win_conda_paths = [
            os.path.expanduser("~/anaconda3"),
            os.path.expanduser("~/miniconda3"),
            "C:/Users/user/anaconda3",
            "C:/ProgramData/Anaconda3",
            "C:/ProgramData/Miniconda3"
        ]
        for conda_base in win_conda_paths:
            if os.path.exists(os.path.join(conda_base, "Scripts", "conda.exe")):
                return conda_base
        return None
    
    for conda_base in possible_conda_paths:
        if os.path.exists(os.path.join(conda_base, "bin", "conda")):
            return conda_base
    
    return None


def create_environment():
    """conda 환경 자동 생성"""
    print("환경이 없습니다. 자동으로 생성합니다...")
    script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    conda_base = find_conda_base()
    if not conda_base:
        print("❌ conda가 설치되어 있지 않습니다.")
        print("https://docs.conda.io/en/latest/miniconda.html 에서 miniconda를 설치하세요.")
        return False
    
    # conda_cmd = os.path.join(conda_base, "bin", "conda")
    env_path = os.path.join(script_dir, "environment.yaml")
    
    try:
        print("🔧 필수 라이브러리 설치 중...")
        subprocess.run(
        ["conda", "env", "create", "--file", env_path],
        check=True
        )
        print("✅ 생성 완료")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 환경 생성 실패: {e}")
        return False
    except Exception as e:
        print(f"❌ 예상치 못한 오류: {e}")
        return False

def activate_conda_environment():
    """conda 환경 자동 활성화 또는 생성"""
    try:
        # 현재 Python 실행 경로 확인
        current_python = sys.executable
        print(f"현재 Python 경로: {current_python}")
        
        # SeSAC 환경 경로 확인
        if 'CLAP_PC' not in current_python:
            print("CLAP_PC 환경이 아닙니다.")
            
            conda_base = find_conda_base()
            if not conda_base:
                print("❌ conda가 설치되어 있지 않습니다.")
                sys.exit(1)
            
            if WINOS:
                sesac_python = os.path.join(conda_base, "envs", "CLAP_PC", "Scripts", "python.exe")
            else:
                sesac_python = os.path.join(conda_base, "envs", "CLAP_PC", "bin", "python")
            
            # SeSAC 환경이 있는지 확인
            if not os.path.exists(sesac_python):
                # SeSAC 환경이 없으면 생성
                if not create_environment():
                    print("환경 생성에 실패했습니다.")
                    sys.exit(1)
            
            print(f"🔄 CLAP_PC 환경으로 전환 중...")
            # 원래 실행된 스크립트를 CLAP_PC 환경에서 재실행
            original_script = sys.argv[0]  # 원래 실행된 파일 (app.py)
            subprocess.run([sesac_python] + sys.argv)
            sys.exit(0)
        else:
            print("✅ CLAP_PC 환경이 활성화되어 있습니다.")
            
    except Exception as e:
        print(f"환경 확인 중 오류 발생: {e}")
        sys.exit(1)

def delete_conda_environment(env_name=''):
    """conda 환경 삭제"""
    try:
        conda_base = find_conda_base()
        if WINOS:
            conda_cmd = os.path.join(conda_base, "Scripts", "conda.exe")
        else:
            conda_cmd = os.path.join(conda_base, "bin", "conda")
        subprocess.run([conda_cmd, "remove", "-n", env_name, "--all", "-y"], 
                        check=True, capture_output=True, text=True)  
        print("삭제 완료")
    except Exception as e:
        print(f"환경 삭제 중 오류 발생: {e}")
        sys.exit(1)

# conda 환경 자동 활성화 실행
# activate_conda_environment()
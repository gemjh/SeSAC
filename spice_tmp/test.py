import sys
import subprocess
import os
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

def delete_conda_environment(env_name=''):
    """conda 환경 삭제"""
    # 현재 실행 중인 conda 환경명 불러오기
    # env_name=os.environ.get("CONDA_DEFAULT_ENV")  
    try:
        conda_base = find_conda_base()
        conda_cmd = os.path.join(conda_base, "bin", "conda")
        subprocess.run([conda_cmd, "remove", "-n", env_name, "--all", "-y"], 
                        check=True, capture_output=True, text=True)  
        print("삭제 완료")
    except Exception as e:
        print(f"환경 삭제 중 오류 발생: {e}")
        sys.exit(1)

def create_environment(env_name, python_version=3.9):
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
        # 필수 라이브러리 설치(requirements.txt)
        subprocess.run([env_pip, "install", "-r", "requirements.txt"],check=True,capture_output=True,text=True,cwd=script_dir)
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
                if not create_sesac_environment('SeSAC'):
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
# delete_conda_environment('tmp')
# conda_env_name = os.environ.get("CONDA_DEFAULT_ENV")

# print(conda_env_name)
# create_environment('tmp')
print('1. 현재 Python 경로:',sys.executable)
activate_conda_environment()
print('3. 현재 Python 경로:',sys.executable)

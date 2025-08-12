def d2result(wav_path):
    import subprocess
    import sys
    import os
    
    # 현재 파일의 디렉토리 경로
    current_file_dir = os.path.dirname(os.path.abspath(__file__))
    # Docker 사용 가능한지 확인
    try:
        docker_check = subprocess.run(["docker", "--version"], capture_output=True, text=True, timeout=5)
        if docker_check.returncode == 0:
            script_path = os.path.join(current_file_dir, 'predict_docker.py')
        else:
            script_path = os.path.join(current_file_dir, 'predict_script.py')
    except:
        script_path = os.path.join(current_file_dir, 'predict_script.py')
    
    try:
        # 환경변수 설정 - 스레드 안전성 강화
        env = os.environ.copy()
        env["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"
        env["TF_CPP_MIN_LOG_LEVEL"] = "3"
        env["ARROW_PRE_1_0_METADATA_VERSION"] = "1"
        env["ARROW_LIBHDFS3_DIR"] = ""
        env["OMP_NUM_THREADS"] = "1"
        env["OPENBLAS_NUM_THREADS"] = "1" 
        env["MKL_NUM_THREADS"] = "1"
        env["VECLIB_MAXIMUM_THREADS"] = "1"
        env["NUMEXPR_NUM_THREADS"] = "1"
        
        # 시스템 Python 사용 시도
        python_candidates = [
            "/opt/homebrew/bin/python3",
            "/usr/local/bin/python3", 
            "/usr/bin/python3",
            sys.executable
        ]
        
        python_path = None
        for candidate in python_candidates:
            if os.path.exists(candidate):
                python_path = candidate
                break
        
        if not python_path:
            python_path = sys.executable
            
        result = subprocess.run([python_path, script_path, wav_path], 
                              capture_output=True, text=True, timeout=60, env=env)
        if result.returncode == 0:
            score = int(result.stdout.strip().split('\n')[-1])
            print(f"녹음파일의 예상 점수는 {score}점 입니다.")
            return score
        else:
            print(f"Error: {result.stderr}")
            print(f"Stdout: {result.stdout}")
            return -1
    except subprocess.TimeoutExpired:
        print("Timeout error")
        return -1
    except Exception as e:
        print(f"Subprocess error: {e}")
        return -1
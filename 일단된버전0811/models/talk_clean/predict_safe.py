#!/usr/bin/env python3
import sys
import os
import subprocess

def main():
    if len(sys.argv) != 2:
        print("ERROR: Usage: python predict_safe.py <wav_file_path>", file=sys.stderr)
        sys.exit(1)
    
    wav_path = sys.argv[1]
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 새로운 Python 프로세스로 실행 (완전 격리)
    env = os.environ.copy()
    env.update({
        "TF_CPP_MIN_LOG_LEVEL": "3",
        "PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION": "python", 
        "CUDA_VISIBLE_DEVICES": "-1",
        "OMP_NUM_THREADS": "1",
        "OPENBLAS_NUM_THREADS": "1",
        "MKL_NUM_THREADS": "1",
        "VECLIB_MAXIMUM_THREADS": "1",
        "NUMEXPR_NUM_THREADS": "1",
        "TF_FORCE_GPU_ALLOW_GROWTH": "true",
        "TF_ENABLE_ONEDNN_OPTS": "0",
        "PYTHONPATH": os.path.dirname(os.path.dirname(current_dir))
    })
    
    # 원본 스크립트를 subprocess로 실행
    script_path = os.path.join(current_dir, 'predict_script.py')
    
    try:
        result = subprocess.run(
            [sys.executable, script_path, wav_path],
            capture_output=True,
            text=True,
            timeout=180,
            env=env,
            cwd=current_dir
        )
        
        if result.returncode == 0:
            print(result.stdout.strip().split('\n')[-1])
        else:
            print(f"ERROR: {result.stderr}", file=sys.stderr)
            sys.exit(1)
            
    except subprocess.TimeoutExpired:
        print("ERROR: Timeout", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
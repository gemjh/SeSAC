#!/usr/bin/env python3
import sys
import os
import subprocess

def main():
    if len(sys.argv) != 2:
        print("ERROR: Usage: python predict_docker.py <wav_file_path>", file=sys.stderr)
        sys.exit(1)
    
    wav_path = sys.argv[1]
    
    # Docker 컨테이너로 실행
    try:
        # 파일을 컨테이너에 마운트해서 실행
        abs_wav_path = os.path.abspath(wav_path)
        abs_dir = os.path.dirname(abs_wav_path)
        filename = os.path.basename(abs_wav_path)
        
        result = subprocess.run([
            "docker", "run", "--rm",
            "-v", f"{abs_dir}:/data",
            "tf-predict", f"/data/{filename}"
        ], capture_output=True, text=True, timeout=180)
        
        if result.returncode == 0:
            print(result.stdout.strip().split('\n')[-1])
        else:
            print(f"ERROR: Docker execution failed", file=sys.stderr)
            print(f"STDOUT: {result.stdout}", file=sys.stderr)
            print(f"STDERR: {result.stderr}", file=sys.stderr)
            print(f"Return code: {result.returncode}", file=sys.stderr)
            sys.exit(1)
            
    except subprocess.TimeoutExpired:
        print("ERROR: Docker execution timeout", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
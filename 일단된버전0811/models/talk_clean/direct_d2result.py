#!/usr/bin/env python3
import sys
import os
import traceback

def main():
    if len(sys.argv) != 2:
        print("ERROR: Usage: python direct_d2result.py <wav_file_path>")
        return
    
    wav_path = sys.argv[1]
    
    try:
        # 환경변수 설정 - 스크립트 시작 시점에서 설정
        os.environ.update({
            "TF_CPP_MIN_LOG_LEVEL": "3",
            "PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION": "python",
            "ARROW_PRE_1_0_METADATA_VERSION": "1",
            "ARROW_LIBHDFS3_DIR": "",
            "OMP_NUM_THREADS": "1",
            "OPENBLAS_NUM_THREADS": "1",
            "MKL_NUM_THREADS": "1",
            "VECLIB_MAXIMUM_THREADS": "1",
            "NUMEXPR_NUM_THREADS": "1",
            "CUDA_VISIBLE_DEVICES": "-1"
        })
        
        # 경로 설정
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        sys.path.insert(0, project_root)
        sys.path.insert(0, current_dir)
        
        # 원래 d2result 함수 직접 import 및 호출
        from CLAP_D_2 import d2result
        
        # d2result 함수가 내부적으로 subprocess를 사용하므로
        # 여기서는 단순히 호출만 함
        score = d2result(wav_path)
        
        if score >= 0:
            print(score)  # 숫자만 출력 (원래 predict_script.py 형식과 동일)
        else:
            print("ERROR: 분석 실패", file=sys.stderr)
            sys.exit(1)
        
    except Exception as e:
        print(f"ERROR: {str(e)}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
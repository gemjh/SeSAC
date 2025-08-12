#!/usr/bin/env python3
# SPICE 모델 FailedPreconditionError 수정 테스트

import tensorflow_hub as hub
import tensorflow as tf
import numpy as np
import librosa
import os
import sys

def setup_tensorflow():
    """TensorFlow 환경 설정"""
    print(f"TensorFlow 버전: {tf.__version__}")
    
    # GPU 메모리 증가 허용
    gpus = tf.config.experimental.list_physical_devices('GPU')
    if gpus:
        try:
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
            print("GPU 메모리 증가 허용 설정 완료")
        except RuntimeError as e:
            print(f"GPU 설정 오류: {e}")
    else:
        print("GPU 없음, CPU 사용")
    
    # Graph 모드 설정
    tf.config.run_functions_eagerly(False)
    print("TensorFlow Graph 모드 설정 완료")

def clear_tfhub_cache():
    """TensorFlow Hub 캐시 클리어"""
    import tempfile
    import shutil
    
    try:
        cache_dir = os.path.join(tempfile.gettempdir(), 'tfhub_modules')
        if os.path.exists(cache_dir):
            shutil.rmtree(cache_dir)
            print("TensorFlow Hub 캐시 클리어 완료")
        else:
            print("TensorFlow Hub 캐시 없음")
    except Exception as e:
        print(f"캐시 클리어 오류: {e}")

def test_spice_model(audio_path):
    """SPICE 모델 테스트"""
    try:
        print("\n=== SPICE 모델 테스트 시작 ===")
        
        # 1. 오디오 로드
        print(f"오디오 로드 중: {audio_path}")
        audio, sr = librosa.load(audio_path, sr=16000)
        
        if np.max(np.abs(audio)) > 0:
            audio = audio / np.max(np.abs(audio))
        
        print(f"오디오 로드 완료: {len(audio)/sr:.2f}초")
        
        # 2. SPICE 모델 로드 및 실행
        print("SPICE 모델 로딩 중...")
        
        with tf.device('/CPU:0'):  # CPU 강제 사용
            model = hub.load("https://tfhub.dev/google/spice/2")
        
        print("SPICE 모델 로드 완료")
        
        # 3. 오디오 전처리
        audio_tensor = tf.convert_to_tensor(audio, dtype=tf.float32)
        print(f"오디오 텐서: shape={audio_tensor.shape}, dtype={audio_tensor.dtype}")
        
        # 4. 모델 실행
        print("SPICE 모델 실행 중...")
        
        with tf.device('/CPU:0'):
            outputs = model.signatures["serving_default"](audio_tensor)
            
            pitch = outputs["pitch"].numpy().flatten()
            uncertainty = outputs["uncertainty"].numpy().flatten()
            confidence = 1.0 - uncertainty
        
        print(f"✅ SPICE 모델 실행 성공!")
        print(f"  - 피치 배열 크기: {len(pitch)}")
        print(f"  - 평균 신뢰도: {np.mean(confidence):.3f}")
        print(f"  - 유효한 피치 개수: {np.sum(pitch > 0)}")
        
        return True
        
    except Exception as e:
        print(f"❌ SPICE 모델 실행 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("SPICE 모델 FailedPreconditionError 수정 테스트")
    print("=" * 50)
    
    # TensorFlow 환경 설정
    setup_tensorflow()
    
    # 캐시 클리어
    clear_tfhub_cache()
    
    # 오디오 파일 경로
    audio_path = "/Users/kimberlyjojohirn/Downloads/SeSAC/project/spice/0_아/e_1_1.wav"
    
    # 파일 존재 확인
    if not os.path.exists(audio_path):
        print(f"❌ 오디오 파일을 찾을 수 없습니다: {audio_path}")
        return False
    
    # SPICE 모델 테스트
    success = test_spice_model(audio_path)
    
    if success:
        print("\n🎉 FailedPreconditionError 수정 성공!")
        print("SPICE 모델이 정상적으로 실행되었습니다.")
    else:
        print("\n💥 FailedPreconditionError 여전히 발생")
        print("추가 해결 방법이 필요합니다.")
    
    return success

if __name__ == "__main__":
    main()
#!/bin/bash

# 새로운 conda 환경 생성
conda create -n tf_clean python=3.9 -y

# 환경 활성화
source activate tf_clean

# 필요한 패키지만 설치
pip install tensorflow==2.13.0
pip install librosa
pip install numpy

echo "새로운 환경 tf_clean이 생성되었습니다."
echo "사용법: conda activate tf_clean"
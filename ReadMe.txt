1. Anaconda 설치
  - Anaconda Prompt 실행
2. 아나콘다 가상환경 설치 (CLAP_PC)
  - yaml 파일을 통한 가상환경 세팅 및 환경 설정
  - 명령 : conda env create --file environment.yaml
  - 참고 : conda remove --name CLAP_PC --all
3. 파일 경로 각자 바꾸고(db,models,ui 폴더가 있는 경로여야 함) streamlit run ui/app.py
4. 로그인
5. zip 파일 업로드: 환자 한 명의 검사 내용 폴더
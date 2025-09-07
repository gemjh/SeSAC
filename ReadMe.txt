1. Anaconda 설치
  - Anaconda Prompt 실행
2. 아나콘다 가상환경 설치 (CLAP_PC)
  - yaml 파일을 통한 가상환경 세팅 및 환경 설정
  - 명령 : conda env create --file environment.yaml
  - 참고 : conda remove --name CLAP_PC --all
3. MySQL 8.0 설치
4. DB 초기 설정
    - MySQL 워크벤치를 실행하여 root로 접속한다.
   
    - DB 스키마 및 사용자 생성과 권한 부여
      * Query 창에 다음의 sql을 복사하여 실행한다.

      CREATE DATABASE clap CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
      CREATE USER 'clapuser'@'%' IDENTIFIED BY '00000000';
      GRANT ALL PRIVILEGES ON clap.* TO 'clapuser'@'%';
      FLUSH PRIVILEGES;

    - DB IMPORT
      * Server > DB Import를 실행
        a. Import form Dump Project Folder의 경로를 db/data 경로로 지정
        b. Select Database Objects to Import에서 clap을 선택
        c. 하단의 Start Import 버튼을 클릭하여 데이터를 import 한다.

5. .env 파일에서 base_path(파일 경로) 각자 바꾸고(db,models,ui 폴더의 상위 폴더여야 함) 터미널에서 streamlit run ui/app.py 실행
6. 로그인
7. zip 파일 업로드 
	- 환자 한 명의 검사 내용 폴더를 압축한 파일(환자번호/검사유형/검사 인덱스/wav파일 순서여야 함)	- 환자번호.csv로 저장된 환자 검사 정보(number, code, name, age, sex, edu, excluded, post_stroke_date, diagnosis, stroke_type, lesion_location, hemiplegia, hemineglect, visual field defect, 검사자, 검사일자, 대상기관)

import streamlit as st
import os
from dotenv import load_dotenv
from pathlib import Path
import sys

# Arrow 관련 환경변수 미리 설정 - 스레드 충돌 방지
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"
os.environ["ARROW_PRE_1_0_METADATA_VERSION"] = "1" 
os.environ["ARROW_LIBHDFS3_DIR"] = ""
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1" 
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 직접 subprocess로 처리하므로 d2result import 불필요
d2result = "available"  # 분석 기능이 사용 가능함을 표시


# env_path = Path(__file__).parent / ".." / ".env"
# load_dotenv(dotenv_path=env_path)
# # 파일 저장 디렉토리
# AUDIO_DIR = "./audio_files"
# os.makedirs(AUDIO_DIR, exist_ok=True)

# def get_connection():
#     conn = mysql.connector.connect(
#         host=os.getenv("db_host"),
#         database=os.getenv("db_database"),
#         user=os.getenv("db_username"),
#         password=os.getenv("db_password")
#     )
#     return conn

# # conn = get_connection()
# # cursor = conn.cursor()

# # 테이블 생성
# # cursor.execute("""
# # CREATE TABLE IF NOT EXISTS audio_metadata (
# #     id INT AUTO_INCREMENT PRIMARY KEY,
# #     filename VARCHAR(255),
# #     file_path VARCHAR(500),
# #     file_size INT,
# #     duration FLOAT,
# #     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# # )
# # """)

# # 파일 업로드 및 저장
# uploaded_file = st.file_uploader("WAV 파일 업로드", type=['wav'])

# if uploaded_file:
#     # 파일을 디스크에 저장
#     file_path = os.path.join(AUDIO_DIR, uploaded_file.name)
#     with open(file_path, "wb") as f:
#         f.write(uploaded_file.getbuffer())

#     # 메타데이터만 DB에 저장
#     # cursor.execute(
#     #     """INSERT INTO audio_metadata 
#     #         (filename, file_path, file_size) 
#     #         VALUES (%s, %s, %s)""",
#     #     (uploaded_file.name, file_path, uploaded_file.size)
#     # )
#     # conn.commit()

# # 저장된 파일 목록 표시
# # def get_audio_files():
# #     cursor.execute("SELECT id, filename, file_path FROM audio_metadata")
# #     return cursor.fetchall()

# audio_files = get_audio_files()
# for file_id, filename, file_path in audio_files:
#     if os.path.exists(file_path):
#         st.audio(file_path, format='audio/wav')
#         st.write(f"ID: {file_id}, 파일명: {filename}")

# print(d2result(os.listdir(AUDIO_DIR)))

import streamlit as st
import os
import shutil

# 파일 저장 디렉토리
AUDIO_DIR = "./audio_files"
os.makedirs(AUDIO_DIR, exist_ok=True)

# 파일 업로드 및 저장
uploaded_file = st.file_uploader("WAV 파일 업로드", type=['wav'])

if uploaded_file:
    try:
        # 파일을 디스크에 저장
        file_path = os.path.join(AUDIO_DIR, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        st.success(f"파일 저장 완료: {file_path}")
        # st.rerun() 제거 - 자동 리로드로 인한 크래시 방지
    except Exception as e:
        st.error(f"파일 저장 중 오류: {e}")

# 저장된 파일 목록 표시
def get_audio_files():
    """디렉토리에서 WAV 파일 목록 가져오기"""
    audio_files = []
    if os.path.exists(AUDIO_DIR):
        for filename in os.listdir(AUDIO_DIR):
            if filename.lower().endswith('.wav'):
                file_path = os.path.join(AUDIO_DIR, filename)
                audio_files.append((filename, file_path))
    return audio_files

# 파일 목록 표시 및 재생
st.subheader("저장된 오디오 파일들")
audio_files = get_audio_files()

if audio_files:
    for filename, file_path in audio_files:
        st.write(f"**{filename}**")
        st.audio(file_path, format='audio/wav')
        
        # 버튼들을 나란히 배치
        col1, col2 = st.columns(2)
        
        with col1:
            button_key = f"btn_analyze_{filename}"
            result_key = f"result_{filename}"
            
            if st.button(f"점수 분석", key=button_key):
                if d2result != "available":
                    st.error("모델이 로딩되지 않아 분석을 수행할 수 없습니다.")
                else:
                    with st.spinner('분석 중... (약 10-30초 소요)'):
                        try:
                            # 직접 d2result 함수 호출 시도
                            import sys
                            import os
                            current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                            sys.path.insert(0, os.path.join(current_dir, 'models', 'talk_clean'))
                            
                            from CLAP_D_2 import d2result
                            score = d2result(file_path)
                            
                            if score >= 0:
                                st.session_state[result_key] = {"type": "success", "message": f"예상 점수: {score}점"}
                            else:
                                st.session_state[result_key] = {"type": "error", "message": "분석 실패"}
                                
                        except Exception as e:
                            st.session_state[result_key] = {"type": "error", "message": f"분석 중 오류: {str(e)}"}
            
            # 분석 결과 표시
            if result_key in st.session_state:
                result_data = st.session_state[result_key]
                if result_data["type"] == "success":
                    st.success(result_data["message"])
                else:
                    st.error(result_data["message"])
        
        with col2:
            if st.button(f"삭제", key=f"delete_{filename}"):
                try:
                    os.remove(file_path)
                    st.success(f"{filename} 삭제 완료")
                    # st.rerun() 제거 - 자동 리로드로 인한 크래시 방지
                except Exception as e:
                    st.error(f"삭제 중 오류: {e}")
        
        st.divider()
else:
    st.info("저장된 오디오 파일이 없습니다.")

# 전체 파일 개수 표시
st.write(f"총 {len(audio_files)}개의 오디오 파일이 저장되어 있습니다.")


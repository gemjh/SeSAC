import streamlit as st
# 페이지 설정
st.set_page_config(
    page_title="CLAP",
    page_icon="👋",
    layout="wide",
    initial_sidebar_state="expanded"
)
import os
# TensorFlow 설정 (import 전에 먼저 설정)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TF_NUM_INTEROP_THREADS'] = '1'
os.environ['TF_NUM_INTRAOP_THREADS'] = '1'
# PyTorch MPS 호환성 문제 해결
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"
os.environ["PYTORCH_MPS_HIGH_WATERMARK_RATIO"] = "0.0"
os.environ["CUDA_VISIBLE_DEVICES"] = ""
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from utils.env_utils import activate_conda_environment

spinner = st.spinner('환경 설정 중...')
spinner.__enter__()
activate_conda_environment()

# MPS 완전 비활성화
import torch
torch.backends.mps.is_available = lambda: False
torch.backends.mps.is_built = lambda: False

# torch.isin을 CPU로 강제하는 패치
original_isin = torch.isin
def patched_isin(elements, test_elements, **kwargs):
    # MPS 텐서를 CPU로 이동
    if hasattr(elements, 'device') and str(elements.device).startswith('mps'):
        elements = elements.cpu()
    if hasattr(test_elements, 'device') and str(test_elements.device).startswith('mps'):
        test_elements = test_elements.cpu()
    return original_isin(elements, test_elements, **kwargs)
torch.isin = patched_isin
from tqdm import tqdm # 진행률 알려주는 라이브러리
from views.login_view import show_login_page
from views.report_view import show_main_interface, show_report_page, show_detail, show_detail_common
from services.db_service import get_db_modules
from services.model_service import get_model_modules


import pandas as pd
import plotly.express as px
import streamlit.components.v1 as components
import tempfile
import os
import zipfile
import shutil
import numpy as np
import librosa
import torch
try:
    import tensorflow as tf
except Exception as e:
    print(f"TensorFlow 로드 실패, CPU 전용으로 fallback: {e}")
    os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
    os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'false'
    import tensorflow as tf
    tf.config.set_visible_devices([], 'GPU')


from pathlib import Path
if sys.platform.startswith('win'):
    WINOS=True
    print("현재 운영체제는 윈도우입니다.")
else: WINOS = False

from services.db_service import (
    get_reports
)
from utils.style_utils import (
    apply_custom_css
)
from utils.footer_utils import add_footer
from services.auth_service import authenticate_user

from services.upload_service import zip_upload, get_connection

spinner.__exit__(None, None, None)

apply_custom_css()


def main():
    # 세션 상태 초기화
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user_info = None
        st.session_state.current_page = "리포트"
        st.session_state.view_mode = "list"
        st.session_state.selected_report = None
        st.session_state.upload_completed=False

    # 첫화면: 로그인화면 / 환자정보등록화면
    if not st.session_state.logged_in:
        show_login_page()
    elif st.session_state.upload_completed:
        show_main_interface(st.session_state.patient_id,st.session_state.path_info) 
    else:
        BASE_DIR = Path(__file__).parent
        patient_csv = BASE_DIR / "patient_id.csv"
        patient_id = st.selectbox("환자ID를 입력하세요.",pd.read_csv(patient_csv)['patient_id'].tolist())
        patient_id=str(patient_id)
        st.session_state.patient_id=patient_id

        # confirm_btn=st.button("확인")
        # if confirm_btn:
        uploaded_file = st.file_uploader("폴더를 압축(zip)한 파일을 업로드하세요.", type=['zip'])
        col1, col2, col3 = st.columns([2.5, 2.5, 5])
        with col1:
            btn_skip=st.button("업로드 스킵")
            if btn_skip & ('patient_id' in st.session_state):
                # DB에서 order_num=1인 path_info 조회
                conn = get_connection()
                cursor = conn.cursor()
                # ============================================================================
                # MySQL cursor unread result 오류 수정 - 2025.08.22 수정
                # 첫 번째 쿼리를 실행했으면 결과를 소비해야 함
                # ============================================================================
                sql = 'SELECT MAX(ORDER_NUM) FROM assess_lst WHERE PATIENT_ID = %s'
                cursor.execute(sql, (patient_id,))
                cursor.fetchone()  # 결과를 소비하여 unread result 방지
                order_num = '1'
                
                sql = "SELECT A.PATIENT_ID,A.ORDER_NUM,A.ASSESS_TYPE,A.QUESTION_CD,A.QUESTION_NO,A.MAIN_PATH,A.SUB_PATH,A.FILE_NAME FROM ASSESS_FILE_LST A, CODE_MAST C WHERE C.CODE_TYPE = 'ASSESS_TYPE' AND A.ASSESS_TYPE = C.MAST_CD AND A.QUESTION_CD=C.SUB_CD AND A.PATIENT_ID = %s AND A.ORDER_NUM = %s ORDER BY A.ASSESS_TYPE, C.ORDER_NUM, A.QUESTION_NO"
                cursor.execute(sql, (str(patient_id), str(order_num)))
                rows = cursor.fetchall()

                path_info = pd.DataFrame(rows, columns=['PATIENT_ID','ORDER_NUM','ASSESS_TYPE','QUESTION_CD','QUESTION_NO','MAIN_PATH','SUB_PATH','FILE_NAME'])
                cursor.close()
                conn.close()
                st.session_state.upload_completed=True
                st.session_state.model_completed=True
                st.session_state.skip=True
                st.session_state.order_num=order_num
                st.session_state.path_info=path_info
                st.rerun()
        with col2:
            if uploaded_file is not None:
                btn_apply = st.button("파일 업로드", key="upload_btn")
                if btn_apply:
                    order_num,path_info=zip_upload(btn_apply,patient_id,uploaded_file)
                    st.session_state.upload_completed=True
                    st.session_state.order_num,st.session_state.path_info=order_num,path_info
                    st.rerun()

if __name__ == "__main__":
    main()

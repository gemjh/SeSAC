import os
# TensorFlow 설정 (import 전에 먼저 설정)
os.environ['DISABLE_MLCOMPUTE'] = '1'
os.environ['TF_METAL'] = '0'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TF_NUM_INTEROP_THREADS'] = '1'
os.environ['TF_NUM_INTRAOP_THREADS'] = '1'

import utils.env_utils as set_env
set_env.activate_conda_environment()
import streamlit as st
from views.login_view import show_login_page
from views.report_view import show_main_interface, show_report_page, show_clap_a_detail, show_clap_d_detail, show_detail_common
from services.db_service import get_db_modules
from services.model_service import get_model_modules
# 페이지 설정
st.set_page_config(
    page_title="CLAP",
    page_icon="👋",
    layout="wide",
    initial_sidebar_state="expanded"
)
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
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
import tensorflow as tf


from pathlib import Path
if sys.platform.startswith('win'):
    WINOS=True
    print("현재 운영체제는 윈도우입니다.")
else: WINOS = False

# ------------------- db 폴더 경로 통일하려고 씀, 최종적으로는 삭제 필요 -------------------
# project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# sys.path.insert(0, os.path.join(os.path.dirname(project_root), '0812'))

# 동적 import를 위해 모듈들을 함수 안에서 import



        # st.session_state.loading_all_ok = True
from services.db_service import (
    get_reports
)
from utils.style_utils import (
    apply_custom_css, 
    create_evaluation_table_html, 
    create_word_level_table, 
    create_sentence_level_table
)
from services.auth_service import authenticate_user

from services.upload_service import zip_upload

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
        show_main_interface(st.session_state.patient_id) 
    else:
        BASE_DIR = Path(__file__).parent
        patient_csv = BASE_DIR / "patient_id.csv"
        patient_id = st.selectbox("환자ID를 입력하세요.",pd.read_csv(patient_csv)['patient_id'].tolist())
        # confirm_btn=st.button("확인")
        # if confirm_btn:
        uploaded_file = st.file_uploader("폴더를 압축(zip)한 파일을 업로드하세요.", type=['zip'])
        if uploaded_file is not None:
            btn_apply = st.button("파일 업로드")
            if btn_apply:
                patient_id=str(patient_id)
                path_info=zip_upload(patient_id,uploaded_file,btn_apply)
                st.session_state.upload_completed=True
                st.session_state.patient_id=patient_id
                st.session_state.path_info=path_info
                st.rerun()

if __name__ == "__main__":
    main()

import streamlit as st
# 페이지 설정
st.set_page_config(
    page_title="CLAP",
    page_icon="👋",
    layout="wide",
    initial_sidebar_state="expanded"
)
import os
import logging
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
from ui.utils.env_utils import activate_conda_environment

spinner = st.spinner('환경 설정 중...')
spinner.__enter__()
activate_conda_environment()
try:
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
    # try:
    from tqdm import tqdm # 진행률 알려주는 라이브러리
    from ui.views.login_view import show_login_page
    from ui.views.report_view import show_main_interface
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
    from ui.services.model_service import model_process


    # GPU 실행 시 tensorflow 설치 오류 방지
    try:
        import tensorflow as tf
    except Exception as e:
        print(f"TensorFlow 로드 실패, CPU 전용으로 fallback: {e}")
        os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
        os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'false'
        import tensorflow as tf
        tf.config.set_visible_devices([], 'GPU')

    # 운영체제 
    from pathlib import Path
    if sys.platform.startswith('win'):
        WINOS=True
        print("현재 운영체제는 윈도우입니다.")
    else: WINOS = False

    from services.db_service import (
        get_reports
    )
    from services.api_client import APIClient
    from utils.style_utils import (
        apply_custom_css
    )

    from services.auth_service import authenticate_user

    from services.upload_service import zip_upload
    apply_custom_css()

except ImportError as e:
    spinner.__exit__(None, None, None)
    st.warning("일시적인 오류가 발생했습니다. 페이지를 새로고침해 주세요")
    print(e)
    st.session_state.clear()
    st.stop()

spinner.__exit__(None, None, None)


def fetch_existing_path_info(patient_id: str):
    """기존 업로드 데이터의 파일 정보를 DB에서 조회"""
    try:
        assessments = APIClient.get_assessments(patient_id)
        if not assessments:
            return None, None
        
        latest = max(
            assessments,
            key=lambda item: int(item.get('order_num', 0) or 0)
        )
        order_num = latest.get('order_num')
        if not order_num:
            return None, None
        
        files = APIClient.get_assessment_files(patient_id, int(order_num))
        if not files:
            return None, None
        
        path_info = pd.DataFrame(files)
        return int(order_num), path_info
    except Exception as e:
        logging.error(f"기존 파일 정보 조회 실패: {e}")
        return None, None


def main():
    btn_apply =False

    # 테스트용(주석해제 시 파일업로드 패스)
    # st.session_state.upload_completed=True
    # patient_id=1001
    # st.session_state.patient_id=patient_id
    # path_info=[]
    # st.session_state.path_info=path_info
    # uploaded_file=[]

    # 세션 상태 초기화
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user_info = None
        st.session_state.current_page = "리포트"
        st.session_state.view_mode = "list"
        st.session_state.upload_completed=False

    # 첫화면: 로그인화면 / 환자정보등록화면
    if not st.session_state.logged_in:
        show_login_page()
    # 파일이 등록된 경우
    elif st.session_state.upload_completed:
        # 리포트 메인 이동
        show_main_interface(st.session_state.patient_id,st.session_state.path_info) 
    # 파일이 등록되지 않은 경우
    else:
        # UI 플레이스홀더 생성
        # ui_placeholder = st.empty()
        
        # with ui_placeholder.container():
            BASE_DIR = Path(__file__).parent
            patient_csv = BASE_DIR / "patient_id.csv"
            patient_id = st.selectbox("환자ID를 입력하세요.",pd.read_csv(patient_csv)['patient_id'].tolist())
            patient_id=str(patient_id)
            st.session_state.patient_id=patient_id

            uploaded_file = st.file_uploader("폴더를 압축(zip)한 파일을 업로드하세요.", type=['zip'])
            skip_upload = st.button("업로드 스킵", key="skip_btn")
            if skip_upload:
                if st.session_state.get('patient_id'):
                    order_num, path_info = fetch_existing_path_info(st.session_state.patient_id)
                    if path_info is None or path_info.empty:
                        st.warning("DB에서 파일 정보를 찾을 수 없습니다.")
                    else:
                        st.session_state.path_info = path_info
                        st.session_state.order_num = order_num
                        st.session_state.upload_completed = True
                        st.rerun()
                else:
                    st.warning("환자 ID를 먼저 선택하세요.")
            col1, col2 = st.columns([2.5, 7.5])
            with col1:
                # zip파일이 등록되면 파일 업로드 버튼 보임
                if uploaded_file is not None:
                    btn_apply = st.button("파일 업로드", key="upload_btn")
                    
    if btn_apply:
        st.session_state.path_info=loading(btn_apply,patient_id,uploaded_file)
        st.session_state.upload_completed=True
        st.rerun()

def loading(btn_apply,patient_id,uploaded_file):
    # import streamlit.components.v1 as components
    # 로딩 애니메이션 시작
    components.html("""
    <div style="
        position: fixed;
        top: 0; left: 0; width: 100vw; height: 100vh;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        backdrop-filter: blur(8px);
        z-index: 99999;
    ">
        <div style="
            border: 8px solid rgba(255,255,255,0.3);
            border-top: 8px solid #ffffff;
            border-radius: 50%;
            width: 60px;
            height: 60px;
            margin-bottom: 20px;
            animation: spin 1s linear infinite;
        "></div>
        <p style="
            margin: 0; 
            font-size: 24px; 
            color: white; 
            font-weight: bold;
            text-align: center;
            letter-spacing: 1px;
        ">분석 중입니다...</p>
    </div>
    <style>
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    </style>
    """, height=800)
    
    # ------------- zip파일 처리 -----------------
    order_num,path_info=zip_upload(btn_apply,patient_id,uploaded_file)

    # ------------- 모델 인스턴스 -----------------              
    fin_scores=model_process(path_info)

    # ------------- 결과 DB 저장 -----------------
    try:
        from services.db_service import save_scores_to_db
        save_scores_to_db(fin_scores,order_num)
        print("점수가 성공적으로 DB에 저장되었습니다.")
        
        # 로딩 제거
        components.html("")  
    except Exception as e:
        print(f"DB 저장 중 오류 발생: {e}")
    return path_info
    

if __name__ == "__main__":
    main()

import streamlit as st
# 페이지 설정
st.set_page_config(
    page_title="CLAP",
    page_icon="👋",
    layout="wide",
    initial_sidebar_state="expanded"
)
import sys
import os
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
from transformers import WhisperProcessor, WhisperForConditionalGeneration
from tensorflow.keras.models import load_model
from pathlib import Path
if sys.platform.startswith('win'):
    WINOS=True
    print("현재 운영체제는 윈도우입니다.")
else: WINOS = False

# TensorFlow 로딩 상태 표시
# if 'tf_loaded' not in st.session_state:
#     with st.spinner('TensorFlow 로딩 중...'):
#         import tensorflow as tf
#         st.session_state.tf_loaded = True


# ------------------- db 폴더 경로 통일하려고 씀, 최종적으로는 삭제 필요 -------------------
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(project_root), '0812'))

from db.src import (
    model_comm,
    report_main
)
# print(sys.path)
# if 'loading_all_ok' not in st.session_state:
#     with st.spinner('모델 로딩 중...'):
from models import (
    talk_pic,
    ah_sound,
    ptk_sound,
    talk_clean
)


        # st.session_state.loading_all_ok = True
from data_utils import (
    evaluation_data, 
    get_reports
)
from ui_utils import (
    apply_custom_css, 
    create_evaluation_table_html, 
    create_word_level_table, 
    create_sentence_level_table
)
from zip_upload3 import zip_upload
from auth_utils import authenticate_user




apply_custom_css()


def main():
    # 세션 상태 초기화
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user_info = None
        st.session_state.current_page = "리포트"
        st.session_state.view_mode = "list"
        st.session_state.selected_report = None
    
    # 로그인 상태 확인
    if not st.session_state.logged_in:
        show_login_page()
    else:
        # 환자 정보 등록 확인
        if 'patients_info' not in st.session_state:
            zip_upload()
        else:
            show_main_interface()
    


def show_login_page():
    """로그인 페이지"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.title("👋 CLAP")
        st.subheader("의료 검사 시스템")
        
        with st.form("login_form"):
            user_id = st.text_input("id", placeholder="user")
            password = st.text_input("비밀번호", type="password", placeholder="d")
            
            if st.form_submit_button("로그인", use_container_width=True):
                if user_id and password:
                    if authenticate_user(user_id, password):
                        st.session_state.logged_in = True
                        st.session_state.user_info = {'user_id': user_id}
                        st.rerun()
                    else:
                        st.error("로그인 정보가 올바르지 않습니다.")
                else:
                    st.error("id와 비밀번호를 입력해주세요.")
        
        st.info("데모 계정 - id: user, 비밀번호: d")

def show_main_interface():
    # all_patient_info=''
    blnk=pd.DataFrame({'patient_id':["선택"]})
    msg, ret_df=report_main.get_patient_lst()
    all_patient_info=ret_df.copy()
    all_patient_info.columns = ["patient_id", "name","sex", "age"]
    if st.button("< 뒤로가기"):
        st.session_state.view_mode = "list"
        # patient_info_str = st.selectbox("환자번호",pd.concat([blnk,all_patient_info['patient_id']]))
        # patient_info=all_patient_info[all_patient_info['patient_id']==patient_info_str]
        st.rerun()
    # 사이드바
    with st.sidebar:
        st.title("👋 CLAP")
        patient_file = st.file_uploader("zip파일 업로드", type="zip")

        save_dir = tempfile.gettempdir()
        os.makedirs(save_dir, exist_ok=True)    # 동명파일이면 덮어씀



        if patient_file:
            # ZIP 저장 경로
            save_path = os.path.join(save_dir, patient_file.name)
            with open(save_path, "wb") as f:
                f.write(patient_file.getbuffer())

            # 압축 해제 경로 (zip 확장자 제거)
            extract_dir = os.path.join(save_dir, os.path.splitext(patient_file.name)[0])
            print(f'----------------------------- 압축 해제 경로: {extract_dir} -----------------------------\n\n\n')
            
            # 기존 폴더 있으면 삭제
            if os.path.exists(extract_dir):
                shutil.rmtree(extract_dir)
            os.makedirs(extract_dir, exist_ok=True)

            # 압축 해제
            with zipfile.ZipFile(save_path, "r") as zip_ref:
                zip_ref.extractall(extract_dir)

            # st.success(f"압축 해제 완료! 폴더 경로: {extract_dir}")
            
            # 압축 해제된 파일 구조 출력 (디버깅용)
            # def print_directory_structure(path, prefix=""):
            #     try:
            #         items = os.listdir(path)
            #         for item in items:
            #             item_path = os.path.join(path, item)
            #             print(f"{prefix}{item}")
            #             if os.path.isdir(item_path) and len(prefix) < 10:  # 깊이 제한
            #                 print_directory_structure(item_path, prefix + "  ")
            #     except:
            #         pass
            
            # print("=== 압축 해제된 파일 구조 ===")
            # print_directory_structure(extract_dir)
            # print("=== 파일 구조 끝 ===")

        patient_info_str = st.selectbox("환자번호",pd.concat([blnk,all_patient_info['patient_id']]))
        patient_info=all_patient_info[all_patient_info['patient_id']==patient_info_str]
        if ("confirmed" not in st.session_state) or (patient_info_str=="선택") or (patient_file is None):
            st.session_state.confirmed = False
        # if not st.session_state.confirmed:
            # if (patent_file is not None) & (patient_info_str!="선택"):
        else:
            st.session_state.confirmed = True

                    # 메뉴: 있어야 할까?
                    # menu_items = ["평가", "재활", "리포트"]
                    # for item in menu_items:
                    #     prefix = "🟡 " if item == st.session_state.current_page else ""
                    #     button_type = "primary" if item == st.session_state.current_page else "secondary"
                    #     if st.button(f"{prefix}{item}", key=f"menu_{item}", type=button_type, use_container_width=True):
                    #         st.session_state.current_page = item
                    #         st.session_state.view_mode = "list"
                    #         if item != "리포트":
                    #             st.info(f"{item} 기능은 개발 중입니다.")
                    #         st.rerun()
                        # 메인 컨텐츠

        if not patient_info.empty:
            # 초기값 설정
            if 'selected_filter' not in st.session_state:
                st.session_state.selected_filter = "CLAP_A"
            
            st.write(f"**{patient_info['name'].iloc[0]} {patient_info['age'].iloc[0]}세**")
            st.write(f"환자번호: {patient_info['patient_id'].iloc[0]}")
            st.write(f"성별: {'여성' if patient_info['sex'].iloc[0]==1 else '남성'}")
        # 로그아웃 버튼
        if st.button("로그아웃", key="logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user_info = None
            st.rerun()

            
    if st.session_state.confirmed and 'selected_filter' in st.session_state:

        # import sys
        # sys.path.append(r'../../db/src')
        # base_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), '0812')        
        # base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # print(base_path)
        # print("--------------------- extract_dir ---------------------\n\n\n")
        # print(extract_dir)
        # print("--------------------- extract_dir ---------------------\n\n\n")
        
        msg, ret = model_comm.get_file_lst()
        # print(ret)
        # wav_label_pairs = []
        print("--------------------- extract_dir ---------------------\n\n\n")
        print(extract_dir)
        print("--------------------- extract_dir ---------------------\n\n\n")
        
        ah_sound_path=[]
        ptk_sound_path=[]
        ltn_rpt_path=[]
        guess_end_path=[]
        read_clean_path=[]
        say_ani_path=[]
        say_obj_path=[]
        talk_clean_path=[]
        talk_pic_path=[]
        for i in range(len(ret)):
            # if ret.loc[i, 'Path'].split('/')==extract_dir.split('/')[-1]:
            # if WINOS == False:
            # patient_info_str = st.selectbox("환자번호",pd.concat([blnk,all_patient_info['patient_id']]))
            p = Path(str(ret.loc[i, 'Path']))  # 문자열 → Path (OS에 맞게 해석)
            # print(p)
            # print("--------------------- p ---------------------\n\n\n")

            parts = p.parts

            # 환자번호가 경로 어딘가에 있는지부터 확인 (Windows의 드라이브/루트 문제 회피)
            if patient_info_str not in parts:
                continue

            # 환자번호가 나타나는 위치를 기준으로 '그 뒤'를 상대 경로로 사용
            idx = parts.index(patient_info_str)
            # 환자번호 이후의 경로(파일명 포함 가능)
            tail = Path(*parts[idx+1:])

            # ret 쪽 파일명이 tail의 마지막과 일치하는지 확인해 중복 추가 방지
            filename = str(ret.loc[i, 'File Name'])
            # if tail.name == filename:
            #     relative_dir = tail.parent        # 이미 파일명이 포함되어 있었으면 디렉토리만
            # else:
            #     relative_dir = tail               # 파일명이 포함되지 않았다면 그대로 사용

            # 최종 경로 생성
            # file_path = Path(extract_dir) / relative_dir / filename
            file_path = Path(extract_dir) / tail / filename


            # 필요하다면 문자열로 변환
            file_path = str(file_path)
            print(file_path)
            print("--------------------- file_path ---------------------\n\n\n")
                # 파일 존재 여부 확인
            if not os.path.exists(file_path):
                st.warning(f"❌ 파일 없음: {file_path}")
                # print(f"❌ 파일 없음: {file_path}")
                break

                # 대안 경로들 시도
            #     alt_paths = [
            #         os.path.join(extract_dir, f"{ret.loc[i, 'File Name']}"),  # 최상위 경로
            #         os.path.join(extract_dir, patient_info_str, relative_path, f"{ret.loc[i, 'File Name']}"),  # 환자번호 포함
            #     ]
            #     for alt_path in alt_paths:
            #         if os.path.exists(alt_path):
            #             print(f"✅ 대안 경로 발견: {alt_path}")
            #             file_path = alt_path
            #             break
            #     else:
            #         print(f"❌ 모든 대안 경로 실패 - 스킵")
            #         continue
            # else:
            #     print(f"✅ 파일 발견: {file_path}")
            
            t = (file_path, int(ret.loc[i, 'Score(Refer)']), 0 if ret.loc[i, 'Score(Alloc)'] == None else int(ret.loc[i, 'Score(Alloc)']))
            print(f"최종 경로: {t[0]}")
            print("--------------------- t ---------------------\n\n\n")
            # d일때
            # print(ret.loc[i, 'Path'].split('/')[1])
            # Path(ret.loc[i, 'Path']).parts[0]==patient_info_str
            if Path(ret.loc[i, 'Path']).parts[1]=='clap_d':
                # print(ret.loc[i, 'Path'].split('/')[2])   
                # print("--------------------- clap_d/? ---------------------\n\n\n")
                
                if (Path(ret.loc[i, 'Path']).parts[2]=='0'):
                    ah_sound_path.append(t[0])
                    # print(ah_sound_path)
                    # print(ah_sound.analyze_pitch_stability(ah_sound_path[0]))
                    if 'ah_sound_result' not in st.session_state:

                        st.session_state.ah_sound_result=ah_sound.analyze_pitch_stability(ah_sound_path[0])
                        print('-------------- ah_sound modeling(1번째 값) ---------------\n\n\n')

                elif (Path(ret.loc[i, 'Path']).parts[2]=='1'):
                    ptk_sound_path.append(t[0])
                    if 'ptk_sound_result' not in st.session_state:
                        st.session_state.ptk_sound_result=ptk_sound.count_peaks_from_waveform(ptk_sound_path[0])
                    print('-------------- ptk_sound modeling(1번째 값) ---------------\n\n\n')
                elif (Path(ret.loc[i, 'Path']).parts[2]=='2'):
                    talk_clean_path.append(t[0])
                    if 'talk_clean_result' not in st.session_state:
                        st.session_state.talk_clean_result=talk_clean.main(talk_clean_path[0])
                    print('-------------- talk_clean modeling(1번째 값) ---------------\n\n\n')
                elif (Path(ret.loc[i, 'Path']).parts[2]=='3'):
                    read_clean_path.append(t[0])
                # else도 고려?

            # a일때
            elif (Path(ret.loc[i, 'Path']).parts[1]=='clap_a'):
                if (Path(ret.loc[i, 'Path']).parts[2]=='3'):
                    ltn_rpt_path.append(t[0])
                elif  (Path(ret.loc[i, 'Path']).parts[2]=='4'):
                    guess_end_path.append(t[0])
                elif (Path(ret.loc[i, 'Path']).parts[2]=='5'):
                    say_obj_path.append(t[0])
                elif (Path(ret.loc[i, 'Path']).parts[2]=='6'):
                    say_ani_path.append(t[0])
                elif (Path(ret.loc[i, 'Path']).parts[2]=='7'):
                    talk_pic_path.append(t[0])
                    if 'talk_pic_result' not in st.session_state:
                        st.session_state.talk_pic_result=talk_pic.score_audio(talk_pic_path[0])
                    print('-------------- talk_pic modeling(1번째 값) ---------------\n\n\n')
                    talk_pic_path.append(t[0])
            # print("---------------------  ---------------------\n\n\n")
        print(
        ah_sound_path,ptk_sound_path,ltn_rpt_path,guess_end_path,read_clean_path,
        say_ani_path,
        say_obj_path,
        talk_clean_path,
        talk_pic_path)
        print("--------------------- path ---------------------\n\n\n")
        # print('------------------------- 모델링 구간 ---------------------------\n\n\n')

        # path_names = [
        #     'ah_sound', 'ptk_sound', 'talk_clean', 'read_clean',
        #     'ltn_rpt', 'guess_end', 'say_obj', 'say_ani', 'talk_pic'
        # ]
        # path_codes=['clap_d/0','clap_d/1','clap_d/2','clap_d/3','clap_a/3','clap_a/4','clap_a/5','clap_a/6','clap_a/7']
        
        # with st.spinner('모델 로딩 중...'):
            

        # print('------------------------- 모델링 완료 ---------------------------\n\n\n')


            # wav_label_pairs.append(t)

        if st.session_state.view_mode == "list":
            show_report_page(patient_info['patient_id'].iloc[0] if not patient_info.empty else '')
        elif st.session_state.view_mode == "clap_a_detail":
            show_clap_a_detail()
        elif st.session_state.view_mode == "clap_d_detail":
            show_clap_d_detail()
            # 환자 정보 표시
            st.divider()
    else:
        st.info("zip파일과 환자 번호를 모두 선택해 주세요")
        patient_info_str = '선택'
        patient_info=all_patient_info[all_patient_info['patient_id']==patient_info_str]


def show_report_page(patient_id):

    # st.header("리포트")
    
    # 탭 버튼들
    col1, col2, col3 = st.columns([2, 2, 6])
    
    with col1:
        if st.button("CLAP-A", key="clap_a_btn", type="primary" if st.session_state.selected_filter == "CLAP_A" else "secondary", disabled=False):
            st.session_state.selected_filter = "CLAP_A"
            st.rerun()
    
    with col2:
        if st.button("CLAP-D", key="clap_d_btn", type="primary" if st.session_state.selected_filter == "CLAP_D" else "secondary", disabled=False):
            st.session_state.selected_filter = "CLAP_D"
            st.rerun()
    
    # 리포트 목록
    reports_df = get_reports(patient_id, st.session_state.selected_filter)

    if not reports_df.empty:
        for idx, row in reports_df.iterrows():
            with st.container():
                col1, col2, col3, col4, col5,col6,col7 = st.columns([0.5, 2, 3,2,2, 0.5, 2])
                
                with col1:
                    st.checkbox("", key=f"checkbox_{idx}")
                
                with col2:
                    st.markdown(
                        f"<div style='line-height: 1.8; font-size: 25px;'><b>{row['검사유형'].replace('_','-')}</b></div>",
                        unsafe_allow_html=True
                    )
                with col3:
                    st.markdown(
                        f"<div style='line-height: 1.8; font-size: 20px;'>검사일자 <b>{row['검사일자']}</b></div>",
                        unsafe_allow_html=True
                    )
                with col4:
                    st.markdown(
                        f"<div style='line-height: 1.8; font-size: 20px;'>의뢰인 <b>{row['의뢰인']}</b></div>",
                        unsafe_allow_html=True
                    )                    
                with col5:
                    st.markdown(
                        f"<div style='line-height: 1.8; font-size: 20px;'>검사자 <b>{row['검사자']}</b></div>",
                        unsafe_allow_html=True
                    )                    
                with col7:
                    if st.button("확인하기 〉", key=f"confirm_{idx}"):
                        st.session_state.selected_report = {
                            'type': row['검사유형'],
                            'date': row['검사일자'],
                            'patient_id': row['patient_id']
                        }
                        if row['검사유형'] == "CLAP_A":
                            st.session_state.view_mode = "clap_a_detail"
                        else:
                            st.session_state.view_mode = "clap_d_detail"
                        st.rerun()
                
                st.divider()
    else:
        st.info(f"{st.session_state.selected_filter} 검사 결과가 없습니다.")

def show_detail_common():
    st.header(st.session_state.selected_filter.replace('_','-'))
    st.subheader(f"전산화 언어 기능 선별 검사({'실어증' if st.session_state.selected_filter=='CLAP_A' else '마비말장애' if st.session_state.selected_filter=='CLAP_D' else ''}) 결과지")

    # 리포트 데이터 가져오기
    report = st.session_state.selected_report
    patient_info = get_reports(report['patient_id']).iloc[0]
    # print(patient_info)
    # print("--------------------- patient_info ---------------------\n\n\n")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write(f"의뢰 기관(과)/의뢰인 {patient_info['의뢰인']}")
        st.write(f"이름 {patient_info['name']} ")
        st.write(f"교육연수 NN")
        st.write(f"방언 NN")

    with col2:
        st.write(f"검사자명 {patient_info['검사자']}")
        st.write(f"성별 {'여자' if patient_info['sex']==1 else '남자'}")
        st.write(f"문해여부 NN")
        st.write(f"발병일 NN")

    with col3:
        st.write(f"검사일자 {patient_info['검사일자']} ")
        st.write(f"개인번호 {patient_info['patient_id']}")

    st.write(f"진단명 NN")
    st.write(f"주요 뇌병변 I NN")
    st.write(f"주요 뇌병변 II NN")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.write(f"**편마비** ")
    with col2:
        st.write(f"**무시증** ")
    with col3:
        st.write(f"**시야결손** ")

    st.write(f"**기타 특이사항** ")
    st.divider()


def show_clap_a_detail():
    show_detail_common()
    # 리포트 데이터 가져오기
    report = st.session_state.selected_report
    clap_a_data = get_reports(report['patient_id'], 'CLAP_A')
    
    # 검사 결과
    if not clap_a_data.empty:
        st.subheader("결과 요약")
        st.write('그림보고 말하기:',st.session_state.talk_pic_result,'점')
        # 차트

def show_clap_d_detail():
    """CLAP-D 상세 리포트 페이지"""
    show_detail_common()
    report = st.session_state.selected_report
    clap_d_data = get_reports(report['patient_id'], 'CLAP_D')

    # 검사 결과

    if not clap_d_data.empty:
        st.subheader("결과 요약")

        st.write('아 소리내기:',st.session_state.ah_sound_result)
        st.write('퍼터커 소리내기:',st.session_state.ptk_sound_result)
        st.write('또박또박 말하기:',st.session_state.talk_clean_result)
        word_level,sentence_level,consonant_word,vowel_word,consonant_sentence='N','N','N','N','N'
        max_time,pa_avg,ta_avg,ka_avg,ptk_avg='N','N','N','N','N'
        total_score = 'N'
        # total_score = a_sound + pa_repeat + ta_repeat + ka_repeat + ptk_repeat + word_level + sentence_level
        
        
        # 평가 리스트
        a_sound, pa_sound, ta_sound, ka_sound, ptk_sound = evaluation_data
        
        evaluation_list = [a_sound, pa_sound, ta_sound, ka_sound, ptk_sound]

        # for문으로 각 평가 테이블 생성
        for eval_item in evaluation_list:
            html_content = create_evaluation_table_html(eval_item)
            # st.components.v1.html 사용 - 높이는 항목 수에 따라 동적으로 계산
            height = 150 + (len(eval_item['items']) * 35)  # 기본 높이 + 각 행당 35px
            components.html(html_content, height=height)

if __name__ == "__main__":
    main()
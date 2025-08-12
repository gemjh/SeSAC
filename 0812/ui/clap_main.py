import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit.components.v1 as components
import tempfile
import os

# TensorFlow 로딩 상태 표시
# if 'tf_loaded' not in st.session_state:
#     with st.spinner('TensorFlow 로딩 중...'):
#         import tensorflow as tf
#         st.session_state.tf_loaded = True
# print('tf 임포트 완료')
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# print(sys.path)
from models.ptk_sound import ptk_sound as ptk
from data_utils import (
    evaluation_data, 
    get_reports, 
    get_clap_a_details, 
    get_clap_d_details
)
from ui_utils import (
    apply_custom_css, 
    get_common_info, 
    create_evaluation_table_html, 
    create_word_level_table, 
    create_sentence_level_table
)
from auth_utils import authenticate_user


# 페이지 설정
st.set_page_config(
    page_title="CLAP",
    page_icon="👋",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
        
        st.info("데모 계정 - id: user, 비밀번호: demo123")

def show_main_interface():
    # 환자 정보: 일단 1001
    patient_info = get_reports("1001")
    
    # 사이드바
    with st.sidebar:
        st.title("👋 CLAP")

        # 메뉴
        menu_items = ["평가", "재활", "리포트"]
        for item in menu_items:
            prefix = "🟡 " if item == st.session_state.current_page else ""
            button_type = "primary" if item == st.session_state.current_page else "secondary"
            if st.button(f"{prefix}{item}", key=f"menu_{item}", type=button_type, use_container_width=True):
                st.session_state.current_page = item
                st.session_state.view_mode = "list"
                if item != "리포트":
                    st.info(f"{item} 기능은 개발 중입니다.")
                st.rerun()

        # 환자 정보 표시
        st.divider()
        # print("-------------------------",patient_info,"-------------------",sep='\n')
        if not patient_info.empty:
            st.write(f"**{patient_info['name'].iloc[0]} {patient_info['age'].iloc[0]}세**")
            st.write(f"환자번호: {patient_info['patient_id'].iloc[0]}")
            st.write(f"성별: {patient_info['gender'].iloc[0]}")

        # 로그아웃 버튼
        if st.button("로그아웃", key="logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user_info = None
            st.rerun()

    # 메인 컨텐츠
    if st.session_state.current_page == "리포트":
        if st.session_state.view_mode == "list":
            show_report_page(patient_info['patient_id'].iloc[0] if not patient_info.empty else "1001")
        elif st.session_state.view_mode == "clap_a_detail":
            show_clap_a_detail()
        elif st.session_state.view_mode == "clap_d_detail":
            show_clap_d_detail()

def show_report_page(patient_id):
    # 초기값 설정
    if 'selected_filter' not in st.session_state:
        st.session_state.selected_filter = "CLAP_A"
    
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
                col1, col2, col3, col4, col5 = st.columns([0.1, 2, 5, 0.5, 1])
                
                with col1:
                    st.checkbox("", key=f"checkbox_{idx}")
                
                with col2:
                    st.write(f"**{row['검사유형']}**")
                
                with col3:
                    st.write(f"검사일자: {row['검사일자']} | 의뢰인: {row['의뢰인']} | 검사자: {row['검사자']}")
                
                with col5:
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

def get_common(patient_id):
    report = st.session_state.selected_report
    patient_info = get_reports(report['patient_id']).iloc[0]
    get_common_info(patient_info, report['date'])


def show_clap_a_detail():
    """CLAP-A 상세 리포트 페이지"""
    if st.button("< 뒤로가기"):
        st.session_state.view_mode = "list"
        st.rerun()
    
    st.header("CLAP-A")
    st.subheader("전산화 언어 기능 선별 검사(실어증) 결과지")
    
    # 리포트 데이터 가져오기
    report = st.session_state.selected_report
    clap_a_data = get_clap_a_details(report['patient_id'], report['date'])
    
    get_common(report['patient_id'])
    
    
    # 검사 결과
    if not clap_a_data.empty:
        categories = clap_a_data['category'].unique()
        for category in categories:
            st.subheader(category)
            category_data = clap_a_data[clap_a_data['category'] == category]

            # talk_obj = st.file_uploader("물건 이름 말하기", type=['wav', 'mp3'], key="talk_obj", label_visibility="collapsed")
            # if talk_obj is not None:
            #     from models.talk_obj import irang as rang

            #     with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            #         tmp_file.write(talk_obj.getvalue())
            #         file_path = tmp_file.name
            #         pa_uploaded = rang.talk_obj(file_path)
            #         st.session_state.pa_uploaded = True
            #         st.rerun()


        # 결과 요약 차트
        col1, col2 = st.columns(2)
        with col1:
            fig = px.bar(clap_a_data, x='category', y='score',
                        title="문항별 점수", labels={'category': '검사항목', 'score': '점수'})
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig = px.bar(clap_a_data, x='category', y='score',
                        title="실어증 점수", labels={'category': '검사항목', 'score': '점수'})
            st.plotly_chart(fig, use_container_width=True)





def show_clap_d_detail():

    """CLAP-D 상세 리포트 페이지"""
    if st.button("< 뒤로가기"):
        st.session_state.view_mode = "list"
        st.rerun()
    
    st.header("CLAP-D")
    st.subheader("검사 결과지")
    
    # 리포트 데이터 가져오기
    report = st.session_state.selected_report
    clap_d_data = get_clap_d_details(report['patient_id'], report['date'])
    patient_info = get_reports(report['patient_id']).iloc[0]

    get_common(report['patient_id'])
    a_sound = 'N'


    # 파일 업로드 상태 관리를 위한 세션 상태 초기화
    if 'ah_uploaded' not in st.session_state:
        st.session_state.ah_uploaded = False
    if 'pa_uploaded' not in st.session_state:
        st.session_state.pa_uploaded = False
    if 'ta_uploaded' not in st.session_state:
        st.session_state.ta_uploaded = False
    if 'ka_uploaded' not in st.session_state:
        st.session_state.ka_uploaded = False
    if 'ptk_uploaded' not in st.session_state:
        st.session_state.ptk_uploaded = False
    
    if 'ah_result' not in st.session_state:
        st.session_state.ah_result = 'N'
    if 'pa_result' not in st.session_state:
        st.session_state.pa_result = 'N'
    if 'ta_result' not in st.session_state:
        st.session_state.ta_result = 'N'
    if 'ka_result' not in st.session_state:
        st.session_state.ka_result = 'N'
    if 'ptk_result' not in st.session_state:
        st.session_state.ptk_result = 'N'
            
    # 검사 결과
    if not clap_d_data.empty:
        st.subheader("결과 요약")


        word_level,sentence_level,consonant_word,vowel_word,consonant_sentence='N','N','N','N','N'

        max_time,pa_avg,ta_avg,ka_avg,ptk_avg='N','N','N','N','N'
        total_score = 'N'
        # total_score = a_sound + pa_repeat + ta_repeat + ka_repeat + ptk_repeat + word_level + sentence_level
        
        # 표모양만들기 1: borderline 넣어서 table 비슷하게 결과와 입력 필드 표시
        st.markdown('<div class="table-container">', unsafe_allow_html=True)
        
        # 테이블모양 헤더
        st.markdown('<div class="table-header">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([3, 3, 2])
        with col1:
            st.markdown('<div class="table-cell" style="border-right: 1px solid #ddd;"><b>문항</div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="table-cell" style="border-right: 1px solid #ddd;"><b>수행 결과</div>', unsafe_allow_html=True)
        with col3:
            st.markdown('<div class="table-cell"><b>점수</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 첫 번째 행 - 아 소리내기 (파일 업로더 포함)
        st.markdown('<div class="table-row">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([3, 3, 2])
        with col1:
            st.markdown('<div class="table-cell" style="border-right: 1px solid #ddd;">\'아\' 소리내기</div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="table-cell" style="border-right: 1px solid #ddd;">최대 발성시간 {max_time}초</div>', unsafe_allow_html=True)
        with col3:
            st.markdown('<div class="table-cell">', unsafe_allow_html=True)
            if not st.session_state.ah_uploaded:
                with st.container():
                    st.markdown('<div class="small-uploader">', unsafe_allow_html=True)
                    ah_sound_inline = st.file_uploader("아 소리 업로드", type=['wav', 'mp3'], key="ah_inline", label_visibility="collapsed")
                    st.markdown('</div>', unsafe_allow_html=True)

                    # ------------------------------------- 무한로딩때문에 일단 주석처리 -------------------------------------
                    if ah_sound_inline is not None:
                        import model.ah_sound as ah  
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                            tmp_file.write(ah_sound_inline.getvalue())
                            file_path = tmp_file.name
                            print("---------------------------\n\n\n")

                            ah_result = ah.analyze_pitch_stability(file_path)
                            print(ah_result)
                            print("---------------------------\n\n\n")
                            st.write(f"{ah_result}점")

                            st.session_state.ah_uploaded = True
                            st.rerun()
                    # ------------------------------------- 무한로딩 -------------------------------------

            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 두 번째 행 - 퍼 반복하기 (파일 업로더 포함)
        st.markdown('<div class="table-row">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([3, 3, 2])
        with col1:
            st.markdown('<div class="table-cell" style="border-right: 1px solid #ddd;">\'퍼\' 반복하기</div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="table-cell" style="border-right: 1px solid #ddd;">평균 횟수 {pa_avg}번</div>', unsafe_allow_html=True)
        with col3:
            st.markdown('<div class="table-cell">', unsafe_allow_html=True)
            if not st.session_state.pa_uploaded:
                with st.container():
                    st.markdown('<div class="small-uploader">', unsafe_allow_html=True)
                    pa_sound_inline = st.file_uploader("퍼 소리 업로드", type=['wav', 'mp3'], key="pa_inline", label_visibility="collapsed")
                    st.markdown('</div>', unsafe_allow_html=True)
                if pa_sound_inline is not None:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                        tmp_file.write(pa_sound_inline.getvalue())
                        file_path = tmp_file.name
                        st.session_state.pa_result = ptk.count_peaks_from_waveform(file_path)
                        st.session_state.pa_uploaded = True
                        st.rerun()
            st.write(f"{st.session_state.pa_result}점")
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 세 번째 행 - 터 반복하기 (파일 업로더 포함)
        st.markdown('<div class="table-row">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([3, 3, 2])
        with col1:
            st.markdown('<div class="table-cell" style="border-right: 1px solid #ddd;">\'터\' 반복하기</div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="table-cell" style="border-right: 1px solid #ddd;">평균 횟수 {ta_avg}번</div>', unsafe_allow_html=True)
        with col3:
            st.markdown('<div class="table-cell">', unsafe_allow_html=True)
            if not st.session_state.ta_uploaded:
                with st.container():
                    st.markdown('<div class="small-uploader">', unsafe_allow_html=True)
                    ta_sound_inline = st.file_uploader("터 소리 업로드", type=['wav', 'mp3'], key="ta_inline", label_visibility="collapsed")
                    st.markdown('</div>', unsafe_allow_html=True)
                if ta_sound_inline is not None:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                        tmp_file.write(ta_sound_inline.getvalue())
                        file_path = tmp_file.name
                        st.session_state.ta_result = ptk.count_peaks_from_waveform(file_path)
                        st.session_state.ta_uploaded = True
                        st.rerun()
            st.write(f"{st.session_state.ta_result}점")
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 네 번째 행 - 커 반복하기 (파일 업로더 포함)
        st.markdown('<div class="table-row">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([3, 3, 2])
        with col1:
            st.markdown('<div class="table-cell" style="border-right: 1px solid #ddd;">\'커\' 반복하기</div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="table-cell" style="border-right: 1px solid #ddd;">평균 횟수 {ka_avg}번</div>', unsafe_allow_html=True)
        with col3:
            st.markdown('<div class="table-cell">', unsafe_allow_html=True)
            if not st.session_state.ka_uploaded:
                with st.container():
                    st.markdown('<div class="small-uploader">', unsafe_allow_html=True)
                    ka_sound_inline = st.file_uploader("커 소리 업로드", type=['wav', 'mp3'], key="ka_inline", label_visibility="collapsed")
                    st.markdown('</div>', unsafe_allow_html=True)
                if ka_sound_inline is not None:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                        tmp_file.write(ka_sound_inline.getvalue())
                        file_path = tmp_file.name
                        st.session_state.ka_result = ptk.count_peaks_from_waveform(file_path)
                        st.session_state.ka_uploaded = True
                        st.rerun()
            st.write(f"{st.session_state.ka_result}점")
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 다섯 번째 행 - 퍼터커 반복하기 (파일 업로더 포함)
        st.markdown('<div class="table-row">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([3, 3, 2])
        with col1:
            st.markdown('<div class="table-cell" style="border-right: 1px solid #ddd;">\'퍼터커\' 반복하기</div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="table-cell" style="border-right: 1px solid #ddd;">평균 횟수 {ptk_avg}번</div>', unsafe_allow_html=True)
        with col3:
            st.markdown('<div class="table-cell">', unsafe_allow_html=True)
            if not st.session_state.ptk_uploaded:
                with st.container():
                    st.markdown('<div class="small-uploader">', unsafe_allow_html=True)
                    ptk_sound_inline = st.file_uploader("퍼터커 소리 업로드", type=['wav', 'mp3'], key="ptk_inline", label_visibility="collapsed")
                    st.markdown('</div>', unsafe_allow_html=True)
                if ptk_sound_inline is not None:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                        tmp_file.write(ptk_sound_inline.getvalue())
                        file_path = tmp_file.name
                        st.session_state.ptk_result = ptk.count_peaks_from_waveform(file_path)
                        st.session_state.ptk_uploaded = True
                        st.rerun()
            st.write(f"{st.session_state.ptk_result}점")
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 나머지 행들(더미데이터)
        st.markdown('<div class="table-row">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([3, 3, 2])
        with col1:
            st.markdown('<div class="table-cell" style="border-right: 1px solid #ddd;">또박또박 말하기 (단어수준)</div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="table-cell" style="border-right: 1px solid #ddd;">자음 정확도: {consonant_word}%<br>모음 정확도: {vowel_word}%</div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="table-cell">{word_level}점</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="table-row">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([3, 3, 2])
        with col1:
            st.markdown('<div class="table-cell" style="border-right: 1px solid #ddd;">또박또박 말하기 (문장수준)</div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="table-cell" style="border-right: 1px solid #ddd;">자음 정확도: {consonant_sentence}%</div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="table-cell">{sentence_level}점</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 합계 행
        st.markdown('<div class="total-row">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([3, 3, 2])
        with col1:
            st.markdown('<div class="table-cell" style="border-right: 1px solid #ddd;"><strong>합계</strong></div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="table-cell" style="border-right: 1px solid #ddd;"></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="table-cell"><strong>{total_score}점</strong></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)  # table-container 닫기

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
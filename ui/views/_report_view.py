from matplotlib.figure import figaspect
import streamlit as st
from views.login_view import show_login_page
from services.db_service import get_db_modules,get_reports
from services.model_service import (
    get_talk_pic, get_ah_sound, get_ptk_sound, get_talk_clean, 
    get_say_ani, get_ltn_rpt, get_say_obj, get_guess_end
)
from utils.style_utils import apply_custom_css
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import streamlit.components.v1 as components
import tempfile
import os
import pandas as pd
import base64
import matplotlib.pyplot as plt
import numpy as np
import logging
from ui.utils.env_utils import model_common_path
base_path=os.path.dirname(model_common_path())

apply_custom_css()


def show_main_interface(path_info):
    # 초기화
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "리포트"
    if 'view_mode' not in st.session_state:
        st.session_state.view_mode = "list"

    # 사이드바
    with st.sidebar:
        # CLAP 로고
        st.markdown("""
        <div style="display: flex; align-items: center; gap: 10px;margin-top: -50px;">
            <img src="data:image/png;base64,{}" width="50" />
            <h1 style="margin: 0; font-size: 2.5rem;">CLAP</h1>
        </div>
        """.format(
            __import__('base64').b64encode(open("ui/views/clap.png", "rb").read()).decode()
        ), unsafe_allow_html=True)
        st.divider()

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
        st.divider()     

        # 초기값 설정
        if 'selected_filter' not in st.session_state:
            st.session_state.selected_filter = "CLAP_A"
        # 사이드바용 환자 정보 조회(이름, 나이, 번호, 성별)
        patient_info=get_reports(st.session_state.patient_id)    
        # if patient_info is not None and len(patient_info) > 0:
        try:
            st.write(f"**{patient_info['PATIENT_NAME'].iloc[0]} {int(patient_info['AGE'].iloc[0])}세**")
            st.write(f"환자번호: {patient_info['PATIENT_ID'].iloc[0]}")
            st.write(f"성별: {'여성' if str(patient_info['SEX'].iloc[0])=='1' else '남성'}")
        except:
            st.write(f"**ㅇㅇ ㅇㅇ세**")
            st.write(f"환자번호: {st.session_state.patient_id}")
            st.write(f"성별: ㅇㅇ")                
        # else:
        #     st.write("환자 정보를 등록하면 여기 표시됩니다")

        st.divider()     

        # 로그아웃 버튼
        if st.button("로그아웃", key="logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()

        # 회사 로고
        # st.markdown("""
        # <div style="display: flex; align-items: center; gap: 10px; margin: auto; margin-left: 20px; padding-top: 20px;">
        #     <img src="data:image/jpeg;base64,{}" width="100"/>
        # </div>
        # """.format(
        #     __import__('base64').b64encode(open("ui/utils/logo.jpeg", "rb").read()).decode()
        # ), unsafe_allow_html=True)

        image_path=os.path.join(base_path,"ui/utils/logo.jpeg")
        add_easter_egg(image_path)
    
    # 리포트 메인화면 호출
    if st.session_state.current_page == "리포트":
        # 초기화면(검사유형 Select하지 않은 상태)
        if st.session_state.view_mode == "list":    
            show_report_page(patient_info['PATIENT_ID'].iloc[0] if not patient_info.empty else '')

        # DB 호출
        else:         
            _, report_main = get_db_modules()     
            _, ret_df =report_main.get_assess_score(st.session_state.patient_id,st.session_state.order_num,st.session_state.selected_filter)

        # fin_scores(검사결과 데이터) 포맷 예시
        # fin_scores = {
        #     'LTN_RPT':ltn_rpt_result,
        #     'GUESS_END':guess_end_result,
        #     'SAY_OBJ':say_obj_result,
        #     'SAY_ANI':say_ani_result,
        #     'TALK_PIC':talk_pic_result,
        #     'AH_SOUND':ah_sound_result,
        #     'P_SOUND':ptk_sound_result[0],
        #     'T_SOUND':ptk_sound_result[1],
        #     'K_SOUND':ptk_sound_result[2],
        #     'PTK_SOUND':ptk_sound_result[3],
        #     'TALK_CLEAN':talk_clean_result
        # }
            fin_scores = dict(zip(ret_df['QUESTION_CD'], ret_df['SCORE']))
            show_detail_assess(fin_scores)
        
            # 환자 정보 표시
            st.divider()
    else:
        # 리포트 메뉴 외
        st.markdown("### 해당 기능은 개발 중입니다 ")
        # st.image("https://cataas.com/cat?width=500&height=400")
        
    # else:
    #     st.info("zip파일과 환자 번호를 모두 선택해 주세요")
        


# 리포트 메인
def show_report_page(patient_id):
    
    # 탭 버튼들
    col1, col2, col3 = st.columns([2, 2, 6])
    
    # CLAP-A 버튼
    with col1:
        if st.button("CLAP-A", key="clap_a_btn", type="primary" if st.session_state.selected_filter == "CLAP_A" else "secondary", disabled=False):
            st.session_state.selected_filter = "CLAP_A"
            st.rerun()
    # CLAP-D 버튼
    with col2:
        if st.button("CLAP-D", key="clap_d_btn", type="primary" if st.session_state.selected_filter == "CLAP_D" else "secondary", disabled=False):
            st.session_state.selected_filter = "CLAP_D"
            st.rerun()
    
    _, report_main = get_db_modules()
    _, reports_df = report_main.get_assess_lst(patient_id, st.session_state.selected_filter)

    if not reports_df.empty:
        # order_num 내림차순 정렬(최신 데이터가 가장 위로 오도록)
        for idx, row in reports_df[::-1].iterrows():
            with st.container():
                # 체크박스, 검사유형, 검사일자, 의뢰인, 검사자, 확인버튼
                col1, col2, col3, col4, col5,col6,col7 = st.columns([0.5, 2, 3,2,2, 0.5, 2])
                
                with col1:
                    st.checkbox("", key=f"checkbox_{idx}")
                
                with col2:
                    st.markdown(
                        f"<div style='line-height: 1.8; font-size: 25px;'><b>{row['ASSESS_TYPE'].replace('_','-')}</b></div>",
                        unsafe_allow_html=True
                    )
                with col3:
                    st.markdown(
                        f"<div style='line-height: 1.8; font-size: 20px;'>검사일자 <b>{row['ASSESS_DATE']}</b></div>",
                        unsafe_allow_html=True
                    )
                with col4:
                    st.markdown(
                        f"<div style='line-height: 1.8; font-size: 20px;'>의뢰인 <b>{row['REQUEST_ORG']}</b></div>",
                        unsafe_allow_html=True
                    )                    
                with col5:
                    st.markdown(
                        f"<div style='line-height: 1.8; font-size: 20px;'>검사자 <b>{row['ASSESS_PERSON']}</b></div>",
                        unsafe_allow_html=True
                    )                    
                with col7:
                    if st.button("확인하기 〉", key=f"confirm_{idx}"):
                        st.session_state.order_num = int(row['ORDER_NUM'])
                        # 상세보기 검사유형 구별
                        if row['ASSESS_TYPE'] == "CLAP_A":
                            st.session_state.view_mode = "clap_a_detail"
                        elif row['ASSESS_TYPE'] == "CLAP_D":
                            st.session_state.view_mode = "clap_d_detail"

                        st.rerun()
                
                st.divider()
    else:
        # 검사결과가 없는 경우
        st.info(f"{st.session_state.selected_filter.replace('_','-')} 검사 결과가 없습니다.")

# 리포트 상세보기 1: 환자 기본정보
def show_detail_common(patient_id):
    # 뒤로가기 버튼
    col1, col2 = st.columns([3, 9])
    with col1:
        if st.button("< 뒤로가기"):
            st.session_state.view_mode = "list"
            st.rerun()
    # 개발과정에서 Order num 정렬 확인 위해 추가
    with col2:
        st.markdown(f"<div style='margin-top: 5px; font-weight: bold; text-align: left; margin-left: 0px; color: white;'>Order: {st.session_state.order_num}</div>", unsafe_allow_html=True)
    
    # CLAP 타입 확인
    clap_type = st.session_state.selected_filter.replace('_','-')
    subtitle = '실어증' if st.session_state.selected_filter=='CLAP_A' else '마비말장애' if st.session_state.selected_filter=='CLAP_D' else '-'

    # 리포트 상세 가져오기
    _, report_main = get_db_modules()
    # --------------------------------------------------------------------------------
    # 상단 고객정보는 order_num별로 따로따로 저장인지, 처음 저장된 값 쭉 쓰는지 모르겠어서 일단 둘다 해둠
    # --------------------------------------------------------------------------------

    _, patient_detail_specific = report_main.get_patient_info(patient_id,st.session_state.order_num) # 따로따로 저장하는 경우
    _, patient_detail = report_main.get_patient_info(patient_id, 1) # 첫 값 쭉 쓰는 경우

    request_org = patient_detail_specific['REQUEST_ORG'][0]
    assess_person = patient_detail_specific['ASSESS_PERSON'][0]
    assess_date = patient_detail_specific['ASSESS_DATE'][0]
    patient_name = patient_detail['PATIENT_NAME'][0]
    sex = '남' if str(patient_detail['SEX'][0])=='0' else '여' 
    age = patient_detail['AGE'][0]
    edu = patient_detail['EDU'][0]
    diagnosis=str(patient_detail['DIAGNOSIS'][0])
    post_stroke_date = patient_detail['POST_STROKE_DATE'][0]
    stroke_type = str(patient_detail['STROKE_TYPE'][0])
    lesion_location=str(patient_detail['LESION_LOCATION'][0])
    hemiplegia = str(patient_detail['HEMIPLEGIA'][0] if patient_detail['HEMIPLEGIA'][0]!=None else '없음')
    hemineglect = str(patient_detail['HEMINEGLECT'][0] if patient_detail['HEMINEGLECT'][0]!=None else '없음')
    visual_field_defect = str(patient_detail['VISUAL_FIELD_DEFECT'][0] if patient_detail['VISUAL_FIELD_DEFECT'][0]!=None else '없음')
    
    # 화면 디자인
    complete_html = f"""
    <div style="background: white; margin: 0; border-radius: 10px; box-shadow: 0 4px 20px rgba(0,0,0,0.15); font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; overflow: hidden;">
        
        <!-- 헤더 섹션 -->
        <div style="
            background: rgba(35,86,137,1);
            color: white;
            padding: 30px 40px;
            margin: 20px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        ">

            <div style="text-align: right; font-size: 12px; line-height: 1.4;">
                Computerized Language Assessment Program for Aphasia
            </div>            
            <div style="text-align: left; font-size: 36px; font-weight: bold; letter-spacing: 3px; margin: 10px 0;">
                {clap_type}
            </div>
            <div style="text-align: left; font-size: 16px; margin: 10px 0; font-weight: 500;">
                전산화 언어 기능 선별 검사 ({subtitle}) 결과지
            </div>
            <div style="text-align: right; font-size: 12px; line-height: 1.4;">
                연구개발<br>충북대학교병원 재활의학과
            </div>            
        </div>
        
        <!-- 환자 정보 섹션 -->
        <div style="padding: 20px;">
        
        <table style="width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 14px;">
            <tr>
                <td style="border: 1px solid #ddd; padding: 10px; background-color: #f8f9fa; font-weight: bold; width: 15%;">의뢰 기관(과) / 의뢰인</td>
                <td style="border: 1px solid #ddd; padding: 10px; width: 20%;">{request_org}</td>
                <td style="border: 1px solid #ddd; padding: 10px; background-color: #f8f9fa; font-weight: bold; width: 15%;">검사자명</td>
                <td style="border: 1px solid #ddd; padding: 10px; width: 20%;">{assess_person}</td>
                <td style="border: 1px solid #ddd; padding: 10px; background-color: #f8f9fa; font-weight: bold; width: 15%;">검사일자</td>
                <td style="border: 1px solid #ddd; padding: 10px; width: 15%;">{assess_date}</td>
            </tr>
            <tr>
                <td style="border: 1px solid #ddd; padding: 10px; background-color: #f8f9fa; font-weight: bold;">이름</td>
                <td style="border: 1px solid #ddd; padding: 10px;">{patient_name}</td>
                <td style="border: 1px solid #ddd; padding: 10px; background-color: #f8f9fa; font-weight: bold;">성별</td>
                <td style="border: 1px solid #ddd; padding: 10px;">{sex}</td>
                <td style="border: 1px solid #ddd; padding: 10px; background-color: #f8f9fa; font-weight: bold;">개인번호</td>
                <td style="border: 1px solid #ddd; padding: 10px;">{patient_id}</td>
            </tr>
            <tr>
                <td style="border: 1px solid #ddd; padding: 10px; background-color: #f8f9fa; font-weight: bold;">교육연수</td>
                <td style="border: 1px solid #ddd; padding: 10px;">{edu}년</td>
                <td style="border: 1px solid #ddd; padding: 10px; background-color: #f8f9fa; font-weight: bold;">문해여부</td>
                <td style="border: 1px solid #ddd; padding: 10px;">가능</td>
                <td style="border: 1px solid #ddd; padding: 10px; background-color: #f8f9fa; font-weight: bold;">연령</td>
                <td style="border: 1px solid #ddd; padding: 10px;">{age}</td>
            </tr>
            <tr>
                <td style="border: 1px solid #ddd; padding: 10px; background-color: #f8f9fa; font-weight: bold;">방언</td>
                <td style="border: 1px solid #ddd; padding: 10px;">표준어</td>
                <td style="border: 1px solid #ddd; padding: 10px; background-color: #f8f9fa; font-weight: bold;">발병일</td>
                <td style="border: 1px solid #ddd; padding: 10px;">{post_stroke_date}</td>
                <td style="border: 1px solid #ddd; padding: 10px; background-color: #f8f9fa; font-weight: bold;">실시 횟수</td>
                <td style="border: 1px solid #ddd; padding: 10px;">N회</td>
            </tr>
        </table>

        <table style="width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 14px;">
            <tr>
                <td style="border: 1px solid #ddd; padding: 10px; background-color: #f8f9fa; font-weight: bold; width: 15%;">진단명</td>
                <td style="border: 1px solid #ddd; padding: 10px;" colspan="5">{'뇌경색' if diagnosis=='0' else '뇌출혈' if diagnosis=='1' else '뇌종양' if diagnosis=='2' else '파킨슨병' if diagnosis=='3' else '기타' if diagnosis=='4' else diagnosis}</td>
            </tr>
            <tr>
                <td style="border: 1px solid #ddd; padding: 10px; background-color: #f8f9fa; font-weight: bold;">주요 뇌병변 I</td>
                <td style="border: 1px solid #ddd; padding: 10px;" colspan="5">{'오른쪽' if stroke_type=='0' else '왼쪽' if stroke_type=='1' else '양쪽' if stroke_type=='2' else stroke_type}</td>
            </tr>
            <tr>
                <td style="border: 1px solid #ddd; padding: 10px; background-color: #f8f9fa; font-weight: bold;">주요 뇌병변 II</td>
                <td style="border: 1px solid #ddd; padding: 10px;" colspan="5">{'전두엽' if lesion_location=='0' else '두정엽' if lesion_location=='1' else '측두엽' if lesion_location=='2' else '후두엽' if lesion_location=='3' else '소뇌' if lesion_location=='4' else '뇌간' if lesion_location=='5' else '기저핵' if lesion_location=='6' else '시상' if lesion_location=='7' else '해당 없음' }</td>
            </tr>
        </table>

        <table style="width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 14px;">
            <tr>
                <td style="border: 1px solid #ddd; padding: 10px; background-color: #f8f9fa; font-weight: bold; width: 15%;">편마비</td>
                <td style="border: 1px solid #ddd; padding: 10px; width: 20%;">{'오른쪽' if hemiplegia=='0' else '왼쪽' if hemiplegia=='1' else '없음' if hemiplegia=='2'  else '양쪽' if (('0' in hemiplegia) * ('1' in hemiplegia)) else hemiplegia }</td>
                <td style="border: 1px solid #ddd; padding: 10px; background-color: #f8f9fa; font-weight: bold; width: 15%;">무시증</td>
                <td style="border: 1px solid #ddd; padding: 10px; width: 20%;">{'오른쪽' if hemineglect=='0' else '왼쪽' if hemineglect=='1' else '없음' if hemineglect=='2' else '양쪽' if (('0' in hemineglect) * ('1' in hemineglect)) else hemineglect }</td>
                <td style="border: 1px solid #ddd; padding: 10px; background-color: #f8f9fa; font-weight: bold; width: 15%;">시야결손</td>
                <td style="border: 1px solid #ddd; padding: 10px; width: 15%;">{'오른쪽' if visual_field_defect=='0' else '왼쪽' if visual_field_defect=='1' else '없음' if visual_field_defect=='2' else '양쪽' if (('0' in visual_field_defect) * ('1' in visual_field_defect)) else visual_field_defect }</td>
            </tr>
            <tr>
                <td style="border: 1px solid #ddd; padding: 10px; background-color: #f8f9fa; font-weight: bold;">기타 특이사항</td>
                <td style="border: 1px solid #ddd; padding: 10px;" colspan="5"></td>
            </tr>
        </table>

        <h3 style="color: #4a90e2; font-weight: bold; margin: 30px 0 20px 0; padding-bottom: 10px; border-bottom: 2px solid #4a90e2;">
            결과 요약
        </h3>
        </div>
    """
    
    return complete_html


# 리포트 상세보기 2: 검사정보
def show_detail_assess(fin_scores):
    import matplotlib
    import platform
    if platform.system() == 'Darwin':  # macOS
        matplotlib.rcParams['font.family'] = 'AppleGothic'
    elif platform.system() == 'Windows':  # Windows
        matplotlib.rcParams['font.family'] = 'Malgun Gothic'
    else:  # Linux
        matplotlib.rcParams['font.family'] = 'DejaVu Sans'
    
    matplotlib.rcParams['axes.unicode_minus'] = False

    ltn_rpt = fin_scores.get('LTN_RPT', '-')
    guess_end = fin_scores.get('GUESS_END', '-')
    name_and_words = fin_scores.get('GUESS_END', 0) + fin_scores.get('SAY_OBJ', 0) + fin_scores.get('SAY_ANI', 0)
    say_obj=fin_scores.get('SAY_OBJ', '-')
    say_ani=fin_scores.get('SAY_ANI', '-')
    talk_pic=fin_scores.get('TALK_PIC', '-')
    talk_byoneself=fin_scores.get('TALK_PIC', 0)
    all_sum=fin_scores.get('LTN_RPT', 0) + fin_scores.get('GUESS_END', 0) + fin_scores.get('SAY_OBJ', 0) + fin_scores.get('SAY_ANI', 0) + fin_scores.get('TALK_PIC', 0)
    Aphasia_sum=fin_scores.get('LTN_RPT', 0) + fin_scores.get('GUESS_END', 0) + fin_scores.get('SAY_OBJ', 0) + fin_scores.get('SAY_ANI', 0) + fin_scores.get('TALK_PIC', 0)
    talk_clean=fin_scores.get('TALK_CLEAN', '-')

    # show_detail_common에서 기본 HTML을 가져옴
    base_html = show_detail_common(st.session_state.patient_id)
    # 검사 결과 테이블 HTML 생성
    results_table = ""
    if st.session_state.selected_filter == "CLAP_A":
        results_table = f"""
        <table style="border-collapse: collapse; width: 80%; margin: auto; margin-bottom: 40px; font-size: 14px; table-layout: fixed;">
            <thead>
                <tr>
                    <th style="border: 1px solid #ddd; padding: 8px; text-align: center; vertical-align: middle; background-color: #e3f2fd; color: #333; font-weight: bold; width: 30%;">문항 (개수)</th>
                    <th style="border: 1px solid #ddd; padding: 8px; text-align: center; vertical-align: middle; background-color: #e3f2fd; color: #333; font-weight: bold; width: 20%;">결과</th>
                    <th style="border: 1px solid #ddd; padding: 8px; text-align: center; vertical-align: middle; background-color: #e3f2fd; color: #333; font-weight: bold; width: 25%;">실어증 점수</th>
                    <th style="border: 1px solid #ddd; padding: 8px; text-align: center; vertical-align: middle; background-color: #e3f2fd; color: #333; font-weight: bold; width: 25%;">점수</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center; vertical-align: middle; color: #333; font-size: 12px;">듣고 따라 말하기 (10)</td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center; vertical-align: middle; color: #333; font-size: 12px;">{ltn_rpt if ltn_rpt=='-' else int(ltn_rpt)}점</td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center; vertical-align: middle; color: #333; font-size: 12px;">따라 말하기</td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center; vertical-align: middle; color: #333; font-size: 12px;">{0 if ltn_rpt=='-' else int(ltn_rpt)}점</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center; vertical-align: middle; color: #333; font-size: 12px;">끝말 맞추기 (5)</td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center; vertical-align: middle; color: #333; font-size: 12px;">{guess_end if guess_end=='-' else int(guess_end)}점</td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center; vertical-align: middle; color: #333; font-size: 12px;" rowspan="3">이름대기 및<br>날말찾기</td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center; vertical-align: middle; color: #333; font-size: 12px;" rowspan="3">{int(name_and_words)}점</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center; vertical-align: middle; color: #333; font-size: 12px;">물건 이름 말하기 (10)</td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center; vertical-align: middle; color: #333; font-size: 12px;">{say_obj if say_obj=='-' else int(say_obj)}점</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center; vertical-align: middle; color: #333; font-size: 12px;">동물 이름 말하기 (1)</td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center; vertical-align: middle; color: #333; font-size: 12px;">{say_ani if say_ani=='-' else int(say_ani)}점</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center; vertical-align: middle; color: #333; font-size: 12px;">그림보고 이야기하기</td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center; vertical-align: middle; color: #333; font-size: 12px;">{talk_pic if talk_pic=='-' else int(talk_pic)}점</td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center; vertical-align: middle; color: #333; font-size: 12px;">스스로 말하기</td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center; vertical-align: middle; color: #333; font-size: 12px;">{int(talk_byoneself)}점</td>
                </tr>
                <tr style="background-color: #e3f2fd; font-weight: bold;">
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center; vertical-align: middle; color: #1976d2; font-weight: bold; font-size: 12px;">합계</td>

                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center; vertical-align: middle; color: #1976d2;" colspan="4">{int(Aphasia_sum)}점</td>
                </tr>
            </tbody>
        </table>
        
        """

        
    elif st.session_state.selected_filter == "CLAP_D":
        results_table = f"""
        <table style="border-collapse: collapse; width: 80%; margin: auto; margin-bottom: 40px; font-size: 20px; table-layout: fixed;">
            <thead>
                <tr>
                    <th style="border: 1px solid #ddd; padding: 8px; text-align: center; vertical-align: middle; background-color: #e3f2fd; color: #333; font-weight: bold; width: 35%;">문항</th>
                    <th style="border: 1px solid #ddd; padding: 8px; text-align: center; vertical-align: middle; background-color: #e3f2fd; color: #333; font-weight: bold; width: 45%;">수행 결과</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center; vertical-align: middle; color: #333; font-size: 12px;">'아' 소리내기</td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center; vertical-align: middle; color: #333; font-size: 12px;">최대 발성시간 {fin_scores.get('AH_SOUND', '-')}초</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center; vertical-align: middle; color: #333; font-size: 12px;">'퍼' 반복하기</td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center; vertical-align: middle; color: #333; font-size: 12px;">평균 횟수 {fin_scores.get('P_SOUND', '-')}회</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center; vertical-align: middle; color: #333; font-size: 12px;">'터' 반복하기</td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center; vertical-align: middle; color: #333; font-size: 12px;">평균 횟수 {fin_scores.get('T_SOUND', '-')}회</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center; vertical-align: middle; color: #333; font-size: 12px;">'커' 반복하기</td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center; vertical-align: middle; color: #333; font-size: 12px;">평균 횟수 {fin_scores.get('K_SOUND', '-')}회</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center; vertical-align: middle; color: #333; font-size: 12px;">'퍼터커' 반복하기</td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center; vertical-align: middle; color: #333; font-size: 12px;">평균 횟수 {fin_scores.get('PTK_SOUND', '-')}회</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center; vertical-align: middle; color: #333; font-size: 12px;">또박또박 말하기<br></td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center; vertical-align: middle; color: #333; font-size: 12px;">{talk_clean if talk_clean=='-' else int(talk_clean)}점</td>
                </tr>
            </tbody>
        </table>
        """
        st.session_state['model_completed']=True
        # fig=show_graph({'AH_SOUND':fin_scores.get('AH_SOUND', 0),
        #                 'P_SOUND': fin_scores.get('P_SOUND', 0),
        #                 'T_SOUND':fin_scores.get('T_SOUND', 0),
        #                 'K_SOUND':fin_scores.get('K_SOUND', 0),
        #                 'PTK_SOUND':fin_scores.get('PTK_SOUND', 0),
        #                 'TALK_CLEAN':fin_scores.get('TALK_CLEAN', 0)
        #                 })
        # st.pyplot(fig)
    # 전체 HTML을 결합하고 컨테이너를 닫음
    complete_html = base_html + results_table + """
    </div>
    """
    
    
    # streamlit components를 사용하여 HTML 렌더링
    import streamlit.components.v1 as components
    components.html(complete_html, height=1200)
    
    # 그래프(CLAP-A 한정)
    if st.session_state.selected_filter == "CLAP_A":        
        col1, col2 = st.columns([1, 1])

        # 만점(없으면 최대값) 계산해서 그래프 통일(백분율)
        max_scores={
            'LTN_RPT':68,
            'GUESS_END':10,
            'SAY_OBJ':20,
            'SAY_ANI':40,
            'TALK_PIC':30,
        }
        graph1_data = {'듣고 따라 말하기':fin_scores.get('LTN_RPT', 0)/max_scores.get('LTN_RPT', 1)*100,
                        '끝말 맞추기':fin_scores.get('GUESS_END', 0)/max_scores.get('GUESS_END', 1)*100,
                        '물건 이름 말하기':fin_scores.get('SAY_OBJ', 0)/max_scores.get('SAY_OBJ', 1)*100,
                        '동물 이름 말하기':fin_scores.get('SAY_ANI', 0)/max_scores.get('SAY_ANI', 1)*100,
                        '그림 보고\n이야기하기':fin_scores.get('TALK_PIC', 0)/max_scores.get('TALK_PIC', 1)*100}
        graph2_data = {'따라 말하기':sum([graph1_data.get('듣고 따라 말하기',0)]),
                        '이름 대기 및\n낱말 찾기': name_and_words/sum([max_scores.get('GUESS_END'),max_scores.get('SAY_ANI'),max_scores.get('TALK_PIC')])*100,
                        '스스로 말하기':sum([graph1_data.get('그림 보고\n이야기하기')])}
        # 최댓값으로 그래프 max 설정
        # max1 = max(graph1_data.values()) if graph1_data.values() else 1
        # max2 = max(graph2_data.values()) if graph2_data.values() else 1
        # common_max = max(max1, max2)

        
        with col1:
            st.header('문항별 점수')
            with st.container():
                fig = show_graph(graph1_data, rmax=100)
                st.pyplot(fig, use_container_width=False)
        with col2:
            st.header('실어증 점수')
            with st.container():
                a_graph=show_graph(graph2_data, rmax=100)
                st.pyplot(a_graph, use_container_width=False)
    

def show_graph(fin_scores: dict,
                          label_map: dict | None = None,
                          rmax: float | None = None):
    """
    fin_scores: {'LTN_RPT':6, 'GUESS_END':5, ...} 형태의 단일 검사 점수 dict
    title: 그래프 제목
    label_map: {'LTN_RPT':'끝말 맞추기', ...} 처럼 축 라벨을 바꾸고 싶을 때 전달
    rmax: 반지름(최대값) 고정하고 싶을 때 숫자로 지정 (None이면 자동)
    return: matplotlib.figure.Figure
    """

    # 한글 폰트 설정
    import matplotlib
    import platform
    
    if platform.system() == 'Darwin':  # macOS
        matplotlib.rcParams['font.family'] = 'AppleGothic'
    elif platform.system() == 'Windows':  # Windows
        matplotlib.rcParams['font.family'] = 'Malgun Gothic'
    else:  # Linux
        matplotlib.rcParams['font.family'] = 'DejaVu Sans'
    
    matplotlib.rcParams['axes.unicode_minus'] = False

    # 라벨과 값 뽑기 (원래 입력 순서 유지)
    keys = list(fin_scores.keys())
    vals = [float(fin_scores[k]) for k in keys]

    # 축 라벨 매핑
    if label_map:
        labels = [label_map.get(k, k) for k in keys]
    else:
        labels = keys

    # 도형을 닫기 위해 첫 값 재추가
    N = len(labels)
    angles = np.linspace(0, 2*np.pi, N, endpoint=False).tolist()
    angles += angles[:1]
    vals_closed = vals + vals[:1]

    # Figure 생성 (상대적 크기)
    import matplotlib.pyplot as plt
    fig_width = plt.rcParams['figure.figsize'][0] * 0.4
    fig_height = plt.rcParams['figure.figsize'][1] * 0.4
    fig, ax = plt.subplots(figsize=(fig_width, fig_height), subplot_kw=dict(polar=True))

    # 위쪽(북쪽)에서 시작, 시계방향
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)

    # 축/눈금
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=8)
    # vmax = max(vals) if vals and rmax is None else (rmax if rmax is not None else 1.0)
    # if vmax <= 0:
    #     vmax = 1.0
    ax.set_ylim(0, rmax)
    # ax.tick_params(axis='y', labelsize=-1)
    ax.set_yticklabels([])


    # 레이더 폴리곤
    ax.plot(angles, vals_closed, linewidth=2)
    ax.fill(angles, vals_closed, alpha=0.25)

    # 그래프 크기 강제 통일
    # plt.subplots_adjust(left=0.05, right=1.95, top=0.95, bottom=0.05)
    plt.tight_layout()

    return fig


@st.dialog("Developers!")
def show_popup():
    st.image(os.path.join(base_path,"ui","utils","private","easteregg.jpeg"), width=450)
    st.write("팀장 : 이랑(끝말맞추기, 물건이름말하기 모델 개발)")
    st.write("팀원1 : 김재헌(UI, 아소리내기 모델 개발)")
    st.write("팀원2 : 김준영(DB, 듣고따라말하기 모델 개발)")
    st.write("팀원3 : 이재현(동물이름말하기, 그림보고이야기하기 모델 개발)")
    st.write("팀원4 : 이효재(또박또박말하기, 퍼터커반복하기 모델 개발)")
    st.write("Special Thanks to **Mr.HAN**:sunglasses:")

    if st.button("닫기"):
        st.rerun()

def add_easter_egg(image_path):
    """ w 클릭하면 이미지 로드하는 이스터에그 """
    import streamlit as st
    from streamlit_image_coordinates import streamlit_image_coordinates
    from PIL import Image
    import numpy as np

    # PIL로 투명 PNG 읽기 (알파 채널 보존)
    image = Image.open(image_path)
    image = np.array(image)

    # 이미지 표시 + 좌표 받기
    coords = streamlit_image_coordinates(image, width=100)

    if coords is not None:
        # 클릭 이벤트 발생 시 처리
        x,y=coords['x'],coords['y']
        if (50<=x<=60) & (50<=y<=60):
            st.success(f"x:{x},y:{y}")
            show_popup()
            # st.write(streamlit_image_coordinates(os.path.join(base_path,"ui","utils","private","easteregg.jpeg"),width=200))
            
            # st.write(streamlit_image_coordinates(os.path.join(base_path,"ui","utils","private"),width=100))
            # 구글드라이브 공유 링크를 직접 다운로드 링크로 변환
            # drive_url = "https://drive.google.com/file/d/1VH1vAmk1Vk13iupKVJesfToj9mvGhpX2/view?usp=drive_link"
            # file_id = drive_url.split('/d/')[1].split('/')[0]
            # direct_url = f"https://drive.google.com/uc?export=download&id={file_id}"
            # st.write(streamlit_image_coordinates(drive_url, width=100))

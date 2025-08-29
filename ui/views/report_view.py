import streamlit as st
from views.login_view import show_login_page
from services.db_service import get_db_modules,get_reports
from services.model_service import (
    get_talk_pic, get_ah_sound, get_ptk_sound, get_talk_clean, 
    get_say_ani, get_ltn_rpt, get_say_obj, get_guess_end
)
from models.guess_end import GuessEndInferencer
from utils.style_utils import apply_custom_css
from utils.footer_utils import add_footer
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import streamlit.components.v1 as components
import tempfile
import os
from pathlib import Path
import pandas as pd
import time
import base64
import matplotlib.pyplot as plt
import numpy as np

apply_custom_css()



def show_main_interface(patient_id,path_info):
    # 초기화
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "리포트"
    if 'view_mode' not in st.session_state:
        st.session_state.view_mode = "list"

    # 사이드바
    with st.sidebar:
        st.markdown("""
        <div style="display: flex; align-items: center; gap: 10px;">
            <img src="data:image/png;base64,{}" width="40" />
            <h1 style="margin: 0; font-size: 2.5rem;">CLAP</h1>
        </div>
        """.format(
            __import__('base64').b64encode(open("ui/views/clap.png", "rb").read()).decode()
        ), unsafe_allow_html=True)
        # 메뉴: 있어야 할까?
        st.divider()
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
        # if not patient_info.empty:
            # 초기값 설정
        if 'selected_filter' not in st.session_state:
            st.session_state.selected_filter = "CLAP_A"
        patient_info=get_reports(patient_id)
        if patient_info is not None and len(patient_info) > 0:
            try:
                st.write(f"**{patient_info['PATIENT_NAME'].iloc[0]} {int(patient_info['AGE'].iloc[0])}세**")
                st.write(f"환자번호: {patient_info['PATIENT_ID'].iloc[0]}")
                st.write(f"성별: {'여성' if patient_info['SEX'].iloc[0]==1 else '남성'}")
            except:
                st.write(f"**ㅇㅇ ㅇㅇ세**")
                st.write(f"환자번호: {st.session_state.patient_id}")
                st.write(f"성별: ㅇㅇ")                
        else:
            st.write("환자 정보를 등록하면 여기 표시됩니다")

        st.divider()     



        # 로그아웃 버튼
        if st.button("로그아웃", key="logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()

        st.markdown("""
        <div style="display: flex; align-items: center; gap: 10px; margin-top: 20px;">
            <img src="data:image/jpeg;base64,{}" width="140" />
        </div>
        """.format(
            __import__('base64').b64encode(open("ui/utils/logo.jpeg", "rb").read()).decode()
        ), unsafe_allow_html=True)

            
        # 파일 경로
        # save_dir = df['MAIN_PATH']
        # print('\n\n\n',save_dir)
    
    # 리포트 메인
    if st.session_state.current_page == "리포트":
        if st.session_state.view_mode == "list":
            show_report_page(patient_info['PATIENT_ID'].iloc[0] if not patient_info.empty else '')
        elif 'model_completed' not in st.session_state:
        # elif True:
            print('---------------------- model_not_completed -------------------')
            with st.spinner('평가 중...'):
                show_detail(model_process(path_info))
        else:         
            model_comm, report_main = get_db_modules()    
#             print('====>', st.session_state.patient_id,st.session_state.order_num,st.session_state.selected_filter)        
            msg, ret_df =report_main.get_assess_score(st.session_state.patient_id,st.session_state.order_num,st.session_state.selected_filter)
#             print('---------')
# # 에러 핸들링 문제, 환자id 조회 문제
#             print(msg)
#             print('---------')

            # ret_df = pd.DataFrame(rows, columns=['PATIENT_ID', 'ORDER_NUM', 'ASSESS_TYPE', 'QUESTION_CD', 'QUESTION_NM', 'SUBSET', 'SCORE', 'SCORE_REF'])
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
            fin_scores={}
            for i in range(len(ret_df)):
                fin_scores[ret_df['QUESTION_CD'][i]]=ret_df['SCORE'][i]
            show_detail(fin_scores)
            # 환자 정보 표시
            st.divider()
    else:
        st.markdown("### 해당 기능은 개발 중입니다 ")
        st.image("https://cataas.com/cat?width=500&height=400")
        
    # else:
    #     st.info("zip파일과 환자 번호를 모두 선택해 주세요")
    

def model_process(path_info):            
        # model_comm, report_main = get_db_modules()
        # 파일 경로와 목록 정보를 조회
        # print('\n\n\ndf',df)
        ret = path_info[['MAIN_PATH','SUB_PATH','FILE_NAME']]
        # print('------------------------------------')
        # print('ret:',ret)
        # print('------------------------------------')

        ah_sound_path=[]
        ptk_sound_path=[]
        ltn_rpt_path=[]
        guess_end_path=[]
        say_ani_path=[]
        say_obj_path=[]
        talk_clean_path=[]
        talk_pic_path=[]

        ah_sound_result=None
        p_sound_result=None
        t_sound_result=None
        k_sound_result=None
        ptk_sound_result=None
        ltn_rpt_result=None
        guess_end_result=None
        say_ani_result=None
        say_obj_result=None
        talk_clean_result=None
        talk_pic_result=None

        a_path_list=[ltn_rpt_path,guess_end_path,say_obj_path,say_ani_path,talk_pic_path]
        d_path_list=[ah_sound_path,ptk_sound_path,talk_clean_path]

        for i in range(len(ret)):
            main_path = str(ret.loc[i, 'MAIN_PATH'])
            sub_path = str(ret.loc[i, 'SUB_PATH'])
            filename = str(ret.loc[i, 'FILE_NAME'])
            if sys.platform.startswith('win'):
                sub_path.replace('/','\\')
            
            # base_path 기준으로 경로 구성: base_path / upload / files / main_path / sub_path / filename
            from dotenv import load_dotenv
            from pathlib import Path as EnvPath
            import os
            env_path = EnvPath(__file__).parent.parent.parent / ".env"
            load_dotenv(dotenv_path=env_path)
            base_path = os.getenv("base_path")
            
            file_path = os.path.join(base_path, 'files','upload',main_path, sub_path.upper(), filename)


            # 필요하다면 문자열로 변환
            file_path = str(file_path)
                # 파일 존재 여부 확인
            # if not os.path.exists(file_path):
            #     # st.warning(f"❌ 파일 없음: {file_path}")
            #     continue
                
            sub_path_parts = Path(sub_path).parts
            # d일 때
            if sub_path_parts[0].lower() == 'clap_d':
                for i in range(3):
                    if sub_path_parts[1] == str(i):
                        d_path_list[i].append(file_path)
                        
            # a일 때
            elif sub_path_parts[0].lower() == 'clap_a':
                for i in range(5):
                    if sub_path_parts[1] == str(i+3):
                        a_path_list[i].append(file_path)

        # ============================================================================
        # 결과 딕셔너리로 저장 - 2025.08.22 수정
        # ============================================================================  
        fin_scores={}

        # ============================================================================
        # 필요할 때만 모듈 import - 2025.08.22 수정
        # ============================================================================                    
        if len(ltn_rpt_path)>0:
            start_time = time.time()
            try:
                ltn_rpt = get_ltn_rpt()
                ltn_rpt_result=ltn_rpt.predict_score(ltn_rpt_path)
                fin_scores['LTN_RPT']=ltn_rpt_result
                print(f"LTN_RPT 모델 실행 시간: {time.time() - start_time:.2f}초")
            except Exception as e:
                print(f"LTN_RPT 모델 실행 중 오류 발생: {e}")
                fin_scores['LTN_RPT'] = 0

        if len(guess_end_path)>0:
            start_time = time.time()
            try:
                guess_end = get_guess_end()
                temp=[]
                infer = guess_end.GuessEndInferencer(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "models", "guess_end_model.keras"))
                for idx,p in enumerate(guess_end_path):
                    temp.append(infer.predict_guess_end(p,idx))
                guess_end_result=sum(temp)
                fin_scores['GUESS_END']=guess_end_result
                print(f"GUESS_END 모델 실행 시간: {time.time() - start_time:.2f}초")
            except Exception as e:
                print(f"GUESS_END 모델 실행 중 오류 발생: {e}")
                fin_scores['GUESS_END'] = 0

        if len(say_obj_path)>0:
            start_time = time.time()
            try:
                say_obj = get_say_obj()
                say_obj_result=say_obj.predict_total_say_obj(say_obj_path[5],say_obj_path[8])  
                fin_scores['SAY_OBJ']=say_obj_result
                print(f"SAY_OBJ 모델 실행 시간: {time.time() - start_time:.2f}초")
            except Exception as e:
                print(f"SAY_OBJ 모델 실행 중 오류 발생: {e}")
                fin_scores['SAY_OBJ'] = 0
            
        if len(say_ani_path)>0:
            start_time = time.time()
            try:
                say_ani = get_say_ani()
                say_ani_result=say_ani.score_audio(say_ani_path[0])
                fin_scores['SAY_ANI']=say_ani_result
                print(f"SAY_ANI 모델 실행 시간: {time.time() - start_time:.2f}초")
            except Exception as e:
                print(f"SAY_ANI 모델 실행 중 오류 발생: {e}")
                fin_scores['SAY_ANI'] = 0
            
        if len(talk_pic_path)>0:
            start_time = time.time()
            try:
                talk_pic = get_talk_pic()
                talk_pic_result=talk_pic.score_audio(talk_pic_path[0])
                fin_scores['TALK_PIC']=talk_pic_result
                print(f"TALK_PIC 모델 실행 시간: {time.time() - start_time:.2f}초")
            except Exception as e:
                print(f"TALK_PIC 모델 실행 중 오류 발생: {e}")
                fin_scores['TALK_PIC'] = 0
            
        if len(ah_sound_path)>0:
            start_time = time.time()
            try:
                ah_sound = get_ah_sound()
                ah_sound_result=round(ah_sound.analyze_pitch_stability(ah_sound_path[0]),2)
                fin_scores['AH_SOUND']=ah_sound_result
                print(f"AH_SOUND 모델 실행 시간: {time.time() - start_time:.2f}초")
            except Exception as e:
                print(f"AH_SOUND 모델 실행 중 오류 발생: {e}")
                fin_scores['AH_SOUND'] = 0

        if len(ptk_sound_path)>0:
            start_time = time.time()
            try:
                ptk_sound = get_ptk_sound()
                temp_p,temp_t,temp_k,temp_ptk=[],[],[],[]
                for i in range(len(ptk_sound_path)):
                    if i in [0,1,2]:
                        temp_p.append(ptk_sound.ptk_each(ptk_sound_path[i]))
                    elif i in [3,4,5]:
                        temp_t.append(ptk_sound.ptk_each(ptk_sound_path[i]))
                    elif i in [6,7,8]:
                        temp_k.append(ptk_sound.ptk_each(ptk_sound_path[i]))
                    elif i in [9,10,11]:
                        temp_ptk.append(ptk_sound.ptk_whole(ptk_sound_path[i]))
                # if 'p' not in st.session_state:
                #     st.session_state.p=max(temp_p)
                # if 't' not in st.session_state:
                #     st.session_state.p=max(temp_t)                
                # if 'k' not in st.session_state:
                #     st.session_state.p=max(temp_k)
                # if 'ptk' not in st.session_state:
                #     st.session_state.p=max(temp_ptk)


                fin_scores['P_SOUND']=round(max(temp_p),2)
                fin_scores['T_SOUND']=round(max(temp_t),2)
                fin_scores['K_SOUND']=round(max(temp_k),2)
                fin_scores['PTK_SOUND']=round(max(temp_ptk),2)
                print(f"PTK_SOUND 모델 실행 시간: {time.time() - start_time:.2f}초")
            except Exception as e:
                print(f"PTK_SOUND 모델 실행 중 오류 발생: {e}")
                fin_scores['P_SOUND'] = 0
                fin_scores['T_SOUND'] = 0
                fin_scores['K_SOUND'] = 0
                fin_scores['PTK_SOUND'] = 0

        if len(talk_clean_path)>0:
            start_time = time.time()
            try:
                talk_clean = get_talk_clean()
                talk_clean_result=talk_clean.main(talk_clean_path)
                fin_scores['TALK_CLEAN']=talk_clean_result
                print(f"TALK_CLEAN 모델 실행 시간: {time.time() - start_time:.2f}초")
            except Exception as e:
                print(f"TALK_CLEAN 모델 실행 중 오류 발생: {e}")
                fin_scores['TALK_CLEAN'] = 0

        # ['PATIENT_ID', 'ORDER_NUM', 'ASSESS_TYPE', 'QUESTION_CD', 'QUESTION_NO', 'QUESTION_MINOR_NO', 'SCORE']
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
        
        # DB에 점수 저장
        try:
            from services.db_service import save_scores_to_db
            save_scores_to_db(fin_scores)
            print("점수가 성공적으로 DB에 저장되었습니다.")
            st.session_state.model_completed=True
        except Exception as e:
            print(f"DB 저장 중 오류 발생: {e}")
        
        return fin_scores

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
    model_comm, report_main = get_db_modules()
    msg, reports_df = report_main.get_assess_lst(patient_id, st.session_state.selected_filter)

    if not reports_df.empty:
        for idx, row in reports_df[::-1].iterrows():
            with st.container():
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
                        st.session_state.selected_report = {
                            'type': row['ASSESS_TYPE'],
                            'date': row['ASSESS_DATE'],
                            'patient_id': row['PATIENT_ID'],
                            'order_num': row['ORDER_NUM']
                        }
                        st.session_state.selected_filter = row['ASSESS_TYPE']  # selected_filter 설정 추가
                        if row['ASSESS_TYPE'] == "CLAP_A":
                            st.session_state.view_mode = "clap_a_detail"
                        elif row['ASSESS_TYPE'] == "CLAP_D":
                            st.session_state.view_mode = "clap_d_detail"
                        # ??? 또 모델링 함
                        st.rerun()
                
                st.divider()
    else:
        st.info(f"{st.session_state.selected_filter.replace('_','-')} 검사 결과가 없습니다.")


def show_detail_common(patient_id):
    # 뒤로가기 버튼
    col1, col2 = st.columns([3, 9])
    with col1:
        if st.button("< 뒤로가기"):
            st.session_state.view_mode = "list"
            st.rerun()
    with col2:
        st.markdown(f"<div style='margin-top: 5px; font-weight: bold; text-align: left; margin-left: 0px; color: white;'>Order: {st.session_state.selected_report['order_num']}</div>", unsafe_allow_html=True)
    
    # CLAP 타입 확인
    clap_type = st.session_state.selected_filter.replace('_','-')
    subtitle = '실어증' if st.session_state.selected_filter=='CLAP_A' else '마비말장애' if st.session_state.selected_filter=='CLAP_D' else ''

    # 리포트 상세 가져오기
    model_comm, report_main = get_db_modules()
    msg, patient_detail = report_main.get_patient_info(patient_id,st.session_state.selected_report['order_num'])

    # streamlit.components.v1.html() 사용하여 완전한 HTML 렌더링
    # 데이터 먼저 추출
    request_org = patient_detail['REQUEST_ORG'][0]
    assess_person = patient_detail['ASSESS_PERSON'][0] 
    assess_date = patient_detail['ASSESS_DATE'][0]
    patient_name = patient_detail['PATIENT_NAME'][0]
    sex = '남' if patient_detail['SEX'][0]==0 else '여' 
    age = patient_detail['AGE'][0]
    patient_id = patient_detail['PATIENT_ID'][0]
    edu = patient_detail['EDU'][0]
    post_stroke_date = patient_detail['POST_STROKE_DATE'][0]
    stroke_type = patient_detail['STROKE_TYPE'][0]
    hemiplegia = patient_detail['HEMIPLEGIA'][0] if patient_detail['HEMIPLEGIA'][0]!=None else '없음'
    hemineglect = patient_detail['HEMINEGLECT'][0] if patient_detail['HEMINEGLECT'][0]!=None else '없음'
    visual_field_defect = patient_detail['VISUAL_FIELD_DEFECT'][0] if patient_detail['VISUAL_FIELD_DEFECT'][0]!=None else '없음'
    
    # 완전한 HTML 문서로 구성 (헤더 포함)
    complete_html = f"""
    <div style="background: white; margin: 0; border-radius: 10px; box-shadow: 0 4px 20px rgba(0,0,0,0.15); font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; overflow: hidden;">
        
        <!-- 헤더 섹션 -->
        <div style="
            background: linear-gradient(135deg, #4a90e2, #357abd);
            color: white;
            padding: 30px 40px;
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
                <td style="border: 1px solid #ddd; padding: 10px;" colspan="5">{stroke_type}</td>
            </tr>
            <tr>
                <td style="border: 1px solid #ddd; padding: 10px; background-color: #f8f9fa; font-weight: bold;">주요 뇌병변 I</td>
                <td style="border: 1px solid #ddd; padding: 10px;" colspan="5">뇌경색 / 뇌혈관 / 미확인 / 기타</td>
            </tr>
            <tr>
                <td style="border: 1px solid #ddd; padding: 10px; background-color: #f8f9fa; font-weight: bold;">주요 뇌병변 II</td>
                <td style="border: 1px solid #ddd; padding: 10px;" colspan="5">대뇌(전두엽 / 두정엽 / 후두엽) / 소뇌 / 뇌간 / 기저핵 / 시상</td>
            </tr>
        </table>

        <table style="width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 14px;">
            <tr>
                <td style="border: 1px solid #ddd; padding: 10px; background-color: #f8f9fa; font-weight: bold; width: 15%;">편마비</td>
                <td style="border: 1px solid #ddd; padding: 10px; width: 20%;">{hemiplegia}</td>
                <td style="border: 1px solid #ddd; padding: 10px; background-color: #f8f9fa; font-weight: bold; width: 15%;">무시증</td>
                <td style="border: 1px solid #ddd; padding: 10px; width: 20%;">{hemineglect}</td>
                <td style="border: 1px solid #ddd; padding: 10px; background-color: #f8f9fa; font-weight: bold; width: 15%;">시야결손</td>
                <td style="border: 1px solid #ddd; padding: 10px; width: 15%;">{visual_field_defect}</td>
            </tr>
            <tr>
                <td style="border: 1px solid #ddd; padding: 10px; background-color: #f8f9fa; font-weight: bold;">기타 특이사항</td>
                <td style="border: 1px solid #ddd; padding: 10px;" colspan="5">-</td>
            </tr>
        </table>

        <h3 style="color: #4a90e2; font-weight: bold; margin: 30px 0 20px 0; padding-bottom: 10px; border-bottom: 2px solid #4a90e2;">
            결과 요약
        </h3>
        </div>
    """
    
    return complete_html



def show_detail(fin_scores):
    
    # 리포트 데이터 가져오기  
    report = st.session_state.selected_report
    
    # show_detail_common에서 기본 HTML을 가져옴
    base_html = show_detail_common(report['patient_id'])
    # 검사 결과 테이블 HTML 생성
    results_table = ""
    if report['type'] == "CLAP_A":
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
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center; vertical-align: middle; color: #333; font-size: 12px;">{fin_scores.get('LTN_RPT', '-')}점</td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center; vertical-align: middle; color: #333; font-size: 12px;">따라 말하기</td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center; vertical-align: middle; color: #333; font-size: 12px;">{fin_scores.get('LTN_RPT', '-')}점</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center; vertical-align: middle; color: #333; font-size: 12px;">끝말 맞추기 (5)</td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center; vertical-align: middle; color: #333; font-size: 12px;">{fin_scores.get('GUESS_END', '-')}점</td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center; vertical-align: middle; color: #333; font-size: 12px;" rowspan="3">이름대기 및<br>날말찾기</td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center; vertical-align: middle; color: #333; font-size: 12px;" rowspan="3">{fin_scores.get('GUESS_END', 0) + fin_scores.get('SAY_OBJ', 0) + fin_scores.get('SAY_ANI', 0)}점</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center; vertical-align: middle; color: #333; font-size: 12px;">물건 이름 말하기 (10)</td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center; vertical-align: middle; color: #333; font-size: 12px;">{fin_scores.get('SAY_OBJ', '-')}점</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center; vertical-align: middle; color: #333; font-size: 12px;">동물 이름 말하기 (1)</td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center; vertical-align: middle; color: #333; font-size: 12px;">{fin_scores.get('SAY_ANI', '-')}점</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center; vertical-align: middle; color: #333; font-size: 12px;">그림보고 이야기하기</td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center; vertical-align: middle; color: #333; font-size: 12px;">{fin_scores.get('TALK_PIC', '-')}점</td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center; vertical-align: middle; color: #333; font-size: 12px;">스스로 말하기</td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center; vertical-align: middle; color: #333; font-size: 12px;">{fin_scores.get('TALK_PIC', '-')}점</td>
                </tr>
                <tr style="background-color: #e3f2fd; font-weight: bold;">
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center; vertical-align: middle; color: #1976d2; font-weight: bold; font-size: 12px;">합계</td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center; vertical-align: middle; color: #1976d2; font-weight: bold; font-size: 12px;">{fin_scores.get('LTN_RPT', 0) + fin_scores.get('GUESS_END', 0) + fin_scores.get('SAY_OBJ', 0) + fin_scores.get('SAY_ANI', 0) + fin_scores.get('TALK_PIC', 0)}점</td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center; vertical-align: middle; color: #1976d2;"></td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center; vertical-align: middle; color: #1976d2; font-weight: bold; font-size: 12px;">{fin_scores.get('LTN_RPT', 0) + fin_scores.get('GUESS_END', 0) + fin_scores.get('SAY_OBJ', 0) + fin_scores.get('SAY_ANI', 0) + fin_scores.get('TALK_PIC', 0)}점</td>
                </tr>
            </tbody>
        </table>
        
        """
        fig = show_graph(fin_scores)
        st.pyplot(fig)
        
    elif report['type'] == "CLAP_D":
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
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center; vertical-align: middle; color: #333; font-size: 12px;">최대 발성시간 {fin_scores.get('AH_SOUND', 'NaN')}초</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center; vertical-align: middle; color: #333; font-size: 12px;">'퍼' 반복하기</td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center; vertical-align: middle; color: #333; font-size: 12px;">평균 회수 {fin_scores.get('P_SOUND', 'NaN')}회</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center; vertical-align: middle; color: #333; font-size: 12px;">'터' 반복하기</td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center; vertical-align: middle; color: #333; font-size: 12px;">평균 회수 {fin_scores.get('T_SOUND', 'NaN')}회</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center; vertical-align: middle; color: #333; font-size: 12px;">'커' 반복하기</td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center; vertical-align: middle; color: #333; font-size: 12px;">평균 회수 {fin_scores.get('K_SOUND', 'NaN')}회</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center; vertical-align: middle; color: #333; font-size: 12px;">'퍼터커' 반복하기</td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center; vertical-align: middle; color: #333; font-size: 12px;">평균 회수 {fin_scores.get('PTK_SOUND', 'NaN')}회</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center; vertical-align: middle; color: #333; font-size: 12px;">또박또박 말하기<br>(단어수준)</td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center; vertical-align: middle; color: #333; font-size: 12px;">{fin_scores.get('TALK_CLEAN', 'NaN')}점</td>
                </tr>
            </tbody>
        </table>
        """
        st.session_state['model_completed']=True
    
    # 전체 HTML을 결합하고 컨테이너를 닫음
    complete_html = base_html + results_table + """
    </div>
    """
    
    # streamlit components를 사용하여 HTML 렌더링
    import streamlit.components.v1 as components
    components.html(complete_html, height=1200)
    
# def show_graph(fin_scores):
# import numpy as np
# import matplotlib.pyplot as plt

# (선택) 한글 폰트 설정 - 환경에 맞게 주석 해제해서 사용하세요.
# import matplotlib
# matplotlib.rcParams['font.family'] = 'AppleGothic'     # macOS
# matplotlib.rcParams['font.family'] = 'Malgun Gothic'   # Windows
# matplotlib.rcParams['axes.unicode_minus'] = False

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

    # Figure 생성
    fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))

    # 위쪽(북쪽)에서 시작, 시계방향
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)

    # 축/눈금
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)
    vmax = max(vals) if rmax is None else rmax
    if vmax <= 0:
        vmax = 1.0
    ax.set_ylim(0, vmax)

    # 레이더 폴리곤
    ax.plot(angles, vals_closed, linewidth=2)
    ax.fill(angles, vals_closed, alpha=0.25)

    return fig

import streamlit as st
from views.login_view import show_login_page
from services.db_service import get_db_modules,get_reports
from services.model_service import (
    get_talk_pic, get_ah_sound, get_ptk_sound, get_talk_clean, 
    get_say_ani, get_ltn_rpt, get_say_obj, get_guess_end
)
from models.guess_end import GuessEndInferencer
from utils.style_utils import apply_custom_css
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import streamlit.components.v1 as components
import tempfile
import os
from pathlib import Path
import pandas as pd



def show_main_interface(patient_id,path_info):
    # 초기화
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "리포트"
    if 'view_mode' not in st.session_state:
        st.session_state.view_mode = "list"

    # 사이드바
    with st.sidebar:
        st.title("👋 CLAP")
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
        # 파일 경로
        # save_dir = df['MAIN_PATH']
        # print('\n\n\n',save_dir)
    
    # 리포트 메인
    if st.session_state.current_page == "리포트":
        if st.session_state.view_mode == "list":
            show_report_page(patient_info['PATIENT_ID'].iloc[0] if not patient_info.empty else '')
        elif 'model_completed' not in st.session_state:
            spinner = st.spinner('평가 중...')
            spinner.__enter__()
            show_detail(model_process(path_info),spinner)
            st.session_state['model_completed']=True
        else:         
            model_comm, report_main = get_db_modules()    
            print('====>', st.session_state.patient_id,st.session_state.order_num,st.session_state.selected_filter)        
            msg, ret_df =report_main.get_assess_score(st.session_state.patient_id,st.session_state.order_num,st.session_state.selected_filter)
            print('---------')
# 에러 핸들링 문제, 환자id 조회 문제
            print(msg)
            print('---------')

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
        st.markdown("### 🐱 개발 중이니 고양이나 보세요!")
        st.image("https://cataas.com/cat?width=500&height=400", caption="매번 다른 고양이를 만나보세요!")
        
    # else:
    #     st.info("zip파일과 환자 번호를 모두 선택해 주세요")
    
def model_process(path_info):            
        # model_comm, report_main = get_db_modules()
        # 파일 경로와 목록 정보를 조회
        # print('\n\n\ndf',df)
        ret = path_info[['MAIN_PATH','SUB_PATH','FILE_NAME']]
        print('------------------------------------')
        print('ret:',ret)
        print('------------------------------------')

        ah_sound_path=[]
        ptk_sound_path=[]
        ltn_rpt_path=[]
        guess_end_path=[]
        say_ani_path=[]
        say_obj_path=[]
        talk_clean_path=[]
        talk_pic_path=[]

        ah_sound_result=None
        ptk_sound_result=[]
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
            ltn_rpt = get_ltn_rpt()
            ltn_rpt_result=ltn_rpt.predict_score(ltn_rpt_path)
            fin_scores['LTN_RPT']=ltn_rpt_result

        if len(guess_end_path)>0:
            guess_end = get_guess_end()
            temp=[]
            infer = guess_end.GuessEndInferencer(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "models", "guess_end_model.keras"))
            for idx,p in enumerate(guess_end_path):
                temp.append(infer.predict_guess_end(p,idx))
            guess_end_result=sum(temp)
            fin_scores['GUESS_END']=guess_end_result

        if len(say_obj_path)>0:
            say_obj = get_say_obj()
            say_obj_result=say_obj.predict_total_say_obj(say_obj_path[5],say_obj_path[8])  
            fin_scores['SAY_OBJ']=say_obj_result
            
        if len(say_ani_path)>0:
            say_ani = get_say_ani()
            say_ani_result=say_ani.score_audio(say_ani_path[0])
            fin_scores['SAY_ANI']=say_ani_result
            
        if len(talk_pic_path)>0:
            talk_pic = get_talk_pic()
            talk_pic_result=talk_pic.score_audio(talk_pic_path[0])
            fin_scores['TALK_PIC']=talk_pic_result
            
        if len(ah_sound_path)>0:
            ah_sound = get_ah_sound()
            ah_sound_result=round(ah_sound.analyze_pitch_stability(ah_sound_path[0]),2)
            fin_scores['AH_SOUND']=ah_sound_result

        if len(ptk_sound_path)>0:
            ptk_sound = get_ptk_sound()
            for i in range(2, len(ptk_sound_path), 3):  # 2, 5, 8, 11
                ptk_sound_result.append(ptk_sound.count_peaks_from_waveform(ptk_sound_path[i]))
            fin_scores['P_SOUND']=ptk_sound_result[0]
            fin_scores['T_SOUND']=ptk_sound_result[1]
            fin_scores['K_SOUND']=ptk_sound_result[2]
            fin_scores['PTK_SOUND']=ptk_sound_result[3]

                
        if len(talk_clean_path)>0:
            talk_clean = get_talk_clean()
            talk_clean_result=talk_clean.main(talk_clean_path)
            fin_scores['TALK_CLEAN']=talk_clean_result

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
                        st.session_state.model_completed=True
                        # ??? 또 모델링 함
                        st.rerun()
                
                st.divider()
    else:
        st.info(f"{st.session_state.selected_filter.replace('_','-')} 검사 결과가 없습니다.")


def show_detail_common(patient_id):
    col1, col2 = st.columns([3, 9])
    with col1:
        if st.button("< 뒤로가기"):
            st.session_state.view_mode = "list"
            st.rerun()
    with col2:
        st.markdown(f"<div style='margin-top: 5px; font-weight: bold; text-align: left; margin-left: 0px;'>Order: {st.session_state.selected_report['order_num']}</div>", unsafe_allow_html=True)
    st.header(st.session_state.selected_filter.replace('_','-'))
    st.subheader(f"전산화 언어 기능 선별 검사({'실어증' if st.session_state.selected_filter=='CLAP_A' else '마비말장애' if st.session_state.selected_filter=='CLAP_D' else ''}) 결과지")

    # 리포트 상세 가져오기
    model_comm, report_main = get_db_modules()
    msg, patient_detail = report_main.get_patient_info(patient_id,st.session_state.selected_report['order_num'])

    col1, col2, col3 = st.columns(3)
    with col1:
        st.write(f"의뢰 기관(과)/의뢰인 {patient_detail['REQUEST_ORG'][0]}")
        st.write(f"이름 {patient_detail['PATIENT_NAME'][0]} ")
        st.write(f"교육연수 {patient_detail['EDU'][0]}년")
        st.write(f"방언 NN")

    with col2:
        st.write(f"검사자명 {patient_detail['ASSESS_PERSON'][0]}")
        st.write(f"성별 {'여자' if patient_detail['SEX'][0]==1 else '남자'}")
        st.write(f"문해여부 NN")
        st.write(f"발병일 {patient_detail['POST_STROKE_DATE'][0]}")

    with col3:
        st.write(f"검사일자 {patient_detail['ASSESS_DATE'][0]} ")
        st.write(f"개인번호 {patient_detail['PATIENT_ID'][0]}")

    st.write(f"진단명 {patient_detail['STROKE_TYPE'][0]}")
    st.write(f"주요 뇌병변 I {patient_detail['DIAGNOSIS'][0]}")
    st.write(f"주요 뇌병변 II {patient_detail['DIAGNOSIS_ETC'][0]}")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.write(f"**편마비** {patient_detail['HEMIPLEGIA'][0]}")
    with col2:
        st.write(f"**무시증** {patient_detail['HEMINEGLECT'][0]}")
    with col3:
        st.write(f"**시야결손** {patient_detail['VISUAL_FIELD_DEFECT'][0]}")

    st.write(f"**기타 특이사항** ")
    # st.divider()



def show_detail(fin_scores):
    # spinner.__exit__(None, None, None)
    # CSS 스타일 적용
    apply_custom_css()
    
    # 리포트 데이터 가져오기
    report = st.session_state.selected_report
    #                         st.session_state.selected_report = {
                            # 'type': row['ASSESS_TYPE'],
                            # 'date': row['ASSESS_DATE'],
                            # 'patient_id': row['PATIENT_ID'],
                            # 'order_num': row['ORDER_NUM']
                        # }
    # score_df=pd.DataFrame([report[patient_id],report[order_num],report['type'],], columns = ['PATIENT_ID', 'ORDER_NUM', 'ASSESS_TYPE', 'QUESTION_CD', 'QUESTION_NO', 'QUESTION_MINOR_NO', 'SCORE'])
    # save_score(score_df):
    #     if (score_df is None) or (len(score_df) == 0):
    #         return f"오류 발생: 입력된 데이터가 없습니다."
    #     if len(score_df.columns) != 7:
    #         return f"오류 발생: 컬럼의 갯수가 7개가 아닙니다."
    # score_df.columns = ['PATIENT_ID', 'ORDER_NUM', 'ASSESS_TYPE', 'QUESTION_CD', 'QUESTION_NO', 'QUESTION_MINOR_NO', 'SCORE']
    
    show_detail_common(report['patient_id'])
    st.subheader("결과 요약")
    
    # 검사 결과
    # if not clap_a_data.empty:
    if report['type'] == "CLAP_A":
        
        # 차트
        table_html = f"""
        <table class="main-table">
            <thead>
                <tr class="header-row">
                    <th>문항 (개수)</th>
                    <th>결과</th>
                    <th colspan="2">실어증 점수</th>
                </tr>
            </thead>
            <tbody>
                <tr style="background-color: #f0f8ff;">
                    <td>듣고 따라 말하기 (10)</td>
                    <td>{fin_scores.get('LTN_RPT', '-')}점</td>
                    <td>따라 말하기</td>
                    <td>{fin_scores.get('LTN_RPT', '-')}점</td>
                </tr>
                <tr style="background-color: #f0f8ff;">
                    <td>끝말 맞추기 (5)</td>
                    <td>{fin_scores.get('GUESS_END', '-')}점</td>
                    <td rowspan="3">이름대기 및<br>날말찾기</td>
                    <td rowspan="3">{fin_scores.get('GUESS_END', 0) + fin_scores.get('SAY_OBJ', 0) + fin_scores.get('SAY_ANI', 0)}점</td>
                </tr>
                <tr style="background-color: #f0f8ff;">
                    <td>물건 이름 말하기 (10)</td>
                    <td>{fin_scores.get('SAY_OBJ', '-')}점</td>
                </tr>
                <tr style="background-color: #f0f8ff;">
                    <td>동물 이름 말하기 (1)</td>
                    <td>{fin_scores.get('SAY_ANI', '-')}점</td>
                </tr>
                <tr style="background-color: #f0f8ff;">
                    <td>그림 보고 이야기 하기</td>
                    <td>{fin_scores.get('TALK_PIC', '-')}점</td>
                    <td>스스로 말하기</td>
                    <td>{fin_scores.get('TALK_PIC', '-')}점</td>
                </tr>
                <tr class="total-row">
                    <td>합계</td>
                    <td>{fin_scores.get('LTN_RPT', 0) + fin_scores.get('GUESS_END', 0) + fin_scores.get('SAY_OBJ', 0) + fin_scores.get('SAY_ANI', 0) + fin_scores.get('TALK_PIC', 0)}점</td>
                    <td></td>
                    <td>{fin_scores.get('LTN_RPT', 0) + fin_scores.get('GUESS_END', 0) + fin_scores.get('SAY_OBJ', 0) + fin_scores.get('SAY_ANI', 0) + fin_scores.get('TALK_PIC', 0)}점</td>
                </tr>
            </tbody>
        </table>
        """
        
        st.markdown(table_html, unsafe_allow_html=True)

    # def show_clap_d_detail(fin_scores):
    elif report['type'] == "CLAP_D":

        """CLAP-D 상세 리포트 페이지"""
        # show_detail_common()
        # report = st.session_state.selected_report
        clap_d_data = get_reports(report['patient_id'], 'CLAP_D')
        
        # 검사 결과
        if not clap_d_data.empty:

            table_html = f"""
            <table class="main-table">
                <thead>
                    <tr class="header-row">
                        <th>문항 (개수)</th>
                        <th>점수</th>
                    </tr>
                </thead>
                <tbody>
                    <tr style="background-color: #f0f8ff;">
                        <td>'아' 소리내기 (10)</td>
                        <td>{fin_scores.get('AH_SOUND', '-')}점</td>
                    </tr>
                    <tr style="background-color: #f0f8ff;">
                        <td>'퍼' 반복하기 (10)</td>
                        <td>{fin_scores.get('P_SOUND', '-')}점</td>
                    </tr>
                    <tr style="background-color: #f0f8ff;">
                        <td>'터' 반복하기 (10)</td>
                        <td>{fin_scores.get('T_SOUND', '-')}점</td>
                    </tr>
                    <tr style="background-color: #f0f8ff;">
                        <td>'커' 반복하기 (10)</td>
                        <td>{fin_scores.get('K_SOUND', '-')}점</td>
                    </tr>
                    <tr style="background-color: #f0f8ff;">
                        <td>'퍼터커' 반복하기 (10)</td>
                        <td>{fin_scores.get('PTK_SOUND', '-')}점</td>
                    </tr>
                    <tr style="background-color: #f0f8ff;">
                        <td>또박또박 말하기</td>
                        <td>{fin_scores.get('TALK_CLEAN', '-')}점</td>
                    </tr>
                </tbody>
            </table>
            """
            
            st.markdown(table_html, unsafe_allow_html=True)
from project.ui.views import results_objectives_view
import streamlit as st
from views.login_view import show_login_page
from services.db_service import get_db_modules,get_reports
from services.model_service import get_model_modules
from models.guess_end import GuessEndInferencer
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import streamlit.components.v1 as components
import tempfile
import os
from utils.style_utils import create_evaluation_table_html
from pathlib import Path


def show_main_interface(patient_id,df):
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
            st.write(f"**{patient_info['PATIENT_NAME'].iloc[0]} {patient_info['AGE'].iloc[0]}세**")
            st.write(f"환자번호: {patient_info['PATIENT_ID'].iloc[0]}")
            st.write(f"성별: {'여성' if patient_info['SEX'].iloc[0]==1 else '남성'}")
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

    if 'upload_completed' in st.session_state:
        spinner = st.spinner('평가 중...')
        spinner.__enter__()
        # model_comm, report_main = get_db_modules()
        # 파일 경로와 목록 정보를 조회
        print('\n\n\ndf',df)
        ret = df[['MAIN_PATH','SUB_PATH','FILE_NAME']]
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
            # print(file_path)
            # print("--------------------- file_path ---------------------\n\n\n")
                # 파일 존재 여부 확인
            if not os.path.exists(file_path):
                st.warning(f"❌ 파일 없음: {file_path}")
                break
            
            t = file_path
            # print(f"최종 경로: {t}")
            # print("--------------------- t ---------------------\n\n\n")
            sub_path_parts = Path(sub_path).parts
            talk_pic, ah_sound, ptk_sound, talk_clean, say_ani,ltn_rpt,say_obj,guess_end = get_model_modules()
            if sub_path_parts[0].lower() == 'clap_d':
                # talk_pic, ah_sound, ptk_sound, talk_clean, say_ani,ltn_rpt = get_model_modules()
                
                
                if sub_path_parts[1] == '0':
                    ah_sound_path.append(t)
                    # print(ah_sound_path)
                    # print(ah_sound.analyze_pitch_stability(ah_sound_path[0]))
                    if 'ah_sound_result' not in st.session_state:
                        # talk_pic, ah_sound, ptk_sound, talk_clean = get_model_modules()
                        st.session_state.ah_sound_result=ah_sound.analyze_pitch_stability(ah_sound_path[0])
                        # print('-------------- ah_sound modeling(1번째 값) ---------------\n\n\n')

                elif sub_path_parts[1] == '1':
                    ptk_sound_path.append(t)

                    # print('-------------- ptk_sound modeling(1번째 값) ---------------\n\n\n')
                elif sub_path_parts[1] == '2':
                    talk_clean_path.append(t)
                    # print('-------------- talk_clean modeling(1번째 값) ---------------\n\n\n')
                elif sub_path_parts[1] == '3':
                    read_clean_path.append(t)
                # else도 고려?

            # a일때
            elif sub_path_parts[0].lower() == 'clap_a':
                if sub_path_parts[1] == '3':
                    ltn_rpt_path.append(t)
                elif sub_path_parts[1] == '4':
                    guess_end_path.append(t)
                    # print('------------------\n\n',guess_end_path,'------------------\n\n')
                    # print('------------------\n\n',t,'------------------\n\n')
                elif sub_path_parts[1] == '5':
                    say_obj_path.append(t)
                elif sub_path_parts[1] == '6':
                    say_ani_path.append(t)
                    if 'say_ani_result' not in st.session_state:
                        # talk_pic, ah_sound, ptk_sound, talk_clean = get_model_modules()
                        st.session_state.say_ani_result=say_ani.score_audio(say_ani_path[0])
                elif sub_path_parts[1] == '7':
                    talk_pic_path.append(t)
                    if 'talk_pic_result' not in st.session_state:
                        # talk_pic, ah_sound, ptk_sound, talk_clean = get_model_modules()
                        st.session_state.talk_pic_result=talk_pic.score_audio(talk_pic_path[0])
                    # print('-------------- talk_pic modeling(1번째 값) ---------------\n\n\n')
                    talk_pic_path.append(t)
        if 'talk_clean_result' not in st.session_state:
            # talk_pic, ah_sound, ptk_sound, talk_clean = get_model_modules()
            st.session_state.talk_clean_result=talk_clean.main(talk_clean_path)
        if 'guess_end_result' not in st.session_state:
            st.session_state.guess_end_result=[]
            infer = GuessEndInferencer(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "models", "guess_end_model.keras"))
            for idx,p in enumerate(guess_end_path):
                st.session_state.guess_end_result.append(infer.predict_guess_end(p,idx))
                # print('-----------------guess_end_result\n\n\n',st.session_state.guess_end_result,'-----------------\n\n\n')
            
        if 'ltn_rpt_result' not in st.session_state:
            # ltn_rpt.predict_score(t) 은 리스트를 파라미터로 받아야 하는데 원소를 받고있어서 에러
            st.session_state.ltn_rpt_result=ltn_rpt.predict_score(ltn_rpt_path)
        if 'say_obj_result' not in st.session_state:
            st.session_state.say_obj_result=say_obj.predict_total_say_obj(say_obj_path[5],say_obj_path[8])      
        if 'ptk_sound_result' not in st.session_state:
            # talk_pic, ah_sound, ptk_sound, talk_clean = get_model_modules()
            st.session_state.ptk_sound_result=[]
            for i in range(1,len(ptk_sound_path),3):
                st.session_state.ptk_sound_result.append(ptk_sound.count_peaks_from_waveform(ptk_sound_path[i]))
                # print('------------------i\n\n',i,'------------------\n\n')
        if st.session_state.current_page == "리포트":
            if st.session_state.view_mode == "list":
                show_report_page(patient_info['PATIENT_ID'].iloc[0] if not patient_info.empty else '')
            elif st.session_state.view_mode == "clap_a_detail":
                show_clap_a_detail()
            elif st.session_state.view_mode == "clap_d_detail":
                show_clap_d_detail()
                # 환자 정보 표시
                st.divider()
        else:
            st.markdown("### 🐱 개발 중이니 고양이나 보세요!")
            st.image("https://cataas.com/cat?width=500&height=400", caption="매번 다른 고양이를 만나보세요!")
        spinner.__exit__(None, None, None)
    
    else:
        st.info("zip파일과 환자 번호를 모두 선택해 주세요")
        # patient_info_str = '선택'
        # patient_info=all_patient_info[all_patient_info['patient_id']==patient_info_str]



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
        for idx, row in reports_df.iterrows():
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
                        if row['ASSESS_TYPE'] == "CLAP_A":
                            st.session_state.view_mode = "clap_a_detail"
                        else:
                            st.session_state.view_mode = "clap_d_detail"
                        st.rerun()
                
                st.divider()
    else:
        st.info(f"{st.session_state.selected_filter} 검사 결과가 없습니다.")


def show_detail_common():
    if st.button("< 뒤로가기"):
        st.session_state.view_mode = "list"
        st.rerun()
    st.header(st.session_state.selected_filter.replace('_','-'))
    st.subheader(f"전산화 언어 기능 선별 검사({'실어증' if st.session_state.selected_filter=='CLAP_A' else '마비말장애' if st.session_state.selected_filter=='CLAP_D' else ''}) 결과지")

    # 리포트 상세 가져오기
    model_comm, report_main = get_db_modules()
    msg, patient_detail = report_main.get_patient_info(st.session_state.selected_report['patient_id'],st.session_state.selected_report['order_num'])
    # report = st.session_state.selected_report
    # patient_detail = reports_df.get_patient_info(reports_df['patient_id']).iloc[0]
    # print(patient_info)
    # print("--------------------- patient_info ---------------------\n\n\n")
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
        st.write('동물 이름 말하기:',st.session_state.say_ani_result,'점')
        st.write('물건 이름 말하기:',st.session_state.say_obj_result,'점')
        st.write('듣고 따라 말하기:',st.session_state.ltn_rpt_result,'점')
        st.write('끝말 맞추기:',sum(st.session_state.guess_end_result),'점')
        # 차트
        # results_objectives_view.show_results_objectives_page()


def show_clap_d_detail():
    """CLAP-D 상세 리포트 페이지"""
    show_detail_common()
    report = st.session_state.selected_report
    clap_d_data = get_reports(report['patient_id'], 'CLAP_D')

    # 검사 결과

    if not clap_d_data.empty:
        st.subheader("결과 요약")

        st.write('아 소리내기:',round(st.session_state.ah_sound_result,2))
        st.write('퍼 반복하기:',st.session_state.ptk_sound_result[0])
        st.write('터 반복하기:',st.session_state.ptk_sound_result[1])
        st.write('커 반복하기:',st.session_state.ptk_sound_result[2])
        st.write('퍼터커 반복하기:',st.session_state.ptk_sound_result[3])
        st.write('또박또박 말하기:',st.session_state.talk_clean_result)
        # word_level,sentence_level,consonant_word,vowel_word,consonant_sentence='N','N','N','N','N'
        # max_time,pa_avg,ta_avg,ka_avg,ptk_avg='N','N','N','N','N'
        # total_score = 'N'
        # total_score = a_sound + pa_repeat + ta_repeat + ka_repeat + ptk_repeat + word_level + sentence_level

        # # ----------------------  임시 DB   ----------------
        # evaluation_data = [
        #     {
        #         'id': 'a_sound',
        #         'title': "'아' 소리내기",
        #         'summary': "최대 발성 시간 NN 초 총점 NN 점",
        #         'items': [
        #             {'no': '연습', 'content': "'아'"},
        #             {'no': '1', 'content': "1회차 '아'"},
        #             {'no': '', 'content': "2회차 '아'"}
        #         ]
        #     },
        #     {
        #         'id': 'pa_sound',
        #         'title': "'퍼' 반복하기",
        #         'summary': "평균 횟수 NN 번 총점 NN 점",
        #         'items': [
        #             {'no': '연습', 'content': "'퍼'"},
        #             {'no': '1', 'content': "1회차 '퍼'"},
        #             {'no': '', 'content': "2회차 '퍼'"},
        #             {'no': '', 'content': "3회차 '퍼'"}
        #         ]
        #     },
        #     {
        #         'id': 'ta_sound',
        #         'title': "'터' 반복하기",
        #         'summary': "평균 횟수 NN 번 총점 NN 점",
        #         'items': [
        #             {'no': '연습', 'content': "'터'"},
        #             {'no': '1', 'content': "1회차 '터'"},
        #             {'no': '', 'content': "2회차 '터'"},
        #             {'no': '', 'content': "3회차 '터'"}
        #         ]
        #     },
        #     {
        #         'id': 'ka_sound',
        #         'title': "'커' 반복하기",
        #         'summary': "평균 횟수 NN 번 총점 NN 점",
        #         'items': [
        #             {'no': '연습', 'content': "'커'"},
        #             {'no': '1', 'content': "1회차 '커'"},
        #             {'no': '', 'content': "2회차 '커'"},
        #             {'no': '', 'content': "3회차 '커'"}
        #         ]
        #     },
        #     {
        #         'id': 'ptk_sound',
        #         'title': "'퍼터커' 반복하기",
        #         'summary': "평균 횟수 NN 번 총점 NN 점",
        #         'items': [
        #             {'no': '연습', 'content': "'퍼터커'"},
        #             {'no': '1', 'content': "1회차 '퍼터커'"},
        #             {'no': '', 'content': "2회차 '퍼터커'"},
        #             {'no': '', 'content': "3회차 '퍼터커'"}
        #         ]
        #     }
        # ]
        # # --------------------------------------
        
        # # 평가 리스트
        # a_sound, pa_sound, ta_sound, ka_sound, ptk_sound = evaluation_data
        
        # evaluation_list = [a_sound, pa_sound, ta_sound, ka_sound, ptk_sound]

        # # for문으로 각 평가 테이블 생성
        # for eval_item in evaluation_list:
        #     html_content = create_evaluation_table_html(eval_item)
        #     # st.components.v1.html 사용 - 높이는 항목 수에 따라 동적으로 계산
        #     height = 150 + (len(eval_item['items']) * 35)  # 기본 높이 + 각 행당 35px
        #     components.html(html_content, height=height)
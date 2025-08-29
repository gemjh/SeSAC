import pandas as pd
import streamlit as st

def save_scores_to_db(fin_scores):
    """모델링 결과를 DB에 저장하는 함수"""
    # 세션에서 환자 정보 가져오기
    patient_id = st.session_state.selected_report['patient_id']
    order_num = st.session_state.selected_report['order_num'] 
    assess_type = st.session_state.selected_report['type']
    
    # QUESTION_NO와 QUESTION_MINOR_NO 매핑 (QUESTION_CD별로)
    question_mapping = {
        'LTN_RPT': {'QUESTION_NO': 0, 'QUESTION_MINOR_NO': 0},
        'GUESS_END': {'QUESTION_NO': 0, 'QUESTION_MINOR_NO': 0}, 
        'SAY_OBJ': {'QUESTION_NO': 0, 'QUESTION_MINOR_NO': 0},
        'SAY_ANI': {'QUESTION_NO': 0, 'QUESTION_MINOR_NO': 0},
        'TALK_PIC': {'QUESTION_NO': 0, 'QUESTION_MINOR_NO': 0},
        'AH_SOUND': {'QUESTION_NO': 0, 'QUESTION_MINOR_NO': 0},
        'P_SOUND': {'QUESTION_NO': 0, 'QUESTION_MINOR_NO': 0},
        'T_SOUND': {'QUESTION_NO': 0, 'QUESTION_MINOR_NO': 0},
        'K_SOUND': {'QUESTION_NO': 0, 'QUESTION_MINOR_NO': 0},
        'PTK_SOUND': {'QUESTION_NO': 0, 'QUESTION_MINOR_NO': 0},
        'TALK_CLEAN': {'QUESTION_NO': 0, 'QUESTION_MINOR_NO': 0}
    }
    
    # DataFrame 생성을 위한 데이터 준비
    score_data = []
    for question_cd, score in fin_scores.items():
        if question_cd in question_mapping:
            score_data.append({
                'PATIENT_ID': patient_id,
                'ORDER_NUM': order_num,
                'ASSESS_TYPE': assess_type,
                'QUESTION_CD': question_cd,
                'QUESTION_NO': question_mapping[question_cd]['QUESTION_NO'],
                'QUESTION_MINOR_NO': question_mapping[question_cd]['QUESTION_MINOR_NO'],
                'SCORE': score
            })
    
    # DataFrame 생성
    score_df = pd.DataFrame(score_data)
    
    # DB 모듈 가져와서 저장
    model_comm, report_main = get_db_modules()
    result = model_comm.save_score(score_df)
    
    return result

def get_db_modules():
    from db.src import model_comm, report_main
    return model_comm, report_main

# 리포트 조회 함수
def get_reports(patient_id, test_type=None):
    model_comm, report_main=get_db_modules()
    msg,df=report_main.get_assess_lst(patient_id)
    # print(df)
    try:
        if patient_id is not None:
            df.columns=[
                'ORDER_NUM', 'PATIENT_ID', 'PATIENT_NAME', 'AGE', 'SEX', 'ASSESS_TYPE', 'MAIN_PATH', 'ASSESS_DATE', 'REQUEST_ORG', 'ASSESS_PERSON'
            ]
    except Exception as e:
        print(f"환자 정보 호출 중 오류 발생: {e}")
        

    if test_type and test_type != "전체":
        df = df[df['ASSESS_TYPE'] == test_type]
    return df

import pandas as pd
import streamlit as st
from services.api_client import APIClient


def save_scores_to_db(fin_scores, order_num):
    """모델링 결과를 DB에 저장하는 함수"""
    # 세션에서 환자 정보 가져오기
    patient_id = st.session_state.patient_id
    # order_num = st.session_state.order_num 
    # assess_type = st.session_state.selected_filter
    
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
    # 폴더 구조대로 순서 배열
    # a_list=['LTN_RPT','GUESS_END','SAY_OBJ','SAY_ANI','TALK_PIC']
    # d_list=['AH_SOUND','P_SOUND','T_SOUND','K_SOUND','PTK_SOUND','TALK_CLEAN']

    # # DataFrame 생성을 위한 데이터 준비
    # score_data = []
    # for question_cd, score in fin_scores.items():
    #     if question_cd in question_mapping:
    #         score_data.append({
    #             'PATIENT_ID': patient_id,
    #             'ORDER_NUM': order_num,
    #             'ASSESS_TYPE': 'CLAP_A' if question_cd in a_list else 'CLAP_D' if question_cd in d_list else None,
    #             'QUESTION_CD': question_cd,
    #             'QUESTION_NO': question_mapping[question_cd]['QUESTION_NO'],
    #             'QUESTION_MINOR_NO': question_mapping[question_cd]['QUESTION_MINOR_NO'],
    #             'SCORE': score
    #         })

    # ===============================================
    # 2025.9.6 명명규칙이 다르면 예외처리하도록 수정(김재헌)
    # ===============================================

    a_list = ['LTN_RPT', 'GUESS_END', 'SAY_OBJ', 'SAY_ANI', 'TALK_PIC']
    d_list = ['AH_SOUND', 'P_SOUND', 'T_SOUND', 'K_SOUND', 'PTK_SOUND', 'TALK_CLEAN']

    # 빠른 조회용 매핑(파이썬 특)
    assess_lookup = {**{k: 'CLAP_A' for k in a_list},
                    **{k: 'CLAP_D' for k in d_list}}

    # DataFrame 생성을 위한 데이터 준비
    score_data = []
    for question_cd, score in fin_scores.items():
        if question_cd in question_mapping:
            try:
                assess_type = assess_lookup.get(question_cd)
                if assess_type not in ['CLAP_A', 'CLAP_D']:
                    raise ValueError(
                        f"잘못된 ASSESS_TYPE: '{assess_type}'. "
                        f"question_cd='{question_cd}'는 등록되어 있지 않습니다. "
                        f"허용되는 값은 CLAP_A, CLAP_D 입니다."
                    )
            except ValueError as e:
                # 필요 시 로깅 후 재전파
                print(f"[DB 저장 중 에러] {e}")
                raise

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
    model_comm, _ = get_db_modules()
    result = model_comm.save_score(score_df)
    
    return result

# 리포트 조회 함수
def get_reports_local(patient_id, test_type=None):
    _, report_main=get_db_modules()

    msg,df=report_main.get_assess_lst(patient_id)
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

def get_reports(patient_id, test_type=None):
    """리포트 조회 - API 버전"""
    try:
        assessments = APIClient.get_assessments(patient_id, test_type)
        df = pd.DataFrame(assessments)
        return df
    except Exception as e:
        print(f"API 호출 중 오류 발생: {e}")
        return pd.DataFrame()

def get_db_modules():
    from db.src import model_comm, report_main
    return model_comm, report_main


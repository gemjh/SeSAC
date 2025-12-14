# #################################################### #
# model_comm : programming by joon0
# 
# [History]
# 2025.08.11 : 개발 시작 
# 2025.08.20 : 
#   1. save_score 개발 (환자의 평가 점수 저장)
#   2. delete_score 개발 (환자의 평가 점수 삭제)
# #################################################### #

from dotenv import load_dotenv
from pathlib import Path
import os
import mysql.connector
import pandas as pd
import streamlit as st

env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

def get_connection():
    try:
        # Railway DB 연결
        conn = mysql.connector.connect(
            host=os.getenv("db_host"),
            database=os.getenv("db_database"),
            user=os.getenv("db_username"),
            password=os.getenv("db_password"),
            port=int(os.getenv("db_port", 3306))
        )
        
        if conn.is_connected():
            print("✅ Railway DB 연결 성공!")
    except mysql.connector.Error as e:
        print(f"❌ 연결 실패: {e}")
    return conn

def is_invalid(value):
    return pd.isna(value) or value == ""

# ####################################### #
# get_file_lst
# 파일 경로와 목록 정보를 조회
# ####################################### #
def get_file_lst(assess_type, question_cd, question_no=None, order_num=None):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = ""
        sql +=  "select lst.PATIENT_ID, lst.ORDER_NUM, lst.ASSESS_TYPE, lst.QUESTION_CD, lst.QUESTION_NO, lst.QUESTION_MINOR_NO "
        sql +=  "   , concat(lst.MAIN_PATH,'/',lst.SUB_PATH) as PATH, lst.FILE_NAME, lst.DURATION, lst.RATE "
        sql +=  "	, ref.SCORE, alc.SCORE_ALLOCATION as alc_score, alc.note "
        sql +=  "from assess_file_lst lst "
        sql +=  "	inner join assess_lst alst "
        sql +=  "		on lst.PATIENT_ID = alst.PATIENT_ID "
        sql +=  "		and lst.ORDER_NUM = alst.ORDER_NUM "
        sql +=  "		and alst.EXCLUDED = '0' "
        sql +=  "	inner join assess_score_reference ref "
        sql +=  "		on lst.PATIENT_ID = ref.PATIENT_ID "
        sql +=  "		and lst.ORDER_NUM = ref.ORDER_NUM "
        sql +=  "		and lst.ASSESS_TYPE = ref.ASSESS_TYPE "
        sql +=  "		and lst.QUESTION_CD = ref.QUESTION_CD "
        sql +=  "		and lst.QUESTION_NO = ref.QUESTION_NO "
        sql +=  "       and ref.USE_YN = 'Y' "
        sql +=  "	left outer join assess_score_allocation alc "
        sql +=  "		on lst.ASSESS_TYPE = alc.ASSESS_TYPE "
        sql +=  "		and lst.QUESTION_CD = alc.QUESTION_CD "
        sql +=  "		and lst.QUESTION_NO = alc.QUESTION_NO "
        sql += f"where lst.ASSESS_TYPE = '{assess_type}' "
        sql += f"and lst.QUESTION_CD = '{question_cd}' "
        if question_no:
            sql += f"and lst.QUESTION_NO = {question_no} "
        if order_num:
            sql += f"and lst.ORDER_NUM = {order_num} "
        sql +=  "and lst.USE_YN = 'Y' "
    
        cursor.execute(sql)
        rows = cursor.fetchall()
        ret_df = pd.DataFrame(rows, columns=['PATIENT_ID', 'ORDER_NUM', 'ASSESS_TYPE', 'QUESTION_CD', 'QUESTION_NO', 'QUESTION_MINOR_NO', 'Path','File Name','Duration', 'Rate', 'Score(Refer)', 'Score(Alloc)', 'Note' ])

        msg = f'{len(ret_df)}건의 데이터가 조회되었습니다.'
        return msg, ret_df

    except Exception as e:
        return f"오류 발생: {str(e)}", None

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# ####################################### #
# save_score : 환자의 평가 점수를 저장한다. (insert or update)
# 입력 받는 dataframe의 컬럼은 다음과 같아야 한다. 
# ['PATIENT_ID', 'ORDER_NUM', 'ASSESS_TYPE', 'QUESTION_CD', 'QUESTION_NO', 'QUESTION_MINOR_NO', 'SCORE']
# ########################################
def save_score(score_df):
    if (score_df is None) or (len(score_df) == 0):
        return f"오류 발생: 입력된 데이터가 없습니다."
    if len(score_df.columns) != 7:
        return f"오류 발생: 컬럼의 갯수가 7개가 아닙니다."
    
    score_df.columns = ['PATIENT_ID', 'ORDER_NUM', 'ASSESS_TYPE', 'QUESTION_CD', 'QUESTION_NO', 'QUESTION_MINOR_NO', 'SCORE']

    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        for i in range(len(score_df)):
            patient_id = st.session_state.patient_id
            order_num = score_df.iloc[i]['ORDER_NUM']
            assess_type = score_df.iloc[i]['ASSESS_TYPE']
            question_cd = score_df.iloc[i]['QUESTION_CD']
            question_no = score_df.iloc[i]['QUESTION_NO']
            question_minor_no = score_df.iloc[i]['QUESTION_MINOR_NO']
            score = score_df.iloc[i]['SCORE']

            # 변수에 값이 없는 경우에는 DB 저장시 오류가 발생하므로 값이 있는지 체크
            if any(is_invalid(v) for v in [patient_id, order_num, assess_type, question_cd, question_no, question_minor_no, score]):
                raise ValueError("필수 값 중 하나 이상이 비어 있습니다.")

            sql  =  ""
            sql +=  "insert into assess_score_t (PATIENT_ID, ORDER_NUM, ASSESS_TYPE, QUESTION_CD, QUESTION_NO, QUESTION_MINOR_NO, SCORE) "
            sql += f"values ('{patient_id}', {order_num}, '{assess_type}', '{question_cd}', {question_no}, {question_minor_no}, {score}) "
            sql +=  "on duplicate key update "
            sql += f"SCORE = {score}, "
            sql +=  "UPDATE_DATE = CURRENT_TIMESTAMP() "
        
            cursor.execute(sql)
            
        conn.commit()
        msg = f'{len(score_df)}건의 데이터를 저장하였습니다.'
        return msg

    except Exception as e:
        conn.rollback()
        return f"오류 발생: {str(e)}"
    
    except ValueError as e:
        return f"오류 발생: {str(e)}"

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# ####################################### #
# delete_score : 환자의 평가 점수를 삭제한다.
# ####################################### #
def delete_score(patient_id, order_num):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        if any(is_invalid(v) for v in [patient_id, order_num]):
            raise ValueError("필수 값 중 하나 이상이 비어 있습니다.")
        
        sql = f"delete from assess_score_t where PATIENT_ID = '{patient_id}' and ORDER_NUM = {order_num} "
        
        cursor.execute(sql)
        conn.commit()

        deleted_count = cursor.rowcount
        msg = f'{deleted_count}건의 데이터를 삭제하였습니다.'

        return msg
    except Exception as e:
        conn.rollback()
        return f"오류 발생: {str(e)}"
    
    except ValueError as e:
        return f"오류 발생: {str(e)}"

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# import sys
# sys.path.append('/Volumes/SSAM/project/db/src')

# import model_comm as mc

# # 평가 점수 조회
# import report_main as rep
# msg, df = rep.get_assess_score('1001', 1)
# df['SUBSET_TOTAL'] = df.groupby('SUBSET')['SCORE'].transform('sum')
# df
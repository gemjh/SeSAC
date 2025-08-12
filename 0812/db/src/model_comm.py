from dotenv import load_dotenv
from pathlib import Path
import os
import mysql.connector
import pandas as pd

env_path = Path(__file__).parent / "../.." / ".env"
load_dotenv(dotenv_path=env_path)

def get_connection():
    conn = mysql.connector.connect(
        host=os.getenv("db_host"),
        database=os.getenv("db_database"),
        user=os.getenv("db_username"),
        password=os.getenv("db_password")
    )
    return conn


# 파일 경로와 목록 정보를 조회
def get_file_lst(assess_type, question_cd, question_no=None, order_num=None):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = ""
        sql +=  "select lst.ORDER_NUM, lst.ASSESS_TYPE, lst.QUESTION_CD, lst.QUESTION_NO, lst.QUESTION_MINOR_NO "
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
        ret_df = pd.DataFrame(rows, columns=['ORDER_NUM', 'ASSESS_TYPE', 'QUESTION_CD', 'QUESTION_NO', 'QUESTION_MINOR_NO', 'Path','File Name','Duration', 'Rate', 'Score(Refer)', 'Score(Alloc)', 'Note' ])

        msg = f'{len(ret_df)}건의 데이터가 조회되었습니다.'
        return msg, ret_df

    except Exception as e:
        return f"오류 발생: {str(e)}", None

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

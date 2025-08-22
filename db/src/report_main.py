# #################################################### #
# report_main.py : programming by joon0
# 
# [History]
# 2025.08.09    : 개발 시작 
# 2025.08.21    : get_assess_lst 수정 => MAIN PATH 컬럼 추가
# #################################################### #

#import streamlit as st
from dotenv import load_dotenv
from pathlib import Path
import os
import mysql.connector
import pandas as pd

env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

def get_connection():
    conn = mysql.connector.connect(
        host=os.getenv("db_host"),
        database=os.getenv("db_database"),
        user=os.getenv("db_username"),
        password=os.getenv("db_password")
    )
    return conn


# ####################################### #
# get_patient_lst : 환자 목록 조회
# ####################################### #
def get_patient_lst():
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = ""
        sql += "select p.PATIENT_ID, p.NAME, p.SEX, max(lst.AGE) as AGE "
        sql += "from patient_info p "
        sql += "	, assess_lst lst "
        sql += "where p.PATIENT_ID = lst.PATIENT_ID "
        sql += "and lst.EXCLUDED = '0' "
        sql += "group by p.PATIENT_ID, p.NAME, p.SEX "

        cursor.execute(sql)
        rows = cursor.fetchall()

        ret_df = pd.DataFrame(rows, columns=['PATIENT_ID', 'Name', 'Sex', 'Age'])
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
# get_assess_lst : 환자 ID를 기준으로 평가목록 조회
# ####################################### #
def get_assess_lst(patient_id, assess_type=None):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = ""
        sql += "select distinct lst.ORDER_NUM, lst.PATIENT_ID, p.name, lst.AGE, p.SEX, flst.ASSESS_TYPE, flst.MAIN_PATH, lst.ASSESS_DATE, lst.REQUEST_ORG, lst.ASSESS_PERSON "
        sql += "from assess_lst lst "
        sql += "	, patient_info p "
        sql += "	, assess_file_lst flst "
        sql += "where lst.PATIENT_ID = p.PATIENT_ID "
        sql += "and lst.PATIENT_ID = flst.PATIENT_ID "
        sql += "and lst.ORDER_NUM = flst.ORDER_NUM "
        sql += f"and lst.PATIENT_ID = '{patient_id}' "
        if assess_type != None:
            sql += f"and flst.ASSESS_TYPE = '{assess_type}' "

        cursor.execute(sql)
        rows = cursor.fetchall()

        ret_df = pd.DataFrame(rows, columns=['ORDER_NUM', 'PATIENT_ID', 'PATIENT_NAME', 'AGE', 'SEX', 'ASSESS_TYPE', 'MAIN_PATH', 'ASSESS_DATE', 'REQUEST_ORG', 'ASSESS_PERSON'])
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
# get_patient_info : 환자 정보 가져오기
# ####################################### #
def get_patient_info(patient_id, order_num):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = ""
        sql +=  "select p.PATIENT_ID, p.NAME, p.SEX "
        sql +=  ", lst.REQUEST_ORG, lst.ASSESS_DATE, lst.ASSESS_PERSON, lst.AGE, lst.EDU, lst.POST_STROKE_DATE "
        sql +=  ", lst.DIAGNOSIS, lst.DIAGNOSIS_ETC, lst.STROKE_TYPE, lst.LESION_LOCATION "
        sql +=  ", lst.HEMIPLEGIA, lst.HEMINEGLECT, lst.VISUAL_FIELD_DEFECT "
        sql +=  "from patient_info p, assess_lst lst "
        sql +=  "where p.PATIENT_ID = lst.PATIENT_ID "
        sql += f"and p.PATIENT_ID = '{patient_id}' "
        sql += f"and lst.ORDER_NUM = {order_num} "

        cursor.execute(sql)
        rows = cursor.fetchall()

        ret_df = pd.DataFrame(rows, columns=['PATIENT_ID', 'PATIENT_NAME', 'SEX', 'REQUEST_ORG', 'ASSESS_DATE', 'ASSESS_PERSON', 'AGE', 'EDU', 'POST_STROKE_DATE', 'DIAGNOSIS', 'DIAGNOSIS_ETC', 'STROKE_TYPE', 'LESION_LOCATION', 'HEMIPLEGIA', 'HEMINEGLECT', 'VISUAL_FIELD_DEFECT'])
        msg = f'{len(ret_df)}건의 데이터가 조회되었습니다.'
        return msg, ret_df

    except Exception as e:
        return f"오류 발생: {str(e)}", None

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
import streamlit as st
import mysql.connector
import pandas as pd

def get_connection():
    conn = mysql.connector.connect(
        host=st.secrets["mysql"]["host"],
        database=st.secrets["mysql"]["database"],
        user=st.secrets["mysql"]["username"],
        password=st.secrets["mysql"]["password"]
    )
    return conn

# 환자 ID를 기준으로 평가목록 조회
def get_assess_lst(patient_id, assess_type=None):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = ""
        sql += "select distinct lst.PATIENT_ID, p.name, lst.AGE, p.SEX, flst.ASSESS_TYPE, lst.ASSESS_DATE, lst.REQUEST_ORG, lst.ASSESS_PERSON "
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

        ret_df = pd.DataFrame(rows)
        msg = f'{len(ret_df)}건의 데이터가 조회되었습니다.'
        return msg, ret_df

    except Exception as e:
        return f"오류 발생: {str(e)}", None

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# 환자 목록 조회
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
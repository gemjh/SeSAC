#import streamlit as st
from dotenv import load_dotenv
from pathlib import Path
import os
import mysql.connector
import pandas as pd

env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


def get_connection():
    host = os.getenv("db_host")
    database = os.getenv("db_database") 
    user = os.getenv("db_username")
    password = os.getenv("db_password")
    
    print(f"DB 연결 정보 - host: {host}, database: {database}, user: {user}, password: {'설정됨' if password else '없음'}")
    
    conn = mysql.connector.connect(
        host=host,
        database=database,
        user=user,
        password=password
    )
    return conn


# 환자 정보
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

# 리포트 메인용 - 환자 ID를 기준으로 평가목록 조회
def get_report_main(patient_id, assess_type=None):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = """ 
        SELECT DISTINCT 
            lst.patient_id,
            lst.order_num, 
            lst.REQUEST_ORG, 
            lst.assess_date, 
            lst.ASSESS_PERSON, 
            flst.ASSESS_TYPE, 
            flst.MAIN_PATH,
            p.NAME,
            p.SEX,
            lst.AGE
        FROM assess_lst lst
        JOIN assess_file_lst flst
            ON lst.PATIENT_ID = flst.PATIENT_ID
            AND lst.ORDER_NUM = flst.ORDER_NUM
        JOIN patient_info p
            ON lst.PATIENT_ID = p.PATIENT_ID
        WHERE lst.PATIENT_ID = %s
        """

        params = [patient_id]

        if assess_type is not None:
            sql += " AND flst.ASSESS_TYPE = %s"
            params.append(assess_type)

        cursor.execute(sql, tuple(params))
        rows = cursor.fetchall()
        ret_df = pd.DataFrame(
            rows,
            columns=[
                'PATIENT_ID','ORDER_NUM','REQUEST_ORG','ASSESS_DATE',
                'ASSESS_PERSON','ASSESS_TYPE','MAIN_PATH','PATIENT_NAME','SEX','AGE'
            ]
        )
        msg = f'{len(ret_df)}건의 데이터가 조회되었습니다.'
        return msg, ret_df


    except Exception as e:
        return f"오류 발생: {str(e)}", None

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# 리포트 상세용 - 환자 정보 가져오기
def get_patient_info(patient_id, order_num):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = ""
        sql +=  "select p.PATIENT_ID, p.NAME, p.SEX "
        sql +=  ", lst.ORDER_NUM,lst.REQUEST_ORG, lst.ASSESS_DATE, lst.ASSESS_PERSON, lst.AGE, lst.EDU, lst.POST_STROKE_DATE "
        sql +=  ", lst.DIAGNOSIS, lst.DIAGNOSIS_ETC, lst.STROKE_TYPE, lst.LESION_LOCATION "
        sql +=  ", lst.HEMIPLEGIA, lst.HEMINEGLECT, lst.VISUAL_FIELD_DEFECT "
        sql +=  "from patient_info p, assess_lst lst "
        sql +=  "where p.PATIENT_ID = lst.PATIENT_ID "
        sql += f"and p.PATIENT_ID = '{patient_id}' "
        sql += f"and lst.ORDER_NUM = {order_num} "

        cursor.execute(sql)
        rows = cursor.fetchall()

        ret_df = pd.DataFrame(rows, columns=['PATIENT_ID', 'PATIENT_NAME', 'SEX', 'ORDER_NUM','REQUEST_ORG', 'ASSESS_DATE', 'ASSESS_PERSON', 'AGE', 'EDU', 'POST_STROKE_DATE', 'DIAGNOSIS', 'DIAGNOSIS_ETC', 'STROKE_TYPE', 'LESION_LOCATION', 'HEMIPLEGIA', 'HEMINEGLECT', 'VISUAL_FIELD_DEFECT'])
        msg = f'{len(ret_df)}건의 데이터가 조회되었습니다.'
        return msg, ret_df

    except Exception as e:
        return f"오류 발생: {str(e)}", None

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
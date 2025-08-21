# #################################################### #
# ZIP_UPLOAD : programming by joon0
# 
# [History]
# 2025.07.30    : 개발 시작 
#                 streamlit에 폴더 업로드 기능을 지원하지 않는 것을 확인
#                 개발 방향 : wave 파일을 폴더 채로 압축해서 업로드를 하고, 압축을 해제하여 wave 파일 정보를 읽어 DB 테이블에 저장
# 2025.08.11~14 : 1. 변경된 디렉토리 구조에 대해 조회하여 파일 정보 가져오기
#                 2. 중복 문제가 있는 경우 minor 번호가 작은 것을 use_yn = ‘N’으로 반영
#                 3. ASSESS_SCORE 테이블에 데이터 입력
# 2025.08.18~19 : 1. 환자 정보 파일(csv)을 읽어 assess_lst 테이블에 저장 추가
#                 2. env에 base_path 적용 ⇒ 파일 업로드 실행시 파일을 저장하는 폴더를 고정
#                 3. 파일 저장 경로를 files/upload로 지정, 
#                 4. logging 적용
# #################################################### #

from dotenv import load_dotenv
from pathlib import Path
import os
import logging
import streamlit as st
import mysql.connector
from datetime import datetime
import zipfile
import shutil
import wave
import pandas as pd
import re

logging.basicConfig(level=logging.INFO)

env_path = Path(__file__).parent.parent.parent / ".env"   # .env 파일 위치에 맞게 수정
logging.debug("[env_path] %s", env_path)
load_dotenv(dotenv_path=env_path)
base_path = os.getenv("base_path")
logging.debug("[base_path] %s", base_path)


def get_connection():
    conn = mysql.connector.connect(
        host=os.getenv("db_host"),
        database=os.getenv("db_database"),
        user=os.getenv("db_username"),
        password=os.getenv("db_password")
    )
    return conn

# st.title("zip 파일 upload")

# patient_id = st.text_input("환자ID를 입력하세요.")

# uploaded_file = st.file_uploader("폴더를 압축(zip)한 파일을 업로드하세요.", type=['zip'])

# btn_apply = st.button("파일 업로드")
def zip_upload(btn_apply,patient_id,uploaded_file):
    if btn_apply & (patient_id is not None) & (uploaded_file is not None):
        logging.info("[START] zip upload ")
        logging.debug("[uploaded_file.name] %s", uploaded_file.name)

        folder_path = ''
        folder_name = ''
        new_folder_name = ''
        new_folder_path = ''

        extract_path = "files/temp"
        upload_folder = "files/upload"
        upload_path = os.path.join(base_path, upload_folder)
        # logging.debug("[upload_path] %s", upload_path)

        # 압축 해제
        with zipfile.ZipFile(uploaded_file, "r") as zip_ref:
            zip_ref.extractall(extract_path)

        # 폴더명 수정
        for folder_name in os.listdir(extract_path):
            folder_path = os.path.join(base_path, extract_path, folder_name)
        
            if os.path.isdir(folder_path) and folder_name == (uploaded_file.name[:uploaded_file.name.rfind('.')]):
                current_time = datetime.now()
                str_date_time = current_time.isoformat().replace(':', "").replace('-', "").replace('.', "_")
                # 새 이름 설정 : 기존 폴더명+일자T시각_msec
                new_folder_name = folder_name+"_"+str_date_time
                new_folder_path = os.path.join(base_path, extract_path, new_folder_name)
                #logging.debug("[new_folder_path] %s", new_folder_path)
                
                # 이름 변경
                os.rename(folder_path, new_folder_path)
                logging.info(f"폴더 {folder_name} → {new_folder_name} 변경됨")

                break
        
        # 압축을 푼 폴더를 이동
        # logging.debug('------------')
        # logging.debug(new_folder_path)
        # logging.debug(upload_path)
        result = ''
        try:
            result = shutil.move(new_folder_path, upload_path)
            logging.info("파일 이동 성공: %s", result)
        except Exception as e:
            logging.error("파일 이동 실패 : %s", e)

        
        if os.path.exists(result):  # 파일 이동을 성공하면 파일 정보를 읽어 DB에 저장한다.
            # DB 연결
            conn = get_connection()
            cursor = conn.cursor()

            # 입력된 환자의 수행회차 가져오기 (없으면 1을 반환)
            sql = 'select ifnull(max(order_num)+1, 1) from assess_lst where PATIENT_ID = %s'
            cursor.execute(sql, (patient_id,))
            order_num = cursor.fetchall()[0][0]
            # logging.debug("[order_num] %s", order_num)

            target_path = os.path.join(upload_path, new_folder_name)
            logging.debug("[target_path] %s", target_path)

            #
            clap_A_cd = {'3':'LTN_RPT', '4':'GUESS_END', '5':'SAY_OBJ', '6':'SAY_ANI', '7':'TALK_PIC'}
            clap_D_cd = {'0':'AH_SOUND', '1':'PTK_SOUND', '2':'TALK_CLEAN', '3':'READ_CLEAN'}

            # 폴더 밑에 있는 파일 정보를 DB에 저장
            path_blitem = target_path
            #print(path_blitem)
            if os.path.isdir(path_blitem):
                sub_lst = os.listdir(path_blitem)

                for slitem in sub_lst:
                    path_slitem = os.path.join(target_path, slitem)
                    # 환자 검사 정보를 텍스트 파일(csv)에서 읽어 assess_lst 테이블에 저장. 파일명은 환자번호.csv (소문자로)
                    logging.debug("[path_slitem] %s", path_slitem)
                    if os.path.isfile(path_slitem):
                        file_nm = ".".join([patient_id, "csv"])
                        if (slitem == file_nm):
                            df = pd.read_csv(path_slitem)

                            pattern = r'^-?\d+(\.\d+)?$' # 숫자 패턴 체크용
                            sql = 'insert into assess_lst (PATIENT_ID, ORDER_NUM, REQUEST_ORG, ASSESS_DATE, ASSESS_PERSON, AGE, EDU, EXCLUDED, POST_STROKE_DATE, DIAGNOSIS, DIAGNOSIS_ETC, STROKE_TYPE, LESION_LOCATION, HEMIPLEGIA, HEMINEGLECT, VISUAL_FIELD_DEFECT) value \n'
                            for idx in range(len(df)):
                                patient_id = df.loc[idx, 'number']
                                request_org = df.loc[idx, '대상기관']
                                request_org = f"'{str(request_org)[:10]}'" if not pd.isna(request_org) else 'null'
                                assess_date = df.loc[idx, '검사일자']
                                assess_date = f"'{str(assess_date)[:10]}'" if not pd.isna(assess_date) else 'null'
                                assess_person = df.loc[idx, '검사자']
                                assess_person = f"'{assess_person}'" if not pd.isna(assess_person) else 'null'
                                code = df.loc[idx, 'code']
                                name = df.loc[idx, 'name']
                                age = df.loc[idx, 'age']
                                age = f"{int(age)}" if not pd.isna(age) else 'null'
                                sex = df.loc[idx, 'sex']
                                sex = f"'{int(sex)}'" if not pd.isna(sex) else 'null'
                                edu = df.loc[idx, 'edu']
                                edu = f"{int(edu)}" if not pd.isna(edu) else 'null'
                                excluded = df.loc[idx, 'excluded']
                                excluded = f"'{int(excluded)}'" if not pd.isna(excluded) else 'null'
                                post_stroke_date = df.loc[idx, 'post_stroke_date']
                                post_stroke_date = f"'{str(post_stroke_date)[:10]}'" if not pd.isna(post_stroke_date) else 'null'
                                diagnosis = df.loc[idx, 'diagnosis'] if not pd.isna(df.loc[idx, 'diagnosis']) else 'null'
                                if (diagnosis != 'null') & (bool(re.match(pattern, str(diagnosis))) != True):
                                    diagnosis_etc = f"'{diagnosis}'"
                                    diagnosis = "'4'"
                                elif diagnosis != 'null':
                                    diagnosis_etc = 'null'
                                    diagnosis = f"'{int(diagnosis)}'"
                                else:
                                    diagnosis_etc = 'null'
                                stroke_type = df.loc[idx, 'stroke_type']
                                stroke_type = f"'{int(stroke_type)}'" if not pd.isna(stroke_type) else 'null'
                                lesion_location = df.loc[idx, 'lesion_location']
                                lesion_location = lesion_location if not pd.isna(lesion_location) else 'null'
                                if (lesion_location != 'null') & (bool(re.match(pattern, str(lesion_location))) == True) & (type(lesion_location) == float):
                                    lesion_location = f"'{int(lesion_location)}'"
                                elif lesion_location != 'null':
                                    lesion_location = f"'{lesion_location}'"
                                hemiplegia = df.loc[idx, 'hemiplegia']
                                hemiplegia = hemiplegia if not pd.isna(hemiplegia) else 'null'
                                if (hemiplegia != 'null') & (bool(re.match(pattern, str(hemiplegia))) == True):
                                    hemiplegia = f"'{int(hemiplegia)}'" 
                                elif hemiplegia != 'null':
                                    hemiplegia = f"'{hemiplegia}'" 
                                hemineglect = df.loc[idx, 'hemineglect']
                                hemineglect = f"'{int(hemineglect)}'" if not pd.isna(hemineglect) else 'null'
                                visual_field_defect = df.loc[idx, 'visual field defect']
                                visual_field_defect = f"'{int(visual_field_defect)}'" if not pd.isna(visual_field_defect) else 'null'

                                sql += f"('{patient_id}', {order_num}, {request_org}, {assess_date}, {assess_person}, {age}, {edu}, {excluded}, {post_stroke_date}, {diagnosis}, {diagnosis_etc}, {stroke_type}, {lesion_location}, {hemiplegia}, {hemineglect}, {visual_field_defect}),\n"
                            sql = sql[:-2]
                            #print(sql)

                            # DB에 데이터 적재
                            try:
                                cursor.execute(sql)
                                logging.info('assess_lst 테이블에 %s 환자 정보 입력', patient_id)
                                conn.commit()
                            except Exception as e:
                                logging.error("[Exception] assess_lst 테이블에 %s 환자 정보 입력 중 오류 발생: %s", patient_id, e)
                                conn.rollback()  # 오류 발생 시 롤백

                    # 폴더 밑에 있는 wave 파일 정보를 저장
                    elif os.path.isdir(path_slitem):
                        if slitem == 'CLAP_A':
                            # CLAP_A에 대한 처리
                            sql = "INSERT INTO ASSESS_FILE_LST (PATIENT_ID,ORDER_NUM,ASSESS_TYPE,QUESTION_CD,QUESTION_NO,QUESTION_MINOR_NO,MAIN_PATH,SUB_PATH,FILE_NAME,DURATION,RATE) VALUES \n"
                            clap_a_lst = os.listdir(path_slitem)
                            for clap_a_item in clap_a_lst:
                                path_clap_a_item = os.path.join(target_path, slitem, clap_a_item)
                                if os.path.isdir(path_clap_a_item) & (clap_A_cd.get(clap_a_item) != None):

                                    # 파일 목록을 가져와 p_로 시작하는 파일 정보만 등록
                                    clap_a_sub_lst = os.listdir(path_clap_a_item)

                                    for item in clap_a_sub_lst:
                                        if item.startswith('p_'):
                                            # wave 파일의 총 시간을 구한다.
                                            with wave.open(os.path.join(path_clap_a_item, item), 'rb') as wav_file:
                                                frames = wav_file.getnframes()         # 전체 프레임 수
                                                rate = wav_file.getframerate()         # 샘플링 레이트 (초당 프레임 수)
                                                duration = frames / float(rate)        # 총 시간 (초)
                                                #print(f"{item} Duration: {duration:.2f} seconds, {rate}")
                                            spl_item = item.split('_')
                                            #sql += "('"+f"{patient_id}"+"', "+str(order_num)+", 'CLAP_A', '"+clap_A_cd.get(clap_a_item)+"', "+item.split('_')[1]+", "+item.split('_')[2][0]+", '"+upload_path+"/"+new_folder_name+"', 'CLAP_A/"+clap_a_item+"', '"+item+"', "+f"{duration:.2f}"+", "+f"{rate}"+"),\n"
                                            sql += f"('{patient_id}', {order_num}, 'CLAP_A', '{clap_A_cd.get(clap_a_item)}', {spl_item[1]}, {spl_item[2][0]}, '{new_folder_name}', '{slitem}/{clap_a_item}', '{item}', {duration:.2f}, {rate}),\n"
                                        else:
                                            continue
                            sql = sql[:-2]
                            # print(sql)
                            try:
                                cursor.execute(sql)
                                logging.info('ASSESS_FILE_LST 테이블에 데이터 입력 (%s/CLAP-A)', patient_id)
                                conn.commit()
                            except Exception as e:
                                logging.error("[Exception] ASSESS_FILE_LST 입력 (%s/CLAP-A) 중 오류 발생: %s", patient_id, e)
                                conn.rollback()  # 오류 발생 시 롤백
                            finally:
                                pass
                            #print('-'*20)
                        elif slitem == 'CLAP_D':
                            # CLAP_D에 대한 처리
                            sql = "INSERT INTO ASSESS_FILE_LST (PATIENT_ID,ORDER_NUM,ASSESS_TYPE,QUESTION_CD,QUESTION_NO,QUESTION_MINOR_NO,MAIN_PATH,SUB_PATH,FILE_NAME,DURATION,RATE) VALUES \n"
                            clap_d_lst = os.listdir(path_slitem)
                            for clap_d_item in clap_d_lst:
                                path_clap_d_item = os.path.join(target_path, slitem, clap_d_item)
                                if os.path.isdir(path_clap_d_item) & (clap_D_cd.get(clap_d_item) != None):

                                    # 파일 목록을 가져와 p_로 시작하는 파일 정보만 등록
                                    clap_d_sub_lst = os.listdir(path_clap_d_item)

                                    for item in clap_d_sub_lst:
                                        if item.startswith('p_'):
                                            # wave 파일의 총 시간을 구한다.
                                            with wave.open(os.path.join(path_clap_d_item, item), 'rb') as wav_file:
                                                frames = wav_file.getnframes()         # 전체 프레임 수
                                                rate = wav_file.getframerate()         # 샘플링 레이트 (초당 프레임 수)
                                                duration = frames / float(rate)        # 총 시간 (초)
                                                #print(f"{item} Duration: {duration:.2f} seconds, {rate}")
                                            spl_item = item.split('_')
                                            #sql += "('"+f"{patient_id}"+"', "+str(order_num)+", 'CLAP_D', '"+clap_D_cd.get(clap_d_item)+"', "+item.split('_')[1]+", "+item.split('_')[2][0]+", '"+upload_path+"/"+new_folder_name+"', 'CLAP_D/"+clap_d_item+"', '"+item+"', "+f"{duration:.2f}"+", "+f"{rate}"+"),\n"
                                            sql += f"('{patient_id}', {order_num}, 'CLAP_D', '{clap_D_cd.get(clap_d_item)}', {spl_item[1]}, {spl_item[2][0]}, '{new_folder_name}', '{slitem}/{clap_d_item}', '{item}', {duration:.2f}, {rate}),\n"
                                        else:
                                            continue
                            sql = sql[:-2]
                            #print(sql)
                            try:
                                cursor.execute(sql)
                                logging.info('ASSESS_FILE_LST 테이블에 데이터 입력 (%s/CLAP-D)', patient_id)
                                conn.commit()
                            except Exception as e:
                                logging.error("[Exception] ASSESS_FILE_LST 입력 (%s/CLAP-D) 중 오류 발생: %s", patient_id, e)
                                conn.rollback()  # 오류 발생 시 롤백
                            finally:
                                pass
                            #print('-'*20)
                        else:
                            continue

                # ASSESS_FILE_LST에 입력된 데이터의 문제별로 복수인지 확인하기
                sql = ""
                sql += "select PATIENT_ID, ORDER_NUM, ASSESS_TYPE, QUESTION_CD, QUESTION_NO, count(*) from assess_file_lst "
                sql += "where PATIENT_ID = %s "
                sql += " and ORDER_NUM = %s "
                sql += " and USE_YN = 'Y' "
                sql += "group by PATIENT_ID, ORDER_NUM, ASSESS_TYPE, QUESTION_CD, QUESTION_NO "
                sql += "having count(*) >= 2 "

                cursor.execute(sql, (str(patient_id), str(order_num)))
                rows = cursor.fetchall()
                if len(rows) > 0:   # 중복 데이터가 있다면
                    sql = "" 
                    # -- Step 1: 중복 조건에 해당하는 레코드 중 QUESTION_MINOR_NO가 가장 작은 것만 골라 임시 테이블로 저장
                    sql += "WITH ranked_records AS ( "
                    sql += "    SELECT  "
                    sql += "        *, "
                    sql += "        ROW_NUMBER() OVER ( "
                    sql += "            PARTITION BY PATIENT_ID, ORDER_NUM, ASSESS_TYPE, QUESTION_CD, QUESTION_NO "
                    sql += "            ORDER BY QUESTION_MINOR_NO ASC "
                    sql += "        ) AS rn "
                    sql += "    FROM assess_file_lst "
                    sql += "    WHERE (PATIENT_ID, ORDER_NUM, ASSESS_TYPE, QUESTION_CD, QUESTION_NO) IN ( "
                    sql += "        SELECT PATIENT_ID, ORDER_NUM, ASSESS_TYPE, QUESTION_CD, QUESTION_NO "
                    sql += "        FROM assess_file_lst "
                    sql += "        where PATIENT_ID = %s "
                    sql += "         and ORDER_NUM = %s "
                    sql += "         and USE_YN = 'Y' "
                    sql += "        GROUP BY PATIENT_ID, ORDER_NUM, ASSESS_TYPE, QUESTION_CD, QUESTION_NO "
                    sql += "        HAVING COUNT(*) >= 2 "
                    sql += "    ) "
                    sql += ") "

                    # -- Step 2: rn = 1인 레코드만 골라서 USE_YN 값을 'N'으로 업데이트
                    sql += "UPDATE assess_file_lst AS a "
                    sql += "JOIN ranked_records AS r "
                    sql += "  ON a.PATIENT_ID = r.PATIENT_ID "
                    sql += " AND a.ORDER_NUM = r.ORDER_NUM "
                    sql += " AND a.ASSESS_TYPE = r.ASSESS_TYPE "
                    sql += " AND a.QUESTION_CD = r.QUESTION_CD "
                    sql += " AND a.QUESTION_NO = r.QUESTION_NO "
                    sql += " AND a.QUESTION_MINOR_NO = r.QUESTION_MINOR_NO "
                    sql += "set a.USE_YN = 'N' "
                    sql += "WHERE r.rn = 1 "
                    try:
                        cursor.execute(sql, (str(patient_id), str(order_num)))
                        logging.info('ASSESS_FILE_LST 데이터 중복 처리 (%s)', patient_id)
                        conn.commit()
                    except Exception as e:
                        logging.error("[Exception] ASSESS_FILE_LST 데이터 중복 처리 (%s) 중 오류 발생: %s", patient_id, e)
                        conn.rollback()  # 오류 발생 시 롤백
                    finally:
                        pass

                # assess_score 테이블에 데이터 입력
                sql = ""
                sql += "INSERT INTO ASSESS_SCORE (PATIENT_ID, ORDER_NUM, ASSESS_TYPE, QUESTION_CD, QUESTION_NO, QUESTION_MINOR_NO, USE_YN) \n"
                sql += "SELECT PATIENT_ID, ORDER_NUM, ASSESS_TYPE, QUESTION_CD, QUESTION_NO, QUESTION_MINOR_NO, USE_YN \n "
                sql += "FROM ASSESS_FILE_LST \n"
                sql += "WHERE PATIENT_ID = %s AND ORDER_NUM = %s "
                try:
                    cursor.execute(sql, (str(patient_id), str(order_num)))
                    logging.info('ASSESS_SCORE 테이블에 데이터 입력(%s)', patient_id)
                    conn.commit()
                except Exception as e:
                    logging.error("[Exception] ASSESS_SCORE 입력(%s) 중 오류 발생: %s", patient_id, e)
                    conn.rollback()  # 오류 발생 시 롤백
                finally:
                    pass

                # 저장한 파일 정보를 조회
                try:
                    st.subheader("저장한 파일 정보 조회")
                    sql = "SELECT A.PATIENT_ID,A.ORDER_NUM,A.ASSESS_TYPE,A.QUESTION_CD,A.QUESTION_NO,A.MAIN_PATH,A.SUB_PATH,A.FILE_NAME \n"
                    sql += "FROM ASSESS_FILE_LST A, CODE_MAST C \n"
                    sql += "WHERE C.CODE_TYPE = 'ASSESS_TYPE' AND A.ASSESS_TYPE = C.MAST_CD AND A.QUESTION_CD=C.SUB_CD AND A.PATIENT_ID = %s AND A.ORDER_NUM = %s \n"
                    sql += "ORDER BY A.ASSESS_TYPE, C.ORDER_NUM, A.QUESTION_NO "
                    # print(sql)
                    cursor.execute(sql, (str(patient_id), str(order_num)))
                    rows = cursor.fetchall()
                    df = pd.DataFrame(rows, columns=['PATIENT_ID','ORDER_NUM','ASSESS_TYPE','QUESTION_CD','QUESTION_NO','MAIN_PATH','SUB_PATH','FILE_NAME'])
                    st.dataframe(df)
                except Exception as e:
                    logging.error("[Exception] 저장한 파일 정보 조회 중 오류 발생: %s", e)
                    # conn.rollback()  # 오류 발생 시 롤백

                # DB 연결 종료
                cursor.close()        
                conn.close()

        logging.info("-"*30)
    return df
    
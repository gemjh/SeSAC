import streamlit as st
import mysql.connector
from datetime import datetime
import zipfile
import os
import shutil
import wave
import pandas as pd
from dotenv import load_dotenv
from pathlib import Path


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

def zip_upload(patient_id,uploaded_file,btn_apply):
    # st.title("zip 파일 upload")

    # patient_id = st.text_input("환자ID를 입력하세요.")

    # uploaded_file = st.file_uploader("폴더를 압축(zip)한 파일을 업로드하세요.", type=['zip'])

    # btn_apply = st.button("파일 업로드")

    if btn_apply & (patient_id is not None) & (uploaded_file is not None):
        print(uploaded_file.name)
        with zipfile.ZipFile(uploaded_file, "r") as zip_ref:
            folder_path = ''
            folder_name = ''
            new_folder_name = ''
            new_folder_path = ''

            extract_path = "temp_upload_folder"
            upload_path = 'upload_folder'
            try:
                zip_ref.extractall(extract_path)
            except OSError as e:
                print(f"파일 다운로드 중 불필요한 파일 스킵: {extract_path}")
                pass
            # 폴더명 수정
            for folder_name in os.listdir(extract_path):
                folder_path = os.path.join('./'+extract_path, folder_name)
            
                if os.path.isdir(folder_path) and folder_name == (uploaded_file.name[:uploaded_file.name.rfind('.')]):
                    current_time = datetime.now()
                    str_date_time = current_time.isoformat().replace(':', "").replace('-', "").replace('.', "_")
                    # 새 이름 설정
                    new_folder_name = folder_name+"_"+str_date_time
                    new_folder_path = os.path.join('./'+extract_path, new_folder_name)
                    #print(new_folder_path)
                    
                    # 이름 변경
                    os.rename(folder_path, new_folder_path)
                    print(f"{folder_name} → {new_folder_name} 변경됨")

                    break
            
            # print(new_folder_path)
            # print(upload_path)
            # print('------------')
            shutil.move(new_folder_path, upload_path)
        

            
            # DB 연결
            conn = get_connection()
            cursor = conn.cursor()

            # 입력된 환자의 수행회차 가져오기 (없으면 1을 반환)
            sql = 'select ifnull(max(order_num)+1, 1) from assess_file_lst where PATIENT_ID = %s'
            cursor.execute(sql, (patient_id,))
            order_num = cursor.fetchall()[0][0]
            #print(order_num)

            base_path = os.path.join("./", upload_path, new_folder_name)
            print(base_path)

            # 환자 검사 정보를 텍스트 파일에서 읽어 assess_lst 테이블에 저장
            file_nm = "" 
            assess_info_file = os.path.join(base_path, file_nm)

            #
            clap_A_cd = {'3':'LTN_RPT', '4':'GUESS_END', '5':'SAY_OBJ', '6':'SAY_ANI', '7':'TALK_PIC'}
            clap_D_cd = {'0':'AH_SOUND', '1':'PTK_SOUND', '2':'TALK_CLEAN', '3':'READ_CLEAN'}

            # 폴더 밑에 있는 파일 정보를 DB에 저장
            path_blitem = base_path
            #print(path_blitem)
            #print(os.path.isdir(path_blitem))
            if os.path.isdir(path_blitem):
                sub_lst = os.listdir(path_blitem)
                #print(sub_lst)
                for slitem in sub_lst:
                    path_slitem = os.path.join(base_path, slitem)
                    if os.path.isdir(path_slitem):
                        if slitem == 'CLAP_A':
                            # CLAP_A에 대한 처리
                            sql = "INSERT INTO ASSESS_FILE_LST (PATIENT_ID,ORDER_NUM,ASSESS_TYPE,QUESTION_CD,QUESTION_NO,QUESTION_MINOR_NO,MAIN_PATH,SUB_PATH,FILE_NAME,DURATION,RATE) VALUES \n"
                            clap_a_lst = os.listdir(path_slitem)
                            for clap_a_item in clap_a_lst:
                                path_clap_a_item = os.path.join(base_path, slitem, clap_a_item)
                                if os.path.isdir(path_clap_a_item) & (clap_A_cd.get(clap_a_item) != None):
                                    #print(blitem, slitem, clap_a_item)
                                    # 파일 목록을 가져와 p_로 시작하는 파일 정보만 등록
                                    clap_a_sub_lst = os.listdir(path_clap_a_item)
                                    #print(clap_a_sub_lst)
                                    for item in clap_a_sub_lst:
                                        if item.startswith('p_'):
                                            # wave 파일의 총 시간을 구한다.
                                            with wave.open(os.path.join(path_clap_a_item, item), 'rb') as wav_file:
                                                frames = wav_file.getnframes()         # 전체 프레임 수
                                                rate = wav_file.getframerate()         # 샘플링 레이트 (초당 프레임 수)
                                                duration = frames / float(rate)        # 총 시간 (초)
                                                #print(f"{item} Duration: {duration:.2f} seconds, {rate}")
                                            sql += "('"+patient_id+"', "+str(order_num)+", 'CLAP_A', '"+clap_A_cd.get(clap_a_item)+"', "+item.split('_')[1]+", "+item.split('_')[2][0]+", '"+new_folder_name+"', 'clap_a/"+clap_a_item+"', '"+item+"', "+f"{duration:.2f}"+", "+str(rate)+"),\n"
                                        else:
                                            continue
                            sql = sql[:-2]
                            #print(sql)
                            try:
                                cursor.execute(sql)
                                print(f'ASSESS_FILE_LST 테이블에 데이터 입력({patient_id}/CLAP-A)')
                                conn.commit()
                            except Exception as e:
                                print(f"[Exception] ASSESS_FILE_LST 입력({patient_id}/CLAP-A) 중 오류 발생: {e}")
                                conn.rollback()  # 오류 발생 시 롤백
                            finally:
                                pass
                            #print('-'*20)
                        elif slitem == 'CLAP_D':
                            # CLAP_D에 대한 처리
                            sql = "INSERT INTO ASSESS_FILE_LST (PATIENT_ID,ORDER_NUM,ASSESS_TYPE,QUESTION_CD,QUESTION_NO,QUESTION_MINOR_NO,MAIN_PATH,SUB_PATH,FILE_NAME,DURATION,RATE) VALUES \n"
                            clap_d_lst = os.listdir(path_slitem)
                            for clap_d_item in clap_d_lst:
                                path_clap_d_item = os.path.join(base_path, slitem, clap_d_item)
                                if os.path.isdir(path_clap_d_item) & (clap_D_cd.get(clap_d_item) != None):
                                    #print(blitem, slitem, clap_a_item)
                                    # 파일 목록을 가져와 p_로 시작하는 파일 정보만 등록
                                    clap_d_sub_lst = os.listdir(path_clap_d_item)
                                    #print(clap_a_sub_lst)
                                    for item in clap_d_sub_lst:
                                        if item.startswith('p_'):
                                            # wave 파일의 총 시간을 구한다.
                                            with wave.open(os.path.join(path_clap_d_item, item), 'rb') as wav_file:
                                                frames = wav_file.getnframes()         # 전체 프레임 수
                                                rate = wav_file.getframerate()         # 샘플링 레이트 (초당 프레임 수)
                                                duration = frames / float(rate)        # 총 시간 (초)
                                                #print(f"{item} Duration: {duration:.2f} seconds, {rate}")
                                            sql += "('"+patient_id+"', "+str(order_num)+", 'CLAP_D', '"+clap_D_cd.get(clap_d_item)+"', "+item.split('_')[1]+", "+item.split('_')[2][0]+", '"+new_folder_name+"', 'clap_d/"+clap_d_item+"', '"+item+"', "+f"{duration:.2f}"+", "+str(rate)+"),\n"
                                        else:
                                            continue
                            sql = sql[:-2]
                            #print(sql)
                            try:
                                cursor.execute(sql)
                                print(f'ASSESS_FILE_LST 테이블에 데이터 입력({patient_id}/CLAP-D)')
                                conn.commit()
                            except Exception as e:
                                print(f"[Exception] ASSESS_FILE_LST 입력({patient_id}/CLAP-D) 중 오류 발생: {e}")
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

            cursor.execute(sql, (patient_id, str(order_num)))
            rows = cursor.fetchall()
            if len(rows) > 0:
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
                    cursor.execute(sql, (patient_id, str(order_num)))
                    print(f'ASSESS_FILE_LST 데이터 중복 처리({patient_id})')
                    conn.commit()
                except Exception as e:
                    print(f"[Exception] ASSESS_FILE_LST 데이터 중복 처리({patient_id}) 중 오류 발생: {e}")
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
                cursor.execute(sql, (patient_id, str(order_num)))
                print(f'ASSESS_SCORE 테이블에 데이터 입력({patient_id})')
                conn.commit()
            except Exception as e:
                print(f"[Exception] ASSESS_SCORE 입력({patient_id}) 중 오류 발생: {e}")
                conn.rollback()  # 오류 발생 시 롤백
            finally:
                pass

            # assess_lst 테이블에 데이터 입력
            # sql = ""
            # sql += "INSERT INTO ASSESS_LST (PATIENT_ID, ORDER_NUM, ASSESS_TYPE, QUESTION_CD, QUESTION_NO, QUESTION_MINOR_NO, USE_YN) \n"
            # sql += "SELECT PATIENT_ID, ORDER_NUM, ASSESS_TYPE, QUESTION_CD, QUESTION_NO, QUESTION_MINOR_NO, USE_YN \n "
            # sql += "FROM ASSESS_FILE_LST \n"
            # sql += "WHERE PATIENT_ID = %s AND ORDER_NUM = %s "
            # try:
            #     cursor.execute(sql, (patient_id, str(order_num)))
            #     print(f'ASSESS_LST 테이블에 데이터 입력({patient_id})')
            #     conn.commit()
            # except Exception as e:
            #     print(f"[Exception] ASSESS_LST 입력({patient_id}) 중 오류 발생: {e}")
            #     conn.rollback()  # 오류 발생 시 롤백
            # finally:
            #     pass

            # 저장한 파일 정보를 조회
            st.subheader("저장한 파일 정보 조회")
            sql = "SELECT A.PATIENT_ID,A.ORDER_NUM,A.ASSESS_TYPE,A.QUESTION_CD,A.QUESTION_NO,A.MAIN_PATH,A.SUB_PATH,A.FILE_NAME \n"
            sql += "FROM ASSESS_FILE_LST A, CODE_MAST C \n"
            sql += "WHERE C.CODE_TYPE = 'ASSESS_TYPE' AND A.ASSESS_TYPE = C.MAST_CD AND A.QUESTION_CD=C.SUB_CD AND A.PATIENT_ID = %s AND A.ORDER_NUM = %s \n"
            sql += "ORDER BY A.ASSESS_TYPE, C.ORDER_NUM, A.QUESTION_NO "
            # print(sql)
            cursor.execute(sql, (patient_id, str(order_num)))
            rows = cursor.fetchall()
            df = pd.DataFrame(rows, columns=['PATIENT_ID','ORDER_NUM','ASSESS_TYPE','QUESTION_CD','QUESTION_NO','MAIN_PATH','SUB_PATH','FILE_NAME'])
            st.dataframe(df)

            # DB 연결 종료
            cursor.close()        
            conn.close()
    return df
# #################################################### #
# ZIP_UPLOAD : API 연동 버전
# 
# [History]
# 2025.01.15    : API 연동으로 전면 수정
#                 - DB 직접 접근 제거
#                 - API 엔드포인트를 통한 메타데이터 전송
#                 - 파일 처리 로직은 로컬 유지
# #################################################### #

from dotenv import load_dotenv
from pathlib import Path
import os
import logging
import streamlit as st
from datetime import datetime
import zipfile
import shutil
import wave
import pandas as pd
import re
import requests
from typing import Tuple, Optional

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 환경변수 로드
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)
base_path = os.getenv("base_path")
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")

# 검사 타입 코드 매핑
clap_A_cd = {'3':'LTN_RPT', '4':'GUESS_END', '5':'SAY_OBJ', '6':'SAY_ANI', '7':'TALK_PIC'}
clap_D_cd = {'0':'AH_SOUND', '1':'PTK_SOUND', '2':'TALK_CLEAN', '3':'READ_CLEAN'}
clap_D_pkt_cd = {1:'P_SOUND', 2:'T_SOUND', 3:'K_SOUND', 4:'PTK_SOUND'}

class APIClient:
    """API 통신 클라이언트"""
    
    @staticmethod
    def get_order_num(patient_id: str) -> int:
        """환자의 수행회차 조회"""
        try:
            response = requests.get(
                f"{API_BASE_URL}/patients/{patient_id}/order",
                timeout=10
            )
            response.raise_for_status()
            return response.json().get('order_num', 1)
        except requests.exceptions.RequestException as e:
            logger.error(f"수행회차 조회 실패: {e}")
            raise Exception(f"API 호출 실패: {str(e)}")
    
    @staticmethod
    def save_patient_assessment(patient_id: str, order_num: int, csv_data: dict) -> bool:
        """환자 검사 정보 저장"""
        try:
            payload = {
                "patient_id": patient_id,
                "order_num": order_num,
                **csv_data
            }
            response = requests.post(
                f"{API_BASE_URL}/assessments/patient-info",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            logger.info(f"환자 검사 정보 저장 완료: {patient_id}")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"환자 검사 정보 저장 실패: {e}")
            return False
    
    @staticmethod
    def save_file_metadata(file_list: list) -> bool:
        """파일 메타데이터 일괄 저장"""
        try:
            response = requests.post(
                f"{API_BASE_URL}/assessments/files/bulk",
                json={"files": file_list},
                timeout=60
            )
            response.raise_for_status()
            logger.info(f"파일 메타데이터 저장 완료: {len(file_list)}건")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"파일 메타데이터 저장 실패: {e}")
            return False
    
    @staticmethod
    def handle_duplicate_files(patient_id: str, order_num: int) -> bool:
        """중복 파일 처리"""
        try:
            response = requests.post(
                f"{API_BASE_URL}/assessments/{patient_id}/{order_num}/deduplicate",
                timeout=30
            )
            response.raise_for_status()
            logger.info(f"중복 파일 처리 완료: {patient_id}")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"중복 파일 처리 실패: {e}")
            return False
    
    @staticmethod
    def initialize_scores(patient_id: str, order_num: int) -> bool:
        """점수 테이블 초기화"""
        try:
            response = requests.post(
                f"{API_BASE_URL}/assessments/{patient_id}/{order_num}/init-scores",
                timeout=30
            )
            response.raise_for_status()
            logger.info(f"점수 테이블 초기화 완료: {patient_id}")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"점수 테이블 초기화 실패: {e}")
            return False


def extract_and_rename_folder(uploaded_file, extract_path: str) -> Tuple[str, str]:
    """압축 해제 및 폴더명 변경"""
    # 압축 해제
    with zipfile.ZipFile(uploaded_file, "r") as zip_ref:
        zip_ref.extractall(extract_path)
    
    # 폴더명 수정
    folder_name = uploaded_file.name[:uploaded_file.name.rfind('.')]
    folder_path = os.path.join(base_path, extract_path, folder_name)
    
    if not os.path.isdir(folder_path):
        raise FileNotFoundError(f"압축 해제된 폴더를 찾을 수 없습니다: {folder_path}")
    
    current_time = datetime.now()
    str_date_time = current_time.isoformat().replace(':', "").replace('-', "").replace('.', "_")
    new_folder_name = f"{folder_name}_{str_date_time}"
    new_folder_path = os.path.join(base_path, extract_path, new_folder_name)
    
    os.rename(folder_path, new_folder_path)
    logger.info(f"폴더명 변경: {folder_name} → {new_folder_name}")
    
    return new_folder_name, new_folder_path


def parse_csv_file(csv_path: str) -> dict:
    """CSV 파일 파싱"""
    df = pd.read_csv(csv_path)
    pattern = r'^-?\d+(\.\d+)?$'
    
    csv_data = {}
    for idx in range(len(df)):
        # 필요한 필드만 추출 및 변환
        csv_data['request_org'] = str(df.loc[idx, '대상기관'])[:10] if not pd.isna(df.loc[idx, '대상기관']) else None
        csv_data['assess_date'] = str(df.loc[idx, '검사일자'])[:10] if not pd.isna(df.loc[idx, '검사일자']) else None
        csv_data['assess_person'] = df.loc[idx, '검사자'] if not pd.isna(df.loc[idx, '검사자']) else None
        csv_data['age'] = int(df.loc[idx, 'age']) if not pd.isna(df.loc[idx, 'age']) else None
        csv_data['sex'] = str(int(df.loc[idx, 'sex'])) if not pd.isna(df.loc[idx, 'sex']) else None
        csv_data['edu'] = int(df.loc[idx, 'edu']) if not pd.isna(df.loc[idx, 'edu']) else None
        csv_data['excluded'] = str(int(df.loc[idx, 'excluded'])) if not pd.isna(df.loc[idx, 'excluded']) else '0'
        csv_data['post_stroke_date'] = str(df.loc[idx, 'post_stroke_date'])[:10] if not pd.isna(df.loc[idx, 'post_stroke_date']) else None
        
        # diagnosis 처리
        diagnosis = df.loc[idx, 'diagnosis'] if not pd.isna(df.loc[idx, 'diagnosis']) else None
        if diagnosis and not bool(re.match(pattern, str(diagnosis))):
            csv_data['diagnosis_etc'] = str(diagnosis)
            csv_data['diagnosis'] = '4'
        elif diagnosis:
            csv_data['diagnosis'] = str(int(diagnosis))
            csv_data['diagnosis_etc'] = None
        else:
            csv_data['diagnosis'] = None
            csv_data['diagnosis_etc'] = None
        
        # 기타 필드
        csv_data['stroke_type'] = str(int(df.loc[idx, 'stroke_type'])) if not pd.isna(df.loc[idx, 'stroke_type']) else None
        
        lesion_location = df.loc[idx, 'lesion_location'] if not pd.isna(df.loc[idx, 'lesion_location']) else None
        if lesion_location and bool(re.match(pattern, str(lesion_location))):
            csv_data['lesion_location'] = str(int(float(lesion_location)))
        elif lesion_location:
            csv_data['lesion_location'] = str(lesion_location)
        else:
            csv_data['lesion_location'] = None
        
        hemiplegia = df.loc[idx, 'hemiplegia'] if not pd.isna(df.loc[idx, 'hemiplegia']) else None
        if hemiplegia and bool(re.match(pattern, str(hemiplegia))):
            csv_data['hemiplegia'] = str(int(hemiplegia))
        elif hemiplegia:
            csv_data['hemiplegia'] = str(hemiplegia)
        else:
            csv_data['hemiplegia'] = None
        
        csv_data['hemineglect'] = str(int(df.loc[idx, 'hemineglect'])) if not pd.isna(df.loc[idx, 'hemineglect']) else None
        csv_data['visual_field_defect'] = str(int(df.loc[idx, 'visual field defect'])) if not pd.isna(df.loc[idx, 'visual field defect']) else None
        
        break  # 첫 번째 행만 처리
    
    return csv_data


def process_wav_files(target_path: str, patient_id: str, order_num: int, new_folder_name: str) -> list:
    """WAV 파일 메타데이터 수집"""
    file_metadata_list = []
    
    for clap_type in ['CLAP_A', 'CLAP_D']:
        clap_path = os.path.join(target_path, clap_type)
        if not os.path.isdir(clap_path):
            continue
        
        clap_list = os.listdir(clap_path)
        code_dict = clap_A_cd if clap_type == 'CLAP_A' else clap_D_cd
        
        for clap_item in clap_list:
            item_path = os.path.join(clap_path, clap_item)
            if not os.path.isdir(item_path) or code_dict.get(clap_item) is None:
                continue
            
            sub_list = os.listdir(item_path)
            for filename in sub_list:
                if not filename.startswith('p_'):
                    continue
                
                # WAV 파일 정보 추출
                wav_path = os.path.join(item_path, filename)
                with wave.open(wav_path, 'rb') as wav_file:
                    frames = wav_file.getnframes()
                    rate = wav_file.getframerate()
                    duration = frames / float(rate)
                
                # 파일명 파싱
                spl_item = filename.split('_')
                question_no = int(spl_item[1])
                question_minor_no = int(spl_item[2][0])
                
                # QUESTION_CD 결정
                if clap_type == 'CLAP_D' and clap_item == '1':  # 퍼터커
                    pkt_idx = int((question_no + 2) / 3)
                    question_cd = clap_D_pkt_cd.get(pkt_idx)
                else:
                    question_cd = code_dict.get(clap_item)
                
                file_metadata_list.append({
                    'patient_id': patient_id,
                    'order_num': order_num,
                    'assess_type': clap_type,
                    'question_cd': question_cd,
                    'question_no': question_no,
                    'question_minor_no': question_minor_no,
                    'main_path': new_folder_name,
                    'sub_path': f"{clap_type}/{clap_item}",
                    'file_name': filename,
                    'duration': round(duration, 2),
                    'rate': rate
                })
    
    return file_metadata_list


def zip_upload(btn_apply: bool, patient_id: str, uploaded_file) -> Tuple[Optional[str], Optional[pd.DataFrame]]:
    """
    ZIP 파일 업로드 및 API를 통한 DB 저장
    
    Returns:
        Tuple[order_num, DataFrame]: 성공 시 회차 번호와 파일 정보 DataFrame, 실패 시 (None, None)
    """
    if not (btn_apply and patient_id and uploaded_file):
        return None, None
    
    logger.info("[START] ZIP 업로드 프로세스 시작")
    logger.debug(f"업로드 파일: {uploaded_file.name}")
    
    extract_path = os.path.join("files", "temp")
    upload_folder = os.path.join("files", "upload")
    upload_path = os.path.join(base_path, upload_folder)
    
    try:
        # 1. 압축 해제 및 폴더명 변경
        new_folder_name, new_folder_path = extract_and_rename_folder(uploaded_file, extract_path)
        
        # 2. 파일 이동
        result = shutil.move(new_folder_path, upload_path)
        if not os.path.exists(result):
            raise Exception("파일 이동 실패")
        logger.info(f"파일 이동 완료: {result}")
        
        target_path = os.path.join(upload_path, new_folder_name)
        
        # 3. API를 통한 수행회차 조회(1부터)
        order_num = APIClient.get_order_num(patient_id)
        logger.info(f"수행회차: {order_num}")
        
        # 4. CSV 파일 처리
        csv_found = False
        csv_file_path = os.path.join(target_path, f"{patient_id}.csv")
        
        if os.path.exists(csv_file_path):
            csv_found = True
            csv_data = parse_csv_file(csv_file_path)
            if not APIClient.save_patient_assessment(patient_id, order_num, csv_data):
                raise Exception("환자 검사 정보 저장 실패")
        else:
            # CSV 없을 경우 기본값으로 저장
            logger.warning(f"CSV 파일 없음 - 기본값으로 저장: {patient_id}")
            default_data = {'excluded': '0'}
            if not APIClient.save_patient_assessment(patient_id, order_num, default_data):
                raise Exception("환자 검사 정보 저장 실패 (기본값)")
        
        # 5. WAV 파일 메타데이터 수집
        file_metadata_list = process_wav_files(target_path, patient_id, order_num, new_folder_name)
        
        if not file_metadata_list:
            raise Exception("처리할 WAV 파일이 없습니다")
        
        logger.info(f"수집된 파일 메타데이터: {len(file_metadata_list)}건")
        
        # 6. API를 통한 파일 메타데이터 저장
        if not APIClient.save_file_metadata(file_metadata_list):
            raise Exception("파일 메타데이터 저장 실패")
        
        # 7. 중복 파일 처리
        if not APIClient.handle_duplicate_files(patient_id, order_num):
            raise Exception("중복 파일 처리 실패")
        
        # 8. 점수 테이블 초기화
        if not APIClient.initialize_scores(patient_id, order_num):
            raise Exception("점수 테이블 초기화 실패")
        
        # 9. 저장된 파일 정보 조회 (API 통해)
        try:
            response = requests.get(
                f"{API_BASE_URL}/assessments/{patient_id}/{order_num}/files",
                timeout=30
            )
            response.raise_for_status()
            files_data = response.json()
            df = pd.DataFrame(files_data)
        except Exception as e:
            logger.error(f"파일 정보 조회 실패: {e}")
            df = pd.DataFrame(file_metadata_list)
        
        logger.info(f"[COMPLETE] ZIP 업로드 완료: {patient_id} - 회차 {order_num}")
        return str(order_num), df
        
    except Exception as e:
        logger.error(f"[ERROR] ZIP 업로드 실패: {str(e)}")
        st.error(f"업로드 중 오류 발생: {str(e)}")
        return None, None
    finally:
        # 임시 폴더 정리
        temp_path = os.path.join(base_path, extract_path)
        if os.path.exists(temp_path):
            try:
                shutil.rmtree(temp_path)
                logger.info("임시 폴더 정리 완료")
            except Exception as e:
                logger.warning(f"임시 폴더 정리 실패: {e}")

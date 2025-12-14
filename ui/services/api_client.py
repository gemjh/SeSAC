import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")

class APIClient:
    """API 클라이언트 클래스"""
    
    @staticmethod
    def get_patients():
        """환자 목록 조회"""
        response = requests.get(f"{API_BASE_URL}/patients")
        response.raise_for_status()
        return response.json()
    
    @staticmethod
    def get_patient(patient_id: str):
        """특정 환자 조회"""
        response = requests.get(f"{API_BASE_URL}/patients/{patient_id}")
        response.raise_for_status()
        return response.json()
    
    @staticmethod
    def get_assessments(patient_id: str, assess_type: str = None):
        """검사 목록 조회"""
        params = {"assess_type": assess_type} if assess_type else {}
        response = requests.get(
            f"{API_BASE_URL}/assessments/{patient_id}",
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    @staticmethod
    def get_assessment_scores(patient_id: str, order_num: int, assess_type: str = None):
        """검사 점수 조회"""
        params = {"assess_type": assess_type} if assess_type else {}
        response = requests.get(
            f"{API_BASE_URL}/assessments/{patient_id}/{order_num}/scores",
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    @staticmethod
    def get_report(patient_id: str, order_num: int):
        """리포트 조회"""
        response = requests.get(
            f"{API_BASE_URL}/reports/{patient_id}/{order_num}"
        )
        response.raise_for_status()
        return response.json()
    
    @staticmethod
    def upload_assessment(patient_id: str, file):
        """검사 파일 업로드"""
        files = {"file": file}
        response = requests.post(
            f"{API_BASE_URL}/assessments/{patient_id}/upload",
            files=files
        )
        response.raise_for_status()
        return response.json()
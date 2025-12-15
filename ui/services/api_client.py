import requests
import os
from dotenv import load_dotenv
from typing import List, Dict, Optional
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")
logger = logging.getLogger(__name__)


class APIClient:    
    # ============================================
    # 공통 메서드
    # ============================================
    @staticmethod
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    def _make_request(method: str, endpoint: str, **kwargs):
        """
        공통 요청 메서드 (retry 로직 포함)
        
        Args:
            method: HTTP 메서드 (GET, POST, PUT, DELETE)
            endpoint: API 엔드포인트 경로
            **kwargs: requests 라이브러리 파라미터
        
        Returns:
            dict: JSON 응답
        """
        url = f"{API_BASE_URL}{endpoint}"
        timeout = kwargs.pop('timeout', 30)
        
        try:
            response = requests.request(method, url, timeout=timeout, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            logger.error(f"API 요청 타임아웃: {url}")
            raise Exception(f"서버 응답 시간 초과: {endpoint}")
        except requests.exceptions.ConnectionError:
            logger.error(f"API 연결 실패: {url}")
            raise Exception(f"서버에 연결할 수 없습니다: {endpoint}")
        except requests.exceptions.HTTPError as e:
            logger.error(f"API 요청 실패: {url}, 상태코드: {e.response.status_code}")
            raise Exception(f"API 오류 ({e.response.status_code}): {endpoint}")
        except requests.exceptions.RequestException as e:
            logger.error(f"API 요청 실패: {url}, 오류: {e}")
            raise Exception(f"API 요청 실패: {str(e)}")
    
    # ============================================
    # 환자 관련
    # ============================================
    @staticmethod
    def get_patients() -> List[Dict]:
        """환자 목록 조회"""
        return APIClient._make_request("GET", "/patients")
    
    @staticmethod
    def get_patient(patient_id: str) -> Dict:
        """특정 환자 조회"""
        return APIClient._make_request("GET", f"/patients/{patient_id}")
    
    # ============================================
    # 검사 관련
    # ============================================
    @staticmethod
    def get_assessments(patient_id: str, assess_type: Optional[str] = None) -> List[Dict]:
        """검사 목록 조회"""
        params = {"assess_type": assess_type} if assess_type else {}
        return APIClient._make_request(
            "GET", 
            f"/assessments/{patient_id}",
            params=params
        )
    
    @staticmethod
    def get_assessment_scores(
        patient_id: str, 
        order_num: int, 
        assess_type: Optional[str] = None
    ) -> List[Dict]:
        """검사 점수 조회"""
        params = {"assess_type": assess_type} if assess_type else {}
        return APIClient._make_request(
            "GET",
            f"/assessments/{patient_id}/{order_num}/scores",
            params=params
        )
    
    @staticmethod
    def get_assessment_files(patient_id: str, order_num: int) -> List[Dict]:
        """검사 파일 메타데이터 조회"""
        return APIClient._make_request(
            "GET",
            f"/assessments/{patient_id}/{order_num}/files"
        )
    
    # ============================================
    # 점수 저장 (신규 추가)
    # ============================================
    @staticmethod
    def save_scores(score_list: List[Dict]) -> bool:
        """
        점수 일괄 저장
        
        Args:
            score_list: 점수 데이터 리스트
                [
                    {
                        'patient_id': str,
                        'order_num': int,
                        'assess_type': str,
                        'question_cd': str,
                        'question_no': int,
                        'question_minor_no': int,
                        'score': float
                    },
                    ...
                ]
        
        Returns:
            bool: 저장 성공 여부
        """
        try:
            result = APIClient._make_request(
                "POST",
                "/scores/bulk",
                json={"scores": score_list}
            )
            return result.get('success', False)
        except Exception as e:
            logger.error(f"점수 저장 실패: {e}")
            return False
    
    # ============================================
    # 리포트 관련
    # ============================================
    @staticmethod
    def get_report(patient_id: str, order_num: int) -> Dict:
        """리포트 조회"""
        return APIClient._make_request(
            "GET",
            f"/reports/{patient_id}/{order_num}"
        )
    
    # ============================================
    # 파일 업로드 관련 (신규 추가)
    # ============================================
    @staticmethod
    def upload_assessment(patient_id: str, file) -> Dict:
        """
        검사 파일 업로드
        
        Args:
            patient_id: 환자 ID
            file: 업로드할 파일 객체
        
        Returns:
            dict: 업로드 결과
        """
        try:
            files = {"file": file}
            result = APIClient._make_request(
                "POST",
                f"/assessments/{patient_id}/upload",
                files=files,
                timeout=120  # 파일 업로드는 타임아웃 길게
            )
            return result
        except Exception as e:
            logger.error(f"파일 업로드 실패: {e}")
            raise
    

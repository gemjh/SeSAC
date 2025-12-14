import pandas as pd
import streamlit as st
from services.api_client import APIClient
import logging

logger = logging.getLogger(__name__)


def save_scores_to_db(fin_scores: dict, order_num: int) -> bool:
    """
    모델링 결과를 API를 통해 DB에 저장하는 함수
    
    Args:
        fin_scores: 모델링 결과 딕셔너리 {'LTN_RPT': 10, 'GUESS_END': 5, ...}
        order_num: 검사 회차 번호
    
    Returns:
        bool: 저장 성공 여부
    """
    try:
        # 세션에서 환자 정보 가져오기
        patient_id = st.session_state.patient_id
        
        # QUESTION_NO와 QUESTION_MINOR_NO 매핑 (QUESTION_CD별로)
        question_mapping = {
            'LTN_RPT': {'QUESTION_NO': 0, 'QUESTION_MINOR_NO': 0},
            'GUESS_END': {'QUESTION_NO': 0, 'QUESTION_MINOR_NO': 0}, 
            'SAY_OBJ': {'QUESTION_NO': 0, 'QUESTION_MINOR_NO': 0},
            'SAY_ANI': {'QUESTION_NO': 0, 'QUESTION_MINOR_NO': 0},
            'TALK_PIC': {'QUESTION_NO': 0, 'QUESTION_MINOR_NO': 0},
            'AH_SOUND': {'QUESTION_NO': 0, 'QUESTION_MINOR_NO': 0},
            'P_SOUND': {'QUESTION_NO': 0, 'QUESTION_MINOR_NO': 0},
            'T_SOUND': {'QUESTION_NO': 0, 'QUESTION_MINOR_NO': 0},
            'K_SOUND': {'QUESTION_NO': 0, 'QUESTION_MINOR_NO': 0},
            'PTK_SOUND': {'QUESTION_NO': 0, 'QUESTION_MINOR_NO': 0},
            'TALK_CLEAN': {'QUESTION_NO': 0, 'QUESTION_MINOR_NO': 0}
        }
        
        # 폴더 구조대로 순서 배열
        a_list = ['LTN_RPT', 'GUESS_END', 'SAY_OBJ', 'SAY_ANI', 'TALK_PIC']
        d_list = ['AH_SOUND', 'P_SOUND', 'T_SOUND', 'K_SOUND', 'PTK_SOUND', 'TALK_CLEAN']
        
        # 빠른 조회용 매핑
        assess_lookup = {**{k: 'CLAP_A' for k in a_list},
                        **{k: 'CLAP_D' for k in d_list}}
        
        # API 전송용 데이터 준비
        score_list = []
        for question_cd, score in fin_scores.items():
            if question_cd in question_mapping:
                try:
                    assess_type = assess_lookup.get(question_cd)
                    if assess_type not in ['CLAP_A', 'CLAP_D']:
                        raise ValueError(
                            f"잘못된 ASSESS_TYPE: '{assess_type}'. "
                            f"question_cd='{question_cd}'는 등록되어 있지 않습니다. "
                            f"허용되는 값은 CLAP_A, CLAP_D 입니다."
                        )
                except ValueError as e:
                    logger.error(f"[DB 저장 중 에러] {e}")
                    raise
                
                score_list.append({
                    'patient_id': patient_id,
                    'order_num': order_num,
                    'assess_type': assess_type,
                    'question_cd': question_cd,
                    'question_no': question_mapping[question_cd]['QUESTION_NO'],
                    'question_minor_no': question_mapping[question_cd]['QUESTION_MINOR_NO'],
                    'score': score
                })
        
        # ============================================
        # 핵심 변경: DB 직접 접근 → API 호출
        # ============================================
        result = APIClient.save_scores(score_list)
        
        if result:
            logger.info(f"점수 저장 완료: {patient_id} - 회차 {order_num} ({len(score_list)}건)")
            return True
        else:
            logger.error(f"점수 저장 실패: {patient_id}")
            return False
        
    except Exception as e:
        logger.error(f"점수 저장 중 오류 발생: {e}")
        st.error(f"점수 저장 실패: {str(e)}")
        return False


def get_reports(patient_id: str, test_type: str = None) -> pd.DataFrame:
    """
    리포트 조회 - API 버전
    
    Args:
        patient_id: 환자 ID
        test_type: 검사 타입 필터 (None이면 전체)
    
    Returns:
        DataFrame: 검사 목록
    """
    try:
        # ============================================
        # 핵심 변경: DB 직접 조회 → API 호출
        # ============================================
        assessments = APIClient.get_assessments(patient_id, test_type)
        
        if not assessments:
            logger.warning(f"검사 기록이 없습니다: {patient_id}")
            return pd.DataFrame()
        
        df = pd.DataFrame(assessments)
        
        # 컬럼명 확인 및 정렬
        expected_cols = [
            'order_num', 'patient_id', 'patient_name', 'age', 'sex',
            'assess_type', 'main_path', 'assess_date', 'request_org', 'assess_person'
        ]
        
        # 컬럼이 모두 있는지 확인
        if not all(col in df.columns for col in expected_cols):
            logger.warning(f"일부 컬럼이 누락되었습니다: {df.columns.tolist()}")
        
        return df
        
    except Exception as e:
        logger.error(f"리포트 조회 중 오류 발생: {e}")
        return pd.DataFrame()


def get_patient_info(patient_id: str) -> dict:
    """
    환자 정보 조회 - API 버전
    
    Args:
        patient_id: 환자 ID
    
    Returns:
        dict: 환자 정보
    """
    try:
        patient_info = APIClient.get_patient(patient_id)
        return patient_info
    except Exception as e:
        logger.error(f"환자 정보 조회 중 오류 발생: {e}")
        st.error(f"환자 정보 조회 실패: {str(e)}")
        return {}


def get_assessment_scores(patient_id: str, order_num: int, assess_type: str = None) -> pd.DataFrame:
    """
    특정 검사의 점수 조회 - API 버전
    
    Args:
        patient_id: 환자 ID
        order_num: 검사 회차
        assess_type: 검사 타입 (선택)
    
    Returns:
        DataFrame: 점수 데이터
    """
    try:
        scores = APIClient.get_assessment_scores(patient_id, order_num, assess_type)
        
        if not scores:
            logger.warning(f"점수가 없습니다: {patient_id} - 회차 {order_num}")
            return pd.DataFrame()
        
        df = pd.DataFrame(scores)
        return df
        
    except Exception as e:
        logger.error(f"점수 조회 중 오류 발생: {e}")
        st.error(f"점수 조회 실패: {str(e)}")
        return pd.DataFrame()


# ============================================
# 하위 호환성: 기존 함수명 유지 (deprecated)
# ============================================
def get_reports_local(patient_id: str, test_type: str = None) -> pd.DataFrame:
    """
    DEPRECATED: get_reports() 사용을 권장합니다.
    로컬 DB 접근 방식은 더 이상 지원되지 않습니다.
    """
    logger.warning("get_reports_local()은 deprecated 되었습니다. get_reports()를 사용하세요.")
    return get_reports(patient_id, test_type)


def get_db_modules():
    """
    DEPRECATED: DB 직접 접근은 더 이상 지원되지 않습니다.
    API를 통한 접근만 가능합니다.
    """
    logger.error("get_db_modules()는 더 이상 지원되지 않습니다. API를 사용하세요.")
    raise NotImplementedError("DB 직접 접근은 지원되지 않습니다. API를 사용하세요.")
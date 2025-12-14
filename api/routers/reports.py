from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from database import get_db

router = APIRouter()

@router.get("/{patient_id}/{order_num}")
def get_report(
    patient_id: str,
    order_num: int,
    db: Session = Depends(get_db)
):
    """검사 리포트 전체 데이터 조회"""
    try:
        # 환자 기본 정보
        patient_query = text("""
            SELECT lst.*, COALESCE(p.NAME, '정보없음') as PATIENT_NAME
            FROM assess_lst lst
            LEFT JOIN patient_info p ON lst.PATIENT_ID = p.PATIENT_ID
            WHERE lst.PATIENT_ID = :patient_id AND lst.ORDER_NUM = :order_num
        """)
        
        patient_cursor = db.execute(
            patient_query, 
            {"patient_id": patient_id, "order_num": order_num}
        )
        patient_info = patient_cursor.fetchone()
        
        if not patient_info:
            raise HTTPException(status_code=404, detail="검사 기록을 찾을 수 없습니다")
        
        # 점수 정보
        scores_query = text("""
            SELECT QUESTION_CD, SCORE 
            FROM assess_score_t
            WHERE PATIENT_ID = :patient_id AND ORDER_NUM = :order_num
        """)
        
        scores_cursor = db.execute(
            scores_query, 
            {"patient_id": patient_id, "order_num": order_num}
        )
        scores = scores_cursor.fetchall()
        
        return {
            "patient_info": {
                "patient_id": patient_info[0],
                "order_num": patient_info[1],
                "patient_name": patient_info[-1],
                "age": patient_info[5],
                "assess_date": str(patient_info[3]) if patient_info[3] else None,
                "request_org": patient_info[2],
                "assess_person": patient_info[4]
            },
            "scores": {row[0]: float(row[1]) if row[1] else 0 for row in scores}
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"리포트 조회 실패: {str(e)}")
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
            SELECT 
                lst.PATIENT_ID,
                lst.ORDER_NUM,
                COALESCE(p.NAME, '정보없음') AS PATIENT_NAME,
                p.SEX AS PATIENT_SEX,
                lst.REQUEST_ORG,
                lst.ASSESS_DATE,
                lst.ASSESS_PERSON,
                lst.AGE,
                lst.EDU,
                lst.POST_STROKE_DATE,
                lst.DIAGNOSIS,
                lst.DIAGNOSIS_ETC,
                lst.STROKE_TYPE,
                lst.LESION_LOCATION,
                lst.HEMIPLEGIA,
                lst.HEMINEGLECT,
                lst.VISUAL_FIELD_DEFECT
            FROM assess_lst lst
            LEFT JOIN patient_info p ON lst.PATIENT_ID = p.PATIENT_ID
            WHERE lst.PATIENT_ID = :patient_id AND lst.ORDER_NUM = :order_num
        """)
        
        patient_cursor = db.execute(
            patient_query, 
            {"patient_id": patient_id, "order_num": order_num}
        )
        patient_info = patient_cursor.mappings().fetchone()
        
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
                "patient_id": patient_info["PATIENT_ID"],
                "order_num": patient_info["ORDER_NUM"],
                "patient_name": patient_info["PATIENT_NAME"],
                "sex": patient_info["PATIENT_SEX"],
                "age": patient_info["AGE"],
                "edu": patient_info["EDU"],
                "request_org": patient_info["REQUEST_ORG"],
                "assess_date": str(patient_info["ASSESS_DATE"]) if patient_info["ASSESS_DATE"] else None,
                "assess_person": patient_info["ASSESS_PERSON"],
                "post_stroke_date": str(patient_info["POST_STROKE_DATE"]) if patient_info["POST_STROKE_DATE"] else None,
                "diagnosis": patient_info["DIAGNOSIS"],
                "diagnosis_etc": patient_info["DIAGNOSIS_ETC"],
                "stroke_type": patient_info["STROKE_TYPE"],
                "lesion_location": patient_info["LESION_LOCATION"],
                "hemiplegia": patient_info["HEMIPLEGIA"],
                "hemineglect": patient_info["HEMINEGLECT"],
                "visual_field_defect": patient_info["VISUAL_FIELD_DEFECT"]
            },
            "scores": {row[0]: float(row[1]) if row[1] else 0 for row in scores}
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"리포트 조회 실패: {str(e)}")

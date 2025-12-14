from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from database import get_db

router = APIRouter()

@router.get("/")
def get_patients(db: Session = Depends(get_db)):
    """전체 환자 목록 조회"""
    try:
        query = text("""
            SELECT DISTINCT p.PATIENT_ID, 
                   COALESCE(pi.NAME, '정보없음') as PATIENT_NAME, 
                   p.AGE, 
                   COALESCE(pi.SEX, '0') as SEX
            FROM assess_lst p
            LEFT JOIN patient_info pi ON p.PATIENT_ID = pi.PATIENT_ID
            ORDER BY p.PATIENT_ID
        """)
        
        cursor = db.execute(query)
        result = cursor.fetchall()
        
        return [
            {
                "patient_id": row[0],
                "patient_name": row[1],
                "age": row[2],
                "sex": row[3]
            }
            for row in result
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"환자 목록 조회 실패: {str(e)}")

@router.get("/{patient_id}")
def get_patient(patient_id: str, db: Session = Depends(get_db)):
    """특정 환자 정보 조회"""
    try:
        query = text("""
            SELECT p.PATIENT_ID, 
                   COALESCE(pi.NAME, '정보없음') as PATIENT_NAME, 
                   p.AGE, 
                   COALESCE(pi.SEX, '0') as SEX
            FROM assess_lst p
            LEFT JOIN patient_info pi ON p.PATIENT_ID = pi.PATIENT_ID
            WHERE p.PATIENT_ID = :patient_id
            LIMIT 1
        """)
        
        cursor = db.execute(query, {"patient_id": patient_id})
        result = cursor.fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail="환자를 찾을 수 없습니다")
        
        return {
            "patient_id": result[0],
            "patient_name": result[1],
            "age": result[2],
            "sex": result[3]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"환자 정보 조회 실패: {str(e)}")
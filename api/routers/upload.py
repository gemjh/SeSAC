from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from pydantic import BaseModel
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from database import get_db

router = APIRouter()


# ============================================
# Request Models
# ============================================
class PatientAssessmentInfo(BaseModel):
    patient_id: str
    order_num: int
    request_org: Optional[str] = None
    assess_date: Optional[str] = None
    assess_person: Optional[str] = None
    age: Optional[int] = None
    sex: Optional[str] = None
    edu: Optional[int] = None
    excluded: str = '0'
    post_stroke_date: Optional[str] = None
    diagnosis: Optional[str] = None
    diagnosis_etc: Optional[str] = None
    stroke_type: Optional[str] = None
    lesion_location: Optional[str] = None
    hemiplegia: Optional[str] = None
    hemineglect: Optional[str] = None
    visual_field_defect: Optional[str] = None


class FileMetadata(BaseModel):
    patient_id: str
    order_num: int
    assess_type: str
    question_cd: str
    question_no: int
    question_minor_no: int
    main_path: str
    sub_path: str
    file_name: str
    duration: float
    rate: int


class FileMetadataBulk(BaseModel):
    files: List[FileMetadata]


class ScoreData(BaseModel):
    patient_id: str
    order_num: int
    assess_type: str
    question_cd: str
    question_no: int
    question_minor_no: int
    score: float


class ScoreBulk(BaseModel):
    scores: List[ScoreData]


# ============================================
# 헬퍼 함수
# ============================================
def to_sql_value(val):
    """Python 값을 SQL 문자열로 변환"""
    if val is None:
        return "NULL"
    elif isinstance(val, str):
        # SQL Injection 방지를 위한 escape
        escaped = val.replace("'", "''")
        return f"'{escaped}'"
    else:
        return str(val)


# ============================================
# Endpoints
# ============================================

@router.get("/patients/{patient_id}/order")
def get_order_num(patient_id: str, db: Session = Depends(get_db)):
    """환자의 수행회차 조회"""
    try:
        query = text("""
            SELECT IFNULL(MAX(order_num) + 1, 1) 
            FROM assess_lst 
            WHERE PATIENT_ID = :patient_id
        """)
        result = db.execute(query, {"patient_id": patient_id}).fetchone()
        return {"order_num": result[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"수행회차 조회 실패: {str(e)}")


@router.post("/assessments/patient-info")
def save_patient_assessment(data: PatientAssessmentInfo, db: Session = Depends(get_db)):
    """환자 검사 정보 저장"""
    try:
        # SQL 파라미터 준비
        params = {
            'patient_id': data.patient_id,
            'order_num': data.order_num,
            'request_org': data.request_org,
            'assess_date': data.assess_date,
            'assess_person': data.assess_person,
            'age': data.age,
            'edu': data.edu,
            'excluded': data.excluded,
            'post_stroke_date': data.post_stroke_date,
            'diagnosis': data.diagnosis,
            'diagnosis_etc': data.diagnosis_etc,
            'stroke_type': data.stroke_type,
            'lesion_location': data.lesion_location,
            'hemiplegia': data.hemiplegia,
            'hemineglect': data.hemineglect,
            'visual_field_defect': data.visual_field_defect
        }
        
        query = text("""
            INSERT INTO assess_lst (
                PATIENT_ID, ORDER_NUM, REQUEST_ORG, ASSESS_DATE, ASSESS_PERSON,
                AGE, EDU, EXCLUDED, POST_STROKE_DATE, DIAGNOSIS, DIAGNOSIS_ETC,
                STROKE_TYPE, LESION_LOCATION, HEMIPLEGIA, HEMINEGLECT, VISUAL_FIELD_DEFECT
            ) VALUES (
                :patient_id, :order_num, :request_org, :assess_date, :assess_person,
                :age, :edu, :excluded, :post_stroke_date, :diagnosis, :diagnosis_etc,
                :stroke_type, :lesion_location, :hemiplegia, :hemineglect, :visual_field_defect
            )
        """)
        
        db.execute(query, params)
        db.commit()
        
        return {
            "success": True,
            "message": f"환자 검사 정보 저장 완료: {data.patient_id}",
            "patient_id": data.patient_id,
            "order_num": data.order_num
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"환자 검사 정보 저장 실패: {str(e)}")


@router.post("/assessments/files/bulk")
def save_file_metadata_bulk(data: FileMetadataBulk, db: Session = Depends(get_db)):
    """파일 메타데이터 일괄 저장"""
    try:
        if not data.files:
            raise HTTPException(status_code=400, detail="저장할 파일 정보가 없습니다")
        
        # 일괄 INSERT를 위한 values 리스트 생성
        values = []
        for file in data.files:
            values.append(f"""(
                '{file.patient_id}', {file.order_num}, '{file.assess_type}', 
                '{file.question_cd}', {file.question_no}, {file.question_minor_no},
                '{file.main_path}', '{file.sub_path}', '{file.file_name}',
                {file.duration}, {file.rate}
            )""")
        
        query = text(f"""
            INSERT INTO assess_file_lst (
                PATIENT_ID, ORDER_NUM, ASSESS_TYPE, QUESTION_CD, 
                QUESTION_NO, QUESTION_MINOR_NO, MAIN_PATH, SUB_PATH, 
                FILE_NAME, DURATION, RATE
            ) VALUES {','.join(values)}
        """)
        
        db.execute(query)
        db.commit()
        
        return {
            "success": True,
            "message": f"파일 메타데이터 {len(data.files)}건 저장 완료",
            "count": len(data.files)
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"파일 메타데이터 저장 실패: {str(e)}")


@router.post("/assessments/{patient_id}/{order_num}/deduplicate")
def handle_duplicate_files(patient_id: str, order_num: int, db: Session = Depends(get_db)):
    """중복 파일 처리 - QUESTION_MINOR_NO가 작은 것을 USE_YN='N'으로 설정"""
    try:
        # Step 1: 중복 조건 확인
        check_query = text("""
            SELECT PATIENT_ID, ORDER_NUM, ASSESS_TYPE, QUESTION_CD, QUESTION_NO, COUNT(*) as cnt
            FROM assess_file_lst
            WHERE PATIENT_ID = :patient_id 
              AND ORDER_NUM = :order_num 
              AND USE_YN = 'Y'
            GROUP BY PATIENT_ID, ORDER_NUM, ASSESS_TYPE, QUESTION_CD, QUESTION_NO
            HAVING COUNT(*) >= 2
        """)
        
        duplicates = db.execute(check_query, {
            "patient_id": patient_id,
            "order_num": order_num
        }).fetchall()
        
        if not duplicates:
            return {
                "success": True,
                "message": "중복 파일 없음",
                "deactivated_count": 0
            }
        
        # Step 2: 중복된 레코드 중 QUESTION_MINOR_NO가 작은 것만 USE_YN='N'으로 업데이트
        update_query = text("""
            WITH ranked_records AS (
                SELECT *,
                    ROW_NUMBER() OVER (
                        PARTITION BY PATIENT_ID, ORDER_NUM, ASSESS_TYPE, QUESTION_CD, QUESTION_NO
                        ORDER BY QUESTION_MINOR_NO ASC
                    ) AS rn
                FROM assess_file_lst
                WHERE PATIENT_ID = :patient_id 
                  AND ORDER_NUM = :order_num 
                  AND USE_YN = 'Y'
                  AND (PATIENT_ID, ORDER_NUM, ASSESS_TYPE, QUESTION_CD, QUESTION_NO) IN (
                    SELECT PATIENT_ID, ORDER_NUM, ASSESS_TYPE, QUESTION_CD, QUESTION_NO
                    FROM assess_file_lst
                    WHERE PATIENT_ID = :patient_id 
                      AND ORDER_NUM = :order_num 
                      AND USE_YN = 'Y'
                    GROUP BY PATIENT_ID, ORDER_NUM, ASSESS_TYPE, QUESTION_CD, QUESTION_NO
                    HAVING COUNT(*) >= 2
                )
            )
            UPDATE assess_file_lst AS a
            JOIN ranked_records AS r
              ON a.PATIENT_ID = r.PATIENT_ID
             AND a.ORDER_NUM = r.ORDER_NUM
             AND a.ASSESS_TYPE = r.ASSESS_TYPE
             AND a.QUESTION_CD = r.QUESTION_CD
             AND a.QUESTION_NO = r.QUESTION_NO
             AND a.QUESTION_MINOR_NO = r.QUESTION_MINOR_NO
            SET a.USE_YN = 'N'
            WHERE r.rn = 1
        """)
        
        result = db.execute(update_query, {
            "patient_id": patient_id,
            "order_num": order_num
        })
        db.commit()
        
        return {
            "success": True,
            "message": f"중복 파일 {len(duplicates)}건 처리 완료",
            "duplicate_groups": len(duplicates),
            "deactivated_count": result.rowcount
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"중복 파일 처리 실패: {str(e)}")


@router.post("/assessments/{patient_id}/{order_num}/init-scores")
def initialize_scores(patient_id: str, order_num: int, db: Session = Depends(get_db)):
    """점수 테이블 초기화 - assess_file_lst의 데이터를 assess_score에 복사"""
    try:
        query = text("""
            INSERT INTO assess_score (
                PATIENT_ID, ORDER_NUM, ASSESS_TYPE, QUESTION_CD, 
                QUESTION_NO, QUESTION_MINOR_NO, USE_YN
            )
            SELECT 
                PATIENT_ID, ORDER_NUM, ASSESS_TYPE, QUESTION_CD,
                QUESTION_NO, QUESTION_MINOR_NO, USE_YN
            FROM assess_file_lst
            WHERE PATIENT_ID = :patient_id 
              AND ORDER_NUM = :order_num
        """)
        
        result = db.execute(query, {
            "patient_id": patient_id,
            "order_num": order_num
        })
        db.commit()
        
        return {
            "success": True,
            "message": f"점수 테이블 초기화 완료: {result.rowcount}건",
            "initialized_count": result.rowcount
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"점수 테이블 초기화 실패: {str(e)}")


@router.get("/assessments/{patient_id}/{order_num}/files")
def get_assessment_files(patient_id: str, order_num: int, db: Session = Depends(get_db)):
    """특정 검사의 파일 목록 조회"""
    try:
        query = text("""
            SELECT 
                A.PATIENT_ID, A.ORDER_NUM, A.ASSESS_TYPE, A.QUESTION_CD,
                A.QUESTION_NO, A.MAIN_PATH, A.SUB_PATH, A.FILE_NAME
            FROM assess_file_lst A
            INNER JOIN code_mast C 
              ON C.CODE_TYPE = 'ASSESS_TYPE' 
             AND A.ASSESS_TYPE = C.MAST_CD 
             AND A.QUESTION_CD = C.SUB_CD
            WHERE A.PATIENT_ID = :patient_id 
              AND A.ORDER_NUM = :order_num 
              AND A.USE_YN = 'Y'
            ORDER BY A.ASSESS_TYPE, C.ORDER_NUM, A.QUESTION_NO
        """)
        
        result = db.execute(query, {
            "patient_id": patient_id,
            "order_num": order_num
        }).fetchall()
        
        return [
            {
                "PATIENT_ID": row[0],
                "ORDER_NUM": row[1],
                "ASSESS_TYPE": row[2],
                "QUESTION_CD": row[3],
                "QUESTION_NO": row[4],
                "MAIN_PATH": row[5],
                "SUB_PATH": row[6],
                "FILE_NAME": row[7]
            }
            for row in result
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"파일 목록 조회 실패: {str(e)}")


@router.post("/scores/bulk")
def save_scores_bulk(data: ScoreBulk, db: Session = Depends(get_db)):
    """점수 일괄 저장"""
    try:
        if not data.scores:
            raise HTTPException(status_code=400, detail="저장할 점수 정보가 없습니다")
        
        # 기존 점수 업데이트 (UPSERT 방식)
        for score in data.scores:
            # 먼저 기존 데이터 확인
            check_query = text("""
                SELECT COUNT(*) 
                FROM assess_score
                WHERE PATIENT_ID = :patient_id
                  AND ORDER_NUM = :order_num
                  AND QUESTION_CD = :question_cd
            """)
            
            exists = db.execute(check_query, {
                "patient_id": score.patient_id,
                "order_num": score.order_num,
                "question_cd": score.question_cd
            }).scalar()
            
            if exists:
                # 업데이트
                update_query = text("""
                    UPDATE assess_score
                    SET SCORE = :score,
                        ASSESS_TYPE = :assess_type
                    WHERE PATIENT_ID = :patient_id
                      AND ORDER_NUM = :order_num
                      AND QUESTION_CD = :question_cd
                """)
                db.execute(update_query, {
                    "score": score.score,
                    "assess_type": score.assess_type,
                    "patient_id": score.patient_id,
                    "order_num": score.order_num,
                    "question_cd": score.question_cd
                })
            else:
                # 삽입
                insert_query = text("""
                    INSERT INTO assess_score (
                        PATIENT_ID, ORDER_NUM, ASSESS_TYPE, QUESTION_CD,
                        QUESTION_NO, QUESTION_MINOR_NO, SCORE
                    ) VALUES (
                        :patient_id, :order_num, :assess_type, :question_cd,
                        :question_no, :question_minor_no, :score
                    )
                """)
                db.execute(insert_query, {
                    "patient_id": score.patient_id,
                    "order_num": score.order_num,
                    "assess_type": score.assess_type,
                    "question_cd": score.question_cd,
                    "question_no": score.question_no,
                    "question_minor_no": score.question_minor_no,
                    "score": score.score
                })
        
        db.commit()
        
        return {
            "success": True,
            "message": f"점수 {len(data.scores)}건 저장 완료",
            "count": len(data.scores)
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"점수 저장 실패: {str(e)}")

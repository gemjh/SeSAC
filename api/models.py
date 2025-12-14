from pydantic import BaseModel
from typing import Optional
from datetime import date

# 환자 정보 모델
class PatientInfo(BaseModel):
    patient_id: str
    patient_name: Optional[str] = None
    age: Optional[int] = None
    sex: Optional[str] = None
    
    class Config:
        from_attributes = True

# 검사 결과 모델
class AssessmentResult(BaseModel):
    patient_id: str
    order_num: int
    assess_type: str
    question_cd: str
    score: float
    
    class Config:
        from_attributes = True

# 검사 목록 응답 모델
class AssessmentListResponse(BaseModel):
    order_num: int
    patient_id: str
    patient_name: Optional[str]
    age: Optional[int]
    sex: Optional[str]
    assess_type: str
    assess_date: Optional[date]
    request_org: Optional[str]
    assess_person: Optional[str]
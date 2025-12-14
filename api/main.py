from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from contextlib import asynccontextmanager
import models
from database import get_db
from routers import patients, assessments, reports
from routers import upload 


# ============================================
# Lifespan 이벤트 (startup/shutdown 대체)
# ============================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명주기 관리"""
    # Startup
    print("=" * 50)
    print("CLAP API Server Starting...")
    print("=" * 50)
    print("✅ Routers registered:")
    for route in app.routes:
        if hasattr(route, "methods"):
            print(f"  {list(route.methods)[0]:6s} {route.path}")
    print("=" * 50)
    
    yield  # 애플리케이션 실행


# ============================================
# FastAPI 앱 생성
# ============================================
app = FastAPI(
    title="CLAP API",
    version="1.0.0",
    description="CLAP 검사 시스템 API",
    lifespan=lifespan
)

# CORS 설정 (Streamlit에서 접근 가능하도록)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 구체적인 도메인 지정 권장
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# 라우터 등록
# ============================================
# 기존 라우터
app.include_router(patients.router, prefix="/api/v1/patients", tags=["Patients"])
app.include_router(assessments.router, prefix="/api/v1/assessments", tags=["Assessments"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["Reports"])

# 새로운 라우터 추가 - 업로드 및 점수 관련
app.include_router(upload.router, prefix="/api/v1", tags=["Upload & Scores"])


# ============================================
# main
# ============================================
@app.get("/")
def read_root():
    """API 루트 엔드포인트"""
    return {
        "message": "CLAP API Server",
        "version": "1.0.0",
        "status": "running"
    }

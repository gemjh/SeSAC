from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import models
from database import get_db
from routers import patients, assessments, reports

app = FastAPI(
    title="CLAP API",
    version="1.0.0"
)

# CORS 설정 (Streamlit에서 접근 가능하도록)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(patients.router, prefix="/api/v1/patients", tags=["Patients"])
app.include_router(assessments.router, prefix="/api/v1/assessments", tags=["Assessments"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["Reports"])

@app.get("/")
def read_root():
    return {"message": "CLAP API Server", "version": "1.0.0"}

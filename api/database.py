from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from pathlib import Path

# .env 파일 로드
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# DB URL 구성
DATABASE_URL = f"mysql+pymysql://{os.getenv('db_username')}:{os.getenv('db_password')}@{os.getenv('db_host')}:{os.getenv('db_port', 3306)}/{os.getenv('db_database')}"

print(f"[DEBUG] Database URL: mysql+pymysql://{os.getenv('db_username')}:***@{os.getenv('db_host')}:{os.getenv('db_port')}/{os.getenv('db_database')}")

engine = create_engine(
    DATABASE_URL, 
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False  # SQL 로깅 끄기
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# DB 세션 의존성
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
# ===================================================================
# Streamlit MySQL 연결 방법들
# ===================================================================

# 1. 필요한 패키지 설치
# pip install streamlit mysql-connector-python pymysql sqlalchemy

import streamlit as st
import mysql.connector
import pandas as pd
import os
from datetime import datetime

# ===================================================================
# 방법 1: mysql-connector-python 사용 (추천)
# ===================================================================

@st.cache_resource
def init_mysql_connection():
    """MySQL 연결 초기화 (캐시됨)"""
    try:
        connection = mysql.connector.connect(
            host='localhost',          # 또는 실제 서버 IP
            user='mysql',      # MySQL 사용자명
            password='1234',  # MySQL 비밀번호
            database='patient_management',  # 데이터베이스명
            port=3306,                # 포트 (기본값: 3306)
            charset='utf8mb4',
            autocommit=True
        )
        return connection
    except mysql.connector.Error as e:
        st.error(f"MySQL 연결 실패: {e}")
        return None

def execute_query(query, params=None):
    """쿼리 실행 함수"""
    conn = init_mysql_connection()
    if conn is None:
        return None
    
    try:
        cursor = conn.cursor(dictionary=True)  # 딕셔너리 형태로 결과 반환
        cursor.execute(query, params)
        
        if query.strip().upper().startswith('SELECT'):
            result = cursor.fetchall()
            return pd.DataFrame(result)
        else:
            conn.commit()
            return cursor.rowcount
            
    except mysql.connector.Error as e:
        st.error(f"쿼리 실행 오류: {e}")
        return None
    finally:
        cursor.close()


# ===================================================================
# 실제 사용 예제 - Streamlit 앱
# ===================================================================

def main_app():
    st.title("🗄️ Streamlit MySQL 연동 예제")
    
    # 데이터베이스 연결 테스트
    st.header("📡 데이터베이스 연결 테스트")
    
    if st.button("연결 테스트"):
        conn = init_mysql_connection()
        
        if conn:
            st.success("✅ 데이터베이스 연결 성공!")
        else:
            st.error("❌ 데이터베이스 연결 실패!")
    
    # 쿼리 실행 섹션
    st.header("📊 쿼리 실행")
    
    # 미리 정의된 쿼리들
    predefined_queries = {
        "전체 환자 조회": "SELECT * FROM patient_summary LIMIT 10",
        "환자 수 조회": "SELECT COUNT(*) as patient_count FROM patient_summary",
    }
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("미리 정의된 쿼리")
        selected_query = st.selectbox("쿼리 선택", list(predefined_queries.keys()))
        
        if st.button("쿼리 실행"):
            query = predefined_queries[selected_query]
            result = execute_query(query)

            if result is not None:
                st.success("쿼리 실행 완료!")
                st.dataframe(result)
    
    with col2:
        st.subheader("사용자 정의 쿼리")
        custom_query = st.text_area(
            "SQL 쿼리 입력",
            placeholder="SELECT * FROM patients WHERE condition = 'value'"
        )
        
        if st.button("사용자 쿼리 실행"):
            if custom_query.strip():
                result = execute_query(custom_query)

                if result is not None:
                    st.success("쿼리 실행 완료!")
                    st.dataframe(result)
            else:
                st.warning("쿼리를 입력해주세요.")
 

# ===================================================================
# 환경 설정 가이드
# ===================================================================

def show_setup_guide():
    st.title("🔧 MySQL 연결 설정 가이드")
    
    st.markdown("""
    ## 1. 필요한 패키지 설치
    ```bash
    pip install streamlit mysql-connector-python  
    ```
    
    ## 2. MySQL 서버 설정
    - MySQL 서버가 실행 중인지 확인
    - 데이터베이스와 테이블 생성
    - 사용자 권한 설정
    
    ## 3. 환경변수 설정 (.env 파일)
    ```
    DB_HOST=localhost
    DB_USER=your_username
    DB_PASSWORD=your_password
    DB_NAME=your_database
    DB_PORT=3306
    ```
    
    ## 4. 테이블 생성 예제 SQL
    ```sql
    CREATE DATABASE patient_management;
    USE patient_management;
    
    CREATE TABLE patients (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        age INT,
        disease VARCHAR(200),
        created_date DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    
    ## 5. 보안 고려사항
    - 환경변수로 DB 정보 관리
    - SQL 인젝션 방지 (매개변수 사용)
    - 연결 풀링 사용
    - HTTPS 사용 (프로덕션)
    """)

# ===================================================================
# 메인 실행
# ===================================================================

if __name__ == "__main__":
    tab1, tab2 = st.tabs(["MySQL 연동 예제", "설정 가이드"])
    
    with tab1:
        main_app()
    
    with tab2:
        show_setup_guide()
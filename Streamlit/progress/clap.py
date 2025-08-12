import streamlit as st
import oracledb
import pandas as pd
from datetime import datetime, date
import hashlib
# import plotly.express as px
# import plotly.graph_objects as go

activate_conda_environment()

# 페이지 설정
st.set_page_config(
    page_title="CLAP",
    page_icon="👋",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* 전체 앱 배경 */
    .stApp {
        background: linear-gradient(135deg, #1e90ff, #00bfff);  
        color: white;
    }
    
    /* 사이드바 스타일 - 파란색 그라데이션 */
    .stSidebar > div:first-child {
        background: linear-gradient(135deg, #1e90ff, #00bfff) !important;
        width: 200px !important;
    }
    
    .css-1d391kg, .css-1lcbmhc, .css-17eq0hr, .css-1cypcdb {
        background: linear-gradient(135deg, #1e90ff, #00bfff) !important;
    }
    
    /* 사이드바 모든 요소 */
    section[data-testid="stSidebar"] {
        background: linear-gradient(135deg, #1e90ff, #00bfff) !important;
        
    }
    
    section[data-testid="stSidebar"] > div {
        display: flex !important;
        flex-direction: column !important;
        height: 100% !important;
        position: relative !important;
    }

    /* 메인 컨텐츠 영역 */
    .main .block-container {
        padding: 20px;
        max-width: none;
    }
    
    /* 사이드바 로고 */
    .sidebar-logo {
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 40px;
        color: white;
        padding: 20px 0;
    }
    
    /* 사이드바 메뉴 */
    .sidebar-menu {
        margin-bottom: 20px;
    }

    /* 사이드바 푸터 */
    .sidebar-footer {
        margin-top: auto !important;
        margin-bottom: 10px;
    }

    /* 메뉴 */
    .menu-item {
        padding: 15px 10px;
        margin-bottom: 5px;
        border-radius: 8px;
        cursor: pointer;
        transition: background 0.2s;
        color: white;
        font-size: 16px;
    }
    
    .menu-item:hover {
        background: rgba(255, 255, 255, 0.1);
    }
    
    .menu-item.active {
        background: rgba(255, 255, 255, 0.2);
        font-weight: bold;
    }
    
    /* 환자 정보 */
    .patient-info {
        background: rgba(0, 0, 0, 0.1);
        padding: 20px;
        border-radius: 8px;
        border-top: 1px solid rgba(255, 255, 255, 0.2);
        color: white;
        margin-bottom: 10px;
    }
        
    .patient-name {
        font-size: 16px;
        font-weight: bold;
        margin-bottom: 5px;
    }
    
    .patient-id {
        font-size: 14px;
        opacity: 0.8;
        margin-bottom: 5px;
    }
    
    .patient-gender {
        font-size: 14px;
        opacity: 0.8;
        margin-bottom: 15px;
    }
    
    /* 헤더 */
    .main-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 30px;
        color: white;
    }
    header[data-testid="stHeader"]{
        background: inherit;
    }
    
    /* 탭 스타일 */
    .tab-container {
        display: flex;
        gap: 10px;
    }
    
    .tab-button {
        padding: 10px 20px;
        border-radius: 25px;
        cursor: pointer;
        font-size: 14px;
        border: none;
        transition: all 0.2s;
    }
    
    .tab-inactive {
        background: rgba(255, 255, 255, 0.2);
        color: white;
    }
    
    .tab-active {
        background: white;
        color: #1e90ff;
        font-weight: bold;
    }
    
    /* 프린트 버튼 */
    .print-button {
        background: none;
        border: 2px solid white;
        color: white;
        padding: 8px 12px;
        border-radius: 6px;
        cursor: pointer;
        font-size: 18px;
    }
    
    /* 리포트 아이템 */
    .report-item {
        background: rgba(255, 255, 255, 0.1);
        margin-bottom: 10px;
        padding: 20px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        backdrop-filter: blur(10px);
        transition: background 0.2s;
    }
    
    .report-item:hover {
        background: rgba(255, 255, 255, 0.15);
    }
    
    .report-info {
        display: flex;
        align-items: center;
        gap: 20px;
        flex: 1;
    }
    
    .report-title {
        font-weight: bold;
        font-size: 16px;
        min-width: 80px;
        color: white;
    }
    
    .report-details {
        display: flex;
        gap: 20px;
        font-size: 14px;
        color: white;
    }
    
    .detail-item {
        display: flex;
        gap: 5px;
    }
    
    .detail-label {
        opacity: 0.8;
    }
    
    .detail-value {
        font-weight: 500;
    }
    
    .confirm-btn {
        background: rgba(255, 255, 255, 0.2);
        border: none;
        color: white;
        padding: 8px 15px;
        border-radius: 6px;
        cursor: pointer;
        font-size: 14px;
        transition: background 0.2s;
    }
    
    .confirm-btn:hover {
        background: rgba(255, 255, 255, 0.3);
    }
    
    /* Streamlit 버튼 기본 스타일 제거/수정 */
    .stButton > button {
        background: none !important;
        border: none !important;
        color: white !important;
        padding: 10px 20px !important;
        border-radius: 25px !important;
        font: inherit !important;
        cursor: pointer !important;
        font-size: 14px !important;
        transition: all 0.2s !important;
    }
    
    .stButton > button:hover {
        background: rgba(255, 255, 255, 0.2) !important;
        color: white !important;
        border: none !important;
        text-decoration: none !important;
    }
    
    .stButton > button:focus {
        background: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
    }
    
    .stButton > button:active {
        background: rgba(255, 255, 255, 0.2) !important;
        color: white !important;
        border: none !important;
    }
    
    /* Primary 버튼 - 흰색 배경 유지 */
    .stButton > button[data-testid="baseButton-primary"] {
        background: white !important;
        color: #1e90ff !important;
        font-weight: bold !important;
    }
    
    .stButton > button[data-testid="baseButton-primary"]:hover {
        background: rgba(255, 255, 255, 0.9) !important;
        color: #1e90ff !important;
    }
    
    .stButton > button[data-testid="baseButton-primary"]:focus {
        background: white !important;
        color: #1e90ff !important;
        outline: none !important;
        box-shadow: none !important;
    }
    
    .stButton > button[data-testid="baseButton-primary"]:active {
        background: rgba(255, 255, 255, 0.9) !important;
        color: #1e90ff !important;
    }
    
    /* 체크박스 스타일 */
    input[type="checkbox"] {
        width: 18px;
        height: 18px;
        accent-color: white;
    }
    
    /* 텍스트 색상 */
    .stMarkdown {
        color: white;
    }
    
    /* 상세 리포트 스타일 */
    .report-detail-container {
        background: white;
        border-radius: 12px;
        padding: 30px;
        margin: 20px 0;
        color: #333;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .report-header {
        border-bottom: 2px solid #1e90ff;
        padding-bottom: 15px;
        margin-bottom: 25px;
    }
    
    .report-title-main {
        font-size: 24px;
        font-weight: bold;
        color: #1e90ff;
        margin-bottom: 5px;
    }
    
    .report-subtitle {
        font-size: 14px;
        color: #666;
    }
    
    .info-table {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 25px;
    }
    
    .info-table td {
        padding: 8px 12px;
        border: 1px solid #ddd;
        font-size: 14px;
    }
    
    .info-table td:first-child {
        background-color: #f5f5f5;
        font-weight: bold;
        width: 120px;
    }
    
    .section-title {
        font-size: 18px;
        font-weight: bold;
        color: #1e90ff;
        margin: 25px 0 15px 0;
        padding-bottom: 5px;
        border-bottom: 1px solid #ddd;
    }
    
    .test-result-table {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 20px;
    }
    
    .test-result-table th,
    .test-result-table td {
        padding: 10px;
        border: 1px solid #ddd;
        text-align: center;
        font-size: 14px;
    }
    
    .test-result-table th {
        background-color: #f0f8ff;
        font-weight: bold;
        color: #1e90ff;
    }
    
    .normal-result {
        background-color: #e8f5e8;
        color: #2e7d32;
    }
    
    .abnormal-result {
        background-color: #ffebee;
        color: #c62828;
    }
    
    .score-badge {
        display: inline-block;
        padding: 4px 8px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: bold;
        margin: 2px;
    }
    
    .score-normal {
        background-color: #4caf50;
        color: white;
    }
    
    .score-warning {
        background-color: #ff9800;
        color: white;
    }
    
    .score-danger {
        background-color: #f44336;
        color: white;
    }
    
    /* 뒤로가기 버튼 */
    .back-button {
        background: rgba(255, 255, 255, 0.2) !important;
        border: 1px solid white !important;
        color: white !important;
        padding: 8px 16px !important;
        border-radius: 20px !important;
        font-size: 14px !important;
        margin-bottom: 20px !important;
    }
    
    .back-button:hover {
        background: rgba(255, 255, 255, 0.3) !important;
    }
</style>
""", unsafe_allow_html=True)

try:
    st.header(st.session_state.current_page)
except:
    st.header('')

# Oracle 데이터베이스 연결 함수
def get_verified_connection():
    """검증된 Oracle 연결을 반환"""
    try:
        connection = oracledb.connect(
            user="system",
            password="oracle", 
            dsn="localhost:1521/XE"
        )
        cursor = connection.cursor()
        cursor.execute("SELECT 1 FROM DUAL")
        cursor.close()
        return connection
    except oracledb.Error as e:
        st.error(f"Oracle 데이터베이스 연결 오류: {e}")
        return None

def safe_close_connection(connection):
    """연결을 안전하게 종료"""
    if connection:
        try:
            connection.close()
        except:
            pass

# Oracle 테이블 생성 함수
def create_demo_tables():
    connection = None
    try:
        connection = get_verified_connection()
        if not connection:
            return
            
        cursor = connection.cursor()
        
        # 시퀀스 생성
        sequences = [
            "CREATE SEQUENCE users_seq START WITH 1 INCREMENT BY 1 NOCACHE",
            "CREATE SEQUENCE patients_seq START WITH 1 INCREMENT BY 1 NOCACHE",
            "CREATE SEQUENCE clap_a_seq START WITH 1 INCREMENT BY 1 NOCACHE",
            "CREATE SEQUENCE clap_d_seq START WITH 1 INCREMENT BY 1 NOCACHE"
        ]
        
        for seq_sql in sequences:
            try:
                cursor.execute(seq_sql)
            except oracledb.DatabaseError:
                pass
        
        # 사용자 테이블 생성
        try:
            cursor.execute("""
                CREATE TABLE users (
                    id NUMBER PRIMARY KEY,
                    user_id VARCHAR2(20) UNIQUE,
                    password_hash VARCHAR2(255)
                )
            """)
        except oracledb.DatabaseError:
            pass
        
        # 환자 테이블 생성
        try:
            cursor.execute("""
                CREATE TABLE patients (
                    id NUMBER PRIMARY KEY,
                    patient_id VARCHAR2(20),
                    name VARCHAR2(50),
                    age NUMBER,
                    gender VARCHAR2(10),
                    test_type VARCHAR2(20),
                    test_date DATE,
                    requester VARCHAR2(100),
                    tester VARCHAR2(50),
                    created_at DATE DEFAULT SYSDATE
                )
            """)
        except oracledb.DatabaseError:
            pass
        
        # CLAP-A 상세 테이블 생성
        try:
            cursor.execute("""
                CREATE TABLE clap_a_results (
                    id NUMBER PRIMARY KEY,
                    patient_id VARCHAR2(20),
                    test_date DATE,
                    total_score NUMBER,
                    category VARCHAR2(50),
                    sub_category VARCHAR2(50),
                    score NUMBER,
                    max_score NUMBER,
                    percentage NUMBER(5,2),
                    status VARCHAR2(20),
                    created_at DATE DEFAULT SYSDATE
                )
            """)
        except oracledb.DatabaseError:
            pass
            
        # CLAP-D 상세 테이블 생성
        try:
            cursor.execute("""
                CREATE TABLE clap_d_results (
                    id NUMBER PRIMARY KEY,
                    patient_id VARCHAR2(20),
                    test_date DATE,
                    category VARCHAR2(50),
                    item VARCHAR2(100),
                    result VARCHAR2(50),
                    normal_range VARCHAR2(50),
                    status VARCHAR2(20),
                    created_at DATE DEFAULT SYSDATE
                )
            """)
        except oracledb.DatabaseError:
            pass
        
        connection.commit()
        
    except oracledb.Error as e:
        st.error(f"테이블 생성 오류: {e}")
    finally:
        safe_close_connection(connection)

# Oracle 샘플 데이터 삽입 함수
def insert_demo_data():
    connection = None
    try:
        connection = get_verified_connection()
        if not connection:
            return
            
        cursor = connection.cursor()
        
        # 사용자 데이터 확인
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        if user_count == 0:
            password_hash = hashlib.md5("demo123".encode()).hexdigest()
            cursor.execute("""
                INSERT INTO users (id, user_id, password_hash)
                VALUES (users_seq.NEXTVAL, :1, :2)
            """, ("user", password_hash))
            
            # 환자 데이터 추가
            cursor.execute("""
                INSERT INTO patients (id, patient_id, name, age, gender, test_type, test_date, requester, tester)
                VALUES (patients_seq.NEXTVAL, :1, :2, :3, :4, :5, TO_DATE(:6, 'YYYY-MM-DD'), :7, :8)
            """, ("01258472", "박충북", 65, "남", "CLAP-D", "2024-10-16", "충북대병원(RM) / 공현호", "백동재"))
            
            cursor.execute("""
                INSERT INTO patients (id, patient_id, name, age, gender, test_type, test_date, requester, tester)
                VALUES (patients_seq.NEXTVAL, :1, :2, :3, :4, :5, TO_DATE(:6, 'YYYY-MM-DD'), :7, :8)
            """, ("01258472", "박충북", 65, "남", "CLAP-A", "2024-10-15", "충북대병원(RM) / 공현호", "백동재"))
            
            # CLAP-A 샘플 데이터 삽입
            clap_a_data = [
                ("01258472", "2024-10-15", "기본정보", "나이", 65, 100, 65.0, "정상"),
                ("01258472", "2024-10-15", "기본정보", "교육연수", 12, 20, 60.0, "정상"),
                ("01258472", "2024-10-15", "인지기능", "MMSE-K", 28, 30, 93.3, "정상"),
                ("01258472", "2024-10-15", "인지기능", "CDR", 0, 3, 0.0, "정상"),
                ("01258472", "2024-10-15", "언어기능", "K-BNT", 45, 60, 75.0, "경도저하"),
                ("01258472", "2024-10-15", "언어기능", "의미유창성", 15, 20, 75.0, "정상"),
                ("01258472", "2024-10-15", "언어기능", "음성유창성", 12, 20, 60.0, "정상"),
            ]
            
            for data in clap_a_data:
                cursor.execute("""
                    INSERT INTO clap_a_results (id, patient_id, test_date, category, sub_category, score, max_score, percentage, status)
                    VALUES (clap_a_seq.NEXTVAL, :1, TO_DATE(:2, 'YYYY-MM-DD'), :3, :4, :5, :6, :7, :8)
                """, data)
            
            # CLAP-D 샘플 데이터 삽입
            clap_d_data = [
                ("01258472", "2024-10-16", "발성검사", "기본주파수", "120.5 Hz", "80-200 Hz", "정상"),
                ("01258472", "2024-10-16", "발성검사", "주파수변동", "1.2%", "<2.0%", "정상"),
                ("01258472", "2024-10-16", "발성검사", "진폭변동", "2.1%", "<3.0%", "정상"),
                ("01258472", "2024-10-16", "조음검사", "자음정확도", "85%", ">90%", "경도저하"),
                ("01258472", "2024-10-16", "조음검사", "모음정확도", "92%", ">95%", "정상"),
                ("01258472", "2024-10-16", "유창성검사", "말속도", "4.2 음절/초", "4.0-6.0", "정상"),
                ("01258472", "2024-10-16", "유창성검사", "비유창성", "8%", "<10%", "정상"),
                ("01258472", "2024-10-16", "억양검사", "억양정확도", "78%", ">80%", "경도저하"),
            ]
            
            for data in clap_d_data:
                cursor.execute("""
                    INSERT INTO clap_d_results (id, patient_id, test_date, category, item, result, normal_range, status)
                    VALUES (clap_d_seq.NEXTVAL, :1, TO_DATE(:2, 'YYYY-MM-DD'), :3, :4, :5, :6, :7)
                """, data)
            
            connection.commit()
            
    except oracledb.Error as e:
        st.error(f"샘플 데이터 삽입 오류: {e}")
    finally:
        safe_close_connection(connection)

# 리포트 확인 함수
def confirm_report():
    """리포트 확인 함수"""
    st.success("리포트가 확인되었습니다!")

# 사용자 확인 함수
def authenticate_user(user_id, password):
    connection = None
    try:
        connection = get_verified_connection()
        if not connection:
            return None
            
        cursor = connection.cursor()
        password_hash = hashlib.md5(password.encode()).hexdigest()
        
        cursor.execute("""
            SELECT * FROM users 
            WHERE user_id = :1 AND password_hash = :2
        """, (user_id, password_hash))
        
        result = cursor.fetchone()
        return result
        
    except oracledb.Error as e:
        st.error(f"Oracle 인증 오류: {e}")
        return None
    finally:
        safe_close_connection(connection)

# 리포트 조회 함수
def get_reports(patient_id, test_type=None):
    connection = None
    try:
        connection = get_verified_connection()
        if not connection:
            return pd.DataFrame()
            
        cursor = connection.cursor()
        
        if test_type and test_type != "전체":
            query = """
                SELECT id, patient_id, name, age, gender, test_type, TO_CHAR(test_date, 'YYYY.MM.DD') as test_date, 
                       requester, tester
                FROM patients 
                WHERE patient_id = :1 AND test_type = :2
                ORDER BY test_date DESC, created_at DESC
            """
            cursor.execute(query, (patient_id, test_type))
        else:
            query = """
                SELECT id, patient_id, name, age, gender, test_type, TO_CHAR(test_date, 'YYYY.MM.DD') as test_date, 
                       requester, tester
                FROM patients 
                WHERE patient_id = :1
                ORDER BY test_date DESC, created_at DESC
            """
            cursor.execute(query, (patient_id,))
        
        results = cursor.fetchall()
        
        return pd.DataFrame(results, columns=[
            'ID', 'patient_id', 'name', 'age', 'gender', '검사유형', '검사일자', '의뢰인', '검사자'
        ])
        
    except oracledb.Error as e:
        st.error(f"Oracle 데이터 조회 오류: {e}")
        return pd.DataFrame()
    finally:
        safe_close_connection(connection)

# CLAP-A 상세 데이터 조회
def get_clap_a_details(patient_id, test_date):
    connection = None
    try:
        connection = get_verified_connection()
        if not connection:
            return pd.DataFrame()
            
        cursor = connection.cursor()
        
        cursor.execute("""
            SELECT category, sub_category, score, max_score, percentage, status
            FROM clap_a_results
            WHERE patient_id = :1 AND test_date = TO_DATE(:2, 'YYYY.MM.DD')
            ORDER BY category, sub_category
        """, (patient_id, test_date))
        
        results = cursor.fetchall()
        return pd.DataFrame(results, columns=[
            'category', 'sub_category', 'score', 'max_score', 'percentage', 'status'
        ])
        
    except oracledb.Error as e:
        st.error(f"CLAP-A 데이터 조회 오류: {e}")
        return pd.DataFrame()
    finally:
        safe_close_connection(connection)

# CLAP-D 상세 데이터 조회
def get_clap_d_details(patient_id, test_date):
    connection = None
    try:
        connection = get_verified_connection()
        if not connection:
            return pd.DataFrame()
            
        cursor = connection.cursor()
        
        cursor.execute("""
            SELECT category, item, result, normal_range, status
            FROM clap_d_results
            WHERE patient_id = :1 AND test_date = TO_DATE(:2, 'YYYY.MM.DD')
            ORDER BY category, item
        """, (patient_id, test_date))
        
        results = cursor.fetchall()
        return pd.DataFrame(results, columns=[
            'category', 'item', 'result', 'normal_range', 'status'
        ])
        
    except oracledb.Error as e:
        st.error(f"CLAP-D 데이터 조회 오류: {e}")
        return pd.DataFrame()
    finally:
        safe_close_connection(connection)

def main():
    # 데이터베이스 초기화
    create_demo_tables()
    insert_demo_data()
    
    # 세션 상태 초기화
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user_info = None
        st.session_state.current_page = "리포트"
        st.session_state.view_mode = "list"  # list, clap_a_detail, clap_d_detail
        st.session_state.selected_report = None
    
    # 로그인 상태 확인
    if not st.session_state.logged_in:
        show_login_page()
    else:
        show_main_interface()

def show_login_page():
    """로그인 페이지"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div style="text-align: center; color: white; font-size: 2rem; margin: 2rem 0;">👋 CLAP</div>', unsafe_allow_html=True)
        st.markdown('<div style="text-align: center; color: white; font-size: 1.2rem; margin-bottom: 2rem;">의료 검사 시스템</div>', unsafe_allow_html=True)
        
        with st.form("login_form"):
            user_id = st.text_input("id", placeholder="user")
            password = st.text_input("비밀번호", type="password", placeholder="demo123")
            
            if st.form_submit_button("로그인", use_container_width=True):
                if user_id and password:
                    user_info = authenticate_user(user_id, password)
                    if user_info:
                        st.session_state.logged_in = True
                        st.session_state.user_info = {
                            'user_id': user_id
                        }
                        st.rerun()
                    else:
                        st.error("로그인 정보가 올바르지 않습니다.")
                else:
                    st.error("id와 비밀번호를 입력해주세요.")
        
        st.info("데모 계정 - id: user, 비밀번호: demo123")

def show_main_interface():
    # 환자 정보
    patient_info = get_reports("01258472")
    
    # 사이드바
    with st.sidebar:
        st.markdown('<div class="sidebar-logo">👋 CLAP</div>', unsafe_allow_html=True)

        # 메뉴
        st.markdown('<div class="sidebar-menu">', unsafe_allow_html=True)
        menu_items = ["평가", "재활", "리포트"]
        for item in menu_items:
            prefix = "🟡 " if item == st.session_state.current_page else ""
            if st.button(f"{prefix}{item}", key=f"menu_{item}", use_container_width=True):
                st.session_state.current_page = item
                st.session_state.view_mode = "list"  # 메뉴 변경시 리스트 뷰로 초기화
                if item != "리포트":
                    st.info(f"{item} 기능은 개발 중입니다.")
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        # 하단 그룹 묶기
        st.markdown('<div class="sidebar-footer" style="position: absolute !important;margin-top:100px">', unsafe_allow_html=True)

        st.markdown(f"""
        <div class="patient-info">
            <div class="patient-name">{patient_info['name'][0]} {patient_info['age'][0]}세</div>
            <div class="patient-id">{patient_info['patient_id'][0]}</div>
            <div class="patient-gender">{patient_info['gender'][0]}</div>
        </div>
        """, unsafe_allow_html=True)

        # 로그아웃 버튼
        logout_clicked = st.button("로그아웃", key="logout", use_container_width=True)
        if logout_clicked:
            st.session_state.logged_in = False
            st.session_state.user_info = None
            st.rerun()
            
        st.markdown('</div>', unsafe_allow_html=True)

    # 메인 컨텐츠
    if st.session_state.current_page == "리포트":
        if st.session_state.view_mode == "list":
            show_report_page(patient_info['patient_id'][0])
        elif st.session_state.view_mode == "clap_a_detail":
            show_clap_a_detail()
        elif st.session_state.view_mode == "clap_d_detail":
            show_clap_d_detail()
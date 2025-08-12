import streamlit as st
import oracledb
import pandas as pd
from datetime import datetime, date
import hashlib

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
    
    /* 로그아웃 버튼 */
    .stButton > button.logout-btn {
        background: rgba(255, 255, 255, 0.2);
        border: none;
        color: white;
        padding: 10px 15px;
        border-radius: 6px;
        cursor: pointer;
        font-size: 14px;
        width: 100%;
        margin-bottom: 10px;
    }

    .stButton > button.logout-btn:hover {
        background: rgba(255, 255, 255, 0.3);
    }

    /* 로그인 버튼 */
    .stFormSubmitButton > button {
        color: #ff4b4b !important;
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
            "CREATE SEQUENCE patients_seq START WITH 1 INCREMENT BY 1 NOCACHE"
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
            
            # 샘플 리포트 추가
            for i in range(5):
                cursor.execute("""
                    INSERT INTO patients (id, patient_id, name, age, gender, test_type, test_date, requester, tester)
                    VALUES (reports_seq.NEXTVAL, :1, :2, :3,:4,:5, TO_DATE(:6, 'YYYY-MM-DD'), :7, :8)
                """, ("01258472","박충북",65, "남","CLAP-D", "2024-10-16", "충북대병원(RM) / 공현호", "백동재"))
            
            connection.commit()
            
    except oracledb.Error as e:
        st.error(f"샘플 데이터 삽입 오류: {e}")
    finally:
        safe_close_connection(connection)

# 리포트 상세보기
def detailed_report(patient_info, test_info):
    """상세 리포트 화면 표시"""
    st.session_state.selected_report = {
        'patient_info': patient_info,
        'test_info': test_info
    }
    st.success('세션이 존재합니다')

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
                SELECT id, patient_id,name,age,gender,test_type, TO_CHAR(test_date, 'YYYY.MM.DD') as test_date, 
                       requester, tester
                FROM patients 
                WHERE patient_id = :1 AND test_type = :2
                ORDER BY test_date DESC, created_at DESC
            """
            cursor.execute(query, (patient_id, test_type))
        else:
            query = """
                SELECT id, patient_id,name,age,gender, test_type, TO_CHAR(test_date, 'YYYY.MM.DD') as test_date, 
                       requester, tester
                FROM patients 
                WHERE patient_id = :1
                ORDER BY test_date DESC, created_at DESC
            """
            cursor.execute(query, (patient_id,))
        
        results = cursor.fetchall()
        
        return pd.DataFrame(results, columns=[
            'ID', 'patient_id','name','age','gender', '검사유형', '검사일자', '의뢰인', '검사자'
        ])
        
    except oracledb.Error as e:
        st.error(f"Oracle 데이터 조회 오류: {e}")
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
    patient_info=get_reports("01258472")
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
                if item != "리포트":
                    st.info(f"{item} 기능은 개발 중입니다.")
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

        # ✅ 하단 그룹 묶기 (스타일 인라인으로 강제 적용)
        st.markdown('<div class="sidebar-footer" style="position: absolute !important;margin-top:100px>', unsafe_allow_html=True)

        st.markdown(f"""
        <div class="patient-info">
            <div class="patient-name">{patient_info['name'][0]} {patient_info['age'][0]}세</div>
            <div class="patient-id">{patient_info['patient_id'][0]}</div>
            <div class="patient-gender">{patient_info['gender'][0]}</div>
        </div>
        """, unsafe_allow_html=True)

        # 로그아웃 버튼을 sidebar-footer 안에 포함
        logout_clicked = st.button("로그아웃", key="logout", use_container_width=True)
        if logout_clicked:
            st.session_state.logged_in = False
            st.session_state.user_info = None
            st.rerun()
            
        st.markdown('</div>', unsafe_allow_html=True)  # sidebar-footer 닫기



    # 메인 컨텐츠
    if st.session_state.current_page == "리포트":
        show_report_page(patient_info['patient_id'][0])

# 리포트 미리보기
def show_report_page(patient_id):
    
    # 헤더 (탭과 프린트 버튼)
    col_tabs, col_print = st.columns([3, 1])
    
    with col_tabs:
        # 탭 버튼들
        col_tab1, col_tab2, col_spacer = st.columns([1, 1, 4])
        
        with col_tab1:
            if st.button("CLAP-A", key="tab_clap_a", type="primary"):
                st.session_state.selected_filter = "CLAP-A"
                st.rerun()
        
        with col_tab2:
            if st.button("CLAP-D", key="tab_clap_d"):
                st.session_state.selected_filter = "CLAP-D"
                st.rerun()
    
    with col_print:
        if st.button("🖨", key="print_btn"):
            st.info("프린트 기능입니다.")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 리포트 목록 가져오기, 없으면 info
    if 'selected_filter' in st.session_state:
        reports_df = get_reports(patient_id, st.session_state.selected_filter)

        if not reports_df.empty:
            for idx, row in reports_df.iterrows():
                # print(row)
                
                # 컬럼을 사용해서 레이아웃 구성
                col1, col2 = st.columns([5, 1])
                
                with col1:
                    # 환자 정보만 가져오면 되니까 줄글로 써버려도 되는데, button처럼 함수를 적용해야 하면...
                    report_html = f"""
                    <div class="report-item" style="margin-bottom: 0;">
                        <div class="report-info">
                            <input type="checkbox" style="width: 18px; height: 18px; accent-color: white; margin-right: 20px;">
                            <div class="report-title">{row['검사유형']}</div>
                            <div class="report-details">
                                <div class="detail-item">
                                    <span class="detail-label">검사일자</span>
                                    <span class="detail-value">{row['검사일자']}</span>
                                </div>
                                <div class="detail-item">
                                    <span class="detail-label">의뢰인</span>
                                    <span class="detail-value">{row['의뢰인']}</span>
                                </div>
                                <div class="detail-item">
                                    <span class="detail-label">검사자</span>
                                    <span class="detail-value">{row['검사자']}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                    """
                    st.markdown(report_html, unsafe_allow_html=True)
                
                with col2:
                    # 확인하기 버튼 스타일 적용
                    st.markdown(f"""
                    <style>
                    .stButton[key="confirm_{idx}"] > button {{
                        margin-top: 25px !important;
                    }}
                    </style>
                    """, unsafe_allow_html=True)
                 
                    # 확인하기 클릭하면 detailed_report 호출
                    if st.button("확인하기 〉", key=f"confirm_{idx}"):
                        patient_info = {
                            'name': row['name'],
                            'age': row['age'], 
                            'gender': row['gender'],
                            'patient_id': row['patient_id']
                        }
                        test_info = {
                            '검사일자': row['검사일자'],
                            '검사자': row['검사자'],
                            '의뢰인': row['의뢰인']
                        }
                        detailed_report(patient_info, test_info)
                # 리포트 아이템 간격
                st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)
                
        else:
            st.info("검사 결과가 없습니다.")
        
    else:
        # reports_df=get_reports(patient_id, "CLAP-A")
        st.info('검사유형을 선택해 주세요')

if __name__ == "__main__":
    main()

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
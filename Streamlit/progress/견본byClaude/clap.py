import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 설정
st.set_page_config(
    page_title="CLAP",
    page_icon="👋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 리포트 조회 함수
def get_reports(patient_id, test_type=None):
    data = [
        {'ID': 1, 'patient_id': '01258472', 'name': '박충북', 'age': 65, 'gender': '남', 
         '검사유형': 'CLAP-D', '검사일자': '2024.10.16', '의뢰인': '충북대병원(RM) / 공현호', '검사자': '백동재'},
        {'ID': 2, 'patient_id': '01258472', 'name': '박충북', 'age': 65, 'gender': '남', 
         '검사유형': 'CLAP-A', '검사일자': '2024.10.15', '의뢰인': '충북대병원(RM) / 공현호', '검사자': '백동재'}
    ]
    
    df = pd.DataFrame(data)
    
    if test_type and test_type != "전체":
        df = df[df['검사유형'] == test_type]
    
    return df


# CLAP-D 상세 데이터 조회
def get_clap_d_details(patient_id, test_date):
    data = [
        {'category': '발성검사', 'item': '기본주파수', 'result': '120.5 Hz', 'normal_range': '80-200 Hz', 'status': '정상'},
        {'category': '발성검사', 'item': '주파수변동', 'result': '1.2%', 'normal_range': '<2.0%', 'status': '정상'},
        {'category': '조음검사', 'item': '자음정확도', 'result': '85%', 'normal_range': '>90%', 'status': '경도저하'},
        {'category': '조음검사', 'item': '모음정확도', 'result': '92%', 'normal_range': '>95%', 'status': '정상'},
    ]
    return pd.DataFrame(data)

# 간단한 인증 함수
def authenticate_user(user_id, password):
    if user_id == "user" and password == "demo123":
        return True
    return False

def main():
    # 세션 상태 초기화
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user_info = None
        st.session_state.current_page = "리포트"
        st.session_state.view_mode = "list"
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
        st.title("👋 CLAP")
        st.subheader("의료 검사 시스템")
        
        with st.form("login_form"):
            user_id = st.text_input("id", placeholder="user")
            password = st.text_input("비밀번호", type="password", placeholder="demo123")
            
            if st.form_submit_button("로그인", use_container_width=True):
                if user_id and password:
                    if authenticate_user(user_id, password):
                        st.session_state.logged_in = True
                        st.session_state.user_info = {'user_id': user_id}
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
        st.title("👋 CLAP")

        # 메뉴
        menu_items = ["평가", "재활", "리포트"]
        for item in menu_items:
            prefix = "🟡 " if item == st.session_state.current_page else ""
            if st.button(f"{prefix}{item}", key=f"menu_{item}", use_container_width=True):
                st.session_state.current_page = item
                st.session_state.view_mode = "list"
                if item != "리포트":
                    st.info(f"{item} 기능은 개발 중입니다.")
                st.rerun()

        # 환자 정보 표시
        st.divider()
        if not patient_info.empty:
            st.write(f"**{patient_info['name'].iloc[0]} {patient_info['age'].iloc[0]}세**")
            st.write(f"환자번호: {patient_info['patient_id'].iloc[0]}")
            st.write(f"성별: {patient_info['gender'].iloc[0]}")

        # 로그아웃 버튼
        if st.button("로그아웃", key="logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user_info = None
            st.rerun()

    # 메인 컨텐츠
    if st.session_state.current_page == "리포트":
        if st.session_state.view_mode == "list":
            show_report_page(patient_info['patient_id'].iloc[0] if not patient_info.empty else "01258472")
        elif st.session_state.view_mode == "clap_a_detail":
            show_clap_a_detail()
        elif st.session_state.view_mode == "clap_d_detail":
            show_clap_d_detail()

def show_report_page(patient_id):
    # 초기값 설정
    if 'selected_filter' not in st.session_state:
        st.session_state.selected_filter = "CLAP-A"
    
    st.header("리포트")
    
    # 탭 버튼들
    col1, col2, col3 = st.columns([1, 1, 8])
    
    with col1:
        if st.button("CLAP-A", type="primary"):
            st.session_state.selected_filter = "CLAP-A"
            st.rerun()
    
    with col2:
        if st.button("CLAP-D", type="primary" if st.session_state.selected_filter == "CLAP-D" else "secondary"):
            st.session_state.selected_filter = "CLAP-D"
            st.rerun()
    
    # 리포트 목록
    reports_df = get_reports(patient_id, st.session_state.selected_filter)

    if not reports_df.empty:
        for idx, row in reports_df.iterrows():
            with st.container():
                col1, col2 = st.columns([5, 1])
                
                with col1:
                    st.write(f"**{row['검사유형']}**")
                    st.write(f"검사일자: {row['검사일자']} | 의뢰인: {row['의뢰인']} | 검사자: {row['검사자']}")
                
                with col2:
                    if st.button("확인하기 〉", key=f"confirm_{idx}"):
                        st.session_state.selected_report = {
                            'type': row['검사유형'],
                            'date': row['검사일자'],
                            'patient_id': row['patient_id']
                        }
                        if row['검사유형'] == "CLAP-A":
                            st.session_state.view_mode = "clap_a_detail"
                        else:
                            st.session_state.view_mode = "clap_d_detail"
                        st.rerun()
                
                st.divider()
    else:
        st.info(f"{st.session_state.selected_filter} 검사 결과가 없습니다.")

def show_clap_a_detail():
    """CLAP-A 상세 리포트 페이지"""
    if st.button("< 뒤로가기"):
        st.session_state.view_mode = "list"
        st.rerun()
    
    st.header("CLAP-A 상세 리포트")
    st.subheader("인지-언어 통합 평가")
    
    # 리포트 데이터 가져오기
    report = st.session_state.selected_report
    clap_a_data = get_clap_a_details(report['patient_id'], report['date'])
    patient_info = get_reports(report['patient_id']).iloc[0]
    
    # 환자 정보
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write(f"**환자명:** {patient_info['name']}")
        st.write(f"**나이:** {patient_info['age']}세")
    with col2:
        st.write(f"**성별:** {patient_info['gender']}")
        st.write(f"**환자번호:** {patient_info['patient_id']}")
    with col3:
        st.write(f"**검사일자:** {report['date']}")
        st.write(f"**검사자:** {patient_info['검사자']}")
    
    st.divider()
    
    # 검사 결과
    if not clap_a_data.empty:
        categories = clap_a_data['category'].unique()
        
        for category in categories:
            st.subheader(category)
            category_data = clap_a_data[clap_a_data['category'] == category]
            
            # 테이블로 표시
            display_data = category_data[['sub_category', 'score', 'max_score', 'percentage', 'status']].copy()
            display_data.columns = ['항목', '점수', '만점', '백분율(%)', '상태']
            st.dataframe(display_data, use_container_width=True)
        
        # 차트
        st.subheader("검사 결과 차트")
        fig = px.bar(clap_a_data, x='sub_category', y='percentage', color='status',
                     title="CLAP-A 검사 결과", labels={'sub_category': '검사항목', 'percentage': '백분율(%)'})
        st.plotly_chart(fig, use_container_width=True)

def show_clap_d_detail():
    """CLAP-D 상세 리포트 페이지"""
    if st.button("< 뒤로가기"):
        st.session_state.view_mode = "list"
        st.rerun()
    
    st.header("CLAP-D 상세 리포트")
    st.subheader("말소리 산출 능력 평가")
    
    # 리포트 데이터 가져오기
    report = st.session_state.selected_report
    clap_d_data = get_clap_d_details(report['patient_id'], report['date'])
    patient_info = get_reports(report['patient_id']).iloc[0]
    
    # 환자 정보
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write(f"**환자명:** {patient_info['name']}")
        st.write(f"**나이:** {patient_info['age']}세")
    with col2:
        st.write(f"**성별:** {patient_info['gender']}")
        st.write(f"**환자번호:** {patient_info['patient_id']}")
    with col3:
        st.write(f"**검사일자:** {report['date']}")
        st.write(f"**검사자:** {patient_info['검사자']}")
    
    st.divider()
    
    # 검사 결과
    if not clap_d_data.empty:
        categories = clap_d_data['category'].unique()
        
        for category in categories:
            st.subheader(category)
            category_data = clap_d_data[clap_d_data['category'] == category]
            
            # 테이블로 표시
            display_data = category_data[['item', 'result', 'normal_range', 'status']].copy()
            display_data.columns = ['검사항목', '결과', '정상범위', '상태']
            st.dataframe(display_data, use_container_width=True)
        
        # 검사 결과 요약
        st.subheader("검사 결과 요약")
        status_counts = clap_d_data['status'].value_counts()
        
        col1, col2 = st.columns(2)
        with col1:
            fig_pie = px.pie(values=status_counts.values, names=status_counts.index, title="검사 결과 분포")
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            category_status = clap_d_data.groupby(['category', 'status']).size().reset_index(name='count')
            fig_bar = px.bar(category_status, x='category', y='count', color='status', title="카테고리별 검사 결과")
            st.plotly_chart(fig_bar, use_container_width=True)

if __name__ == "__main__":
    main()
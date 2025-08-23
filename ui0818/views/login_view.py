import streamlit as st
from services import auth_service
def show_login_page():
    """로그인 페이지"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.title("👋 CLAP")
        st.subheader("의료 검사 시스템")
        
        with st.form("login_form"):
            user_id = st.text_input("id", placeholder="user")
            password = st.text_input("비밀번호", type="password", placeholder="d")
            
            if st.form_submit_button("로그인", use_container_width=True):
                if user_id and password:
                    if auth_service.authenticate_user(user_id, password):
                        st.session_state.logged_in = True
                        st.session_state.user_info = {'user_id': user_id}
                        st.rerun()
                    else:
                        st.error("로그인 정보가 올바르지 않습니다.")
                else:
                    st.error("id와 비밀번호를 입력해주세요.")
        
        st.info("데모 계정 - id: user, 비밀번호: d")

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
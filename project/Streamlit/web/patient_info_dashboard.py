import streamlit as st
import pandas as pd
import numpy as np

# 페이지 설정
st.set_page_config(
    page_title="환자 정보 관리 시스템",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state='collapsed'
)

# 헤더
st.title("🏥 환자 정보 관리 시스템")
st.markdown("---")

# 사이드바
st.sidebar.header("📋 파일 업로드")
st.sidebar.markdown("patient_info.csv 파일을 업로드해주세요")

# 파일 업로더
uploaded_file = st.sidebar.file_uploader(
    "CSV 파일 선택",
    type=['csv'],
    help="이름, 검사결과, 총 점수, 의심 여부 컬럼이 포함된 CSV 파일"
)
# print(uploaded_file)
# 메인 컨텐츠 영역
col1, col2 = st.columns([2, 1])

with col1:
    st.header("📊 환자 데이터")
    
    if uploaded_file is not None:
        try:
            # CSV 파일 읽기
            df = pd.read_csv(uploaded_file)
            
            # 데이터 검증
            required_columns = ['이름', '검사결과', '총 점수', '의심 여부']
            
            if all(col in df.columns for col in required_columns):
                st.success(f"✅ 파일이 성공적으로 업로드되었습니다! ({len(df)}건의 데이터)")
                
                # 데이터 전처리
                df['의심 여부'] = df['의심 여부'].astype(str).str.upper()
                
                # 검색 기능
                st.subheader("🔍 데이터 필터링")
                
                filter_col1, filter_col2, filter_col3 = st.columns(3)
                
                with filter_col1:
                    name_filter = st.text_input("이름으로 검색", placeholder="환자 이름 입력")
                
                with filter_col2:
                    result_filter = st.selectbox(
                        "결과 필터",
                        ["전체"] + list(df['검사결과'].unique())
                    )
                
                with filter_col3:
                    suspicion_filter = st.selectbox(
                        "의심 여부 필터",
                        ["전체", "T", "F"]
                    )
                
                # 데이터 필터링
                filtered_df = df.copy()
                
                if name_filter:
                    filtered_df = filtered_df[filtered_df['이름'].str.contains(name_filter, case=False, na=False)]
                
                if result_filter != "전체":
                    filtered_df = filtered_df[filtered_df['검사결과'] == result_filter]
                
                if suspicion_filter != "전체":
                    filtered_df = filtered_df[filtered_df['의심 여부'] == suspicion_filter]
                
                # 데이터 표시
                st.subheader("📋 환자 목록")
                
                if len(filtered_df) > 0:
                    # 의심 여부에 따른 스타일링을 위한 함수
                    def highlight_suspicion(row):
                        if row['의심 여부'] == 'T':
                            return ['background-color: #ffebee'] * len(row)  # 연한 빨간색
                        else:
                            return ['background-color: #e8f5e8'] * len(row)  # 연한 초록색
                    
                    # 스타일이 적용된 데이터프레임 표시
                    styled_df = filtered_df.style.apply(highlight_suspicion, axis=1)
                    st.dataframe(
                        styled_df,
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    # 데이터 요약 정보
                    st.subheader("📈 데이터 요약")
                    
                    summary_col1, summary_col2, summary_col3 = st.columns(3)
                    
                    with summary_col1:
                        st.metric("총 환자 수", len(filtered_df))
                    
                    with summary_col2:
                        suspicion_count = len(filtered_df[filtered_df['의심 여부'] == 'T'])
                        st.metric("의심 환자", suspicion_count)
                    
                    with summary_col3:
                        if '총 점수' in filtered_df.columns:
                            avg_score = filtered_df['총 점수'].mean()
                            st.metric("평균 점수", f"{avg_score:.1f}")
                    
                
                else:
                    st.warning("⚠️ 필터 조건에 맞는 데이터가 없습니다.")
                
                # 원본 데이터 보기 옵션
                # if st.checkbox("원본 데이터 보기"):
                #     st.subheader("📄 원본 데이터")
                #     st.dataframe(df, use_container_width=True)
                
            else:
                st.error("❌ CSV 파일에 필요한 컬럼이 없습니다.")
                st.write("필요한 컬럼:", required_columns)
                st.write("현재 파일의 컬럼:", list(df.columns))
                
        except Exception as e:
            st.error(f"❌ 파일을 읽는 중 오류가 발생했습니다: {str(e)}")
    
    else:
        # 샘플 데이터 표시
        st.info("📁 CSV 파일을 업로드하면 환자 데이터가 여기에 표시됩니다.")
        
        # 샘플 데이터 예시
        st.subheader("📋 샘플 데이터 형식")
        sample_data = {
            '이름': ['김철수', '이영희', '박민수', '최지영'],
            '검사결과': ['경증', '중등도', '중증', '경증'],
            '총 점수': [75, 82, 91, 68],
            '의심 여부': ['F', 'T', 'T', 'F']
        }
        sample_df = pd.DataFrame(sample_data)
        
        # 샘플 데이터에 스타일 적용
        def highlight_sample_suspicion(row):
            if row['의심 여부'] == 'T':
                return ['background-color: #ffebee'] * len(row)
            else:
                return ['background-color: #e8f5e8'] * len(row)
        
        styled_sample = sample_df.style.apply(highlight_sample_suspicion, axis=1)
        st.dataframe(styled_sample, use_container_width=True, hide_index=True)

with col2:
    st.header("ℹ️ 시스템 정보")
    
    # 시스템 안내
    st.markdown("""
    ### 📝 사용 방법
    1. 왼쪽 사이드바에서 CSV 파일을 업로드하세요
    2. 데이터가 자동으로 표시됩니다
    3. 필터를 사용해 원하는 데이터를 찾으세요
    
    ### 📋 CSV 파일 형식
    다음 컬럼이 필요합니다:
    - **이름**: 환자 이름
    - **검사결과**: 검사 결과 상태
    - **총 점수**: 숫자형 점수
    - **의심 여부**: T(True) 또는 F(False)
    
    ### 🎨 색상 표시
    - 🔴 **연한 빨간색**: 의심 환자 (T)
    - 🟢 **연한 초록색**: 정상 환자 (F)
    """)
    

# 푸터
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "🏥 환자 정보 관리 시스템 | Streamlit 기반"
    "</div>",
    unsafe_allow_html=True
)
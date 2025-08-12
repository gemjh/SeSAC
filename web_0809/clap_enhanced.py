import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit.components.v1 as components
import sys
# from report_main import get_assess_lst
import report_main as rmn
import tempfile
import ptk_sound as ptk


# 페이지 설정
st.set_page_config(
    page_title="CLAP",
    page_icon="👋",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.markdown("""
<style>
.custom-table {
    width: 100%;
    border-collapse: collapse;
    margin: 20px 0;
    font-size: 14px;
}
.custom-table th, .custom-table td {
    border: 1px solid #ddd;
    padding: 8px;
    text-align: center;
    vertical-align: middle;
}
.custom-table th {
    background-color: #f2f2f2;
    font-weight: bold;
}
.custom-table .header-row {
    background-color: #e6e6e6;
    font-weight: bold;
}
.custom-table .category-cell {
    background-color: #f8f8f8;
    font-weight: bold;
}
.custom-table .aphasia-category {

    font-weight: bold;
    vertical-align: middle;
}
.pronunciation-table {
    width: 100%;
    border-collapse: collapse;
    margin: 20px 0;
    font-size: 14px;
}
.pronunciation-table .section-title {
    font-size: 16px;
    font-weight: bold;
    margin: 5px 0 10px 0;
    color: #333;
}
.pronunciation-table .category-cell {
    background-color: #f8f8f8;
    font-weight: bold;
    text-align: left;
    padding-left: 15px;
}
.pronunciation-table th {
    background-color: #f2f2f2 !important;
    font-weight: bold;
}
.pronunciation-table th, .pronunciation-table td {
    border: 1px solid #ddd;
    padding: 12px 8px;
    text-align: center;
    vertical-align: middle;
}

.pronunciation-table .header-main {
    background-color: #e6e6e6;
    font-weight: bold;
}

.pronunciation-table .sub-category {
    background-color: #fafafa;
    text-align: left;
    padding-left: 20px;
}
.pronunciation-table .total-row {
    font-weight: bold;
}
.assessment-table {
    width: 100%;
    border-collapse: collapse;
    margin: 20px 0;
    font-size: 14px;
}
.assessment-table th {
    background-color: #f2f2f2 !important;
    font-weight: bold;
}
.assessment-table th, .assessment-table td {
    border: 1px solid #ddd;
    padding: 12px 8px;
    text-align: center;
    vertical-align: middle;
}
.assessment-table .header-main {
    background-color: #e6e6e6;
    font-weight: bold;
}
.assessment-table .sub-category {
    background-color: #fafafa;
    text-align: left;
    padding-left: 20px;
}
.assessment-table .total-row {
    background-color: #e6e6e6;
    font-weight: bold;
}
.assessment-table .word-column {
    background-color: white;
    text-align: left;
    padding-left: 10px;
    width: 80px;
}
.assessment-table .phoneme-columns {
    width: 40px;
    background-color: white;
}
.assessment-table .result-column {
    width: 60px;
    background-color: white;
}
.assessment-table .score-column {
    width: 50px;
    background-color: white;
}
.small-uploader {
    font-size: 12px;
}
.small-uploader > div > div {
    padding: 2px 4px;
    min-height: 25px;
}
.small-uploader .stFileUploader > div > div > div {
    padding: 2px;
    font-size: 10px;
}
.table-row {
    border-bottom: 1px solid #ddd;
    padding: 8px 0;
    margin: 0;
}
.table-header {
    border-bottom: 2px solid #333;
    font-weight: bold;
    padding: 10px 0;
    margin: 0;
}
.table-cell {
    padding: 8px 12px;
    vertical-align: middle;
    border-right: 1px solid #ddd;
}
.table-cell:last-child {
    border-right: none;
}
.total-row {
    border-top: 2px solid #333;
    font-weight: bold;
    padding: 10px 0;
    margin: 0;
}
.table-container {
    overflow: hidden;
    margin: 20px 0;
}
.table-container .stColumn:nth-child(1),
.table-container .stColumn:nth-child(2) {
    border-right: 1px solid #ddd !important;
}
.table-container [data-testid="column"] {
    border-right: 1px solid #ddd !important;
}
.table-container [data-testid="column"]:last-child {
    border-right: none !important;
}
.assessment-table .summary-row {
    background-color: #f9f9f9;
    font-weight: bold;
}
.assessment-table .description-cell {
    background-color: white;
    text-align: left;
    padding: 10px;
    font-size: 12px;
    line-height: 1.4;
}
.red-text {
    color: #e74c3c;
}
.blue-text {
    color: #3498db;
}
.section-title {
    font-size: 16px;
    font-weight: bold;
    margin: 5px 0 10px 0;
    color: #333;
}
.summary-text {
    text-align: right;
    font-size: 14px;
    color: #666;
    margin-bottom: 10px;
}
</style>
""",unsafe_allow_html=True)


# ----------------------  임시 DB   ----------------

evaluation_data = [
    {
        'id': 'a_sound',
        'title': "'아' 소리내기",
        'summary': "최대 발성 시간 NN 초 총점 NN 점",
        'items': [
            {'no': '연습', 'content': "'아'"},
            {'no': '1', 'content': "1회차 '아'"},
            {'no': '', 'content': "2회차 '아'"}
        ]
    },
    {
        'id': 'pa_sound',
        'title': "'퍼' 반복하기",
        'summary': "평균 횟수 NN 번 총점 NN 점",
        'items': [
            {'no': '연습', 'content': "'퍼'"},
            {'no': '1', 'content': "1회차 '퍼'"},
            {'no': '', 'content': "2회차 '퍼'"},
            {'no': '', 'content': "3회차 '퍼'"}
        ]
    },
    {
        'id': 'ta_sound',
        'title': "'터' 반복하기",
        'summary': "평균 횟수 NN 번 총점 NN 점",
        'items': [
            {'no': '연습', 'content': "'터'"},
            {'no': '1', 'content': "1회차 '터'"},
            {'no': '', 'content': "2회차 '터'"},
            {'no': '', 'content': "3회차 '터'"}
        ]
    },
    {
        'id': 'ka_sound',
        'title': "'커' 반복하기",
        'summary': "평균 횟수 NN 번 총점 NN 점",
        'items': [
            {'no': '연습', 'content': "'커'"},
            {'no': '1', 'content': "1회차 '커'"},
            {'no': '', 'content': "2회차 '커'"},
            {'no': '', 'content': "3회차 '커'"}
        ]
    },
    {
        'id': 'ptk_sound',
        'title': "'퍼터커' 반복하기",
        'summary': "평균 횟수 NN 번 총점 NN 점",
        'items': [
            {'no': '연습', 'content': "'퍼터커'"},
            {'no': '1', 'content': "1회차 '퍼터커'"},
            {'no': '', 'content': "2회차 '퍼터커'"},
            {'no': '', 'content': "3회차 '퍼터커'"}
        ]
    }
]
# --------------------------------------



# 리포트 조회 함수
def get_reports(patient_id, test_type=None):
    patient_id='1001'
    msg,df=rmn.get_assess_lst(patient_id)
    try:
        df.columns=['patient_id','name','age','gender','검사유형','검사일자','의뢰인','검사자']
    except:
        df=pd.DataFrame(['1001','박충북',65,0,'CLAP_D','2025-08-01','충북대병원','김재헌']).T
        df.columns=['patient_id','name','age','gender','검사유형','검사일자','의뢰인','검사자']

    # print('----------------------------------------\n\n\n\n',type(df),df)


    if test_type and test_type != "전체":
        df = df[df['검사유형'] == test_type]
    return df

# CLAP-A 상세 데이터 조회
def get_clap_a_details(patient_id, test_date):
            # display_data = category_data[['item_cnt', 'ans_cnt', 'score', 'apasia_score']].copy()

    data = [
        {'category': '결과 요약', 'item_cnt': 'O/X 고르기(15)', 'ans_cnt': '개', 'score': 'NN개', 'apasia_score': 'NN점'},
        {'category': '결과 요약', 'item_cnt': '사물 찾기(6)', 'ans_cnt': 'NN개', 'score': 'NN개', 'apasia_score': 'NN점'},
        {'category': '결과 요약', 'item_cnt': '그림 고르기(15)', 'ans_cnt': 'NN개', 'score': 'NN개', 'apasia_score': 'NN점'},
        {'category': '결과 요약', 'item_cnt': '듣고 따라 말하기(15)', 'ans_cnt': 'NN개', 'score': 'NN개', 'apasia_score': 'NN점'},
        {'category': '결과 요약', 'item_cnt': '끝말 맞추기(15)', 'ans_cnt': 'NN개', 'score': 'NN개', 'apasia_score': 'NN점'},
        {'category': '결과 요약', 'item_cnt': '물건 이름 말하기(15)', 'ans_cnt': 'NN개', 'score': 'NN개', 'apasia_score': 'NN점'},
        {'category': '결과 요약', 'item_cnt': '동물 이름 말하기(15)', 'ans_cnt': 'NN개', 'score': 'NN개', 'apasia_score': 'NN점'},
        {'category': '결과 요약', 'item_cnt': '그림 보고 이야기하기(15)', 'ans_cnt': 'NN개', 'score': 'NN개', 'apasia_score': 'NN점'},

    ]

    return pd.DataFrame(data)

# CLAP-D 상세 데이터 조회
def get_clap_d_details(patient_id, test_date):
    data = [        
        {'patient_id':patient_id, 'category': '아 검사', 'result': 100,'date':test_date},

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
    # 환자 정보: 일단 1001
    patient_info = get_reports("1001")
    
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
        # print("-------------------------",patient_info,"-------------------",sep='\n')
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
            show_report_page(patient_info['patient_id'].iloc[0] if not patient_info.empty else "1001")
        elif st.session_state.view_mode == "clap_a_detail":
            show_clap_a_detail()
        elif st.session_state.view_mode == "clap_d_detail":
            show_clap_d_detail()

def show_report_page(patient_id):
    # 초기값 설정
    if 'selected_filter' not in st.session_state:
        st.session_state.selected_filter = "CLAP_A"
    
    st.header("리포트")
    
    # 탭 버튼들
    col1, col2, col3 = st.columns([1, 1, 8])
    
    with col1:
        if st.button("CLAP-A", type="primary" if st.session_state.selected_filter == "CLAP_A" else "secondary"):
            st.session_state.selected_filter = "CLAP_A"
            st.rerun()
    
    with col2:
        if st.button("CLAP-D", type="primary" if st.session_state.selected_filter == "CLAP_D" else "secondary"):
            st.session_state.selected_filter = "CLAP_D"
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

def get_common(patient_id):
    report = st.session_state.selected_report
    patient_info = get_reports(report['patient_id']).iloc[0]
    # 환자 정보
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write(f"**의뢰 기관(과)/의뢰인** ")
        st.write(f"**이름**{patient_info['name']} ")
        st.write(f"**교육연수** ")
        st.write(f"**방언** ")

    with col2:
        st.write(f"**검사자명**")
        st.write(f"**성별** ")
        st.write(f"**문해여부** ")
        st.write(f"**발병일** ")

    with col3:
        st.write(f"검사일자**{report['date']}** ")
        st.write(f"**개인번호** ")

    st.write(f"**진단명** ")
    st.write(f"**주요 뇌병변 I** ")
    st.write(f"**주요 뇌병변 II** ")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.write(f"**편마비** ")

    with col2:
        st.write(f"**무시증** ")

    with col3:
        st.write(f"**시야결손** ")

    st.write(f"**기타 특이사항** ")
    st.divider()


def show_clap_a_detail():
    """CLAP-A 상세 리포트 페이지"""
    if st.button("< 뒤로가기"):
        st.session_state.view_mode = "list"
        st.rerun()
    
    st.header("CLAP-A")
    st.subheader("전산화 언어 기능 선별 검사(실어증) 결과지")
    
    # 리포트 데이터 가져오기
    report = st.session_state.selected_report
    clap_a_data = get_clap_a_details(report['patient_id'], report['date'])
    
    get_common(report['patient_id'])
    
    
    # 검사 결과
    if not clap_a_data.empty:
        categories = clap_a_data['category'].unique()
        for category in categories:
            st.subheader(category)
            category_data = clap_a_data[clap_a_data['category'] == category]

            



        # 결과 요약 차트
        col1, col2 = st.columns(2)
        with col1:
            fig = px.bar(clap_a_data, x='category', y='score',
                        title="문항별 점수", labels={'category': '검사항목', 'score': '점수'})
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig = px.bar(clap_a_data, x='category', y='score',
                        title="실어증 점수", labels={'category': '검사항목', 'score': '점수'})
            st.plotly_chart(fig, use_container_width=True)


def create_evaluation_table_html(eval_item):
    """st.components.v1.html을 위한 완전한 HTML 문서 생성"""
    
    html_content = f"""
        <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 10px;
        }}

        .pronunciation-detail-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
            font-size: 14px;
        }}
        .pronunciation-detail-table th {{
            background-color: #f2f2f2 !important;
            font-weight: bold;
        }}
        .pronunciation-detail-table th, .pronunciation-detail-table td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: center;
            vertical-align: middle;
        }}
        .pronunciation-detail-table .content-column {{
            background-color: white;
            text-align: left;
            padding-left: 15px;
            width: 200px;
        }}
        .pronunciation-detail-table .button-column {{
            width: auto;
            background-color: white;
        }}
        .pronunciation-detail-table .time-column {{
            width: 80px;
            background-color: white;
        }}
        .pronunciation-detail-table .score-column {{
            width: 60px;
            background-color: white;
        }}
        .rec-button {{
            background-color: #e74c3c;
            color: white;
            border: none;
            border-radius: 15px;
            padding: 4px 12px;
            font-size: 11px;
            margin-right: 5px;
            cursor: pointer;
            transition: background-color 0.3s;
        }}
        .rec-button:hover {{
            background-color: #c0392b;
        }}
        .graph-button {{
            background-color: #3498db;
            color: white;
            border: none;
            border-radius: 15px;
            padding: 4px 12px;
            font-size: 11px;
            cursor: pointer;
            transition: background-color 0.3s;
        }}
        .graph-button:hover {{
            background-color: #2980b9;
        }}
        .section-title{{
            font-size: 16px;
            font-weight: bold;
            margin: 5px 0 10px 0;
            color: #333;
        }}
        .summary-text {{
            text-align: right;
            font-size: 14px;
            color: #666;
            margin-bottom: 10px;
        }}
        </style>
    </head>
    <body>
        <div class="section-title">{eval_item['title']}</div>
        <div class="summary-text">{eval_item['summary']}</div>
        
        <table class="pronunciation-detail-table">
            <thead>
                <tr>
                    <th class="no-column">NO.</th>
                    <th colspan="2" class="content-column">문항</th>
                    <th class="time-column">발성시간</th>
                    <th class="score-column">점수</th>
                </tr>
            </thead>
            <tbody>
    """
    
    # 각 항목을 위한 행들 추가
    for i, item in enumerate(eval_item['items']):
        html_content += f"""
                <tr>
                    <td class="no-column">{item['no']}</td>
                    <td class="content-column">{item['content']}</td>
                    <td class="button-column">
                        <button class="rec-button" onclick="recordSound('{eval_item['id']}', {i})">REC.</button>
                        <button class="graph-button" onclick="showGraph('{eval_item['id']}', {i})">GRAPH</button>
                    </td>
                    <td class="time-column">NNN초</td>
                    <td class="score-column"></td>
                </tr>
        """
    
    html_content += """
            </tbody>
        </table>
        
        <script>
        function recordSound(evalId, itemIndex) {
            alert('🎤 ' + evalId + ' - ' + itemIndex + '번째 항목 녹음을 시작합니다!');
            // 실제 녹음 기능을 여기에 구현할 수 있습니다
        }
        
        function showGraph(evalId, itemIndex) {
            alert('📊 ' + evalId + ' - ' + itemIndex + '번째 항목의 그래프를 표시합니다!');
            // 실제 그래프 표시 기능을 여기에 구현할 수 있습니다
        }
        </script>
    </body>
    </html>
    """
    
    return html_content


def create_word_level_table(word_level_data):
    """단어수준 또박또박 말하기 테이블 생성"""
    html = """
    <div class="section-title">또박또박 말하기</div>
    <div class="summary-text">단어 수준&nbsp;&nbsp;&nbsp;&nbsp;자음정확도 NN/NN NN% 모음 정확도 NN/NN NN% 총점 NN 점</div>
    
    <table class="assessment-table">
        <thead>
            <tr>
                <th>NO.</th>
                <th>문항</th>
                <th>초성</th>
                <th>중성</th>
                <th>7종성</th>
                <th>모음</th>
                <th>전사</th>
                <th>점수</th>
            </tr>
        </thead>
        <tbody>
        </tbody>
    </table>
    """
    return html

def create_sentence_level_table(sentence_level_data):
    """문장수준 또박또박 말하기 테이블 생성"""
    
    html = """
    <div class="section-title">또박또박 읽기</div>
    <div class="summary-text">문장 수준&nbsp;&nbsp;&nbsp;&nbsp;자음정확도 NN/NN NN% 총점 NN 점</div>
    
    <table class="assessment-table">
        <thead>
            <tr>
                <th>NO.</th>
                <th>문항</th>
                <th colspan="2">반응 기록</th>
                <th>점수</th>
            </tr>
            <tr>
                <th></th>
                <th></th>
                <th>자음 정확도</th>
                <th>개수</th>
                <th></th>
            </tr>
        </thead>
        <tbody>
    """
    
    for data_item in sentence_level_data:
        no = data_item['no']
        sentences = data_item['sentence']
        phonemes = data_item['phonemes']
        score = data_item['score']
        
        phonemes_count = len(phonemes)
        sentence_text = "<br>".join(sentences)
        
        for i, phoneme in enumerate(phonemes):
            sound = phoneme['sound']
            count = phoneme['count']
            
            if i == 0:  # 첫 번째 행
                html += f"""
            <tr>
                <td rowspan="{phonemes_count}">{no}</td>
                <td class="category-cell" rowspan="{phonemes_count}">{sentence_text}</td>
                <td>{sound}</td>
                <td>{count}</td>
                <td rowspan="{phonemes_count}">{score}</td>
            </tr>
                """
            else:  # 나머지 행들
                html += f"""
            <tr>
                <td>{sound}</td>
                <td>{count}</td>
            </tr>
                """
    
    html += """
        </tbody>
    </table>
    """
    
    return html



def show_clap_d_detail():

    """CLAP-D 상세 리포트 페이지"""
    if st.button("< 뒤로가기"):
        st.session_state.view_mode = "list"
        st.rerun()
    
    st.header("CLAP-D")
    st.subheader("검사 결과지")
    
    # 리포트 데이터 가져오기
    report = st.session_state.selected_report
    clap_d_data = get_clap_d_details(report['patient_id'], report['date'])
    patient_info = get_reports(report['patient_id']).iloc[0]

    get_common(report['patient_id'])
    a_sound = 'N'


    # 파일 업로드 상태 관리를 위한 세션 상태 초기화
    if 'ah_uploaded' not in st.session_state:
        st.session_state.ah_uploaded = False
    if 'pa_uploaded' not in st.session_state:
        st.session_state.pa_uploaded = False
    if 'ta_uploaded' not in st.session_state:
        st.session_state.ta_uploaded = False
    if 'ka_uploaded' not in st.session_state:
        st.session_state.ka_uploaded = False
    if 'ptk_uploaded' not in st.session_state:
        st.session_state.ptk_uploaded = False
    
    if 'ah_result' not in st.session_state:
        st.session_state.ah_result = 'N'
    if 'pa_result' not in st.session_state:
        st.session_state.pa_result = 'N'
    if 'ta_result' not in st.session_state:
        st.session_state.ta_result = 'N'
    if 'ka_result' not in st.session_state:
        st.session_state.ka_result = 'N'
    if 'ptk_result' not in st.session_state:
        st.session_state.ptk_result = 'N'

    # pa_repeat, ta_repeat, ka_repeat, ptk_repeat = 'N', 'N', 'N', 'N'
            
    # 검사 결과
    if not clap_d_data.empty:
        st.subheader("결과 요약")
        # a_sound=ah.execute(input)
        # print("------------------------------",a_sound,"------------------------------",sep='\n\n\n')


        word_level,sentence_level,consonant_word,vowel_word,consonant_sentence='N','N','N','N','N'

        max_time,pa_avg,ta_avg,ka_avg,ptk_avg='N','N','N','N','N'
        total_score = 'N'
        # total_score = a_sound + pa_repeat + ta_repeat + ka_repeat + ptk_repeat + word_level + sentence_level
        
        # 표모양만들기 1: borderline 넣어서 table 비슷하게 결과와 입력 필드 표시
        st.markdown('<div class="table-container">', unsafe_allow_html=True)
        
        # 테이블모양 헤더
        st.markdown('<div class="table-header">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([3, 3, 2])
        with col1:
            st.markdown('<div class="table-cell" style="border-right: 1px solid #ddd;">문항</div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="table-cell" style="border-right: 1px solid #ddd;">수행 결과</div>', unsafe_allow_html=True)
        with col3:
            st.markdown('<div class="table-cell">점수</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 첫 번째 행 - 아 소리내기 (파일 업로더 포함)
        st.markdown('<div class="table-row">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([3, 3, 2])
        with col1:
            st.markdown('<div class="table-cell" style="border-right: 1px solid #ddd;">\'아\' 소리내기</div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="table-cell" style="border-right: 1px solid #ddd;">최대 발성시간 {max_time}초</div>', unsafe_allow_html=True)
        with col3:
            st.markdown('<div class="table-cell">', unsafe_allow_html=True)
            if not st.session_state.ah_uploaded:
                with st.container():
                    st.markdown('<div class="small-uploader">', unsafe_allow_html=True)
                    ah_sound_inline = st.file_uploader("", type=['wav', 'mp3'], key="ah_inline", label_visibility="collapsed")
                    st.markdown('</div>', unsafe_allow_html=True)

                # ------------------------------------- 무한로딩때문에 일단 주석처리 -------------------------------------
                # if ah_sound_inline is not None:
                #     import ah_sound as ah
                #     with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                #         tmp_file.write(ah_sound_inline.getvalue())
                #         file_path = tmp_file.name
                #         st.session_state.ah_result = ah.analyze_pitch_stability(file_path)
                #         st.session_state.ah_uploaded = True
                #         st.rerun()
                # ------------------------------------- 무한로딩 -------------------------------------

            st.write(f"{st.session_state.ah_result}점")
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 두 번째 행 - 퍼 반복하기 (파일 업로더 포함)
        st.markdown('<div class="table-row">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([3, 3, 2])
        with col1:
            st.markdown('<div class="table-cell" style="border-right: 1px solid #ddd;">\'퍼\' 반복하기</div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="table-cell" style="border-right: 1px solid #ddd;">평균 횟수 {pa_avg}번</div>', unsafe_allow_html=True)
        with col3:
            st.markdown('<div class="table-cell">', unsafe_allow_html=True)
            if not st.session_state.pa_uploaded:
                with st.container():
                    st.markdown('<div class="small-uploader">', unsafe_allow_html=True)
                    pa_sound_inline = st.file_uploader("", type=['wav', 'mp3'], key="pa_inline", label_visibility="collapsed")
                    st.markdown('</div>', unsafe_allow_html=True)
                if pa_sound_inline is not None:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                        tmp_file.write(pa_sound_inline.getvalue())
                        file_path = tmp_file.name
                        st.session_state.pa_result = ptk.count_peaks_from_waveform(file_path)
                        st.session_state.pa_uploaded = True
                        st.rerun()
            st.write(f"{st.session_state.pa_result}점")
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 세 번째 행 - 터 반복하기 (파일 업로더 포함)
        st.markdown('<div class="table-row">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([3, 3, 2])
        with col1:
            st.markdown('<div class="table-cell" style="border-right: 1px solid #ddd;">\'터\' 반복하기</div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="table-cell" style="border-right: 1px solid #ddd;">평균 횟수 {ta_avg}번</div>', unsafe_allow_html=True)
        with col3:
            st.markdown('<div class="table-cell">', unsafe_allow_html=True)
            if not st.session_state.ta_uploaded:
                with st.container():
                    st.markdown('<div class="small-uploader">', unsafe_allow_html=True)
                    ta_sound_inline = st.file_uploader("", type=['wav', 'mp3'], key="ta_inline", label_visibility="collapsed")
                    st.markdown('</div>', unsafe_allow_html=True)
                if ta_sound_inline is not None:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                        tmp_file.write(ta_sound_inline.getvalue())
                        file_path = tmp_file.name
                        st.session_state.ta_result = ptk.count_peaks_from_waveform(file_path)
                        st.session_state.ta_uploaded = True
                        st.rerun()
            st.write(f"{st.session_state.ta_result}점")
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 네 번째 행 - 커 반복하기 (파일 업로더 포함)
        st.markdown('<div class="table-row">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([3, 3, 2])
        with col1:
            st.markdown('<div class="table-cell" style="border-right: 1px solid #ddd;">\'커\' 반복하기</div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="table-cell" style="border-right: 1px solid #ddd;">평균 횟수 {ka_avg}번</div>', unsafe_allow_html=True)
        with col3:
            st.markdown('<div class="table-cell">', unsafe_allow_html=True)
            if not st.session_state.ka_uploaded:
                with st.container():
                    st.markdown('<div class="small-uploader">', unsafe_allow_html=True)
                    ka_sound_inline = st.file_uploader("", type=['wav', 'mp3'], key="ka_inline", label_visibility="collapsed")
                    st.markdown('</div>', unsafe_allow_html=True)
                if ka_sound_inline is not None:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                        tmp_file.write(ka_sound_inline.getvalue())
                        file_path = tmp_file.name
                        st.session_state.ka_result = ptk.count_peaks_from_waveform(file_path)
                        st.session_state.ka_uploaded = True
                        st.rerun()
            st.write(f"{st.session_state.ka_result}점")
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 다섯 번째 행 - 퍼터커 반복하기 (파일 업로더 포함)
        st.markdown('<div class="table-row">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([3, 3, 2])
        with col1:
            st.markdown('<div class="table-cell" style="border-right: 1px solid #ddd;">\'퍼터커\' 반복하기</div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="table-cell" style="border-right: 1px solid #ddd;">평균 횟수 {ptk_avg}번</div>', unsafe_allow_html=True)
        with col3:
            st.markdown('<div class="table-cell">', unsafe_allow_html=True)
            if not st.session_state.ptk_uploaded:
                with st.container():
                    st.markdown('<div class="small-uploader">', unsafe_allow_html=True)
                    ptk_sound_inline = st.file_uploader("", type=['wav', 'mp3'], key="ptk_inline", label_visibility="collapsed")
                    st.markdown('</div>', unsafe_allow_html=True)
                if ptk_sound_inline is not None:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                        tmp_file.write(ptk_sound_inline.getvalue())
                        file_path = tmp_file.name
                        st.session_state.ptk_result = ptk.count_peaks_from_waveform(file_path)
                        st.session_state.ptk_uploaded = True
                        st.rerun()
            st.write(f"{st.session_state.ptk_result}점")
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 나머지 행들(더미데이터)
        st.markdown('<div class="table-row">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([3, 3, 2])
        with col1:
            st.markdown('<div class="table-cell" style="border-right: 1px solid #ddd;">또박또박 말하기 (단어수준)</div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="table-cell" style="border-right: 1px solid #ddd;">자음 정확도: {consonant_word}%<br>모음 정확도: {vowel_word}%</div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="table-cell">{word_level}점</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="table-row">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([3, 3, 2])
        with col1:
            st.markdown('<div class="table-cell" style="border-right: 1px solid #ddd;">또박또박 말하기 (문장수준)</div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="table-cell" style="border-right: 1px solid #ddd;">자음 정확도: {consonant_sentence}%</div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="table-cell">{sentence_level}점</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 합계 행
        st.markdown('<div class="total-row">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([3, 3, 2])
        with col1:
            st.markdown('<div class="table-cell" style="border-right: 1px solid #ddd;"><strong>합계</strong></div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="table-cell" style="border-right: 1px solid #ddd;"></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="table-cell"><strong>{total_score}점</strong></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)  # table-container 닫기

        # 평가 리스트
        a_sound, pa_sound, ta_sound, ka_sound, ptk_sound = evaluation_data
        
        evaluation_list = [a_sound, pa_sound, ta_sound, ka_sound, ptk_sound]

        # for문으로 각 평가 테이블 생성
        for eval_item in evaluation_list:
            html_content = create_evaluation_table_html(eval_item)
            # st.components.v1.html 사용 - 높이는 항목 수에 따라 동적으로 계산
            height = 150 + (len(eval_item['items']) * 35)  # 기본 높이 + 각 행당 35px
            components.html(html_content, height=height)

        # 또박또박: 잠시 삭제, 수정필요
        # st.subheader("또박또박 말하기")
        # word_table_html = create_word_level_table()
        # st.markdown(word_table_html, unsafe_allow_html=True)
        
        # 문장수준 표
        # st.subheader("또박또박 읽기")
        # sentence_table_html = create_sentence_level_table(sentence_level_data)
        # st.markdown(sentence_table_html, unsafe_allow_html=True)
        

if __name__ == "__main__":
    main()
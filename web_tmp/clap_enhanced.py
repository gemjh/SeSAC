import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit.components.v1 as components

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
    background-color: #e6e6e6;
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





# -----------------------------------------평가 데이터 정의(임시)--------------------------------------------
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
word_level_data = [
    {'no': '연습', 'word': '모자', 'initial': 'ㅁ', 'medial': 'ㅗ', 'final': '', 'medial2': '', 'result': '', 'score': ''},
    {'no': '1', 'word': '나비', 'initial': 'ㄴ', 'medial': 'ㅏ', 'final': '', 'medial2': 'ㅣ', 'result': '나비', 'score': '0'},
    {'no': '2', 'word': '포도', 'initial': 'ㅍ', 'medial': 'ㅗ', 'final': 'ㄷ', 'medial2': 'ㅗ', 'result': '모도', 'score': '0'},
    {'no': '3', 'word': '방울', 'initial': '', 'medial': '', 'final': 'ㅌ', 'medial2': '', 'result': '', 'score': ''},
    {'no': '4', 'word': '수갑', 'initial': 'ㅅ', 'medial': '', 'final': 'ㅂ', 'medial2': '', 'result': '나비', 'score': ''},
    {'no': '5', 'word': '가위', 'initial': 'ㄱ', 'medial': '', 'final': '', 'medial2': 'ㅟ', 'result': '', 'score': ''},
]

sentence_level_data = [
    {'no': '1', 'sentence': ['우리나라의 봄은 신그럽다.','집식은 뽀뽀 지치고, 푸른 새싹은 끊움을 띠어낸다.'], 
     'phonemes': [
         {'sound': 'ㅅ', 'count': '3'},
         {'sound': 'ㅆ', 'count': '2'},
         {'sound': 'ㅈ', 'count': '2'},
         {'sound': 'ㅉ', 'count': '2'},
         {'sound': 'ㅊ', 'count': '1'},
         {'sound': 'ㄹ', 'count': '6'},
         {'sound': 'ㅅ', 'count': '1'}
     ],'score':100},
    {'no': '2', 'sentence': ['아이들이 수영장에서 물놀이를 하고 있다.','환영장의 물장구를 치며 청년시고 있다.'],
     'phonemes': [
         {'sound': 'ㅈ', 'count': '3'},
         {'sound': 'ㅊ', 'count': '4'},
         {'sound': 'ㄹ', 'count': '8'}
     ],'score':100}
]

# ----------------------------------------- 추후 상기 데이터 삭제 요망 -----------------------------------------






# 리포트 조회 함수
def get_reports(patient_id, test_type=None):
    patient_id='01258472'
    data = [
        {'ID': 1, 'patient_id': patient_id, 'name': '박충북', 'age': 65, 'gender': '남', 
         '검사유형': 'CLAP-D', '검사일자': '2024.10.16', '의뢰인': '충북대병원(RM) / 공현호', '검사자': '백동재'},
        {'ID': 2, 'patient_id': patient_id, 'name': '박충북', 'age': 65, 'gender': '남', 
         '검사유형': 'CLAP-A', '검사일자': '2024.10.15', '의뢰인': '충북대병원(RM) / 공현호', '검사자': '백동재'}
    ]
    
    df = pd.DataFrame(data)
    
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
        if st.button("CLAP-A", type="primary" if st.session_state.selected_filter == "CLAP-A" else "secondary"):
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

            temp()



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

def temp():
    # -----------------------------임시------------------------------------------------
    # 테스트 항목 정의 (순서, 그룹화 정보 포함)
    test_items = [
        {
            'key': 'ox_choice',
            'name': 'O/X 고르기 (15)',
            'aphasia_group': 'listening',
            'aphasia_name': '알아듣기',
            'group_size': 3,
            'is_first_in_group': True
        },
        {
            'key': 'object_find',
            'name': '사물 찾기 (6)',
            'aphasia_group': 'listening',
            'group_size': 3,
            'is_first_in_group': False
        },
        {
            'key': 'picture_choice',
            'name': '그림 고르기 (6)',
            'aphasia_group': 'listening',
            'group_size': 3,
            'is_first_in_group': False
        },
        {
            'key': 'repeat_speaking',
            'name': '듣고 따라 말하기 (10)',
            'aphasia_group': 'repeating',
            'aphasia_name': '따라 말하기',
            'group_size': 1,
            'is_first_in_group': True
        },
        {
            'key': 'word_chain',
            'name': '끝말 맞추기 (5)',
            'aphasia_group': 'naming',
            'aphasia_name': '이름대기 및<br>날말찾기',
            'group_size': 2,
            'is_first_in_group': True
        },
        {
            'key': 'object_naming',
            'name': '물건 이름 말하기 (10)',
            'aphasia_group': 'naming',
            'group_size': 2,
            'is_first_in_group': False
        },
        {
            'key': 'animal_naming',
            'name': '동물 이름 말하기 (1)',
            'aphasia_group': 'speaking',
            'aphasia_name': '스스로 말하기',
            'group_size': 2,
            'is_first_in_group': True
        },
        {
            'key': 'picture_story',
            'name': '그림 보고 이야기 하기 (NN)',
            'aphasia_group': 'speaking',
            'group_size': 2,
            'is_first_in_group': False
        }
    ]
    test_results={
        'ox_choice': {'correct': 12, 'score': 12},
        'object_find': {'correct': 5, 'score': 5},
        'picture_choice': {'correct': 6, 'score': 6},
        'repeat_speaking': {'correct': 8, 'score': 8},
        'word_chain': {'correct': 4, 'score': 4},
        'object_naming': {'correct': 9, 'score': 9},
        'animal_naming': {'correct': 1, 'score': 1},
        'picture_story': {'correct': 0, 'score': 85},
        'aphasia_scores': {
            'listening': 23,
            'repeating': 8,
            'naming': 13,
            'speaking': 86,
            'total': 130
        }}
    html_parts = []
    html_parts.append('<table class="custom-table">')
    html_parts.append('<thead>')
    html_parts.append('<tr>')
    html_parts.append('<th>문항 (개수)</th>')
    html_parts.append('<th colspan="2">결과</th>')
    html_parts.append('<th colspan="2">실어증 점수</th>')
    html_parts.append('</tr>')
    html_parts.append('<tr>')
    html_parts.append('<th></th>')
    html_parts.append('<th>정답 수</th>')
    html_parts.append('<th>점수</th>')
    html_parts.append('<th></th>')
    html_parts.append('<th></th>')
    html_parts.append('</tr>')
    html_parts.append('</thead>')
    html_parts.append('<tbody>')
    
    # 각 테스트 항목 행 생성
    for item in test_items:
        key = item['key']
        name = item['name']
        
        # 결과 데이터 가져오기
        if key in test_results:
            correct = test_results[key]['correct']
            score = test_results[key]['score']
            
            # 점수 표시 형식 결정 (일부 항목은 점수, 일부는 개수)
            if key in ['repeat_speaking', 'picture_story']:
                score_text = f"{score}점"
            else:
                score_text = f"{score}개"
                
            correct_text = f"{correct}개"
        else:
            correct_text = "NN개"
            score_text = "NN개" if key not in ['repeat_speaking', 'picture_story'] else "NN점"
        
        html_parts.append('<tr>')
        html_parts.append(f'<td class="category-cell">{name}</td>')
        html_parts.append(f'<td>{correct_text}</td>')
        html_parts.append(f'<td>{score_text}</td>')
        
        # 실어증 점수 셀 추가
        if item['is_first_in_group']:
            group_size = item['group_size']
            aphasia_name = item['aphasia_name']
            aphasia_group = item['aphasia_group']
            
            if 'aphasia_scores' in test_results and aphasia_group in test_results['aphasia_scores']:
                aphasia_score = test_results['aphasia_scores'][aphasia_group]
                aphasia_score_text = f"{aphasia_score}점"
            else:
                aphasia_score_text = "NN점"
            
            html_parts.append(f'<td rowspan="{group_size}" class="aphasia-category">{aphasia_name}</td>')
            html_parts.append(f'<td rowspan="{group_size}" class="aphasia-category">{aphasia_score_text}</td>')
        
        html_parts.append('</tr>')
    
    # 합계 행
    if 'aphasia_scores' in test_results and 'total' in test_results['aphasia_scores']:
        total_score = test_results['aphasia_scores']['total']
        total_score_text = f"{total_score}점"
    else:
        total_score_text = "NN점"

# --------------------------------------------------------------------------------------------------------
    return html_parts



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
    
    # 검사 결과
    if not clap_d_data.empty:
        st.subheader("결과 요약")
        a_sound, pa_sound, ta_sound, ka_sound, ptk_sound=100,100,100,100,100
        pa_repeat,ta_repeat,ka_repeat,ptk_repeat,word_level,sentence_level,consonant_word,vowel_word,consonant_sentence=100,100,100,100,100,100,100,100,100
        if True:
            max_time,pa_avg,ta_avg,ka_avg,ptk_avg=10,1,1,1,1
            total_score = a_sound + pa_repeat + ta_repeat + ka_repeat + ptk_repeat + word_level + sentence_level
            
            # 계산된 결과를 표로 표시
            result_html = f"""
            <div style="margin-top: 20px;">
            <table class="pronunciation-table">
                <thead>
                    <tr>
                        <th>문항</th>
                        <th>수행 결과</th>
                        <th>점수</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td class="category-cell">'아' 소리내기</td>
                        <td>최대 발성시간 {max_time}초</td>
                        <td>{a_sound}점</td>
                    </tr>
                    <tr>
                        <td class="category-cell">'퍼' 반복하기</td>
                        <td>평균 횟수 {pa_avg}번</td>
                        <td>{pa_repeat}점</td>
                    </tr>
                    <tr>
                        <td class="category-cell">'터' 반복하기</td>
                        <td>평균 횟수 {ta_avg}번</td>
                        <td>{ta_repeat}점</td>
                    </tr>
                    <tr>
                        <td class="category-cell">'커' 반복하기</td>
                        <td>평균 횟수 {ka_avg}번</td>
                        <td>{ka_repeat}점</td>
                    </tr>
                    <tr>
                        <td class="category-cell">'퍼터커' 반복하기</td>
                        <td>평균 횟수 {ptk_avg}번</td>
                        <td>{ptk_repeat}점</td>
                    </tr>
                    <tr>
                        <td rowspan="2" class="category-cell">또박또박 말하기 (단어수준)</td>
                        <td class="sub-category">자음 정확도: {consonant_word}%</td>
                        <td rowspan="2">{word_level}점</td>
                    </tr>
                    <tr>
                        <td class="sub-category">모음 정확도: {vowel_word}%</td>
                    </tr>
                    <tr>
                        <td class="category-cell">또박또박 말하기 (문장수준)</td>
                        <td>자음 정확도: {consonant_sentence}%</td>
                        <td>{sentence_level}점</td>
                    </tr>
                    <tr class="total-row">
                        <td><strong>합계</strong></td>
                        <td></td>
                        <td><strong>{total_score}점</strong></td>
                    </tr>
                </tbody>
            </table>
            </div>
            """
            
            st.markdown(result_html, unsafe_allow_html=True)

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
import streamlit as st

# CSS 스타일 정의
CSS_STYLES = """
<style>
/* 전체 앱 및 헤더 배경 */
.stApp{
    background: linear-gradient(135deg, #1e90ff, #00bfff);  
    color: white;
}
h1, h2, h3 {
    color: white;
}

/* 헤더 배경 제거 */
header[data-testid="stHeader"] {
    background: transparent !important;
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
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
    margin: 0 !important;
    padding: 0 !important;
    width: fit-content !important;
    min-width: 200px !important;
}
section.stSidebar {
    background: linear-gradient(135deg, #1e90ff, #00bfff) !important;
    width: fit-content !important;
    min-width: 200px !important;
    padding: 0 !important;
    margin: 0 !important;
}
section[data-testid="stSidebar"] > div {
    display: flex !important;
    flex-direction: column !important;
    height: 100% !important;
    position: relative !important;
}

/* Streamlit 버튼 기본 스타일 */
.stButton > button {
    background: rgba(255, 255, 255, 0.2);
    border: none !important;
    color: white !important;
    padding: 10px 20px !important;
    border-radius: 25px !important;
    font: inherit !important;
    cursor: pointer !important;
    font-size: 14px !important;
    transition: all 0.2s !important;
    min-width: 120px !important;
    max-width: 200px !important;
    width: auto !important;
    white-space: nowrap !important;
    text-align: left;
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

/* Primary 버튼 - 기본 스타일 */
.stButton > button[data-testid="baseButton-primary"] {
    background: rgba(255, 255, 255, 0.3) !important;
    color: white !important;
    font-weight: bold !important;
}

.stButton > button[data-testid="baseButton-primary"]:hover {
    background: rgba(255, 255, 255, 0.4) !important;
    color: white !important;
}

.stButton > button[data-testid="baseButton-primary"]:focus {
    background: rgba(255, 255, 255, 0.3) !important;
    color: white !important;
    outline: none !important;
    box-shadow: none !important;
}

.stButton > button[data-testid="baseButton-primary"]:active {
    background: rgba(255, 255, 255, 0.4) !important;
    color: white !important;
}

/* CLAP 버튼 스타일 - key 기반 정확한 선택자 */
.st-key-clap_a_btn button,
.st-key-clap_d_btn button,
.st-key-clap_a_btn .stButton > button,
.st-key-clap_d_btn .stButton > button {
    background: rgba(255, 255, 255, 0.4) !important;
    color: #1e90ff !important;
    height: 50px !important;
    margin-bottom: 10px !important;
    width: 80px !important;
    max-width: 80px !important;
    min-width: 80px !important;
}

.st-key-clap_a_btn button:hover,
.st-key-clap_d_btn button:hover,
.st-key-clap_a_btn .stButton > button:hover,
.st-key-clap_d_btn .stButton > button:hover {
    background: rgba(255, 255, 255, 0.9) !important;
    color: #1e90ff !important;
}

/* Primary 상태 */
.st-key-clap_a_btn button[kind="primary"],
.st-key-clap_d_btn button[kind="primary"] {
    background: white !important;
    color: #1e90ff !important;
    font-weight: bold !important;
}

/* Secondary 상태 - 명시적으로 설정 */
.st-key-clap_a_btn button[kind="secondary"],
.st-key-clap_d_btn button[kind="secondary"] {
    background: rgba(255, 255, 255, 0.4) !important;
    color: #1e90ff !important;
}

.st-key-clap_a_btn button[data-testid="baseButton-primary"]:hover,
.st-key-clap_d_btn button[data-testid="baseButton-primary"]:hover,
.st-key-clap_a_btn .stButton > button[data-testid="baseButton-primary"]:hover,
.st-key-clap_d_btn .stButton > button[data-testid="baseButton-primary"]:hover {
    background: white !important;
    color: #1e90ff !important;
}

/* CLAP 버튼 컨테이너 간격 조정 */
.st-key-clap_a_btn,
.st-key-clap_d_btn {
    margin-right: 15px !important;
    margin-bottom: 10px !important;
}

/* CLAP 버튼 컨테이너 높이 조절 */
div[data-testid="column"]:nth-child(1),
div[data-testid="column"]:nth-child(2) {
    min-height: 70px !important;
    padding-bottom: 10px !important;
    padding-right: 10px !important;
}

/* 로그인 버튼 */
.stFormSubmitButton > button {
    color: #ff4b4b !important;
}

/* 버튼들이 겹치면 줄바꿈 */
.stColumns {
    flex-wrap: wrap !important;
}

.stColumns > div[data-testid="column"] {
    flex-shrink: 0 !important;
    min-width: fit-content !important;
}

/* 버튼 컨테이너 */
.stButton {
    display: inline-block !important;
    margin-right: 10px !important;
    margin-bottom: 5px !important;
}

.stButton:last-child {
    margin-right: 0px !important;
}

/* 파일 업로더 스타일 */
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

/* 테이블 관련 스타일 */
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
.table-container [data-testid="column"] {
    border-right: 1px solid #ddd !important;
}
.table-container [data-testid="column"]:last-child {
    border-right: none !important;
}

/* 업로드 버튼 스타일 */
.st-key-upload_btn {
    text-align: left;
}

/* HTML 테이블용 스타일 */
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
.assessment-table .category-cell {
    background-color: #f8f8f8;
    font-weight: bold;
    text-align: left;
    padding-left: 15px;
}
</style>
"""

def apply_custom_css():
    """CSS 스타일을 적용하는 함수"""
    st.markdown(CSS_STYLES, unsafe_allow_html=True)


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
        }
        
        function showGraph(evalId, itemIndex) {
            alert('📊 ' + evalId + ' - ' + itemIndex + '번째 항목의 그래프를 표시합니다!');
        }
        </script>
    </body>
    </html>
    """
    
    return html_content

def create_word_level_table(word_level_data=None):
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
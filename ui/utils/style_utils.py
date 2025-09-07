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

/* 결과 요약 테이블 */
.main-table {
    border-collapse: collapse;
    width: 100%;
    margin: 20px 0;
}
.main-table th, .main-table td {
    border: 1px solid #ddd;
    padding: 12px;
    text-align: center;
    vertical-align: middle;
    color: black !important;
}
.main-table th {
    background-color: #d8ebff;
    font-weight: bold;
    color: #333;
}
.header-row {
    background-color: #d4edda;
    font-weight: bold;
}
.total-row {
    background-color: #d8ebff;
    font-weight: bold;
}
.category-section {
    background-color: #f8f9fa;
    padding: 15px;
    margin: 10px 0;
    border-radius: 5px;
    border: 1px solid #dee2e6;
}
.category-header {
    background-color: #d8ebff;
    padding: 8px;
    margin-bottom: 10px;
    border-radius: 3px;
    font-weight: bold;
    text-align: center;
}

/* 사이드바 접기 버튼 완전히 숨기기 - 더 강력한 선택자 */
[data-testid="collapsedControl"] {
    display: none !important;
    visibility: hidden !important;
    opacity: 0 !important;
    pointer-events: none !important;
}

button[kind="header"],
button[title="Close sidebar"],
button[aria-label="Close sidebar"],
.css-1rs6os .css-17ziqus,
.css-1rs6os .edgvbvh9,
.css-vk3wp9,
.css-17ziqus {
    display: none !important;
    visibility: hidden !important;
    opacity: 0 !important;
}

/* 사이드바 접기/펼치기 버튼 모두 제거 */
div[data-testid="stSidebarNav"] button {
    display: none !important;
}

/* 사이드바 고정 */
section[data-testid="stSidebar"] {
    min-width: 200px !important;
    width: 200px !important;
}

/* CLAP 리포트 전용 스타일 */
.clap-report {
    background: white;
    color: black;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.clap-header {
    background: linear-gradient(135deg, #2E8B57, #20B2AA);
    color: white;
    text-align: center;
    padding: 20px;
    margin: -20px -20px 30px -20px;
    border-radius: 0;
}

.clap-title {
    font-size: 36px;
    font-weight: bold;
    margin: 0;
    letter-spacing: 2px;
}

.clap-subtitle {
    font-size: 16px;
    margin: 5px 0 0 0;
    font-weight: normal;
}

.clap-institute {
    font-size: 12px;
    margin: 10px 0 0 0;
    text-align: right;
}

.patient-info-grid {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 20px;
    margin: 30px 0;
    background: #f8f9fa;
    padding: 20px;
    border-radius: 8px;
    border: 1px solid #dee2e6;
}

.patient-info-item {
    display: flex;
    justify-content: space-between;
    padding: 8px 0;
    border-bottom: 1px dotted #ccc;
}

.patient-info-label {
    font-weight: bold;
    color: #333;
    font-size: 14px;
}

.patient-info-value {
    color: #666;
    font-size: 14px;
}

.results-section {
    margin: 40px 0;
}

.results-title {
    font-size: 20px;
    font-weight: bold;
    color: #333;
    margin: 0 0 20px 0;
    text-align: center;
    padding: 15px;
    background: #f0f0f0;
    border-radius: 5px;
}

.clap-results-table {
    width: 100%;
    border-collapse: collapse;
    margin: 20px 0;
    font-size: 14px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.clap-results-table th {
    background: linear-gradient(135deg, #2E8B57, #20B2AA);
    color: white;
    font-weight: bold;
    padding: 15px 12px;
    text-align: center;
    border: 1px solid #fff;
    font-size: 14px;
}

.clap-results-table td {
    padding: 12px;
    text-align: center;
    border: 1px solid #ddd;
    background: #fff;
    color: #333;
    font-size: 14px;
    vertical-align: middle;
}

.clap-results-table tbody tr:nth-child(even) {
    background: #f8f9fa;
}

.clap-results-table tbody tr:hover {
    background: #e3f2fd;
}

.test-item-column {
    text-align: left !important;
    font-weight: 500;
    background: #f5f5f5 !important;
    padding-left: 20px !important;
}

.score-column {
    font-weight: bold;
    color: #2E8B57;
    font-size: 16px;
}

.category-header-row th {
    background: linear-gradient(135deg, #4CAF50, #45a049) !important;
    color: white !important;
    font-size: 15px;
    text-align: center;
}

.total-row td {
    background: linear-gradient(135deg, #FF6B6B, #FF8E8E) !important;
    color: white !important;
    font-weight: bold;
    font-size: 16px;
}

.percentage-display {
    font-size: 14px;
    color: #666;
    font-style: italic;
}

.back-button {
    background: #6c757d;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 5px;
    margin: 20px 0;
    cursor: pointer;
}

.back-button:hover {
    background: #5a6268;
}
</style>
"""

def apply_custom_css():
    """CSS 스타일을 적용하는 함수"""
    st.markdown(CSS_STYLES, unsafe_allow_html=True)


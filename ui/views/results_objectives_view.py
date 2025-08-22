import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
from services.db_service import get_db_modules

def show_results_objectives_view():
    """결과 요약 화면을 표시하는 함수"""
    
    st.header("결과 요약")
    st.subheader("전산화 언어 기능 선별 검사 결과지")
    
    # 환자 정보 섹션
    model_comm, report_main = get_db_modules()
    
    # 세션 상태에서 환자 정보 가져오기
    if 'selected_report' in st.session_state:
        msg, patient_detail = report_main.get_patient_info(
            st.session_state.selected_report['patient_id'],
            st.session_state.selected_report['order_num']
        )
        patient_name = patient_detail['PATIENT_NAME'][0] if patient_detail is not None and len(patient_detail) > 0 else "환자명"
        patient_age = patient_detail['AGE'][0] if patient_detail is not None and len(patient_detail) > 0 else 0
    else:
        patient_name = "환자명"
        patient_age = 0
    
    # 결과 및 목표 데이터 생성
    results_objectives_data = create_results_objectives_data()
    
    # 메인 컨테이너
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # 결과 요약 테이블
        show_results_summary_table(results_objectives_data)
        
        # 실어증 중증도 섹션
        show_severity_section()
        
    with col2:
        # 실어증 유형 차트
        show_aphasia_type_chart()
        
        # 실어증 유형 요약
        show_aphasia_summary()

def create_results_objectives_data():
    """결과 및 목표 데이터를 생성하는 함수"""
    
    # 세션 상태에서 모델링 결과 가져오기
    if 'talk_pic_result' in st.session_state:
        talk_pic_score = round(st.session_state.talk_pic_result, 1) if st.session_state.talk_pic_result else 0
    else:
        talk_pic_score = 0
        
    if 'say_ani_result' in st.session_state:
        say_ani_score = round(st.session_state.say_ani_result, 1) if st.session_state.say_ani_result else 0
    else:
        say_ani_score = 0
        
    if 'say_obj_result' in st.session_state:
        say_obj_score = round(st.session_state.say_obj_result, 1) if st.session_state.say_obj_result else 0
    else:
        say_obj_score = 0
        
    if 'ltn_rpt_result' in st.session_state:
        ltn_rpt_score = round(st.session_state.ltn_rpt_result, 1) if st.session_state.ltn_rpt_result else 0
    else:
        ltn_rpt_score = 0
        
    if 'guess_end_result' in st.session_state:
        guess_end_score = sum(st.session_state.guess_end_result) if st.session_state.guess_end_result else 0
    else:
        guess_end_score = 0
    
    return {
        'results': [
            {'task': 'O/X 고르기 (15)', 'current': 'NN개', 'max_score': 'NN개', 'real_score': 0},
            {'task': '사물 찾기 (6)', 'current': 'NN개', 'max_score': 'NN개', 'real_score': 0},
            {'task': '그림 고르기 (6)', 'current': 'NN개', 'max_score': 'NN개', 'real_score': 0},
            {'task': '듣고 따라 말하기 (10)', 'current': f'{ltn_rpt_score}점', 'max_score': 'NN점', 'real_score': ltn_rpt_score},
            {'task': '끝말 맞추기 (5)', 'current': f'{guess_end_score}점', 'max_score': 'NN점', 'real_score': guess_end_score},
            {'task': '물건 이름 말하기 (10)', 'current': f'{say_obj_score}점', 'max_score': 'NN점', 'real_score': say_obj_score},
            {'task': '동물 이름 말하기 (1)', 'current': f'{say_ani_score}점', 'max_score': 'NN점', 'real_score': say_ani_score},
            {'task': '그림 보고 이야기 하기 (NN)', 'current': f'{talk_pic_score}점', 'max_score': 'NN점', 'real_score': talk_pic_score},
            {'task': '합계', 'current': 'NN점', 'max_score': 'NN점', 'real_score': 0}
        ],
        'severity': {'level': '실어증 중증도', 'description': '실어증 유형'},
        'chart_data': {
            'categories': ['그림보고\n이야기하기', '동물\n이름말하기', '그림\n고르기', '듣고\n따라말하기', '물건\n이름말하기', '이름\n말하기', '듣고 따라\n말하기', '끝말\n맞추기'],
            'current_scores': [talk_pic_score, say_ani_score, 0, ltn_rpt_score, say_obj_score, 0, ltn_rpt_score, guess_end_score],
            'target_scores': [100, 100, 100, 100, 100, 100, 100, 100]
        }
    }

def show_results_summary_table(data):
    """결과 요약 테이블을 표시하는 함수"""
    
    st.markdown("### 결과 요약")
    
    # 테이블 HTML 생성
    table_html = """
    <style>
    .results-table {
        width: 100%;
        border-collapse: collapse;
        font-family: 'Noto Sans KR', sans-serif;
        margin: 20px 0;
    }
    .results-table th, .results-table td {
        border: 1px solid #ddd;
        padding: 8px;
        text-align: center;
    }
    .results-table th {
        background-color: #f5f5f5;
        font-weight: bold;
    }
    .results-table tr:nth-child(even) {
        background-color: #f9f9f9;
    }
    .task-name {
        text-align: left !important;
        padding-left: 12px !important;
    }
    .total-row {
        background-color: #e8f4f8 !important;
        font-weight: bold;
    }
    </style>
    
    <table class="results-table">
        <thead>
            <tr>
                <th style="width: 40%">문항 (개수)</th>
                <th style="width: 20%">정답 수</th>
                <th style="width: 20%">점수</th>
                <th style="width: 20%">실어증 점수</th>
            </tr>
        </thead>
        <tbody>
    """
    
    for i, item in enumerate(data['results']):
        row_class = "total-row" if item['task'] == '합계' else ""
        table_html += f"""
            <tr class="{row_class}">
                <td class="task-name">{item['task']}</td>
                <td>{item['current']}</td>
                <td>{item['max_score']}</td>
                <td>NN점</td>
            </tr>
        """
    
    table_html += """
        </tbody>
    </table>
    """
    
    st.markdown(table_html, unsafe_allow_html=True)

def show_severity_section():
    """실어증 중증도 섹션을 표시하는 함수"""
    
    st.markdown("### 실어증 중증도")
    
    # 중증도 HTML
    severity_html = """
    <div style="background-color: #f0f8ff; padding: 15px; border-radius: 8px; margin: 10px 0;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="flex: 1; text-align: center;">
                <div style="font-size: 14px; color: #666;">문항별 점수</div>
            </div>
            <div style="flex: 1; text-align: center;">
                <div style="font-size: 14px; color: #666;">실어증 점수</div>
            </div>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 10px;">
            <div style="flex: 1; text-align: center;">
                <div style="font-size: 24px; font-weight: bold; color: #333;">NN점</div>
            </div>
            <div style="flex: 1; text-align: center;">
                <div style="font-size: 24px; font-weight: bold; color: #333;">NN점</div>
            </div>
        </div>
    </div>
    """
    
    st.markdown(severity_html, unsafe_allow_html=True)

def show_aphasia_type_chart():
    """실어증 유형 차트를 표시하는 함수"""
    
    st.markdown("### 실어증 유형")
    
    # 차트 데이터 생성
    data = create_results_objectives_data()
    
    # 레이더 차트 생성
    categories = data['chart_data']['categories']
    current_scores = data['chart_data']['current_scores']
    target_scores = data['chart_data']['target_scores']
    
    # 각도 계산 (8각형)
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    angles += angles[:1]  # 원을 닫기 위해 첫 번째 점 추가
    
    current_scores += current_scores[:1]
    target_scores += target_scores[:1]
    categories += categories[:1]
    
    fig = go.Figure()
    
    # 목표 점수 (외곽선)
    fig.add_trace(go.Scatterpolar(
        r=target_scores,
        theta=categories,
        fill=None,
        line=dict(color='lightblue', width=2, dash='dash'),
        name='이전 검사',
        showlegend=True
    ))
    
    # 현재 점수 (채워진 영역)
    fig.add_trace(go.Scatterpolar(
        r=current_scores,
        theta=categories,
        fill='toself',
        fillcolor='rgba(135, 206, 250, 0.3)',
        line=dict(color='blue', width=2),
        name='현재 검사',
        showlegend=True
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickmode='linear',
                tick0=0,
                dtick=25
            ),
            angularaxis=dict(
                tickfont=dict(size=10)
            )
        ),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        ),
        height=400,
        margin=dict(t=50, b=100, l=50, r=50)
    )
    
    st.plotly_chart(fig, use_container_width=True)

def show_aphasia_summary():
    """실어증 유형 요약을 표시하는 함수"""
    
    st.markdown("### 실어증 유형")
    
    # 요약 박스들
    col1, col2 = st.columns(2)
    
    with col1:
        summary_box_html = """
        <div style="background-color: #f0f8ff; padding: 15px; border-radius: 8px; margin: 10px 0; text-align: center;">
            <div style="font-size: 14px; color: #666; margin-bottom: 5px;">문항별 점수</div>
            <div style="font-size: 18px; font-weight: bold; color: #333;">안아플기</div>
        </div>
        """
        st.markdown(summary_box_html, unsafe_allow_html=True)
    
    with col2:
        summary_box_html = """
        <div style="background-color: #f0f8ff; padding: 15px; border-radius: 8px; margin: 10px 0; text-align: center;">
            <div style="font-size: 14px; color: #666; margin-bottom: 5px;">실어증 유형</div>
            <div style="font-size: 18px; font-weight: bold; color: #333;">따라 말하기</div>
        </div>
        """
        st.markdown(summary_box_html, unsafe_allow_html=True)
    
    # 추가 설명 박스들
    col1, col2 = st.columns(2)
    
    with col1:
        explanation_html = """
        <div style="background-color: #fff8dc; padding: 15px; border-radius: 8px; margin: 10px 0; text-align: center;">
            <div style="font-size: 18px; font-weight: bold; color: #333; margin-bottom: 5px;">스스로 말하기</div>
            <div style="font-size: 14px; color: #666;">NN점</div>
        </div>
        """
        st.markdown(explanation_html, unsafe_allow_html=True)
    
    with col2:
        explanation_html = """
        <div style="background-color: #fff8dc; padding: 15px; border-radius: 8px; margin: 10px 0; text-align: center;">
            <div style="font-size: 18px; font-weight: bold; color: #333; margin-bottom: 5px;">이름대기 및 낱말창착</div>
            <div style="font-size: 14px; color: #666;">NN점</div>
        </div>
        """
        st.markdown(explanation_html, unsafe_allow_html=True)

def show_results_objectives_page():
    """결과 및 목표 페이지의 메인 함수"""
    
    # 뒤로가기 버튼
    # if st.button("< 뒤로가기"):
    #     st.session_state.view_mode = "clap_a_detail" if st.session_state.selected_filter == "CLAP_A" else "clap_d_detail"
    #     st.rerun()
    
    # 메인 컨텐츠
    show_results_objectives_view()
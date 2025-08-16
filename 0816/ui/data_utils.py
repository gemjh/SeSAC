import pandas as pd
import os
import sys

# 0812 폴더 경로를 sys.path에 추가
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(project_root), '0812'))

import db.src.report_main as rmn
import db.src.model_comm as mc

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
    msg,df=rmn.get_assess_lst(patient_id)
    try:
        df.columns=['order_num','patient_id','name','age','sex','검사유형','검사일자','의뢰인','검사자']
    except:
        st.warning("DB 연결돼 있지 않음: 더미 데이터로 대체")
        df=pd.DataFrame(['0','1001','박충북',65,0,'CLAP_D','2025-08-01','충북대병원','김재헌']).T
        df.columns=['order_num','patient_id','name','age','sex','검사유형','검사일자','의뢰인','검사자']

    if test_type and test_type != "전체":
        df = df[df['검사유형'] == test_type]
    return df

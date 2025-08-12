import pandas as pd
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
def get_reports(patient_id=1001, test_type=None):
    base_path = r"/Volumes/SSAM/project/0812/db/data"
    msg, ret = mc.get_file_lst('CLAP_A', 'LTN_RPT', 1)

    wav_label_pairs = []
    for i in range(len(ret)):
        t = (os.path.join(base_path, f"{ret.loc[i, 'Path']}", f"{ret.loc[i, 'File Name']}"), int(ret.loc[i, 'Score(Refer)'])/int(ret.loc[i, 'Score(Alloc)']))
        wav_label_pairs.append(t)

    print(len(wav_label_pairs))
    print(wav_label_pairs[0])

    msg,df=rmn.get_assess_lst(patient_id)
    try:
        df.columns=['patient_id','name','age','gender','검사유형','검사일자','의뢰인','검사자']
    except:
        df=pd.DataFrame(['1001','박충북',65,0,'CLAP_D','2025-08-01','충북대병원','김재헌']).T
        df.columns=['patient_id','name','age','gender','검사유형','검사일자','의뢰인','검사자']

    if test_type and test_type != "전체":
        df = df[df['검사유형'] == test_type]
    return df

# CLAP-A 상세 데이터 조회
def get_clap_a_details(patient_id, test_date):
    data={'':''}
    return pd.DataFrame(data)

# CLAP-D 상세 데이터 조회
def get_clap_d_details(patient_id, test_date):
    data = [        
        {'patient_id':patient_id, 'category': '아 검사', 'result': 100,'date':test_date},
    ]
    return pd.DataFrame(data)
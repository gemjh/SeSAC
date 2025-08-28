import pandas as pd

def get_db_modules():
    from db.src import model_comm, report_main
    return model_comm, report_main

# 리포트 조회 함수
def get_reports(patient_id, test_type=None):
    model_comm, report_main=get_db_modules()
    msg,df=report_main.get_assess_lst(patient_id)
    # print(df)
    try:
        if patient_id is not None:
            df.columns=[
                'ORDER_NUM', 'PATIENT_ID', 'PATIENT_NAME', 'AGE', 'SEX', 'ASSESS_TYPE', 'MAIN_PATH', 'ASSESS_DATE', 'REQUEST_ORG', 'ASSESS_PERSON'
            ]
    except Exception as e:
        print(f"환자 정보 호출 중 오류 발생: {e}")
        

    if test_type and test_type != "전체":
        df = df[df['ASSESS_TYPE'] == test_type]
    return df

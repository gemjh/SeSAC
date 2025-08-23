import pandas as pd
def get_db_modules():
    from db.src import model_comm, report_main
    return model_comm, report_main

# 리포트 조회 함수
def get_reports(patient_id, test_type=None):
    model_comm, report_main=get_db_modules()
    msg,df=report_main.get_report_main(patient_id)
    print(df)
    try:
        if patient_id is not None:
            df.columns=[
                'PATIENT_ID','ORDER_NUM','REQUEST_ORG','ASSESS_DATE',
                'ASSESS_PERSON','ASSESS_TYPE','MAIN_PATH','PATIENT_NAME','SEX','AGE'
            ]
        else:
            df=pd.DataFrame(['1001',1,'충북대','2025-11-14','김재헌','CLAP_D','1001','박충북',0,65]).T
            df.columns=[
                'PATIENT_ID','ORDER_NUM','REQUEST_ORG','ASSESS_DATE',
                'ASSESS_PERSON','ASSESS_TYPE','MAIN_PATH','PATIENT_NAME','SEX','AGE'
            ]
    except Exception as e:
        print(f"환자 정보 호출 중 오류 발생: {e}")
        

    if test_type and test_type != "전체":
        df = df[df['검사유형'] == test_type]
    return df

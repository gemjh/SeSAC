import pandas as pd
def get_db_modules():
    from db.src import model_comm, report_main
    return model_comm, report_main

# 리포트 조회 함수
def get_reports(patient_id, test_type=None):
    model_comm, report_main=get_db_modules()
    msg,df=report_main.get_assess_lst(patient_id)
    print(df)
    try:
        if patient_id is not None:
            df.columns=['order_num','patient_id','name','age','sex','검사유형','검사일자','의뢰인','검사자']
        else:
            df=pd.DataFrame(['0','1001','박충북',65,0,'CLAP_D','2025-08-01','충북대병원','김재헌']).T
            df.columns=['order_num','patient_id','name','age','sex','검사유형','검사일자','의뢰인','검사자']
    except Exception as e:
        print(f"환자 정보 호출 중 오류 발생: {e}")
        

    if test_type and test_type != "전체":
        df = df[df['검사유형'] == test_type]
    return df

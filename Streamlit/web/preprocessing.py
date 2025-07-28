import pandas as pd
df=pd.read_csv('D:\sesac\Streamlit\patient_summary.csv')
print(df)
df.to_csv('patient.csv',index=False,encoding='cp949')
print('완료')
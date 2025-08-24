import pandas as pd
df=pd.read_csv('D:\sesac\Streamlit\patient_summary.csv')
columns={}
for ex,new in zip(df.columns,['name','result','score','suspicion']):
    columns[ex]=new
df=df.rename(columns=columns)
print(df)
df.to_csv('patient.csv',index=False,encoding='cp949')
print('완료')

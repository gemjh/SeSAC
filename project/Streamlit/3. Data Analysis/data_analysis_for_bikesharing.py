"""
Streamlit app for Interactive Data Analysis
"""
import time

import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import seaborn as sns

@st.cache_data
def data_preprocess():
    bike_train = pd.read_csv('./data/bike_train.csv', encoding='utf8')
    df = bike_train.copy()

    df['datetime'] = df.datetime.apply(pd.to_datetime)
    df['year'] = df.datetime.apply(lambda x : x.year)
    df['month'] = df.datetime.apply(lambda x : x.month)
    df['day'] = df.datetime.apply(lambda x : x.day)
    df['hour'] = df.datetime.apply(lambda x : x.hour)
    df['minute'] = df.datetime.apply(lambda x : x.minute)
    df['dayofweek'] = df.datetime.apply(lambda x : x.dayofweek)

    df['season'] = df['season'].map({1 : 'Spring',
                                    2 : 'Summer',
                                    3 : 'Fall',
                                    4 : 'Winter'})

    df['weather'] = df['weather'].map({1 : 'Clear',
                                    2 : 'Mist, Few clouds',
                                    3 : 'Light Snow, Rain, Thunder',
                                    4 : 'Heavy Snow, Rain, Thunder'})
    

    return bike_train, df

begin = time.time()

# --- page
# Note
# This must be the first Streamlit command used on an app page, and must only be set once per page.
st.set_page_config(page_title='Analysis - Bike Sharing Dataset', page_icon=':smile:')

# --- data prepare
bike, bike_preprocessed = data_preprocess()

# --- sidebar
numeric_columns  = ['temp', 'atemp', 'humidity', 'windspeed', 'count']
numeric_column = st.sidebar.selectbox("**데이터 분포** : 기상 정보 및 대여 횟수를 선택하세요", options=numeric_columns)
bins = st.sidebar.slider("bins 를 선택하세요.", 30, 70, 50, 10)
st.sidebar.write("---")

category_columns1 = ['year', 'month', 'dayofweek', 'hour']
category_column1 = st.sidebar.selectbox("**대여율(1)** : 날짜와 시간별 대여율을 선택하세요", options=category_columns1)
st.sidebar.write("---")

category_columns2 = ['workingday', 'holiday', 'season', 'weather']
category_column2 = st.sidebar.selectbox("**대여율(3)** :시간대 외 다른 정보를 선택하세요", options=category_columns2)
st.sidebar.write("---")

numeric_columns2  = ['temp', 'atemp', 'humidity', 'windspeed']
numeric_column2 = st.sidebar.selectbox("**산점도** : 기상 정보를 선택하세요", options=numeric_columns2)
st.sidebar.write("---")


# --- body
st.title("Bike Sharing Dataset Analysis")

tabs = st.tabs(['데이터', '전처리 데이터', '데이터 분포', 
                '대여율(1)', '대여율(2)', 
                '대여율(3)', '사분위 분포',
                '산점도', '상관관계'
                ])
with tabs[0]:
    st.write(f"{bike.shape = }")
    st.dataframe(bike)
    st.write(pd.concat([bike.dtypes, bike.count()], axis=1).T)

with tabs[1]:
    st.write("##### 데이터 탐색을 위해 일부 전처리된 데이터 ")
    st.write(f"{bike_preprocessed.shape = }")
    st.dataframe(bike_preprocessed)
    st.write(pd.concat([bike_preprocessed.dtypes, bike_preprocessed.count()], axis=1).T)

with tabs[2]:
    st.write("##### 기상 정보 및 대여 횟수에 대한 히스토그램 ")
    fig = plt.figure()
    sns.histplot(data=bike_preprocessed, x=numeric_column, bins=bins)
    st.pyplot(fig)

with tabs[3]:
    st.write("##### 날짜와 시간별 대여율")
    fig = plt.figure()
    sns.barplot(data=bike_preprocessed, x=category_column1, y='count')
    st.pyplot(fig)

with tabs[4]:
    st.write("#####  근무/휴일별 시간대 대여율")
    fig = plt.figure()
    sns.pointplot(data=bike_preprocessed, x='hour', y='count', hue='workingday')
    st.pyplot(fig)

with tabs[5]:
    st.write("##### 시간대 외 다른 정보(휴일, 계절, 날씨)별 대여율")
    fig = plt.figure()
    sns.barplot(data=bike_preprocessed, x=category_column2, y='count')
    if (category_column2 == 'season') or (category_column2 == 'weather'):
        plt.xticks(rotation=45) 
    st.pyplot(fig)        

with tabs[6]:
    st.write("##### 시간대 외 다른 정보(휴일, 계절, 날씨)별 사분위 분포")
    fig = plt.figure()
    sns.boxplot(data=bike_preprocessed, x=category_column2, y='count')
    if (category_column2 == 'season') or (category_column2 == 'weather'):
        plt.xticks(rotation=45) 
    st.pyplot(fig)  

with tabs[7]:
    st.write("##### 기상 정보(온도, 체감온도, 습도, 풍속)별 대여 횟수간 산점도")
    fig = plt.figure()
    sns.regplot(data=bike_preprocessed, x=numeric_column2, y='count',
                scatter_kws={'alpha':0.2}, line_kws={'color' : 'blue'})
    st.pyplot(fig)

with tabs[8]:
    st.write("##### 기상 정보(온도, 체감온도, 습도, 풍속)별 대여 횟수간 상관계수")
    fig = plt.figure()
    corr = bike_preprocessed[['temp', 'atemp', 'humidity', 'windspeed', 'count']].corr()    
    sns.heatmap(corr, annot=True, fmt='.2f', linewidths=0.5, cmap='YlGnBu')
    st.pyplot(fig)    

elapsed = time.time() - begin
st.info(f"{elapsed = :.1f} secs")
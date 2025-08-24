"""
Streamlit app for AI Predict
"""
import time
from pathlib import Path

import pandas as pd
import numpy as np
import streamlit as st
# --- page
st.set_page_config(page_title='Predict', page_icon=':heart:')


@st.cache_data
def data_preprocess(csv):
    bike_train = pd.read_csv(csv, encoding='utf8')
    # 이상치 제거
    df = bike_train[bike_train['weather'] != 4]

    # datetime으로부터 파생특성 추가
    df['datetime'] = df.datetime.apply(pd.to_datetime)
    df['year'] = df.datetime.apply(lambda x : x.year)
    df['month'] = df.datetime.apply(lambda x : x.month)
    df['hour'] = df.datetime.apply(lambda x : x.hour)
    # df['dayofweek'] = df.datetime.apply(lambda x : x.dayofweek)

    drop_features = ['casual', 'registered', 'datetime', 'windspeed', 'count']
    df = df.drop(drop_features, axis=1)

    return bike_train, df

@st.cache_resource
def load_ai_pickle(pkl):
    import joblib
    dct = joblib.load(pkl)
    return dct

begin = time.time()

BASE_DIR = Path.cwd()
CSV_FILE = BASE_DIR / 'DATA' / 'bike_train.csv'
PICKLE_NAME = BASE_DIR / 'bikesharing_model.pkl'

# --- data prepare
bike, bike_preprocessed = data_preprocess(CSV_FILE)
dctPickle = load_ai_pickle(PICKLE_NAME)

# --- sidebar
# 기상 정보
temp_min, temp_max, temp_mean = bike_preprocessed.temp.min(), bike_preprocessed.temp.max(), bike_preprocessed.temp.mean()
atemp_min, atemp_max, atemp_mean = bike_preprocessed.atemp.min(), bike_preprocessed.atemp.max(), bike_preprocessed.atemp.mean()
humidity_min, humidity_max, humidity_mean = bike_preprocessed.humidity.min(), bike_preprocessed.humidity.max(), bike_preprocessed.humidity.mean()

# 날짜 시간 정보
year_options = bike_preprocessed.year.unique()
hour_options = bike_preprocessed.hour.unique()
month_options = bike_preprocessed.month.unique()

# 그 외 정보
season_dict = {'Spring' : 1, 'Summer' : 2, 'Fall' : 3, 'Winter' : 4}
holiday_dict = {'Not Holiday' : 0, 'Holiday' : 1}
workingday_dict = {'Not Workingday' : 0 , 'Workingday' : 1}
weather_dict = {'Clear' : 1, 'Mist, Few clouds' : 2, 
                'Light Snow, Rain, Thunder' : 3, 'Heavy Snow, Rain, Thunder' : 4}

# 기상 정보 선택
temp = st.sidebar.slider("Temrature 선택", temp_min, temp_max, temp_mean, 0.1)
atemp = st.sidebar.slider("Apparent Temperature 선택", atemp_min, atemp_max, atemp_mean, 0.1)
humidity = st.sidebar.slider("Humidity 선택", humidity_min, humidity_max, humidity_min, 1)

# 날짜 시간 정보 선택
year = st.sidebar.selectbox("Year 선택", options=year_options)
month = st.sidebar.selectbox("Month 선택", options=month_options)
hour = st.sidebar.selectbox("Hour 선택", options=hour_options)

# 그 외 정보 선택
season = st.sidebar.selectbox("Season 선택", options=season_dict.keys())
holiday = st.sidebar.selectbox("Holiday 선택", options=holiday_dict.keys())
workingday = st.sidebar.selectbox("Workingday 선택", options=workingday_dict.keys())
weather = st.sidebar.selectbox("Weather 선택", options=weather_dict.keys())


# --- body
st.title("Streamlit AI 예측")
st.write("#### 자전거 대여량을 예측합니다.")
st.write("---")

st.write("##### 입력된 데이터")
widgetData = [season, holiday, workingday, weather, temp, atemp, humidity, year, month, hour]
dfWidget = pd.DataFrame(data=[widgetData], columns=bike_preprocessed.columns)
st.write(dfWidget)

#  0   season      10885 non-null  int64  
#  1   holiday     10885 non-null  int64  
#  2   workingday  10885 non-null  int64  
#  3   weather     10885 non-null  int64  
#  4   temp        10885 non-null  float64
#  5   atemp       10885 non-null  float64
#  6   humidity    10885 non-null  int64  
#  7   year        10885 non-null  int64  
#  8   month       10885 non-null  int64  
#  9   hour        10885 non-null  int64  

predictData = [season_dict[season], holiday_dict[holiday], 
               workingday_dict[workingday], weather_dict[weather], 
               temp, atemp, humidity, year, month, hour]
dfPredict = pd.DataFrame(data=[predictData], columns=bike_preprocessed.columns)
"---"

pred = dctPickle.predict(dfPredict)
pred = np.expm1(pred)
st.write('**자전거 대여량**', pred)

"---"

elapsed = time.time() - begin
st.info(f"{elapsed = :.1f} secs")

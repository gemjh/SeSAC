"""
session state 4th example
- session state 도 st.cache_data 처럼, 한번만 실행하는 효과가 있다.
- 그러나 session 은 브라우저당 독립적, cache 는 모든 세션에 공유된다.
- widget 도 session state 와 동일한 특징을 갖는다.
"""
import streamlit as st
import pandas as pd
import numpy as np


@st.cache_data
def get_df():
    print("get_df()...")
    tmp = pd.DataFrame(np.random.randn(20, 2), columns=["x", "y"])
    return tmp


# if "df" not in st.session_state:
#     st.session_state.df = pd.DataFrame(np.random.randn(20, 2), columns=["x", "y"])

df = get_df()

st.header("Choose a datapoint color")

# 사용자가 위젯을 변경했을 때 스크립트가 처음부터 재실행 
color = st.color_picker("Color", "#FF0000")
st.divider()
st.write(f"{color = }")
st.write(f"{st.session_state}")
st.divider()

# key 파라미터를 통해 session_state에 키값 추가
# color = st.color_picker("Color", "#FF0000", key='kcolor')
# st.divider()
# st.write(f"{color = }")
# st.write(f"{st.session_state}")
# st.divider()


st.scatter_chart(df, x="x", y="y", color=color)

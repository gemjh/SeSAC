import streamlit as st
import numpy as np
import pandas as pd

# 1. st.slider()
x = st.slider('x')  # 👈 this is a widget
st.write(x, 'squared is', x * x)

# 2. st.text_input
st.text_input("Your name", key="name")

# You can access the value at any point with:
st.session_state.name

# 3. st.checkox
if st.checkbox('Show dataframe'):
    chart_data = pd.DataFrame(
       np.random.randn(20, 3),
       columns=['a', 'b', 'c'])

    chart_data

# 4. st.selectbox
df = pd.DataFrame({
    'first column': [1, 2, 3, 4],
    'second column': [10, 20, 30, 40]
    })

option = st.selectbox(
    'Which number do you like best?',
     df['first column'])

'You selected: ', option
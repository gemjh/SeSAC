import streamlit as st
import numpy as np
import pandas as pd

# 1. basic
dataframe = np.random.randn(10, 20)
st.dataframe(dataframe)

# 2. style
dataframe = pd.DataFrame(
    np.random.randn(10, 20),
    columns=('col %d' % i for i in range(20)))

st.dataframe(dataframe.style.highlight_max(axis=0))

# 3. static table
dataframe = pd.DataFrame(
    np.random.randn(10, 20),
    columns=('col %d' % i for i in range(20)))
st.table(dataframe)
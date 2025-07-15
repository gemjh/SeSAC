"""
session state 1st example
- st.session_state 라는 dict-like 객체를 기본으로 제공한다.
- st.session_state 는 rerun 시, 이전 값을 유지한다.
"""
import streamlit as st

if "counter" not in st.session_state:
    st.session_state.counter = 0

st.session_state.counter += 1

st.header(f"This page has run {st.session_state.counter} times.")
st.button("Run it again")

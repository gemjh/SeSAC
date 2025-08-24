import streamlit as st

# 1. 초기화
if 'key' not in st.session_state:
    st.session_state['key'] = 'value'

# Session State also supports attribute based syntax
if 'key' not in st.session_state:
    st.session_state.key = 'value'

st.write('initialized:')
st.session_state
st.divider()

# 2. 읽기
st.write(st.session_state.key)
# Outputs: value
st.divider()


# 3. 수정
st.session_state.key = 'value2'     # Attribute API
st.session_state['key'] = 'value2'  # Dictionary like API

st.write(st.session_state.key)
# Outputs: value2
st.divider()

# 4. Session State 조회
st.write(st.session_state)

# With magic:
st.session_state
st.divider()

# 5. 초기화되지 않은 변수
# st.write(st.session_state['value'])
# Throws an exception!

# 6. 삭제
# Delete a single key-value pair
del st.session_state['key']
st.session_state
st.divider()


# 7. 전체 아이템 삭제
for key in st.session_state.keys():
    del st.session_state[key]

st.session_state    
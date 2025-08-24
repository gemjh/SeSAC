import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import subprocess
import sys
import os

# 페이지 제목
st.title("Streamlit 기본 예제")

# 사이드바에 제목
st.sidebar.title("Streamlit 개요")

# 사이드바에 설명
st.sidebar.markdown("""
## Streamlit 장단점
- 웹 프로그래밍은 클라이언트와 서버 양쪽을 코딩해야 하는데 스트림릿의 가장 큰 장점은 클라이언트와 서버 코딩을, 파이썬 하나로 할 수 있다는 점
- Frontend 코딩의 화면 요소 만들기, 배치와 스타일링 등을 간단하게 할 수 있음
- Backend 코딩에서의 URL, 처리, HTML 이나 API 응답 등의 처리가 간단함
- 클라이언트와 서버간 비동기 연동에 대한 코딩이 불필요
- 개발 후에 상용서버에 배포하는 것도 간편
- (단점) 속도가 느리고, 일반 웹 프로그래밍을 하기에는 기능이 충분하지 않음
""")

# Magic Command 실행 함수
def run_magic_cmd():
    try:
        # magic_cmd.py 파일의 경로
        magic_cmd_path = "magic_cmd.py"
        
        # 파일이 존재하는지 확인
        if os.path.exists(magic_cmd_path):
            # magic_cmd.py 파일을 실행
            result = subprocess.run([sys.executable, magic_cmd_path], 
                                  capture_output=True, text=True, cwd=os.getcwd())
            
            if result.returncode == 0:
                st.success("magic_cmd.py 실행 완료!")
                st.code(result.stdout, language='python')
            else:
                st.error(f"magic_cmd.py 실행 중 오류 발생: {result.stderr}")
        else:
            st.error(f"magic_cmd.py 파일을 찾을 수 없습니다. 경로: {magic_cmd_path}")
    except Exception as e:
        st.error(f"실행 중 오류 발생: {str(e)}")

# 메인 컨텐츠
st.header("1. Display data")

# Magic command 예제
st.subheader("(1) Magic command 지원")
st.write("st.write()를 호출하지 않고도 앱에 쓸 수 있음")

# Magic Command 실행 버튼
if st.button("🎯 magic_cmd.py 실행하기"):
    run_magic_cmd()

# Magic command 예제들
st.markdown("### Magic Command 예제들")

# 1. 마크다운 텍스트
st.markdown("""
# This is the document title

This is some _markdown_.
""")

# 2. 데이터프레임 (magic command 스타일)
df_magic = pd.DataFrame({'col1': [1,2,3]})
st.write("Magic command로 데이터프레임 표시:")
df_magic  # 👈 Draw the dataframe

# 3. 변수 값 표시
x = 10
st.write("Magic command로 변수 값 표시:")
st.write('x', x)  # 👈 Draw the string 'x' and then the value of x

# 4. Matplotlib 차트
st.write("Magic command로 Matplotlib 차트 표시:")
arr = np.random.normal(1, 1, size=100)
fig, ax = plt.subplots()
ax.hist(arr, bins=20)
st.pyplot(fig)  # 👈 Draw a Matplotlib chart

# 데이터프레임 예제
st.subheader("(2) Data frame 쓰기")
df = pd.DataFrame({
    'first column': [1, 2, 3, 4],
    'second column': [10, 20, 30, 40]
})
st.write("기본 데이터프레임:")
st.write(df)

# 차트 예제
st.subheader("(3) Chart 그리기")
chart_data = pd.DataFrame(
    np.random.randn(20, 3),
    columns=['a', 'b', 'c'])

st.line_chart(chart_data)

# 위젯 예제
st.header("2. Widget")
name = st.text_input("이름을 입력하세요")
if name:
    st.write(f"안녕하세요, {name}님!")

age = st.slider("나이를 선택하세요", 0, 100, 25)
st.write(f"선택한 나이: {age}")

# 레이아웃 예제
st.header("3. Layout")
col1, col2 = st.columns(2)

with col1:
    st.write("첫 번째 컬럼")
    st.button("버튼 1")

with col2:
    st.write("두 번째 컬럼")
    st.button("버튼 2")

# 진행률 표시
st.header("4. Progress")
progress_bar = st.progress(0)
for i in range(100):
    progress_bar.progress(i + 1)
st.success("완료!") 
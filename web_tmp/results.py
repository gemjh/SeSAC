import streamlit as st

# 결과1번: 결과 요약
html_table_result = """
<table class="custom-table">
    <thead>
        <tr>
            <th>문항 (개수)</th>
            <th colspan="2">결과</th>
            <th colspan="2">실어증 점수</th>
        </tr>
        <tr>
            <th></th>
            <th>정답 수</th>
            <th>점수</th>
            <th></th>
            <th></th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td class="category-cell">O/X 고르기 (15)</td>
            <td>NN개</td>
            <td>NN개</td>
            <td rowspan="3" class="aphasia-category">알아듣기</td>
            <td rowspan="3" class="aphasia-category">NN점</td>
        </tr>
        <tr>
            <td class="category-cell">사물 찾기 (6)</td>
            <td>NN개</td>
            <td>NN개</td>
            <!-- rowspan으로 병합된 셀 -->
            <!-- rowspan으로 병합된 셀 -->
        </tr>
        <tr>
            <td class="category-cell">그림 고르기 (6)</td>
            <td>NN개</td>
            <td>NN개</td>
            <!-- rowspan으로 병합된 셀 -->
            <!-- rowspan으로 병합된 셀 -->
        </tr>
        <tr>
            <td class="category-cell">듣고 따라 말하기 (10)</td>
            <td>NN개</td>
            <td>NN점</td>
            <td class="aphasia-category">따라 말하기</td>
            <td class="aphasia-category">NN점</td>
        </tr>
        <tr>
            <td class="category-cell">끝말 맞추기 (5)</td>
            <td>NN개</td>
            <td>NN개</td>
            <td rowspan="2" class="aphasia-category">이름대기 및<br>날말찾기</td>
            <td rowspan="2" class="aphasia-category">NN점</td>
        </tr>
        <tr>
            <td class="category-cell">물건 이름 말하기 (10)</td>
            <td>NN개</td>
            <td>NN개</td>
            <!-- rowspan으로 병합된 셀 -->
            <!-- rowspan으로 병합된 셀 -->
        </tr>
        <tr>
            <td class="category-cell">동물 이름 말하기 (1)</td>
            <td>NN개</td>
            <td>NN개</td>
            <td rowspan="2" class="aphasia-category">스스로 말하기</td>
            <td rowspan="2" class="aphasia-category">NN점</td>
        </tr>
        <tr>
            <td class="category-cell">그림 보고 이야기 하기 (NN)</td>
            <td>NN개</td>
            <td>NN점</td>
            <!-- rowspan으로 병합된 셀 -->
            <!-- rowspan으로 병합된 셀 -->
        </tr>
        <tr class="header-row">
            <td><strong>합계</strong></td>
            <td></td>
            <td><strong>NN점</strong></td>
            <td></td>
            <td><strong>NN점</strong></td>
        </tr>
    </tbody>
</table>

"""

st.markdown(html_table_result, unsafe_allow_html=True)

# 결과 요약 차트
col1, col2 = st.columns(2)
with col1:
    fig = px.bar(clap_a_data, x='category', y='score',
                title="문항별 점수", labels={'category': '검사항목', 'score': '점수'})
    st.plotly_chart(fig, use_container_width=True)
with col2:
    fig = px.bar(clap_a_data, x='category', y='score',
                title="실어증 점수", labels={'category': '검사항목', 'score': '점수'})
    st.plotly_chart(fig, use_container_width=True)


# 결과2번: O/X 고르기
html_table_ox = """
<table class="custom-table">
    <thead>
        <tr>
            <th>NO.</th>
            <th>문항</th>
            <th>목표 반응</th>
            <th colspan="2">반응 기록</th>
            <th>점수</th>            
        </tr>
        <tr>
            <th></th>
            <th></th>
            <th></th>
            <th>응답</th>
            <th>무응답</th>
            <th></th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td class="category-cell">연습</td>
            <td>여기가 경찰서입니까?</td>
            <td>코끼리는 코가 깁니까?</td>
            <td>O</td>
            <td>O</td>
            <td>✔️</td>
        </tr>
    </tbody>
</table>

"""

# 결과3번: 사물 찾기
html_table_ox = """
<table class="custom-table">
    <thead>
        <tr>
            <th>NO.</th>
            <th>문항</th>
            <th colspan="2">반응 기록</th>
            <th>점수</th>            
        </tr>
        <tr>
            <th></th>
            <th></th>
            <th>응답</th>
            <th>무응답</th>
            <th></th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td class="category-cell">연습</td>
            <td>버스</td>
            <td></td>
            <td>✔️</td>
            <td></td>
        </tr>
    </tbody>
</table>
"""

# 결과4번: 그림 고르기
html_table_pic = """
<table class="custom-table">
    <thead>
        <tr>
            <th>NO.</th>
            <th>문항</th>
            <th colspan="2">반응 기록</th>
            <th>점수</th>            
        </tr>
        <tr>
            <th></th>
            <th></th>
            <th>응답</th>
            <th>무응답</th>
            <th></th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td class="category-cell">연습</td>
            <td>A. 식탁 위에 사과 세 개가 놓여 있다. <br>B.식탁 위에 사과 두 개가 놓여 있다.<br>C.식탁 위에 오렌지 세 개가 놓여 있다.
            </td>
            <td></td>
            <td>✔️</td>
            <td></td>
        </tr>
    </tbody>
</table>
"""

# 결과5번: 듣고 따라 말하기
html_table_repeat = """
<table class="custom-table">
    <thead>
        <tr>
            <th>NO.</th>
            <th>문항</th>
            <th>목표 반응</th>
            <th>반응 기록</th>
            <th>점수</th>            
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>1</td>
            <td>오이</td>
            <td>오이</td>
            <td>오이</td>
            <td>2</td>
        </tr>
    </tbody>
</table>
"""

# 결과 6번: 끝말 맞추기
html_table_last = """
<table class="custom-table">
    <thead>
        <tr>
            <th>NO.</th>
            <th>문항</th>
            <th>목표 반응</th>
            <th>반응 기록</th>
            <th>점수</th>            
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>1</td>
            <td>토끼는 빠르고, 거북이는<br></td>
            <td>느리다,</td>
            <td>오이</td>
            <td>2</td>
        </tr>
    </tbody>
</table>
"""
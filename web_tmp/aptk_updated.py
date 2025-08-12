import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# from clapd import pa_repeat, ta_repeat

# 페이지 설정
st.set_page_config(page_title="CLAP-D", layout="wide")
st.markdown("""
<style>
    .pronunciation-table {
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
        font-size: 14px;
    }
    .pronunciation-table .section-title {
        font-size: 16px;
        font-weight: bold;
        margin: 5px 0 10px 0;
        color: #333;
    }
    .pronunciation-table .category-cell {
        background-color: #f8f8f8;
        font-weight: bold;
        text-align: left;
        padding-left: 15px;
    }
    .pronunciation-table th {
        background-color: #f2f2f2 !important;
        font-weight: bold;
    }
    .pronunciation-table th, .pronunciation-table td {
        border: 1px solid #ddd;
        padding: 12px 8px;
        text-align: center;
        vertical-align: middle;
    }

    .pronunciation-table .header-main {
        background-color: #e6e6e6;
        font-weight: bold;
    }

    .pronunciation-table .sub-category {
        background-color: #fafafa;
        text-align: left;
        padding-left: 20px;
    }
    .pronunciation-table .total-row {
        background-color: #e6e6e6;
        font-weight: bold;
    }
    .assessment-table {
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
        font-size: 14px;
    }
    .assessment-table th {
        background-color: #f2f2f2 !important;
        font-weight: bold;
    }
    .assessment-table th, .assessment-table td {
        border: 1px solid #ddd;
        padding: 12px 8px;
        text-align: center;
        vertical-align: middle;
    }
    .assessment-table .header-main {
        background-color: #e6e6e6;
        font-weight: bold;
    }
    .assessment-table .sub-category {
        background-color: #fafafa;
        text-align: left;
        padding-left: 20px;
    }
    .assessment-table .total-row {
        background-color: #e6e6e6;
        font-weight: bold;
    }
    .assessment-table .word-column {
        background-color: white;
        text-align: left;
        padding-left: 10px;
        width: 80px;
    }
    .assessment-table .phoneme-columns {
        width: 40px;
        background-color: white;
    }
    .assessment-table .result-column {
        width: 60px;
        background-color: white;
    }
    .assessment-table .score-column {
        width: 50px;
        background-color: white;
    }
    .assessment-table .summary-row {
        background-color: #f9f9f9;
        font-weight: bold;
    }
    .assessment-table .description-cell {
        background-color: white;
        text-align: left;
        padding: 10px;
        font-size: 12px;
        line-height: 1.4;
    }
    .red-text {
        color: #e74c3c;
    }
    .blue-text {
        color: #3498db;
    }
    .section-title {
        font-size: 16px;
        font-weight: bold;
        margin: 5px 0 10px 0;
        color: #333;
    }
    .summary-text {
        text-align: right;
        font-size: 14px;
        color: #666;
        margin-bottom: 10px;
    }
</style>
""",unsafe_allow_html=True)

# -----------------------------------------평가 데이터 정의(임시)--------------------------------------------
evaluation_data = [
    {
        'id': 'a_sound',
        'title': "'아' 소리내기",
        'summary': "최대 발성 시간 NN 초 총점 NN 점",
        'items': [
            {'no': '연습', 'content': "'아'"},
            {'no': '1', 'content': "1회차 '아'"},
            {'no': '', 'content': "2회차 '아'"}
        ]
    },
    {
        'id': 'pa_sound',
        'title': "'퍼' 반복하기",
        'summary': "평균 횟수 NN 번 총점 NN 점",
        'items': [
            {'no': '연습', 'content': "'퍼'"},
            {'no': '1', 'content': "1회차 '퍼'"},
            {'no': '', 'content': "2회차 '퍼'"},
            {'no': '', 'content': "3회차 '퍼'"}
        ]
    },
    {
        'id': 'ta_sound',
        'title': "'터' 반복하기",
        'summary': "평균 횟수 NN 번 총점 NN 점",
        'items': [
            {'no': '연습', 'content': "'터'"},
            {'no': '1', 'content': "1회차 '터'"},
            {'no': '', 'content': "2회차 '터'"},
            {'no': '', 'content': "3회차 '터'"}
        ]
    },
    {
        'id': 'ka_sound',
        'title': "'커' 반복하기",
        'summary': "평균 횟수 NN 번 총점 NN 점",
        'items': [
            {'no': '연습', 'content': "'커'"},
            {'no': '1', 'content': "1회차 '커'"},
            {'no': '', 'content': "2회차 '커'"},
            {'no': '', 'content': "3회차 '커'"}
        ]
    },
    {
        'id': 'ptk_sound',
        'title': "'퍼터커' 반복하기",
        'summary': "평균 횟수 NN 번 총점 NN 점",
        'items': [
            {'no': '연습', 'content': "'퍼터커'"},
            {'no': '1', 'content': "1회차 '퍼터커'"},
            {'no': '', 'content': "2회차 '퍼터커'"},
            {'no': '', 'content': "3회차 '퍼터커'"}
        ]
    }
]
word_level_data = [
    {'no': '연습', 'word': '모자', 'initial': 'ㅁ', 'medial': 'ㅗ', 'final': '', 'medial2': '', 'result': '', 'score': ''},
    {'no': '1', 'word': '나비', 'initial': 'ㄴ', 'medial': 'ㅏ', 'final': '', 'medial2': 'ㅣ', 'result': '나비', 'score': '0'},
    {'no': '2', 'word': '포도', 'initial': 'ㅍ', 'medial': 'ㅗ', 'final': 'ㄷ', 'medial2': 'ㅗ', 'result': '모도', 'score': '0'},
    {'no': '3', 'word': '방울', 'initial': '', 'medial': '', 'final': 'ㅌ', 'medial2': '', 'result': '', 'score': ''},
    {'no': '4', 'word': '수갑', 'initial': 'ㅅ', 'medial': '', 'final': 'ㅂ', 'medial2': '', 'result': '나비', 'score': ''},
    {'no': '5', 'word': '가위', 'initial': 'ㄱ', 'medial': '', 'final': '', 'medial2': 'ㅟ', 'result': '', 'score': ''},
]

sentence_level_data = [
    {'no': '1', 'sentence': ['우리나라의 봄은 신그럽다.','집식은 뽀뽀 지치고, 푸른 새싹은 끊움을 띠어낸다.'], 
     'phonemes': [
         {'sound': 'ㅅ', 'count': '3'},
         {'sound': 'ㅆ', 'count': '2'},
         {'sound': 'ㅈ', 'count': '2'},
         {'sound': 'ㅉ', 'count': '2'},
         {'sound': 'ㅊ', 'count': '1'},
         {'sound': 'ㄹ', 'count': '6'},
         {'sound': 'ㅅ', 'count': '1'}
     ],'score':100},
    {'no': '2', 'sentence': ['아이들이 수영장에서 물놀이를 하고 있다.','환영장의 물장구를 치며 청년시고 있다.'],
     'phonemes': [
         {'sound': 'ㅈ', 'count': '3'},
         {'sound': 'ㅊ', 'count': '4'},
         {'sound': 'ㄹ', 'count': '8'}
     ],'score':100}
]

# ----------------------------------------- 추후 상기 데이터 삭제 요망 -----------------------------------------



# 테이블 생성
def create_evaluation_table_html(eval_item):
    """st.components.v1.html을 위한 완전한 HTML 문서 생성"""
    
    html_content = f"""
        <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 10px;
        }}

        .pronunciation-detail-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
            font-size: 14px;
        }}
        .pronunciation-detail-table th {{
            background-color: #f2f2f2 !important;
            font-weight: bold;
        }}
        .pronunciation-detail-table th, .pronunciation-detail-table td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: center;
            vertical-align: middle;
        }}
        .pronunciation-detail-table .content-column {{
            background-color: white;
            text-align: left;
            padding-left: 15px;
            width: 200px;
        }}
        .pronunciation-detail-table .button-column {{
            width: auto;
            background-color: white;
        }}
        .pronunciation-detail-table .time-column {{
            width: 80px;
            background-color: white;
        }}
        .pronunciation-detail-table .score-column {{
            width: 60px;
            background-color: white;
        }}
        .rec-button {{
            background-color: #e74c3c;
            color: white;
            border: none;
            border-radius: 15px;
            padding: 4px 12px;
            font-size: 11px;
            margin-right: 5px;
            cursor: pointer;
            transition: background-color 0.3s;
        }}
        .rec-button:hover {{
            background-color: #c0392b;
        }}
        .graph-button {{
            background-color: #3498db;
            color: white;
            border: none;
            border-radius: 15px;
            padding: 4px 12px;
            font-size: 11px;
            cursor: pointer;
            transition: background-color 0.3s;
        }}
        .graph-button:hover {{
            background-color: #2980b9;
        }}
        .section-title{{
            font-size: 16px;
            font-weight: bold;
            margin: 5px 0 10px 0;
            color: #333;
        }}
        .summary-text {{
            text-align: right;
            font-size: 14px;
            color: #666;
            margin-bottom: 10px;
        }}
        </style>
    </head>
    <body>
        <div class="section-title">{eval_item['title']}</div>
        <div class="summary-text">{eval_item['summary']}</div>
        
        <table class="pronunciation-detail-table">
            <thead>
                <tr>
                    <th class="no-column">NO.</th>
                    <th colspan="2" class="content-column">문항</th>
                    <th class="time-column">발성시간</th>
                    <th class="score-column">점수</th>
                </tr>
            </thead>
            <tbody>
    """
    
    # 각 항목을 위한 행들 추가
    for i, item in enumerate(eval_item['items']):
        html_content += f"""
                <tr>
                    <td class="no-column">{item['no']}</td>
                    <td class="content-column">{item['content']}</td>
                    <td class="button-column">
                        <button class="rec-button" onclick="recordSound('{eval_item['id']}', {i})">REC.</button>
                        <button class="graph-button" onclick="showGraph('{eval_item['id']}', {i})">GRAPH</button>
                    </td>
                    <td class="time-column">NNN초</td>
                    <td class="score-column"></td>
                </tr>
        """
    
    html_content += """
            </tbody>
        </table>
        
        <script>
        function recordSound(evalId, itemIndex) {
            alert('🎤 ' + evalId + ' - ' + itemIndex + '번째 항목 녹음을 시작합니다!');
            // 실제 녹음 기능을 여기에 구현할 수 있습니다
        }
        
        function showGraph(evalId, itemIndex) {
            alert('📊 ' + evalId + ' - ' + itemIndex + '번째 항목의 그래프를 표시합니다!');
            // 실제 그래프 표시 기능을 여기에 구현할 수 있습니다
        }
        </script>
    </body>
    </html>
    """
    
    return html_content


def create_word_level_table():
    """단어수준 또박또박 말하기 테이블 생성"""
    html = """
    <div class="section-title">또박또박 말하기</div>
    <div class="summary-text">단어 수준&nbsp;&nbsp;&nbsp;&nbsp;자음정확도 NN/NN NN% 모음 정확도 NN/NN NN% 총점 NN 점</div>
    
    <table class="assessment-table">
        <thead>
            <tr>
                <th>NO.</th>
                <th>문항</th>
                <th>초성</th>
                <th>중성</th>
                <th>7종성</th>
                <th>모음</th>
                <th>전사</th>
                <th>점수</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>연습</td>
                <td class="category-cell">모자</td>
                <td>ㅁ</td>
                <td>ㅗ</td>
                <td></td>
                <td></td>
                <td></td>
                <td></td>
            </tr>
            <tr>
                <td>1</td>
                <td class="category-cell">나비</td>
                <td><span class="red-text">ㄴ</span></td>
                <td><span class="red-text">ㅏ</span></td>
                <td></td>
                <td>ㅣ</td>
                <td>나비</td>
                <td>0</td>
            </tr>
            <tr>
                <td>2</td>
                <td class="category-cell">포도</td>
                <td><span class="red-text">ㅍ</span></td>
                <td><span class="red-text">ㅗ</span></td>
                <td>ㄷ</td>
                <td>ㅗ</td>
                <td>모도</td>
                <td>0</td>
            </tr>
            <tr>
                <td>3</td>
                <td class="category-cell">방울</td>
                <td></td>
                <td></td>
                <td>ㅌ</td>
                <td></td>
                <td></td>
                <td></td>
            </tr>
            <tr>
                <td>4</td>
                <td class="category-cell">수갑</td>
                <td><span class="red-text">ㅅ</span></td>
                <td></td>
                <td>ㅂ</td>
                <td></td>
                <td>나비</td>
                <td></td>
            </tr>
            <tr>
                <td>5</td>
                <td class="category-cell">가위</td>
                <td><span class="red-text">ㄱ</span></td>
                <td></td>
                <td></td>
                <td>ㅟ</td>
                <td></td>
                <td></td>
            </tr>
        </tbody>
    </table>
    """
    return html

def create_sentence_level_table(sentence_level_data):
    """문장수준 또박또박 말하기 테이블 생성"""
    
    html = """
    <div class="section-title">또박또박 읽기</div>
    <div class="summary-text">문장 수준&nbsp;&nbsp;&nbsp;&nbsp;자음정확도 NN/NN NN% 총점 NN 점</div>
    
    <table class="assessment-table">
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
                <th>자음 정확도</th>
                <th>개수</th>
                <th></th>
            </tr>
        </thead>
        <tbody>
    """
    
    for data_item in sentence_level_data:
        no = data_item['no']
        sentences = data_item['sentence']
        phonemes = data_item['phonemes']
        score = data_item['score']
        
        phonemes_count = len(phonemes)
        sentence_text = "<br>".join(sentences)
        
        for i, phoneme in enumerate(phonemes):
            sound = phoneme['sound']
            count = phoneme['count']
            
            if i == 0:  # 첫 번째 행
                html += f"""
            <tr>
                <td rowspan="{phonemes_count}">{no}</td>
                <td class="category-cell" rowspan="{phonemes_count}">{sentence_text}</td>
                <td>{sound}</td>
                <td>{count}</td>
                <td rowspan="{phonemes_count}">{score}</td>
            </tr>
                """
            else:  # 나머지 행들
                html += f"""
            <tr>
                <td>{sound}</td>
                <td>{count}</td>
            </tr>
                """
    
    html += """
        </tbody>
    </table>
    """
    
    return html


# 메인 애플리케이션
def main():
    st.subheader("결과 요약")
    a_sound, pa_sound, ta_sound, ka_sound, ptk_sound=100,100,100,100,100
    pa_repeat,ta_repeat,ka_repeat,ptk_repeat,word_level,sentence_level,consonant_word,vowel_word,consonant_sentence=100,100,100,100,100,100,100,100,100
    if True:
        max_time,pa_avg,ta_avg,ka_avg,ptk_avg=10,1,1,1,1
        total_score = a_sound + pa_repeat + ta_repeat + ka_repeat + ptk_repeat + word_level + sentence_level
        
        # 계산된 결과를 표로 표시
        result_html = f"""
        <div style="margin-top: 20px;">
        <table class="pronunciation-table">
            <thead>
                <tr>
                    <th>문항</th>
                    <th>수행 결과</th>
                    <th>점수</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td class="category-cell">'아' 소리내기</td>
                    <td>최대 발성시간 {max_time}초</td>
                    <td>{a_sound}점</td>
                </tr>
                <tr>
                    <td class="category-cell">'퍼' 반복하기</td>
                    <td>평균 횟수 {pa_avg}번</td>
                    <td>{pa_repeat}점</td>
                </tr>
                <tr>
                    <td class="category-cell">'터' 반복하기</td>
                    <td>평균 횟수 {ta_avg}번</td>
                    <td>{ta_repeat}점</td>
                </tr>
                <tr>
                    <td class="category-cell">'커' 반복하기</td>
                    <td>평균 횟수 {ka_avg}번</td>
                    <td>{ka_repeat}점</td>
                </tr>
                <tr>
                    <td class="category-cell">'퍼터커' 반복하기</td>
                    <td>평균 횟수 {ptk_avg}번</td>
                    <td>{ptk_repeat}점</td>
                </tr>
                <tr>
                    <td rowspan="2" class="category-cell">또박또박 말하기 (단어수준)</td>
                    <td class="sub-category">자음 정확도: {consonant_word}%</td>
                    <td rowspan="2">{word_level}점</td>
                </tr>
                <tr>
                    <td class="sub-category">모음 정확도: {vowel_word}%</td>
                </tr>
                <tr>
                    <td class="category-cell">또박또박 말하기 (문장수준)</td>
                    <td>자음 정확도: {consonant_sentence}%</td>
                    <td>{sentence_level}점</td>
                </tr>
                <tr class="total-row">
                    <td><strong>합계</strong></td>
                    <td></td>
                    <td><strong>{total_score}점</strong></td>
                </tr>
            </tbody>
        </table>
        </div>
        """
        
        st.markdown(result_html, unsafe_allow_html=True)

    # 평가 리스트
    a_sound, pa_sound, ta_sound, ka_sound, ptk_sound = evaluation_data
    
    evaluation_list = [a_sound, pa_sound, ta_sound, ka_sound, ptk_sound]

    # for문으로 각 평가 테이블 생성
    for eval_item in evaluation_list:
        html_content = create_evaluation_table_html(eval_item)
        # st.components.v1.html 사용 - 높이는 항목 수에 따라 동적으로 계산
        height = 150 + (len(eval_item['items']) * 35)  # 기본 높이 + 각 행당 35px
        components.html(html_content, height=height)

    # 또박또박
    # st.subheader("또박또박 말하기")
    word_table_html = create_word_level_table()
    st.markdown(word_table_html, unsafe_allow_html=True)
    
    # 문장수준 표
    # st.subheader("또박또박 읽기")
    sentence_table_html = create_sentence_level_table(sentence_level_data)
    st.markdown(sentence_table_html, unsafe_allow_html=True)
    
# 실행
if __name__ == "__main__":
    main()
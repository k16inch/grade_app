import streamlit as st
import pandas as pd

# 1. 웹 페이지 제목 설정
st.title("지필고사 성적 분석기")

# 2. 엑셀 파일 업로드 기능 (xlsx 파일만 허용)
uploaded_file = st.file_uploader("성적 엑셀 파일(XLXS DATA)을 업로드하세요", type=["xlsx"])

# 사용자가 파일을 업로드했을 때만 아래 로직이 실행됩니다
if uploaded_file is not None:
    
    # 3. 엑셀 파일 읽기 (위의 4줄은 제목이나 공백으로 생각하고 5번째 줄부터 읽음)
    df = pd.read_excel(uploaded_file, header=4)
    
    # 4. 성적 데이터 전처리
    # 첫 번째 열(이름/학번 등)을 제외하고 점수가 적힌 열만 선택
    score_data = df.iloc[:, 1:]
    
    # 숫자가 아닌 데이터는 지우고, 모든 점수를 하나의 긴 줄로 합칩니다 (stack)
    all_scores = score_data.apply(pd.to_numeric, errors='coerce').stack().dropna()
    
    # 5. 점수 구간 설정 (0점부터 101점 직전까지)
    bins = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 101]
    labels = ["0-9", "10-19", "20-29", "30-39", "40-49", "50-59", "60-69", "70-79", "80-89", "90-100"]
    
    # 점수들을 위에서 정한 구간(labels)에 맞게 분류
    categories = pd.cut(all_scores, bins=bins, labels=labels, right=False)
    
    # 6. 결과 출력
    st.write("### 성적 분포 통계")
    
    # 구간별로 학생이 몇 명인지 세고 점수 순서대로 정렬
    result = categories.value_counts().sort_index()
    
    # 화면에 막대그래프 그리기
    st.bar_chart(result) 
    
    # 화면에 텍스트 표 형태로도 출력
    st.write(result)

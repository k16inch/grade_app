import streamlit as st
import pandas as pd

st.title("지필고사 성적 분석기")

uploaded_file = st.file_uploader("성적 엑셀 파일(XLXS DATA)을 업로드하세요", type=["xlsx"])

if uploaded_file is not None:
    # 엑셀 파일 읽기
    df = pd.read_excel(uploaded_file, header=4)
    
    # 성적 분석 로직
    score_data = df.iloc[:, 1:]
    all_scores = score_data.apply(pd.to_numeric, errors='coerce').stack().dropna()
    
    bins = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 101]
    labels = ["0-9", "10-19", "20-29", "30-39", "40-49", "50-59", "60-69", "70-79", "80-89", "90-100"]
    categories = pd.cut(all_scores, bins=bins, labels=labels, right=False)
    
    # 결과 출력
    st.write("### 성적 분포 통계")
    result = categories.value_counts().sort_index()
    
    st.bar_chart(result)  # 그래프 출력
    st.write(result)

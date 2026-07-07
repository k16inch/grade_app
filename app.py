import streamlit as st
import pandas as pd

# 웹 페이지 제목 설정
st.title("지필고사 성적 분석기")

# 엑셀 파일 업로드 기능 (xlsx 파일만 허용)
uploaded_file = st.file_uploader("성적 엑셀 파일(XLXS DATA)을 업로드하세요", type=["xlsx"])

# 사용자가 파일을 업로드했을 때만 실행
if uploaded_file is not None:
    
    # 엑셀 파일 읽기 (5번째 줄부터 읽음)
    df = pd.read_excel(uploaded_file, header=4)
    
    # 성적 데이터 전처리 (첫 번째 열 제외)
    score_data = df.iloc[:, 1:]
    
    # 모든 점수를 숫자형으로 바꾸고 빈 칸은 제거
    all_scores = score_data.apply(pd.to_numeric, errors='coerce').stack().dropna()
    
    # ----------------------------------------------------
    # [새로 추가된 기능] 주요 성적 통계 계산
    # ----------------------------------------------------
    avg_score = all_scores.mean()  # 평균 점수
    max_score = all_scores.max()  # 최고 점수
    min_score = all_scores.min()  # 최저 점수
    
    st.write("### 📊 성적 요약")
    # 화면에 예쁜 3칸 상자로 통계 지표를 보여줍니다
    col1, col2, col3 = st.columns(3)
    col1.metric(label="평균 점수", value=f"{avg_score:.2f}점")
    col2.metric(label="최고 점수", value=f"{max_score:.0f}점")
    col3.metric(label="최저 점수", value=f"{min_score:.0f}점")
    
    st.markdown("---") # 화면 구분선
    # ----------------------------------------------------
    
    # 점수 구간 설정 (0점부터 101점 직전까지)
    bins = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 101]
    labels = ["0-9", "10-19", "20-29", "30-39", "40-49", "50-59", "60-69", "70-79", "80-89", "90-100"]
    
    # 점수들을 구간에 맞게 분류
    categories = pd.cut(all_scores, bins=bins, labels=labels, right=False)
    
    # 결과 출력
    st.write("### 📈 성적 분포 통계")
    
    # 구간별 학생 수 계산 및 정렬
    result = categories.value_counts().sort_index()
    
    # 화면에 막대그래프와 표 출력
    st.bar_chart(result) 
    st.write(result)

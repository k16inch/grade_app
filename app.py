import streamlit as st
import pandas as pd

# 웹 페이지 제목 및 설명
st.set_page_config(page_title="성적 분석기", layout="centered")
st.title("📊 성적 데이터 분석 시스템")
st.markdown("엑셀 파일을 업로드하고 성취 등급 컷트라인을 입력하면, 자동으로 분포와 등급을 분석합니다.")

# 1. 파일 업로드 기능
uploaded_file = st.file_uploader("엑셀 파일을 업로드해 주세요 (.xlsx)", type=["xlsx"])

if uploaded_file is not None:
    # 엑셀 파일 읽기
    try:
        df = pd.read_excel(uploaded_file)
        st.success("파일이 성공적으로 업로드되었습니다!")
        
        # 성적이 들어있는 열 선택 (사용자가 직접 선택 가능)
        columns = df.columns.tolist()
        score_column = st.selectbox("성적 데이터가 포함된 열(Column)을 선택하세요:", columns)
        
        scores = df[score_column].dropna() # 결측치 제거
        
        st.divider() # 구분선
        
        # 사이드바 또는 메인 화면에 컷트라인 입력창 배치
        st.subheader("⚙️ 성취점수 등급 컷트라인 설정")
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1: cutoff_A = st.number_input("A등급 이상", value=90.0, step=1.0)
        with col2: cutoff_B = st.number_input("B등급 이상", value=80.0, step=1.0)
        with col3: cutoff_C = st.number_input("C등급 이상", value=70.0, step=1.0)
        with col4: cutoff_D = st.number_input("D등급 이상", value=60.0, step=1.0)
        with col5: cutoff_E = st.number_input("E등급 이상", value=50.0, step=1.0)
        
        # 분석 실행 버튼
        if st.button("📊 성적 분석 시작", type="primary"):
            
            st.divider()
            
            # --- [분석 1] 10점 단위 성적 분포 ---
            st.subheader("1️⃣ 10점 단위 성적분포인원")
            
            dist_bins = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 101]
            dist_labels = [
                '0~9점', '10~19점', '20~29점', '30~39점', '40~49점', 
                '50~59점', '60~69점', '70~79점', '80~89점', '90~100점'
            ]
            
            dist_categories = pd.cut(scores, bins=dist_bins, labels=dist_labels, right=False)
            dist_counts = dist_categories.value_counts().reindex(dist_labels, fill_value=0)
            
            # 데이터프레임으로 변환하여 웹에 이쁘게 출력
            df_dist = pd.DataFrame({"인원 수(명)": dist_counts})
            st.dataframe(df_dist, use_container_width=True)
            
            total_calculated = dist_counts.sum()
            st.info(f"💡 **분포 인원 합계 (총 응시학생 수): {total_calculated}명**")
            
            st.divider()
            
            # --- [분석 2] 성취 등급별 인원 ---
            st.subheader("2️⃣ 성취점수 등급별 인원")
            
            grade_bins = [-1, cutoff_E, cutoff_D, cutoff_C, cutoff_B, cutoff_A, 101]
            grade_labels = ['미도달', 'E등급', 'D등급', 'C등급', 'B등급', 'A등급']
            
            grade_categories = pd.cut(scores, bins=grade_bins, labels=grade_labels, right=False)
            grade_counts = grade_categories.value_counts().reindex(reversed(grade_labels), fill_value=0)
            
            df_grade = pd.DataFrame({"인원 수(명)": grade_counts})
            st.dataframe(df_grade, use_container_width=True)
            
            # 보너스: 스트림릿 자체 그래프 기능으로 시각화까지!
            st.bar_chart(df_grade)
            
    except Exception as e:
        st.error(f"데이터를 처리하는 중 오류가 발생했습니다: {e}")
else:
    st.info("👆 분석을 시작하려면 성적 엑셀 파일을 업로드해 주세요.")

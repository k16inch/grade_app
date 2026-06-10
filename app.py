import streamlit as st
import pandas as pd
import numpy as np

# 웹 페이지 제목 및 설명
st.set_page_config(page_title="정기고사 성적 분석", layout="centered")
st.title("📊 통합 성적 데이터 분석 시스템")
st.markdown("모든 반의 성적 데이터를 하나로 통합하여 전체 학생을 대상으로 성적 분포와 등급을 분석합니다.")

# 1. 파일 업로드 기능
uploaded_file = st.file_uploader("엑셀 파일을 업로드해 주세요 (.xlsx)", type=["xlsx"])

if uploaded_file is not None:
    try:
        # 서식에 맞춰 가공하기 위해 헤더 없이(header=None) 엑셀을 읽어옵니다.
        raw_df = pd.read_excel(uploaded_file, header=None)
        
        # ----------------------------------------------------
        # [데이터 정제] 전체 학생 점수 통합 추출
        # ----------------------------------------------------
        # 5행(인덱스 4)의 B열(인덱스 1)부터 오른쪽 끝까지의 '반' 개수 파악
        class_labels = raw_df.iloc[4, 1:].dropna().tolist()
        num_classes = len(class_labels)
        
        # 6행(인덱스 5)의 A열(인덱스 0)부터 아래로 내려가며 '응시생수' 행 위치 찾기
        id_series = raw_df.iloc[5:, 0]
        end_row_index = len(raw_df) 
        for idx, val in enumerate(id_series):
            if pd.isna(val) or (isinstance(val, str) and ('응시' in val or '합계' in val or '통계' in val)):
                end_row_index = 5 + idx  
                break
                
        # 모든 반(열)의 점수 구역을 통째로 지정해서 가져옵니다.
        score_matrix = raw_df.iloc[5:end_row_index, 1:1+num_classes]
        
        # 2차원 배열 형태의 점수들을 1차원 리스트로 일렬로 통합합니다 (전체 학생 합치기)
        all_scores_flat = score_matrix.values.flatten()
        
        # 숫자로 강제 변환하고 결측치(공백, 결석 등)를 제거합니다.
        scores = pd.to_numeric(pd.Series(all_scores_flat), errors='coerce').dropna()
        
        st.success(f"총 {num_classes}개 반, 전체 {len(scores)}명의 성적 데이터가 통합되었습니다!")
        
        st.divider()
        
        # ⚙️ 컷트라인 설정 UI
        st.subheader("⚙️ 성취점수 등급 컷트라인 설정")
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1: cutoff_A = st.number_input("A등급 이상", value=90.0, step=1.0)
        with col2: cutoff_B = st.number_input("B등급 이상", value=80.0, step=1.0)
        with col3: cutoff_C = st.number_input("C등급 이상", value=70.0, step=1.0)
        with col4: cutoff_D = st.number_input("D등급 이상", value=60.0, step=1.0)
        with col5: cutoff_E = st.number_input("E등급 이상", value=50.0, step=1.0)
        
        if st.button("📊 통합 성적 분석 시작", type="primary"):
            st.divider()
            
            # --- [분석 1] 전체 10점 단위 성적 분포 ---
            st.subheader("1️⃣ 전체 학생 10점 단위 성적분포인원")
            
            dist_bins = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 101]
            dist_labels = [
                '0~9점', '10~19점', '20~29점', '30~39점', '40~49점', 
                '50~59점', '60~69점', '70~79점', '80~89점', '90~100점'
            ]
            
            dist_categories = pd.cut(scores, bins=dist_bins, labels=dist_labels, right=False)
            dist_counts = dist_categories.value_counts().reindex(dist_labels, fill_value=0)
            
            # 표 형태로 변환 및 총합계 행 추가
            df_dist = pd.DataFrame({"인원 수(명)": dist_counts})
            df_dist.loc['총합계'] = df_dist["인원 수(명)"].sum()
            
            st.dataframe(df_dist, use_container_width=True)
            
            st.divider()
            
            # --- [분석 2] 전체 성취 등급별 인원 ---
            st.subheader("2️⃣ 전체 학생 성취점수 등급별 인원")
            
            grade_bins = [-1, cutoff_E, cutoff_D, cutoff_C, cutoff_B, cutoff_A, 101]
            grade_labels = ['미도달', 'E등급', 'D등급', 'C등급', 'B등급', 'A등급']
            
            grade_categories = pd.cut(scores, bins=grade_bins, labels=grade_labels, right=False)
            grade_counts = grade_categories.value_counts().reindex(reversed(grade_labels), fill_value=0)
            
            # 표 형태로 변환 및 총합계 행 추가
            df_grade = pd.DataFrame({"인원 수(명)": grade_counts})
            
            # 그래프를 그릴 때는 '총합계' 행이 들어가면 막대가 너무 길어지므로, 그래프용 데이터를 먼저 복사해둡니다.
            df_grade_chart = df_grade.copy()
            
            # 실제 화면 표에는 총합계 추가
            df_grade.loc['총합계'] = df_grade["인원 수(명)"].sum()
            
            st.dataframe(df_grade, use_container_width=True)
            
            # 시각화 그래프 출력 (합계 제외한 순수 등급만 표현)
            st.markdown("**[성취 등급 분포 시각화]**")
            st.bar_chart(df_grade_chart)
            
    except Exception as e:
        st.error(f"데이터를 처리하는 중 오류가 발생했습니다. 파일 형식을 확인해 주세요. (오류 내용: {e})")
else:
    st.info("👆 분석을 시작하려면 성적 엑셀 파일을 업로드해 주세요.")

import streamlit as st
import pandas as pd
import numpy as np

# 웹 페이지 제목 및 설명
st.set_page_config(page_title="정기고사 성적 분석기", layout="centered")
st.title("📊 정기고사 과목 성적 분석기")
st.markdown("나이스-지필평가조회-교과목별일람표-전체학급 파일(XLS Data)을 저장하고 불러오시면 됩니다.")

# 1. 파일 업로드 기능
uploaded_file = st.file_uploader("나이스에서 다운로드한 엑셀 파일을 업로드해 주세요 (.xlsx)", type=["xlsx"])

if uploaded_file is not None:
    try:
        # 서식에 맞춰 가공하기 위해 헤더 없이(header=None) 엑셀을 읽어옵니다.
        raw_df = pd.read_excel(uploaded_file, header=None)
        
        # ----------------------------------------------------
        # [데이터 정제] 전체 학생 점수 통합 추출
        # ----------------------------------------------------
        class_labels = raw_df.iloc[4, 1:].dropna().tolist()
        num_classes = len(class_labels)
        
        id_series = raw_df.iloc[5:, 0]
        end_row_index = len(raw_df) 
        for idx, val in enumerate(id_series):
            if pd.isna(val) or (isinstance(val, str) and ('응시' in val or '합계' in val or '통계' in val)):
                end_row_index = 5 + idx  
                break
                
        score_matrix = raw_df.iloc[5:end_row_index, 1:1+num_classes]
        all_scores_flat = score_matrix.values.flatten()
        scores = pd.to_numeric(pd.Series(all_scores_flat), errors='coerce').dropna()
        total_students = len(scores)
        
        st.success(f"총 {num_classes}개 반, 전체 {total_students}명의 성적 데이터가 입력되었습니다!")
        
        st.divider()
        
        # ----------------------------------------------------
        # ⚙️ 성취도 평가 유형 및 컷트라인 설정 UI
        # ----------------------------------------------------
        st.subheader("⚙️ 성취도 분할점수(컷트라인) 설정")
        
        # 과목 유형 선택 (3등급 vs 5등급 vs 6등급)
        subject_type = st.radio(
            "과목의 성취도 등급 유형을 선택하세요:",
            ["3등급 체제 (A, B, C)", "5등급 체제 (A, B, C, D, E)", "6등급 체제 (A, B, C, D, E, 미도달)"],
            horizontal=True
        )
        
        # 선택한 유형에 따라 입력창 동적 변경
        if subject_type == "3등급 체제 (A, B, C)":
            col1, col2 = st.columns(2)
            with col1: cutoff_A = st.number_input("A등급 기준 점수 (이상)", value=80.0, step=1.0)
            with col2: cutoff_B = st.number_input("B등급 기준 점수 (이상)", value=60.0, step=1.0)
            
        elif subject_type == "5등급 체제 (A, B, C, D, E)":
            col1, col2, col3, col4 = st.columns(4)
            with col1: cutoff_A = st.number_input("A등급 기준 점수 (이상)", value=90.0, step=1.0)
            with col2: cutoff_B = st.number_input("B등급 기준 점수 (이상)", value=80.0, step=1.0)
            with col3: cutoff_C = st.number_input("C등급 기준 점수 (이상)", value=70.0, step=1.0)
            with col4: cutoff_D = st.number_input("D등급 기준 점수 (이상)", value=60.0, step=1.0)
            
        else:
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1: cutoff_A = st.number_input("A등급 이상", value=90.0, step=1.0)
            with col2: cutoff_B = st.number_input("B등급 이상", value=80.0, step=1.0)
            with col3: cutoff_C = st.number_input("C등급 이상", value=70.0, step=1.0)
            with col4: cutoff_D = st.number_input("D등급 이상", value=60.0, step=1.0)
            with col5: cutoff_E = st.number_input("E등급 이상", value=50.0, step=1.0)
        
        if st.button("📊 통합 성적 분석 시작", type="primary"):
            st.divider()
            
            # ----------------------------------------------------
            # --- [분석 1] 성적 구간별 분포 (내림차순 정렬) ---
            # ----------------------------------------------------
            st.subheader("1️⃣ 점수 구간별 성적분포 (인원 및 비율)")
            
            dist_bins = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 101]
            dist_labels = [
                '0~9점', '10~19점', '20~29점', '30~39점', '40~49점', 
                '50~59점', '60~69점', '70~79점', '80~89점', '90~100점'
            ]
            
            dist_categories = pd.cut(scores, bins=dist_bins, labels=dist_labels, right=False)
            dist_counts = dist_categories.value_counts().reindex(dist_labels, fill_value=0)
            
            # 높은 점수부터 나열하기 위해 dist_labels를 역순(reversed)으로 순회하여 딕셔너리 구성
            dist_data = {}
            for label in reversed(dist_labels):
                count = dist_counts[label]
                pct = (count / total_students * 100) if total_students > 0 else 0
                dist_data[label] = [f"{count}명", f"{pct:.1f}%"]
            
            dist_data['총합계'] = [f"{total_students}명", "100.0%"]
            df_dist_horizontal = pd.DataFrame(dist_data, index=['학생 수', '비율(%)'])
            st.dataframe(df_dist_horizontal, use_container_width=True)
            
            st.divider()
            
            # ----------------------------------------------------
            # --- [분석 2] 성취 등급별 인원 (가로형) ---
            # ----------------------------------------------------
            st.subheader(f"2️⃣ 성취점수 등급별 분포 ({subject_type.split()[0]})")
            
            if subject_type == "3등급 체제 (A, B, C)":
                grade_bins = [-1, cutoff_B, cutoff_A, 101]
                grade_labels = ['C등급', 'B등급', 'A등급']
                
            elif subject_type == "5등급 체제 (A, B, C, D, E)":
                grade_bins = [-1, cutoff_D, cutoff_C, cutoff_B, cutoff_A, 101]
                grade_labels = ['E등급', 'D등급', 'C등급', 'B등급', 'A등급']
                
            else:
                grade_bins = [-1, cutoff_E, cutoff_D, cutoff_C, cutoff_B, cutoff_A, 101]
                grade_labels = ['미도달', 'E등급', 'D등급', 'C등급', 'B등급', 'A등급']
            
            grade_categories = pd.cut(scores, bins=grade_bins, labels=grade_labels, right=False)
            grade_counts = grade_categories.value_counts().reindex(reversed(grade_labels), fill_value=0)
            
            grade_data = {}
            for label in reversed(grade_labels):
                count = grade_counts[label]
                pct = (count / total_students * 100) if total_students > 0 else 0
                grade_data[label] = [f"{count}명", f"{pct:.1f}%"]
                
            grade_data['총합계'] = [f"{total_students}명", "100.0%"]
            
            df_grade_horizontal = pd.DataFrame(grade_data, index=['학생 수', '비율(%)'])
            st.dataframe(df_grade_horizontal, use_container_width=True)
            
    except Exception as e:
        st.error(f"데이터를 처리하는 중 오류가 발생했습니다. 파일 형식을 확인해 주세요. (오류 내용: {e})")
else:
    st.info("👆 분석을 시작하려면 성적 엑셀 파일을 업로드해 주세요.")

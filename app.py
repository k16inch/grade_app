import streamlit as st
import pandas as pd
import numpy as np

# 웹 페이지 제목 및 설명
st.set_page_config(page_title="성적 분석기", layout="centered")
st.title("📊 성적 데이터 분석 시스템")
st.markdown("특정 서식의 엑셀 파일에서 원하는 반의 성적 데이터만 추출하여 분석합니다.")

# 1. 파일 업로드 기능
uploaded_file = st.file_uploader("엑셀 파일을 업로드해 주세요 (.xlsx)", type=["xlsx"])

if uploaded_file is not None:
    try:
        # 서식에 맞춰 가공하기 위해 헤더 없이(header=None) 엑셀을 통째로 읽어옵니다.
        raw_df = pd.read_excel(uploaded_file, header=None)
        
        # ----------------------------------------------------
        # [데이터 정제] 행과 열 위치 지정 처리
        # ----------------------------------------------------
        # 5행(파이썬 인덱스 4)의 B열(인덱스 1)부터 오른쪽 끝까지가 '반' 이름
        class_labels = raw_df.iloc[4, 1:].dropna().tolist()
        
        # 6행(파이썬 인덱스 5)의 A열(인덱스 0)부터 아래로 '번호' 리스트 생성
        # 하단에 '응시생수'나 숫자가 아닌 텍스트가 나오기 전까지만 자릅니다.
        id_series = raw_df.iloc[5:, 0]
        
        # '응시생수' 행의 위치 찾기 (문자열에 '응시' 또는 '수' 등이 포함되거나 숫자가 아닌 지점)
        end_row_index = len(raw_df) # 기본값은 끝까지
        for idx, val in enumerate(id_series):
            if pd.isna(val) or (isinstance(val, str) and ('응시' in val or '합계' in val or '통계' in val)):
                end_row_index = 5 + idx  # 5행부터 시작했으므로 인덱스 보정
                break
                
        # 실제 학생 점수 데이터만 슬라이싱
        # 행: 6행(인덱스 5)부터 ~ '응시생수' 전까지
        # 열: B열(인덱스 1)부터 ~ 반 개수만큼
        score_matrix = raw_df.iloc[5:end_row_index, 1:1+len(class_labels)]
        
        # 가독성을 위해 데이터프레임 구조 재구성
        student_ids = raw_df.iloc[5:end_row_index, 0].astype(str).tolist()
        clean_df = pd.DataFrame(score_matrix.values, index=student_ids, columns=class_labels)
        
        st.success("파일 구조가 정상적으로 인식되었습니다!")
        
        # ----------------------------------------------------
        # [화면 기능] 분석할 반 선택
        # ----------------------------------------------------
        selected_class = st.selectbox("분석할 반을 선택하세요:", class_labels)
        
        # 선택된 반의 점수 데이터 추출 및 숫자로 강제 변환 (공백이나 누락 데이터 제외)
        scores = pd.to_numeric(clean_df[selected_class], errors='coerce').dropna()
        
        # 학생 목록 미리보기 (선택 사항)
        with st.expander(f"👁️ {selected_class} 데이터 확인 (총 {len(scores)}명)"):
            preview_df = pd.DataFrame({"번호": scores.index, "점수": scores.values})
            st.dataframe(preview_df, use_container_width=True, hide_index=True)
        
        st.divider()
        
        # ⚙️ 컷트라인 설정 UI
        st.subheader("⚙️ 성취점수 등급 컷트라인 설정")
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1: cutoff_A = st.number_input("A등급 이상", value=90.0, step=1.0)
        with col2: cutoff_B = st.number_input("B등급 이상", value=80.0, step=1.0)
        with col3: cutoff_C = st.number_input("C등급 이상", value=70.0, step=1.0)
        with col4: cutoff_D = st.number_input("D등급 이상", value=60.0, step=1.0)
        with col5: cutoff_E = st.number_input("E등급 이상", value=50.0, step=1.0)
        
        if st.button("📊 성적 분석 시작", type="primary"):
            st.divider()
            
            # --- [분석 1] 10점 단위 성적 분포 ---
            st.subheader(f"1️⃣ [{selected_class}] 10점 단위 성적분포인원")
            
            dist_bins = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 101]
            dist_labels = [
                '0~9점', '10~19점', '20~29점', '30~39점', '40~49점', 
                '50~59점', '60~69점', '70~79점', '80~89점', '90~100점'
            ]
            
            dist_categories = pd.cut(scores, bins=dist_bins, labels=dist_labels, right=False)
            dist_counts = dist_categories.value_counts().reindex(dist_labels, fill_value=0)
            
            df_dist = pd.DataFrame({"인원 수(명)": dist_counts})
            st.dataframe(df_dist, use_container_width=True)
            
            total_calculated = dist_counts.sum()
            st.info(f"💡 **분포 인원 합계 (총 응시학생 수): {total_calculated}명**")
            
            st.divider()
            
            # --- [분석 2] 성취 등급별 인원 ---
            st.subheader(f"2️⃣ [{selected_class}] 성취점수 등급별 인원")
            
            grade_bins = [-1, cutoff_E, cutoff_D, cutoff_C, cutoff_B, cutoff_A, 101]
            grade_labels = ['미도달', 'E등급', 'D등급', 'C등급', 'B등급', 'A등급']
            
            grade_categories = pd.cut(scores, bins=grade_bins, labels=grade_labels, right=False)
            grade_counts = grade_categories.value_counts().reindex(reversed(grade_labels), fill_value=0)
            
            df_grade = pd.DataFrame({"인원 수(명)": grade_counts})
            st.dataframe(df_grade, use_container_width=True)
            st.bar_chart(df_grade)
            
    except Exception as e:
        st.error(f"데이터를 처리하는 중 오류가 발생했습니다. 파일 형식을 확인해 주세요. (오류 내용: {e})")
else:
    st.info("👆 분석을 시작하려면 성적 엑셀 파일을 업로드해 주세요.")

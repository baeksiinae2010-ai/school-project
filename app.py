import streamlit as st
from supabase import create_client
import re
import pandas as pd

# 1. Supabase 연결 설정
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# 2. 다음 ID(S_001, S_002...)를 생성하는 함수 (가장 높은 숫자 기준 +1)
def get_next_id():
    try:
        response = supabase.table("student_survey").select("id").execute()
        data = response.data
        if not data: return "S_001"
        nums = []
        for item in data:
            match = re.search(r'S_(\d+)', item['id'])
            if match: nums.append(int(match.group(1)))
        if not nums: return "S_001"
        next_num = max(nums) + 1
        return f"S_{next_num:03d}"
    except: return "S_ERR"

# 3. 사이드바 메뉴 설정
st.sidebar.title("메뉴")
page = st.sidebar.radio("페이지 선택", ["설문 참여", "데이터 분석"])

# --- [페이지 1: 설문 참여 페이지] ---
if page == "설문 참여":
    st.title("학생 생활 설문조사")
    st.markdown("작성해주신 응답은 연구 목적으로만 활용됩니다.")
    
    # 빈 공간(placeholder)을 만들어서 현재 할당될 S_ 번호를 화면 상단에 표시
    current_id = get_next_id()
    id_display = st.empty()
    id_display.info(f"📌 현재 할당된 설문 번호: **{current_id}**")

    with st.form("survey_form", clear_on_submit=True):
        st.subheader("설문지 작성")
        
        grade_options = [f"{g}-{c}" for g in range(1, 4) for c in range(1, 13)]
        grade_class = st.selectbox("학년-반 선택", options=["선택하세요..."] + grade_options)
        
        sleep_hours = st.slider("평균 수면 시간 (시간)", 0.0, 24.0, 7.0, 0.5)
        phone_hours = st.slider("평균 스마트폰 사용 시간 (시간)", 0.0, 24.0, 3.0, 0.5)
        breakfast = st.radio("아침 식사를 하셨나요?", ["예", "아니오"], horizontal=True)
        commute_minutes = st.number_input("통학 시간 (분)", min_value=0, max_value=180, value=30)
        tired_score = st.select_slider("피곤함 정도 (1: 아주 상쾌함 ~ 10: 매우 피곤함)", options=list(range(1, 11)), value=5)
        focus_score = st.select_slider("수업 집중도 (1: 전혀 안됨 ~ 10: 매우 잘됨)", options=list(range(1, 11)), value=7)
        favorite_subject = st.selectbox("가장 좋아하는 과목", ["국어", "수학", "영어", "과학", "사회", "체육", "음악", "미술", "정보", "기타"])

        submitted = st.form_submit_button("설문지 제출하기")

        if submitted:
            if grade_class == "선택하세요...":
                st.error("학년-반 정보를 선택해주세요!")
            else:
                new_data = {
                    "id": current_id, 
                    "grade_class": grade_class, 
                    "sleep_hours": sleep_hours,
                    "phone_hours": phone_hours, 
                    "breakfast": "YES" if breakfast == "예" else "NO", 
                    "commute_minutes": commute_minutes,
                    "tired_score": tired_score, 
                    "focus_score": focus_score, 
                    "favorite_subject": favorite_subject
                }
                try:
                    supabase.table("student_survey").insert(new_data).execute()
                    st.success(f"성공적으로 제출되었습니다! (관리 번호: {current_id})")
                    
                    # 제출 완료 후 다음 사람을 위해 번호 즉시 업데이트
                    next_id = get_next_id()
                    id_display.info(f"📌 현재 할당된 설문 번호: **{next_id}**")
                except Exception as e:
                    st.error(f"저장 오류 발생: {e}")

# --- [페이지 2: 데이터 분석 페이지] ---
elif page == "데이터 분석":
    st.title("설문 데이터 분석")
    st.markdown("수집된 데이터를 실시간으로 시각화합니다.")

    try:
        response = supabase.table("student_survey").select("*").execute()
        if response.data:
            df = pd.DataFrame(response.data)
            
            col1, col2, col3 = st.columns(3)
            col1.metric("총 응답 수", f"{len(df)}명")
            col2.metric("평균 수면 시간", f"{df['sleep_hours'].mean():.1f}시간")
            col3.metric("평균 피곤함", f"{df['tired_score'].mean():.1f}점")
            
            st.divider()

            st.subheader("과목별 선호도 분포")
            subject_counts = df['favorite_subject'].value_counts()
            st.bar_chart(subject_counts)

            st.subheader("전체 응답 데이터 리스트")
            st.dataframe(df.sort_values(by="id", ascending=False), use_container_width=True)
            
        else:
            st.warning("아직 수집된 데이터가 없습니다.")
    except Exception as e:
        st.error(f"데이터 로드 오류: {e}")
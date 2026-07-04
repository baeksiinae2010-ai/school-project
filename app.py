import streamlit as st
from supabase import create_client
import datetime

# 1. Supabase 연결 설정 (Streamlit Secrets 보안 저장소에서 불러오기)
@st.cache_resource
def init_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_supabase()

# 2. 웹화면 UI 디자인
st.set_page_config(page_title="학생 생활 패턴 설문조사", layout="centered")
st.title("📊 학생 생활 패턴 설문조사")
st.write("여러분의 일상적인 생활 패턴을 입력해주세요. 데이터는 통계 목적으로만 사용됩니다.")

# 설문지 폼 시작
with st.form("survey_form", clear_on_submit=True):
    st.subheader("📝 설문 내용 입력")
    
    # 학반 입력 (예: 1-1, 1-2 등)
    grade_class = st.text_input("학반 (예: 1-1)", placeholder="학년-반 형식으로 입력하세요")
    
    # 수면 시간 (소수점 입력 가능)
    sleep_hours = st.number_input("하루 평균 수면 시간 (시간)", min_value=0.0, max_value=24.0, value=7.0, step=0.5)
    
    # 스마트폰 사용 시간
    phone_hours = st.number_input("하루 평균 스마트폰 사용 시간 (시간)", min_value=0.0, max_value=24.0, value=3.0, step=0.5)
    
    # 아침 식사 여부
    breakfast = st.radio("아침 식사를 하셨나요?", ["YES", "NO"], index=0)
    
    # 등교 소요 시간
    commute_minutes = st.number_input("등교하는 데 걸리는 시간 (분)", min_value=0, max_value=180, value=30, step=5)
    
    # 제출 버튼
    submitted = st.form_submit_button("설문지 제출하기")

# 3. 데이터 저장 로직
if submitted:
    if not grade_class:
        st.error("학반 정보를 입력해주세요!")
    else:
        # 중복 에러(23505)를 피하기 위해 중복되지 않는 고유한 ID 생성 (예: s_현재시간타임스탬프)
        unique_id = f"s_{int(datetime.datetime.now().timestamp())}"
        
        # Supabase에 데이터 보낼 상자(딕셔너리) 만들기
        survey_data = {
            "id": unique_id,
            "grade_class": grade_class,
            "sleep_hours": sleep_hours,
            "phone_hours": phone_hours,
            "breakfast": breakfast,
            "commute_minutes": int(commute_minutes)
        }
        
        try:
            # student_survey 테이블에 데이터 한 줄 집어넣기
            response = supabase.table("student_survey").insert(survey_data).execute()
            
            st.success("🎉 설문조사가 성공적으로 제출되었습니다! 감사합니다.")
            st.balloons()
        except Exception as e:
            st.error(f"데이터 저장 중 오류가 발생했습니다: {e}")

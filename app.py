import streamlit as st
from supabase import create_client
import re

# 1. Supabase 연결 설정
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# 2. 다음 ID(S_XXX)를 생성하는 함수
def get_next_id():
    try:
        # DB에서 모든 ID 가져오기
        response = supabase.table("student_survey").select("id").execute()
        data = response.data
        
        if not data:
            return "S_001"
        
        # ID들 중에서 숫자 부분만 추출 (예: 'S_005' -> 5)
        nums = []
        for item in data:
            match = re.search(r'S_(\d+)', item['id'])
            if match:
                nums.append(int(match.group(1)))
        
        if not nums:
            return "S_001"
            
        # 가장 큰 숫자에 +1
        next_num = max(nums) + 1
        # S_와 함께 3자리 숫자로 포맷팅 (예: S_006)
        return f"S_{next_num:03d}"
    except Exception as e:
        return "S_ERR"

# 3. 화면 UI 구성
st.set_page_config(page_title="학생 생활 설문조사", layout="centered")

st.title("🏫 학교 생활 설문조사")
st.markdown("여러분의 소중한 응답은 연구 자료로만 활용됩니다.")

with st.form("survey_form", clear_on_submit=True):
    st.subheader("📝 설문 내용 입력")
    
    # 학반 입력 (직접 쓰기)
    grade_class = st.text_input("학반 (예: 1-1)", placeholder="학년-반 형식으로 입력하세요")
    
    # 시간 관련 (슬라이더 - 범위 조절이 쉬움)
    sleep_hours = st.slider("하루 평균 수면 시간 (시간)", 0.0, 24.0, 7.0, 0.5)
    phone_hours = st.slider("하루 평균 스마트폰 사용 시간 (시간)", 0.0, 24.0, 3.0, 0.5)
    
    # 생활 습관 (라디오 버튼 / 숫자 입력)
    breakfast = st.radio("아침 식사를 하셨나요?", ["YES", "NO"], horizontal=True)
    commute_minutes = st.number_input("등교하는 데 걸리는 시간 (분)", min_value=0, max_value=180, value=30)
    
    # 심리/상태 (선택형 슬라이더 - 1~10 점수)
    tired_score = st.select_slider("현재 피곤함 정도 (1: 아주 상쾌함 ~ 10: 매우 피곤함)", options=list(range(1, 11)), value=5)
    concentration_score = st.select_slider("수업 집중도 점수 (1: 전혀 안됨 ~ 10: 매우 잘됨)", options=list(range(1, 11)), value=7)
    
    # 선호 과목 (드롭다운 셀렉트박스)
    favorite_subject = st.selectbox("가장 좋아하는 과목", ["국어", "수학", "영어", "과학", "사회", "체육", "음악", "미술", "정보", "기타"])

    # 제출 버튼
    submitted = st.form_submit_button("설문지 제출하기")

    if submitted:
        if not grade_class:
            st.error("학반 정보를 입력해주세요!")
        else:
            # 4. 데이터 저장 로직
            next_id = get_next_id()
            
            new_data = {
                "id": next_id,
                "grade_class": grade_class,
                "sleep_hours": sleep_hours,
                "phone_hours": phone_hours,
                "breakfast": breakfast,
                "commute_minutes": commute_minutes,
                "tired_score": tired_score,
                "concentration_score": concentration_score,
                "favorite_subject": favorite_subject
            }
            
            try:
                response = supabase.table("student_survey").insert(new_data).execute()
                st.success(f"성공적으로 저장되었습니다! (관리 번호: {next_id})")
                st.balloons()
            except Exception as e:
                st.error(f"데이터 저장 중 오류가 발생했습니다: {e}")

st.info("※ 참고: 제출 후에는 수정이 불가능하니 신중하게 입력해 주세요.")

### ✅ 다음 할 일 (매우 중요!)
코드에 `id`를 직접 넣는 로직을 추가했기 때문에, 아까 보셨던 **RLS 에러**가 나지 않으려면 Supabase에서 정책(Policy) 설정을 완료해야 합니다.

1.  **Supabase Table Editor**로 가서 `student_survey` 테이블을 엽니다.
2.  상단의 **`RLS`** 또는 **`Policies`** 버튼을 누릅니다.
3.  **`New Policy`** -> **`INSERT`** 선택 -> Target Roles를 **`anon`**으로 설정 -> 저장.

이렇게 하면 이제 에러 없이 데이터가 아주 잘 저장될 거예요! 코드를 붙여넣고 테스트해 보신 뒤 결과를 알려주세요.
import streamlit as st
from supabase import create_client
import re
import pandas as pd

# 1. Supabase Connection Setup
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# 2. Function to generate next ID (S_001, S_002...)
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

# 3. Sidebar Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select Page", ["Survey", "Analysis"])

# --- [Page 1: Survey Page] ---
if page == "Survey":
    st.title("Student School Survey")
    st.markdown("Your responses will be used for research purposes only.")

    with st.form("survey_form", clear_on_submit=True):
        st.subheader("Survey Form")
        
        # Grade/Class Selection Widget
        grade_options = [f"{g}-{c}" for g in range(1, 4) for c in range(1, 13)]
        grade_class = st.selectbox("Select Grade-Class", options=["Select..."] + grade_options)
        
        sleep_hours = st.slider("Avg. Sleep Hours", 0.0, 24.0, 7.0, 0.5)
        phone_hours = st.slider("Avg. Phone Usage Hours", 0.0, 24.0, 3.0, 0.5)
        breakfast = st.radio("Did you have breakfast?", ["YES", "NO"], horizontal=True)
        commute_minutes = st.number_input("Commute Time (minutes)", min_value=0, max_value=180, value=30)
        tired_score = st.select_slider("Tiredness Score (1: Fresh ~ 10: Exhausted)", options=list(range(1, 11)), value=5)
        focus_score = st.select_slider("Focus Score (1: Low ~ 10: High)", options=list(range(1, 11)), value=7)
        favorite_subject = st.selectbox("Favorite Subject", ["Korean", "Math", "English", "Science", "Social", "PE", "Music", "Art", "IT", "Other"])

        submitted = st.form_submit_button("Submit Survey")

        if submitted:
            if grade_class == "Select...":
                st.error("Please select your Grade-Class!")
            else:
                next_id = get_next_id()
                new_data = {
                    "id": next_id, "grade_class": grade_class, "sleep_hours": sleep_hours,
                    "phone_hours": phone_hours, "breakfast": breakfast, "commute_minutes": commute_minutes,
                    "tired_score": tired_score, "focus_score": focus_score, "favorite_subject": favorite_subject
                }
                try:
                    supabase.table("student_survey").insert(new_data).execute()
                    st.success(f"Success! (Ref ID: {next_id})")
                except Exception as e:
                    st.error(f"Save Error: {e}")

# --- [Page 2: Analysis Page] ---
elif page == "Analysis":
    st.title("Survey Data Analysis")
    st.markdown("Real-time data visualization from Supabase.")

    try:
        response = supabase.table("student_survey").select("*").execute()
        if response.data:
            df = pd.DataFrame(response.data)
            
            # Summary Metrics
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Responses", f"{len(df)}")
            col2.metric("Avg. Sleep", f"{df['sleep_hours'].mean():.1f}h")
            col3.metric("Avg. Tiredness", f"{df['tired_score'].mean():.1f}")
            
            st.divider()

            # Chart: Favorite Subject
            st.subheader("Subject Preference")
            subject_counts = df['favorite_subject'].value_counts()
            st.bar_chart(subject_counts)

            # Data Table
            st.subheader("Full Data List")
            st.dataframe(df.sort_values(by="id", ascending=False), use_container_width=True)
            
        else:
            st.warning("No data found.")
    except Exception as e:
        st.error(f"Load Error: {e}")

st.sidebar.info("baeksiinae2010-ai | School Project")
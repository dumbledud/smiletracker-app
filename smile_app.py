import streamlit as st
import datetime
import random
import pandas as pd

# Mock AI smile and shot detection result generator
def analyze_video_mock(video_name):
    results = []
    for i in range(30):
        shot_made = True  # Assume all shots in the set are made
        smile_detected = random.choice([True, False])  # Randomly simulate smile detection
        results.append({
            'Shot Number': i + 1,
            'Shot Made': shot_made,
            'Smile Detected': smile_detected,
            'Timestamp': (datetime.datetime.now() + datetime.timedelta(seconds=i*5)).strftime('%H:%M:%S')
        })
    return results

# Streamlit app interface
st.set_page_config(page_title="SmileTracker", layout="centered")

st.title("🏀 SmileTracker: 30-for-30 Hoop Joy")

st.markdown("""
Upload your video taken from behind the hoop using your iPhone.  
I'll analyze it for **30 made shots** and check if you were **smiling** on each one!
""")

uploaded_video = st.file_uploader("🎥 Upload your video", type=["mp4", "mov", "avi"])

if uploaded_video:
    st.video(uploaded_video)

    st.success("Video uploaded! Ready to analyze...")

    with st.spinner("Running smile + shot detection AI... (simulated)"):
        analysis_results = analyze_video_mock(uploaded_video.name)

    st.subheader("📊 Shot & Smile Summary")

    smile_count = sum(1 for r in analysis_results if r['Smile Detected'])
    st.metric("Smiling Shots", f"{smile_count}/30")

    df_results = pd.DataFrame(analysis_results)
    st.dataframe(df_results)

    # Award badges
    st.subheader("🏅 Badges Earned")

    if smile_count == 30:
        st.success("🏅 30 Joys – Perfect positivity!")
    elif smile_count >= 20:
        st.info("🏅 Consistency Star – 20+ smiles")
    else:
        st.warning("😊 Keep practicing smiling through your shots!")

    if df_results.iloc[0]['Smile Detected'] is False and df_results.iloc[-1]['Smile Detected'] is True:
        st.success("🏅 Quick Reset – You turned it around!")

    if smile_count >= 5 and smile_count < 30:
        st.info("🏅 Streak Seeker – Keep it going tomorrow!")

else:
    st.info("⬆️ Upload a video to begin analysis.")

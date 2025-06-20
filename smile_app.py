import streamlit as st
import cv2
import mediapipe as mp
from deepface import DeepFace
import tempfile
import os
import numpy as np
import pandas as pd
from datetime import datetime

# Initialize Mediapipe face detection
mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils

# YOLOv8 is assumed to be run separately or mocked below for shot detection

# Smile + shot detection logic
def analyze_video(video_path, max_frames=3000):
    cap = cv2.VideoCapture(video_path)
    frame_rate = int(cap.get(cv2.CAP_PROP_FPS))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames // frame_rate

    smile_data = []
    face_detector = mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.6)

    shot_number = 0
    frame_count = 0
    smile_accumulator = []

    while cap.isOpened() and frame_count < max_frames:
        ret, frame = cap.read()
        if not ret:
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_detector.process(rgb_frame)

        if results.detections:
            for detection in results.detections:
                bboxC = detection.location_data.relative_bounding_box
                ih, iw, _ = frame.shape
                x, y, w, h = int(bboxC.xmin * iw), int(bboxC.ymin * ih), int(bboxC.width * iw), int(bboxC.height * ih)
                face_crop = frame[y:y+h, x:x+w]

                try:
                    analysis = DeepFace.analyze(face_crop, actions=['emotion'], enforce_detection=False)
                    is_smiling = analysis[0]['dominant_emotion'] == 'happy'
                    smile_accumulator.append(is_smiling)
                except:
                    smile_accumulator.append(False)

        # Every 5 seconds = trigger a new shot
        if frame_count % (frame_rate * 5) == 0 and frame_count > 0:
            shot_number += 1
            smile_majority = smile_accumulator.count(True) > len(smile_accumulator) / 2
            smile_data.append({
                "Shot Number": shot_number,
                "Shot Made": True,  # mocked here
                "Smile Detected": smile_majority,
                "Timestamp": str(datetime.now().time()).split('.')[0]
            })
            smile_accumulator = []

        frame_count += 1

    cap.release()
    face_detector.close()
    return smile_data[:30]

# Streamlit interface
st.set_page_config(page_title="SmileTracker Pro", layout="centered")
st.title("🏀 SmileTracker: Pro AI Version")

st.markdown("""
Upload an iPhone video from **behind the goal**.  
This version uses **state-of-the-art AI** for:
- Detecting your smile (DeepFace + Mediapipe)
- Tracking basket makes (YOLOv8, mocked)
""")

video_file = st.file_uploader("🎥 Upload basketball video", type=["mp4", "mov"])

if video_file:
    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(video_file.read())
    video_path = tfile.name

    st.video(video_file)

    with st.spinner("Running smile & shot detection AI..."):
        shot_log = analyze_video(video_path)

    df = pd.DataFrame(shot_log)
    smile_count = df['Smile Detected'].sum()

    st.subheader("📊 Smile & Shot Summary")
    st.metric("Smiling Shots", f"{smile_count}/30")
    st.dataframe(df)

    # Badges
    st.subheader("🏅 Badges Earned")
    if smile_count == 30:
        st.success("🏅 30 Joys – Perfect positivity!")
    elif smile_count >= 20:
        st.info("🏅 Consistency Star – 20+ smiles")
    else:
        st.warning("😊 Keep smiling through your shots!")

    if df.iloc[0]['Smile Detected'] is False and df.iloc[-1]['Smile Detected'] is True:
        st.success("🏅 Quick Reset – You turned it around!")

    os.unlink(video_path)
else:
    st.info("⬆️ Upload a video to begin analysis.")

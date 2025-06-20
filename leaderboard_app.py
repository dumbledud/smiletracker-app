import pandas as pd
import datetime
from pathlib import Path
import json
import streamlit as st

# Directory to simulate database
LEADERBOARD_DIR = Path("leaderboard_data")
LEADERBOARD_DIR.mkdir(exist_ok=True)

# Save session data
def save_score(name, smile_count):
    today = datetime.date.today().isoformat()
    data = {
        "name": name,
        "smile_count": smile_count,
        "date": today
    }
    file_path = LEADERBOARD_DIR / f"{name}_{today}.json"
    with open(file_path, "w") as f:
        json.dump(data, f)

# Load all leaderboard entries
def load_leaderboard():
    entries = []
    for file in LEADERBOARD_DIR.glob("*.json"):
        with open(file, "r") as f:
            try:
                data = json.load(f)
                entries.append(data)
            except:
                continue
    return pd.DataFrame(entries)

# Streamlit interface
st.set_page_config(page_title="🏆 SmileTracker Leaderboard", layout="centered")
st.title("🏆 SmileTracker Family Leaderboard")

with st.form("submit_score_form"):
    name = st.text_input("Your name")
    smile_count = st.slider("How many smiles did you get out of 30?", 0, 30, 15)
    submitted = st.form_submit_button("Submit Score")
    if submitted and name:
        save_score(name, smile_count)
        st.success(f"Score for {name} saved!")

# Load and display leaderboard
df = load_leaderboard()
if not df.empty:
    df = df.sort_values(by=["smile_count", "date"], ascending=[False, True])
    st.subheader("🏅 Current Rankings")
    st.dataframe(df.reset_index(drop=True))
else:
    st.info("No scores submitted yet. Be the first to track your smiling shots!")

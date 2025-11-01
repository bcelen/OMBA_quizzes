import streamlit as st
import pandas as pd
import numpy as np
import requests
from scipy.stats import norm
import matplotlib.pyplot as plt

st.set_page_config(page_title="Weekly Quiz Adjustment", layout="wide")

st.title("📊 Weekly Quiz Adjustment Dashboard")

# --- User Input ---
week_labels = [f"Week {i} Quiz results" for i in range(1, 7)]
week_files = [f"week{i}.csv" for i in range(1, 7)]

with st.container():
    col1, col2, col3 = st.columns([2, 2, 3])
    with col1:
        week_selection = st.selectbox("Select a quiz week:", options=week_labels)
    with col2:
        target_mean = st.slider("🎯 Adjusted Average (Target)", min_value=7.4, max_value=7.6, value=7.5, step=0.01)
    with col3:
        target_pct_above_8 = st.slider("🔥 Max % of Adjusted Scores ≥ 8.0", min_value=0.20, max_value=0.30, value=0.30, step=0.01)

week_index = week_labels.index(week_selection)
filename = week_files[week_index]

# --- Download Raw CSV from GitHub ---
github_url = f"https://raw.githubusercontent.com/bcelen/weekly_quizzes/main/{filename}"

try:
    df = pd.read_csv(github_url)
    raw_scores = df.iloc[:, 0].dropna()
    raw_scores = pd.to_numeric(raw_scores, errors='coerce')
    raw_scores = raw_scores.dropna()
    raw_scores = np.clip(raw_scores.values, 0, 10)

    st.success(f"✅ Loaded {filename} with {len(raw_scores)} valid scores.")

    # --- Compute Z Scores ---
    z_scores = (raw_scores - np.mean(raw_scores)) / np.std(raw_scores)

    # --- Find std dev to cap % > 8 at user-specified level ---
    z_threshold = norm.ppf(1 - target_pct_above_8)
    required_std = (8 - target_mean) / z_threshold

    adjusted_scores = np.clip(z_scores * required_std + target_mean, 0, 10)

    # --- Sort by original scores ---
    sorted_indices = np.argsort(raw_scores)
    raw_sorted = raw_scores[sorted_indices]
    adjusted_sorted = adjusted_scores[sorted_indices]

    # --- Summary Statistics ---
    pct_above_8 = np.mean(adjusted_scores >= 8) * 100
    summary = {
        "📦 Students": len(raw_scores),
        "🎯 Target Mean": round(target_mean, 2),
        "📐 Adjusted Mean": round(np.mean(adjusted_scores), 2),
        "📊 Adjusted Std Dev": round(np.std(adjusted_scores), 2),
        "🔥 % ≥ 8.0": f"{pct_above_8:.1f}%"
    }

    st.subheader("Summary")
    st.dataframe(pd.DataFrame([summary]))

    # --- Line Graph ---
    st.subheader("📈 Student Scores (Raw vs Adjusted, Sorted by Raw Scores)")
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(range(len(raw_sorted)), raw_sorted, marker='o', linestyle='-', label='Original', color='gray')
    ax.plot(range(len(adjusted_sorted)), adjusted_sorted, marker='o', linestyle='-', label='Adjusted', color='blue')
    ax.set_ylim(0, 10)
    ax.set_xlabel("Student Index (Sorted by Original Score)")
    ax.set_ylabel("Score")
    ax.set_title("Student Marks: Raw vs Adjusted")
    ax.legend()
    st.pyplot(fig)

    # --- Table Output ---
    st.subheader("Raw vs Adjusted Scores")
    table_df = pd.DataFrame({
        "Original Score": np.round(raw_scores, 2),
        "Adjusted Score": np.round(adjusted_scores, 2)
    })
    st.dataframe(table_df, use_container_width=True)

    # --- Download Option ---
    csv = table_df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download Adjusted Scores CSV", data=csv, file_name=f"{filename.replace('.csv', '')}_adjusted.csv")

except Exception:
    st.warning("⚠️ The quiz marks are not available yet. Please check back later.")

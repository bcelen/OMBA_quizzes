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
    actual_summary = {
        "📦 Students": len(raw_scores),
        "🎯 Mean": round(np.mean(raw_scores), 2),
        "📐 Std Dev": round(np.std(raw_scores), 2),
        "🔥 % ≥ 8.0": f"{np.mean(raw_scores >= 8) * 100:.1f}%"
    }

    adjusted_summary = {
        "📦 Students": len(adjusted_scores),
        "🎯 Mean": round(np.mean(adjusted_scores), 2),
        "📐 Std Dev": round(np.std(adjusted_scores), 2),
        "🔥 % ≥ 8.0": f"{np.mean(adjusted_scores >= 8) * 100:.1f}%"
    }

    summary_df = pd.DataFrame([actual_summary, adjusted_summary], index=["Actual Scores", "Adjusted Scores"])

    st.subheader("Summary")
    st.dataframe(summary_df)

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

    # --- Personal Score Lookup ---
    st.subheader("🔍 Find Your Adjusted Score and Rank")
    with st.form("lookup_form"):
        user_score = st.number_input("Enter your actual quiz score (0-10):", min_value=0.0, max_value=10.0, step=0.1)
        submitted = st.form_submit_button("Find My Adjusted Score")

    if submitted:
        user_z = (user_score - np.mean(raw_scores)) / np.std(raw_scores)
        user_adjusted = round(np.clip(user_z * required_std + target_mean, 0, 10), 2)
        rank = int(np.sum(adjusted_scores > user_adjusted)) + 1
        total = len(adjusted_scores)
        st.info(f"Your adjusted score is: **{user_adjusted}**\n\nYour rank is: **{rank}** out of {total} students.")

        # --- Add marker to plot ---
        fig2, ax2 = plt.subplots(figsize=(10, 4))
        ax2.plot(range(len(raw_sorted)), raw_sorted, marker='o', linestyle='-', label='Original', color='gray')
        ax2.plot(range(len(adjusted_sorted)), adjusted_sorted, marker='o', linestyle='-', label='Adjusted', color='blue')
        ax2.axhline(user_adjusted, color='red', linestyle='--', linewidth=1, label='Your Adjusted Score')
        ax2.set_ylim(0, 10)
        ax2.set_xlabel("Student Index (Sorted by Original Score)")
        ax2.set_ylabel("Score")
        ax2.set_title("Your Score in Context")
        ax2.legend()
        st.pyplot(fig2)

except Exception:
    st.warning("⚠️ The quiz marks are not available yet. Please check back later.")

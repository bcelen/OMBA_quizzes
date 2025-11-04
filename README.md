# 📊 Weekly Quiz Results Dashboard

This Streamlit app provides an interactive visualization and adjustment tool for weekly quiz results in the Online MBA program.

## 🎯 Purpose

The dashboard enables students to:

- View the distribution of original and adjusted quiz marks.
- Understand how MBS grading policies affect their final marks.
- Explore statistical summaries of each quiz week.
- Estimate their adjusted mark and rank by entering their original mark.

## 🧮 Adjustment Methodology

MBS grade policy requires that:

- The **mean of final marks (out of 100)** lies between **74 and 76** (equivalent to 7.4–7.6 out of 10).
- The **percentage of marks above 8** (i.e. H1) does **not exceed 30%**.

This dashboard applies a linear transformation to preserve the original **z-scores** while adjusting the distribution to match these constraints. The adjustments are **indicative** and may change later due to administrative updates (e.g., revised zero marks after the consensus date).

## 📦 Data Source

Each week's quiz results are stored as a CSV file in the associated GitHub repository:
- Format: `week1.csv`, `week2.csv`, ..., `week6.csv`
- Each file contains a single column of student marks (out of 10)

The app dynamically fetches data based on the selected week.

## 📈 Features

- **Interactive week selection** via dropdown
- **Customizable target mean and H1 cap** using sliders
- **Side-by-side plots** of original and adjusted mark distributions
- **Summary statistics** (mean, standard deviation) for both versions
- **Student mark lookup** to see adjusted result and class rank
- **Visual indicators** for personal original and adjusted marks on the distribution chart

## 🛠️ Technologies

- [Streamlit](https://streamlit.io/) for UI
- [Pandas](https://pandas.pydata.org/) and [NumPy](https://numpy.org/) for data handling
- [Matplotlib](https://matplotlib.org/) for plotting
- [SciPy](https://scipy.org/) for normal distribution transformations

## 📁 File Structure
.
├── app.py                # Main Streamlit application
├── about.md              # Project overview (this file)
├── week1.csv             # Weekly quiz data
├── week2.csv
…
## 🚨 Disclaimer

This tool is for **informational purposes only**. The final mark distributions may change after moderation, re-marking, or exclusion of incomplete assessments. Students should refer to official Canvas announcements for final grades.

---

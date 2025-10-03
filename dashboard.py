import streamlit as st
import pandas as pd
import os
import datetime
import matplotlib.pyplot as plt

st.set_page_config(page_title="Smart Attendance Dashboard", layout="wide")
st.title("📊 Smart Attendance Dashboard")

ATTENDANCE_DIR = "attendance"

# Select today's date by default
today = datetime.date.today().strftime("%Y-%m-%d")
files = [f for f in os.listdir(ATTENDANCE_DIR) if f.endswith(".csv")]

if not files:
    st.warning("⚠️ No attendance records found yet!")
else:
    # Pick a file to view
    selected = st.selectbox("Select a date file", sorted(files, reverse=True), index=0)
    df = pd.read_csv(os.path.join(ATTENDANCE_DIR, selected))

    st.subheader(f"Attendance for {selected.replace('.csv','')}")

    # ✅ Attendance summary
    total_present = len(df["Name"].unique())
    st.metric("Total Present", total_present)

    # Show list of students
    st.write("### ✅ Present Students:")
    st.write(", ".join(df["Name"].unique()))

    # 📊 Attendance Chart
    fig, ax = plt.subplots()
    df["Name"].value_counts().plot(kind="bar", ax=ax)
    ax.set_xlabel("Students")
    ax.set_ylabel("Marked Count")
    ax.set_title("Attendance Marking Frequency")
    st.pyplot(fig)

    # If you have a master list of all students, you can calculate absentees:
    # all_students = ["Arjun", "Priya", "Ravi", "Sneha"]
    # absent = set(all_students) - set(df["Name"].unique())
    # st.write("### ❌ Absent Students:", ", ".join(absent))

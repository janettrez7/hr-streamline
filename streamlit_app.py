# streamlit_app.py
import streamlit as st
import zipfile
import tempfile
import os
import pandas as pd
from resume_scorer import process_and_score_resumes_from_text

st.set_page_config(page_title="Resume Scorer", layout="centered")
st.title("📄 AI Resume Scorer")
st.write("Enter Job Description and upload a ZIP of resumes. Get scores based on JD criteria.")

# New: JD input as text box
jd_text_input = st.text_area("Paste the Job Description here", height=250)

# Upload resume ZIP
resume_zip = st.file_uploader("Upload Resumes (ZIP with PDF/DOCX files)", type="zip")

if st.button("Run Scoring") and jd_text_input and resume_zip:
    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = os.path.join(tmpdir, resume_zip.name)
        with open(zip_path, "wb") as f:
            f.write(resume_zip.read())

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            resume_dir = os.path.join(tmpdir, "resumes")
            zip_ref.extractall(resume_dir)

        results = process_and_score_resumes_from_text(jd_text_input, resume_dir)

        if results.empty:
            st.warning("No valid resumes processed or no match found with JD.")
        else:
            st.success("Scoring Complete!")
            st.dataframe(results, use_container_width=True)

            csv = results.to_csv(index=False).encode("utf-8")
            st.download_button("Download Results as CSV", csv, "resume_scores.csv", "text/csv")

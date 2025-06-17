# streamlit_app.py
import streamlit as st
import zipfile
import tempfile
import os
import pandas as pd
from resume_scorer import process_and_score_resumes

st.set_page_config(page_title="Resume Scorer", layout="centered")
st.title("📄 AI Resume Scorer")
st.write("Upload a JD and a ZIP of resumes. Get scores based on the JD criteria.")

jd_file = st.file_uploader("Upload Job Description (PDF/DOCX/TXT)", type=["pdf", "docx", "txt"])
resume_zip = st.file_uploader("Upload Resumes (ZIP with PDF/DOCX files)", type="zip")

if st.button("Run Scoring") and jd_file and resume_zip:
    with tempfile.TemporaryDirectory() as tmpdir:
        jd_path = os.path.join(tmpdir, jd_file.name)
        with open(jd_path, "wb") as f:
            f.write(jd_file.read())

        zip_path = os.path.join(tmpdir, resume_zip.name)
        with open(zip_path, "wb") as f:
            f.write(resume_zip.read())

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(os.path.join(tmpdir, "resumes"))

        results = process_and_score_resumes(jd_path, os.path.join(tmpdir, "resumes"))

        if results.empty:
            st.warning("No valid resumes processed or no match found with JD.")
        else:
            st.success("Scoring Complete!")
            st.dataframe(results, use_container_width=True)

            csv = results.to_csv(index=False).encode("utf-8")
            st.download_button("Download Results as CSV", csv, "resume_scores.csv", "text/csv")

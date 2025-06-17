# streamlit_app.py
import streamlit as st
import os
import tempfile
import zipfile
import pandas as pd
from resume_scorer import process_and_score_resumes

st.title("🧠 Resume Scorer - AI Powered")

jd_file = st.file_uploader("Upload Job Description (PDF/DOCX/TXT)", type=["pdf", "docx", "txt"])
resumes_zip = st.file_uploader("Upload Resumes as ZIP (PDF/DOCX)", type="zip")

if jd_file and resumes_zip:
    with tempfile.TemporaryDirectory() as tmpdir:
        jd_path = os.path.join(tmpdir, jd_file.name)
        with open(jd_path, "wb") as f:
            f.write(jd_file.read())

        zip_path = os.path.join(tmpdir, resumes_zip.name)
        with open(zip_path, "wb") as f:
            f.write(resumes_zip.read())

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(os.path.join(tmpdir, "resumes"))

        results = process_and_score_resumes(jd_path, os.path.join(tmpdir, "resumes"))

        if not results.empty:
            st.success("Scoring Complete!")
            st.dataframe(results)
            st.download_button("Download CSV", results.to_csv(index=False), file_name="scored_resumes.csv")
        else:
            st.warning("No valid resumes found or JD/resumes were unreadable.")

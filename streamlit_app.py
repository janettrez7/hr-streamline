import streamlit as st
import zipfile
import os
import tempfile
from resume_scorer import process_and_score_resumes

st.title("🧠 Resume Scoring Tool")
st.markdown("Upload a Job Description and a ZIP file of resumes to get scores.")

jd_file = st.file_uploader("Upload Job Description (PDF or TXT)", type=["pdf", "txt"])
resume_zip = st.file_uploader("Upload ZIP of Resumes (PDF or DOCX)", type="zip")

if st.button("Score Resumes") and jd_file and resume_zip:
    with tempfile.TemporaryDirectory() as tmpdir:
        jd_path = os.path.join(tmpdir, jd_file.name)
        zip_path = os.path.join(tmpdir, resume_zip.name)

        with open(jd_path, "wb") as f:
            f.write(jd_file.read())
        with open(zip_path, "wb") as f:
            f.write(resume_zip.read())

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(os.path.join(tmpdir, "resumes"))

        results = process_and_score_resumes(jd_path, os.path.join(tmpdir, "resumes"))

        st.success("Scoring Complete!")
        st.dataframe(results)

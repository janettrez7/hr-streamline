import streamlit as st
import tempfile
import os
import pandas as pd
from resume_scorer import process_and_score_resumes

st.set_page_config(page_title="Resume Scorer", layout="centered")
st.title("📄 AI Resume Scorer")
st.write("Paste your JD criteria and upload a resume (PDF/DOCX).")

# JD criteria input
jd_text = st.text_area("Paste Job Description Criteria (one skill per line or separated by commas):")

# Single resume uploader
resume_file = st.file_uploader("Upload a Resume (PDF/DOCX)", type=["pdf", "docx"])

if st.button("Run Scoring") and jd_text and resume_file:
    with tempfile.TemporaryDirectory() as tmpdir:
        # Save JD text
        jd_path = os.path.join(tmpdir, "jd.txt")
        with open(jd_path, "w", encoding="utf-8") as f:
            f.write(jd_text)

        # Save resume
        resume_path = os.path.join(tmpdir, resume_file.name)
        with open(resume_path, "wb") as f:
            f.write(resume_file.read())

        # Process single resume
        results = process_and_score_resumes(jd_path, tmpdir)

        if results.empty:
            st.warning("No valid resume processed or no match found with JD.")
        else:
            st.success("Scoring Complete!")
            st.dataframe(results, use_container_width=True)

            csv = results.to_csv(index=False).encode("utf-8")
            st.download_button("Download Results as CSV", csv, "resume_score.csv", "text/csv")

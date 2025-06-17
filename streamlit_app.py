
import os
import tempfile
import streamlit as st
import pandas as pd
from resume_scorer import process_and_score_resumes

st.set_page_config(page_title="AI Resume Scorer", layout="centered")

st.title("📄 AI Resume Scorer")
st.markdown("Upload a single resume and input a job description (JD) to score match.")

jd_text = st.text_area("Paste the Job Description here", height=200)
uploaded_resume = st.file_uploader("Upload a single resume PDF", type=["pdf"])

if st.button("Run Scoring"):
    if not jd_text or not uploaded_resume:
        st.error("Please provide both a resume and job description.")
    else:
        with tempfile.TemporaryDirectory() as tmpdir:
            jd_path = os.path.join(tmpdir, "jd.txt")
            with open(jd_path, "w") as f:
                f.write(jd_text)

            resume_path = os.path.join(tmpdir, uploaded_resume.name)
            with open(resume_path, "wb") as f:
                f.write(uploaded_resume.read())

            results_df = process_and_score_resumes(jd_path, [resume_path])

            st.success("Scoring Complete!")
            st.dataframe(results_df[['Filename', 'Score']])

            for _, row in results_df.iterrows():
                st.subheader(f"Feedback for {row['Filename']}")
                st.markdown(f"**Score:** {row['Score']}%")
                st.markdown(f"**Feedback:**\n\n{row['JD Criteria Feedback']}")

            st.download_button(
                "Download Results as CSV",
                data=results_df.to_csv(index=False),
                file_name="scoring_results.csv",
                mime="text/csv"
            )

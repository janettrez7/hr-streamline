import os
import re
import fitz  # PyMuPDF
import pandas as pd

def extract_text_from_pdf(file_path):
    """Extracts text from PDF using PyMuPDF."""
    text = ""
    try:
        with fitz.open(file_path) as doc:
            for page in doc:
                text += page.get_text()
    except Exception as e:
        print(f"Error extracting text from {file_path}: {e}")
    return text

def match_score(resume_text, jd_criteria):
    """Matches each JD criterion against the resume text."""
    resume_text = resume_text.lower()
    feedback = []
    matched_count = 0

    for item in jd_criteria:
        keyword = item.strip().lower()
        if re.search(rf"\\b{re.escape(keyword)}\\b", resume_text):
            feedback.append(f"✅ Matched: {item}")
            matched_count += 1
        else:
            feedback.append(f"❌ Missing: {item}")

    score_percent = (matched_count / len(jd_criteria)) * 100 if jd_criteria else 0
    return score_percent, "\n".join(feedback)

def process_and_score_resumes(jd_path, resume_paths):
    """Processes resumes and returns DataFrame with scores and feedback."""
    with open(jd_path, "r", encoding="utf-8") as f:
        jd_text = f.read()

    # Split JD text into criteria (by lines or commas)
    jd_criteria = [line.strip() for line in jd_text.replace(",", "\n").splitlines() if line.strip()]

    results = []

    for resume_file in resume_paths:
        resume_text = extract_text_from_pdf(resume_file)
        if not resume_text.strip():
            print(f"⚠️ No text extracted from {resume_file}")
            continue

        score, feedback = match_score(resume_text, jd_criteria)

        results.append({
            "Filename": os.path.basename(resume_file),
            "Score": round(score, 2),
            "JD Criteria Feedback": feedback
        })

    return pd.DataFrame(results)

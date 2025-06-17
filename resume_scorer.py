import os
import re
import fitz  # PyMuPDF
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

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

def generate_feedback_with_ai(jd_criteria, resume_text):
    """Generates AI-style feedback by comparing JD criteria to resume."""
    feedback = []
    matched_count = 0
    resume_text = resume_text.lower()

    for item in jd_criteria:
        keyword = item.strip().lower()
        if re.search(rf"\\b{re.escape(keyword)}\\b", resume_text):
            feedback.append(f"✅ The resume mentions '{item}', which is required.")
            matched_count += 1
        else:
            feedback.append(f"❌ The resume is missing the required keyword: '{item}'.")

    score_percent = (matched_count / len(jd_criteria)) * 100 if jd_criteria else 0
    return score_percent, "\n".join(feedback)

def process_and_score_resumes(jd_path, resume_paths):
    """Processes resumes and returns DataFrame with scores and AI-style feedback."""
    with open(jd_path, "r", encoding="utf-8") as f:
        jd_text = f.read()

    jd_criteria = [line.strip() for line in jd_text.replace(",", "\n").splitlines() if line.strip()]

    results = []

    for resume_file in resume_paths:
        resume_text = extract_text_from_pdf(resume_file)
        if not resume_text.strip():
            print(f"⚠️ No text extracted from {resume_file}")
            continue

        score, feedback = generate_feedback_with_ai(jd_criteria, resume_text)

        results.append({
            "Filename": os.path.basename(resume_file),
            "Score": round(score, 2),
            "JD Criteria Feedback": feedback
        })

    return pd.DataFrame(results)

import os
import re
import pandas as pd
import docx2txt
import fitz  # PyMuPDF

def extract_text_from_pdf(file_path):
    """Extracts text from a PDF file."""
    try:
        text = ""
        with fitz.open(file_path) as pdf:
            for page in pdf:
                text += page.get_text()
        return text
    except Exception as e:
        return ""

def extract_text_from_docx(file_path):
    """Extracts text from a DOCX file."""
    try:
        return docx2txt.process(file_path)
    except Exception as e:
        return ""

def extract_resume_text(file_path):
    """Determines file type and extracts text."""
    ext = os.path.splitext(file_path)[-1].lower()
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext == ".docx":
        return extract_text_from_docx(file_path)
    else:
        return ""

def match_score(resume_text, jd_criteria):
    """Scores the resume based on JD criteria and gives feedback."""
    matched = []
    feedback = []
    score = 0

    for criterion in jd_criteria:
        pattern = re.compile(r"\b" + re.escape(criterion.lower()) + r"\b")
        if pattern.search(resume_text.lower()):
            matched.append(criterion)
            feedback.append(f"✅ Matched: {criterion}")
            score += 1
        else:
            feedback.append(f"❌ Missing: {criterion}")

    score_percent = (score / len(jd_criteria)) * 100 if jd_criteria else 0
    return score_percent, "\n".join(feedback)

def process_and_score_resumes(jd_text, resumes_folder_or_file):
    """Processes all resumes in a folder or single file and returns scores."""
    jd_criteria = [line.strip() for line in jd_text.strip().split("\n") if line.strip()]
    scores = []

    # Handle single file case
    if os.path.isfile(resumes_folder_or_file):
        files = [resumes_folder_or_file]
    else:
        files = [
            os.path.join(resumes_folder_or_file, f)
            for f in os.listdir(resumes_folder_or_file)
            if f.lower().endswith((".pdf", ".docx"))
        ]

    for file in files:
        resume_text = extract_resume_text(file)

        if not resume_text.strip():
            continue  # Skip empty resumes

        score, feedback = match_score(resume_text, jd_criteria)
        scores.append({
            "Filename": os.path.basename(file),
            "Score": round(score, 2),
            "JD Criteria Feedback": feedback
        })

    return pd.DataFrame(scores).sort_values(by="Score", ascending=False)

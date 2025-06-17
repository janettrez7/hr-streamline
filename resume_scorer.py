
import os
import fitz  # PyMuPDF
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def extract_text_from_pdf(file_path):
    text = ""
    try:
        with fitz.open(file_path) as doc:
            for page in doc:
                text += page.get_text()
    except Exception as e:
        text += f"Error reading {file_path}: {e}"
    return text

def match_score(jd_text, resume_text):
    tfidf = TfidfVectorizer(stop_words='english')
    try:
        tfidf_matrix = tfidf.fit_transform([jd_text, resume_text])
        score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return round(score * 100, 2)
    except:
        return 0.0

def process_and_score_resumes(jd_path, resume_paths):
    with open(jd_path, 'r') as f:
        jd_text = f.read()

    scores = []
    for resume_file in resume_paths:
        resume_text = extract_text_from_pdf(resume_file)
        score = match_score(jd_text, resume_text)
        feedback = "✅ Good Match" if score > 60 else "⚠️ Needs Improvement" if score > 30 else "❌ Poor Match"
        scores.append({
            "Filename": os.path.basename(resume_file),
            "Score": score,
            "JD Criteria Feedback": feedback
        })

    return pd.DataFrame(scores).sort_values(by="Score", ascending=False)

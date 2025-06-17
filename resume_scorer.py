import os
import pdfplumber
import docx
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def extract_text(path):
    if path.endswith(".pdf"):
        with pdfplumber.open(path) as pdf:
            return "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())
    elif path.endswith(".docx"):
        doc = docx.Document(path)
        return "\n".join(p.text for p in doc.paragraphs)
    else:
        return ""

def process_and_score_resumes(jd_path, resumes_folder):
    jd_text = extract_text(jd_path)

    scores = []
    for file in os.listdir(resumes_folder):
        if not file.endswith((".pdf", ".docx")):
            continue
        resume_path = os.path.join(resumes_folder, file)
        resume_text = extract_text(resume_path)

        vectorizer = TfidfVectorizer(stop_words='english')
        vectors = vectorizer.fit_transform([jd_text, resume_text])
        score = cosine_similarity(vectors[0:1], vectors[1:2])[0][0] * 100

        scores.append({
            "Candidate": file,
            "Score (out of 100)": round(score, 2)
        })

    return pd.DataFrame(scores).sort_values(by="Score (out of 100)", ascending=False)

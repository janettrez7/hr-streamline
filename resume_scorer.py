import os
import pdfplumber
import docx
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def extract_text(path):
    try:
        if path.endswith(".pdf"):
            with pdfplumber.open(path) as pdf:
                text = "\n".join(
                    page.extract_text() or "" for page in pdf.pages
                )
                return text.strip()
        elif path.endswith(".docx"):
            doc = docx.Document(path)
            return "\n".join(p.text for p in doc.paragraphs if p.text).strip()
        elif path.endswith(".txt"):
            with open(path, 'r') as f:
                return f.read().strip()
    except Exception as e:
        print(f"Error reading {path}: {e}")
    return ""


def process_and_score_resumes(jd_path, resumes_folder):
    jd_text = extract_text(jd_path)
    if not jd_text:
        return pd.DataFrame([{"Candidate": "JD not readable", "Score (out of 100)": 0}])

    scores = []

    for file in os.listdir(resumes_folder):
        if not file.endswith((".pdf", ".docx")):
            continue

        resume_path = os.path.join(resumes_folder, file)
        resume_text = extract_text(resume_path)

        if not resume_text:
            print(f"Skipping {file}: no text found.")
            continue  # skip empty or unreadable resumes

        vectorizer = TfidfVectorizer(stop_words='english')
        vectors = vectorizer.fit_transform([jd_text, resume_text])
        score = cosine_similarity(vectors[0:1], vectors[1:2])[0][0] * 100

        scores.append({
            "Candidate": file,
            "Score (out of 100)": round(score, 2)
        })

    if not scores:
        return pd.DataFrame([{"Candidate": "No valid resumes found", "Score (out of 100)": 0}])

    return pd.DataFrame(scores).sort_values(by="Score (out of 100)", ascending=False)


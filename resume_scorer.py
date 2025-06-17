# resume_scorer.py
import os
import re
import pdfplumber
import docx
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def extract_text(path):
    try:
        if path.endswith(".pdf"):
            with pdfplumber.open(path) as pdf:
                text = "\n".join(page.extract_text() or "" for page in pdf.pages)
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


def extract_jd_criteria(jd_text):
    jd_text = jd_text.lower()

    skills = re.findall(r"(?:skills required|key skills|technical skills)[:\-\u2022]*\s*(.*)", jd_text)
    education = re.findall(r"(?:education|qualification)[:\-\u2022]*\s*(.*)", jd_text)
    experience = re.findall(r"(\d+)\+?\s*(?:years|yrs)\s*experience", jd_text)
    keywords = re.findall(r"(?:responsibilities|expectations)[:\-\u2022]*\s*(.*)", jd_text)

    return {
        "skills": re.split(r"[\,\n]", skills[0]) if skills else [],
        "education": education[0] if education else "",
        "experience": int(experience[0]) if experience else 0,
        "keywords": re.split(r"[\,\n]", keywords[0]) if keywords else []
    }


def evaluate_resume(jd, resume_text):
    text = resume_text.lower()
    report = {}

    # Skills Match
    matched_skills = [s for s in jd["skills"] if s.strip().lower() in text]
    report["Skills Match"] = {
        "matched": len(matched_skills) >= len(jd["skills"]) * 0.6 if jd["skills"] else True,
        "reason": f"Matched {len(matched_skills)} out of {len(jd['skills'])} skills"
    }

    # Experience Match
    exp_match = re.search(r"(\d+)\+?\s*(?:years|yrs)\s*experience", text)
    resume_exp = int(exp_match.group(1)) if exp_match else 0
    report["Experience Match"] = {
        "matched": resume_exp >= jd["experience"],
        "reason": f"Required {jd['experience']} yrs, found {resume_exp} yrs"
    }

    # Education Match
    report["Education Match"] = {
        "matched": jd["education"].lower() in text,
        "reason": f"{'Found' if jd['education'].lower() in text else 'Not found'} '{jd['education']}'"
    }

    # Keywords Match
    matched_keywords = [k for k in jd["keywords"] if k.strip().lower() in text]
    report["Keyword Match"] = {
        "matched": len(matched_keywords) >= len(jd["keywords"]) * 0.5 if jd["keywords"] else True,
        "reason": f"Matched {len(matched_keywords)} out of {len(jd['keywords'])} keywords"
    }

    # Score
    weights = {
        "Skills Match": 0.4,
        "Experience Match": 0.3,
        "Education Match": 0.2,
        "Keyword Match": 0.1
    }
    score = sum(weights[k] * 100 for k, v in report.items() if v["matched"])

    return score, report


def process_and_score_resumes(jd_path, resumes_folder):
    jd_text = extract_text(jd_path)
    jd_criteria = extract_jd_criteria(jd_text)

    scores = []

    for file in os.listdir(resumes_folder):
        if not file.endswith((".pdf", ".docx")):
            continue

        resume_path = os.path.join(resumes_folder, file)
        resume_text = extract_text(resume_path)
        if not resume_text:
            print(f"Skipping {file}: no text found.")
            continue

        score, report = evaluate_resume(jd_criteria, resume_text)

        scores.append({
            "Candidate": file,
            "Score": round(score, 2),
            "Skills Match": "✅" if report["Skills Match"]["matched"] else "❌",
            "Skills Reason": report["Skills Match"]["reason"],
            "Experience Match": "✅" if report["Experience Match"]["matched"] else "❌",
            "Experience Reason": report["Experience Match"]["reason"],
            "Education Match": "✅" if report["Education Match"]["matched"] else "❌",
            "Education Reason": report["Education Match"]["reason"],
            "Keyword Match": "✅" if report["Keyword Match"]["matched"] else "❌",
            "Keyword Reason": report["Keyword Match"]["reason"]
        })

    return pd.DataFrame(scores).sort_values(by="Score", ascending=False)

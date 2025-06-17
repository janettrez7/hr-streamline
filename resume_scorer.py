import os
import docx
import pytesseract
import pdfplumber
import pandas as pd
from pdf2image import convert_from_path
from PIL import Image

def extract_text(path):
    try:
        if path.lower().endswith(".pdf"):
            with pdfplumber.open(path) as pdf:
                text = "\n".join((page.extract_text() or "") for page in pdf.pages).strip()
            if not text:
                print("🔁 Falling back to OCR for", path)
                images = convert_from_path(path)
                text = "\n".join(pytesseract.image_to_string(img) for img in images)
            return text
        if path.lower().endswith(".docx"):
            doc = docx.Document(path)
            return "\n".join(p.text for p in doc.paragraphs if p.text).strip()
        if path.lower().endswith(".txt"):
            return open(path, 'r', encoding='utf-8', errors='ignore').read().strip()
    except Exception as e:
        print(f"⚠️ Error reading {path}: {e}")
    return ""

def parse_jd_text(jd_text):
    lines = jd_text.lower().splitlines()
    keywords = [line.strip() for line in lines if line.strip()]
    return keywords

def score_resume(resume_text, jd_keywords):
    resume_text = resume_text.lower()
    score = 0
    criteria_details = []
    for keyword in jd_keywords:
        if keyword in resume_text:
            score += 1
            criteria_details.append((keyword, "✅ Matched"))
        else:
            criteria_details.append((keyword, "❌ Not Found"))
    return score, criteria_details

def process_and_score_resumes(jd_path, resume_dir):
    jd_text = extract_text(jd_path)
    jd_keywords = parse_jd_text(jd_text)
    
    scores = []

    for fname in os.listdir(resume_dir):
        path = os.path.join(resume_dir, fname)
        if not os.path.isfile(path):
            continue
        resume_text = extract_text(path)
        if not resume_text:
            print(f"🚫 No text found in {fname}")
            continue
        score, details = score_resume(resume_text, jd_keywords)
        percent_score = round((score / len(jd_keywords)) * 100, 2) if jd_keywords else 0
        feedback = "\n".join([f"{k}: {v}" for k, v in details])
        scores.append({
            "Resume": fname,
            "Score": percent_score,
            "JD Criteria Feedback": feedback
        })

    return pd.DataFrame(scores).sort_values(by="Score", ascending=False)

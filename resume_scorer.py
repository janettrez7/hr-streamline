# import os
# import docx
# import pytesseract
# import pdfplumber
# import pandas as pd
# from pdf2image import convert_from_path
# from PIL import Image

# def extract_text(path):
#     try:
#         if path.lower().endswith(".pdf"):
#             with pdfplumber.open(path) as pdf:
#                 text = "\n".join((page.extract_text() or "") for page in pdf.pages).strip()
#             if not text:
#                 images = convert_from_path(path)
#                 text = "\n".join(pytesseract.image_to_string(img) for img in images)
#             return text
#         elif path.lower().endswith(".docx"):
#             doc = docx.Document(path)
#             return "\n".join(p.text for p in doc.paragraphs if p.text).strip()
#         elif path.lower().endswith(".txt"):
#             return open(path, 'r', encoding='utf-8', errors='ignore').read().strip()
#     except Exception as e:
#         print(f"⚠️ Error reading {path}: {e}")
#     return ""

# def parse_jd_text(jd_text):
#     lines = jd_text.lower().splitlines()
#     return [line.strip() for line in lines if line.strip()]

# def score_resume(resume_text, jd_keywords):
#     resume_text = resume_text.lower()
#     score = 0
#     details = []
#     for keyword in jd_keywords:
#         if keyword in resume_text:
#             score += 1
#             details.append((keyword, "✅ Matched"))
#         else:
#             details.append((keyword, "❌ Not Found"))
#     return score, details

# def process_and_score_resumes(jd_path, resume_dir):
#     jd_text = extract_text(jd_path)
#     jd_keywords = parse_jd_text(jd_text)

#     scores = []

#     for fname in os.listdir(resume_dir):
#         path = os.path.join(resume_dir, fname)

#         # Skip non-text-resume files
#         if not any(fname.lower().endswith(ext) for ext in [".pdf", ".docx", ".txt"]):
#             print(f"🚫 Skipping non-resume file: {fname}")
#             continue

#         resume_text = extract_text(path)
#         if not resume_text:
#             print(f"🚫 No text found in {fname}")
#             continue

#         score, details = score_resume(resume_text, jd_keywords)
#         percent_score = round((score / len(jd_keywords)) * 100, 2) if jd_keywords else 0
#         feedback = "\n".join([f"{k}: {v}" for k, v in details])

#         scores.append({
#             "Resume": fname,
#             "Score": percent_score,
#             "JD Criteria Feedback": feedback
#         })

#     df = pd.DataFrame(scores)
#     return df.sort_values(by="Score", ascending=False) if not df.empty else df

# def process_and_score_resumes_from_text(jd_text, resume_folder):
#     jd_keywords = parse_jd_text(jd_text)
#     return process_and_score_resumes(jd_keywords, resume_folder)

import os
import pandas as pd
from utils import extract_text_from_file, match_score

def process_and_score_resumes(jd_path, resume_dir):
    with open(jd_path, "r", encoding="utf-8") as f:
        jd_criteria = [c.strip().lower() for line in f for c in line.split(",") if c.strip()]

    scores = []
    for fname in os.listdir(resume_dir):
        if not fname.lower().endswith((".pdf", ".docx", ".txt")):
            continue

        fpath = os.path.join(resume_dir, fname)
        resume_text = extract_text_from_file(fpath).lower()

        if not resume_text.strip():
            continue

        matched = [skill for skill in jd_criteria if skill in resume_text]
        score = (len(matched) / len(jd_criteria)) * 100 if jd_criteria else 0

        feedback = []
        for skill in jd_criteria:
            if skill in resume_text:
                feedback.append(f"✅ {skill}")
            else:
                feedback.append(f"❌ {skill}")

        scores.append({
            "Resume": fname,
            "Score": round(score, 2),
            "JD Criteria Feedback": "\n".join(feedback)
        })

    return pd.DataFrame(scores).sort_values(by="Score", ascending=False)


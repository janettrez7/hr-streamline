# resume_scorer.py
import os, re
import pdfplumber, docx
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def extract_text(path):
    try:
        if path.lower().endswith(".pdf"):
            with pdfplumber.open(path) as pdf:
                return "\n".join(page.extract_text() or "" for page in pdf.pages).strip()
        if path.lower().endswith(".docx"):
            doc = docx.Document(path)
            return "\n".join(p.text for p in doc.paragraphs if p.text).strip()
        if path.lower().endswith(".txt"):
            return open(path, 'r', encoding='utf-8', errors='ignore').read().strip()
    except Exception as e:
        print(f"⚠️ Error reading {path}: {e}")
    return ""

def extract_jd_criteria(jd_text):
    jd = jd_text.lower()
    skills = re.findall(r"(?:skills required|technical skills)[:\-•]*\s*(.*)", jd)
    edu = re.findall(r"(?:education|qualification)[:\-•]*\s*(.*)", jd)
    exp = re.findall(r"(\d+)\+?\s*(?:years|yrs)\s*experience", jd)
    keywords = re.findall(r"(?:responsibilities|expectations)[:\-•]*\s*(.*)", jd)
    return {
        "skills": [s.strip() for s in re.split(r"[,\n]", skills[0])] if skills else [],
        "education": edu[0].strip() if edu else "",
        "experience": int(exp[0]) if exp else 0,
        "keywords": [k.strip() for k in re.split(r"[,\n]", keywords[0])] if keywords else []
    }

def evaluate_resume(jd, text):
    rpt = {}
    t = text.lower()
    matched_skills = [s for s in jd["skills"] if s.lower() in t]
    rpt["Skills Match"] = {"matched": len(matched_skills)>= max(1, len(jd["skills"])*0.6), "reason": f"{len(matched_skills)}/{len(jd['skills'])}"}
    
    exp_m = re.search(r"(\d+)\+?\s*(?:years|yrs)\s*experience", t)
    res_exp = int(exp_m.group(1)) if exp_m else 0
    rpt["Experience Match"] = {"matched": res_exp >= jd["experience"], "reason": f"required {jd['experience']}, found {res_exp}"}
    
    edu_ok = jd["education"] and jd["education"].lower() in t
    rpt["Education Match"] = {"matched": edu_ok, "reason": "found" if edu_ok else "not found"}
    
    matches_k = [k for k in jd["keywords"] if k.lower() in t]
    rpt["Keyword Match"] = {"matched": len(matches_k)>= max(1, len(jd["keywords"])*0.5), "reason": f"{len(matches_k)}/{len(jd['keywords'])}"}
    
    weights = {"Skills Match":0.4,"Experience Match":0.3,"Education Match":0.2,"Keyword Match":0.1}
    score = sum(weights[k]*100 for k,v in rpt.items() if v["matched"])
    return score, rpt

def process_and_score_resumes(jd_path, resumes_folder):
    jd_text = extract_text(jd_path)
    print("🔍 Extracted JD (first 500 chars):\n", jd_text[:500])
    if not jd_text:
        print("❌ JD extraction failed.")
        return pd.DataFrame()
    
    jd_crit = extract_jd_criteria(jd_text)
    print("🏷️ JD criteria extracted:\n", jd_crit)
    
    files = [f for f in os.listdir(resumes_folder) if f.lower().endswith((".pdf",".docx",".txt"))]
    print("📄 Found resumes:", files)
    if not files:
        print("❌ No resumes to process.")
        return pd.DataFrame()
    
    rows = []
    for fname in files:
        path = os.path.join(resumes_folder, fname)
        txt = extract_text(path)
        print(f"-- Processing {fname}, length:", len(txt))
        if not txt:
            print("   ⚠️ Skipping, no text.")
            continue
        
        score, rep = evaluate_resume(jd_crit, txt)
        print(f"   ✅ Score: {score}, report: {rep}")
        rows.append({
            "Candidate": fname, "Score": round(score,2),
            "Skills Match": "✅" if rep["Skills Match"]["matched"] else "❌", "Skills Reason": rep["Skills Match"]["reason"],
            "Experience Match": "✅" if rep["Experience Match"]["matched"] else "❌", "Experience Reason": rep["Experience Match"]["reason"],
            "Education Match": "✅" if rep["Education Match"]["matched"] else "❌", "Education Reason": rep["Education Match"]["reason"],
            "Keyword Match": "✅" if rep["Keyword Match"]["matched"] else "❌", "Keyword Reason": rep["Keyword Match"]["reason"],
        })
    
    df = pd.DataFrame(rows)
    return df.sort_values("Score", ascending=False) if not df.empty else df

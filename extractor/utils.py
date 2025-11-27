import os
import re
import json
import spacy
import docx
import logging
from pathlib import Path
from docx import Document
from pypdf import PdfReader
from datetime import datetime
from django.conf import settings

# Load SpaCy model
nlp = spacy.load("en_core_web_sm")


# ------------------- Extract Text -------------------
def extract_text_from_docx(file):
    try:
        doc = Document(file)
        return "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
    except Exception as e:
        logging.error("Error extracting text from DOCX: %s", e)
        return ""


def extract_text_from_pdf(file):
    text = ""
    try:
        pdf = PdfReader(file)
        for page in pdf.pages:
            content = page.extract_text()
            if content:
                text += content + "\n"
    except Exception as e:
        logging.error("Error extracting text from PDF: %s", e)
        return ""
    return text


# ------------------- Date Parsing Helper -------------------
def parse_date(date_str):
    """Convert resume date string to datetime object"""
    date_str = date_str.strip().lower().replace("present", datetime.now().strftime("%b %Y"))

    # Common formats: Jan 2020, March 2019, 2021
    formats = ["%b %Y", "%B %Y", "%Y"]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None


def calculate_experience(text):
    """
    Find date ranges in resume and calculate total years of experience.
    Example: Jan 2020 - Mar 2022
    """
    date_pattern = r"([A-Za-z]{3,9}\s\d{4}|\d{4})\s*[-–]\s*(Present|[A-Za-z]{3,9}\s\d{4}|\d{4})"
    matches = re.findall(date_pattern, text, flags=re.IGNORECASE)

    total_months = 0
    for start, end in matches:
        start_date = parse_date(start)
        end_date = parse_date(end)
        if start_date and end_date:
            months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
            if months > 0:
                total_months += months

    if total_months == 0:
        return "Fresher (No prior work experience found)"

    years, months = divmod(total_months, 12)
    return f"{years} years {months} months" if years else f"{months} months"


# ------------------- Summary Extraction -------------------
def extract_summary(text):
    summary_keywords = ["summary", "objective", "profile"]
    for keyword in summary_keywords:
        pattern = re.compile(
            rf"{keyword}[:\-]?\s*(.+?)(?=\n[A-Z])",
            re.IGNORECASE | re.DOTALL,
        )
        match = pattern.search(text)
        if match:
            return match.group(1).strip()

    doc = nlp(text)
    sentences = list(doc.sents)
    return " ".join([sent.text for sent in sentences[:3]]) if sentences else "No summary found"


# ------------------- Experience Extraction -------------------
def extract_experience(text):
    exp_keywords = ["experience", "work experience", "employment history", "professional experience"]

    for keyword in exp_keywords:
        pattern = re.compile(
            rf"{keyword}[:\-]?\s*(.+?)(?=\n[A-Z])",
            re.IGNORECASE | re.DOTALL,
        )
        match = pattern.search(text)
        if match:
            return match.group(1).strip()

    doc = nlp(text)
    companies = [ent.text for ent in doc.ents if ent.label_ == "ORG"]
    if companies:
        return f"Companies: {', '.join(companies[:3])}"

    return "Fresher"

#<------------------Education information------------------>
def extract_education(text):
    education_keywords = ["education", "academic background", "qualifications", "educational qualifications"]
    for keyword in education_keywords:
        pattern = re.compile(
            rf"{keyword}[:\-]?\s*(.+?)(?=\n[A-Z])",
            re.IGNORECASE | re.DOTALL,
        )
        match = pattern.search(text)
        if match:
            return match.group(1).strip()
    return None

#<-------------------Projects------------------->
def extract_projects(text):
    project_keywords = ["projects", "project experience", "notable projects"]
    for keyword in project_keywords:
        pattern = re.compile(
            rf"{keyword}[:\-]?\s*(.+?)(?=\n[A-Z])",
            re.IGNORECASE | re.DOTALL,
        )
        match = pattern.search(text)
        if match:
            return match.group(1).strip()
    return None

    


# ------------------- Skills Extraction -------------------
def extract_skills(text):
    if not text.strip():
        return []

    skills_file = Path(settings.BASE_DIR) / "skills" / "skills.json"
    try:
        with open(skills_file, "r") as f:
            skills = json.load(f).get("skills", [])
    except FileNotFoundError:
        logging.error("Skills file not found: %s", skills_file)
        return []

    # Use SpaCy for NLP-based extraction
    doc = nlp(text.lower())
    text_lemmas = {token.lemma_ for token in doc if token.is_alpha}

    extracted = []
    for skill in skills:
        skill_doc = nlp(skill.lower())
        skill_lemmas = {token.lemma_ for token in skill_doc if token.is_alpha}
        if skill_lemmas.issubset(text_lemmas):
            extracted.append(skill)

    return list(set(extracted))


# ------------------- Skills Extraction from Job Description -------------------
def extract_skills_from_jd(text):
    if not text.strip():
        return []

    skills_file = Path(settings.BASE_DIR) / "skills" / "skills.json"
    try:
        with open(skills_file, "r") as f:
            skills = json.load(f).get("skills", [])
    except FileNotFoundError:
        logging.error("Skills file not found: %s", skills_file)
        return []

    # Use SpaCy for NLP-based extraction
    doc = nlp(text.lower())
    text_lemmas = {token.lemma_ for token in doc if token.is_alpha}

    extracted = []
    for skill in skills:
        skill_doc = nlp(skill.lower())
        skill_lemmas = {token.lemma_ for token in skill_doc if token.is_alpha}
        if skill_lemmas.issubset(text_lemmas):
            extracted.append(skill)

    return list(set(extracted))

#<----------achivement---------->

def extract_achievements(text):
    achievement_keywords = ["achievements", "certifications", "awards", "recognitions", "honors"]
    results = []

    for keyword in achievement_keywords:
        # Match the section until the next heading (newline + capitalized word) or end of text
        pattern = re.compile(
            rf"{keyword}[:\-]?\s*(.+?)(?=\n[A-Z]|\Z)",
            re.IGNORECASE | re.DOTALL
        )
        match = pattern.search(text)
        if match:
            results.append(match.group(1).strip())

    return results if results else None

#<----------github links---------->

def extract_github_links(text):
    # Find all GitHub links in the text
    github_pattern = r"https?://github\.com/[^\s]+"
    links = re.findall(github_pattern, text)
    return ", ".join(links) if links else ""
        

# ---------- Short Summary Generator ----------
def generate_short_summary(data):
    summary = data.get("summary", "")
    experience = data.get("experience", "")
    skills = data.get("skills", [])

    if summary and summary != "No summary found":
        # Truncate long summary to 150 characters
        short = summary[:150] + "..." if len(summary) > 150 else summary
    else:
        # Generate short summary from experience and skills
        exp_part = f" with experience in {experience}" if experience and experience != "Fresher" else ""
        skills_part = f". Key skills: {', '.join(skills[:5])}" if skills else ""
        short = f"Professional{exp_part}{skills_part}."

    return short

# ---------- Main Extractor ----------
def extract_resume_data(file, file_type="pdf"):
    # 1. Extract text
    if file_type == "docx":
        text = extract_text_from_docx(file)
    elif file_type == "pdf":
        text = extract_text_from_pdf(file)
    else:
        return {"error": "Unsupported file format"}

    if not text:
        return {"error": "Failed to extract text from the file"}

    # 2. Extract fields
    data = {
        "summary": extract_summary(text),
        "experience": extract_experience(text),
        "skills": extract_skills(text),
        "total_experience": calculate_experience(text),
        "achievements": extract_achievements(text),
        "education": extract_education(text),
        "projects": extract_projects(text),
        "github_links": extract_github_links(text),

    }

    # 3. Generate short summary
    data["short_summary"] = generate_short_summary(data)

    return data
#<-------------------ats checker------------------->

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def get_embedding(text, model=nlp):
    """
    Get the average vector embedding for the given text using spaCy model.
    """
    doc = model(text.lower())
    if len(doc) == 0:
        return np.zeros((model.vocab.vectors_length,))
    return doc.vector

def semantic_similarity_missing_skills(resume_text, jd_skills, threshold=0.75):
    """
    Find missing skills based on semantic similarity between resume text and job description skills.
    Uses cosine similarity on vector embeddings for better accuracy.
    Returns a list of missing skills that are semantically close but not explicitly mentioned.
    """
    resume_vec = get_embedding(resume_text)
    missing_skills = []

    for skill in jd_skills:
        skill_vec = get_embedding(skill)
        if np.linalg.norm(resume_vec) == 0 or np.linalg.norm(skill_vec) == 0:
            similarity = 0
        else:
            similarity = cosine_similarity([resume_vec], [skill_vec])[0][0]
        if similarity < threshold:
            missing_skills.append(skill)

    return missing_skills


def ats_checker(resume_text, job_description):
    # Extract skills using NLP
    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills_from_jd(job_description)

    if not jd_skills:
        return {"error": "No skills found in job description."}

    # Matched and missing skills based on exact match
    matched_skills = set(resume_skills).intersection(set(jd_skills))
    missing_skills_exact = set(jd_skills) - set(resume_skills)

    # Enhanced missing skills based on semantic similarity
    missing_skills_semantic = semantic_similarity_missing_skills(resume_text, list(missing_skills_exact))

    # Combine missing skills (exact + semantic)
    missing_skills_combined = list(missing_skills_exact.union(set(missing_skills_semantic)))

    # Match count and percentage based on combined missing skills
    match_count = len(jd_skills) - len(missing_skills_combined)
    total_jd_skills = len(jd_skills)
    match_percentage = (match_count / total_jd_skills) * 100 if total_jd_skills > 0 else 0

    return {
        "total_jd_skills": total_jd_skills,
        "matched_skills": list(matched_skills),
        "missing_skills": missing_skills_combined,
        "missing_skills_semantic": missing_skills_semantic,
        "match_count": match_count,
        "match_percentage": round(match_percentage, 2),
    }
# <------------------- End of File ------------------->
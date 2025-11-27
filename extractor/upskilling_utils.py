"""
Upskilling Utilities - Free AI-Based Skill Gap Analysis & Course Recommendations
Uses sentence-transformers (free embeddings) and scikit-learn for semantic matching
No paid APIs (OpenAI, Gemini, etc.)
"""

import json
import os
import logging
from pathlib import Path
from typing import List, Dict, Any

# Initialize logger first
logger = logging.getLogger(__name__)

# Try importing ML libraries with error handling
try:
    import numpy as np
    from sklearn.metrics.pairwise import cosine_similarity
    from sentence_transformers import SentenceTransformer
    ML_AVAILABLE = True
except ImportError as e:
    logger.error(f"ML libraries not available: {e}")
    ML_AVAILABLE = False
    np = None
    cosine_similarity = None
    SentenceTransformer = None

from django.conf import settings

# Import existing utilities
from .utils import (
    extract_text_from_pdf, 
    extract_text_from_docx,
    extract_skills
)

# Global variable to cache the embedding model (load once, use many times)
_embedding_model = None


def get_embedding_model():
    """
    Load and cache the sentence-transformer model (free, local, no API needed)
    Using 'all-MiniLM-L6-v2' - lightweight and fast
    """
    if not ML_AVAILABLE:
        raise ImportError("ML libraries (sentence-transformers, sklearn) are not installed")
    
    global _embedding_model
    if _embedding_model is None:
        logger.info("Loading sentence-transformer model (first time only)...")
        try:
            # Use a lightweight, free, open-source model
            _embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Model loaded successfully!")
        except Exception as e:
            logger.error(f"Error loading embedding model: {e}")
            raise
    return _embedding_model


def parse_resume_for_upskilling(resume_file) -> Dict[str, Any]:
    """
    Parse resume and extract text and skills
    Supports PDF and DOCX formats
    """
    try:
        file_name = resume_file.name.lower()
        
        # Extract text based on file type
        if file_name.endswith('.pdf'):
            text = extract_text_from_pdf(resume_file)
        elif file_name.endswith('.docx'):
            text = extract_text_from_docx(resume_file)
        else:
            return {"error": "Unsupported file format. Please upload PDF or DOCX."}
        
        if not text:
            return {"error": "Failed to extract text from resume."}
        
        # Extract skills using existing utility
        skills = extract_skills(text)
        
        return {
            "text": text,
            "skills": skills,
            "skill_count": len(skills)
        }
    
    except Exception as e:
        logger.error(f"Error parsing resume: {e}")
        return {"error": str(e)}


def load_courses_database() -> Dict[str, Any]:
    """
    Load the courses database from JSON file
    """
    try:
        courses_file = Path(settings.BASE_DIR) / "courses_database.json"
        with open(courses_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error("Courses database not found")
        return {"courses": [], "job_role_skills": {}}
    except Exception as e:
        logger.error(f"Error loading courses database: {e}")
        return {"courses": [], "job_role_skills": {}}


def get_required_skills_for_role(job_role: str) -> List[str]:
    """
    Get required skills for a specific job role from database
    Uses semantic matching to find closest job role if exact match not found
    """
    db = load_courses_database()
    job_role_skills = db.get("job_role_skills", {})
    
    # Exact match
    if job_role in job_role_skills:
        return job_role_skills[job_role]
    
    # Case-insensitive match
    for role, skills in job_role_skills.items():
        if role.lower() == job_role.lower():
            return skills
    
    # Semantic matching using embeddings
    try:
        model = get_embedding_model()
        job_role_embedding = model.encode([job_role.lower()])
        
        best_match = None
        best_similarity = 0.0
        
        for role in job_role_skills.keys():
            role_embedding = model.encode([role.lower()])
            similarity = cosine_similarity(job_role_embedding, role_embedding)[0][0]
            
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = role
        
        # If similarity is above threshold (0.6), use the matched role
        if best_match and best_similarity > 0.6:
            logger.info(f"Matched '{job_role}' to '{best_match}' with similarity {best_similarity:.2f}")
            return job_role_skills[best_match]
    
    except Exception as e:
        logger.error(f"Error in semantic matching: {e}")
    
    # Default: return general software engineering skills
    return [
        "Programming", "Data Structures", "Algorithms", "Problem Solving",
        "Git", "Communication", "Teamwork"
    ]


def analyze_skill_gaps(resume_skills: List[str], required_skills: List[str]) -> Dict[str, Any]:
    """
    Analyze skill gaps between resume and job requirements
    Uses free embeddings for semantic similarity
    """
    try:
        model = get_embedding_model()
        
        # Convert to lowercase for comparison
        resume_skills_lower = [s.lower() for s in resume_skills]
        required_skills_lower = [s.lower() for s in required_skills]
        
        # Exact matches
        matched_skills = []
        for skill in required_skills:
            if skill.lower() in resume_skills_lower:
                matched_skills.append(skill)
        
        # Semantic matching for remaining skills
        missing_skills = []
        semantically_matched = []
        
        for req_skill in required_skills:
            if req_skill in matched_skills:
                continue
            
            # Encode required skill
            req_embedding = model.encode([req_skill.lower()])
            
            # Check semantic similarity with all resume skills
            max_similarity = 0.0
            best_match = None
            
            for res_skill in resume_skills:
                res_embedding = model.encode([res_skill.lower()])
                similarity = cosine_similarity(req_embedding, res_embedding)[0][0]
                
                if similarity > max_similarity:
                    max_similarity = similarity
                    best_match = res_skill
            
            # If similarity > 0.75, consider it semantically matched
            if max_similarity > 0.75:
                semantically_matched.append({
                    "required": req_skill,
                    "matched_with": best_match,
                    "similarity": round(float(max_similarity), 2)
                })
                matched_skills.append(req_skill)
            else:
                missing_skills.append(req_skill)
        
        # Calculate match percentage
        match_percentage = (len(matched_skills) / len(required_skills) * 100) if required_skills else 0
        
        return {
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "semantically_matched": semantically_matched,
            "total_required": len(required_skills),
            "total_matched": len(matched_skills),
            "match_percentage": round(match_percentage, 2)
        }
    
    except Exception as e:
        logger.error(f"Error analyzing skill gaps: {e}")
        return {
            "matched_skills": [],
            "missing_skills": required_skills,
            "semantically_matched": [],
            "total_required": len(required_skills),
            "total_matched": 0,
            "match_percentage": 0,
            "error": str(e)
        }


def recommend_courses_for_skills(missing_skills: List[str], limit: int = 10) -> List[Dict[str, Any]]:
    """
    Recommend courses based on missing skills using semantic matching
    Uses free embeddings to match skills with course content
    """
    try:
        if not missing_skills:
            return []
        
        model = get_embedding_model()
        db = load_courses_database()
        courses = db.get("courses", [])
        
        if not courses:
            return []
        
        # Encode missing skills
        missing_skills_text = " ".join(missing_skills).lower()
        missing_embedding = model.encode([missing_skills_text])
        
        # Calculate relevance scores for each course
        course_scores = []
        
        for course in courses:
            # Create course text from title and skills
            course_skills = course.get("skills", [])
            course_text = f"{course.get('title', '')} {' '.join(course_skills)}".lower()
            course_embedding = model.encode([course_text])
            
            # Calculate similarity
            similarity = cosine_similarity(missing_embedding, course_embedding)[0][0]
            
            # Check if any missing skill is directly in course skills
            direct_match_count = sum(1 for skill in missing_skills if any(
                skill.lower() in cs.lower() for cs in course_skills
            ))
            
            # Boost score for direct matches
            final_score = similarity + (direct_match_count * 0.2)
            
            course_scores.append({
                "course": course,
                "score": float(final_score),
                "similarity": round(float(similarity), 2),
                "direct_matches": direct_match_count
            })
        
        # Sort by score (descending)
        course_scores.sort(key=lambda x: x["score"], reverse=True)
        
        # Return top N courses
        recommended = []
        for item in course_scores[:limit]:
            course = item["course"]
            recommended.append({
                "id": course.get("id"),
                "title": course.get("title"),
                "platform": course.get("platform"),
                "url": course.get("url"),
                "skills": course.get("skills", []),
                "level": course.get("level"),
                "duration": course.get("duration"),
                "relevance_score": round(item["score"], 2),
                "matching_skills": [skill for skill in missing_skills if any(
                    skill.lower() in cs.lower() for cs in course.get("skills", [])
                )]
            })
        
        return recommended
    
    except Exception as e:
        logger.error(f"Error recommending courses: {e}")
        return []


def generate_upskilling_report(
    resume_file, 
    target_job_role: str
) -> Dict[str, Any]:
    """
    Main function to generate complete upskilling report
    1. Parse resume
    2. Get required skills for job role
    3. Analyze skill gaps
    4. Recommend courses
    All using FREE, local AI methods
    """
    try:
        # Step 1: Parse resume
        logger.info("Parsing resume...")
        resume_data = parse_resume_for_upskilling(resume_file)
        
        if "error" in resume_data:
            return {"error": resume_data["error"]}
        
        resume_skills = resume_data["skills"]
        
        # Step 2: Get required skills for job role
        logger.info(f"Getting required skills for role: {target_job_role}")
        required_skills = get_required_skills_for_role(target_job_role)
        
        # Step 3: Analyze skill gaps
        logger.info("Analyzing skill gaps...")
        gap_analysis = analyze_skill_gaps(resume_skills, required_skills)
        
        # Step 4: Recommend courses
        logger.info("Recommending courses...")
        recommended_courses = recommend_courses_for_skills(
            gap_analysis["missing_skills"], 
            limit=10
        )
        
        # Generate summary
        summary = generate_summary(
            resume_skills, 
            required_skills, 
            gap_analysis, 
            recommended_courses
        )
        
        return {
            "success": True,
            "target_job_role": target_job_role,
            "skills_detected": resume_skills,
            "skills_required": required_skills,
            "gap_analysis": gap_analysis,
            "recommended_courses": recommended_courses,
            "summary": summary
        }
    
    except Exception as e:
        logger.error(f"Error generating upskilling report: {e}")
        return {"error": f"Failed to generate report: {str(e)}"}


def generate_summary(
    resume_skills: List[str],
    required_skills: List[str],
    gap_analysis: Dict[str, Any],
    recommended_courses: List[Dict[str, Any]]
) -> str:
    """
    Generate a human-readable summary of the upskilling analysis
    """
    match_percentage = gap_analysis.get("match_percentage", 0)
    matched_count = gap_analysis.get("total_matched", 0)
    missing_count = len(gap_analysis.get("missing_skills", []))
    
    summary = f"Your resume matches {match_percentage}% of the required skills for this role. "
    summary += f"You have {matched_count} out of {len(required_skills)} required skills. "
    
    if missing_count > 0:
        summary += f"You need to develop {missing_count} additional skill(s). "
        summary += f"We've recommended {len(recommended_courses)} courses to help you bridge these gaps."
    else:
        summary += "Congratulations! You have all the required skills for this role."
    
    return summary


def get_job_roles_list() -> List[str]:
    """
    Get list of all available job roles from database
    """
    db = load_courses_database()
    return list(db.get("job_role_skills", {}).keys())


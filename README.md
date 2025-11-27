# AI Career Development Platform

Smart resume analyzer + job recommender + upskilling guide.

## Features
- Hybrid ATS compatibility checker (keyword + semantic matching)  
- AI-powered job role prediction using Random Forest  
- Skill gap analysis with free course recommendations  

## Quick Start

**Docker:**
```bash
docker-compose build
docker-compose up
# Open http://localhost:8000
```

**Manual:**
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_lg
python manage.py migrate
python manage.py runserver
```

## Tech Stack
Django | spaCy | Random Forest | sentence-transformers | Bootstrap

## Usage
1. Upload resume (PDF/DOCX)
2. Check ATS compatibility OR Get job predictions OR Analyze skill gaps
3. Get personalized recommendations


## Future Work
Multi-language support | Real-time job APIs | Interview prep | Mobile app

# Job Recommendation Integration Guide

## Overview
The Job Recommendation module has been successfully integrated into the AI Resume Detection project. This module uses Machine Learning (TF-IDF + Random Forest) to predict job roles based on user skills/resume text and provides LinkedIn job search links.

## What Was Done

### A. New Django App Created
- **App Name**: `job_recommendation`
- **Location**: `Ai_Resume_detection/job_recommendation/`

### B. Files Created/Modified

#### New Files:
1. **job_recommendation/__init__.py** - App initialization
2. **job_recommendation/apps.py** - App configuration
3. **job_recommendation/models.py** - Database model for recommendation history
4. **job_recommendation/admin.py** - Django admin configuration
5. **job_recommendation/views.py** - View functions and API endpoints
6. **job_recommendation/urls.py** - URL routing
7. **job_recommendation/job_utils.py** - Core ML logic (model loading, prediction)
8. **job_recommendation/templates/job_recommendation/job_recommendation.html** - Main UI page
9. **job_recommendation/templates/job_recommendation/history.html** - History page
10. **job_recommendation/models/** - Directory containing ML model files (.pkl)
11. **job_recommendation/migrations/__init__.py** - Migrations directory

#### Modified Files:
1. **backend/settings.py** - Added 'job_recommendation' to INSTALLED_APPS
2. **backend/urls.py** - Added job-recommendation/ URL pattern
3. **extractor/templates/extractor/index.html** - Added Job Recommendation card, navigation link, and hero button

### C. Features Implemented

#### 1. **ML-Based Job Prediction**
- Uses TF-IDF vectorizer and Random Forest classifier
- Predicts job roles from resume text/skills
- Returns confidence scores

#### 2. **User Interface**
- Beautiful, responsive UI matching the existing design
- Text area for skills/resume input
- Real-time prediction results
- LinkedIn job search integration

#### 3. **LinkedIn Integration**
- Automatically generates LinkedIn job search URLs
- Opens job listings in a new tab

#### 4. **History Tracking**
- Saves recommendation history for logged-in users
- Viewable at `/job-recommendation/history/`

#### 5. **API Endpoint**
- RESTful API at `/job-recommendation/api/recommend/`
- Accepts POST requests with resume text
- Returns JSON with predicted role and LinkedIn URL

## How to Use

### For Users:

1. **From Homepage**: Click the "AI Job Recommendation" card in the Features section
2. **From Navigation**: Click "Jobs" in the top navigation menu
3. **From Hero Section**: Click the "Job Recommendation" button

4. **On Job Recommendation Page**:
   - Enter your skills or paste your resume text
   - Click "Get Job Recommendations"
   - View your predicted job role
   - Click "View Jobs on LinkedIn" to see live job listings

### For Developers:

#### URL Routes:
- Main page: `/job-recommendation/`
- API endpoint: `/job-recommendation/api/recommend/` (POST)
- History page: `/job-recommendation/history/` (requires login)

#### API Usage Example:
```python
import requests

url = "http://localhost:8000/job-recommendation/api/recommend/"
data = {
    "resume_text": "Python, Django, REST API, PostgreSQL, Docker"
}
headers = {
    "Content-Type": "application/json",
    "X-CSRFToken": "your-csrf-token"
}

response = requests.post(url, json=data, headers=headers)
result = response.json()

print(result)
# Output:
# {
#     "success": True,
#     "data": {
#         "predicted_role": "Backend Developer",
#         "role_slug": "backend-developer",
#         "confidence": 85.5,
#         "linkedin_url": "https://in.linkedin.com/jobs/backend-developer-jobs",
#         "message": "Based on your profile, we recommend applying for Backend Developer positions."
#     }
# }
```

## Database Model

### JobRecommendationHistory
- **user**: ForeignKey to User (nullable for anonymous users)
- **resume_text**: TextField (stores input text, max 1000 chars)
- **predicted_role**: CharField (AI-predicted job role)
- **jobs_found**: IntegerField (number of jobs found, currently 0)
- **created_at**: DateTimeField (auto-generated timestamp)

## ML Models

### Model Files Location:
`job_recommendation/models/`

- **tfidf_vectorizer_job_recommendation.pkl**: TF-IDF vectorizer trained on job descriptions
- **rf_classifier_job_recommendation.pkl**: Random Forest classifier for job prediction

### Supported Job Roles (Examples):
- Python Developer
- Data Scientist
- Machine Learning Engineer
- Backend Developer
- Frontend Developer
- Full Stack Developer
- DevOps Engineer
- Data Analyst
- etc.

## Next Steps & Enhancements

### To Enable Scraping (Optional):
If you want to add live job scraping functionality:
1. Add `selenium` and `webdriver-manager` to requirements.txt
2. Update Dockerfile to install Chrome/Chromium
3. Implement scraping logic in `job_utils.py` using the code from `app.py`

### Recommended Enhancements:
1. **Cache predictions** - Store recent predictions to speed up repeated queries
2. **Job database** - Create a local job database to avoid LinkedIn dependencies
3. **Resume file upload** - Allow users to upload PDF/DOCX files directly
4. **Skills extraction** - Use NLP to automatically extract skills from resume text
5. **Multiple predictions** - Show top 3 role recommendations with confidence scores
6. **Email alerts** - Send email notifications when new jobs are available
7. **Advanced filters** - Add location, experience level, salary filters

## Testing

### To test the integration:

1. **Start Docker containers**:
```bash
cd Ai_Resume_detectionnew/Ai_Resume_detection
docker-compose up --build
```

2. **Run migrations** (inside Docker container):
```bash
docker exec -it ai_resume_detection-web-1 python manage.py makemigrations
docker exec -it ai_resume_detection-web-1 python manage.py migrate
```

3. **Access the application**:
   - Homepage: http://localhost:8000/
   - Job Recommendation: http://localhost:8000/job-recommendation/

4. **Test the functionality**:
   - Enter skills: "Python, Machine Learning, TensorFlow, Data Analysis"
   - Click "Get Job Recommendations"
   - Verify the predicted role appears
   - Click the LinkedIn button to verify the URL

## Troubleshooting

### Issue: Models not loading
**Solution**: Ensure .pkl files are in `job_recommendation/models/` directory

### Issue: URL not found (404)
**Solution**: 
- Verify `job_recommendation` is in INSTALLED_APPS
- Check that urls.py includes the job_recommendation URLs
- Restart Docker containers

### Issue: Template not found
**Solution**: 
- Verify templates are in `job_recommendation/templates/job_recommendation/`
- Restart Docker containers

### Issue: Import errors
**Solution**: 
- Ensure all requirements are installed
- Check that scikit-learn is in requirements.txt
- Rebuild Docker image: `docker-compose up --build`

## Architecture

```
job_recommendation/
├── __init__.py
├── apps.py              # App configuration
├── models.py            # Database models
├── admin.py             # Admin interface
├── views.py             # View functions & API endpoints
├── urls.py              # URL routing
├── job_utils.py         # Core ML logic
├── migrations/          # Database migrations
│   └── __init__.py
├── models/              # ML model files
│   ├── tfidf_vectorizer_job_recommendation.pkl
│   └── rf_classifier_job_recommendation.pkl
└── templates/
    └── job_recommendation/
        ├── job_recommendation.html  # Main page
        └── history.html             # History page
```

## Credits

Original Streamlit app: `job_recommed_new/app.py`
Adapted and integrated into Django by: Cursor AI
Date: November 2025

## Support

For issues or questions:
1. Check this documentation
2. Review the code comments in `job_utils.py` and `views.py`
3. Check Django logs for detailed error messages
4. Verify model files are present and not corrupted

---

**Status**: ✅ Fully Integrated and Ready to Use
**Last Updated**: November 19, 2025


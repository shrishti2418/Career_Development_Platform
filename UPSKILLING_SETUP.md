# AI-Based Upskilling Recommendation System - Setup Guide

## ✨ Features Added
- **Free AI-Powered Analysis** - Uses sentence-transformers (no paid APIs)
- **Skill Gap Detection** - Semantic matching with embeddings
- **Course Recommendations** - 50+ free courses from Coursera, YouTube, edX, etc.
- **18+ Job Roles** - Pre-configured role requirements
- **Beautiful UI** - Modern, responsive design

## 🚀 Quick Start with Docker

### Step 1: Build and Run with Docker Compose
```bash
cd Ai_Resume_detection
docker-compose up --build
```

This will:
1. Install all dependencies (Django, sentence-transformers, scikit-learn, etc.)
2. Download the spaCy language model
3. Run database migrations
4. Start the development server on `http://localhost:8000`

### Step 2: Access the Application
Open your browser and go to:
- **Main App**: http://localhost:8000
- **Upskilling Page**: http://localhost:8000/upskilling/
- **Admin Panel**: http://localhost:8000/admin/

### Step 3: Create Admin User (Optional)
In a new terminal:
```bash
docker-compose exec web python manage.py createsuperuser
```

## 📦 Manual Installation (Without Docker)

If you prefer not to use Docker:

```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Download spaCy model
python -m spacy download en_core_web_sm

# 5. Run migrations
python manage.py makemigrations
python manage.py migrate

# 6. Start server
python manage.py runserver
```

## 🎯 How to Use

### 1. Navigate to Upskilling Page
Click the **"Upskilling"** button in the navbar (gold color with graduation cap icon).

### 2. Upload Resume
- Supports PDF and DOCX formats
- Drag and drop or click to upload

### 3. Enter Target Job Role
Choose from pre-configured roles or type custom role:
- Full Stack Developer
- Backend Developer
- Frontend Developer
- Data Scientist
- Machine Learning Engineer
- DevOps Engineer
- Cloud Engineer
- Mobile Developer
- And more...

### 4. Get Instant Results
The system will show:
- ✅ **Skills Detected** - From your resume
- 📊 **Match Percentage** - How well you match the role
- ❌ **Skill Gaps** - What you need to learn
- 📚 **Course Recommendations** - Top 10 free courses

## 🆓 100% Free Technologies Used

### AI/ML Stack (All Free & Open Source)
- **sentence-transformers** - Free embeddings for semantic matching
- **scikit-learn** - Cosine similarity calculations
- **faiss-cpu** - Fast similarity search (local, no API)
- **spaCy** - Natural language processing

### No Paid APIs Required
- ❌ No OpenAI
- ❌ No Gemini
- ❌ No Claude
- ❌ No paid embedding services
- ✅ Everything runs locally!

## 📚 Course Database

The system includes 50+ free courses from:
- Coursera (free audit options)
- YouTube
- edX
- freeCodeCamp
- Microsoft Learn
- Google Cloud Skills Boost

### Courses Cover:
- Programming (Python, JavaScript, Java, C++, Go, Rust)
- Web Development (React, Angular, Vue, Node.js, Django, Flask)
- Mobile Development (React Native, Flutter, Swift, Kotlin)
- Data Science & ML (TensorFlow, PyTorch, Pandas, scikit-learn)
- DevOps (Docker, Kubernetes, Jenkins, Terraform)
- Cloud (AWS, Azure, GCP)
- Databases (SQL, MongoDB, PostgreSQL, Redis)
- And more...

## 🔧 Technical Architecture

### Backend Flow:
1. **Resume Parser** (`upskilling_utils.py`)
   - Extracts text from PDF/DOCX
   - Uses spaCy for skill extraction

2. **Skill Gap Analysis**
   - Loads job role requirements from `courses_database.json`
   - Uses sentence-transformers for semantic matching
   - Calculates cosine similarity between skills

3. **Course Recommendation**
   - Matches missing skills with course catalog
   - Ranks courses by relevance score
   - Returns top 10 recommendations

### Frontend:
- Vanilla JavaScript (no build step required)
- Responsive CSS design
- Real-time API communication
- Beautiful UI with gradient effects

## 📊 Database Models

### UpskillingAnalysis Model
Stores:
- User (FK to auth.User)
- Target job role
- Skills detected (JSON)
- Skills required (JSON)
- Skill gaps (JSON)
- Recommended courses (JSON)
- Timestamp

## 🎨 UI Features

- **Modern Design** - Gradient backgrounds, smooth animations
- **Responsive** - Works on mobile, tablet, desktop
- **Real-time Feedback** - Loading spinners, error messages
- **Color-coded Results** - Green for matched, red for missing
- **Course Cards** - Beautiful course display with platform logos
- **History View** - See past analyses (for logged-in users)

## 🔐 Authentication

- Upskilling works for both **guest** and **authenticated** users
- Authenticated users get **history tracking**
- Results are saved in database for logged-in users

## 🌐 API Endpoints

### POST `/api/upskilling/analyze/`
Analyzes resume and returns recommendations.

**Request:**
```json
{
  "resume_file": <file>,
  "target_job_role": "Full Stack Developer"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "target_job_role": "Full Stack Developer",
    "skills_detected": [...],
    "skills_required": [...],
    "gap_analysis": {
      "matched_skills": [...],
      "missing_skills": [...],
      "match_percentage": 75.5
    },
    "recommended_courses": [...],
    "summary": "..."
  }
}
```

### GET `/api/upskilling/job-roles/`
Returns list of available job roles.

## 🎓 Adding New Courses

Edit `backend/courses_database.json`:

```json
{
  "id": 51,
  "title": "Your Course Title",
  "platform": "Platform Name",
  "url": "https://course-url.com",
  "skills": ["Skill1", "Skill2"],
  "level": "Beginner|Intermediate|Advanced",
  "duration": "X hours"
}
```

## 🎯 Adding New Job Roles

Edit `backend/courses_database.json` under `job_role_skills`:

```json
"Your Job Role": ["Skill1", "Skill2", "Skill3"]
```

## 🐛 Troubleshooting

### Issue: "Model not found"
```bash
python -m spacy download en_core_web_sm
```

### Issue: "sentence-transformers taking long time"
First run downloads the model (~90MB). Subsequent runs are fast.

### Issue: Docker build fails
Make sure Docker Desktop is running and you have internet connection.

## 📝 Notes

- **First Analysis** may take 15-20 seconds (model loading)
- **Subsequent analyses** are faster (2-5 seconds)
- **Models are cached** in memory for performance
- **All processing is local** - no data sent to external APIs

## 🎉 Success!

Your AI Upskilling Recommendation System is now ready! Visit:
**http://localhost:8000/upskilling/**

Happy Upskilling! 🚀


# Troubleshooting Guide - Upskilling System

## Issue: "Failed to connect to the server" Error

### Quick Diagnostic Steps

#### Step 1: Check if Server is Running
Open terminal and check:
```bash
docker-compose ps
```

**Expected output:**
```
NAME                COMMAND                  SERVICE             STATUS
web-1               "sh -c 'python manag…"   web                 running
```

**If not running:**
```bash
cd Ai_Resume_detection
docker-compose up
```

---

#### Step 2: Check Server Logs
Look at the terminal where docker-compose is running. Look for:

**✅ Success (should see):**
```
web-1  | System check identified no issues
web-1  | Starting development server at http://0.0.0.0:8000/
```

**❌ Error (look for):**
```
ImportError: cannot import name 'SentenceTransformer'
ImportError: No module named 'sentence_transformers'
ModuleNotFoundError: No module named 'sklearn'
```

---

#### Step 3: Test API Endpoint Directly
Open browser and go to:
```
http://localhost:8000/api/upskilling/job-roles/
```

**Expected JSON response:**
```json
{
  "success": true,
  "upskilling_available": true,
  "job_roles": ["Full Stack Developer", "Backend Developer", ...]
}
```

**If you see `"upskilling_available": false`:**
- ML libraries not installed correctly
- See "Fix ML Libraries" section below

**If you get 404 or connection error:**
- Server not running
- Wrong port (check if it's 8000)

---

#### Step 4: Check Browser Console
1. Open upskilling page: http://localhost:8000/upskilling/
2. Press `F12` to open Developer Tools
3. Go to "Console" tab
4. Click "Analyze & Get Recommendations"
5. Look for error messages

**Common errors:**
- `TypeError: Failed to fetch` → Server not running
- `403 Forbidden` → CSRF token issue
- `500 Internal Server Error` → Server-side error (check logs)
- `503 Service Unavailable` → ML libraries not available

---

## Common Fixes

### Fix 1: Rebuild Docker with Updated Requirements
```bash
cd Ai_Resume_detection
docker-compose down
docker-compose up --build
```

Wait for complete build (5-10 minutes first time).

---

### Fix 2: Fix ML Libraries Installation

If you see `"upskilling_available": false`, the ML libraries didn't install correctly.

**Option A: Rebuild Docker**
```bash
docker-compose down -v
docker system prune -a  # Clean everything
docker-compose up --build
```

**Option B: Install in Running Container**
```bash
docker-compose exec web pip install torch==2.1.0 sentence-transformers==2.3.1 scikit-learn==1.3.0
docker-compose restart
```

---

### Fix 3: Clear Browser Cache
Sometimes old JavaScript is cached:
1. Press `Ctrl + Shift + R` (Windows/Linux)
2. Or `Cmd + Shift + R` (Mac)
3. This force-reloads the page

---

### Fix 4: Check CSRF Token
If you get 403 errors:
1. Make sure you're accessing via http://localhost:8000 (not file://)
2. Clear browser cookies
3. Try in incognito/private mode

---

### Fix 5: Port Already in Use
If port 8000 is busy:

**Windows:**
```powershell
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**Linux/Mac:**
```bash
lsof -ti:8000 | xargs kill -9
```

Then restart:
```bash
docker-compose up
```

---

## Detailed Error Messages

### Error: "Upskilling system is not available"
**Cause:** ML libraries (sentence-transformers, sklearn) not installed

**Fix:**
```bash
docker-compose down
docker-compose up --build
```

Check during build for:
```
Successfully installed torch-2.1.0 sentence-transformers-2.3.1 scikit-learn-1.3.0
```

---

### Error: "ImportError: cannot import name 'cached_download'"
**Cause:** Version mismatch between sentence-transformers and huggingface-hub

**Fix:** Already fixed in updated `requirements.txt`. Rebuild:
```bash
docker-compose up --build
```

---

### Error: "Server error: 500"
**Cause:** Python error in backend

**Steps:**
1. Look at terminal/docker logs
2. Find the full Python traceback
3. Common causes:
   - Missing import (logger, etc.)
   - Database not migrated
   - File permission issues

**Fix for migrations:**
```bash
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
docker-compose restart
```

---

## Verification Checklist

✅ **All these should work:**

1. **Server running**
   ```bash
   docker-compose ps
   # Should show "running"
   ```

2. **Main page loads**
   ```
   http://localhost:8000
   ```

3. **Upskilling page loads**
   ```
   http://localhost:8000/upskilling/
   ```

4. **API returns job roles**
   ```
   http://localhost:8000/api/upskilling/job-roles/
   # Should return JSON with job roles
   ```

5. **File upload works**
   - Upload a PDF resume
   - Enter "Full Stack Developer"
   - Click analyze
   - Should show results (not error)

---

## Manual Testing Commands

### Test 1: Check if ML libraries work
```bash
docker-compose exec web python -c "from sentence_transformers import SentenceTransformer; print('OK')"
```

**Expected:** `OK`

---

### Test 2: Check if database is ready
```bash
docker-compose exec web python manage.py showmigrations extractor
```

**Should show:**
```
[X] 0001_initial
[X] 0002_resume_achievements...
[X] 0007_login_signup
[X] 0008_upskillinganalysis (new)
```

If missing, run:
```bash
docker-compose exec web python manage.py migrate
```

---

### Test 3: Check Python environment
```bash
docker-compose exec web pip list | grep -E "sentence|torch|sklearn"
```

**Expected:**
```
sentence-transformers  2.3.1
scikit-learn          1.3.0
torch                 2.1.0
```

---

## Still Not Working?

### Get Detailed Logs
```bash
docker-compose logs web --tail=100
```

### Try Local Installation (Without Docker)
```bash
cd Ai_Resume_detection

# Create venv
python -m venv venv

# Activate
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Test import
python -c "from extractor.upskilling_utils import get_job_roles_list; print(get_job_roles_list())"

# Run server
python manage.py runserver
```

If this works, the issue is Docker-specific.

---

## Get Help

If still stuck, provide:
1. **Server logs** (from `docker-compose logs`)
2. **Browser console errors** (from F12 Developer Tools)
3. **Output of:**
   ```bash
   docker-compose ps
   curl http://localhost:8000/api/upskilling/job-roles/
   ```

This will help diagnose the exact issue! 🚀


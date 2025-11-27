
import re
import logging
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .form import ResumeForm, DemoResumeForm
from .utils import extract_resume_data, calculate_experience, extract_text_from_docx, extract_text_from_pdf, ats_checker
from .models import Resume
from rest_framework.decorators import api_view
from rest_framework.response import Response
import openai
from transformers import pipeline

# Initialize logger
logger = logging.getLogger(__name__)
def index(request):
    context = {}
    if request.method == "POST":
        form = DemoResumeForm(request.POST, request.FILES)
        context['form'] = form
        if form.is_valid():
            resume_file = request.FILES["file"]
            file_name = resume_file.name.lower()

            if file_name.endswith('.pdf'):
                file_type = "pdf"
            elif file_name.endswith('.docx'):
                file_type = "docx"
            else:
                form.add_error(None, 'Unsupported file type. Please upload a PDF or DOCX file.')
                return render(request, "extractor/index.html", context)

            # Extract resume data using utility function
            data = extract_resume_data(resume_file, file_type=file_type)

            # Check if extraction returned error or empty text
            if "error" in data or not data.get("summary"):
                form.add_error(None, 'Failed to extract data from the resume. Please upload a valid PDF or DOCX file.')
                return render(request, "extractor/index.html", context)

            # Check if demo ATS check is requested
            demo_job_description = request.POST.get("demo_job_description", "").strip()
            if demo_job_description:
                # Perform demo ATS check with short responses
                resume_text = extract_text_from_pdf(resume_file) if file_type == "pdf" else extract_text_from_docx(resume_file)
                if resume_text:
                    ats_result = ats_checker(resume_text, demo_job_description)
                    if "error" not in ats_result:
                        context['demo_ats_score'] = ats_result["match_percentage"]
                        context['demo_matched_skills'] = ", ".join(ats_result["matched_skills"][:5])  # Short list
                        context['demo_missing_skills'] = ", ".join(ats_result["missing_skills"][:3])  # Short list
                        context['demo_message'] = f"Demo ATS Score: {ats_result['match_percentage']}%. Matched: {len(ats_result['matched_skills'])} skills."
                    else:
                        context['demo_message'] = "Demo ATS check failed. Please try the full ATS Checker."
                else:
                    context['demo_message'] = "Failed to extract text for demo ATS check."

            # Assign extracted data to context for display
            context['skills'] = ", ".join(data.get("skills", []))
            context['summary'] = data.get("summary", "")
            context['experience'] = data.get("experience", "Fresher")
            context['education'] = data.get("education", "")
            context['projects'] = data.get("projects", "")
            achievements = data.get("achievements")
            if isinstance(achievements, list):
                context['achievements'] = ", ".join(achievements)
            else:
                context['achievements'] = achievements or ""

            # Add GitHub links from extracted data
            context['github_links'] = data.get("github_links", "")
            context['short_summary'] = data.get("short_summary", "")
            context['total_experience'] = calculate_experience(context['summary'] + " " + context['experience'])
            context['message'] = "Resume analyzed successfully."
            context['scroll_to'] = 'results'

            # Save resume to database if user is authenticated
            if request.user.is_authenticated:
                resume_instance = Resume(
                    user=request.user,
                    file=resume_file,
                    skills=", ".join(data.get("skills", [])),
                    summary=data.get("summary", ""),
                    experience=data.get("experience", "Fresher"),
                    education=data.get("education", ""),
                    projects=data.get("projects", ""),
                    achievements=", ".join(data.get("achievements", [])) if isinstance(data.get("achievements"), list) else data.get("achievements", ""),
                    github_links=data.get("github_links", ""),
                )
                resume_instance.save()
        else:
            context['message'] = "Form submission failed. Please check the errors below."
    else:
        context['form'] = ResumeForm()
        if request.user.is_authenticated:
            resumes = Resume.objects.filter(user=request.user).order_by('-uploaded_at')
            context['resumes'] = resumes

    return render(request, "extractor/index.html", context)

@login_required
def upload_resume(request):
    if request.method == "POST":
        form = ResumeForm(request.POST, request.FILES)
        if form.is_valid():
            resume_instance = form.save(commit=False)
            resume_instance.user = request.user
            resume_file = request.FILES["file"]
            file_name = resume_file.name.lower()

            if file_name.endswith('.pdf'):
                file_type = "pdf"
            elif file_name.endswith('.docx'):
                file_type = "docx"
            else:
                # Unsupported file type
                form.add_error('file', 'Unsupported file type. Please upload a PDF or DOCX file.')
                return render(request, "extractor/upload.html", {"form": form})

            # Extract resume data using utility function
            data = extract_resume_data(resume_file, file_type=file_type)

            # Check if extraction returned error or empty text
            if "error" in data or not data.get("summary"):
                form.add_error('file', 'Failed to extract data from the resume. Please upload a valid PDF or DOCX file.')
                return render(request, "extractor/upload.html", {"form": form})

            # Assign extracted data to resume instance
            resume_instance.skills = ", ".join(data.get("skills", []))
            resume_instance.summary = data.get("summary", "")
            resume_instance.experience = data.get("experience", "Fresher")
            resume_instance.education = data.get("education", "")
            resume_instance.projects = data.get("projects", "")
            achievements = data.get("achievements")
            if isinstance(achievements, list):
                resume_instance.achievements = ", ".join(achievements)
            else:
                resume_instance.achievements = achievements or ""

            # Add GitHub links from extracted data
            resume_instance.github_links = data.get("github_links", "")

            resume_instance.save()

            context = {
                "form": ResumeForm(),
                "short_summary": data.get("short_summary", ""),
                "skills": resume_instance.skills,
                "summary": resume_instance.summary,
                "experience": resume_instance.experience,
                "achievements": resume_instance.achievements,
                "total_experience": calculate_experience(resume_instance.summary + " " + resume_instance.experience),
                "projects": resume_instance.projects,
                "education": resume_instance.education,
                "github_links": resume_instance.github_links,
                "message": "Resume uploaded and processed successfully."
            }

            # Check for optional ATS check
            job_description = request.POST.get("job_description", "").strip()
            if job_description:
                # Extract text for ATS check
                resume_text = extract_text_from_pdf(resume_file) if file_type == "pdf" else extract_text_from_docx(resume_file)
                if resume_text:
                    ats_result = ats_checker(resume_text, job_description)
                    if "error" not in ats_result:
                        context.update({
                            "ats_result": ats_result,
                            "job_description": job_description,
                            "missing_count": ats_result["total_jd_skills"] - ats_result["match_count"],
                            "missing_indices": list(range(ats_result["total_jd_skills"] - ats_result["match_count"])),
                            "resume_text": resume_text[:500] + "..." if len(resume_text) > 500 else resume_text,
                            "message": "Resume uploaded, processed, and ATS checked successfully."
                        })
                    else:
                        context["message"] = "Resume uploaded successfully, but ATS check failed: " + ats_result["error"]
                else:
                    context["message"] = "Resume uploaded successfully, but failed to extract text for ATS check."

            return render(request, "extractor/upload.html", context)
        else:
            return render(request, "extractor/upload.html", {"form": form})

    else:
        form = ResumeForm()
        return render(request, "extractor/upload.html", {"form": form})
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseServerError

# ATS Checker View
def ats_checker_view(request):
    if request.method == "POST":
        job_description = request.POST.get("job_description", "").strip()
        resume_file = request.FILES.get("resume_file")

        if not resume_file:
            return render(request, "extractor/ats_checker.html", {"error": "Please upload a resume file."})

        file_name = resume_file.name.lower()

        if file_name.endswith('.pdf'):
            resume_text = extract_text_from_pdf(resume_file)
        elif file_name.endswith('.docx'):
            resume_text = extract_text_from_docx(resume_file)
        else:
            return render(request, "extractor/ats_checker.html", {"error": "Unsupported file type. Please upload a PDF or DOCX file."})

        if not resume_text:
            return render(request, "extractor/ats_checker.html", {"error": "Failed to extract text from the resume."})

        ats_result = ats_checker(resume_text, job_description)

        if "error" in ats_result:
            return render(request, "extractor/ats_checker.html", {"error": ats_result["error"]})

        return render(request, "extractor/ats_checker.html", {"ats_result": ats_result})

    return render(request, "extractor/ats_checker.html")


@api_view(["POST"])
def ats_checker_api(request):
    job_description = request.data.get("job_description", "").strip()
    resume_file = request.FILES.get("resume_file")

    if not job_description:
        return Response({"error": "Please provide a job description."}, status=400)
    if not resume_file:
        return Response({"error": "Please upload a resume file."}, status=400)

    file_name = resume_file.name.lower()
    if file_name.endswith('.pdf'):
        resume_text = extract_text_from_pdf(resume_file)
    elif file_name.endswith('.docx'):
        resume_text = extract_text_from_docx(resume_file)
    else:
        return Response({"error": "Unsupported file type."}, status=400)

    if not resume_text:
        return Response({"error": "Failed to extract text from the resume."}, status=500)

    ats_result = ats_checker(resume_text, job_description)

    if "error" in ats_result:
        return Response({"error": ats_result["error"]}, status=500)

    return Response({
        "job_description": job_description,
        "ats_result": ats_result,
        "resume_preview": resume_text[:500] + "..." if len(resume_text) > 500 else resume_text
    })


def chat_view(request):
    return render(request, "extractor/chat.html")


@api_view(["POST"])
def chat_api(request):
    user_message = request.data.get("message", "").strip()
    if not user_message:
        return Response({"response": "Please enter a message."})

    system_prompt = """
    You are a helpful chatbot for the AI Resume Detection company. Your role is to assist users with questions related to resume analysis, uploading resumes, ATS checking, and general inquiries about our services. Do not answer questions outside of these topics. If a question is unrelated, politely redirect to resume-related topics.
    """

    try:
        # Try using OpenAI API for better responses
        openai.api_key = settings.OPENAI_API_KEY if hasattr(settings, 'OPENAI_API_KEY') else None
        if openai.api_key:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=150,
                temperature=0.7,
                top_p=0.9
            )
            bot_response = response.choices[0].message.content.strip()
        else:
            # Fallback to DialoGPT if no OpenAI key
            chat_pipeline = pipeline("text-generation", model="microsoft/DialoGPT-medium")
            input_text = system_prompt + "\nUser: " + user_message + "\nBot:"
            generated = chat_pipeline(input_text, max_length=150, num_return_sequences=1, temperature=0.6, pad_token_id=50256, do_sample=True, top_p=0.9)
            full_response = generated[0]['generated_text']
            bot_part = full_response.split("Bot:")[-1].strip()
            bot_response = bot_part.split('\n')[0].strip()
            if not bot_response or len(bot_response) < 5:
                bot_response = "I'm here to help with resume-related questions. How can I assist you?"
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        bot_response = "Sorry, I'm having trouble responding right now. Please try again later."

    return Response({"response": bot_response})


from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import redirect
from .form import CustomUserCreationForm

def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        if password1 != password2:
            return JsonResponse({'error': 'Passwords do not match.'}, status=400)
        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Username already exists.'}, status=400)
        if User.objects.filter(email=email).exists():
            return JsonResponse({'error': 'Email already exists.'}, status=400)
        try:
            user = User.objects.create_user(username=username, email=email, password=password1)
            login(request, user)
            return JsonResponse({'message': 'User created successfully.'}, status=201)
        except Exception as e:
            return JsonResponse({'error': f'Error creating account: {str(e)}'}, status=500)
    return render(request, 'extractor/signup.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = User.objects.filter(email=email).first()
        if user:
            user = authenticate(request, username=user.username, password=password)
            if user is not None:
                login(request, user)
                return redirect('index')
            else:
                return JsonResponse({'error': 'Invalid email or password.'}, status=400)
        else:
            return JsonResponse({'error': 'Invalid email or password.'}, status=400)
    return render(request, 'extractor/login.html')

def new_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, "Invalid username or password.")
            return render(request, 'extractor/new_login.html')
    return render(request, 'extractor/new_login.html')

def new_signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'extractor/new_signup.html')
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, 'extractor/new_signup.html')
        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)
        return redirect('index')
    return render(request, 'extractor/new_signup.html')

@login_required
def profile_view(request):
    from .models import UserProfile
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    resumes = Resume.objects.filter(user=request.user).order_by('-uploaded_at')
    upskilling_analyses = UpskillingAnalysis.objects.filter(user=request.user).order_by('-created_at')

    # Parse JSON fields for upskilling analyses
    for analysis in upskilling_analyses:
        try:
            analysis.skills_detected_list = json_module.loads(analysis.skills_detected) if analysis.skills_detected else []
            analysis.skill_gaps_list = json_module.loads(analysis.skill_gaps) if analysis.skill_gaps else []
            analysis.recommended_courses_list = json_module.loads(analysis.recommended_courses) if analysis.recommended_courses else []
        except:
            analysis.skills_detected_list = []
            analysis.skill_gaps_list = []
            analysis.recommended_courses_list = []

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        user_profile.name = name
        user_profile.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('profile')
    return render(request, "extractor/profile.html", {"user_profile": user_profile, "resumes": resumes, "upskilling_analyses": upskilling_analyses})

#logout
from django.contrib.auth import logout
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('index')
    return render(request, 'extractor/logout.html')


# ==================== UPSKILLING SYSTEM ====================
# Free AI-based upskilling recommendation system
# No paid APIs - uses sentence-transformers and scikit-learn

import json as json_module
from .models import UpskillingAnalysis

# Import upskilling utilities with error handling
try:
    from .upskilling_utils import (
        generate_upskilling_report,
        get_job_roles_list
    )
    UPSKILLING_AVAILABLE = True
except ImportError as e:
    logger.error(f"Upskilling utilities not available: {e}")
    UPSKILLING_AVAILABLE = False
    # Provide fallback functions
    def generate_upskilling_report(*args, **kwargs):
        return {"error": "Upskilling system not available. Please install required ML packages."}
    def get_job_roles_list():
        return []

def upskilling_view(request):
    """
    Main upskilling page view
    """
    job_roles = get_job_roles_list()
    context = {
        'job_roles': job_roles
    }
    
    # Show user's previous analyses if authenticated
    if request.user.is_authenticated:
        previous_analyses = UpskillingAnalysis.objects.filter(user=request.user)[:5]
        context['previous_analyses'] = previous_analyses
    
    return render(request, 'extractor/upskilling.html', context)


@api_view(['POST'])
def upskilling_analyze_api(request):
    """
    API endpoint for upskilling analysis
    Accepts: resume file + target job role
    Returns: skill gaps + course recommendations (all FREE AI)
    """
    try:
        # Check if upskilling system is available
        if not UPSKILLING_AVAILABLE:
            return Response({
                "error": "Upskilling system is not available. ML libraries may not be installed. Please check server logs."
            }, status=503)
        
        # Get inputs
        resume_file = request.FILES.get('resume_file')
        target_job_role = request.data.get('target_job_role', '').strip()
        
        # Validation
        if not resume_file:
            return Response({
                "error": "Please upload a resume file."
            }, status=400)
        
        if not target_job_role:
            return Response({
                "error": "Please specify a target job role."
            }, status=400)
        
        # Validate file type
        file_name = resume_file.name.lower()
        if not (file_name.endswith('.pdf') or file_name.endswith('.docx')):
            return Response({
                "error": "Unsupported file format. Please upload PDF or DOCX."
            }, status=400)
        
        # Generate upskilling report using FREE AI
        logger.info(f"Generating upskilling report for role: {target_job_role}")
        report = generate_upskilling_report(resume_file, target_job_role)
        
        if "error" in report:
            return Response({
                "error": report["error"]
            }, status=500)
        
        # Save to database if user is authenticated
        if request.user.is_authenticated:
            try:
                analysis = UpskillingAnalysis.objects.create(
                    user=request.user,
                    target_job_role=target_job_role,
                    skills_detected=json_module.dumps(report["skills_detected"]),
                    skills_required=json_module.dumps(report["skills_required"]),
                    skill_gaps=json_module.dumps(report["gap_analysis"]["missing_skills"]),
                    recommended_courses=json_module.dumps(report["recommended_courses"])
                )
                logger.info(f"Saved upskilling analysis for user: {request.user.username}")
            except Exception as e:
                logger.error(f"Error saving upskilling analysis: {e}")
        
        return Response({
            "success": True,
            "data": report
        })
    
    except Exception as e:
        logger.error(f"Error in upskilling analysis: {e}")
        return Response({
            "error": f"An error occurred: {str(e)}"
        }, status=500)


@api_view(['GET'])
def upskilling_job_roles_api(request):
    """
    API endpoint to get list of available job roles
    """
    try:
        job_roles = get_job_roles_list()
        return Response({
            "success": True,
            "upskilling_available": UPSKILLING_AVAILABLE,
            "job_roles": job_roles
        })
    except Exception as e:
        logger.error(f"Error fetching job roles: {e}")
        return Response({
            "error": str(e)
        }, status=500)


@login_required
def upskilling_history_view(request):
    """
    View user's upskilling analysis history
    """
    analyses = UpskillingAnalysis.objects.filter(user=request.user).order_by('-created_at')
    
    # Parse JSON fields for display
    for analysis in analyses:
        try:
            analysis.skills_detected_list = json_module.loads(analysis.skills_detected) if analysis.skills_detected else []
            analysis.skill_gaps_list = json_module.loads(analysis.skill_gaps) if analysis.skill_gaps else []
            analysis.recommended_courses_list = json_module.loads(analysis.recommended_courses) if analysis.recommended_courses else []
        except:
            analysis.skills_detected_list = []
            analysis.skill_gaps_list = []
            analysis.recommended_courses_list = []
    
    return render(request, 'extractor/upskilling_history.html', {
        'analyses': analyses
    })


    

    

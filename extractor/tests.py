import json
from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Resume
from .utils import (
    extract_text_from_pdf, extract_text_from_docx, calculate_experience,
    extract_summary, extract_experience, extract_skills, extract_achievements,
    extract_github_links, extract_resume_data, ats_checker
)
from unittest.mock import patch, MagicMock
import io

class UtilsTestCase(TestCase):
    def test_extract_text_from_pdf(self):
        # Mock PDF file
        mock_pdf = SimpleUploadedFile("test.pdf", b"Sample PDF text", content_type="application/pdf")
        with patch('extractor.utils.PdfReader') as mock_reader:
            mock_page = MagicMock()
            mock_page.extract_text.return_value = "Sample PDF text"
            mock_reader.return_value.pages = [mock_page]
            text = extract_text_from_pdf(mock_pdf)
            self.assertEqual(text, "Sample PDF text\n")

    def test_extract_text_from_docx(self):
        # Mock DOCX file
        mock_docx = SimpleUploadedFile("test.docx", b"Sample DOCX text", content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        with patch('extractor.utils.Document') as mock_doc:
            mock_para = MagicMock()
            mock_para.text = "Sample DOCX text"
            mock_doc.return_value.paragraphs = [mock_para]
            text = extract_text_from_docx(mock_docx)
            self.assertEqual(text, "Sample DOCX text")

    def test_calculate_experience(self):
        text = "Jan 2020 - Mar 2022"
        experience = calculate_experience(text)
        self.assertEqual(experience, "2 years 2 months")

    def test_extract_summary(self):
        text = "Summary: Experienced developer."
        summary = extract_summary(text)
        self.assertIn("Experienced developer", summary)

    def test_extract_experience(self):
        text = "Experience: Worked at XYZ Corp."
        experience = extract_experience(text)
        self.assertIn("XYZ Corp", experience)

    def test_extract_skills(self):
        text = "Skills: Python, Django"

        class MockPath:
            def __init__(self, *args):
                pass
            def __truediv__(self, other):
                return MockPath()

        with patch('extractor.utils.Path', MockPath):
            with patch('builtins.open', create=True) as mock_open:
                with patch('json.load', return_value={"skills": ["Python", "Django"]}):
                    with patch('django.conf.settings.BASE_DIR', "/fake/path"):
                        skills = extract_skills(text)
                        self.assertIn("Python", skills)

    def test_extract_achievements(self):
        text = "Achievements: Won award."
        achievements = extract_achievements(text)
        self.assertIsInstance(achievements, list)
        self.assertIn("Won award", achievements[0])

    def test_extract_github_links(self):
        text = "GitHub: https://github.com/user/repo"
        links = extract_github_links(text)
        self.assertEqual(links, "https://github.com/user/repo")

    def test_extract_resume_data(self):
        mock_file = SimpleUploadedFile("test.pdf", b"Sample text", content_type="application/pdf")
        with patch('extractor.utils.extract_text_from_pdf', return_value="Sample resume text"):
            with patch('extractor.utils.extract_summary', return_value="Summary"):
                with patch('extractor.utils.extract_experience', return_value="Experience"):
                    with patch('extractor.utils.extract_skills', return_value=["Python"]):
                        with patch('extractor.utils.extract_achievements', return_value=["Award"]):
                            with patch('extractor.utils.extract_education', return_value="Education"):
                                with patch('extractor.utils.extract_projects', return_value="Projects"):
                                    with patch('extractor.utils.extract_github_links', return_value=""):
                                        with patch('extractor.utils.calculate_experience', return_value="1 year"):
                                            data = extract_resume_data(mock_file, "pdf")
                                            self.assertIn("summary", data)
                                            self.assertEqual(data["summary"], "Summary")

    def test_ats_checker(self):
        resume_text = "Python developer"
        jd = "Looking for Python skills"
        with patch('extractor.utils.extract_skills', return_value=["Python"]):
            with patch('extractor.utils.extract_skills_from_jd', return_value=["Python"]):
                with patch('extractor.utils.semantic_similarity_missing_skills', return_value=[]):
                    result = ats_checker(resume_text, jd)
                    self.assertIn("match_percentage", result)
                    self.assertEqual(result["match_percentage"], 100.0)


class ViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

    def test_index_view_authenticated(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'extractor/index.html')

    def test_upload_resume_view_get(self):
        response = self.client.get('/upload/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'extractor/upload.html')

    def test_ats_checker_view_get(self):
        response = self.client.get('/ats_checker/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'extractor/ats_checker.html')

    def test_profile_view(self):
        response = self.client.get('/profile/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'extractor/profile.html')
        self.assertIn('user_profile', response.context)
        self.assertEqual(response.context['user_profile'].user, self.user)

    def test_profile_view_post(self):
        response = self.client.post('/profile/', {'name': 'Test Name'})
        self.assertEqual(response.status_code, 302)  # Redirect after successful update
        self.user.userprofile.refresh_from_db()
        self.assertEqual(self.user.userprofile.name, 'Test Name')


class APITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')

    def test_ats_checker_api(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'job_description': 'Python developer needed',
            'resume_file': SimpleUploadedFile("test.pdf", b"Sample", content_type="application/pdf")
        }
        with patch('extractor.views.extract_text_from_pdf', return_value="Python skills"):
            with patch('extractor.views.ats_checker', return_value={'match_percentage': 50.0}):
                response = self.client.post('/api/ats_checker/', data, format='multipart')
                self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_chat_api(self):
        self.client.force_authenticate(user=self.user)
        data = {'message': 'Hello'}
        with patch('openai.OpenAI') as mock_openai:
            mock_choice = MagicMock()
            mock_choice.message.content = "Hi there!"
            mock_response = MagicMock()
            mock_response.choices = [mock_choice]
            mock_openai.return_value.chat.completions.create.return_value = mock_response
            response = self.client.post('/api/chat/', data, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)

import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from extractor.utils import extract_resume_data

# Test with the PDF file
pdf_path = 'media/resumes/Monu_Maurya_FullStack_Resume.pdf'
try:
    with open(pdf_path, 'rb') as f:
        data = extract_resume_data(f, file_type='pdf')

    if "error" in data:
        print(f"Error: {data['error']}")
    else:
        print("Extracted Data:")
        for key, value in data.items():
            print(f"{key}: {value}")
except FileNotFoundError:
    print(f"File not found: {pdf_path}")
except Exception as e:
    print(f"Exception: {e}")

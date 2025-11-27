import requests
from bs4 import BeautifulSoup

# Get the page
response = requests.get('http://localhost:8000')
soup = BeautifulSoup(response.text, 'html.parser')

# Find CSRF token
csrf_input = soup.find('input', {'name': 'csrfmiddlewaretoken'})
if csrf_input:
    csrf_token = csrf_input['value']
    print("CSRF Token:", csrf_token)
else:
    print("CSRF token not found")
    csrf_token = None

# Post the form with demo_job_description
files = {'file': open('media/resumes/Monu_Maurya_FullStack_Resume.pdf', 'rb')}
data = {'csrfmiddlewaretoken': csrf_token, 'demo_job_description': 'Python Developer'}

post_response = requests.post('http://localhost:8000', files=files, data=data, cookies=response.cookies)

# Check if "Extracted Information" in response
if "Extracted Information" in post_response.text:
    print("SUCCESS: Extracted Information found in response")
else:
    print("FAILURE: Extracted Information not found")
    print("Response status:", post_response.status_code)
    # Print part of response
    print("Response text (first 1000 chars):", post_response.text[:1000])

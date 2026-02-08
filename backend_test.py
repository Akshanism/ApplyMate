import requests
import sys
import os
import io
from datetime import datetime

class ApplyMateAPITester:
    def __init__(self):
        # Use the public endpoint from frontend/.env
        self.base_url = "https://application-ready.preview.emergentagent.com"
        self.api_url = f"{self.base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.errors = []

    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
            self.errors.append(f"{name}: {details}")
            
        if details and success:
            print(f"   Details: {details}")

    def test_api_root(self):
        """Test the API root endpoint"""
        try:
            response = requests.get(f"{self.api_url}/", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                details += f", Response: {response.json()}"
            self.log_test("API Root Endpoint", success, details)
            return success
        except Exception as e:
            self.log_test("API Root Endpoint", False, str(e))
            return False

    def create_test_pdf_content(self):
        """Create a simple test PDF content (mock)"""
        # For testing purposes, we'll create a simple text file to simulate PDF
        return b"""John Doe
Software Engineer
Email: john.doe@email.com
Phone: (555) 123-4567

EXPERIENCE:
Software Engineer at TechCorp (2020-2023)
- Developed web applications using React and Node.js
- Implemented REST APIs and database integration
- Collaborated with cross-functional teams

SKILLS:
- Programming: Python, JavaScript, React
- Databases: MongoDB, PostgreSQL
- Tools: Git, Docker, AWS

EDUCATION:
Bachelor of Computer Science
State University (2016-2020)
"""

    def create_test_docx_content(self):
        """Create test DOCX content (mock)"""
        # Same content as PDF but in bytes format for DOCX simulation
        return self.create_test_pdf_content()

    def test_invalid_file_type(self):
        """Test API with invalid file type"""
        try:
            # Create a fake .txt file
            files = {'resume': ('test.txt', b'test content', 'text/plain')}
            data = {'job_description': 'Test job description'}
            
            response = requests.post(
                f"{self.api_url}/tailor-application",
                files=files,
                data=data,
                timeout=30
            )
            
            success = response.status_code == 400
            details = f"Status: {response.status_code}"
            if response.status_code == 400:
                details += f", Error: {response.json().get('detail', 'No detail')}"
            
            self.log_test("Invalid File Type Rejection", success, details)
            return success
        except Exception as e:
            self.log_test("Invalid File Type Rejection", False, str(e))
            return False

    def test_missing_job_description(self):
        """Test API with missing job description"""
        try:
            files = {'resume': ('test.pdf', self.create_test_pdf_content(), 'application/pdf')}
            data = {'job_description': ''}
            
            response = requests.post(
                f"{self.api_url}/tailor-application",
                files=files,
                data=data,
                timeout=30
            )
            
            success = response.status_code == 400
            details = f"Status: {response.status_code}"
            if response.status_code == 400:
                details += f", Error: {response.json().get('detail', 'No detail')}"
            
            self.log_test("Missing Job Description Validation", success, details)
            return success
        except Exception as e:
            self.log_test("Missing Job Description Validation", False, str(e))
            return False

    def test_valid_pdf_upload(self):
        """Test API with valid PDF file and job description"""
        try:
            files = {'resume': ('john_doe_resume.pdf', self.create_test_pdf_content(), 'application/pdf')}
            data = {
                'job_description': '''
Senior Software Engineer - Full Stack
Company: TechStart Inc.

We are looking for an experienced Full Stack Developer to join our team.

Requirements:
- 3+ years of experience in web development
- Proficiency in React, Node.js, and databases
- Experience with REST APIs
- Strong problem-solving skills
- Bachelor's degree in Computer Science or related field

Responsibilities:
- Develop and maintain web applications
- Design and implement REST APIs
- Work with databases and data modeling
- Collaborate with product and design teams
- Participate in code reviews
                '''
            }
            
            response = requests.post(
                f"{self.api_url}/tailor-application",
                files=files,
                data=data,
                timeout=60  # Longer timeout for AI processing
            )
            
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                result = response.json()
                # Validate response structure
                required_keys = ['resume_bullets', 'cover_letter', 'application_email']
                has_all_keys = all(key in result for key in required_keys)
                
                if has_all_keys:
                    details += f", Resume bullets: {len(result['resume_bullets'])}"
                    details += f", Cover letter length: {len(result['cover_letter'])} chars"
                    details += f", Email length: {len(result['application_email'])} chars"
                    
                    # Check if content is meaningful (not error messages)
                    is_meaningful = (
                        len(result['resume_bullets']) > 0 and
                        'Error' not in result['cover_letter'] and
                        'Error' not in result['application_email']
                    )
                    
                    if not is_meaningful:
                        success = False
                        details += " - Content appears to be error messages"
                else:
                    success = False
                    details += f" - Missing keys: {[k for k in required_keys if k not in result]}"
            else:
                if response.headers.get('content-type', '').startswith('application/json'):
                    details += f", Error: {response.json().get('detail', 'No detail')}"
                else:
                    details += f", Response: {response.text[:200]}..."
            
            self.log_test("Valid PDF Upload and Processing", success, details)
            return success, response.json() if success else None
        except Exception as e:
            self.log_test("Valid PDF Upload and Processing", False, str(e))
            return False, None

    def test_valid_docx_upload(self):
        """Test API with valid DOCX file"""
        try:
            files = {'resume': ('john_doe_resume.docx', self.create_test_docx_content(), 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
            data = {
                'job_description': 'Frontend Developer position requiring React and JavaScript skills.'
            }
            
            response = requests.post(
                f"{self.api_url}/tailor-application",
                files=files,
                data=data,
                timeout=60
            )
            
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                result = response.json()
                required_keys = ['resume_bullets', 'cover_letter', 'application_email']
                has_all_keys = all(key in result for key in required_keys)
                success = has_all_keys
                details += f", Has all required fields: {has_all_keys}"
            else:
                if response.headers.get('content-type', '').startswith('application/json'):
                    details += f", Error: {response.json().get('detail', 'No detail')}"
            
            self.log_test("Valid DOCX Upload and Processing", success, details)
            return success
        except Exception as e:
            self.log_test("Valid DOCX Upload and Processing", False, str(e))
            return False

    def print_summary(self):
        """Print test summary"""
        print(f"\n{'='*50}")
        print(f"TEST SUMMARY")
        print(f"{'='*50}")
        print(f"Tests run: {self.tests_run}")
        print(f"Tests passed: {self.tests_passed}")
        print(f"Tests failed: {self.tests_run - self.tests_passed}")
        print(f"Success rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if self.errors:
            print(f"\nFAILED TESTS:")
            for error in self.errors:
                print(f"  - {error}")
        
        return self.tests_passed == self.tests_run

def main():
    print("Starting ApplyMate API Testing...")
    print(f"Timestamp: {datetime.now()}")
    print(f"Testing against: https://application-ready.preview.emergentagent.com/api")
    print("="*50)
    
    tester = ApplyMateAPITester()
    
    # Run tests
    tester.test_api_root()
    tester.test_invalid_file_type()
    tester.test_missing_job_description()
    success, result = tester.test_valid_pdf_upload()
    tester.test_valid_docx_upload()
    
    # Print summary
    all_passed = tester.print_summary()
    
    # Test Claude AI integration quality if we got a successful response
    if success and result:
        print(f"\n{'='*50}")
        print("SAMPLE AI OUTPUT QUALITY CHECK")
        print(f"{'='*50}")
        print("Resume Bullets:")
        for i, bullet in enumerate(result['resume_bullets'][:3], 1):
            print(f"  {i}. {bullet}")
        
        print(f"\nCover Letter Preview:")
        print(f"  {result['cover_letter'][:200]}...")
        
        print(f"\nApplication Email Preview:")
        print(f"  {result['application_email'][:150]}...")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
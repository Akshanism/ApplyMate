ApplyMate

ApplyMate is an AI-powered job application copilot that generates recruiter-ready resume bullets, cover letters, and application emails from a resume and job description.

The product is intentionally minimal and focused on producing clear, professional, ATS-friendly output.


Features
	•	Resume upload (PDF or DOCX)
	•	Job description input
	•	AI-generated:
	•	Resume bullet points
	•	Cover letter
	•	Application email
	•	Clean, responsive UI
	•	Clear validation and error handling


Tech Stack
	•	Frontend: React, Tailwind CSS
	•	Backend: FastAPI (Python)
	•	AI: Anthropic Claude (via Emergent)
	•	Deployment: Vercel (frontend)


Running Locally

Backend:

cd backend
pip install -r requirements.txt
python -m uvicorn server:app –host 0.0.0.0 –port 8000

Health check:

curl http://127.0.0.1:8000/api/


Configuration

Create backend/.env:

CORS_ORIGINS=*
EMERGENT_LLM_KEY=sk-emergent-xxxxxxxx

Environment files are excluded from version control.


Notes
	•	Job descriptions must be at least 50 characters
	•	Only PDF and DOCX resumes are supported
	•	No authentication or payments (MVP)



ApplyMate is built as a focused MVP demonstrating full-stack development, AI integration, and production-ready engineering practices.
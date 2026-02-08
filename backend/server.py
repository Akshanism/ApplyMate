from fastapi import FastAPI, APIRouter, UploadFile, File, Form, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
import os
import logging
from pathlib import Path
from pydantic import BaseModel
from typing import List
import PyPDF2
import docx
import io
from emergentintegrations.llm.chat import LlmChat, UserMessage


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Response Models
class TailorResponse(BaseModel):
    resume_bullets: List[str]
    cover_letter: str
    application_email: str


# Helper Functions
def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract text from PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading PDF: {str(e)}")


def extract_text_from_docx(file_content: bytes) -> str:
    """Extract text from DOCX file"""
    try:
        doc = docx.Document(io.BytesIO(file_content))
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading DOCX: {str(e)}")


async def generate_tailored_content(resume_text: str, job_description: str) -> TailorResponse:
    """Use Claude Sonnet 4.5 to generate tailored application content"""
    
    api_key = os.environ.get('EMERGENT_LLM_KEY')
    if not api_key:
        raise HTTPException(status_code=500, detail="API key not configured")
    
    # Initialize Claude chat
    chat = LlmChat(
        api_key=api_key,
        session_id="applymate-session",
        system_message="""You are a professional recruiter and career advisor.
Your job is to rewrite resumes and cover letters to maximize clarity, relevance, and professionalism.
Prioritize practicality and credibility over creativity.

When generating content:
- Be professional, confident, and natural
- Avoid buzzwords, fluff, exaggeration, and emojis
- Resume bullets must be clear, quantified where possible, and ATS-friendly
- Cover letters must be concise (under one page)
- Maintain consistent tone across all outputs"""
    ).with_model("anthropic", "claude-sonnet-4-5-20250929")
    
    # Create prompt
    prompt = f"""Based on this resume and job description, generate tailored application materials.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Please provide:
1. 5-7 ATS-friendly resume bullet points tailored to this job
2. A professional cover letter (under one page)
3. A short application email

Format your response EXACTLY like this:

RESUME BULLETS:
- [bullet 1]
- [bullet 2]
- [bullet 3]
...

COVER LETTER:
[cover letter text]

APPLICATION EMAIL:
[email text]"""
    
    try:
        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        
        # Parse response
        return parse_ai_response(response)
    except Exception as e:
        logger.error(f"Error calling AI: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")


def parse_ai_response(response: str) -> TailorResponse:
    """Parse AI response into structured format"""
    try:
        # Split response into sections
        resume_section = ""
        cover_letter_section = ""
        email_section = ""
        
        if "RESUME BULLETS:" in response:
            parts = response.split("RESUME BULLETS:", 1)[1]
            if "COVER LETTER:" in parts:
                resume_section, rest = parts.split("COVER LETTER:", 1)
                if "APPLICATION EMAIL:" in rest:
                    cover_letter_section, email_section = rest.split("APPLICATION EMAIL:", 1)
                else:
                    cover_letter_section = rest
        
        # Parse resume bullets
        bullets = []
        for line in resume_section.strip().split("\n"):
            line = line.strip()
            if line and (line.startswith("-") or line.startswith("•")):
                bullets.append(line.lstrip("-•").strip())
        
        # Clean up sections
        cover_letter = cover_letter_section.strip()
        email = email_section.strip()
        
        # Fallback if parsing fails
        if not bullets:
            bullets = ["Unable to generate bullets - please try again"]
        if not cover_letter:
            cover_letter = "Unable to generate cover letter - please try again"
        if not email:
            email = "Unable to generate email - please try again"
        
        return TailorResponse(
            resume_bullets=bullets,
            cover_letter=cover_letter,
            application_email=email
        )
    except Exception as e:
        logger.error(f"Error parsing response: {str(e)}")
        # Return fallback response
        return TailorResponse(
            resume_bullets=["Error parsing AI response"],
            cover_letter="Error parsing AI response",
            application_email="Error parsing AI response"
        )


# Routes
@api_router.get("/")
async def root():
    return {"message": "ApplyMate API"}


@api_router.post("/tailor-application", response_model=TailorResponse)
async def tailor_application(
    resume: UploadFile = File(...),
    job_description: str = Form(...)
):
    """Main endpoint to tailor job application materials"""
    
    # Validate file type
    if not resume.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")
    
    file_extension = resume.filename.lower().split('.')[-1]
    if file_extension not in ['pdf', 'docx']:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and DOCX files are supported"
        )
    
    # Read file content
    file_content = await resume.read()
    
    # Extract text based on file type
    if file_extension == 'pdf':
        resume_text = extract_text_from_pdf(file_content)
    else:  # docx
        resume_text = extract_text_from_docx(file_content)
    
    if not resume_text.strip():
        raise HTTPException(
            status_code=400,
            detail="Could not extract text from resume. Please ensure the file is not empty or corrupted."
        )
    
    # Validate job description
    if not job_description.strip():
        raise HTTPException(status_code=400, detail="Job description is required")
    
    # Generate tailored content
    result = await generate_tailored_content(resume_text, job_description)
    
    return result


# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
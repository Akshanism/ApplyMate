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

# Load env
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

# App
app = FastAPI()
api_router = APIRouter(prefix="/api")

# Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Response model
class TailorResponse(BaseModel):
    resume_bullets: List[str]
    cover_letter: str
    application_email: str

# Helpers
def extract_text_from_pdf(file_content: bytes) -> str:
    try:
        reader = PyPDF2.PdfReader(io.BytesIO(file_content))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"PDF read error: {e}")

def extract_text_from_docx(file_content: bytes) -> str:
    try:
        doc = docx.Document(io.BytesIO(file_content))
        return "\n".join(p.text for p in doc.paragraphs)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"DOCX read error: {e}")

async def generate_tailored_content(resume_text: str, job_description: str) -> TailorResponse:
    api_key = os.getenv("EMERGENT_LLM_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="EMERGENT_LLM_KEY not set")

    chat = (
        LlmChat(
            api_key=api_key,
            session_id="applymate",
            system_message=(
                "You are a professional recruiter. "
                "Generate ATS-friendly resume bullets, a concise cover letter, "
                "and a short application email."
            ),
        )
        .with_model("anthropic", "claude-sonnet-4-5-20250929")
    )

    prompt = f"""
RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Format exactly:

RESUME BULLETS:
- bullet

COVER LETTER:
text

APPLICATION EMAIL:
text
"""

    response = await chat.send_message(UserMessage(text=prompt))
    return parse_ai_response(response)

def parse_ai_response(response: str) -> TailorResponse:
    bullets, cover, email = [], "", ""

    if "RESUME BULLETS:" in response:
        after = response.split("RESUME BULLETS:", 1)[1]
        resume_part, rest = after.split("COVER LETTER:", 1)
        cover_part, email_part = rest.split("APPLICATION EMAIL:", 1)

        bullets = [
            line.lstrip("-• ").strip()
            for line in resume_part.splitlines()
            if line.strip().startswith(("-", "•"))
        ]
        cover = cover_part.strip()
        email = email_part.strip()

    return TailorResponse(
        resume_bullets=bullets or ["Generation failed"],
        cover_letter=cover or "Generation failed",
        application_email=email or "Generation failed",
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
    if not resume.filename:
        raise HTTPException(status_code=400, detail="No resume uploaded")

    ext = resume.filename.lower().split(".")[-1]
    if ext not in {"pdf", "docx"}:
        raise HTTPException(status_code=400, detail="Only PDF or DOCX allowed")

    file_bytes = await resume.read()
    resume_text = (
        extract_text_from_pdf(file_bytes)
        if ext == "pdf"
        else extract_text_from_docx(file_bytes)
    )

    if not resume_text.strip():
        raise HTTPException(status_code=400, detail="Resume text empty")

    clean_jd = job_description.strip()
    if len(clean_jd) < 50:
        raise HTTPException(
            status_code=400,
            detail="Job description must be at least 50 characters",
        )

    return await generate_tailored_content(resume_text, clean_jd)

# Middleware
app.include_router(api_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
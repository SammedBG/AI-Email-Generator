import os
from groq import Groq
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="AI Email Generator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

prompt_history = []


class EmailRequest(BaseModel):
    prompt: str
    tone: str = "Professional"


class EmailResponse(BaseModel):
    subject: str
    body: str


TONE_INSTRUCTIONS = {
    "Professional": "Write in a clear, professional business tone.",
    "Friendly": "Write in a warm, friendly, approachable tone while still being appropriate for email.",
    "Formal": "Write in a very formal, traditional business tone with respectful language.",
    "Casual": "Write in a relaxed, casual tone as if writing to a colleague you know well.",
}


def build_prompt(user_prompt: str, tone: str) -> str:
    tone_instruction = TONE_INSTRUCTIONS.get(tone, TONE_INSTRUCTIONS["Professional"])
    return f"""You are an expert email writer. {tone_instruction}

Write a complete email based on this request: "{user_prompt}"

Format your response EXACTLY like this, with no extra text:
SUBJECT: <subject line here>
BODY:
<email body here>"""


def parse_email_response(text: str) -> EmailResponse:
    subject = "Generated Email"
    body = text.strip()
    if "SUBJECT:" in text and "BODY:" in text:
        try:
            subject = text.split("SUBJECT:")[1].split("BODY:")[0].strip()
            body = text.split("BODY:")[1].strip()
        except IndexError:
            pass
    return EmailResponse(subject=subject, body=body)


@app.get("/")
def root():
    return {"status": "ok", "message": "AI Email Generator API is running"}


@app.get("/health")
def health_check():
    return {"status": "healthy", "groq_configured": GROQ_API_KEY is not None}


@app.post("/generate", response_model=EmailResponse)
def generate_email(request: EmailRequest):
    if not request.prompt or not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")

    if not client:
        raise HTTPException(
            status_code=500,
            detail="GROQ_API_KEY not configured on the server. Please set it in .env",
        )

    full_prompt = build_prompt(request.prompt, request.tone)

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": full_prompt}],
            temperature=0.7,
            max_tokens=500,
        )
        raw_text = completion.choices[0].message.content
        result = parse_email_response(raw_text)

        prompt_history.append(
            {"prompt": request.prompt, "tone": request.tone, "subject": result.subject}
        )
        return result

    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to generate email. LLM API error: {str(e)}")


@app.get("/history")
def get_history():
    return {"history": prompt_history[-20:]}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
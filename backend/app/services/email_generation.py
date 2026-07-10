"""Email generation helpers and provider integration."""

from __future__ import annotations

import re
from datetime import datetime, timezone

from groq import Groq

from app.config import AI_MODEL, AI_PROVIDER, AVAILABLE_MODEL_IDS, GROQ_API_KEY
from app.schemas import EmailRequest, EmailResponse, HistoryItem

TONE_INSTRUCTIONS = {
    "Professional": "Write in a clear, professional business tone.",
    "Friendly": "Write in a warm, friendly, approachable tone while still being appropriate for email.",
    "Formal": "Write in a very formal, traditional business tone with respectful language.",
    "Casual": "Write in a relaxed, casual tone as if writing to a colleague you know well.",
}

client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

from app.database import history_collection, is_mongodb_available

# Per-user history: {username: [HistoryItem dicts]}
user_history: dict[str, list[dict]] = {}


def get_tone(tone: str) -> str:
    return tone if tone in TONE_INSTRUCTIONS else "Professional"


def resolve_model(requested: str | None) -> str:
    """Return the requested model if valid, otherwise the default."""
    if requested and requested in AVAILABLE_MODEL_IDS:
        return requested
    return AI_MODEL


def build_prompt(user_prompt: str, tone: str) -> str:
    tone_instruction = TONE_INSTRUCTIONS.get(get_tone(tone), TONE_INSTRUCTIONS["Professional"])
    return f"""You are an expert email writer. {tone_instruction}

Write a complete email based on this request: "{user_prompt}"

Format your response EXACTLY like this:
SUBJECT: <subject line here>
BODY:
<email body here>

Do not include any other text, explanations, markdown formatting, or bullet points."""


def infer_subject_from_prompt(user_prompt: str) -> str:
    cleaned = re.sub(r"^(write|draft|generate|create)\s+", "", user_prompt.strip(), flags=re.I)
    cleaned = cleaned.strip().strip(".?!")

    if not cleaned:
        return "Generated Email"

    lowered = cleaned.lower()
    if "interview" in lowered:
        return "Follow-Up After the Interview"
    if "leave" in lowered or "time off" in lowered:
        return "Leave Request"
    if "cold outreach" in lowered or "outreach" in lowered:
        return "Introduction and Outreach"
    if "follow-up" in lowered or "follow up" in lowered:
        return "Follow-Up Email"

    words = cleaned.split()
    headline = " ".join(words[:6])
    return headline[:1].upper() + headline[1:]


def parse_email_response(text: str) -> tuple[str, str]:
    subject = "Generated Email"
    body = text.strip()

    subject_match = re.search(r"(?im)^\s*subject\s*:\s*(.+)$", text)
    body_match = re.search(r"(?ims)^\s*body\s*:\s*(.*)$", text)

    if subject_match:
        subject = subject_match.group(1).strip()

    if body_match:
        body = body_match.group(1).strip()

    body = re.sub(r"^\s*(subject|body)\s*:\s*", "", body, flags=re.I).strip()

    if not subject or subject == "Generated Email":
        subject = infer_subject_from_prompt(body if body else text)

    return subject, body


def resolve_provider() -> str:
    if AI_PROVIDER == "mock":
        return "mock"

    if AI_PROVIDER == "groq" and client:
        return "groq"

    return "mock"


def compose_fallback_email(request: EmailRequest, model: str) -> EmailResponse:
    tone = get_tone(request.tone)
    subject = infer_subject_from_prompt(request.prompt)

    tone_openers = {
        "Professional": "I hope this message finds you well.",
        "Friendly": "I hope you're having a great day.",
        "Formal": "I trust you are well.",
        "Casual": "Hope you're doing well.",
    }
    tone_closers = {
        "Professional": "Best regards,",
        "Friendly": "Warm regards,",
        "Formal": "Sincerely,",
        "Casual": "Thanks,",
    }

    body = (
        f"{tone_openers[tone]}\n\n"
        f"I am writing to help with your request: {request.prompt.strip()}.\n\n"
        "Here is a polished email draft you can adapt and send:\n\n"
        "[Paste the final email content here or personalize the details as needed.]\n\n"
        f"{tone_closers[tone]}\n[Your Name]"
    )

    return EmailResponse(
        subject=subject,
        body=body,
        provider="mock",
        model="template-fallback",
    )


def build_response(subject: str, body: str, provider: str, model: str) -> EmailResponse:
    return EmailResponse(
        subject=subject,
        body=body,
        provider=provider,
        model=model if provider == "groq" else "template-fallback",
    )


async def append_history(response: EmailResponse, request: EmailRequest, username: str) -> None:
    item = HistoryItem(
        prompt=request.prompt.strip(),
        tone=get_tone(request.tone),
        subject=response.subject,
        provider=response.provider,
        model=response.model,
        created_at=datetime.now(timezone.utc).isoformat(),
    ).model_dump()

    if await is_mongodb_available():
        item["username"] = username.lower()
        await history_collection.insert_one(item)
    else:
        if username not in user_history:
            user_history[username] = []
        user_history[username].append(item)


async def get_history(username: str) -> list[dict]:
    if await is_mongodb_available():
        cursor = history_collection.find({"username": username.lower()}).sort("created_at", -1).limit(20)
        items = await cursor.to_list(length=20)
        # Reverse to return chronological order (oldest to newest)
        items.reverse()
        # MongoDB documents contain _id which is ObjectId (not serializable to JSON), we remove it or convert to string.
        for item in items:
            if "_id" in item:
                item["_id"] = str(item["_id"])
        return items
    return user_history.get(username, [])[-20:]


async def generate_email(request: EmailRequest, username: str) -> EmailResponse:
    provider = resolve_provider()
    model = resolve_model(request.model)
    full_prompt = build_prompt(request.prompt, request.tone)

    if provider != "groq":
        response = compose_fallback_email(request, model)
        await append_history(response, request, username)
        return response

    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": full_prompt}],
            temperature=0.7,
            max_tokens=500,
        )
        raw_text = completion.choices[0].message.content or ""
        subject, body = parse_email_response(raw_text)
        response = build_response(subject, body, provider, model)
        await append_history(response, request, username)
        return response
    except Exception:
        response = compose_fallback_email(request, model)
        await append_history(response, request, username)
        return response


def generate_stream_text(request: EmailRequest):
    provider = resolve_provider()
    model = resolve_model(request.model)

    if provider != "groq":
        fallback = compose_fallback_email(request, model)
        for token in fallback.body.split():
            yield token + " "
        return

    full_prompt = build_prompt(request.prompt, request.tone)

    try:
        stream = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": full_prompt}],
            temperature=0.7,
            max_tokens=500,
            stream=True,
        )
        for chunk in stream:
            token = chunk.choices[0].delta.content
            if token:
                yield token
    except Exception as error:
        yield f"\n[Error: {error}]"

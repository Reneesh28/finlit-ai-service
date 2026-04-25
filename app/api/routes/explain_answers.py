from fastapi import APIRouter, Request
import os
from groq import Groq
import json
import re

router = APIRouter()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def extract_json(text):
    text = text.replace("```json", "").replace("```", "").strip()
    match = re.search(r"\[.*\]", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except:
            return []
    return []


@router.post("/explain-answers")
async def explain_answers(request: Request):
    try:
        body = await request.json()
        questions = body.get("questions", [])

        if not questions:
            return {"success": False, "message": "No questions provided"}

        prompt = f"""
You are a financial literacy tutor.

Explain the correct answers for these questions:

{questions}

Rules:
- Keep explanation short (2–3 lines)
- Simple and clear
- Educational tone

Return ONLY JSON:

[
  {{
    "question": "...",
    "correctAnswer": "...",
    "explanation": "..."
  }}
]
"""

        response = client.chat.completions.create(
            model=os.getenv("GROQ_MODEL"),
            messages=[
                {"role": "system", "content": "Return JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5
        )

        raw = response.choices[0].message.content
        parsed = extract_json(raw)

        return {
            "success": True,
            "data": parsed
        }

    except Exception as e:
        return {
            "success": False,
            "message": "Error generating explanations",
            "error": str(e)
        }
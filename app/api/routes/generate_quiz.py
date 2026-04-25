from fastapi import APIRouter, Request
import requests
import os
import json
import re
from groq import Groq

router = APIRouter()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:5000")
INTERNAL_API_KEY = os.getenv("INTERNAL_API_KEY")

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# ================= SAFE JSON EXTRACTION =================
def extract_json(text):
    text = text.strip()

    # remove markdown formatting if present
    text = text.replace("```json", "").replace("```", "")

    try:
        return json.loads(text)
    except:
        pass

    match = re.search(r"\[.*\]", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except:
            return []

    return []


# ================= VALIDATION =================
def validate_questions(questions, expected_count):
    valid = []

    for q in questions:
        if not isinstance(q, dict):
            continue

        question = q.get("question")
        options = q.get("options")
        correct = q.get("correctAnswer")

        if (
            isinstance(question, str) and
            isinstance(options, list) and
            len(options) == 4 and
            isinstance(correct, str) and
            correct in options
        ):
            valid.append({
                "question": question.strip(),
                "options": options,
                "correctAnswer": correct,
                "difficulty": q.get("difficulty", "easy"),
                "category": q.get("category", "general")
            })

    return valid[:expected_count]


# ================= MAIN ROUTE =================
@router.post("/generate-quiz")
async def generate_quiz(request: Request):
    try:
        body = await request.json()
        token = body.get("token")

        if not token:
            return {"success": False, "message": "Auth token required"}

        # 🔐 STEP 1 — FETCH ANALYTICS
        analytics_res = requests.get(
            f"{BACKEND_URL}/api/quiz/analytics",
            headers={"Authorization": f"Bearer {token}"}
        )

        if analytics_res.status_code != 200:
            return {"success": False, "message": "Failed to fetch analytics"}

        analytics = analytics_res.json()["data"]

        difficulty = analytics.get("suggestedDifficulty", "easy")
        distribution = analytics.get("categoryDistribution", [])
        mode = analytics.get("mode", "normal")  # ✅ NEW

        if not distribution:
            return {"success": False, "message": "No category distribution found"}

        total_questions = len(distribution)

        # ================= 🎯 CHALLENGE MODE PROMPT =================
        extra_rules = ""

        if mode == "challenge":
            extra_rules = """
CHALLENGE MODE RULES:
- Questions must be HARD
- Use real-life financial scenarios
- Include tricky/confusing options
- Avoid obvious answers
- Test deep understanding, not definitions
"""

        prompt = f"""
You are a financial literacy expert.

Generate {total_questions} multiple-choice questions.

Difficulty: {difficulty}
Mode: {mode}

{extra_rules}

Distribute questions across these categories:
{distribution}

Requirements:
- Each question must belong to one of the categories
- Exactly 4 options per question
- correctAnswer must match one option
- Questions must be practical and clear

Return ONLY a valid JSON array (no explanation).
"""

        # ================= 🔁 RETRY MECHANISM =================
        MAX_RETRIES = 3
        validated = []
        raw_output = ""

        for attempt in range(MAX_RETRIES):
            response = client.chat.completions.create(
                model=os.getenv("GROQ_MODEL"),
                messages=[
                    {"role": "system", "content": "Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )

            raw_output = response.choices[0].message.content
            parsed = extract_json(raw_output)
            validated = validate_questions(parsed, total_questions)

            if len(validated) == total_questions:
                break

        # ================= ❌ FAIL-SAFE =================
        if len(validated) < total_questions:
            return {
                "success": False,
                "fallback": True,
                "message": "AI failed to generate sufficient valid questions after retries",
                "received": len(validated),
                "expected": total_questions
            }

        # ================= 💾 SAVE TO BACKEND =================
        save_res = requests.post(
            f"{BACKEND_URL}/api/quiz/generate",
            headers={
                "x-api-key": INTERNAL_API_KEY,
                "Content-Type": "application/json"
            },
            json={"questions": validated}
        )

        if save_res.status_code != 201:
            return {
                "success": False,
                "message": "Failed to store questions",
                "backend_error": save_res.text
            }

        return {
            "success": True,
            "questions_generated": len(validated),
            "difficulty": difficulty,
            "mode": mode,  # ✅ NEW
            "distribution_used": distribution
        }

    except Exception as e:
        return {
            "success": False,
            "message": "Server error",
            "error": str(e)
        }
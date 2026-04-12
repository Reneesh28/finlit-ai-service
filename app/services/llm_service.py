from groq import Groq
from app.core.config import GROQ_API_KEY, GROQ_MODEL

client = Groq(api_key=GROQ_API_KEY)

def generate_response(user_message: str):
    try:
        completion = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a financial advisor. Give clear, practical, and beginner-friendly advice."
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            temperature=0.7,
            max_tokens=200
        )

        return completion.choices[0].message.content.strip()

    except Exception as e:
        print("AI ERROR:", str(e))
        return f"AI service error: {str(e)}"
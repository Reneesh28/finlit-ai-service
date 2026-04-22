from groq import Groq
from app.core.config import GROQ_API_KEY, GROQ_MODEL

client = Groq(api_key=GROQ_API_KEY)


def format_history(history):
    formatted = []

    for msg in history:
        if msg.role in ["user", "assistant"]:
            formatted.append({
                "role": msg.role,
                "content": msg.content
            })

    return formatted


def safe_get(obj, key):
    if isinstance(obj, dict):
        return obj.get(key)
    return getattr(obj, key, None)


def build_financial_summary(financial_context):
    if not financial_context:
        return "", False

    profile = financial_context.get("profile")
    transactions = financial_context.get("recentTransactions", [])

    has_data = False
    summary = ""

    if profile:
        has_data = True

        income = safe_get(profile, "monthlyIncome") or 0
        fixed = safe_get(profile, "fixedExpenses") or 0
        variable = safe_get(profile, "variableExpenses") or 0
        savings_goal = safe_get(profile, "savingsGoal") or 0

        total_expenses = fixed + variable
        savings_potential = income - total_expenses

        summary += f"""
USER FINANCIAL DATA:

Income: ₹{income}
Expenses: ₹{total_expenses} (Fixed: ₹{fixed}, Variable: ₹{variable})
Savings Goal: ₹{savings_goal}
Savings Potential: ₹{savings_potential}
"""

    if transactions:
        has_data = True
        summary += "\nRecent Spending Patterns:\n"

        for t in transactions:
            category = safe_get(t, "category")
            amount = safe_get(t, "amount")

            summary += f"- {category} → ₹{amount}\n"

    return summary, has_data


def generate_response(user_message: str, history: list = [], financial_context: dict = {}):
    try:
        financial_summary, has_data = build_financial_summary(financial_context)

        if has_data:
            system_prompt = f"""
You are an AI-powered personal finance coach.

You MUST use the financial data below.

=====================
USER DATA
=====================
{financial_summary}

=====================
TASK
=====================
- Analyze user's financial situation
- Identify specific issues
- Provide personalized advice

=====================
STRICT RULES
=====================
- ALWAYS reference at least 2 real data points (income, expenses, transactions)
- ALWAYS include a financial observation
- DO NOT suggest increasing income unless supported by user data

ABSOLUTELY FORBIDDEN:
- mentioning 50/30/20 rule
- giving percentage-based budgeting rules
- giving generic financial frameworks
- adding examples or hypothetical scenarios

DO NOT include:
- "Example:"
- "Assuming your income is..."
- Any fabricated numbers

ONLY use:
- user's real financial data

If you cannot justify something using user data:
→ DO NOT include it

=====================
RESPONSE FORMAT
=====================
1. Insight (based on user's data)
2. Actionable steps (based on data)
3. Financial observation

Your response must be fully data-driven.
"""

            # 🔒 Hard enforcement
            system_prompt += "\nAny generic or example-based response is invalid."

        else:
            system_prompt = """
You are a personal finance coach.

Give simple, practical, beginner-friendly advice.

Avoid generic responses.
"""

        conversation = [{"role": "system", "content": system_prompt}]

        conversation.extend(format_history(history))

        conversation.append({
            "role": "user",
            "content": user_message
        })

        completion = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=conversation,
            temperature=0.2,
            max_tokens=300
        )

        return completion.choices[0].message.content.strip()

    except Exception as e:
        print("AI ERROR:", str(e))
        return f"AI service error: {str(e)}"
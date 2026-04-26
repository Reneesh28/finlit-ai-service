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
DATA:

Income: {income}
Expenses: {total_expenses} (Fixed: {fixed}, Variable: {variable})
Savings Goal: {savings_goal}
Savings Potential: {savings_potential}
"""

    if transactions:
        has_data = True
        summary += "\nRecent Spending Patterns:\n"

        for t in transactions:
            category = safe_get(t, "category")
            amount = safe_get(t, "amount")

            summary += f"- {category} -> {amount}\n"

    return summary, has_data


def generate_response(user_message: str, history: list = [], financial_context: dict = {}):
    try:
        financial_summary, has_data = build_financial_summary(financial_context)

        if has_data:
            system_prompt = f"""
You are a Budgeting Assistant. 

Your task is to analyze the spending data provided below and offer observations and practical budgeting suggestions.

=====================
DATA PROVIDED
=====================
{financial_summary}

=====================
ANALYSIS STEPS
=====================
1. Spending Review: Look at the income and expense numbers.
2. Observation: Note any trends in the spending categories.
3. Suggestions: Offer 3 practical ideas to help manage the budget better.

=====================
GUIDELINES
=====================
- Use the numbers provided in the data.
- Offer practical ideas for managing expenses.
- Keep the tone helpful and neutral.
"""
        else:
            system_prompt = """
You are a Budgeting Assistant. 

Help the user understand general budgeting principles and offer practical spending management suggestions.
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
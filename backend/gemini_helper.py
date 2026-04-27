import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_ai_explanation(problem_text: str, pattern: str, complexity: dict) -> str:
    prompt = f"""
You are an expert DSA coding interview coach helping a student prepare for Amazon SDE interviews.

Problem Statement:
{problem_text}

Detected Pattern: {pattern}
Time Complexity: {complexity['time']}
Space Complexity: {complexity['space']}

Give a concise response in this exact format:

APPROACH:
(2-3 lines explaining the optimal approach)

PSEUDOCODE:
(clean step-by-step pseudocode)

KEY INSIGHT:
(one line — the "aha moment" for this problem)

SIMILAR LEETCODE PROBLEMS:
(3 problem names)
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Groq error: {str(e)}"

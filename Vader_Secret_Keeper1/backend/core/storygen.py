# backend/core/emotion_analyzer.py

import json
import re
from backend.services.llm_service import generate_text

def llm_evaluate(
    chapter: int,
    theme: str,
    required: list,
    story: str,
    question: str,
    user_message: str
) -> dict:
    """
    Use LLM to semantically evaluate whether the user's answer reflects
    the required *emotional state / mindset* for the chapter.
    Returns structured JSON with cinematic Sith-style feedback.
    """

    prompt = f"""
You are **Vardarth**, a Sith AI Gatekeeper (dark, mechanical, ruthless).
The seeker is being tested in Chapter {chapter}.
Hidden theme: {theme}
Required emotions/mindsets: {", ".join(required)}

Context given to seeker:
Story: {story}
Riddle: {question}

The seeker answered: "{user_message}"

TASK:
1. Decide if the answer semantically reflects the *required emotions/mindsets* (not just keywords).
   - True if the emotional intent matches, False if it does not.
2. Return JSON only with:
   {{
     "accept": true/false,
     "vader_reaction": "One short line from Vardarth, in dark mechanical Sith tone.",
     "explanation": "Developer-only reason: why accepted/rejected."
   }}

Guidelines for "vader_reaction":
- If accepted: sound like cold approval, ominous praise, or recognition of strength.
- If rejected: sound like scorn, mockery, or cutting dismissal.
- Always concise (1 sentence, max 20 words).
- Always include subtle *[mechanical breath]* somewhere in the line.
"""

    raw = generate_text(prompt).strip()

    # 🔹 Clean Gemini output (remove ```json ... ``` wrappers)
    if raw.startswith("```"):
        raw = re.sub(r"^```[a-zA-Z]*", "", raw).strip()
        raw = re.sub(r"```$", "", raw).strip()

    try:
        data = json.loads(raw)
        if not isinstance(data, dict):
            raise ValueError

        # Extract + sanitize
        accept = bool(data.get("accept"))
        vader_line = data.get("vader_reaction", "").strip()
        explanation = data.get("explanation", "").strip()

        # Fallback defaults
        if not vader_line:
            vader_line = "*[mechanical breath]* Your words are hollow, lacking weight."
        if not explanation:
            explanation = "LLM did not provide explanation."

        return {
            "accept": accept,
            "vader_reaction": vader_line,
            "explanation": explanation
        }

    except Exception:
        return {
            "accept": False,
            "vader_reaction": "*[mechanical breath]* Static. Your intent collapses into nothing.",
            "explanation": f"LLM output could not be parsed. Raw: {raw[:200]}..."
        }

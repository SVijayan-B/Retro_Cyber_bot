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
=======
import re
import json
from typing import List, Dict, Any, Tuple
from backend.services.llm_service import generate_text

# Synonyms map (for heuristic matching)
_EMOTION_SYNONYMS: Dict[str, List[str]] = {
    "curiosity": ["curiosity","curious","seek","seeking","discover","investigate","explore","inquiry","inquisitive"],
    "anger": ["anger","angry","fury","rage","wrath","vengeance","rageful","resentment"],
    "dominance": ["dominance","dominate","power","control","rule","conquer"],
    "realisation": ["realisation","realize","realise","understand","awaken","awareness"],
    "peace": ["peace","calm","accept","balance","serenity","tranquil"],
    "balance": ["balance","balanced","harmony"],
}

def _normalize(text: str) -> str:
    return (text or "").lower()

def keyword_match(required: List[str], text: str) -> Tuple[bool, List[str]]:
    """
    For each required base-key, ensure at least one synonym is present.
    Returns (all_found, matched_keys)
    """
    tl = _normalize(text)
    matched = []
    for key in required:
        syns = _EMOTION_SYNONYMS.get(key, [key])
        found = False
        for s in syns:
            if re.search(r"\b" + re.escape(s) + r"\b", tl):
                found = True
                matched.append(key)
                break
        if not found:
            return False, matched
    return True, matched

def llm_evaluate(
    chapter: int, 
    theme_name: str, 
    required: List[str], 
    story: str, 
    question: str, 
    user_answer: str
) -> Dict[str, Any]:
    """
    Ask the LLM to evaluate whether user_answer expresses the required themes/emotions.
    On parse failure, return fallback heuristic.
    """
    prompt = f"""
You are Vardarth, an intimidating Sith gatekeeper who judges a seeker.
Task: Decide if the user's answer expresses the required themes.

Return ONLY a JSON object with these fields:
- "accept": true or false
- "matched": an array of base keys that match (use: curiosity, anger, dominance, realisation, peace, balance)
- "explanation": one short sentence explaining why you accepted or rejected
- "vader_reaction": a single vivid emotional line Vardarth would speak (short, in voice)

Context:
Chapter: {chapter}
Theme: {theme_name}
Required keys: {required}
Story (context): \"\"\"{story}\"\"\"  
Question: \"{question}\"  
User answer: \"{user_answer}\"  

Be strict but fair. Output JSON only.
"""
    raw = generate_text(prompt)

    # try to extract JSON substring safely
    try:
        first = raw.find("{")
        last = raw.rfind("}")
        if first != -1 and last != -1 and last > first:
            js = raw[first:last+1]
            data = json.loads(js)
            return {
                "accept": bool(data.get("accept")),
                "matched": data.get("matched") or [],
                "explanation": data.get("explanation","").strip(),
                "vader_reaction": data.get("vader_reaction","").strip(),
                "raw": raw
            }
    except Exception:
        pass

    # fallback heuristic
    ok, matched = keyword_match(required, user_answer)
    vader_reaction = "Your words are...thin. Find sharper hunger." if not ok else "Yes. The flame is true."
    explanation = "Matched by keywords: " + ", ".join(matched) if matched else "No required keywords found."
    return {
        "accept": ok,
        "matched": matched,
        "explanation": explanation,
        "vader_reaction": vader_reaction,
        "raw": raw
    }


# backend/core/emotion_analyzer.py
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

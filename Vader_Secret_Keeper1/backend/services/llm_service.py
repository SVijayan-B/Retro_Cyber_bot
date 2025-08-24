# backend/services/llm_service.py


import os
import re

import os

from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()  # reads .env in project root

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

if not API_KEY:


    # fallback: raise so you immediately know

    raise RuntimeError("GEMINI_API_KEY not found in environment. Add to .env or export it.")

genai.configure(api_key=API_KEY)



def _clean_markdown_fences(text: str) -> str:
    """
    Removes Markdown-style fences (```json, ```text, ``` etc.) from LLM output.
    Ensures clean raw text/JSON is returned.
    """
    if not text:
        return text
    # remove opening fences like ```json or ```text
    text = re.sub(r"^```[a-zA-Z0-9]*\s*", "", text.strip())
    # remove trailing ```
    text = re.sub(r"```$", "", text.strip())
    return text.strip()


def generate_text(prompt: str, temperature: float = 0.2, max_output_tokens: int = 512) -> str:
    """
    Call Gemini and return generated text, cleaned of markdown wrappers.

def generate_text(prompt: str, temperature: float = 0.2, max_output_tokens: int = 512) -> str:
    """
    Call Gemini and return generated text. This wrapper handles a couple of response shapes.

    """
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        resp = model.generate_content(prompt)


        # common SDK shapes: resp.text
        if hasattr(resp, "text") and resp.text:
            return _clean_markdown_fences(resp.text)

        # fallback for dict-like responses
        if isinstance(resp, dict):
            candidates = resp.get("candidates") or resp.get("outputs")
            if isinstance(candidates, list) and candidates:
                candidate = candidates[0]
                if isinstance(candidate, dict):
                    for k in ("content", "output", "text"):
                        if k in candidate:
                            return _clean_markdown_fences(candidate[k])
                return _clean_markdown_fences(str(candidate))

        return _clean_markdown_fences(str(resp))

    except Exception as e:

        # common SDK shapes: resp.text
        if hasattr(resp, "text") and resp.text:
            return resp.text.strip()
        # fallback for dict-like responses
        if isinstance(resp, dict):
            # try to extract candidate text
            candidates = resp.get("candidates") or resp.get("outputs")
            if isinstance(candidates, list) and candidates:
                candidate = candidates[0]
                # candidate may be string or dict
                if isinstance(candidate, dict):
                    for k in ("content", "output", "text"):
                        if k in candidate:
                            return candidate[k].strip()
                return str(candidate).strip()
        return str(resp)
    except Exception as e:
        # return an explicit sentinel so caller can handle it

        return f"[LLM_ERROR] {repr(e)}"

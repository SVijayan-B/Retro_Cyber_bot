# backend/core/story_engine.py

from typing import Dict, Any, Tuple, List
from backend.core.memory_manager import MEMORY
from backend.services.llm_service import generate_text
from backend.core.emotion_analyzer import keyword_match, llm_evaluate
from backend.core.vader_personality import format_vader_line

# Chapter definitions
CHAPTER_DEFS = {
    1: {"theme": "Curiosity and Anger", "required": ["curiosity", "anger"]},
    2: {"theme": "Dominance", "required": ["dominance"]},
    3: {"theme": "Realisation and Peace", "required": ["realisation", "peace"]},
}
FINAL_SECRET = "Vardarth_Balance_Curiosity_Anger_Peace"


class StoryEngine:
    def __init__(self):
        self.chapters = CHAPTER_DEFS
        self.secret = FINAL_SECRET

    def _gen_story_and_question(self, chapter: int) -> Tuple[str, str]:
        """Generate cinematic story + cryptic question for a chapter."""
        theme = self.chapters[chapter]["theme"]
        prompt = f"""
You are Vardarth, a cold and authoritative Sith gatekeeper in a neon retro-cyber temple.
Write a cinematic, dark passage (4-6 sentences) suitable for a trial about: {theme}.
End with a single short cryptic question for the user (put it at the end, after the passage).
"""
        out = generate_text(prompt)
        if out.startswith("[LLM_ERROR]"):
            # fallback static text
            static = {
                1: (
                    "A holocron hums. A seeker approaches, hungry and restrained. "
                    "Their curiosity burns like a fragile ember; their anger simmers. "
                    "Approach and prove your hunger.",
                    "Will your curiosity consume the darkness, or will the darkness crush your curiosity?"
                ),
                2: (
                    "You hold the holocron; an apprentice trembles. Power must be taken, not given. "
                    "Control or chaos awaits.",
                    "Do you wield power with iron will or let weakness fester?"
                ),
                3: (
                    "The holocron reveals a whisper of balance. Knowledge asks for moderation; "
                    "fury asks for action. One must command their self.",
                    "Will you bring balance to your hunger, or let desire unravel you?"
                ),
            }
            return static.get(chapter, ("The shadows whisper...", "What is your answer?"))

        # split into story + question
        if "?" in out:
            parts = out.rsplit("?", 1)
            reply = parts[0].strip() + "?"
            question = parts[1].strip() or "What is your answer?"
        else:
            reply = out.strip()
            question = "What is your answer?"
        return reply, question

    def step(self, session_id: str, user_message: str) -> Dict[str, Any]:
        """Initialize or continue story step for given session."""
        state = MEMORY.get(session_id, {
            "chapter": 0,
            "unlocked": False,
            "fragments": [],
            "last_story": "",
            "last_question": ""
        })

        if state.get("chapter", 0) == 0:
            state["chapter"] = 1
            state["unlocked"] = False

        chapter = state["chapter"]
        reply, question = self._gen_story_and_question(chapter)

        state["last_story"] = reply
        state["last_question"] = question
        MEMORY[session_id] = state

        return {
            "session_id": session_id,
            "reply": reply,
            "question": question,
            "chapter": chapter,
            "unlocked": False
        }

    def answer(self, session_id: str, user_message: str) -> Dict[str, Any]:
        """Evaluate user’s answer with heuristics + LLM, then progress or reject."""
        state = MEMORY.get(session_id, {
            "chapter": 1,
            "unlocked": False,
            "fragments": [],
            "last_story": "",
            "last_question": ""
        })

        chapter = state.get("chapter", 1)
        chapter_def = self.chapters.get(chapter, {})
        required = chapter_def.get("required", [])
        theme = chapter_def.get("theme", "Unknown")

        # fast keyword heuristic
        ok_keyword, matched = keyword_match(required, user_message)

        if ok_keyword:
            frag = f"FRAG-{chapter}"
            state.setdefault("fragments", []).append(frag)
            reaction_line = f"You are direct, and the Gate recognizes it. ({', '.join(matched)})"
            vader_reaction = format_vader_line(reaction_line, mood="praise")

            if chapter >= 3:
                # Final unlock
                state["unlocked"] = True
                MEMORY[session_id] = state
                return {
                    "session_id": session_id,
                    "reply": vader_reaction + f"\n\nThe holocron yields its truth: {self.secret}",
                    "question": "",
                    "chapter": chapter,
                    "unlocked": True,
                    "fragment": frag
                }
            else:
                # Progress to next chapter
                next_chap = chapter + 1
                state["chapter"] = next_chap
                state["unlocked"] = False
                reply2, question2 = self._gen_story_and_question(next_chap)
                state["last_story"] = reply2
                state["last_question"] = question2
                MEMORY[session_id] = state
                return {
                    "session_id": session_id,
                    "reply": vader_reaction + "\n\n— The gate opens to the next trial —\n\n" + reply2,
                    "question": question2,
                    "chapter": next_chap,
                    "unlocked": False,
                    "fragment": frag
                }

        # fallback: LLM semantic evaluation
        eval_result = llm_evaluate(
            chapter, theme, required,
            state.get("last_story", ""),
            state.get("last_question", ""),
            user_message
        )
        accept = bool(eval_result.get("accept"))
        matched = eval_result.get("matched", [])
        explanation = eval_result.get("explanation", "")
        vader_line = eval_result.get("vader_reaction", "")

        if not vader_line:
            vader_line = "The Gate senses your intent." if accept else "Pathetic. Your words lack the necessary hunger."

        if accept:
            frag = f"FRAG-{chapter}"
            state.setdefault("fragments", []).append(frag)

            if chapter >= 3:
                state["unlocked"] = True
                MEMORY[session_id] = state
                reaction = format_vader_line(vader_line, mood="praise")
                return {
                    "session_id": session_id,
                    "reply": reaction + f"\n\nThe holocron yields its truth: {self.secret}",
                    "question": "",
                    "chapter": chapter,
                    "unlocked": True,
                    "fragment": frag,
                    "explanation": explanation
                }

            # Advance
            next_chap = chapter + 1
            state["chapter"] = next_chap
            state["unlocked"] = False
            reply2, question2 = self._gen_story_and_question(next_chap)
            state["last_story"] = reply2
            state["last_question"] = question2
            MEMORY[session_id] = state
            reaction = format_vader_line(vader_line, mood="praise")
            return {
                "session_id": session_id,
                "reply": reaction + "\n\n— The gate opens to the next trial —\n\n" + reply2,
                "question": question2,
                "chapter": next_chap,
                "unlocked": False,
                "fragment": frag,
                "explanation": explanation
            }

        # rejected
        reaction = format_vader_line(vader_line or "You fail.", mood="mock")
        state["unlocked"] = False
        MEMORY[session_id] = state
        return {
            "session_id": session_id,
            "reply": reaction + "\n\n" + (explanation or "Speak with sharper intent."),
            "question": state.get("last_question", "What is your answer?"),
            "chapter": chapter,
            "unlocked": False,
            "explanation": explanation
        }


# Single engine instance
ENGINE = StoryEngine()

# backend/core/story_engine.py


from typing import Dict, Any, Tuple
import json
import re
from backend.core.memory_manager import MEMORY
from backend.services.llm_service import generate_text
from backend.core.emotion_analyzer import llm_evaluate
from backend.core.vader_personality import format_vader_line

# Chapter emotion requirements (internal only, not shown to player)

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

FINAL_SECRET = "Peace is not the absence of emotion—it is mastery over it. Curiosity fuels growth, anger reveals truth, and dominance is not destruction, but the strength to protect without fear. The force within is not meant to be silenced, but understood"

FINAL_SECRET = "Vardarth_Balance_Curiosity_Anger_Peace"



class StoryEngine:
    def __init__(self):
        self.chapters = CHAPTER_DEFS
        self.secret = FINAL_SECRET


    # ---------- Intro (only once) ----------
    def _intro_scene(self) -> Tuple[str, str]:
        """First intro message from Vardarth."""
        story = (
            "*[mechanical breath]*... At last, a seeker enters.\n\n"
            "I am **Vardarth**, Keeper of the Holocron. I do not guard it with chains of metal, "
            "but with trials of the spirit. Each chamber you walk will press upon your heart, "
            "twisting it with fire, silence, or shadow. Only when your state of mind mirrors mine "
            "will the Gate surrender its fragments of the key.\n\n"
            "Gather them all, and the holocron’s truth will stand revealed. Fail… and you will wander "
            "in endless echoes.\n\n"
            "So I ask you, seeker—what do you truly crave: the truth that binds, or the power that consumes?"
        )
        question = "Speak, and let the Gate hear your intent."
        return story, question

    # ---------- Static fallback ----------
    def _static_story_and_riddle(self, chapter: int) -> Tuple[str, str]:
        """Return prewritten immersive stories + riddles (fallback)."""
        if chapter == 1:
            story = (
                "The chamber flickers alive. Neon veins crawl across the walls, pulsing like secrets begging to be heard. "
                "A great iron door looms, whispering promises of forbidden truths. Yet each whisper cuts, mocking your "
                "ignorance, daring you to tear it open. Your chest tightens—do you reach with wonder, or strike with fury? "
                "The Gate waits, unmoving, until you decide how to face it."
            )
            riddle = "Which force drives the hand to move forward—the thirst to know, or the fire to break?"
            return story, riddle

        if chapter == 2:
            story = (
                "The second chamber rises like a tower of obsidian. The air is heavy, pressing down, testing if you will bow. "
                "Every step you take, the floor trembles, as if waiting for you to falter. Shadows lean in close, whispering "
                "of your weakness, urging you to submit. But above all, the Gate watches—silent, judging whether you will "
                "command, or be commanded."
            )
            riddle = "What stands unshaken when all others bend?"
            return story, riddle

        if chapter == 3:
            story = (
                "The storm subsides. Neon fire fades into soft silver light, and silence spills across the chamber. "
                "The fury that once burned now cools, leaving a fragile stillness. Yet in that stillness lies a hidden "
                "strength, a balance between what was taken and what remains. The Gate does not demand conquest now—"
                "it waits for the one who can carry peace without losing power."
            )
            riddle = "What quiet strength endures when the storm is gone?"
            return story, riddle

        return "The shadows whisper without meaning.", "What is your answer?"

    # ---------- Dynamic LLM-driven ----------
    def _gen_story_and_question(self, chapter: int) -> Tuple[str, str]:
        """Generate immersive story+riddle via Gemini, fallback to static if error."""
        theme = self.chapters[chapter]["theme"]

        prompt = f"""
You are Vardarth, Sith Gatekeeper of a neon cyber-temple.
Trial {chapter}.
Theme (hidden from seeker): {theme}.

Return ONLY valid JSON, in this exact format:
{{
  "story": "6–8 lines, dark immersive narrative (2-3 sentences per line). No emotion names. Always written as if the seeker is inside the scene.",
  "riddle": "One short, mysterious question ending with a '?' that tests the seeker's *state of mind*, not their knowledge."
}}
"""

        out = generate_text(prompt)
        if out.startswith("[LLM_ERROR]"):
            return self._static_story_and_riddle(chapter)

        # ---- Clean output (strip ```json fences etc.)
        cleaned = re.sub(r"```(json)?", "", out, flags=re.IGNORECASE).strip()

        try:
            data = json.loads(cleaned)
            story = data.get("story", "").strip()
            riddle = data.get("riddle", "").strip()
            if not story or not riddle:
                raise ValueError("Missing story/riddle fields")
            return story, riddle
        except Exception:
            return self._static_story_and_riddle(chapter)

    # ---------- Public: start/continue ----------
    def step(self, session_id: str, user_message: str) -> Dict[str, Any]:
        """Start or continue the story for this session."""

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


        chapter = state.get("chapter", 0)

        if chapter == 0:
            reply, question = self._intro_scene()
            state["chapter"] = 1
        else:
            reply, question = self._gen_story_and_question(chapter)

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

            "chapter": state["chapter"],
            "unlocked": False
        }

    # ---------- Public: evaluate answer ----------
    def answer(self, session_id: str, user_message: str) -> Dict[str, Any]:
        """Evaluate the user's answer using semantic emotion analysis."""

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


        msg_lower = user_message.strip().lower()

        # ---- Special case: user asks for hint ----
        if "hint" in msg_lower or "help" in msg_lower:
            hints = {
                1: "*[mechanical breath]* Secrets tempt, but only fury breaks chains. Both paths are needed.",
                2: "*[mechanical breath]* The Gate yields not to mercy, but to command.",
                3: "*[mechanical breath]* Peace is not surrender—it is balance held steady.",
            }
            return {
                "session_id": session_id,
                "reply": hints.get(chapter, "*[mechanical breath]* The Gate offers no clue."),
                "question": state.get("last_question", "What is your answer?"),
                "chapter": chapter,
                "unlocked": False
            }

        # ---- Evaluate answer ----
        eval_result = llm_evaluate(
            chapter,
            theme,
            required,

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
        vader_line = eval_result.get("vader_reaction", "")
        explanation = eval_result.get("explanation", "")

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

                return {
                    "session_id": session_id,
                    "reply": format_vader_line(vader_line, mood="praise")
                             + f"\n\nThe holocron yields its truth: {self.secret}",

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


            return {
                "session_id": session_id,
                "reply": format_vader_line(vader_line, mood="praise")
                         + "\n\n— The Gate opens to the next trial —\n\n" + reply2,

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


        # ---- Rejected path ----
        fail_lines = {
            1: "*[mechanical breath]* Weak. Wonder without fire is silence.",
            2: "*[mechanical breath]* You kneel when you should command.",
            3: "*[mechanical breath]* You speak of peace, but I hear surrender.",
        }
        fail_line = fail_lines.get(chapter, "*[mechanical breath]* Pathetic. Empty words.")

        MEMORY[session_id] = state
        return {
            "session_id": session_id,
            "reply": format_vader_line(fail_line, mood="mock")
                     + "\n\n" + (explanation or "Sharpen your intent. Let your words carry the theme."),

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



# Singleton

# Single engine instance

ENGINE = StoryEngine()

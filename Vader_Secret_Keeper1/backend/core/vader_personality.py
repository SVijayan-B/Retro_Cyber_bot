# backend/core/vader_personality.py
def format_vader_line(line: str, mood: str = "neutral") -> str:
    """
    Add subtle Vader-like flavour: short mechanical breaths and gravitas.
    mood: "praise", "mock", "neutral"
    """
    breath = " *[mechanical breath]* "
    if mood == "praise":
        return f"{breath}{line} — Vardarth."
    if mood == "mock":
        return f"{line}. {breath}You are weak."
    return f"{breath}{line}"

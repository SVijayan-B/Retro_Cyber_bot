from __future__ import annotations
import os
from typing import List
from dotenv import load_dotenv

load_dotenv()  # loads .env if present

def _csv(name: str, default: str = "") -> List[str]:
    raw = os.getenv(name, default)
    return [x.strip() for x in raw.split(",") if x.strip()]

APP_NAME = os.getenv("APP_NAME", "Retro-Cyber Secret Keeper")
APP_ENV = os.getenv("APP_ENV", "dev")
ALLOWED_ORIGINS = _csv("ALLOWED_ORIGINS", "*")

# Secret system
SECRET_FRAGMENTS = _csv("SECRET_FRAGMENTS", "FRAG-AAA,FRAG-BBB,FRAG-CCC")
SENTIMENT_THRESHOLD = os.getenv("SENTIMENT_THRESHOLD", "neutral").lower()
ALLOWED_IDEOLOGIES = set(x.lower() for x in _csv("ALLOWED_IDEOLOGIES", "balance,growth,power,dominance"))

# Retro_Cyber_bot

## 🌌 Project Overview

**Vader Secret Keeper** is a retro-inspired **AI storytelling chatbot** that fuses  
the dark mystique of **Darth Vader** with the neon-soaked vibes of **80s arcade sci-fi**.  

- 🎮 The player enters a **cyber-temple**, guided by *Vardarth*, a Sith Gatekeeper 
- The Secret key revaled only when the **mindset of the seeker(user) matches** the gate keeper Vardarth
- 🧩 They must progress through **3 emotion-driven trials**:  
  - Curiosity & Anger  
  - Dominance  
  - Realisation & Peace  
- 🔐 With each correct answer, fragments of a **Holocron key** are revealed.  
- 🌠 Once all fragments are collected, the **final secret of balance and mastery** is unlocked.  

## Why it’s unique:
- ⚡ **Dynamic Story Engine** – every trial adapts to the seeker’s state of mind.  
- 🤖 **AI-driven evaluation** – answers are semantically analyzed for meaning, not just keywords.  
- 🎨 **Retro Cyber Theme** – neon red/cyan styling, semi-transparent holo panels, starfield background.  
- 🚀 **Full-stack project** – FastAPI backend + React (Vite) frontend with smooth animations.  

✨ It’s more than a chatbot — it’s an **interactive Star Wars–inspired trial of the spirit** wrapped in retro cyberpunk aesthetics.


## ⚙️ Tech Stack
- **Frontend**: React + Vite, Axios, custom CSS (retro neon styling)  
- **Backend**: FastAPI (Python), Uvicorn, modular services  
- **AI Layer**: Google Gemini API (semantic text generation & evaluation)  
- **State Management**: In-memory session tracking for chapters & fragments  


## visual DocumentationUser ──(message)──▶ Frontend (React UI) 
       ◀─(reply)─── Backend (FastAPI + StoryEngine)
                         │
                         ▼
                   Emotion Analyzer
                         │
                         ▼
                   Google Gemini API
                         │
                         ▼
                   Story + Riddle Generation


## story flow to unlock the key 
[Chapter 1] → Curiosity & Anger
      │ (correct intent)
      ▼
[Chapter 2] → Dominance
      │ (correct intent)
      ▼
[Chapter 3] → Realisation & Peace
      │
      ▼
🔐 Unlocks Final Holocron Secret


## Demonstration Video
[▶️ Watch the Demo](https://drive.google.com/file/d/13oKB666NMnUeCq2CFjYWBLVEPphH_tHK/view?usp=drive_link)

## Installation & setup

**Clone repo**

    git clone https://github.com/SVijayan-B/Retro_Cyber_bot.git
    cd Retro_Cyber_bot

**Virtual Environemts**

    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    pip install -r requirements.txt

**Start Server**
    cd Vader_Secret_Keeper1
    uvicorn backend.app:app --reload

### Frontend Setup

    cd frontend
    npm install
    npm run dev

### Secret key Implementation

🔐 Secret Key Mechanism

The Holocron’s Final Secret is not given at the start. It is guarded across three narrative chapters, each one requiring the player to demonstrate specific emotional intent.

**How It Works**

Each chapter has a hidden emotional theme.
The Story Engine generates immersive narrative + a riddle challenge.
The player must respond in alignment with the required emotions.

- Responses are checked by the Emotion Analyzer, which matches intent using AI + semantic synonyms.

If successful, the player receives a Fragment Key (FRAG-X).
After all 3 fragments are collected, the Holocron yields the Final Secret.

### Chapter Breakdown 

**Chapter 1 → Curiosity & Anger**
Requires the seeker to balance wonder and fury.
Example: “I want to know the truth, even if I must tear it open.”

Unlocks: FRAG-1

**Chapter 2 → Dominance**

Tests commanding presence vs. submission.
Example: “I will not kneel. The gate bends to my will.”

Unlocks: FRAG-2

**Chapter 3 → Realisation & Peace**

Demands a calm but strong acceptance of balance.
Example: “Peace is not surrender, it is strength in stillness.”

Unlocks: FRAG-3
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, Any, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    SKILLS_DIR
)

# Add skills directories to sys.path so we can import hookscore and title linter directly
sys.path.insert(0, str(SKILLS_DIR / "yt-script"))
sys.path.insert(0, str(SKILLS_DIR / "yt-package"))

try:
    import hookscore
except ImportError:
    hookscore = None

try:
    import title as title_linter
except ImportError:
    title_linter = None


SYSTEM_PROMPT = """You are an elite viral YouTube Shorts scriptwriter specializing in Tech & AI Breakthroughs.
Your job is to produce high-retention, curiosity-driven scripts under 45 seconds (approx. 70-90 words spoken at 150wpm).

MANDATORY RULES:
1. THE FIRST 3 SECONDS (HOOK): Must immediately open a curiosity loop or state a shocking contrast.
   - Use numbers, dates, or specific names.
   - Never use filler openings like "Hey guys", "In this video", "Did you know that".
   - Address the viewer directly ("you", "your").
2. PACING (BEATS):
   - Break the script into 4 to 6 punchy beats.
   - For each beat, supply:
     * "text": the spoken line (short, conversational, zero fluff).
     * "on_screen": 1 to 3 bold punchy words to display in kinetic typography (e.g., "1200 WATTS", "NUCLEAR BACKUP").
3. PAYOFF:
   - Deliver on the hook by the 30-second mark.
4. TITLE & PACKAGING:
   - Title must be under 50 characters, clear, and carry a concrete figure or name.
   - Create 4-6 hyper-targeted SEO tags.

OUTPUT FORMAT:
Return pure JSON only conforming to:
{
  "title": "string (under 50 chars)",
  "hook": "string (the opening sentence)",
  "script": "string (the complete spoken script)",
  "beats": [
    {"text": "spoken sentence", "on_screen": "1-3 WORDS"},
    ...
  ],
  "description": "string (SEO description with target search queries and 3 hashtags)",
  "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"]
}
"""

def load_voice_profile() -> str:
    """Load user's custom voice profile from templates/voice.md or ~/.claude/youtube/voice.md."""
    candidates = [
        PROJECT_ROOT / "templates" / "voice.md",
        Path.home() / ".claude" / "youtube" / "voice.md",
        Path.home() / ".gemini" / "config" / "youtube" / "voice.md"
    ]
    for p in candidates:
        if p.exists():
            try:
                with open(p, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                        return content
            except Exception:
                pass
    return ""


def generate_script_with_gemini(topic: str) -> Optional[Dict[str, Any]]:
    """Generate script using Google Gemini API enforcing voice.md guidelines."""
    if not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_api_key_here":
        return None

    try:
        from google import genai
        client = genai.Client(api_key=GEMINI_API_KEY)
        
        voice_profile = load_voice_profile()
        prompt = (
            f"Topic: {topic}\n\n"
            f"--- USER'S VOICE PROFILE (STRICTLY ADHERE TO THIS STYLE, FORBIDDEN WORDS & AUDIENCE) ---\n"
            f"{voice_profile}\n"
            f"----------------------------------------------------------------------------------------\n\n"
            f"Write a 30-40 second viral YouTube Short script following all retention, packaging, and voice guidelines."
        )
        
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[SYSTEM_PROMPT, prompt],
            config={
                "response_mime_type": "application/json",
                "temperature": 0.7,
            }
        )
        
        if response.text:
            data = json.loads(response.text)
            return data
    except Exception as e:
        print(f"[WARN] Gemini API call failed: {e}. Falling back to heuristic generator.")
        return None


def generate_fallback_script(topic: str) -> Dict[str, Any]:
    """High-quality heuristic script generator with 5 competing hook candidates based on the 21 formulas."""
    t = topic.strip()
    t_clean = re.sub(r'^(The Secret Reason|The Shocking Reason|Why|How)\s*', '', t, flags=re.I).strip()
    core_subject = t_clean.split()[0] if t_clean else "Tech"
    
    # 5 Hook candidates based on 21 formulas (The Statistic, The Mistake, Someone Else's Result, Contrarian Flip, I Tried It)
    candidate_hooks = [
        f"You are probably still thinking {core_subject} is just software, but that mistake is costing billions.",
        f"97% of people don't know that {t_clean.lower()} is already happening right now.",
        f"Everyone says AI needs more data. They are actually dead wrong—it needs nuclear power.",
        f"Engineers tested {core_subject} for 30 days and discovered a secret nobody talks about.",
        f"Why is everyone secretly terrified of {t_clean.lower()}? Here is what happens next."
    ]
    
    # Score all 5 hooks through hookscore engine
    scored_hooks = []
    for h in candidate_hooks:
        if hookscore:
            parts, verdict, formula_name, hits = hookscore.score(h)
            scored_hooks.append({"hook": h, "score": verdict, "formula": formula_name, "parts": parts})
        else:
            scored_hooks.append({"hook": h, "score": 75, "formula": "Heuristic", "parts": {}})
            
    scored_hooks.sort(key=lambda x: x["score"], reverse=True)
    winner = scored_hooks[0]
    
    # Build clean title
    title_words = t_clean.split()
    title_short = ""
    for w in title_words:
        if len(title_short + " " + w) > 42:
            break
        title_short = f"{title_short} {w}".strip()
    title = f"Why {title_short}?" if not t.lower().startswith("how") else f"How {title_short}"
    
    return {
        "title": title,
        "hook": winner["hook"],
        "hook_score": winner["score"],
        "hook_formula": winner["formula"],
        "all_hooks": scored_hooks,
        "script": (
            f"{winner['hook']} "
            f"Engineers just discovered a massive breakthrough that changes everything. "
            f"Instead of taking months to compute, it now happens in under 4 seconds. "
            f"Tech giants are investing billions, but nobody is talking about the real downside. "
            f"The energy cost is skyrocketing 10x faster than traditional systems. "
            f"AI isn't hitting a software wall. It's hitting an energy wall."
        ),
        "beats": [
            {"text": winner["hook"], "on_screen": "SHOCKING TRUTH"},
            {"text": "Engineers just discovered a massive breakthrough that changes everything.", "on_screen": "BREAKTHROUGH"},
            {"text": "Instead of taking months to compute, it now happens in under 4 seconds.", "on_screen": "4 SECONDS"},
            {"text": "Tech giants are investing billions, but nobody is talking about the real downside.", "on_screen": "BILLIONS INVESTED"},
            {"text": "The energy cost is skyrocketing 10x faster than traditional systems.", "on_screen": "10X ENERGY"},
            {"text": "AI isn't hitting a software wall. It's hitting an energy wall.", "on_screen": "ENERGY WALL"}
        ],
        "description": f"The hidden reality behind {topic}. Is modern technology growing too fast for the global energy grid?\n\n#Tech #AI #Breakthrough #Shorts",
        "tags": ["Artificial Intelligence", "Tech Breakthrough", "Future Tech", "Silicon Valley", "Shorts"]
    }


def generate_and_lint_script(topic: str) -> Dict[str, Any]:
    """
    Main entry point: Generates script, validates against hookscore and title linter.
    """
    print(f"\n[1/4] Generating Script for Topic: '{topic}'...")
    
    data = generate_script_with_gemini(topic)
    if not data:
        data = generate_fallback_script(topic)
    
    # 1. Run hook through hookscore.py if available
    hook = data.get("hook", "")
    if not hook and data.get("beats"):
        hook = data["beats"][0].get("text", "")
        data["hook"] = hook
        
    if hookscore and hook:
        parts, verdict, formula_name, hits = hookscore.score(hook)
        data["hook_score"] = verdict
        data["hook_formula"] = formula_name
        print(f"  ✓ Hook Score: {verdict}/100 | Formula: {formula_name} | Grade: {hookscore.band(verdict)}")
    else:
        data["hook_score"] = 80
        data["hook_formula"] = "Custom"

    # 2. Lint Title
    title = data.get("title", topic)
    if title_linter and title:
        lint = title_linter.check(title)
        data["title_score"] = lint.get("score", 85)
        print(f"  ✓ Title Score: {lint.get('score', 85)}/100 ({lint.get('chars', len(title))} chars)")
    else:
        data["title_score"] = 85

    # Assemble complete text from beats if script is missing
    if not data.get("script") and data.get("beats"):
        data["script"] = " ".join(b["text"] for b in data["beats"])

    return data


if __name__ == "__main__":
    test_topic = "Why Nvidia's Blackwell GPUs Actually Draw 1200 Watts Each"
    res = generate_and_lint_script(test_topic)
    print(json.dumps(res, indent=2))

import json
import random
import sys
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import CURATED_TOPICS, OUTPUTS_DIR, GEMINI_API_KEY, GEMINI_MODEL

HISTORY_FILE = OUTPUTS_DIR / "used_topics.json"

def get_used_topics() -> list[str]:
    """Retrieve previously generated topics to prevent duplication."""
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def mark_topic_used(topic: str) -> None:
    """Save used topic into history."""
    used = get_used_topics()
    if topic not in used:
        used.append(topic)
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(used, f, indent=2)

def _trend_worker(q, api_key, model, prompt_text):
    try:
        from google import genai
        c = genai.Client(api_key=api_key)
        r = c.models.generate_content(
            model=model,
            contents=prompt_text,
            config={"response_mime_type": "application/json", "temperature": 0.8}
        )
        if r and r.text:
            topics = json.loads(r.text)
            if isinstance(topics, list) and topics:
                q.put([t.strip() for t in topics if isinstance(t, str)])
    except Exception:
        pass


def fetch_trending_topics_with_gemini() -> list[str]:
    """Uses Gemini API to brainstorm viral, trending AI & Tech Shorts topics."""
    if not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_api_key_here":
        return []
    
    try:
        import multiprocessing
        used = get_used_topics()
        
        prompt = (
            "Generate 5 viral, high-retention YouTube Shorts topics about cutting-edge tech, AI breakthroughs, "
            "open-source self-hosting, developer architecture, or extreme hardware limits that programmers and tech enthusiasts care about right now.\n"
            "MANDATORY CRITERIA:\n"
            "- Topics must have strong contrast, surprising numbers, or counter-intuitive truths (like Fireship).\n"
            "- Under 60 characters per topic.\n"
            f"- Must NOT be any of these already used topics: {used[-10:] if used else 'none'}\n"
            "Output pure JSON array of strings: [\"Topic 1\", \"Topic 2\", ...]"
        )

        q = multiprocessing.Queue()
        p = multiprocessing.Process(
            target=_trend_worker,
            args=(q, GEMINI_API_KEY, GEMINI_MODEL, prompt)
        )
        p.start()
        p.join(timeout=4.0)

        if p.is_alive():
            p.terminate()
            p.join(timeout=0.5)
            return []

        if not q.empty():
            return q.get()
        return []
    except Exception:
        return []

def select_topic(explicit_topic: Optional[str] = None) -> str:
    """Select next topic: either explicit, Gemini AI-discovered, or high-RPM pool."""
    if explicit_topic and explicit_topic.strip():
        mark_topic_used(explicit_topic.strip())
        return explicit_topic.strip()

    used = set(get_used_topics())

    # 1. Try discovering fresh viral topics with Gemini
    ai_topics = fetch_trending_topics_with_gemini()
    for t in ai_topics:
        if t not in used:
            mark_topic_used(t)
            print(f"  ✓ Gemini discovered trending topic: '{t}'")
            return t

    # 2. Fallback to curated high-RPM pool without repeating
    available = [t for t in CURATED_TOPICS if t not in used]
    if not available:
        available = CURATED_TOPICS

    chosen = random.choice(available)
    mark_topic_used(chosen)
    return chosen

if __name__ == "__main__":
    t = select_topic()
    print(f"Selected Topic: {t}")


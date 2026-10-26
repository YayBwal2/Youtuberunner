import json
import random
from pathlib import Path
from typing import Optional
from config import CURATED_TOPICS, OUTPUTS_DIR

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

def select_topic(explicit_topic: Optional[str] = None) -> str:
    """Select next topic from explicit argument or high-RPM pool without repeating."""
    if explicit_topic and explicit_topic.strip():
        mark_topic_used(explicit_topic.strip())
        return explicit_topic.strip()

    used = set(get_used_topics())
    available = [t for t in CURATED_TOPICS if t not in used]

    # If all curated topics have been used, reset pool
    if not available:
        available = CURATED_TOPICS

    chosen = random.choice(available)
    mark_topic_used(chosen)
    return chosen

if __name__ == "__main__":
    t = select_topic()
    print(f"Selected Topic: {t}")

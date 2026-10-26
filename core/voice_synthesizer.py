import asyncio
import re
from pathlib import Path
from typing import Dict, Any, List, Tuple
import edge_tts

import sys
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import (
    VOICE_NAME,
    VOICE_RATE,
    VOICE_PITCH,
    TEMP_DIR
)


def calculate_word_timings(sentence_boundaries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Interpolates exact word timings based on character lengths within each sentence boundary.
    """
    words_timeline = []
    
    for s in sentence_boundaries:
        s_start = s["start"]
        s_end = s["end"]
        s_text = s["text"]
        s_duration = max(0.2, s_end - s_start)
        
        raw_words = s_text.strip().split()
        if not raw_words:
            continue
            
        total_chars = sum(len(w) for w in raw_words)
        if total_chars == 0:
            total_chars = len(raw_words)
            
        curr_t = s_start
        for w in raw_words:
            # Word duration proportional to character count
            w_dur = (len(w) / total_chars) * s_duration
            w_start = curr_t
            w_end = min(s_end, curr_t + w_dur)
            curr_t = w_end
            
            clean_w = re.sub(r'^[^\w]+|[^\w]+$', '', w).upper()
            if clean_w:
                words_timeline.append({
                    "word": clean_w,
                    "raw": w,
                    "start": round(w_start, 3),
                    "end": round(w_end, 3),
                    "sentence": s_text
                })
                
    return words_timeline


async def _generate_audio_async(text: str, output_path: Path) -> Tuple[List[Dict[str, Any]], str]:
    """Async generation with edge-tts."""
    comm = edge_tts.Communicate(text, voice=VOICE_NAME, rate=VOICE_RATE, pitch=VOICE_PITCH)
    sub = edge_tts.SubMaker()
    sentence_boundaries = []

    with open(output_path, "wb") as f:
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "SentenceBoundary":
                sub.feed(chunk)
                # 10,000,000 ticks per second
                start = chunk["offset"] / 10_000_000.0
                duration = chunk["duration"] / 10_000_000.0
                sentence_boundaries.append({
                    "text": chunk["text"],
                    "start": round(start, 3),
                    "end": round(start + duration, 3)
                })

    srt_content = sub.get_srt()
    return sentence_boundaries, srt_content


def synthesize_speech(script_text: str, output_filename: str = "narration.mp3") -> Dict[str, Any]:
    """
    Main entry point: Generates speech MP3 and returns timing metadata.
    """
    print(f"\n[2/4] Synthesizing Voice with edge-tts ('{VOICE_NAME}')...")
    audio_path = TEMP_DIR / output_filename
    srt_path = TEMP_DIR / output_filename.replace(".mp3", ".srt")
    
    sentence_boundaries, srt_content = asyncio.run(_generate_audio_async(script_text, audio_path))
    
    with open(srt_path, "w", encoding="utf-8") as f:
        f.write(srt_content)
        
    word_timings = calculate_word_timings(sentence_boundaries)
    total_duration = sentence_boundaries[-1]["end"] if sentence_boundaries else 0.0
    
    print(f"  ✓ Audio generated: {audio_path.name} ({total_duration:.1f}s)")
    print(f"  ✓ Processed {len(sentence_boundaries)} sentences and {len(word_timings)} word timings")
    
    return {
        "audio_path": str(audio_path),
        "srt_path": str(srt_path),
        "duration": total_duration,
        "sentences": sentence_boundaries,
        "words": word_timings
    }


if __name__ == "__main__":
    test_text = "Nvidia's new Blackwell GPU draws twelve hundred watts. That is more power than your entire kitchen."
    res = synthesize_speech(test_text)
    print("Words sample:", res["words"][:5])

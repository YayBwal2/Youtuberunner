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


async def _generate_audio_async(text: str, output_path: Path) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], str]:
    """
    Async generation with edge-tts capturing real neural WordBoundary events.
    Guarantees millisecond-accurate spoken word timestamps directly from Microsoft TTS.
    """
    comm = edge_tts.Communicate(
        text,
        voice=VOICE_NAME,
        rate=VOICE_RATE,
        pitch=VOICE_PITCH,
        boundary="WordBoundary"
    )
    
    words_timeline: List[Dict[str, Any]] = []

    with open(output_path, "wb") as f:
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                start = round(chunk["offset"] / 10_000_000.0, 3)
                duration = round(chunk["duration"] / 10_000_000.0, 3)
                raw_w = chunk["text"]
                clean_w = re.sub(r'^[^\w]+|[^\w]+$', '', raw_w).upper()
                if clean_w:
                    words_timeline.append({
                        "word": clean_w,
                        "raw": raw_w,
                        "start": start,
                        "end": round(start + duration, 3)
                    })

    # Group words into sentence boundaries based on script punctuation
    sentence_boundaries: List[Dict[str, Any]] = []
    # Split text into sentences
    raw_sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
    
    word_idx = 0
    total_words = len(words_timeline)

    for s_text in raw_sentences:
        s_words = s_text.split()
        if not s_words:
            continue
        
        target_count = len(s_words)
        end_idx = min(total_words, word_idx + target_count)
        
        if word_idx < total_words:
            s_start = words_timeline[word_idx]["start"]
            s_end = words_timeline[end_idx - 1]["end"]
            
            # Tag sentence on each word
            for w in words_timeline[word_idx:end_idx]:
                w["sentence"] = s_text
                
            sentence_boundaries.append({
                "text": s_text,
                "start": s_start,
                "end": s_end
            })
            word_idx = end_idx

    # If leftover words exist, extend final sentence
    if word_idx < total_words and sentence_boundaries:
        sentence_boundaries[-1]["end"] = words_timeline[-1]["end"]

    # Generate SRT content from exact word chunks
    srt_lines = []
    chunk_size = 3
    sub_idx = 1
    for i in range(0, len(words_timeline), chunk_size):
        group = words_timeline[i:i + chunk_size]
        if not group:
            continue
        g_start = group[0]["start"]
        g_end = group[-1]["end"]
        g_text = " ".join(w["raw"] for w in group)
        
        def to_srt_time(secs: float) -> str:
            hours = int(secs // 3600)
            mins = int((secs % 3600) // 60)
            seconds = int(secs % 60)
            millis = int((secs - int(secs)) * 1000)
            return f"{hours:02d}:{mins:02d}:{seconds:02d},{millis:03d}"

        srt_lines.append(f"{sub_idx}\n{to_srt_time(g_start)} --> {to_srt_time(g_end)}\n{g_text}\n")
        sub_idx += 1

    srt_content = "\n".join(srt_lines)
    return sentence_boundaries, words_timeline, srt_content


def synthesize_speech(script_text: str, output_filename: str = "narration.mp3") -> Dict[str, Any]:
    """
    Main entry point: Generates speech MP3 and returns timing metadata with real neural word boundaries.
    """
    print(f"\n[2/4] Synthesizing Voice with edge-tts ('{VOICE_NAME}')...")
    audio_path = TEMP_DIR / output_filename
    srt_path = TEMP_DIR / output_filename.replace(".mp3", ".srt")
    
    sentence_boundaries, word_timings, srt_content = asyncio.run(_generate_audio_async(script_text, audio_path))
    
    with open(srt_path, "w", encoding="utf-8") as f:
        f.write(srt_content)
        
    total_duration = word_timings[-1]["end"] if word_timings else 0.0
    
    print(f"  ✓ Audio generated: {audio_path.name} ({total_duration:.1f}s)")
    print(f"  ✓ Captured {len(word_timings)} real neural word timestamps across {len(sentence_boundaries)} sentences")
    
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

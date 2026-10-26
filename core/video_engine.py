import math
import re
import sys
from pathlib import Path
from typing import Dict, Any, List

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import VideoClip, AudioFileClip

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import (
    VIDEO_WIDTH,
    VIDEO_HEIGHT,
    VIDEO_FPS,
    FONT_MONO,
    FONT_SANS,
    COLORS,
    OUTPUTS_DIR,
    TEMP_DIR
)


def create_developer_background() -> Image.Image:
    """Pre-compute a sleek Slate Black background with a subtle developer dot matrix."""
    base = Image.new("RGB", (VIDEO_WIDTH, VIDEO_HEIGHT), COLORS["bg_dark"])
    draw = ImageDraw.Draw(base)
    
    # Subtle dot matrix (40px spacing)
    dot_color = (26, 36, 54)  # very subtle slate dot
    for x in range(40, VIDEO_WIDTH, 50):
        for y in range(40, VIDEO_HEIGHT, 50):
            draw.ellipse([x, y, x + 2, y + 2], fill=dot_color)
            
    return base


def build_word_chunks(words: List[Dict[str, Any]], chunk_size: int = 3) -> List[Dict[str, Any]]:
    """Group words into small readable 3-word chunks for kinetic typography."""
    chunks = []
    for i in range(0, len(words), chunk_size):
        group = words[i:i + chunk_size]
        if not group:
            continue
        c_start = group[0]["start"]
        c_end = group[-1]["end"]
        chunks.append({
            "start": c_start,
            "end": c_end,
            "words": group
        })
    return chunks


def render_shorts_video(
    script_data: Dict[str, Any],
    voice_data: Dict[str, Any],
    output_filename: str = "shorts_video.mp4"
) -> str:
    """
    Renders 9:16 vertical MP4 in Fireship / Developer Terminal Minimalist style.
    """
    print(f"\n[3/4] Rendering Developer Terminal Video ({VIDEO_WIDTH}x{VIDEO_HEIGHT} @ {VIDEO_FPS}fps)...")
    
    duration = voice_data["duration"]
    audio_path = voice_data["audio_path"]
    words_timeline = voice_data["words"]
    beats = script_data.get("beats", [])
    topic_title = script_data.get("title", "system")
    
    # Clean topic slug for terminal title
    terminal_slug = re.sub(r'[^\w]', '_', topic_title.lower()).strip('_')[:24]
    
    # Pre-compute word chunks
    chunks = build_word_chunks(words_timeline, chunk_size=3)
    
    # Fonts
    font_mono_small = ImageFont.truetype(str(FONT_MONO), 26)
    font_mono_code = ImageFont.truetype(str(FONT_MONO), 31)
    font_badge = ImageFont.truetype(str(FONT_MONO), 28)
    font_caption = ImageFont.truetype(str(FONT_SANS), 72)
    
    # Pre-render base background
    base_bg = create_developer_background()
    
    # Terminal Dimensions (Top half)
    card_x1, card_y1 = 60, 240
    card_x2, card_y2 = VIDEO_WIDTH - 60, 920
    
    # Generate frame at time t
    def make_frame(t: float) -> np.ndarray:
        frame = base_bg.copy()
        draw = ImageDraw.Draw(frame)
        
        # -------------------------------------------------------------
        # 1. macOS / VS Code Terminal Card (Top half)
        # -------------------------------------------------------------
        # Window outer container
        draw.rounded_rectangle(
            [card_x1, card_y1, card_x2, card_y2],
            radius=24,
            fill=(17, 24, 39),
            outline=(51, 65, 85),
            width=2
        )
        
        # Titlebar
        draw.rounded_rectangle([card_x1, card_y1, card_x2, card_y1 + 64], radius=24, fill=(30, 41, 59))
        draw.rectangle([card_x1, card_y1 + 40, card_x2, card_y1 + 64], fill=(30, 41, 59))
        
        # Traffic light buttons (Red, Yellow, Green)
        draw.ellipse([card_x1 + 24, card_y1 + 22, card_x1 + 44, card_y1 + 42], fill=(239, 68, 68))
        draw.ellipse([card_x1 + 54, card_y1 + 22, card_x1 + 74, card_y1 + 42], fill=(245, 158, 11))
        draw.ellipse([card_x1 + 84, card_y1 + 22, card_x1 + 104, card_y1 + 42], fill=(34, 197, 94))
        
        # Terminal Tab Title
        tab_str = f"bash ~ /{terminal_slug}.sh"
        tb = font_mono_small.getbbox(tab_str)
        tw = tb[2] - tb[0]
        draw.text(((VIDEO_WIDTH - tw) // 2, card_y1 + 18), tab_str, font=font_mono_small, fill=(148, 163, 184))
        
        # Terminal Body Code (revealed progressively across beats)
        terminal_lines = [
            ("$ system --monitor --live", (148, 163, 184)),
            ("[✓] Architecture: PRODUCTION_READY", (34, 197, 94)),
        ]
        
        # Determine how many beats have been spoken so far
        num_beats = len(beats) if beats else 1
        current_beat_idx = min(num_beats - 1, int((t / max(0.1, duration)) * num_beats))
        
        for b_i in range(current_beat_idx + 1):
            if b_i < len(beats):
                b_cue = beats[b_i].get("on_screen", "").upper().replace(" ", "_")
                if b_i == 0:
                    terminal_lines.append((f"[!] Target: {b_cue}", (245, 158, 11)))
                elif b_i % 2 == 1:
                    terminal_lines.append((f"    └─ Analysis: {b_cue}", (56, 189, 248)))
                else:
                    terminal_lines.append((f"[✓] Status: {b_cue}", (34, 197, 94)))
                    
        # Blinking terminal cursor
        cursor_visible = (int(t * 2) % 2 == 0)
        cursor_char = " █" if cursor_visible else ""
        terminal_lines.append((f">{cursor_char}", (34, 197, 94)))
        
        # Draw code lines (limit to last 7 lines to avoid overflow)
        display_lines = terminal_lines[-7:]
        line_y = card_y1 + 96
        for text_line, color in display_lines:
            draw.text((card_x1 + 36, line_y), text_line, font=font_mono_code, fill=color)
            line_y += 56
            
        # -------------------------------------------------------------
        # 2. On-Screen Code Comment Pill Badge (Middle)
        # -------------------------------------------------------------
        active_cue = beats[current_beat_idx].get("on_screen", "").upper() if beats else "CORE LOGIC"
        badge_text = f"// {active_cue}"
        bb = font_badge.getbbox(badge_text)
        bw, bh = bb[2] - bb[0], bb[3] - bb[1]
        bx = (VIDEO_WIDTH - bw) // 2
        by = 1080
        
        draw.rounded_rectangle(
            [bx - 24, by - 8, bx + bw + 24, by + bh + 10],
            radius=12,
            fill=(30, 41, 59),
            outline=(34, 197, 94),
            width=1
        )
        draw.text((bx, by), badge_text, font=font_badge, fill=(34, 197, 94))
        
        # -------------------------------------------------------------
        # 3. Kinetic Typography (Bottom half)
        # -------------------------------------------------------------
        active_chunk = None
        for c in chunks:
            if c["start"] <= t <= c["end"] + 0.15:
                active_chunk = c
                break
                
        if not active_chunk and chunks:
            if t < chunks[0]["start"]:
                active_chunk = chunks[0]
            elif t > chunks[-1]["end"]:
                active_chunk = chunks[-1]
                
        if active_chunk:
            c_words = active_chunk["words"]
            word_meas = []
            for w_info in c_words:
                w_str = w_info["word"]
                w_bb = font_caption.getbbox(w_str)
                word_meas.append((w_str, w_bb[2] - w_bb[0], w_bb[3] - w_bb[1]))
                
            spacing = 28
            total_chunk_width = sum(m[1] for m in word_meas) + (len(word_meas) - 1) * spacing
            start_x = (VIDEO_WIDTH - total_chunk_width) // 2
            center_y = 1200
            
            curr_x = start_x
            for idx, w_info in enumerate(c_words):
                w_str, w_width, _ = word_meas[idx]
                is_active = (w_info["start"] <= t < w_info["end"])
                
                if is_active:
                    # Glowing Neon Green for active spoken word
                    draw.text((curr_x + 3, center_y + 3), w_str, font=font_caption, fill=(0, 0, 0))
                    draw.text((curr_x, center_y), w_str, font=font_caption, fill=(34, 197, 94))
                else:
                    # Crisp white with subtle drop shadow
                    draw.text((curr_x + 3, center_y + 3), w_str, font=font_caption, fill=(10, 15, 25))
                    draw.text((curr_x, center_y), w_str, font=font_caption, fill=(255, 255, 255))
                    
                curr_x += w_width + spacing
                
        # -------------------------------------------------------------
        # 4. Neon Progress Bar (Very bottom)
        # -------------------------------------------------------------
        progress_ratio = min(1.0, max(0.0, t / max(0.1, duration)))
        bar_width = int(progress_ratio * VIDEO_WIDTH)
        draw.rectangle([0, VIDEO_HEIGHT - 12, VIDEO_WIDTH, VIDEO_HEIGHT], fill=(30, 41, 59))
        if bar_width > 0:
            draw.rectangle([0, VIDEO_HEIGHT - 12, bar_width, VIDEO_HEIGHT], fill=(34, 197, 94))
            
        return np.array(frame)

    # Render MoviePy Video
    video_clip = VideoClip(make_frame, duration=duration)
    audio_clip = AudioFileClip(audio_path)
    video_clip = video_clip.with_audio(audio_clip)
    
    output_path = OUTPUTS_DIR / output_filename
    video_clip.write_videofile(
        str(output_path),
        fps=VIDEO_FPS,
        codec="libx264",
        audio_codec="aac",
        preset="fast",
        threads=4,
        logger=None
    )
    
    # Save video thumbnail
    thumb_path = OUTPUTS_DIR / output_filename.replace(".mp4", "_thumb.png")
    thumb_frame = Image.fromarray(make_frame(min(2.0, duration / 2)))
    thumb_frame.save(thumb_path)
    
    print(f"  ✓ Video exported: {output_path.name} ({duration:.1f}s)")
    print(f"  ✓ Thumbnail exported: {thumb_path.name}")
    
    return str(output_path)


if __name__ == "__main__":
    from core.script_generator import generate_fallback_script
    from core.voice_synthesizer import synthesize_speech
    
    test_topic = "Why The Energy Wall is AI's Biggest Problem"
    s_data = generate_fallback_script(test_topic)
    v_data = synthesize_speech(s_data["script"])
    v_path = render_shorts_video(s_data, v_data, "developer_shorts_demo.mp4")
    print(f"Rendered test video: {v_path}")

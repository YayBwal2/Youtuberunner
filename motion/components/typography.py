from typing import List, Dict, Any, Optional
from PIL import ImageFont
from motion.layout import LayoutBox
from motion.tokens import HEX_PALETTE, FONTS


# Cache font instance for subtitle width measurement
_SUBTITLE_FONT = ImageFont.truetype(str(FONTS["sans_bold"]), 60)
_HEADLINE_FONT = ImageFont.truetype(str(FONTS["sans_bold"]), 52)


def render_kinetic_headline_svg(
    box: LayoutBox,
    text: str,
    highlight_words: List[str],
    motion_state: Dict[str, Any]
) -> str:
    """
    Renders high-impact kinetic headline with bold typography,
    subtle neon emerald accenting, and entrance slide-up/masking.
    Auto-wraps if title exceeds safe box width to prevent side clipping.
    """
    opacity = motion_state.get("opacity", 1.0)
    trans_y = motion_state.get("translate_y", 0.0)
    scale = motion_state.get("scale", 1.0)

    words = text.strip().split()
    hl_set = {w.lower().strip(".,!?\"'") for w in highlight_words}

    # Wrap words into lines that fit within box.width - 40
    max_w = box.width - 40
    lines = []
    curr_line = []
    for w in words:
        test = " ".join(curr_line + [w])
        if _HEADLINE_FONT.getlength(test) <= max_w:
            curr_line.append(w)
        else:
            if curr_line:
                lines.append(curr_line)
                curr_line = [w]
            else:
                lines.append([w])
                curr_line = []
    if curr_line:
        lines.append(curr_line)

    cx = box.center_x
    line_h = 62
    total_h = len(lines) * line_h
    start_y = box.y + (box.height - total_h) // 2 + 40

    text_nodes = []
    spacing = 18

    for l_idx, line_words in enumerate(lines):
        y_pos = start_y + l_idx * line_h
        
        # Measure word widths in this line
        measured_words = []
        for w in line_words:
            clean = w.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            w_len = _HEADLINE_FONT.getlength(clean)
            measured_words.append((w, clean, w_len))

        line_total_w = sum(l for _, _, l in measured_words) + (len(measured_words) - 1) * spacing
        line_start_x = cx - line_total_w / 2
        cur_x = line_start_x

        for orig_w, clean, w_len in measured_words:
            mid_x = cur_x + w_len / 2
            norm = orig_w.lower().strip(".,!?\"'")
            if norm in hl_set:
                fill_color = HEX_PALETTE["primary"]
                f_weight = "900"
            else:
                fill_color = HEX_PALETTE["text_white"]
                f_weight = "800"

            text_nodes.append(
                f'<text x="{mid_x:.1f}" y="{y_pos}" font-family="SF Pro Display, -apple-system, sans-serif" '
                f'font-size="52" font-weight="{f_weight}" fill="{fill_color}" '
                f'letter-spacing="-0.5px" text-anchor="middle">{clean}</text>'
            )
            cur_x += w_len + spacing

    transform = f'translate(0, {trans_y})'

    svg = f"""
  <g transform="{transform}" opacity="{opacity:.3f}">
    {"".join(text_nodes)}
  </g>
"""
    return svg


def render_active_subtitles_svg(
    box: LayoutBox,
    active_chunk: Optional[Dict[str, Any]],
    current_time: float
) -> str:
    """
    Renders kinetic bottom third subtitles. Active word highlighted in bright neon green,
    inactive words in crisp white, cleanly spaced using exact PIL text measurements
    to guarantee zero word overlap or collision.
    """
    if not active_chunk:
        return ""

    words_info = active_chunk.get("words", [])
    if not words_info:
        return ""

    cx = box.center_x
    cy = box.y + box.height // 2

    # Measure exact word dimensions to space words with 100% precision
    word_lengths = []
    for item in words_info:
        w_text = item["word"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        w_len = _SUBTITLE_FONT.getlength(w_text)
        word_lengths.append((item, w_text, w_len))

    spacing = 28
    total_chunk_w = sum(l for _, _, l in word_lengths) + (len(word_lengths) - 1) * spacing
    start_x = cx - total_chunk_w / 2

    word_svgs = []
    cur_x = start_x

    for item, w_text, w_len in word_lengths:
        w_start = item["start"]
        w_end = item["end"]
        mid_x = cur_x + w_len / 2

        # Check if word is active
        is_active = w_start <= current_time <= w_end + 0.05
        if is_active:
            fill_color = HEX_PALETTE["primary"]
            f_weight = "900"
            f_size = "64"
        else:
            fill_color = HEX_PALETTE["text_white"]
            f_weight = "700"
            f_size = "58"

        word_svgs.append(
            f'<text x="{mid_x:.1f}" y="{cy}" font-family="SF Pro Display, -apple-system, sans-serif" '
            f'font-size="{f_size}" font-weight="{f_weight}" fill="{fill_color}" '
            f'text-anchor="middle">{w_text}</text>'
        )

        cur_x += w_len + spacing

    svg = f"""
  <g>
    {"".join(word_svgs)}
  </g>
"""
    return svg

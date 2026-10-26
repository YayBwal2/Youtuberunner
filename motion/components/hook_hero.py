"""
motion/components/hook_hero.py - Visual Specification v1.0 Hook Scene Component
Fullscreen Kinetic Typography Dominance (104px Display) with Neon Pill Box.
Muted subtitles during first 3s for maximum visual impact.
Centered at Safe Area Center X = 500px.
"""

import math
from typing import Dict, Any


def ease_out_expo(t: float) -> float:
    return 1.0 if t >= 1.0 else 1.0 - math.pow(2, -10 * t)


def ease_out_back(t: float, s: float = 1.4) -> float:
    t = max(0.0, min(1.0, t)) - 1.0
    return t * t * ((s + 1.0) * t + s) + 1.0


def render_hook_hero_svg(
    safe_cx: int,
    line1: str,
    line2: str,
    pill_text: str,
    t_rel: float,
    duration: float,
    accent_color: str = "#22C55E"
) -> str:
    """
    Renders the Fullscreen Kinetic Typo Hook at relative scene time t_rel.
    """
    clean_l1 = line1.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").upper()
    clean_l2 = line2.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").upper()
    clean_pill = pill_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").upper()

    # Exit transition at end of scene (last 0.4s)
    exit_alpha = 1.0
    exit_offset_y = 0.0
    if duration > 0.6 and t_rel > (duration - 0.4):
        trans_p = (t_rel - (duration - 0.4)) / 0.4
        trans_p = max(0.0, min(1.0, trans_p))
        exit_alpha = max(0.0, 1.0 - trans_p * trans_p)
        exit_offset_y = -35.0 * trans_p

    # Dynamic font scaling to guarantee text never clips beyond Safe Area (max width: 750px at safe_cx=500)
    # Average uppercase bold letter width is ~0.62 * font_size
    len1 = max(1, len(clean_l1))
    len2 = max(1, len(clean_l2))
    
    fs1 = min(104, max(44, int(750 / (len1 * 0.62))))
    fs2 = min(104, max(44, int(750 / (len2 * 0.62))))

    # Line 1: Reveal 0.0s to 0.35s
    p1 = max(0.0, min(1.0, t_rel / 0.35))
    e1 = ease_out_expo(p1)
    l1_alpha = p1
    l1_y = 780 + (1.0 - e1) * 70 + exit_offset_y

    # Line 2: Reveal 0.20s to 0.55s
    p2 = max(0.0, min(1.0, (t_rel - 0.20) / 0.35)) if t_rel >= 0.20 else 0.0
    e2 = ease_out_expo(p2)
    l2_alpha = p2
    l2_y = 890 + (1.0 - e2) * 70 + exit_offset_y

    # Line 3: Neon Pill Box (reveal 0.45s to 0.90s)
    p3 = max(0.0, min(1.0, (t_rel - 0.45) / 0.45)) if t_rel >= 0.45 else 0.0
    e3 = ease_out_back(p3, s=1.4)
    l3_alpha = min(1.0, p3 * 2.0)
    pill_scale = max(0.001, e3)
    pill_y = 960 + exit_offset_y

    # Compute pill width and font size based on text length
    fs_pill = 70
    if len(clean_pill) > 14:
        fs_pill = max(46, int(70 * (14 / len(clean_pill))))

    pill_w = max(640, min(800, len(clean_pill) * (fs_pill // 2 + 8) + 120))
    pill_h = 140
    pill_half_w = pill_w // 2
    pill_half_h = pill_h // 2

    # Centered scaling matrix transform
    pill_transform = (
        f"translate({safe_cx}, {pill_y + pill_half_h}) "
        f"scale({pill_scale:.4f}) "
        f"translate({-pill_half_w}, {-pill_half_h})"
    )

    svg = f"""
  <!-- Hook Typo Dominance Group (Safe Center X: {safe_cx}) -->
  <g opacity="{exit_alpha:.3f}">
    <!-- Line 1 -->
    <text x="{safe_cx}" y="{l1_y:.1f}" 
          font-family="Arial, Helvetica, sans-serif" 
          font-size="{fs1}" font-weight="900" letter-spacing="-1.5" 
          fill="#FFFFFF" opacity="{l1_alpha:.3f}" text-anchor="middle">
      {clean_l1}
    </text>

    <!-- Line 2 -->
    <text x="{safe_cx}" y="{l2_y:.1f}" 
          font-family="Arial, Helvetica, sans-serif" 
          font-size="{fs2}" font-weight="900" letter-spacing="-1.5" 
          fill="#FFFFFF" opacity="{l2_alpha:.3f}" text-anchor="middle">
      {clean_l2}
    </text>

    <!-- Line 3: High-Impact Pill Box -->
    <g transform="{pill_transform}" opacity="{l3_alpha:.3f}">
      <rect width="{pill_w}" height="{pill_h}" rx="32" fill="{accent_color}" 
            filter="drop-shadow(0px 14px 20px rgba(34, 197, 94, 0.4))"/>
      <text x="{pill_half_w}" y="98" 
            font-family="Arial, Helvetica, sans-serif" 
            font-size="{fs_pill}" font-weight="900" letter-spacing="1.0" 
            fill="#090D16" text-anchor="middle">
        {clean_pill}
      </text>
    </g>
  </g>
"""
    return svg

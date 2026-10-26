"""
motion/components/verdict_card.py - Visual Specification v1.0 Payoff Scene Component
High-Impact Verdict Card (800x820px @ x:100 to 900) with Verified Badge,
Big Hero Metric Number (124px), Supporting Metric, and Loop Anchor CTA.
"""

from typing import Dict, Any


def ease_out_back(t: float, s: float = 1.1) -> float:
    t = max(0.0, min(1.0, t)) - 1.0
    return t * t * ((s + 1.0) * t + s) + 1.0


def render_verdict_card_svg(
    safe_cx: int,
    category_text: str,
    verified_badge: str,
    hero_metric: str,
    metric_subtitle: str,
    second_metric: str,
    second_subtitle: str,
    loop_anchor_question: str,
    loop_anchor_cta: str,
    t_rel: float,
    duration: float,
    sub_line1: str = "",
    sub_line2: str = ""
) -> str:
    """
    Renders the High-Impact Payoff Verdict Card with Loop Anchor CTA.
    """
    clean_cat = category_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").upper()
    clean_badge = verified_badge.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    clean_hero = hero_metric.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    clean_hero_sub = metric_subtitle.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").upper()
    clean_m2 = second_metric.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").upper()
    clean_m2_sub = second_subtitle.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").upper()
    clean_loop_q = loop_anchor_question.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    clean_loop_cta = loop_anchor_cta.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").upper()

    # Card entrance animation (first 0.5s of scene)
    p_enter = max(0.0, min(1.0, t_rel / 0.5))
    e_enter = ease_out_back(p_enter, s=1.1)
    card_alpha = p_enter
    card_y = 500 + (1.0 - e_enter) * 35.0

    # Subtitles
    subtitles_svg = ""
    if sub_line1 or sub_line2:
        clean_sub1 = sub_line1.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").upper()
        clean_sub2 = sub_line2.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").upper()
        subtitles_svg = f"""
    <!-- NEURAL SUBTITLES (Safe Center X: {safe_cx}, Y: 1400) -->
    <g transform="translate({safe_cx}, 1400)">
      <text x="0" y="0" text-anchor="middle" font-family="system-ui, -apple-system, Arial, sans-serif" font-size="44" font-weight="700" fill="#FFFFFF">
        {clean_sub1}
      </text>
      <text x="0" y="56" text-anchor="middle" font-family="system-ui, -apple-system, Arial, sans-serif" font-size="52" font-weight="900" fill="#22C55E">
        {clean_sub2}
      </text>
    </g>
"""

    badge_w = max(340, len(clean_badge) * 12 + 40)
    badge_x = 400 - badge_w // 2

    svg = f"""
  <!-- Section Category Header -->
  <text x="{safe_cx}" y="440" 
        font-family="system-ui, -apple-system, Arial, sans-serif" 
        font-size="42" font-weight="800" letter-spacing="2" 
        fill="#94A3B8" text-anchor="middle" opacity="{card_alpha:.3f}">
    {clean_cat}
  </text>

  <!-- VERDICT CARD CONTAINER (800 x 820 @ x: 100) -->
  <g transform="translate(100, {card_y:.1f})" opacity="{card_alpha:.3f}"
     filter="drop-shadow(0px 16px 24px rgba(34, 197, 94, 0.25))">
    <rect width="800" height="820" rx="28" fill="#111827" stroke="#22C55E" stroke-width="2.5"/>

    <!-- Status Verified Pill Badge -->
    <g transform="translate({badge_x}, 70)">
      <rect width="{badge_w}" height="58" rx="29" fill="rgba(34, 197, 94, 0.15)" stroke="#22C55E" stroke-width="2"/>
      <text x="{badge_w // 2}" y="38" font-family="'SF Mono', Menlo, monospace" font-size="22" font-weight="700" letter-spacing="1" fill="#22C55E" text-anchor="middle">
        {clean_badge}
      </text>
    </g>

    <!-- Big Hero Metric Number -->
    <text x="400" y="270" font-family="system-ui, -apple-system, Arial, sans-serif" font-size="124" font-weight="900" letter-spacing="-2" fill="#FFFFFF" text-anchor="middle">
      {clean_hero}
    </text>
    <text x="400" y="330" font-family="'SF Mono', Menlo, monospace" font-size="24" font-weight="600" letter-spacing="2" fill="#94A3B8" text-anchor="middle">
      {clean_hero_sub}
    </text>

    <!-- Subtle Divider Line -->
    <line x1="70" y1="390" x2="730" y2="390" stroke="#334155" stroke-width="2"/>

    <!-- Supporting Metric 2 -->
    <text x="400" y="480" font-family="system-ui, -apple-system, Arial, sans-serif" font-size="64" font-weight="900" fill="#22C55E" text-anchor="middle">
      {clean_m2}
    </text>
    <text x="400" y="525" font-family="'SF Mono', Menlo, monospace" font-size="22" fill="#94A3B8" text-anchor="middle">
      {clean_m2_sub}
    </text>

    <!-- Loop Anchor Interaction Box -->
    <g transform="translate(50, 600)">
      <rect width="700" height="150" rx="16" fill="#1E293B" stroke="#334155" stroke-width="1.5"/>
      <text x="350" y="58" font-family="system-ui, -apple-system, Arial, sans-serif" font-size="26" font-weight="700" fill="#CBD5E1" text-anchor="middle">
        {clean_loop_q}
      </text>
      <text x="350" y="105" font-family="'SF Mono', Menlo, monospace" font-size="22" font-weight="800" fill="#38BDF8" text-anchor="middle">
        {clean_loop_cta}
      </text>
    </g>
  </g>

  {subtitles_svg}
"""
    return svg

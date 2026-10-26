"""
motion/components/progressive_stage.py - Visual Specification v1.0 Explanation Stage
Single Focused Stage (800x820px @ x:100 to 900) with Progressive Disclosure.
macOS Dark Chrome, glowing active node, dashed connectors, and 2-line wrapped subtitles.
"""

import math
from typing import List, Dict, Any, Optional


def ease_out_back(t: float, s: float = 1.1) -> float:
    t = max(0.0, min(1.0, t)) - 1.0
    return t * t * ((s + 1.0) * t + s) + 1.0


def render_progressive_stage_svg(
    safe_cx: int,
    header_text: str,
    window_title: str,
    nodes: List[Dict[str, Any]],
    active_index: int,
    t_rel: float,
    duration: float,
    sub_line1: str = "",
    sub_line2: str = ""
) -> str:
    """
    Renders the Single Focused Stage container with progressive disclosure nodes.
    """
    clean_header = header_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").upper()
    clean_win_title = window_title.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    # Stage entrance animation (first 0.5s of scene)
    p_enter = max(0.0, min(1.0, t_rel / 0.5))
    e_enter = ease_out_back(p_enter, s=1.1)
    stage_alpha = p_enter
    stage_y = 430 + (1.0 - e_enter) * 35.0

    # Render up to 3 nodes inside the stage container (width: 800, height: 820)
    node_elements = []
    num_nodes = min(3, len(nodes))
    node_y_positions = [100, 340, 580]

    for idx in range(num_nodes):
        node = nodes[idx]
        is_active = (idx == active_index)
        is_past = (idx < active_index)
        ny = node_y_positions[idx]

        label = node.get("label", f"Node {idx + 1}").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        badge = node.get("badge", "STAGE").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        l1 = node.get("line1", "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        l2 = node.get("line2", "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        accent = node.get("accent", "#22C55E")

        if is_active:
            border = accent
            border_w = "2.5"
            bg = "#1E293B"
            title_color = "#FFFFFF"
            badge_bg = "rgba(34, 197, 94, 0.18)"
            badge_stroke = accent
            badge_color = accent
            glow_filter = f'filter="drop-shadow(0px 0px 10px rgba(34, 197, 94, 0.35))"'
            indicator_bar = f'<rect x="0" y="0" width="8" height="175" rx="4" fill="{accent}"/>'
            status_color = "#38BDF8"
        elif is_past:
            border = "#334155"
            border_w = "1.5"
            bg = "#1E293B"
            title_color = "#CBD5E1"
            badge_bg = "#1E293B"
            badge_stroke = "#475569"
            badge_color = "#94A3B8"
            glow_filter = ""
            indicator_bar = f'<rect x="0" y="0" width="6" height="175" rx="3" fill="#22C55E"/>'
            status_color = "#22C55E"
        else:
            border = "#334155"
            border_w = "1.5"
            bg = "#0F172A"
            title_color = "#94A3B8"
            badge_bg = "#1E293B"
            badge_stroke = "#475569"
            badge_color = "#94A3B8"
            glow_filter = ""
            indicator_bar = ""
            status_color = "#64748B"

        badge_w = max(160, len(badge) * 11 + 28)
        badge_x = 730 - badge_w - 20

        node_svg = f"""
      <!-- Node {idx + 1} ({label}) -->
      <g transform="translate(35, {ny})" {glow_filter}>
        <rect width="730" height="175" rx="16" fill="{bg}" stroke="{border}" stroke-width="{border_w}"/>
        {indicator_bar}
        <text x="32" y="58" font-family="system-ui, -apple-system, Arial, sans-serif" font-size="32" font-weight="800" fill="{title_color}">
          {label}
        </text>
        <rect x="{badge_x}" y="28" width="{badge_w}" height="42" rx="10" fill="{badge_bg}" stroke="{badge_stroke}" stroke-width="1.2"/>
        <text x="{badge_x + badge_w // 2}" y="56" font-family="'SF Mono', Menlo, monospace" font-size="18" font-weight="700" fill="{badge_color}" text-anchor="middle">
          {badge}
        </text>
        <text x="32" y="112" font-family="'SF Mono', Menlo, monospace" font-size="20" fill="#CBD5E1">
          {l1}
        </text>
        <text x="32" y="146" font-family="'SF Mono', Menlo, monospace" font-size="18" fill="{status_color}">
          {l2}
        </text>
      </g>
"""
        node_elements.append(node_svg)

        # Connector to next node
        if idx < num_nodes - 1:
            conn_y1 = ny + 175
            conn_y2 = node_y_positions[idx + 1]
            conn_stroke = "#22C55E" if (idx < active_index or is_active) else "#334155"
            node_elements.append(
                f'<line x1="400" y1="{conn_y1}" x2="400" y2="{conn_y2}" stroke="{conn_stroke}" stroke-width="2.5" stroke-dasharray="6,4"/>'
            )

    nodes_joined = "\n".join(node_elements)

    # Subtitles (2-line wrapped)
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

    svg = f"""
  <!-- Section Category Header -->
  <text x="{safe_cx}" y="380" 
        font-family="system-ui, -apple-system, Arial, sans-serif" 
        font-size="44" font-weight="800" letter-spacing="2" 
        fill="#94A3B8" text-anchor="middle" opacity="{stage_alpha:.3f}">
    {clean_header}
  </text>

  <!-- FOCUSED STAGE CONTAINER (800 x 820 @ x: 100) -->
  <g transform="translate(100, {stage_y:.1f})" opacity="{stage_alpha:.3f}">
    <!-- Stage Frame -->
    <rect width="800" height="820" rx="22" fill="#0B0F19" stroke="#334155" stroke-width="2"/>

    <!-- Window Title Bar -->
    <path d="M 0,22 Q 0,0 22,0 L 778,0 Q 800,0 800,22 L 800,64 L 0,64 Z" fill="#1E293B"/>
    <line x1="0" y1="64" x2="800" y2="64" stroke="#334155" stroke-width="1.5"/>
    <circle cx="36" cy="32" r="7" fill="#EF4444"/>
    <circle cx="62" cy="32" r="7" fill="#F59E0B"/>
    <circle cx="88" cy="32" r="7" fill="#22C55E"/>
    <text x="400" y="39" font-family="'SF Mono', Menlo, Monaco, monospace" font-size="19" fill="#94A3B8" text-anchor="middle">
      {clean_win_title}
    </text>

    {nodes_joined}
  </g>

  {subtitles_svg}
"""
    return svg

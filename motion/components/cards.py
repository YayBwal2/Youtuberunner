from typing import List, Dict, Any, Optional
from motion.layout import LayoutBox
from motion.tokens import HEX_PALETTE


def render_terminal_card_svg(
    box: LayoutBox,
    title: str,
    lines: List[str],
    motion_state: Dict[str, Any]
) -> str:
    """
    Renders macOS / Developer Terminal Window card as clean, scalable SVG.
    Includes titlebar, traffic light buttons, and syntax-highlighted code lines.
    """
    opacity = motion_state.get("opacity", 1.0)
    trans_y = motion_state.get("translate_y", 0.0)
    scale = motion_state.get("scale", 1.0)

    # Box dimensions
    w = box.width
    h = box.height
    cx = box.center_x
    cy = box.center_y

    header_h = 56
    pad_x = 36
    pad_y = 32

    # Traffic light dot coordinates
    c_red_x = 36
    c_yellow_x = 64
    c_green_x = 92
    c_y = header_h // 2

    # Syntax formatted lines
    code_lines_svg = []
    line_y = header_h + pad_y + 16
    line_height = 44

    for line in lines:
        clean_line = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        
        # Syntax coloring heuristic
        if clean_line.startswith("$"):
            # Command line prompt
            prompt_part = '<tspan fill="#22c55e" font-weight="bold">$ </tspan>'
            rest_cmd = clean_line[1:].strip()
            text_svg = f'<tspan fill="#38bdf8">{rest_cmd}</tspan>'
            content = prompt_part + text_svg
        elif "[OK]" in clean_line or "[+]" in clean_line or "[✓]" in clean_line or "[SUCCESS]" in clean_line:
            content = f'<tspan fill="#22c55e" font-weight="bold">{clean_line}</tspan>'
        elif "[!]" in clean_line or "[WARN]" in clean_line:
            content = f'<tspan fill="#f59e0b" font-weight="bold">{clean_line}</tspan>'
        elif "->" in clean_line or "=" in clean_line:
            content = f'<tspan fill="#e2e8f0">{clean_line}</tspan>'
        else:
            content = f'<tspan fill="#94a3b8">{clean_line}</tspan>'

        code_lines_svg.append(
            f'<text x="{pad_x}" y="{line_y}" font-family="SF Mono, Menlo, monospace" '
            f'font-size="28" fill="#e2e8f0">{content}</text>'
        )
        line_y += line_height

    lines_joined = "\n      ".join(code_lines_svg)

    # Matrix transform centered on box
    transform = f'translate({box.x}, {box.y + trans_y}) scale({scale})'
    # Centered scaling transform
    transform_centered = (
        f'translate({cx}, {cy + trans_y}) '
        f'scale({scale}) '
        f'translate({-w // 2}, {-h // 2})'
    )

    svg = f"""
  <g transform="{transform_centered}" opacity="{opacity:.3f}">
    <!-- Drop Shadow Filter -->
    <defs>
      <filter id="card-shadow" x="-10%" y="-10%" width="125%" height="125%">
        <feDropShadow dx="0" dy="16" stdDeviation="24" flood-color="#000000" flood-opacity="0.45"/>
      </filter>
    </defs>

    <!-- Main Window Background -->
    <rect width="{w}" height="{h}" rx="20" ry="20" fill="{HEX_PALETTE['surface']}" 
          stroke="{HEX_PALETTE['border']}" stroke-width="2" filter="url(#card-shadow)"/>

    <!-- Title Bar Header -->
    <path d="M 0 20 Q 0 0 20 0 L {w - 20} 0 Q {w} 0 {w} 20 L {w} {header_h} L 0 {header_h} Z" 
          fill="{HEX_PALETTE['surface_title']}"/>
    <line x1="0" y1="{header_h}" x2="{w}" y2="{header_h}" stroke="{HEX_PALETTE['border']}" stroke-width="1.5"/>

    <!-- Traffic Light Buttons -->
    <circle cx="{c_red_x}" cy="{c_y}" r="8" fill="{HEX_PALETTE['danger']}"/>
    <circle cx="{c_yellow_x}" cy="{c_y}" r="8" fill="{HEX_PALETTE['warning']}"/>
    <circle cx="{c_green_x}" cy="{c_y}" r="8" fill="{HEX_PALETTE['primary']}"/>

    <!-- Window Title -->
    <text x="{w // 2}" y="{c_y + 6}" font-family="SF Pro Text, -apple-system, sans-serif" 
          font-size="20" font-weight="600" fill="{HEX_PALETTE['text_muted']}" text-anchor="middle">
      {title}
    </text>

    <!-- Code Body -->
    <g>
      {lines_joined}
    </g>
  </g>
"""
    return svg

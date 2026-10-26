from typing import List, Dict, Any, Optional
from motion.layout import LayoutBox
from motion.tokens import HEX_PALETTE


def render_architecture_diagram_svg(
    box: LayoutBox,
    nodes: List[Dict[str, str]],
    connections: List[Dict[str, Any]],
    motion_state: Dict[str, Any]
) -> str:
    """
    Renders high-tech developer architecture diagrams (e.g., [GPU Blackwell] -> [1200W Supply] -> [Liquid Loop])
    with sleek glowing connection lines, ports, and animated cards.
    """
    opacity = motion_state.get("opacity", 1.0)
    trans_y = motion_state.get("translate_y", 0.0)
    scale = motion_state.get("scale", 1.0)

    w = box.width
    h = box.height
    cx = box.center_x
    cy = box.center_y

    node_count = len(nodes)
    if node_count == 0:
        return ""

    # Distribute nodes vertically with generous dimensions
    node_w = min(w - 20, 860)
    node_h = 135
    spacing = 36
    total_h = node_count * node_h + (node_count - 1) * spacing
    start_y = (h - total_h) // 2

    node_svgs = []
    line_svgs = []

    for i, node in enumerate(nodes):
        ny = start_y + i * (node_h + spacing)
        nx = (w - node_w) // 2
        
        label = node.get("label", f"Node {i+1}").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        sub = node.get("sub", "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        badge = node.get("badge", "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        accent = node.get("accent", HEX_PALETTE["primary"])

        sub_svg = ""
        if sub:
            sub_svg = f'<text x="32" y="90" font-family="SF Mono, monospace" font-size="20" fill="{HEX_PALETTE["text_muted"]}">{sub}</text>'

        # Node Box
        node_svgs.append(f"""
      <!-- Node {i+1} -->
      <g transform="translate({nx}, {ny})">
        <rect width="{node_w}" height="{node_h}" rx="18" ry="18" fill="{HEX_PALETTE['surface']}" 
              stroke="{accent}" stroke-width="2" opacity="0.95"/>
        <!-- Accent indicator bar -->
        <rect x="0" y="0" width="8" height="{node_h}" rx="4" ry="4" fill="{accent}"/>
        
        <!-- Main Label -->
        <text x="32" y="52" font-family="SF Pro Display, -apple-system, sans-serif" 
              font-size="30" font-weight="700" fill="{HEX_PALETTE['text_white']}">
          {label}
        </text>

        <!-- Sub Description -->
        {sub_svg}

        <!-- Badge -->
        <rect x="{node_w - 180}" y="32" width="150" height="46" rx="23" ry="23" 
              fill="{accent}" fill-opacity="0.15" stroke="{accent}" stroke-width="1.5"/>
        <text x="{node_w - 105}" y="62" font-family="SF Mono, monospace" 
              font-size="20" font-weight="bold" fill="{accent}" text-anchor="middle">
          {badge}
        </text>
      </g>
""")

        # Connector arrow down to next node
        if i < node_count - 1:
            line_x = w // 2
            line_y1 = ny + node_h
            line_y2 = line_y1 + spacing
            line_svgs.append(f"""
      <line x1="{line_x}" y1="{line_y1}" x2="{line_x}" y2="{line_y2}" 
            stroke="{HEX_PALETTE['border']}" stroke-width="3" stroke-dasharray="6,4"/>
      <polygon points="{line_x-6},{line_y2-6} {line_x+6},{line_y2-6} {line_x},{line_y2}" 
               fill="{HEX_PALETTE['primary']}"/>
""")

    transform_centered = (
        f'translate({cx}, {cy + trans_y}) '
        f'scale({scale}) '
        f'translate({-w // 2}, {-h // 2})'
    )

    svg = f"""
  <g transform="{transform_centered}" opacity="{opacity:.3f}">
    <!-- Connectors -->
    {"".join(line_svgs)}
    <!-- Nodes -->
    {"".join(node_svgs)}
  </g>
"""
    return svg

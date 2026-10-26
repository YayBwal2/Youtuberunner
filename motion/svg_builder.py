from typing import List, Dict, Any, Optional
from motion.tokens import (
    REFERENCE_WIDTH,
    REFERENCE_HEIGHT,
    HEX_PALETTE,
    get_safe_area
)
from motion.layout import LayoutEngine
from motion.schema import ComponentType, SemanticSlot
from motion.timeline import TimelineScene
from motion.components.cards import render_terminal_card_svg
from motion.components.typography import render_kinetic_headline_svg, render_active_subtitles_svg
from motion.components.diagrams import render_architecture_diagram_svg


class SVGBuilder:
    """
    Assembles a full-frame 1080x1920 SVG for a single video frame timestamp.
    """
    def __init__(self, width: int = REFERENCE_WIDTH, height: int = REFERENCE_HEIGHT):
        self.width = width
        self.height = height
        self.layout = LayoutEngine(width, height)
        self.safe_area = self.layout.safe_area

    def build_frame_svg(
        self,
        scene: TimelineScene,
        t: float,
        global_duration: float,
        active_chunk: Optional[Dict[str, Any]] = None,
        category: str = "DEEP DIVE"
    ) -> str:
        """
        Builds the complete SVG representation of the frame at global time t.
        """
        sa = self.safe_area
        components_svg: List[str] = []

        # Sort scene components by layer_order
        sorted_components = sorted(scene.components, key=lambda c: c.spec.motion.layer_order)

        for comp in sorted_components:
            motion_state = comp.get_motion_state(t)
            if not motion_state["is_visible"]:
                continue

            spec = comp.spec
            slot_box = self.layout.get_slot_box(spec.slot)

            if spec.type == ComponentType.CODE_TERMINAL:
                title = spec.props.get("title", "main.py")
                lines = spec.props.get("lines", [])
                svg_node = render_terminal_card_svg(slot_box, title, lines, motion_state)
                components_svg.append(svg_node)

            elif spec.type == ComponentType.KINETIC_HEADLINE:
                text = spec.props.get("text", "")
                hl_words = spec.props.get("highlight_words", [])
                svg_node = render_kinetic_headline_svg(slot_box, text, hl_words, motion_state)
                components_svg.append(svg_node)

            elif spec.type == ComponentType.ARCHITECTURE_DIAGRAM:
                nodes = spec.props.get("nodes", [])
                connections = spec.props.get("connections", [])
                svg_node = render_architecture_diagram_svg(slot_box, nodes, connections, motion_state)
                components_svg.append(svg_node)

        # 3. Active subtitles in bottom ticker slot
        ticker_box = self.layout.get_slot_box(SemanticSlot.TICKER_BOTTOM)
        subtitles_svg = render_active_subtitles_svg(ticker_box, active_chunk, t)

        # 4. Global Progress Bar (y = 1910)
        progress = max(0.0, min(1.0, t / max(0.1, global_duration)))
        progress_w = int(self.width * progress)

        # Dot matrix grid background
        dot_elements = []
        for gx in range(40, self.width, 50):
            for gy in range(40, self.height, 50):
                dot_elements.append(f'<circle cx="{gx}" cy="{gy}" r="1.5" fill="{HEX_PALETTE["dot_matrix"]}"/>')
        dots_svg = "\n    ".join(dot_elements)

        full_svg = f"""<svg xmlns="http://www.w3.org/2000/svg" 
     width="{self.width}" height="{self.height}" viewBox="0 0 {self.width} {self.height}">
  <!-- Background Canvas -->
  <rect width="{self.width}" height="{self.height}" fill="{HEX_PALETTE['bg_slate']}"/>
  
  <!-- Dot Matrix Grid -->
  <g opacity="0.8">
    {dots_svg}
  </g>

  <!-- Category Pill Badge (Top Safe Area) -->
  <g transform="translate({sa.center_x}, {sa.y - 40})">
    <rect x="-90" y="-18" width="180" height="36" rx="18" ry="18" 
          fill="{HEX_PALETTE['surface_title']}" stroke="{HEX_PALETTE['border']}" stroke-width="1.5"/>
    <circle cx="-65" cy="0" r="4" fill="{HEX_PALETTE['primary']}"/>
    <text x="-48" y="5" font-family="SF Mono, monospace" font-size="16" font-weight="bold" 
          fill="{HEX_PALETTE['primary']}" letter-spacing="1.5px">{category}</text>
  </g>

  <!-- Render Scene Components -->
  {"".join(components_svg)}

  <!-- Kinetic Subtitles -->
  {subtitles_svg}

  <!-- Bottom Timeline Progress Bar -->
  <rect x="0" y="{self.height - 8}" width="{self.width}" height="8" fill="{HEX_PALETTE['progress_bg']}"/>
  <rect x="0" y="{self.height - 8}" width="{progress_w}" height="8" fill="{HEX_PALETTE['progress_fill']}"/>
</svg>"""
        return full_svg

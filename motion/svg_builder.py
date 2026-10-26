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
from motion.components.hook_hero import render_hook_hero_svg
from motion.components.progressive_stage import render_progressive_stage_svg
from motion.components.verdict_card import render_verdict_card_svg


class SVGBuilder:
    """
    Assembles a full-frame 1080x1920 SVG for a single video frame timestamp.
    Fully supports Visual Specification v1.0 Scene Archetypes:
    - Hook Typo Hero (Fullscreen 104px display + Neon Pill Box)
    - Single Focused Stage (macOS Dark Chrome + Progressive Disclosure Nodes)
    - Payoff Verdict Card (Hero Metric + Loop Anchor CTA)
    And legacy component fallback.
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
        t_rel = max(0.0, t - scene.start_time)
        scene_dur = max(0.1, scene.duration)

        components_svg: List[str] = []
        is_hook_scene = False
        suppress_subtitles = False

        # Sort scene components by layer_order
        sorted_components = sorted(scene.components, key=lambda c: c.spec.motion.layer_order)

        for comp in sorted_components:
            spec = comp.spec
            props = spec.props

            # 1. Visual Specification v1.0 Archetypes
            if spec.type == ComponentType.HOOK_TYPO_HERO:
                is_hook_scene = True
                suppress_subtitles = True
                svg_node = render_hook_hero_svg(
                    safe_cx=sa.center_x,
                    line1=props.get("line1", "TECH BREAKTHROUGH"),
                    line2=props.get("line2", ""),
                    pill_text=props.get("pill_text", "MUST SEE"),
                    t_rel=t_rel,
                    duration=scene_dur,
                    accent_color=props.get("accent_color", "#22C55E")
                )
                components_svg.append(svg_node)

            elif spec.type == ComponentType.PROGRESSIVE_STAGE:
                # Calculate active node index based on progression through scene
                nodes = props.get("nodes", [])
                num_nodes = max(1, len(nodes))
                node_prog = min(num_nodes - 1, int((t_rel / scene_dur) * num_nodes))
                
                # Format 2-line subtitles from active_chunk
                sub_l1 = ""
                sub_l2 = ""
                if active_chunk and "words" in active_chunk:
                    words = [w.get("raw", "") for w in active_chunk["words"]]
                    if len(words) <= 2:
                        sub_l1 = " ".join(words)
                    else:
                        mid = len(words) // 2
                        sub_l1 = " ".join(words[:mid])
                        sub_l2 = " ".join(words[mid:])

                svg_node = render_progressive_stage_svg(
                    safe_cx=sa.center_x,
                    header_text=props.get("header_text", "SYSTEM ARCHITECTURE"),
                    window_title=props.get("window_title", "architecture.sys"),
                    nodes=nodes,
                    active_index=node_prog,
                    t_rel=t_rel,
                    duration=scene_dur,
                    sub_line1=props.get("sub_line1", sub_l1),
                    sub_line2=props.get("sub_line2", sub_l2)
                )
                components_svg.append(svg_node)
                suppress_subtitles = True  # Rendered inside progressive_stage

            elif spec.type == ComponentType.PAYOFF_VERDICT_CARD:
                sub_l1 = ""
                sub_l2 = ""
                if active_chunk and "words" in active_chunk:
                    words = [w.get("raw", "") for w in active_chunk["words"]]
                    if len(words) <= 2:
                        sub_l1 = " ".join(words)
                    else:
                        mid = len(words) // 2
                        sub_l1 = " ".join(words[:mid])
                        sub_l2 = " ".join(words[mid:])

                svg_node = render_verdict_card_svg(
                    safe_cx=sa.center_x,
                    category_text=props.get("category_text", "FINAL VERDICT"),
                    verified_badge=props.get("verified_badge", "[OK] 100% VERIFIED"),
                    hero_metric=props.get("hero_metric", "VERIFIED"),
                    metric_subtitle=props.get("metric_subtitle", "TEST RESULTS"),
                    second_metric=props.get("second_metric", "READY"),
                    second_subtitle=props.get("second_subtitle", "DEPLOY NOW"),
                    loop_anchor_question=props.get("loop_anchor_question", "What do you think?"),
                    loop_anchor_cta=props.get("loop_anchor_cta", "COMMENT BELOW"),
                    t_rel=t_rel,
                    duration=scene_dur,
                    sub_line1=props.get("sub_line1", sub_l1),
                    sub_line2=props.get("sub_line2", sub_l2)
                )
                components_svg.append(svg_node)
                suppress_subtitles = True  # Rendered inside verdict_card

            # 2. Legacy Components Fallback
            else:
                motion_state = comp.get_motion_state(t)
                if not motion_state["is_visible"]:
                    continue
                slot_box = self.layout.get_slot_box(spec.slot)

                if spec.type == ComponentType.CODE_TERMINAL:
                    title = props.get("title", "main.py")
                    lines = props.get("lines", [])
                    svg_node = render_terminal_card_svg(slot_box, title, lines, motion_state)
                    components_svg.append(svg_node)

                elif spec.type == ComponentType.KINETIC_HEADLINE:
                    text = props.get("text", "")
                    hl_words = props.get("highlight_words", [])
                    svg_node = render_kinetic_headline_svg(slot_box, text, hl_words, motion_state)
                    components_svg.append(svg_node)

                elif spec.type == ComponentType.ARCHITECTURE_DIAGRAM:
                    nodes = props.get("nodes", [])
                    connections = props.get("connections", [])
                    svg_node = render_architecture_diagram_svg(slot_box, nodes, connections, motion_state)
                    components_svg.append(svg_node)

        # 3. Subtitles (render ticker only if not suppressed by v1.0 archetypes)
        subtitles_svg = ""
        if not suppress_subtitles:
            ticker_box = self.layout.get_slot_box(SemanticSlot.TICKER_BOTTOM)
            subtitles_svg = render_active_subtitles_svg(ticker_box, active_chunk, t)

        # 4. Global Progress Bar (y = 1912)
        progress = max(0.0, min(1.0, t / max(0.1, global_duration)))
        progress_w = int(self.width * progress)

        # Dot matrix grid background
        dot_elements = []
        for gx in range(40, self.width, 50):
            for gy in range(40, self.height, 50):
                dot_elements.append(f'<circle cx="{gx}" cy="{gy}" r="1.5" fill="{HEX_PALETTE["dot_matrix"]}"/>')
        dots_svg = "\n    ".join(dot_elements)

        # Category pill at top (hide during hook for maximum typography punch)
        category_header_svg = ""
        if not is_hook_scene:
            category_header_svg = f"""
  <g transform="translate({sa.center_x}, {sa.y - 40})">
    <rect x="-90" y="-18" width="180" height="36" rx="18" ry="18" 
          fill="{HEX_PALETTE['surface_title']}" stroke="{HEX_PALETTE['border']}" stroke-width="1.5"/>
    <circle cx="-65" cy="0" r="4" fill="{HEX_PALETTE['primary']}"/>
    <text x="-48" y="5" font-family="SF Mono, monospace" font-size="16" font-weight="bold" 
          fill="{HEX_PALETTE['primary']}" letter-spacing="1.5px">{category}</text>
  </g>
"""

        full_svg = f"""<svg xmlns="http://www.w3.org/2000/svg" 
     width="{self.width}" height="{self.height}" viewBox="0 0 {self.width} {self.height}">
  <defs>
    <radialGradient id="bgGlow" cx="46%" cy="48%" r="65%">
      <stop offset="0%" stop-color="#1E293B" stop-opacity="0.6"/>
      <stop offset="100%" stop-color="#090D16" stop-opacity="1.0"/>
    </radialGradient>
  </defs>

  <!-- Background Canvas -->
  <rect width="{self.width}" height="{self.height}" fill="url(#bgGlow)"/>
  
  <!-- Dot Matrix Grid -->
  <g opacity="0.6">
    {dots_svg}
  </g>

  {category_header_svg}

  <!-- Render Scene Components -->
  {"".join(components_svg)}

  <!-- Kinetic Subtitles -->
  {subtitles_svg}

  <!-- Bottom Timeline Progress Bar -->
  <rect x="0" y="{self.height - 8}" width="{self.width}" height="8" fill="{HEX_PALETTE['progress_bg']}"/>
  <rect x="0" y="{self.height - 8}" width="{progress_w}" height="8" fill="{HEX_PALETTE['progress_fill']}"/>
</svg>"""
        return full_svg

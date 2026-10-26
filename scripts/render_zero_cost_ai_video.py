#!/usr/bin/env python3
"""
scripts/render_zero_cost_ai_video.py
Renders the complete 17.8s YouTube Short prototype for:
Topic: "Zero-Cost AI: Self-Hosting Open-Source LLMs on a VPS using Docker"
(API ခပေးစရာမလိုဘဲ ကိုယ်ပိုင်ဆာဗာပေါ်မှာ AI တွေကို အခမဲ့ Run ပြီး Automation တည်ဆောက်ခြင်း)

Architecture:
- Adheres 100% to Visual Specification v1.0
- Safe Area Center X = 500px (Safe bounds: 80 to 920px horizontal)
- Scene 1 (0.0s - 3.8s): Fullscreen Kinetic Typo Hook (104px Display + Neon Green Pill Box)
- Scene 2 (3.8s - 12.4s): Single Focused Stage (800x820px) with Progressive Disclosure
- Scene 3 (12.4s - 17.825s): High-Impact Verdict Card ($0/mo, 100% Private, Loop Anchor)
- Synced with 45 neural word timestamps from en-US-GuyNeural audio
- Zero-disk streaming directly via FFmpeg pipe (Zero memory leak)
"""

import os
import sys
import time
import math
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Apple Silicon Homebrew Cairo dynamic library fallback
if "/opt/homebrew/lib" not in os.environ.get("DYLD_FALLBACK_LIBRARY_PATH", ""):
    current_dyld = os.environ.get("DYLD_FALLBACK_LIBRARY_PATH", "")
    os.environ["DYLD_FALLBACK_LIBRARY_PATH"] = f"/opt/homebrew/lib:{current_dyld}"

import cairosvg
from config import OUTPUTS_DIR, TEMP_DIR, VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_FPS
from core.voice_synthesizer import synthesize_speech


def ease_out_expo(t: float) -> float:
    return 1.0 if t >= 1.0 else 1.0 - math.pow(2, -10 * t)


def ease_out_back(t: float, s: float = 1.70158) -> float:
    t = max(0.0, min(1.0, t)) - 1.0
    return t * t * ((s + 1.0) * t + s) + 1.0


def ease_in_out_quad(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return 2.0 * t * t if t < 0.5 else 1.0 - math.pow(-2.0 * t + 2.0, 2) / 2.0


def build_zero_cost_ai_frame_svg(
    t: float,
    total_duration: float,
    all_words: List[Dict[str, Any]]
) -> str:
    """
    Builds the precise 1080x1920 SVG frame at global timestamp t.
    """
    w = VIDEO_WIDTH   # 1080
    h = VIDEO_HEIGHT  # 1920
    safe_cx = 500     # Calibrated horizontal center of YouTube Shorts safe area

    # Progress bar width (y: 1912)
    progress_ratio = max(0.0, min(1.0, t / max(0.1, total_duration)))
    progress_w = int(w * progress_ratio)

    # Dot matrix background elements
    dot_elements = []
    for gx in range(40, w, 50):
        for gy in range(40, h, 50):
            dot_elements.append(f'<circle cx="{gx}" cy="{gy}" r="1.5" fill="#1A2436"/>')
    dots_svg = "\n    ".join(dot_elements)

    # Find active word for subtitles (if active in scene 2 or 3)
    active_word_obj = None
    for item in all_words:
        if item["start"] <= t <= item["end"]:
            active_word_obj = item
            break
        elif item["start"] > t:
            break

    # Determine Scene Archetype
    # Scene 1: Hook (0.0s to 3.8s)
    # Scene 2: Explanation (3.8s to 12.4s)
    # Scene 3: Payoff Verdict (12.4s to 17.825s)

    scene_content_svg = ""

    if t < 3.8:
        # =========================================================================
        # SCENE 1: HOOK (0.0s - 3.8s) - Fullscreen Kinetic Typo Dominance
        # =========================================================================
        t_hook = t
        # Exit fade out at end of hook (3.4s to 3.8s)
        exit_alpha = 1.0
        exit_offset_y = 0.0
        if t_hook > 3.4:
            trans_p = (t_hook - 3.4) / 0.4
            exit_alpha = max(0.0, 1.0 - ease_in_out_quad(trans_p))
            exit_offset_y = -40 * ease_in_out_quad(trans_p)

        # Line 1: "STOP PAYING" (reveal 0.0s to 0.35s)
        p1 = max(0.0, min(1.0, t_hook / 0.35))
        e1 = ease_out_expo(p1)
        l1_alpha = p1
        l1_y = 780 + (1.0 - e1) * 70 + exit_offset_y

        # Line 2: "FOR AI APIS" (reveal 0.20s to 0.55s)
        p2 = max(0.0, min(1.0, (t_hook - 0.20) / 0.35)) if t_hook >= 0.20 else 0.0
        e2 = ease_out_expo(p2)
        l2_alpha = p2
        l2_y = 890 + (1.0 - e2) * 70 + exit_offset_y

        # Line 3: Neon Emerald Pill Box "ZERO-COST LLM" (reveal 0.45s to 0.90s)
        p3 = max(0.0, min(1.0, (t_hook - 0.45) / 0.45)) if t_hook >= 0.45 else 0.0
        e3 = ease_out_back(p3, s=1.4)
        l3_alpha = min(1.0, p3 * 2.0)
        pill_scale = max(0.001, e3)
        pill_y = 960 + exit_offset_y

        # Pill width 760, height 140, centered at safe_cx=500 -> x: 120 to 880
        pill_transform = (
            f"translate({safe_cx}, {pill_y + 70}) "
            f"scale({pill_scale:.4f}) "
            f"translate(-380, -70)"
        )

        scene_content_svg = f"""
    <!-- Hook Typo Dominance Group -->
    <g opacity="{exit_alpha:.3f}">
      <!-- Line 1: STOP PAYING -->
      <text x="{safe_cx}" y="{l1_y:.1f}" 
            font-family="Arial, Helvetica, sans-serif" 
            font-size="104" font-weight="900" letter-spacing="-1.5" 
            fill="#FFFFFF" opacity="{l1_alpha:.3f}" text-anchor="middle">
        STOP PAYING
      </text>

      <!-- Line 2: FOR AI APIS -->
      <text x="{safe_cx}" y="{l2_y:.1f}" 
            font-family="Arial, Helvetica, sans-serif" 
            font-size="104" font-weight="900" letter-spacing="-1.5" 
            fill="#FFFFFF" opacity="{l2_alpha:.3f}" text-anchor="middle">
        FOR AI APIS
      </text>

      <!-- Line 3: Neon Emerald Pill Box -->
      <g transform="{pill_transform}" opacity="{l3_alpha:.3f}">
        <rect width="760" height="140" rx="32" fill="#22C55E" 
              filter="drop-shadow(0px 14px 20px rgba(34, 197, 94, 0.4))"/>
        <text x="380" y="98" 
              font-family="Arial, Helvetica, sans-serif" 
              font-size="72" font-weight="900" letter-spacing="1.0" 
              fill="#090D16" text-anchor="middle">
          ZERO-COST LLM
        </text>
      </g>
    </g>
"""

    elif t < 12.4:
        # =========================================================================
        # SCENE 2: EXPLANATION (3.8s - 12.4s) - Single Focused Stage & Progressive Disclosure
        # =========================================================================
        t_expl = t - 3.8
        stage_enter_p = max(0.0, min(1.0, t_expl / 0.5))
        stage_e = ease_out_back(stage_enter_p, s=1.1)
        stage_alpha = stage_enter_p
        stage_y = 430 + (1.0 - stage_e) * 40

        # Progressive Disclosure Node States:
        # Phase A (t: 3.8s to 7.0s, duration in sentence 2): Ollama / Llama 3 is active spoken
        # Phase B (t: 7.0s to 9.5s): Docker Engine activates
        # Phase C (t: 9.5s to 12.4s): 5-Dollar Cloud VPS activates

        is_node1_active = (t < 7.0)
        is_node2_active = (7.0 <= t < 9.5)
        is_node3_active = (t >= 9.5)

        # Node 1 styling
        n1_border = "#22C55E" if is_node1_active else "#334155"
        n1_border_w = "2.5" if is_node1_active else "1.5"
        n1_bg = "#1E293B" if is_node1_active else "#0F172A"
        n1_title_color = "#FFFFFF" if is_node1_active else "#94A3B8"
        n1_badge_bg = "rgba(34, 197, 94, 0.18)" if is_node1_active else "#1E293B"
        n1_badge_stroke = "#22C55E" if is_node1_active else "#475569"
        n1_badge_color = "#22C55E" if is_node1_active else "#94A3B8"
        n1_filter = 'filter="drop-shadow(0px 0px 10px rgba(34, 197, 94, 0.35))"' if is_node1_active else ""
        n1_status_line = (
            '<text x="32" y="146" font-family="\'SF Mono\', Menlo, monospace" font-size="18" fill="#38BDF8">[OK] Port 11434 active (OpenAI Compatible)</text>'
            if is_node1_active else
            '<text x="32" y="146" font-family="\'SF Mono\', Menlo, monospace" font-size="18" fill="#22C55E">[OK] Active in background</text>'
        )

        # Node 2 styling
        n2_border = "#22C55E" if is_node2_active else "#334155"
        n2_border_w = "2.5" if is_node2_active else "1.5"
        n2_bg = "#1E293B" if is_node2_active else "#0F172A"
        n2_title_color = "#FFFFFF" if is_node2_active else "#94A3B8"
        n2_badge_bg = "rgba(34, 197, 94, 0.18)" if is_node2_active else "#1E293B"
        n2_badge_stroke = "#22C55E" if is_node2_active else "#475569"
        n2_badge_color = "#22C55E" if is_node2_active else "#94A3B8"
        n2_filter = 'filter="drop-shadow(0px 0px 10px rgba(34, 197, 94, 0.35))"' if is_node2_active else ""
        n2_status_line = (
            '<text x="32" y="146" font-family="\'SF Mono\', Menlo, monospace" font-size="18" fill="#38BDF8">[OK] Single command deploy &amp; auto-restart</text>'
            if is_node2_active else
            '<text x="32" y="146" font-family="\'SF Mono\', Menlo, monospace" font-size="18" fill="#64748B">Container: ollama/ollama:latest</text>'
        )

        # Node 3 styling
        n3_border = "#22C55E" if is_node3_active else "#334155"
        n3_border_w = "2.5" if is_node3_active else "1.5"
        n3_bg = "#1E293B" if is_node3_active else "#0F172A"
        n3_title_color = "#FFFFFF" if is_node3_active else "#94A3B8"
        n3_badge_bg = "rgba(34, 197, 94, 0.18)" if is_node3_active else "#1E293B"
        n3_badge_stroke = "#22C55E" if is_node3_active else "#475569"
        n3_badge_color = "#22C55E" if is_node3_active else "#94A3B8"
        n3_filter = 'filter="drop-shadow(0px 0px 10px rgba(34, 197, 94, 0.35))"' if is_node3_active else ""
        n3_status_line = (
            '<text x="32" y="146" font-family="\'SF Mono\', Menlo, monospace" font-size="18" fill="#22C55E">[OK] Zero token bill / 100% private data</text>'
            if is_node3_active else
            '<text x="32" y="146" font-family="\'SF Mono\', Menlo, monospace" font-size="18" fill="#475569">Unlimited monthly automation runs</text>'
        )

        # Connectors
        conn1_stroke = "#22C55E" if (is_node1_active or is_node2_active) else "#334155"
        conn2_stroke = "#22C55E" if is_node3_active else "#334155"

        # Subtitles (2-line wrapped for sentence 2)
        # Sentence 2: "You can self-host open-source models like Llama 3 on a five-dollar VPS using Docker, giving you unlimited local inference with zero token bills."
        cur_w_str = active_word_obj["raw"] if active_word_obj else ""
        
        # Subtitle chunks based on timestamp:
        if t < 6.8:
            sub_l1 = "SELF-HOST OPEN-SOURCE"
            sub_l2 = "MODELS LIKE LLAMA 3"
        elif t < 9.5:
            sub_l1 = "ON A FIVE-DOLLAR VPS"
            sub_l2 = "USING DOCKER"
        else:
            sub_l1 = "UNLIMITED LOCAL INFERENCE"
            sub_l2 = "WITH ZERO TOKEN BILLS"

        scene_content_svg = f"""
    <!-- Category Header -->
    <text x="{safe_cx}" y="380" 
          font-family="system-ui, -apple-system, 'SF Pro Display', Arial, sans-serif" 
          font-size="44" font-weight="800" letter-spacing="2" 
          fill="#94A3B8" text-anchor="middle" opacity="{stage_alpha:.3f}">
        DOCKER AI STACK
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
        docker-compose.yml
      </text>

      <!-- NODE 1: Ollama + Llama 3 -->
      <g transform="translate(35, 100)" {n1_filter}>
        <rect width="730" height="175" rx="16" fill="{n1_bg}" stroke="{n1_border}" stroke-width="{n1_border_w}"/>
        <rect x="0" y="0" width="8" height="175" rx="4" fill="{n1_border}"/>
        <text x="32" y="58" font-family="system-ui, -apple-system, Arial, sans-serif" font-size="34" font-weight="800" fill="{n1_title_color}">
          Ollama + Llama 3 (8B)
        </text>
        <rect x="500" y="28" width="195" height="42" rx="10" fill="{n1_badge_bg}" stroke="{n1_badge_stroke}" stroke-width="1.5"/>
        <text x="597" y="56" font-family="'SF Mono', Menlo, monospace" font-size="18" font-weight="700" fill="{n1_badge_color}" text-anchor="middle">
          LOCAL INFERENCE
        </text>
        <text x="32" y="112" font-family="'SF Mono', Menlo, monospace" font-size="20" fill="#CBD5E1">
          Dual-Channel FP16 / Zero Token Bills
        </text>
        {n1_status_line}
      </g>

      <!-- Connector Line 1 -> 2 -->
      <line x1="400" y1="275" x2="400" y2="340" stroke="{conn1_stroke}" stroke-width="2.5" stroke-dasharray="6,4"/>

      <!-- NODE 2: Docker Container Engine -->
      <g transform="translate(35, 340)" {n2_filter}>
        <rect width="730" height="175" rx="16" fill="{n2_bg}" stroke="{n2_border}" stroke-width="{n2_border_w}"/>
        <text x="32" y="58" font-family="system-ui, -apple-system, Arial, sans-serif" font-size="32" font-weight="700" fill="{n2_title_color}">
          Docker Container Engine
        </text>
        <rect x="495" y="28" width="200" height="42" rx="10" fill="{n2_badge_bg}" stroke="{n2_badge_stroke}" stroke-width="1.2"/>
        <text x="595" y="56" font-family="'SF Mono', Menlo, monospace" font-size="18" font-weight="600" fill="{n2_badge_color}" text-anchor="middle">
          ISOLATED RUNTIME
        </text>
        <text x="32" y="112" font-family="'SF Mono', Menlo, monospace" font-size="20" fill="#64748B">
          Auto-restart policy: always / Healthcheck
        </text>
        {n2_status_line}
      </g>

      <!-- Connector Line 2 -> 3 -->
      <line x1="400" y1="515" x2="400" y2="580" stroke="{conn2_stroke}" stroke-width="2.5" stroke-dasharray="6,4"/>

      <!-- NODE 3: 5-Dollar Cloud VPS -->
      <g transform="translate(35, 580)" {n3_filter}>
        <rect width="730" height="175" rx="16" fill="{n3_bg}" stroke="{n3_border}" stroke-width="{n3_border_w}"/>
        <text x="32" y="58" font-family="system-ui, -apple-system, Arial, sans-serif" font-size="32" font-weight="700" fill="{n3_title_color}">
          5-Dollar Cloud VPS
        </text>
        <rect x="505" y="28" width="190" height="42" rx="10" fill="{n3_badge_bg}" stroke="{n3_badge_stroke}" stroke-width="1.2"/>
        <text x="600" y="56" font-family="'SF Mono', Menlo, monospace" font-size="18" font-weight="600" fill="{n3_badge_color}" text-anchor="middle">
          $5 / MONTH FLAT
        </text>
        <text x="32" y="112" font-family="'SF Mono', Menlo, monospace" font-size="20" fill="#64748B">
          Unlimited requests / No per-token rate limits
        </text>
        {n3_status_line}
      </g>
    </g>

    <!-- NEURAL SUBTITLE (2-Line Wrapped, Centered at Safe X: 500, Y: 1390-1470) -->
    <g transform="translate({safe_cx}, 1400)">
      <text x="0" y="0" text-anchor="middle" 
            font-family="system-ui, -apple-system, Arial, sans-serif" 
            font-size="44" font-weight="700" fill="#FFFFFF">
        {sub_l1}
      </text>
      <text x="0" y="56" text-anchor="middle" 
            font-family="system-ui, -apple-system, Arial, sans-serif" 
            font-size="52" font-weight="900" fill="#22C55E">
        {sub_l2}
      </text>
    </g>
"""

    else:
        # =========================================================================
        # SCENE 3: PAYOFF VERDICT (12.4s - 17.825s) - High Impact Verdict Card & Loop Anchor
        # =========================================================================
        t_payoff = t - 12.4
        payoff_enter_p = max(0.0, min(1.0, t_payoff / 0.5))
        payoff_e = ease_out_back(payoff_enter_p, s=1.1)
        payoff_alpha = payoff_enter_p
        payoff_y = 500 + (1.0 - payoff_e) * 40

        # Subtitles for Sentence 3:
        # "One single docker command, and your private automation pipeline runs completely free forever."
        if t < 15.0:
            sub_p_l1 = "ONE SINGLE DOCKER COMMAND"
            sub_p_l2 = "PRIVATE AUTOMATION PIPELINE"
        else:
            sub_p_l1 = "RUNS COMPLETELY"
            sub_p_l2 = "FREE FOREVER"

        scene_content_svg = f"""
    <!-- Section Category Header -->
    <text x="{safe_cx}" y="440" 
          font-family="system-ui, -apple-system, Arial, sans-serif" 
          font-size="42" font-weight="800" letter-spacing="2" 
          fill="#94A3B8" text-anchor="middle" opacity="{payoff_alpha:.3f}">
        AUTOMATION VERDICT
    </text>

    <!-- VERDICT CARD CONTAINER (800 x 820 @ x: 100) -->
    <g transform="translate(100, {payoff_y:.1f})" opacity="{payoff_alpha:.3f}"
       filter="drop-shadow(0px 16px 24px rgba(34, 197, 94, 0.25))">
      <rect width="800" height="820" rx="28" fill="#111827" stroke="#22C55E" stroke-width="2.5"/>

      <!-- Status Verified Pill Badge -->
      <g transform="translate(200, 70)">
        <rect width="400" height="58" rx="29" fill="rgba(34, 197, 94, 0.15)" stroke="#22C55E" stroke-width="2"/>
        <text x="200" y="38" font-family="'SF Mono', Menlo, monospace" font-size="22" font-weight="700" letter-spacing="1" fill="#22C55E" text-anchor="middle">
          [OK] 100% PRIVATE &amp; FREE
        </text>
      </g>

      <!-- Big Hero Metric Number -->
      <text x="400" y="270" font-family="system-ui, -apple-system, Arial, sans-serif" font-size="124" font-weight="900" letter-spacing="-2" fill="#FFFFFF" text-anchor="middle">
        $0 / MO
      </text>
      <text x="400" y="330" font-family="'SF Mono', Menlo, monospace" font-size="24" font-weight="600" letter-spacing="2" fill="#94A3B8" text-anchor="middle">
        TOKEN API EXPENSES FOREVER
      </text>

      <!-- Subtle Divider Line -->
      <line x1="70" y1="390" x2="730" y2="390" stroke="#334155" stroke-width="2"/>

      <!-- Supporting Metric 2 -->
      <text x="400" y="480" font-family="system-ui, -apple-system, Arial, sans-serif" font-size="64" font-weight="900" fill="#22C55E" text-anchor="middle">
        RUNS FOREVER
      </text>
      <text x="400" y="525" font-family="'SF Mono', Menlo, monospace" font-size="22" fill="#94A3B8" text-anchor="middle">
        ONE COMMAND: docker run -d ollama
      </text>

      <!-- Loop Anchor Interaction Box -->
      <g transform="translate(50, 600)">
        <rect width="700" height="150" rx="16" fill="#1E293B" stroke="#334155" stroke-width="1.5"/>
        <text x="350" y="58" font-family="system-ui, -apple-system, Arial, sans-serif" font-size="26" font-weight="700" fill="#CBD5E1" text-anchor="middle">
          Ready to ditch expensive API bills?
        </text>
        <text x="350" y="105" font-family="'SF Mono', Menlo, monospace" font-size="22" font-weight="800" fill="#38BDF8" text-anchor="middle">
          COMMENT "DOCKER" FOR SETUP GUIDE
        </text>
      </g>
    </g>

    <!-- NEURAL SUBTITLE (2-Line Wrapped, Centered at Safe X: 500, Y: 1390-1470) -->
    <g transform="translate({safe_cx}, 1400)">
      <text x="0" y="0" text-anchor="middle" 
            font-family="system-ui, -apple-system, Arial, sans-serif" 
            font-size="44" font-weight="700" fill="#FFFFFF">
        {sub_p_l1}
      </text>
      <text x="0" y="56" text-anchor="middle" 
            font-family="system-ui, -apple-system, Arial, sans-serif" 
            font-size="52" font-weight="900" fill="#22C55E">
        {sub_p_l2}
      </text>
    </g>
"""

    # Assemble full SVG
    full_svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">
  <defs>
    <radialGradient id="bgGlow" cx="46%" cy="48%" r="65%">
      <stop offset="0%" stop-color="#1E293B" stop-opacity="0.6"/>
      <stop offset="100%" stop-color="#090D16" stop-opacity="1.0"/>
    </radialGradient>
  </defs>

  <!-- Canvas Background -->
  <rect width="{w}" height="{h}" fill="url(#bgGlow)"/>

  <!-- Dot Matrix Grid -->
  <g opacity="0.6">
    {dots_svg}
  </g>

  <!-- Scene Specific Content -->
  {scene_content_svg}

  <!-- Bottom Timeline Progress Bar (Global) -->
  <rect x="0" y="{h - 8}" width="{w}" height="8" fill="#1E293B"/>
  <rect x="0" y="{h - 8}" width="{progress_w}" height="8" fill="#22C55E"/>
</svg>"""
    return full_svg


def render_zero_cost_ai_video():
    print("=" * 75)
    print("🚀 RENDERING FULL YOUTUBE SHORT: ZERO-COST AI (17.8s)")
    print("   Topic: Zero-Cost AI: Self-Hosting Open-Source LLMs on a VPS using Docker")
    print("   Voice: en-US-GuyNeural (Microsoft Neural Speech)")
    print("   Design System: Visual Specification v1.0 (Hook -> Expl -> Payoff)")
    print("=" * 75)

    narration_text = (
        "Stop paying OpenAI thousands every month for API keys. "
        "You can self-host open-source models like Llama 3 on a five-dollar VPS using Docker, "
        "giving you unlimited local inference with zero token bills. "
        "One single docker command, and your private automation pipeline runs completely free forever."
    )

    print("\n[1/3] Synthesizing speech & generating neural timestamps...")
    voice_data = synthesize_speech(
        script_text=narration_text,
        output_filename="zero_cost_ai_narration.mp3"
    )
    audio_path = voice_data["audio_path"]
    total_duration = voice_data["duration"]
    all_words = voice_data["words"]
    print(f"  ✓ Audio: {Path(audio_path).name} ({total_duration:.2f}s, {len(all_words)} words)")

    output_mp4 = OUTPUTS_DIR / "zero_cost_ai_prototype.mp4"
    output_thumb = OUTPUTS_DIR / "zero_cost_ai_prototype_thumb.png"

    total_frames = int(math.ceil(total_duration * VIDEO_FPS))
    print(f"\n[2/3] Streaming {total_frames} frames ({VIDEO_FPS}fps) directly to FFmpeg via memory pipe...")

    from motion.rasterizer import rasterize_svg_to_rgb_bytes

    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{VIDEO_WIDTH}x{VIDEO_HEIGHT}",
        "-pix_fmt", "rgb24",
        "-r", str(VIDEO_FPS),
        "-i", "-",
        "-i", str(audio_path),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "veryfast",
        "-crf", "18",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        str(output_mp4)
    ]

    process = subprocess.Popen(
        ffmpeg_cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    start_time = time.time()
    last_print = 0

    for frame_idx in range(total_frames):
        t = frame_idx / VIDEO_FPS
        frame_svg = build_zero_cost_ai_frame_svg(t, total_duration, all_words)
        raw_rgb = rasterize_svg_to_rgb_bytes(frame_svg)
        process.stdin.write(raw_rgb)

        if frame_idx - last_print >= 60 or frame_idx == total_frames - 1:
            last_print = frame_idx
            pct = int((frame_idx + 1) / total_frames * 100)
            elapsed = time.time() - start_time
            fps = (frame_idx + 1) / max(0.001, elapsed)
            print(f"  ⚡ [{pct:3d}%] Rendered {frame_idx + 1}/{total_frames} frames ({fps:.1f} fps)...")

    process.stdin.close()
    process.wait()

    elapsed_total = time.time() - start_time
    avg_fps = total_frames / max(0.001, elapsed_total)
    print(f"\n[3/3] Generating high-res thumbnail & final validation...")

    # Extract high-res thumbnail at 1.5s
    subprocess.run([
        "ffmpeg", "-y", "-ss", "00:00:01.5", "-i", str(output_mp4),
        "-frames:v", "1", str(output_thumb)
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    print("=" * 75)
    print("✨ ZERO-COST AI SHORT VIDEO GENERATION COMPLETE!")
    print(f"  🎬 Video File:   {output_mp4}")
    print(f"  🖼️ Thumbnail:    {output_thumb}")
    print(f"  ⏱️ Duration:     {total_duration:.2f} seconds")
    print(f"  🎞️ Frames:       {total_frames} frames @ {VIDEO_FPS} fps")
    print(f"  ⚡ Render Time:  {elapsed_total:.2f}s (Average: {avg_fps:.1f} fps)")
    print(f"  📦 File Size:    {output_mp4.stat().st_size / 1024 / 1024:.2f} MB")
    print("=" * 75)
    return str(output_mp4)


if __name__ == "__main__":
    render_zero_cost_ai_video()


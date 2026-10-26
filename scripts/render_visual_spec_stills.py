#!/usr/bin/env python3
"""
scripts/render_visual_spec_stills.py
Renders high-fidelity 1080x1920 still frames for:
1. Hook Scene (Fullscreen Typo Dominance)
2. Explanation Scene (Single Focused Stage with Progressive Disclosure)
3. Payoff Scene (High-Impact Verdict with Loop Anchor)
And generates paired comparison frames with YouTube Shorts UI Overlay.
"""

import os
import sys
from pathlib import Path

# Add project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Apple Silicon Cairo dynamic library fallback
if "/opt/homebrew/lib" not in os.environ.get("DYLD_FALLBACK_LIBRARY_PATH", ""):
    current_dyld = os.environ.get("DYLD_FALLBACK_LIBRARY_PATH", "")
    os.environ["DYLD_FALLBACK_LIBRARY_PATH"] = f"/opt/homebrew/lib:{current_dyld}"

import cairosvg
from PIL import Image, ImageDraw, ImageFont

OUTPUT_DIR = Path("/Users/yannaingaung/.gemini/antigravity-ide/brain/e36466b8-8fab-4a55-8251-deb892e1d6ea")
WORKSPACE_OUTPUT_DIR = PROJECT_ROOT / "outputs" / "visual_spec_stills"
WORKSPACE_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ==============================================================================
# 1. SVG GENERATORS FOR 3 SCENE ARCHETYPES
# ==============================================================================

def get_hook_scene_svg() -> str:
    """Hook Scene (0-2s): Fullscreen Typo Dominance, No Card Clutter, Single Accent Pill"""
    # Safe Area Center X = 500 (80 to 920)
    return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 1920" width="1080" height="1920">
    <defs>
        <radialGradient id="bgGlow" cx="46%" cy="48%" r="65%">
            <stop offset="0%" stop-color="#1E293B" stop-opacity="0.6"/>
            <stop offset="100%" stop-color="#090D16" stop-opacity="1.0"/>
        </radialGradient>
        <filter id="pillShadow" x="-10%" y="-10%" width="120%" height="130%">
            <feDropShadow dx="0" dy="12" stdDeviation="16" flood-color="#22C55E" flood-opacity="0.3"/>
        </filter>
    </defs>

    <!-- Canvas Background -->
    <rect width="1080" height="1920" fill="url(#bgGlow)"/>

    <!-- Kinetic Typography (Centered in Safe Area X: 500, Y: 720-1120) -->
    <!-- Line 1: Heavy Display (104px) -->
    <text x="500" y="780" 
          font-family="system-ui, -apple-system, 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif" 
          font-size="104" 
          font-weight="900" 
          letter-spacing="-1.5" 
          fill="#FFFFFF" 
          text-anchor="middle">
        NVIDIA
    </text>

    <!-- Line 2: Heavy Display (104px) -->
    <text x="500" y="890" 
          font-family="system-ui, -apple-system, 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif" 
          font-size="104" 
          font-weight="900" 
          letter-spacing="-1.5" 
          fill="#FFFFFF" 
          text-anchor="middle">
        BLACKWELL
    </text>

    <!-- Line 3: High-Impact Neon Emerald Pill Box (Width: 620px, Centered at X: 500 -> x: 190 to 810) -->
    <g transform="translate(190, 960)">
        <rect width="620" height="130" rx="28" fill="#22C55E" filter="url(#pillShadow)"/>
        <text x="310" y="92" 
              font-family="system-ui, -apple-system, 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif" 
              font-size="84" 
              font-weight="900" 
              letter-spacing="0.5" 
              fill="#090D16" 
              text-anchor="middle">
            1200 WATTS
        </text>
    </g>
</svg>"""


def get_explanation_scene_svg() -> str:
    """Explanation Scene (2-25s): Single Focused Stage (800x820 @ x:100), Progressive Disclosure"""
    return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 1920" width="1080" height="1920">
    <defs>
        <linearGradient id="stageGrad" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stop-color="#111827"/>
            <stop offset="100%" stop-color="#0B0F19"/>
        </linearGradient>
        <filter id="activeGlow" x="-10%" y="-10%" width="120%" height="130%">
            <feDropShadow dx="0" dy="0" stdDeviation="10" flood-color="#22C55E" flood-opacity="0.4"/>
        </filter>
    </defs>

    <!-- Canvas Background -->
    <rect width="1080" height="1920" fill="#0F172A"/>

    <!-- Section Category Header (Centered at Safe X: 500) -->
    <text x="500" y="380" 
          font-family="system-ui, -apple-system, 'SF Pro Display', Arial, sans-serif" 
          font-size="44" 
          font-weight="800" 
          letter-spacing="2" 
          fill="#94A3B8" 
          text-anchor="middle">
        POWER PROGRESSION
    </text>

    <!-- FOCUSED STAGE CONTAINER (800 x 820 @ x: 100 -> Safe right: 900 < 920) -->
    <g transform="translate(100, 430)">
        <!-- Stage Frame -->
        <rect width="800" height="820" rx="22" fill="url(#stageGrad)" stroke="#334155" stroke-width="2"/>
        
        <!-- Window Title Bar -->
        <path d="M 0,22 Q 0,0 22,0 L 778,0 Q 800,0 800,22 L 800,64 L 0,64 Z" fill="#1E293B"/>
        <line x1="0" y1="64" x2="800" y2="64" stroke="#334155" stroke-width="1.5"/>
        
        <!-- macOS Window Controls -->
        <circle cx="36" cy="32" r="7" fill="#EF4444"/>
        <circle cx="62" cy="32" r="7" fill="#F59E0B"/>
        <circle cx="88" cy="32" r="7" fill="#22C55E"/>
        <text x="400" y="39" 
              font-family="'SF Mono', Menlo, Monaco, monospace" 
              font-size="19" 
              fill="#94A3B8" 
              text-anchor="middle">
            blackwell_telemetry.sys
        </text>

        <!-- NODE 1: ACTIVE (Spoken) - Highlighted with Neon Green & Glow -->
        <g transform="translate(35, 100)" filter="url(#activeGlow)">
            <rect width="730" height="175" rx="16" fill="#1E293B" stroke="#22C55E" stroke-width="2.5"/>
            <!-- Left active indicator bar -->
            <rect x="0" y="0" width="8" height="175" rx="4" fill="#22C55E"/>
            <text x="32" y="58" 
                  font-family="system-ui, -apple-system, Arial, sans-serif" 
                  font-size="34" 
                  font-weight="800" 
                  fill="#FFFFFF">
                Nvidia GB200 NVL72
            </text>
            <!-- Badge -->
            <rect x="535" y="28" width="160" height="42" rx="10" fill="#22C55E" fill-opacity="0.18" stroke="#22C55E" stroke-width="1.5"/>
            <text x="615" y="56" 
                  font-family="'SF Mono', Menlo, monospace" 
                  font-size="20" 
                  font-weight="700" 
                  fill="#22C55E" 
                  text-anchor="middle">
                1200W TDP
            </text>
            <!-- Node Specs -->
            <text x="32" y="112" font-family="'SF Mono', Menlo, monospace" font-size="20" fill="#CBD5E1">
                Dual-Die B200 / TSMC 4NP CoWoS-L
            </text>
            <text x="32" y="146" font-family="'SF Mono', Menlo, monospace" font-size="18" fill="#38BDF8">
                [OK] Peak telemetry draw confirmed
            </text>
        </g>

        <!-- Connector Line 1 -> 2 (Animated / Pulsed Green) -->
        <line x1="400" y1="275" x2="400" y2="340" stroke="#22C55E" stroke-width="2.5" stroke-dasharray="6,4"/>

        <!-- NODE 2: MUTED (Upcoming) - Slate Border, Lower Opacity -->
        <g transform="translate(35, 340)">
            <rect width="730" height="175" rx="16" fill="#0F172A" stroke="#334155" stroke-width="1.5"/>
            <text x="32" y="58" 
                  font-family="system-ui, -apple-system, Arial, sans-serif" 
                  font-size="32" 
                  font-weight="700" 
                  fill="#94A3B8">
                Direct Liquid Cooling
            </text>
            <!-- Badge -->
            <rect x="535" y="28" width="160" height="42" rx="10" fill="#1E293B" stroke="#475569" stroke-width="1.2"/>
            <text x="615" y="56" 
                  font-family="'SF Mono', Menlo, monospace" 
                  font-size="19" 
                  font-weight="600" 
                  fill="#94A3B8" 
                  text-anchor="middle">
                45°C DELTA
            </text>
            <!-- Node Specs -->
            <text x="32" y="112" font-family="'SF Mono', Menlo, monospace" font-size="20" fill="#64748B">
                2 L/min cold plate manifold flow
            </text>
            <text x="32" y="146" font-family="'SF Mono', Menlo, monospace" font-size="18" fill="#475569">
                Subsea heat exchanger ready
            </text>
        </g>

        <!-- Connector Line 2 -> 3 (Muted Slate) -->
        <line x1="400" y1="515" x2="400" y2="580" stroke="#334155" stroke-width="1.5"/>

        <!-- NODE 3: MUTED (Upcoming) -->
        <g transform="translate(35, 580)">
            <rect width="730" height="175" rx="16" fill="#0F172A" stroke="#334155" stroke-width="1.5"/>
            <text x="32" y="58" 
                  font-family="system-ui, -apple-system, Arial, sans-serif" 
                  font-size="32" 
                  font-weight="700" 
                  fill="#94A3B8">
                Megawatt Datacenter
            </text>
            <!-- Badge -->
            <rect x="515" y="28" width="180" height="42" rx="10" fill="#1E293B" stroke="#475569" stroke-width="1.2"/>
            <text x="605" y="56" 
                  font-family="'SF Mono', Menlo, monospace" 
                  font-size="19" 
                  font-weight="600" 
                  fill="#94A3B8" 
                  text-anchor="middle">
                100+ kW/RACK
            </text>
            <!-- Node Specs -->
            <text x="32" y="112" font-family="'SF Mono', Menlo, monospace" font-size="20" fill="#64748B">
                Utility grid substation limit reached
            </text>
            <text x="32" y="146" font-family="'SF Mono', Menlo, monospace" font-size="18" fill="#475569">
                Requires nuclear SMR direct connect
            </text>
        </g>
    </g>

    <!-- NEURAL SUBTITLE (2-Line Wrapped, Centered at Safe X: 500, Y: 1390-1470) -->
    <g transform="translate(500, 1400)">
        <text x="0" y="0" text-anchor="middle" font-family="system-ui, -apple-system, Arial, sans-serif" font-size="46" font-weight="600" fill="#FFFFFF">
            NVIDIA'S NEW BLACKWELL
        </text>
        <text x="0" y="56" text-anchor="middle" font-family="system-ui, -apple-system, Arial, sans-serif" font-size="54" font-weight="900" fill="#22C55E">
            DRAWS 1200 WATTS
        </text>
    </g>
</svg>"""


def get_payoff_scene_svg() -> str:
    """Payoff Scene (Ending): High-Impact Verdict Card, Verified Claims, Loop Anchor"""
    # Safe Area: Centered at X: 500, Width: 800 (x: 100 to 900)
    return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 1920" width="1080" height="1920">
    <defs>
        <radialGradient id="payoffGlow" cx="46%" cy="50%" r="60%">
            <stop offset="0%" stop-color="#1E293B" stop-opacity="0.8"/>
            <stop offset="100%" stop-color="#090D16" stop-opacity="1.0"/>
        </radialGradient>
        <filter id="verdictShadow" x="-10%" y="-10%" width="120%" height="130%">
            <feDropShadow dx="0" dy="16" stdDeviation="24" flood-color="#22C55E" flood-opacity="0.25"/>
        </filter>
    </defs>

    <!-- Canvas Background -->
    <rect width="1080" height="1920" fill="url(#payoffGlow)"/>

    <!-- Section Category Header (Centered at Safe X: 500) -->
    <text x="500" y="440" 
          font-family="system-ui, -apple-system, Arial, sans-serif" 
          font-size="42" 
          font-weight="800" 
          letter-spacing="2" 
          fill="#94A3B8" 
          text-anchor="middle">
        BENCHMARK VERDICT
    </text>

    <!-- VERDICT CARD CONTAINER (800 x 820 @ x: 100 -> Safe Right: 900 < 920) -->
    <g transform="translate(100, 500)" filter="url(#verdictShadow)">
        <rect width="800" height="820" rx="28" fill="#111827" stroke="#22C55E" stroke-width="2.5"/>

        <!-- Status Verified Pill Badge -->
        <g transform="translate(240, 70)">
            <rect width="320" height="58" rx="29" fill="#22C55E" fill-opacity="0.15" stroke="#22C55E" stroke-width="2"/>
            <text x="160" y="38" 
                  font-family="'SF Mono', Menlo, monospace" 
                  font-size="24" 
                  font-weight="700" 
                  letter-spacing="1" 
                  fill="#22C55E" 
                  text-anchor="middle">
                [OK] VERIFIED SPEC
            </text>
        </g>

        <!-- Big Hero Metric Number -->
        <text x="400" y="280" 
              font-family="system-ui, -apple-system, Arial, sans-serif" 
              font-size="124" 
              font-weight="900" 
              letter-spacing="-2" 
              fill="#FFFFFF" 
              text-anchor="middle">
            1200W
        </text>
        <text x="400" y="340" 
              font-family="'SF Mono', Menlo, monospace" 
              font-size="26" 
              font-weight="600" 
              letter-spacing="2" 
              fill="#94A3B8" 
              text-anchor="middle">
            PEAK POWER CONSUMPTION
        </text>

        <!-- Subtle Divider Line -->
        <line x1="70" y1="410" x2="730" y2="410" stroke="#334155" stroke-width="2"/>

        <!-- Supporting Metric / Comparison -->
        <text x="400" y="495" 
              font-family="system-ui, -apple-system, Arial, sans-serif" 
              font-size="42" 
              font-weight="800" 
              fill="#38BDF8" 
              text-anchor="middle">
            5× MORE POWER DENSE
        </text>
        <text x="400" y="550" 
              font-family="system-ui, -apple-system, Arial, sans-serif" 
              font-size="25" 
              font-weight="500" 
              fill="#CBD5E1" 
              text-anchor="middle">
            Than entire standard server racks in 2019
        </text>

        <!-- Loop Transition Anchor (Directly answers why and prompts loop restart) -->
        <g transform="translate(80, 640)">
            <rect width="640" height="96" rx="18" fill="#1E293B" stroke="#334155" stroke-width="1.5"/>
            <text x="320" y="44" 
                  font-family="'SF Mono', Menlo, monospace" 
                  font-size="20" 
                  font-weight="600" 
                  fill="#22C55E" 
                  text-anchor="middle">
                LOOP ANCHOR //
            </text>
            <text x="320" y="74" 
                  font-family="system-ui, -apple-system, Arial, sans-serif" 
                  font-size="22" 
                  font-weight="700" 
                  fill="#FFFFFF" 
                  text-anchor="middle">
                "And that's why data centers are going nuclear..."
            </text>
        </g>
    </g>
</svg>"""


# ==============================================================================
# 2. YOUTUBE SHORTS UI OVERLAY GENERATOR
# ==============================================================================

def create_shorts_overlay() -> Image.Image:
    """Creates a transparent RGBA image with YouTube Shorts Native UI Overlay mockup."""
    overlay = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # 1. Top Safe Area Mask / Header (y: 0 to 240)
    # Subtle dark gradient at top
    for y in range(240):
        alpha = int(140 * (1 - y / 240))
        draw.line([(0, y), (1080, y)], fill=(0, 0, 0, alpha))

    # Top boundary guide line (dashed amber)
    draw.line([(0, 240), (1080, 240)], fill=(245, 158, 11, 160), width=2)
    draw.text((80, 210), "▲ TOP UI RISK ZONE (240px: Notch, Search, Sounds)", fill=(245, 158, 11, 230))

    # Top mockup icons: Back arrow, Sound pill, Search, Camera
    draw.rounded_rectangle([(360, 90), (720, 150)], radius=30, fill=(255, 255, 255, 40))
    draw.text((430, 108), "♫ Original sound", fill=(255, 255, 255, 220))

    # 2. Right Actions Column (x: 920 to 1080, y: 700 to 1540)
    draw.line([(920, 240), (920, 1540)], fill=(239, 68, 68, 160), width=2)
    draw.text((928, 660), "ACTION\nICONS\n(160px)", fill=(239, 68, 68, 230))

    # Right side Action Buttons (Like, Dislike, Comment, Share, Remix, Audio Disc)
    actions = [
        ("👍", "142K", 740),
        ("👎", "Dislike", 880),
        ("💬", "1.8K", 1020),
        ("↗️", "Share", 1160),
        ("✂️", "Remix", 1300),
        ("💿", "", 1430)
    ]
    for icon, label, y_pos in actions:
        draw.ellipse([(970, y_pos), (1030, y_pos + 60)], fill=(255, 255, 255, 45))
        draw.text((986, y_pos + 16), icon, fill=(255, 255, 255, 240))
        if label:
            draw.text((980, y_pos + 68), label, fill=(255, 255, 255, 220))

    # 3. Bottom Safe Area Mask / Channel Details (y: 1540 to 1920)
    # Subtle dark gradient at bottom
    for y in range(1540, 1920):
        progress = (y - 1540) / 380
        alpha = int(180 * progress)
        draw.line([(0, y), (1080, y)], fill=(0, 0, 0, alpha))

    # Bottom boundary guide line (dashed amber)
    draw.line([(0, 1540), (1080, 1540)], fill=(245, 158, 11, 160), width=2)
    draw.text((80, 1515), "▼ BOTTOM UI RISK ZONE (380px: Profile, Handle, CTA)", fill=(245, 158, 11, 230))

    # Channel Avatar
    draw.ellipse([(80, 1570), (144, 1634)], fill=(34, 197, 94, 220))
    draw.text((102, 1588), "TR", fill=(0, 0, 0, 255))

    # Channel Handle & Subscribe Button
    draw.text((160, 1580), "@TechRunner", fill=(255, 255, 255, 255))
    draw.rounded_rectangle([(330, 1572), (480, 1628)], radius=28, fill=(255, 255, 255, 255))
    draw.text((358, 1588), "Subscribe", fill=(0, 0, 0, 255))

    # Video Title & Audio Ticker
    draw.text((80, 1660), "Nvidia's Blackwell GPU is breaking power grids...", fill=(255, 255, 255, 230))
    draw.text((80, 1710), "♫ TechRunner • Original Audio", fill=(200, 200, 200, 180))

    # Red Progress bar at very bottom
    draw.rectangle([(0, 1912), (1080, 1920)], fill=(255, 255, 255, 60))
    draw.rectangle([(0, 1912), (320, 1920)], fill=(239, 68, 68, 255))

    return overlay


# ==============================================================================
# 3. RENDER RUNNER
# ==============================================================================

def render_all_stills():
    print("=" * 70)
    print("🎨 RENDERING VISUAL SPECIFICATION v1.0 PROTOTYPE STILLS (1080x1920)")
    print("=" * 70)

    scenes = [
        ("preview_01_hook", get_hook_scene_svg()),
        ("preview_02_explanation", get_explanation_scene_svg()),
        ("preview_03_payoff", get_payoff_scene_svg()),
    ]

    overlay_img = create_shorts_overlay()

    for name, svg_code in scenes:
        print(f"\n[+] Rendering {name}...")
        raw_png_bytes = cairosvg.svg2png(bytestring=svg_code.encode("utf-8"), output_width=1080, output_height=1920)

        # Save Pure Frame
        pure_path_brain = OUTPUT_DIR / f"{name}_pure.png"
        pure_path_ws = WORKSPACE_OUTPUT_DIR / f"{name}_pure.png"
        with open(pure_path_brain, "wb") as f:
            f.write(raw_png_bytes)
        with open(pure_path_ws, "wb") as f:
            f.write(raw_png_bytes)
        print(f"  ✓ Saved pure frame: {pure_path_brain.name}")

        # Composite with YouTube Shorts UI Overlay
        base_img = Image.open(pure_path_brain).convert("RGBA")
        composite_img = Image.alpha_composite(base_img, overlay_img)

        overlay_path_brain = OUTPUT_DIR / f"{name}_with_overlay.png"
        overlay_path_ws = WORKSPACE_OUTPUT_DIR / f"{name}_with_overlay.png"
        composite_img.save(overlay_path_brain, "PNG")
        composite_img.save(overlay_path_ws, "PNG")
        print(f"  ✓ Saved overlay test frame: {overlay_path_brain.name}")

    print("\n" + "=" * 70)
    print("✨ ALL PROTOTYPE STILLS GENERATED SUCCESSFULLY!")
    print(f"📁 Artifact Directory: {OUTPUT_DIR}")
    print(f"📁 Workspace Outputs:  {WORKSPACE_OUTPUT_DIR}")
    print("=" * 70)


if __name__ == "__main__":
    render_all_stills()

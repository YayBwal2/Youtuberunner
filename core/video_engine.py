import os
import re
import sys
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Ensure Cairo dynamic library is located on macOS Apple Silicon
if "/opt/homebrew/lib" not in os.environ.get("DYLD_FALLBACK_LIBRARY_PATH", ""):
    current_dyld = os.environ.get("DYLD_FALLBACK_LIBRARY_PATH", "")
    os.environ["DYLD_FALLBACK_LIBRARY_PATH"] = f"/opt/homebrew/lib:{current_dyld}"

from config import (
    VIDEO_WIDTH,
    VIDEO_HEIGHT,
    VIDEO_FPS,
    OUTPUTS_DIR,
    TEMP_DIR
)
from motion.schema import (
    Storyboard,
    SceneSpec,
    ComponentSpec,
    ComponentType,
    SemanticSlot,
    MotionSpec,
    validate_storyboard
)
from motion.timeline import VoiceSceneMapper
from motion.rasterizer import MotionRenderer

# Legacy engine fallback import
try:
    import core.video_engine_legacy as legacy_engine
except ImportError:
    legacy_engine = None


def build_storyboard_from_script(script_data: Dict[str, Any]) -> Storyboard:
    """
    Translates script beats, title, and topic intent into a validated, multi-scene Storyboard
    conforming strictly to Visual Specification v1.0:
    - Scene 1: HookTypoHero (Fullscreen 104px display + Neon Pill Box, Safe Center X=500, muted subtitles)
    - Scene 2: ProgressiveStage (800x820px macOS Dark Stage with progressive disclosure nodes & 2-line subtitles)
    - Scene 3: PayoffVerdictCard (High-impact Hero Metric + Loop Anchor CTA)
    """
    title = script_data.get("title", "TECH BREAKTHROUGH")
    clean_title = re.sub(r'^[^\w]+|[^\w]+$', '', title).upper()
    beats = script_data.get("beats", [])
    num_beats = len(beats)

    # -------------------------------------------------------------------------
    # Parse Keywords and Colors from Topic
    # -------------------------------------------------------------------------
    title_words = clean_title.split()
    lower_title = title.lower()

    # Dynamic accent color heuristic based on topic domain
    if any(k in lower_title for k in ["cost", "free", "zero", "save", "cheap"]):
        accent_color = "#22C55E"  # Emerald Green (Cost / Free / Open Source)
    elif any(k in lower_title for k in ["ai", "llm", "gpt", "model", "neural"]):
        accent_color = "#A855F7"  # Purple / Violet (AI & Neural)
    elif any(k in lower_title for k in ["watt", "power", "gpu", "chip", "nvidia", "hardware"]):
        accent_color = "#F59E0B"  # Neon Amber (Hardware / Extreme Power)
    else:
        accent_color = "#38BDF8"  # Sky Blue (Developer / Cloud / Architecture)

    scenes: List[SceneSpec] = []

    # -------------------------------------------------------------------------
    # 1. SCENE 1: HOOK TYPO HERO (0.0s – ~3.5s)
    # -------------------------------------------------------------------------
    # Keep line1 and line2 punchy (2 words each for massive display impact)
    sanitized_words = [w.strip("?:!.,\"'") for w in title_words if w.strip("?:!.,\"'")]
    if not sanitized_words:
        sanitized_words = ["TECH", "BREAKTHROUGH"]

    filtered = [w for w in sanitized_words if w.upper() not in ["WHY", "HOW", "IS", "THE", "ARE"]]
    words_to_use = filtered if len(filtered) >= 2 else sanitized_words

    if len(words_to_use) >= 4:
        line1 = " ".join(words_to_use[:2])
        line2 = " ".join(words_to_use[2:4])
    elif len(words_to_use) == 3:
        line1 = " ".join(words_to_use[:2])
        line2 = words_to_use[2]
    elif len(words_to_use) == 2:
        line1 = words_to_use[0]
        line2 = words_to_use[1]
    else:
        line1 = words_to_use[0]
        line2 = "BREAKTHROUGH"


    # Pill box text: extracted from on_screen or numbers in title
    if beats and beats[0].get("on_screen"):
        pill_text = beats[0]["on_screen"].upper()
    elif any(c.isdigit() for c in clean_title):
        nums = [w for w in title_words if any(c.isdigit() for c in w)]
        pill_text = f"{nums[0]} VERIFIED" if nums else "MUST SEE"
    elif "FREE" in clean_title or "ZERO" in clean_title:
        pill_text = "ZERO-COST LLM"
    else:
        pill_text = "TECH BREAKTHROUGH"

    scenes.append(
        SceneSpec(
            scene_id="scene_01_hook",
            slot=SemanticSlot.HERO_CARD,
            visual_intent="Fullscreen kinetic typography dominance with neon pill box",
            components=[
                ComponentSpec(
                    type=ComponentType.HOOK_TYPO_HERO,
                    slot=SemanticSlot.CARD_CENTER,
                    props={
                        "line1": line1,
                        "line2": line2,
                        "pill_text": pill_text,
                        "accent_color": accent_color
                    },
                    motion=MotionSpec(enter="mask_reveal_up", exit="fade_out", delay=0.0, duration=0.45, layer_order=1)
                )
            ]
        )
    )

    # -------------------------------------------------------------------------
    # 2. SCENE 2: PROGRESSIVE STAGE (3.5s – ~12.5s)
    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------
    # 2. SCENE 2: PROGRESSIVE STAGE (Dynamic from script beats)
    # -------------------------------------------------------------------------
    header_text = "SYSTEM ARCHITECTURE"
    if num_beats >= 2 and beats[1].get("on_screen"):
        header_text = beats[1]["on_screen"].upper()
    elif beats and beats[0].get("on_screen"):
        header_text = beats[0]["on_screen"].upper()

    # Dynamic window title based on topic domain
    if any(k in lower_title for k in ["robot", "humanoid", "hardware", "sensor", "motor"]):
        win_title = "robotics_controller.sys"
    elif any(k in lower_title for k in ["docker", "container", "compose"]):
        win_title = "docker-compose.yml"
    elif any(k in lower_title for k in ["python", "script", "code", "app"]):
        win_title = "main.py"
    elif any(k in lower_title for k in ["ai", "model", "neural", "llm", "gpt"]):
        win_title = "neural_pipeline.py"
    else:
        win_title = f"{title_words[0].lower()}_engine.sys" if title_words else "architecture.sys"

    # Select 3 beats to populate 3 dynamic progressive disclosure nodes
    if num_beats >= 4:
        b1, b2, b3 = beats[1], beats[2], beats[3]
    elif num_beats == 3:
        b1, b2, b3 = beats[0], beats[1], beats[2]
    elif num_beats == 2:
        b1, b2, b3 = beats[0], beats[1], beats[1]
    elif num_beats == 1:
        b1 = b2 = b3 = beats[0]
    else:
        b1 = b2 = b3 = {"text": title, "on_screen": "CORE SYSTEM"}

    def _format_beat_line(text: str, max_len: int = 50) -> str:
        t_clean = re.sub(r'^(Here\'s the logic:?|The algorithm|Instead of|You are|This telemetry)\s*', '', text, flags=re.I).strip()
        if len(t_clean) > max_len:
            return t_clean[:max_len - 3] + "..."
        return t_clean

    node1_label = b1.get("on_screen", f"{title_words[0]} Input").title()
    node1_l1 = _format_beat_line(b1.get("text", "Input streaming telemetry"))
    node1_l2 = f"[OK] Active {node1_label} stream"

    node2_label = b2.get("on_screen", "Compute Engine").title()
    node2_l1 = _format_beat_line(b2.get("text", "Continuous optimization pipeline"))
    node2_l2 = f"[OK] {node2_label} processing loop"

    node3_label = b3.get("on_screen", "Control Execution").title()
    node3_l1 = _format_beat_line(b3.get("text", "Real-time edge architecture"))
    node3_l2 = f"[OK] Verified low-latency execution"

    nodes_list = [
        {"label": node1_label, "badge": "ACTIVE", "line1": node1_l1, "line2": node1_l2, "accent": accent_color},
        {"label": node2_label, "badge": "PROCESSING", "line1": node2_l1, "line2": node2_l2, "accent": accent_color},
        {"label": node3_label, "badge": "VERIFIED", "line1": node3_l1, "line2": node3_l2, "accent": accent_color}
    ]

    scenes.append(
        SceneSpec(
            scene_id="scene_02_explanation",
            slot=SemanticSlot.HERO_CARD,
            visual_intent="Single focused macOS dark stage with progressive disclosure",
            components=[
                ComponentSpec(
                    type=ComponentType.PROGRESSIVE_STAGE,
                    slot=SemanticSlot.HERO_CARD,
                    props={
                        "header_text": header_text,
                        "window_title": win_title,
                        "nodes": nodes_list
                    },
                    motion=MotionSpec(enter="spring_pop_in", exit="none", delay=0.1, duration=0.5, layer_order=1)
                )
            ]
        )
    )

    # -------------------------------------------------------------------------
    # 3. SCENE 3: PAYOFF VERDICT CARD (Dynamic metric extraction)
    # -------------------------------------------------------------------------
    verdict_header = "ENGINEERING VERDICT"
    if beats and beats[-1].get("on_screen"):
        verdict_header = f"{beats[-1]['on_screen'].upper()} VERDICT"

    # Extract dynamic numbers/metrics from script or title
    full_script_text = f"{title} {script_data.get('script', '')}"
    num_matches = re.findall(r'(\b\d{1,3}(?:,\d{3})*(?:\.\d+)?(?:\s*(?:Hz|lbs?|x|s|ms|%|X|GB|MB|K|M|B))?|\$\d+)\b', full_script_text, flags=re.I)
    
    if num_matches:
        hero_num = num_matches[0].strip()
        hero_sub = "MEASURED TELEMETRY METRIC"
    else:
        hero_num = "100%"
        hero_sub = "OPTIMIZED ARCHITECTURE"

        clean_subj = [w for w in title_words if w.upper() not in ["HOW", "WHY", "IS", "THE", "ARE", "WHAT", "CAN", "AT"]]
        subject_term = clean_subj[0].title() if clean_subj else "this"
        loop_anchor_q = f"Did you know how {subject_term} works?"

    scenes.append(
        SceneSpec(
            scene_id="scene_03_payoff",
            slot=SemanticSlot.HERO_CARD,
            visual_intent="High-impact payoff verdict card with verified spec and loop anchor",
            components=[
                ComponentSpec(
                    type=ComponentType.PAYOFF_VERDICT_CARD,
                    slot=SemanticSlot.HERO_CARD,
                    props={
                        "category_text": verdict_header,
                        "verified_badge": "[OK] ARCHITECTURE VERIFIED",
                        "hero_metric": hero_num,
                        "metric_subtitle": hero_sub,
                        "second_metric": "REAL-TIME",
                        "second_subtitle": "PRODUCTION EDGE DEPLOYMENT",
                        "loop_anchor_question": loop_anchor_q,
                        "loop_anchor_cta": "SUBSCRIBE FOR DAILY BREAKTHROUGHS"
                    },
                    motion=MotionSpec(enter="spring_pop_in", exit="none", delay=0.1, duration=0.5, layer_order=1)
                )
            ]
        )
    )

    return Storyboard(
        schema_version="1.0.0",
        fps=VIDEO_FPS,
        canvas_profile=f"9:16_{VIDEO_WIDTH}x{VIDEO_HEIGHT}",
        title=title,
        scenes=scenes
    )


def render_shorts_video(
    script_data: Dict[str, Any],
    voice_data: Dict[str, Any],
    output_path: Optional[str] = None,
    thumb_path: Optional[str] = None,
    output_filename: str = "shorts_video.mp4",
    use_motion_engine: bool = True
) -> str:
    """
    Main entry point called by run.py:
    Renders 9:16 vertical video using Visual Specification v1.0 Motion Graphics Engine.
    Streams directly via FFmpeg memory pipe (Zero disk I/O, zero memory drift).
    """
    final_output = output_path or str(OUTPUTS_DIR / "videos" / output_filename)
    final_thumb = thumb_path or final_output.replace(".mp4", "_thumb.png")

    # Ensure parent folder exists
    Path(final_output).parent.mkdir(parents=True, exist_ok=True)

    if use_motion_engine:
        try:
            print(f"\n[3/4] Rendering via Motion Graphics Engine (Visual Spec v1.0 @ {VIDEO_FPS}fps)...")
            storyboard = build_storyboard_from_script(script_data)
            timeline_scenes = VoiceSceneMapper.map_storyboard_to_voice(storyboard, voice_data)
            
            renderer = MotionRenderer(width=VIDEO_WIDTH, height=VIDEO_HEIGHT, fps=VIDEO_FPS)
            stats = renderer.render_memory_pipe(
                scenes=timeline_scenes,
                audio_path=voice_data["audio_path"],
                total_duration=voice_data["duration"],
                output_path=final_output,
                all_words=voice_data["words"]
            )
            print(f"  ✓ Motion Engine rendered {stats['total_frames']} frames in {stats['elapsed_seconds']}s ({stats['render_fps']} fps)")

            # Extract high-res thumbnail frame at 1.5s
            subprocess.run([
                "ffmpeg", "-y", "-ss", "00:00:01.5", "-i", final_output,
                "-frames:v", "1", final_thumb
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"  ✓ Thumbnail generated: {Path(final_thumb).name}")

            return final_output

        except Exception as e:
            print(f"[WARN] Motion graphics engine encountered error: {e}. Falling back to legacy engine...")

    # Fallback to Legacy Engine
    if legacy_engine:
        print("[INFO] Executing legacy rendering engine fallback...")
        return legacy_engine.render_shorts_video(script_data, voice_data, output_filename)
    else:
        raise RuntimeError("Legacy engine is not available for fallback.")


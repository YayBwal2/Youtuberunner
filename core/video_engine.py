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
    Translates script beats, title, and topic intent into a validated, multi-scene Storyboard.
    Supports both direct Gemini-supplied storyboards and automated algorithmic compilation.
    """
    # 1. If Gemini already provided a structured storyboard dictionary, validate directly
    if "storyboard" in script_data and isinstance(script_data["storyboard"], dict):
        try:
            return validate_storyboard(script_data["storyboard"], strict=True)
        except Exception as e:
            print(f"[WARN] Gemini storyboard validation warning: {e}. Compiling from beats...")

    title = script_data.get("title", "TECH BREAKTHROUGH")
    clean_title = re.sub(r'^[^\w]+|[^\w]+$', '', title).upper()
    beats = script_data.get("beats", [])
    
    # Extract keywords for headline highlight
    title_words = clean_title.split()
    highlight_words = [w for w in title_words if len(w) > 4 or any(c.isdigit() for c in w)]
    if not highlight_words and title_words:
        highlight_words = [title_words[-1]]

    scenes: List[SceneSpec] = []
    num_beats = len(beats)

    # -------------------------------------------------------------
    # Scene 1: Hook & Developer Telemetry Card
    # -------------------------------------------------------------
    hook_lines = [
        f"$ sys.init --target \"{title_words[0] if title_words else 'GPU'}\"",
        "[OK] Architecture: 4nm Custom Die",
        "[!] Peak Load: Confirmed",
        "[OK] Telemetry: Active & Streaming"
    ]
    if beats:
        hook_lines[1] = f"[OK] Context: {beats[0].get('on_screen', 'ANALYSIS RUNNING')}"

    scenes.append(
        SceneSpec(
            scene_id="scene_01_hook",
            slot=SemanticSlot.HERO_CARD,
            visual_intent="Hook reveal and macOS telemetry card",
            components=[
                ComponentSpec(
                    type=ComponentType.KINETIC_HEADLINE,
                    slot=SemanticSlot.HEADLINE_TOP,
                    props={"text": clean_title, "highlight_words": highlight_words},
                    motion=MotionSpec(enter="mask_reveal_up", exit="fade_out", delay=0.0, duration=0.45, layer_order=2)
                ),
                ComponentSpec(
                    type=ComponentType.CODE_TERMINAL,
                    slot=SemanticSlot.HERO_CARD,
                    props={
                        "title": f"telemetry_{title_words[0].lower() if title_words else 'main'}.py",
                        "lines": hook_lines
                    },
                    motion=MotionSpec(enter="spring_pop_in", exit="fade_slide_down", delay=0.2, duration=0.65, layer_order=1)
                )
            ]
        )
    )

    # -------------------------------------------------------------
    # Scene 2: Architecture Flow Diagram (Middle Deep-Dive)
    # -------------------------------------------------------------
    diag_headline = "SYSTEM ARCHITECTURE"
    if num_beats >= 2 and beats[1].get("on_screen"):
        diag_headline = beats[1]["on_screen"].upper()

    scenes.append(
        SceneSpec(
            scene_id="scene_02_diagram",
            slot=SemanticSlot.DIAGRAM_SPLIT,
            visual_intent="High-tech architecture flow diagram",
            components=[
                ComponentSpec(
                    type=ComponentType.KINETIC_HEADLINE,
                    slot=SemanticSlot.HEADLINE_TOP,
                    props={"text": diag_headline, "highlight_words": [diag_headline.split()[0]]},
                    motion=MotionSpec(enter="mask_reveal_up", exit="fade_out", delay=0.0, duration=0.4, layer_order=2)
                ),
                ComponentSpec(
                    type=ComponentType.ARCHITECTURE_DIAGRAM,
                    slot=SemanticSlot.HERO_CARD,
                    props={
                        "nodes": [
                            {"label": f"{title_words[0] if title_words else 'System'} Compute Die", "sub": "1.8 TB/s Memory Fabric", "badge": "STAGE 1", "accent": "#22c55e"},
                            {"label": "Direct Liquid Cooling", "sub": "45°C Thermal Delta", "badge": "COOLING", "accent": "#38bdf8"},
                            {"label": "Datacenter Rack Scaler", "sub": "100+ kW / Sub-Rack", "badge": "OUTPUT", "accent": "#f59e0b"}
                        ],
                        "connections": []
                    },
                    motion=MotionSpec(enter="diagram_grow", exit="none", delay=0.15, duration=0.6, layer_order=1)
                )
            ]
        )
    )

    # -------------------------------------------------------------
    # Scene 3: Conclusion / Payoff Terminal Verdict
    # -------------------------------------------------------------
    final_headline = "ENGINEERING VERDICT"
    if num_beats >= 3 and beats[-1].get("on_screen"):
        final_headline = beats[-1]["on_screen"].upper()

    scenes.append(
        SceneSpec(
            scene_id="scene_03_verdict",
            slot=SemanticSlot.HERO_CARD,
            visual_intent="Final conclusion and benchmark verdict",
            components=[
                ComponentSpec(
                    type=ComponentType.KINETIC_HEADLINE,
                    slot=SemanticSlot.HEADLINE_TOP,
                    props={"text": final_headline, "highlight_words": ["VERDICT", final_headline.split()[-1]]},
                    motion=MotionSpec(enter="mask_reveal_up", exit="none", delay=0.0, duration=0.4, layer_order=2)
                ),
                ComponentSpec(
                    type=ComponentType.CODE_TERMINAL,
                    slot=SemanticSlot.HERO_CARD,
                    props={
                        "title": "final_benchmark.sh",
                        "lines": [
                            "$ ./verify_deployment --strict",
                            "[OK] Tests Passed: 100%",
                            "[OK] Efficiency: Verified",
                            "[OK] STATUS: PRODUCTION READY"
                        ]
                    },
                    motion=MotionSpec(enter="spring_pop_in", exit="none", delay=0.2, duration=0.6, layer_order=1)
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
    output_filename: str = "shorts_video.mp4",
    use_motion_engine: bool = True
) -> str:
    """
    Main entry point called by run.py:
    Renders 9:16 vertical video using Python-native Motion Graphics Engine (SVG/CairoSVG/FFmpeg).
    Automatically falls back to legacy engine if motion rendering is disabled or encounters error.
    """
    output_path = str(OUTPUTS_DIR / output_filename)
    thumb_path = output_path.replace(".mp4", "_thumb.png")

    if use_motion_engine:
        try:
            print(f"\n[3/4] Rendering via Motion Graphics Engine (SVG/Cairo + FFmpeg @ {VIDEO_FPS}fps)...")
            storyboard = build_storyboard_from_script(script_data)
            timeline_scenes = VoiceSceneMapper.map_storyboard_to_voice(storyboard, voice_data)
            
            renderer = MotionRenderer(width=VIDEO_WIDTH, height=VIDEO_HEIGHT, fps=VIDEO_FPS)
            stats = renderer.render_disk_cached(
                scenes=timeline_scenes,
                audio_path=voice_data["audio_path"],
                total_duration=voice_data["duration"],
                output_path=output_path,
                all_words=voice_data["words"],
                cleanup_frames=True
            )
            print(f"  ✓ Motion Engine rendered {stats['total_frames']} frames in {stats['elapsed_seconds']}s ({stats['render_fps']} fps)")

            # Extract high-res thumbnail frame at 1.5s
            subprocess.run([
                "ffmpeg", "-y", "-ss", "00:00:01.5", "-i", output_path,
                "-frames:v", "1", thumb_path
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"  ✓ Thumbnail generated: {Path(thumb_path).name}")

            return output_path

        except Exception as e:
            print(f"[WARN] Motion graphics engine encountered error: {e}. Falling back to legacy engine...")

    # Fallback to Legacy Engine
    if legacy_engine:
        print("[INFO] Executing legacy rendering engine fallback...")
        return legacy_engine.render_shorts_video(script_data, voice_data, output_filename)
    else:
        raise RuntimeError("Legacy engine is not available for fallback.")

#!/usr/bin/env python3
"""
scripts/run_prototype.py - Phase 3 One-Scene Prototype Runner
Tests 5-8 second scene with:
- Kinetic headline reveal
- macOS Terminal card with spring pop-in
- Architecture diagram
- Voice synchronization with pause snapping
"""

import os
import sys
import time
from pathlib import Path

# Add project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Apple Silicon Homebrew Cairo dynamic library path
if "/opt/homebrew/lib" not in os.environ.get("DYLD_FALLBACK_LIBRARY_PATH", ""):
    current_dyld = os.environ.get("DYLD_FALLBACK_LIBRARY_PATH", "")
    os.environ["DYLD_FALLBACK_LIBRARY_PATH"] = f"/opt/homebrew/lib:{current_dyld}"

from config import OUTPUTS_DIR, TEMP_DIR
from core.voice_synthesizer import synthesize_speech
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


def run_prototype():
    print("=" * 70)
    print("🎬 PHASE 3: ONE-SCENE PROTOTYPE BENCHMARK (6-8s)")
    print("=" * 70)

    # 1. Synthesize 6-second developer narration
    narration_text = (
        "Nvidia's new Blackwell GPU draws 1200 watts. "
        "That is more power than an entire server rack used five years ago."
    )
    print("\n[1/3] Synthesizing high-fidelity neural voice...")
    voice_data = synthesize_speech(
        script_text=narration_text,
        output_filename="prototype_audio.mp3"
    )
    print(f"  ✓ Audio generated: {voice_data['duration']}s, {len(voice_data['words'])} words.")

    # 2. Build Semantic Storyboard
    raw_storyboard = {
        "schema_version": "1.0.0",
        "fps": 30,
        "canvas_profile": "9:16_1080x1920",
        "title": "Nvidia Blackwell 1200W",
        "scenes": [
            {
                "scene_id": "scene_01_hook",
                "narration_ref": "sentences:0",
                "slot": "hero_card",
                "visual_intent": "Headline reveal and terminal power check",
                "components": [
                    {
                        "type": "KineticHeadline",
                        "slot": "headline_top",
                        "props": {
                            "text": "NVIDIA BLACKWELL 1200W",
                            "highlight_words": ["1200W", "NVIDIA"]
                        },
                        "motion": {
                            "enter": "mask_reveal_up",
                            "exit": "fade_out",
                            "delay": 0.0,
                            "duration": 0.45,
                            "easing": "ease_out_expo",
                            "properties": ["opacity", "translate_y"],
                            "layer_order": 2
                        }
                    },
                    {
                        "type": "CodeTerminal",
                        "slot": "hero_card",
                        "props": {
                            "title": "blackwell_telemetry.py",
                            "lines": [
                                "$ python telemetry.py --gpu GB200",
                                "[OK] Chip: Dual-Die Blackwell",
                                "[!] Peak Draw: 1200 Watts",
                                "[OK] Cooling: Direct-to-Chip Liquid"
                            ]
                        },
                        "motion": {
                            "enter": "spring_pop_in",
                            "exit": "fade_slide_down",
                            "delay": 0.25,
                            "duration": 0.65,
                            "easing": "spring",
                            "properties": ["opacity", "translate_y", "scale"],
                            "layer_order": 1
                        }
                    }
                ]
            },
            {
                "scene_id": "scene_02_diagram",
                "narration_ref": "sentences:1",
                "slot": "diagram_split",
                "visual_intent": "Architecture flow diagram showing power progression",
                "components": [
                    {
                        "type": "KineticHeadline",
                        "slot": "headline_top",
                        "props": {
                            "text": "SERVER RACK DENSITY",
                            "highlight_words": ["DENSITY"]
                        },
                        "motion": {
                            "enter": "mask_reveal_up",
                            "exit": "none",
                            "delay": 0.0,
                            "duration": 0.4,
                            "easing": "ease_out_expo",
                            "layer_order": 2
                        }
                    },
                    {
                        "type": "ArchitectureDiagram",
                        "slot": "hero_card",
                        "props": {
                            "nodes": [
                                {"label": "Nvidia GB200 NVL72", "badge": "1200W TDP", "accent": "#22c55e"},
                                {"label": "Direct Liquid Cooling", "badge": "45°C DELTA", "accent": "#38bdf8"},
                                {"label": "Megawatt Datacenter", "badge": "100+ kW/RACK", "accent": "#f59e0b"}
                            ],
                            "connections": []
                        },
                        "motion": {
                            "enter": "diagram_grow",
                            "exit": "none",
                            "delay": 0.15,
                            "duration": 0.6,
                            "easing": "ease_out_expo",
                            "layer_order": 1
                        }
                    }
                ]
            }
        ]
    }

    print("\n[2/3] Validating Storyboard schema & mapping timeline...")
    storyboard = validate_storyboard(raw_storyboard, strict=True)
    timeline_scenes = VoiceSceneMapper.map_storyboard_to_voice(storyboard, voice_data)
    
    print(f"  ✓ Mapped {len(timeline_scenes)} scenes:")
    for s in timeline_scenes:
        print(f"    - [{s.spec.scene_id}]: {s.start_time:.2f}s -> {s.end_time:.2f}s (dur: {s.duration:.2f}s)")

    # 3. Render Prototype
    output_mp4 = str(OUTPUTS_DIR / "prototype_scene.mp4")
    print(f"\n[3/3] Rendering prototype via MotionRenderer to: {output_mp4}")
    renderer = MotionRenderer()
    
    stats = renderer.render_memory_pipe(
        scenes=timeline_scenes,
        audio_path=voice_data["audio_path"],
        total_duration=voice_data["duration"],
        output_path=output_mp4,
        all_words=voice_data["words"]
    )

    print("\n" + "=" * 70)
    print("✨ PROTOTYPE RENDER COMPLETE!")
    print(f"  📁 Output:        {output_mp4}")
    print(f"  ⏱️ Render Time:   {stats['elapsed_seconds']}s")
    print(f"  🎞️ Frames:        {stats['total_frames']} frames")
    print(f"  ⚡ Render Speed:  {stats['render_fps']} fps")
    print("=" * 70)

    return stats


if __name__ == "__main__":
    run_prototype()

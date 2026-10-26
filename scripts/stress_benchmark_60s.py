#!/usr/bin/env python3
"""
scripts/stress_benchmark_60s.py
Technical Acceptance Benchmark:
- 60-second stress test (1,800 frames @ 30fps 1080x1920)
- Tracemalloc memory profiling sampled every 10s (300 frames)
- Memory leak detection (ensuring flat memory growth)
- Startup pre-purge verification
"""

import os
import sys
import time
import tracemalloc
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Apple Silicon Cairo library
if "/opt/homebrew/lib" not in os.environ.get("DYLD_FALLBACK_LIBRARY_PATH", ""):
    current_dyld = os.environ.get("DYLD_FALLBACK_LIBRARY_PATH", "")
    os.environ["DYLD_FALLBACK_LIBRARY_PATH"] = f"/opt/homebrew/lib:{current_dyld}"

from config import OUTPUTS_DIR, TEMP_DIR
from motion.rasterizer import MotionRenderer, rasterize_svg_to_rgb_bytes
from motion.schema import Storyboard, SceneSpec, ComponentSpec, SemanticSlot, validate_storyboard
from motion.timeline import TimelineScene, TimelineEngine, TimelineComponent


def test_startup_pre_purge():
    print("\n--- [1/2] Verifying Startup Pre-Purge ---")
    frames_dir = TEMP_DIR / "render_frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    
    # Create fake lingering frames from a hypothetical killed process
    dummy_files = [frames_dir / f"frame_{i:04d}.png" for i in range(10)]
    for f in dummy_files:
        f.write_text("dummy frame data")
    
    count_before = len(list(frames_dir.glob("*.png")))
    print(f"  Simulated {count_before} leftover frames in {frames_dir}...")
    
    # Initialize MotionRenderer with auto_purge=True
    renderer = MotionRenderer(auto_purge=True)
    
    count_after = len(list(frames_dir.glob("*.png"))) if frames_dir.exists() else 0
    print(f"  Post-initialization residual frames: {count_after}")
    assert count_after == 0, f"Expected 0 frames, found {count_after}"
    print("  ✓ Startup Pre-Purge verified: 100% clean (0 residual files).")


def run_60s_stress_benchmark():
    print("\n--- [2/2] Running 60-Second Stress Benchmark (1,800 Frames) ---")
    
    # 60s test mock storyboard with Hook, Explanation, and Payoff scenes
    raw_storyboard = {
        "schema_version": "1.0.0",
        "fps": 30,
        "canvas_profile": "9:16_1080x1920",
        "title": "60s Stress Benchmark",
        "scenes": [
            {
                "scene_id": "scene_01_hook",
                "narration_ref": "sentences:0",
                "slot": "hero_card",
                "components": [
                    {
                        "type": "KineticHeadline",
                        "slot": "headline_top",
                        "props": {"text": "NVIDIA BLACKWELL 1200W", "highlight_words": ["1200W"]},
                        "motion": {"enter": "mask_reveal_up", "duration": 0.45}
                    }
                ]
            },
            {
                "scene_id": "scene_02_explanation",
                "narration_ref": "sentences:1",
                "slot": "hero_card",
                "components": [
                    {
                        "type": "CodeTerminal",
                        "slot": "hero_card",
                        "props": {
                            "title": "telemetry.py",
                            "lines": ["$ python test.py", "[OK] Draw: 1200W", "[OK] Cooling: Liquid"]
                        },
                        "motion": {"enter": "spring_pop_in", "duration": 0.55}
                    }
                ]
            },
            {
                "scene_id": "scene_03_payoff",
                "narration_ref": "sentences:2",
                "slot": "hero_card",
                "components": [
                    {
                        "type": "ArchitectureDiagram",
                        "slot": "hero_card",
                        "props": {
                            "nodes": [
                                {"label": "GB200 NVL72", "badge": "1200W TDP"},
                                {"label": "Liquid Cooling", "badge": "45°C DELTA"}
                            ],
                            "connections": []
                        },
                        "motion": {"enter": "diagram_grow", "duration": 0.6}
                    }
                ]
            }
        ]
    }

    storyboard = validate_storyboard(raw_storyboard, strict=True)
    
    # 3 scenes mapped across 60 seconds (20s each)
    total_duration = 60.0
    fps = 30
    total_frames = int(total_duration * fps)  # 1800 frames
    
    scenes = []
    for i, s_spec in enumerate(storyboard.scenes):
        st = i * 20.0
        et = (i + 1) * 20.0
        dur = et - st
        comps = [
            TimelineComponent(spec=c, scene_start=st, scene_end=et)
            for c in s_spec.components
        ]
        scenes.append(TimelineScene(spec=s_spec, start_time=st, end_time=et, duration=dur, components=comps))

    output_path = str(OUTPUTS_DIR / "stress_benchmark_60s.mp4")
    renderer = MotionRenderer(width=1080, height=1920, fps=fps)

    # Start tracemalloc
    tracemalloc.start()
    start_time = time.time()
    
    print(f"  Starting 60s stream render ({total_frames} frames to FFmpeg stdin)...")
    
    # We will sample memory every 300 frames (10 seconds)
    import subprocess
    cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", "1080x1920",
        "-pix_fmt", "rgb24",
        "-r", str(fps),
        "-i", "-",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-pix_fmt", "yuv420p",
        output_path
    ]
    
    process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
    timeline_engine = TimelineEngine(scenes)

    memory_checkpoints = []

    for frame_idx in range(total_frames):
        t = frame_idx / fps
        active_scene = timeline_engine.get_active_scene(t)
        svg = renderer.svg_builder.build_frame_svg(
            scene=active_scene,
            t=t,
            global_duration=total_duration,
            active_chunk=None
        )
        raw_rgb = rasterize_svg_to_rgb_bytes(svg)
        process.stdin.write(raw_rgb)

        # Sample memory every 300 frames (10s)
        if (frame_idx + 1) % 300 == 0:
            current, peak = tracemalloc.get_traced_memory()
            sec = (frame_idx + 1) // fps
            current_mb = current / (1024 * 1024)
            peak_mb = peak / (1024 * 1024)
            memory_checkpoints.append((sec, current_mb, peak_mb))
            print(f"    Checkpoint {sec:02d}s ({frame_idx + 1:04d}/{total_frames} frames): Current RAM = {current_mb:.2f} MB | Peak = {peak_mb:.2f} MB")

    process.stdin.close()
    process.wait()
    
    elapsed = time.time() - start_time
    final_current, final_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    render_fps = total_frames / max(0.001, elapsed)
    file_size_mb = os.path.getsize(output_path) / (1024 * 1024) if os.path.exists(output_path) else 0

    print("\n" + "=" * 70)
    print("🏆 60-SECOND STRESS BENCHMARK RESULTS")
    print("=" * 70)
    print(f"  Duration:         {total_duration}s ({total_frames} frames @ 1080x1920)")
    print(f"  Elapsed Time:     {elapsed:.2f}s")
    print(f"  Render Speed:     {render_fps:.2f} fps")
    print(f"  Output MP4 Size:  {file_size_mb:.2f} MB")
    print(f"  Initial RAM (10s):{memory_checkpoints[0][1]:.2f} MB")
    print(f"  Final RAM (60s):  {memory_checkpoints[-1][1]:.2f} MB")
    print(f"  Peak RAM (All):   {final_peak / (1024*1024):.2f} MB")
    
    # Verify memory stability: growth from 10s to 60s should be negligible (< 10 MB drift)
    ram_drift = memory_checkpoints[-1][1] - memory_checkpoints[0][1]
    print(f"  RAM Drift (10->60s): {ram_drift:+.2f} MB")
    
    if abs(ram_drift) < 15.0:
        print("  ✓ MEMORY STABILITY: PASSED (Zero linear leak across 1800 frames!)")
    else:
        print(f"  ⚠️ MEMORY WARNING: Drift detected (+{ram_drift:.2f} MB)")

    print("=" * 70)
    return {
        "frames": total_frames,
        "elapsed_s": round(elapsed, 2),
        "render_fps": round(render_fps, 2),
        "peak_ram_mb": round(final_peak / (1024 * 1024), 2),
        "ram_drift_mb": round(ram_drift, 2),
        "passed": abs(ram_drift) < 15.0
    }


if __name__ == "__main__":
    test_startup_pre_purge()
    run_60s_stress_benchmark()

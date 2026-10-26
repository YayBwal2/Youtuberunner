import io
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

import numpy as np
from PIL import Image

# Ensure Apple Silicon Homebrew Cairo dynamic library path is set
if "/opt/homebrew/lib" not in os.environ.get("DYLD_FALLBACK_LIBRARY_PATH", ""):
    current_dyld = os.environ.get("DYLD_FALLBACK_LIBRARY_PATH", "")
    os.environ["DYLD_FALLBACK_LIBRARY_PATH"] = f"/opt/homebrew/lib:{current_dyld}"

import cairosvg

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import (
    VIDEO_WIDTH,
    VIDEO_HEIGHT,
    VIDEO_FPS,
    TEMP_DIR,
    OUTPUTS_DIR
)
from motion.svg_builder import SVGBuilder
from motion.timeline import TimelineScene, TimelineEngine


def rasterize_svg_to_pil(svg_markup: str) -> Image.Image:
    """Converts SVG XML string to PIL RGBA Image via CairoSVG."""
    png_bytes = cairosvg.svg2png(bytestring=svg_markup.encode("utf-8"))
    return Image.open(io.BytesIO(png_bytes)).convert("RGB")


def rasterize_svg_to_rgb_bytes(svg_markup: str) -> bytes:
    """Converts SVG XML string directly to raw 24-bit RGB byte buffer."""
    img = rasterize_svg_to_pil(svg_markup)
    return img.tobytes()


class MotionRenderer:
    """
    Renders timeline scenes to MP4 with support for:
    Option A: Direct FFmpeg stdin memory pipe (no disk I/O)
    Option B: Disk-cached frames + FFmpeg concat
    Provides timing and resource profiling for benchmarking.
    """
    def __init__(self, width: int = VIDEO_WIDTH, height: int = VIDEO_HEIGHT, fps: int = VIDEO_FPS, auto_purge: bool = True):
        self.width = width
        self.height = height
        self.fps = fps
        self.svg_builder = SVGBuilder(width, height)
        if auto_purge:
            self.startup_pre_purge()

    @staticmethod
    def startup_pre_purge():
        """
        Purges any leftover temporary render frames from previous interrupted runs.
        Ensures 0 MB residual disk footprint on startup.
        """
        import shutil
        frames_dir = TEMP_DIR / "render_frames"
        if frames_dir.exists():
            try:
                shutil.rmtree(frames_dir)
            except Exception:
                pass

    def render_memory_pipe(
        self,
        scenes: List[TimelineScene],
        audio_path: str,
        total_duration: float,
        output_path: str,
        all_words: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Option A: Streams raw RGB frame buffers directly into FFmpeg stdin.
        Eliminates disk I/O entirely.
        """
        start_time = time.time()
        total_frames = int(total_duration * self.fps)
        all_words = all_words or []

        # Build 3-word chunks for subtitles
        word_chunks = []
        chunk_size = 3
        for i in range(0, len(all_words), chunk_size):
            group = all_words[i:i + chunk_size]
            if group:
                word_chunks.append({
                    "start": group[0]["start"],
                    "end": group[-1]["end"],
                    "words": group
                })

        # Start FFmpeg subprocess listening on stdin
        cmd = [
            "ffmpeg",
            "-y",
            "-f", "rawvideo",
            "-vcodec", "rawvideo",
            "-s", f"{self.width}x{self.height}",
            "-pix_fmt", "rgb24",
            "-r", str(self.fps),
            "-i", "-",               # pipe:0 stdin
            "-i", str(audio_path),    # Audio input
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-preset", "fast",
            "-crf", "16",
            "-b:v", "6M",
            "-maxrate", "10M",
            "-bufsize", "12M",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            str(output_path)
        ]

        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        timeline_engine = TimelineEngine(scenes)

        for frame_idx in range(total_frames):
            t = frame_idx / self.fps
            active_scene = timeline_engine.get_active_scene(t)
            
            # Find active subtitle chunk
            active_chunk = None
            for ch in word_chunks:
                if ch["start"] <= t <= ch["end"] + 0.15:
                    active_chunk = ch
                    break

            # Build and rasterize SVG
            svg = self.svg_builder.build_frame_svg(
                scene=active_scene,
                t=t,
                global_duration=total_duration,
                active_chunk=active_chunk
            )
            raw_rgb = rasterize_svg_to_rgb_bytes(svg)
            process.stdin.write(raw_rgb)

        process.stdin.close()
        process.wait()

        elapsed = time.time() - start_time
        fps_achieved = total_frames / max(0.001, elapsed)

        return {
            "mode": "memory_pipe",
            "output_path": output_path,
            "total_frames": total_frames,
            "duration": total_duration,
            "elapsed_seconds": round(elapsed, 2),
            "render_fps": round(fps_achieved, 2),
            "ffmpeg_exit": process.returncode
        }

    def render_disk_cached(
        self,
        scenes: List[TimelineScene],
        audio_path: str,
        total_duration: float,
        output_path: str,
        all_words: Optional[List[Dict[str, Any]]] = None,
        cleanup_frames: bool = True
    ) -> Dict[str, Any]:
        """
        Option B: Writes PNG frames to disk first, then concatenates with FFmpeg.
        Automatically purges temporary PNG frame files after encoding to maintain zero residual disk usage.
        """
        import shutil
        start_time = time.time()
        frames_dir = TEMP_DIR / "render_frames"
        frames_dir.mkdir(parents=True, exist_ok=True)

        try:
            # Clear any preexisting frames
            for p in frames_dir.glob("*.png"):
                p.unlink()

            total_frames = int(total_duration * self.fps)
            all_words = all_words or []

            word_chunks = []
            chunk_size = 3
            for i in range(0, len(all_words), chunk_size):
                group = all_words[i:i + chunk_size]
                if group:
                    word_chunks.append({
                        "start": group[0]["start"],
                        "end": group[-1]["end"],
                        "words": group
                    })

            timeline_engine = TimelineEngine(scenes)

            for frame_idx in range(total_frames):
                t = frame_idx / self.fps
                active_scene = timeline_engine.get_active_scene(t)
                
                active_chunk = None
                for ch in word_chunks:
                    if ch["start"] <= t <= ch["end"] + 0.15:
                        active_chunk = ch
                        break

                svg = self.svg_builder.build_frame_svg(
                    scene=active_scene,
                    t=t,
                    global_duration=total_duration,
                    active_chunk=active_chunk
                )
                frame_path = frames_dir / f"frame_{frame_idx:05d}.png"
                cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to=str(frame_path))

            # Run FFmpeg concat from disk
            cmd = [
                "ffmpeg",
                "-y",
                "-r", str(self.fps),
                "-i", str(frames_dir / "frame_%05d.png"),
                "-i", str(audio_path),
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                "-preset", "fast",
                "-crf", "16",
                "-b:v", "6M",
                "-maxrate", "10M",
                "-bufsize", "12M",
                "-c:a", "aac",
                "-b:a", "192k",
                "-shortest",
                str(output_path)
            ]
            res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

            elapsed = time.time() - start_time
            fps_achieved = total_frames / max(0.001, elapsed)

            return {
                "mode": "disk_cached",
                "output_path": output_path,
                "total_frames": total_frames,
                "duration": total_duration,
                "elapsed_seconds": round(elapsed, 2),
                "render_fps": round(fps_achieved, 2),
                "ffmpeg_exit": res.returncode
            }
        finally:
            if cleanup_frames and frames_dir.exists():
                shutil.rmtree(frames_dir, ignore_errors=True)

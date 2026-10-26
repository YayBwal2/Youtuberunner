#!/usr/bin/env python3
"""
run.py - Automated YouTube Shorts Pipeline Orchestrator

Usage:
    .venv/bin/python run.py                         # Run full pipeline with next trending topic
    .venv/bin/python run.py --topic "Custom Topic" # Run for specific topic
    .venv/bin/python run.py --no-upload            # Render and save locally without uploading
    .venv/bin/python run.py --dry-run              # Script and audio only, skip video render
"""

import argparse
import datetime
import json
import re
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import OUTPUTS_DIR, YOUTUBE_PRIVACY_STATUS
from core.trends_fetcher import select_topic
from core.script_generator import generate_and_lint_script
from core.voice_synthesizer import synthesize_speech
from core.video_engine import render_shorts_video
from core.youtube_uploader import upload_video


def slugify(text: str) -> str:
    """Create safe filename slug from title."""
    s = re.sub(r'[^\w\s-]', '', text).strip().lower()
    return re.sub(r'[-\s]+', '_', s)[:36]


def run_pipeline(
    topic: str = None,
    no_upload: bool = False,
    dry_run: bool = False,
    privacy: str = YOUTUBE_PRIVACY_STATUS
):
    start_time = datetime.datetime.now()
    timestamp_str = start_time.strftime("%Y%m%d_%H%M%S")

    print("=" * 70)
    print("🚀 YOUTUBE RUNNER - 100% AUTOMATED SHORTS PIPELINE")
    print("=" * 70)

    # 1. Select Topic
    chosen_topic = select_topic(topic)
    print(f"🎯 Target Topic: {chosen_topic}")
    slug = f"{timestamp_str}_{slugify(chosen_topic)}"

    # 2. Script & Hook Generation
    script_data = generate_and_lint_script(chosen_topic)
    
    # Save script JSON
    script_json_path = OUTPUTS_DIR / f"{slug}_script.json"
    with open(script_json_path, "w", encoding="utf-8") as f:
        json.dump(script_data, f, indent=2)
    print(f"  ✓ Script metadata saved to: {script_json_path.name}")

    if dry_run:
        print("\n[DRY RUN] Script generation complete. Exiting (--dry-run).")
        return

    # 3. Voice Synthesis (edge-tts)
    voice_data = synthesize_speech(
        script_text=script_data["script"],
        output_filename=f"{slug}_audio.mp3"
    )

    # 4. Video Assembly & Kinetic Typography
    video_filename = f"{slug}.mp4"
    video_path = render_shorts_video(
        script_data=script_data,
        voice_data=voice_data,
        output_filename=video_filename
    )

    # 5. YouTube Upload
    video_id = None
    if no_upload:
        print("\n[INFO] Upload skipped (--no-upload flag specified). Video saved locally.")
    else:
        video_id = upload_video(
            video_path=video_path,
            title=script_data.get("title", chosen_topic),
            description=script_data.get("description", ""),
            tags=script_data.get("tags", []),
            privacy_status=privacy
        )

    # Complete Summary
    elapsed = (datetime.datetime.now() - start_time).total_seconds()
    print("\n" + "=" * 70)
    print(f"🎉 PIPELINE COMPLETED IN {elapsed:.1f} SECONDS")
    print(f"📁 Video:      {video_path}")
    print(f"🖼️ Thumbnail:  {video_path.replace('.mp4', '_thumb.png')}")
    print(f"📝 Title:      {script_data.get('title')}")
    print(f"⭐ Hook Score: {script_data.get('hook_score')}/100 ({script_data.get('hook_formula')})")
    if video_id:
        print(f"📺 YouTube:    https://youtu.be/{video_id} ({privacy.upper()})")
    print("=" * 70 + "\n")


def main():
    parser = argparse.ArgumentParser(description="YouTube Runner Automated Shorts Pipeline")
    parser.add_argument("--topic", type=str, default=None, help="Specific topic (defaults to next trending topic)")
    parser.add_argument("--no-upload", action="store_true", help="Render video but skip YouTube upload")
    parser.add_argument("--dry-run", action="store_true", help="Generate script only, skip video render")
    parser.add_argument("--privacy", type=str, choices=["private", "unlisted", "public"], default=YOUTUBE_PRIVACY_STATUS)
    args = parser.parse_args()

    run_pipeline(
        topic=args.topic,
        no_upload=args.no_upload,
        dry_run=args.dry_run,
        privacy=args.privacy
    )


if __name__ == "__main__":
    main()

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

from config import (
    OUTPUTS_DIR,
    YOUTUBE_PRIVACY_STATUS,
    STORAGE_RETENTION_DAYS,
    AUTO_CLEANUP_AFTER_UPLOAD
)
from core.trends_fetcher import select_topic
from core.script_generator import generate_and_lint_script
from core.voice_synthesizer import synthesize_speech
from core.video_engine import render_shorts_video
from core.youtube_uploader import upload_video
from core.storage_manager import cleanup_storage


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

    # Dedicated project folder for each video run to avoid file clutter
    run_dir = OUTPUTS_DIR / "videos" / slug
    run_dir.mkdir(parents=True, exist_ok=True)

    # 2. Script & Hook Generation
    script_data = generate_and_lint_script(chosen_topic)
    script_data["slug"] = slug
    script_data["topic"] = chosen_topic
    script_data["created_at"] = timestamp_str

    if dry_run:
        script_json_path = run_dir / "script.json"
        with open(script_json_path, "w", encoding="utf-8") as f:
            json.dump(script_data, f, indent=2)
        print(f"\n[DRY RUN] Script generation complete. Saved to: {script_json_path.name}")
        return

    # 3. Voice Synthesis (edge-tts)
    voice_data = synthesize_speech(
        script_text=script_data["script"],
        output_filename=f"{slug}_audio.mp3"
    )

    # Save audio copy in project folder
    final_audio_path = run_dir / "audio.mp3"
    try:
        import shutil
        shutil.copy2(voice_data["audio_path"], final_audio_path)
    except Exception:
        pass

    # 4. Video Assembly via Visual Specification v1.0 Motion Graphics Engine
    video_path = str(run_dir / f"{slug}.mp4")
    thumb_path = str(run_dir / "thumbnail.png")

    render_shorts_video(
        script_data=script_data,
        voice_data=voice_data,
        output_path=video_path,
        thumb_path=thumb_path
    )

    # 5. YouTube Upload
    video_id = None
    upload_status = "pending"

    if no_upload:
        upload_status = "skipped"
        print("\n[INFO] Upload skipped (--no-upload flag specified). Video saved locally.")
    else:
        try:
            video_id = upload_video(
                video_path=video_path,
                title=script_data.get("title", chosen_topic),
                description=script_data.get("description", ""),
                tags=script_data.get("tags", []),
                privacy_status=privacy,
                thumbnail_path=thumb_path
            )
            upload_status = "uploaded" if video_id else "pending_credentials"
        except Exception as e:
            upload_status = "failed"
            print(f"[WARN] YouTube upload encountered notice: {e}")

    # Record complete run metadata in script.json
    script_data["video_path"] = video_path
    script_data["thumbnail_path"] = thumb_path
    script_data["youtube_video_id"] = video_id
    script_data["youtube_url"] = f"https://youtu.be/{video_id}" if video_id else None
    script_data["upload_status"] = upload_status

    script_json_path = run_dir / "script.json"
    with open(script_json_path, "w", encoding="utf-8") as f:
        json.dump(script_data, f, indent=2)
    print(f"  ✓ Complete run metadata saved to: {script_json_path}")

    # Complete Summary
    elapsed = (datetime.datetime.now() - start_time).total_seconds()
    print("\n" + "=" * 70)
    print(f"🎉 PIPELINE COMPLETED IN {elapsed:.1f} SECONDS")
    print(f"📁 Video Folder: {run_dir}")
    print(f"🎬 Video:        {Path(video_path).name}")
    print(f"🖼️ Thumbnail:    {Path(thumb_path).name}")
    print(f"📝 Title:        {script_data.get('title')}")
    print(f"⭐ Hook Score:   {script_data.get('hook_score')}/100 ({script_data.get('hook_formula')})")
    print(f"📤 Upload:       {upload_status.upper()}")
    if video_id:
        print(f"📺 YouTube:      https://youtu.be/{video_id} ({privacy.upper()})")

    # Automated Storage Lifecycle Cleanup (Protects VPS from filling up)
    if AUTO_CLEANUP_AFTER_UPLOAD:
        try:
            cl = cleanup_storage(retention_days=STORAGE_RETENTION_DAYS)
            if cl.get("freed_mb", 0) > 0:
                print(f"🧹 Auto-Storage Cleanup: Freed {cl['freed_mb']} MB (Purged media from {cl['purged_runs']} older run(s))")
        except Exception:
            pass
    print("=" * 70 + "\n")



def main():
    parser = argparse.ArgumentParser(description="YouTube Runner Automated Shorts Pipeline")
    parser.add_argument("--topic", type=str, default=None, help="Specific topic (defaults to next trending topic)")
    parser.add_argument("--no-upload", action="store_true", help="Render video but skip YouTube upload")
    parser.add_argument("--dry-run", action="store_true", help="Generate script only, skip video render")
    parser.add_argument("--privacy", type=str, choices=["private", "unlisted", "public"], default=YOUTUBE_PRIVACY_STATUS)
    parser.add_argument("--cleanup", action="store_true", help="Run storage cleanup to purge older uploaded videos and temp files")
    parser.add_argument("--retention-days", type=int, default=STORAGE_RETENTION_DAYS, help="Retention period in days for cleanup")
    args = parser.parse_args()

    if args.cleanup:
        print(f"🧹 Performing storage cleanup (Retention: {args.retention_days} days)...")
        cl = cleanup_storage(retention_days=args.retention_days)
        print(f"  ✓ Purged media from {cl['purged_runs']} older run(s)")
        print(f"  ✓ Freed {cl['freed_mb']} MB")
        return

    run_pipeline(
        topic=args.topic,
        no_upload=args.no_upload,
        dry_run=args.dry_run,
        privacy=args.privacy
    )


if __name__ == "__main__":
    main()

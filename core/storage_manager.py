"""
core/storage_manager.py - Automated Storage Lifecycle & Retention Manager

Prevents VPS disk exhaustion by automatically purging heavy media files (.mp4, .mp3, .png)
for videos that have already been uploaded to YouTube, while preserving lightweight
metadata (script.json) forever.
"""

import os
import sys
import time
import json
from pathlib import Path
from typing import Dict, Any, List

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import (
    OUTPUTS_DIR,
    TEMP_DIR,
    STORAGE_RETENTION_DAYS,
    AUTO_CLEANUP_AFTER_UPLOAD
)


def purge_temp_directory(max_age_hours: float = 12.0) -> int:
    """Purges intermediate files in temp/ older than max_age_hours."""
    if not TEMP_DIR.exists():
        return 0
        
    freed_bytes = 0
    now = time.time()
    cutoff = now - (max_age_hours * 3600)

    for item in TEMP_DIR.glob("*"):
        if item.is_file() and item.stat().st_mtime < cutoff:
            try:
                freed_bytes += item.stat().st_size
                item.unlink()
            except Exception:
                pass
    return freed_bytes


def cleanup_storage(
    retention_days: int = STORAGE_RETENTION_DAYS,
    only_uploaded: bool = True,
    dry_run: bool = False
) -> Dict[str, Any]:
    """
    Scans outputs/videos/ and removes large media files (.mp4, .mp3, .png)
    for runs older than retention_days, while strictly retaining script.json.
    """
    videos_dir = OUTPUTS_DIR / "videos"
    if not videos_dir.exists():
        return {"freed_mb": 0.0, "purged_videos": 0, "status": "no_videos_dir"}

    now = time.time()
    cutoff_seconds = retention_days * 86400
    total_freed_bytes = 0
    purged_folders = []

    # 1. Clean temp directory
    temp_freed = purge_temp_directory(max_age_hours=12.0)
    total_freed_bytes += temp_freed

    # 2. Iterate video run directories
    for run_folder in videos_dir.iterdir():
        if not run_folder.is_dir():
            # If loose mp4 in videos_dir older than retention
            if run_folder.suffix in [".mp4", ".mov", ".avi"]:
                if (now - run_folder.stat().st_mtime) > cutoff_seconds:
                    size = run_folder.stat().st_size
                    total_freed_bytes += size
                    if not dry_run:
                        try:
                            run_folder.unlink()
                        except Exception:
                            pass
            continue

        meta_file = run_folder / "script.json"
        is_uploaded = False
        
        if meta_file.exists():
            try:
                with open(meta_file, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                    is_uploaded = (meta.get("upload_status") == "uploaded") or bool(meta.get("youtube_video_id"))
            except Exception:
                is_uploaded = False

        # If only_uploaded is True, do not delete if not yet uploaded
        if only_uploaded and not is_uploaded:
            continue

        folder_mtime = run_folder.stat().st_mtime
        age_seconds = now - folder_mtime

        if age_seconds > cutoff_seconds:
            # Purge heavy media files (.mp4, .mp3, .png), keep script.json
            folder_freed = 0
            for media_file in run_folder.glob("*"):
                if media_file.name == "script.json":
                    continue  # Keep metadata (2KB) forever!
                if media_file.is_file():
                    file_size = media_file.stat().st_size
                    folder_freed += file_size
                    total_freed_bytes += file_size
                    if not dry_run:
                        try:
                            media_file.unlink()
                        except Exception:
                            pass
            
            if folder_freed > 0:
                purged_folders.append(run_folder.name)

    freed_mb = round(total_freed_bytes / (1024 * 1024), 2)
    return {
        "freed_mb": freed_mb,
        "purged_runs": len(purged_folders),
        "purged_folders": purged_folders,
        "retention_days": retention_days
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="YouTube Runner Storage Lifecycle Manager")
    parser.add_argument("--days", type=int, default=STORAGE_RETENTION_DAYS, help="Purge media older than N days")
    parser.add_argument("--all", action="store_true", help="Purge media regardless of upload status")
    parser.add_argument("--dry-run", action="store_true", help="Calculate freed space without deleting")
    args = parser.parse_args()

    print(f"🧹 Running Storage Cleanup (Retention: {args.days} days)...")
    res = cleanup_storage(retention_days=args.days, only_uploaded=not args.all, dry_run=args.dry_run)
    print(f"  ✓ Purged {res['purged_runs']} older video run(s)")
    print(f"  ✓ Space Freed: {res['freed_mb']} MB")

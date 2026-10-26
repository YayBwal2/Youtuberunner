#!/usr/bin/env python3
"""
scheduler.py - Automated Daily Scheduler for VPS / Server Execution

Usage:
    .venv/bin/python scheduler.py                    # Runs daily at configured time (default 18:00)
    .venv/bin/python scheduler.py --time "14:30"    # Custom daily time
    .venv/bin/python scheduler.py --now              # Run once immediately, then stay in schedule loop
    .venv/bin/python scheduler.py --cron-help       # Display Linux crontab instructions
"""

import argparse
import sys
import time
from pathlib import Path
import schedule

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from run import run_pipeline


def job():
    print(f"\n[CRON TRIGGER] Starting scheduled YouTube generation: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    try:
        run_pipeline(no_upload=False)
    except Exception as e:
        print(f"[ERROR] Scheduled job failed: {e}")


def print_cron_instructions(times_list: list[str]):
    python_bin = PROJECT_ROOT / ".venv" / "bin" / "python"
    script_path = PROJECT_ROOT / "run.py"
    log_path = PROJECT_ROOT / "outputs" / "cron.log"
    print("\n" + "=" * 65)
    print("📋 LINUX CRONTAB SETUP (Zero RAM Idle - 3 Videos/Day)")
    print("=" * 65)
    print("Run `crontab -e` on your server and paste the following lines:")
    for t_str in times_list:
        h, m = t_str.split(":")
        print(f"{int(m)} {int(h)} * * * cd '{PROJECT_ROOT}' && {python_bin} {script_path} >> '{log_path}' 2>&1")
    print("\nThis will automatically generate and upload 3 videos daily.")
    print("=" * 65 + "\n")


def main():
    parser = argparse.ArgumentParser(description="YouTube Runner Automated Scheduler")
    parser.add_argument("--times", type=str, default="06:00,12:00,18:00", help="Comma-separated times (e.g. '06:00,12:00,18:00' for 3 videos/day)")
    parser.add_argument("--now", action="store_true", help="Run once immediately on startup")
    parser.add_argument("--cron-help", action="store_true", help="Show Linux crontab instructions")
    args = parser.parse_args()

    times_list = [t.strip() for t in args.times.split(",") if t.strip()]

    if args.cron_help:
        print_cron_instructions(times_list)
        return

    print(f"⏰ Scheduler active! YouTube Runner will run {len(times_list)} times daily at: {', '.join(times_list)}...")
    
    if args.now:
        print("▶️ Executing immediate run (--now)...")
        job()

    for t_str in times_list:
        schedule.every().day.at(t_str).do(job)


    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == "__main__":
    main()

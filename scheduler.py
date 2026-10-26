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


def print_cron_instructions():
    python_bin = PROJECT_ROOT / ".venv" / "bin" / "python"
    script_path = PROJECT_ROOT / "run.py"
    log_path = PROJECT_ROOT / "outputs" / "cron.log"
    print("\n" + "=" * 60)
    print("📋 LINUX CRONTAB SETUP (Zero RAM when idle)")
    print("=" * 60)
    print("Run `crontab -e` on your VPS and paste the following line:")
    print(f"\n0 18 * * * cd '{PROJECT_ROOT}' && {python_bin} {script_path} >> '{log_path}' 2>&1\n")
    print("This will execute every day at 18:00 UTC automatically.")
    print("=" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(description="YouTube Runner Automated Scheduler")
    parser.add_argument("--time", type=str, default="18:00", help="Time of day to run (HH:MM format)")
    parser.add_argument("--now", action="store_true", help="Run once immediately on startup")
    parser.add_argument("--cron-help", action="store_true", help="Show Linux crontab instructions")
    args = parser.parse_args()

    if args.cron_help:
        print_cron_instructions()
        return

    print(f"⏰ Scheduler active! YouTube Runner will run daily at {args.time}...")
    
    if args.now:
        print("▶️ Executing immediate run (--now)...")
        job()

    schedule.every().day.at(args.time).do(job)

    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == "__main__":
    main()

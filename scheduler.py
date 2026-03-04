"""
scheduler.py — Background job scheduler using the `schedule` library.

Schedule:
- Search all platforms every 6 hours
- Auto-apply to pending Naukri jobs every 12 hours
- Prints stats after each run
"""

import logging
import time
from datetime import datetime

import schedule

import config
import database
from scrapers.all_scrapers import search_all_platforms

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def run_search():
    """Execute a full multi-platform job search and save results to the database."""
    print(f"\n⏰ [{datetime.now().strftime('%H:%M')}] Running scheduled job search…")
    keywords = config.JOB_KEYWORDS[0] if config.JOB_KEYWORDS else "developer"
    try:
        jobs = search_all_platforms(keywords=keywords, location=config.JOB_LOCATION)
        stats = database.get_stats()
        print(f"   📊 DB stats — Total: {stats['total_jobs']} | Applied: {stats['total_applied']}")
    except Exception as exc:  # noqa: BLE001
        logger.error("Scheduled search failed: %s", exc)


def run_apply():
    """Auto-apply to all pending Naukri jobs."""
    print(f"\n⏰ [{datetime.now().strftime('%H:%M')}] Running scheduled auto-apply…")
    try:
        from applier.naukri_apply import apply_to_all_pending  # lazy import (Selenium)
        count = apply_to_all_pending()
        print(f"   ✅ Applied to {count} jobs")
    except ImportError:
        logger.warning("Selenium not available — skipping auto-apply step.")
    except Exception as exc:  # noqa: BLE001
        logger.error("Scheduled auto-apply failed: %s", exc)


def start_scheduler():
    """
    Configure and start the scheduler.

    Runs an immediate search + apply on startup, then repeats on schedule.
    """
    print("\n⏰ Starting auto-scheduler…")
    print("   • Job search every 6 hours")
    print("   • Auto-apply every 12 hours")
    print("   Press Ctrl+C to stop.\n")

    # Run immediately on start
    run_search()
    run_apply()

    # Schedule recurring runs
    schedule.every(6).hours.do(run_search)
    schedule.every(12).hours.do(run_apply)

    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        print("\n⏹  Scheduler stopped.")


if __name__ == "__main__":
    start_scheduler()

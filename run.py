"""
run.py — Main entry point for the Job Automation system.

Supports:
  • Interactive CLI menu
  • Command-line arguments: python run.py search|apply|dashboard|auto|stats
"""

import sys
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

BANNER = r"""
  ____      _         _         _                        _
 |__  |    | |       / \  _   _| |_ ___  _ __ ___   __ _| |_  ___   _ __
   / / _  _| |      / _ \| | | | __/ _ \| '_ ` _ \ / _` | __|/ _ \ | '__|
  / / | || | |     / ___ \ |_| | || (_) | | | | | | (_| | |_| (_) || |
 /_/  |___||_|    /_/   \_\__,_|\__\___/|_| |_| |_|\__,_|\__|\___/ |_|

        🤖  Auto Job Search & Auto Apply  •  100% FREE
        ─────────────────────────────────────────────────
"""

MENU = """
  1. 🔍  Search Jobs Now
  2. 📝  Auto-Apply to Pending Jobs
  3. 🖥️   Open Dashboard
  4. ⏰  Start Auto-Scheduler
  5. 📊  View Stats
  6. 🚪  Exit

  Enter choice [1-6]: """


def do_search():
    import config
    from scrapers.all_scrapers import search_all_platforms

    keywords = config.JOB_KEYWORDS[0] if config.JOB_KEYWORDS else "developer"
    search_all_platforms(keywords=keywords, location=config.JOB_LOCATION)


def do_apply():
    try:
        from applier.naukri_apply import apply_to_all_pending
        print("\n📝 Starting auto-apply on Naukri.com…")
        count = apply_to_all_pending()
        print(f"   ✅ Applied to {count} jobs")
    except ImportError:
        print("   ⚠️  Selenium not installed. Run: pip install selenium")
    except Exception as exc:  # noqa: BLE001
        print(f"   ❌ Auto-apply error: {exc}")


def do_dashboard():
    from dashboard import run_dashboard
    run_dashboard()


def do_auto():
    from scheduler import start_scheduler
    start_scheduler()


def do_stats():
    import database
    stats = database.get_stats()
    print("\n📊 Database Statistics")
    print("=" * 40)
    print(f"  Total jobs found    : {stats['total_jobs']}")
    print(f"  Applications sent   : {stats['total_applied']}")
    print(f"  Interviews          : {stats['total_interviews']}")
    print(f"  Offers              : {stats['total_offers']}")
    print("=" * 40)


ACTIONS = {
    "search": do_search,
    "apply": do_apply,
    "dashboard": do_dashboard,
    "auto": do_auto,
    "stats": do_stats,
}

MENU_MAP = {
    "1": do_search,
    "2": do_apply,
    "3": do_dashboard,
    "4": do_auto,
    "5": do_stats,
}


def main():
    print(BANNER)

    # CLI argument mode
    if len(sys.argv) > 1:
        action = sys.argv[1].lower()
        if action in ACTIONS:
            ACTIONS[action]()
        else:
            print(f"Unknown command '{action}'. Use: search | apply | dashboard | auto | stats")
            sys.exit(1)
        return

    # Interactive menu mode
    while True:
        choice = input(MENU).strip()

        if choice == "6":
            print("\n👋  Goodbye!\n")
            break
        elif choice in MENU_MAP:
            MENU_MAP[choice]()
        else:
            print("  ⚠️  Invalid choice — please enter a number between 1 and 6.")


if __name__ == "__main__":
    main()

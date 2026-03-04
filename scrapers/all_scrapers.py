"""
scrapers/all_scrapers.py — Combined scraper that searches ALL platforms at once.

Deduplicates results by URL, saves to the database, and prints a summary.
"""

import logging
from datetime import datetime

import database
import config
from scrapers.linkedin_free import scrape_linkedin
from scrapers.naukri_free import scrape_naukri
from scrapers.indeed_free import scrape_indeed
from scrapers.remoteok_free import scrape_remoteok
from scrapers.adzuna_free import scrape_adzuna
from scrapers.themuse_free import scrape_themuse
from scrapers.arbeitnow_free import scrape_arbeitnow

logger = logging.getLogger(__name__)


def search_all_platforms(
    keywords: str | None = None,
    location: str | None = None,
    max_jobs_per_source: int | None = None,
) -> list[dict]:
    """
    Run every available scraper in sequence and return a deduplicated list of jobs.

    Jobs are also saved to the SQLite database automatically.

    Args:
        keywords: Search keywords (defaults to first keyword in config).
        location: Job location (defaults to config.JOB_LOCATION).
        max_jobs_per_source: Per-platform cap (defaults to config.MAX_JOBS_PER_SOURCE).

    Returns:
        Combined, deduplicated list of job dicts.
    """
    if keywords is None:
        keywords = config.JOB_KEYWORDS[0] if config.JOB_KEYWORDS else "developer"
    if location is None:
        location = config.JOB_LOCATION
    if max_jobs_per_source is None:
        max_jobs_per_source = config.MAX_JOBS_PER_SOURCE

    print(f"\n🔍 Searching all platforms for: '{keywords}' in '{location}'")
    print("=" * 60)

    scrapers = [
        ("LinkedIn", scrape_linkedin),
        ("Naukri", scrape_naukri),
        ("Indeed", scrape_indeed),
        ("RemoteOK", scrape_remoteok),
        ("Adzuna", scrape_adzuna),
        ("The Muse", scrape_themuse),
        ("Arbeitnow", scrape_arbeitnow),
    ]

    all_jobs: list[dict] = []
    seen_urls: set[str] = set()
    source_counts: dict[str, int] = {}

    for name, scraper_fn in scrapers:
        print(f"  ⏳ Scraping {name}...", end=" ", flush=True)
        try:
            jobs = scraper_fn(keywords=keywords, location=location, max_jobs=max_jobs_per_source)
        except Exception as exc:  # noqa: BLE001
            logger.error("%s scraper raised an exception: %s", name, exc)
            jobs = []

        new_jobs = 0
        for job in jobs:
            url = job.get("url", "")
            if url and url in seen_urls:
                continue  # Deduplicate
            if url:
                seen_urls.add(url)
            all_jobs.append(job)
            new_jobs += 1

        source_counts[name] = new_jobs
        print(f"✅ {new_jobs} jobs found")

    # Save all collected jobs to the database
    print("\n💾 Saving jobs to database...")
    saved_count = 0
    for job in all_jobs:
        job_id = database.save_job(job)
        if job_id is not None:
            saved_count += 1

    # Print summary
    print("\n" + "=" * 60)
    print(f"📊 SUMMARY — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)
    for name, count in source_counts.items():
        print(f"  {name:<15} {count:>4} jobs")
    print("-" * 60)
    print(f"  {'Total found':<15} {len(all_jobs):>4} jobs")
    print(f"  {'New (saved)':<15} {saved_count:>4} jobs")
    print("=" * 60)

    return all_jobs

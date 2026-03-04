"""
scrapers/remoteok_free.py — Use RemoteOK's free public JSON API.

Endpoint: https://remoteok.com/api
No API key required.
"""

import time
import random
import logging

import requests

import config

logger = logging.getLogger(__name__)

API_URL = "https://remoteok.com/api"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
    "Referer": "https://remoteok.com/",
}


def scrape_remoteok(keywords: str = "", location: str = "", max_jobs: int | None = None) -> list[dict]:
    """
    Fetch remote jobs from RemoteOK's free API and return a list of job dicts.

    Args:
        keywords: Job search keywords used to filter results client-side.
        location: Not used (all RemoteOK jobs are remote); kept for API consistency.
        max_jobs: Maximum number of jobs to return.

    Returns:
        List of job dicts with standard keys.
    """
    if max_jobs is None:
        max_jobs = config.MAX_JOBS_PER_SOURCE

    logger.info("RemoteOK: fetching jobs (keyword filter: '%s')", keywords)

    try:
        # A small initial delay is recommended by RemoteOK
        time.sleep(random.uniform(1, 2))
        response = requests.get(API_URL, headers=HEADERS, timeout=20)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:
        logger.error("RemoteOK request failed: %s", exc)
        return []
    except ValueError as exc:
        logger.error("RemoteOK JSON parse error: %s", exc)
        return []

    # First element is metadata, skip it
    if data and isinstance(data[0], dict) and "legal" in data[0]:
        data = data[1:]

    jobs = []
    keyword_lower = keywords.lower()

    for item in data:
        if len(jobs) >= max_jobs:
            break

        try:
            title = item.get("position", "")
            company = item.get("company", "")
            tags = item.get("tags", [])
            salary = ""
            salary_min = item.get("salary_min")
            salary_max = item.get("salary_max")
            if salary_min and salary_max:
                salary = f"${salary_min:,} – ${salary_max:,}"
            elif salary_min:
                salary = f"${salary_min:,}+"

            url = item.get("url", "")
            description = item.get("description", "")
            posted_date = item.get("date", "")

            # Client-side keyword filter
            if keyword_lower and keyword_lower not in title.lower():
                tag_text = " ".join(tags).lower()
                if keyword_lower not in tag_text and keyword_lower not in description.lower():
                    continue

            if not title:
                continue

            jobs.append(
                {
                    "title": title,
                    "company": company,
                    "location": "Remote",
                    "salary": salary,
                    "description": description[:500] if description else "",
                    "url": url,
                    "source": "remoteok",
                    "tags": tags[:10],
                    "posted_date": posted_date,
                }
            )
        except Exception as exc:  # noqa: BLE001
            logger.debug("RemoteOK item parse error: %s", exc)
            continue

    logger.info("RemoteOK: found %d jobs", len(jobs))
    return jobs

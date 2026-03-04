"""
scrapers/themuse_free.py — Use The Muse's free public API.

Endpoint: https://www.themuse.com/api/public/jobs
No API key required.
"""

import time
import random
import logging

import requests

import config

logger = logging.getLogger(__name__)

BASE_URL = "https://www.themuse.com/api/public/jobs"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
}


def scrape_themuse(keywords: str = "", location: str = "", max_jobs: int | None = None) -> list[dict]:
    """
    Fetch jobs from The Muse's free API and return a list of job dicts.

    Args:
        keywords: Job search keywords used for client-side filtering.
        location: Location filter applied client-side.
        max_jobs: Maximum number of jobs to return.

    Returns:
        List of job dicts with standard keys.
    """
    if max_jobs is None:
        max_jobs = config.MAX_JOBS_PER_SOURCE

    jobs = []
    page = 1
    keyword_lower = keywords.lower()
    location_lower = location.lower()

    logger.info("The Muse: searching for '%s' in '%s'", keywords, location)

    while len(jobs) < max_jobs:
        params = {
            "page": page,
            "category": "Computer and IT",  # Narrow to tech jobs
            "level": "Mid Level",
        }

        try:
            response = requests.get(BASE_URL, headers=HEADERS, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as exc:
            logger.error("The Muse request failed: %s", exc)
            break
        except ValueError as exc:
            logger.error("The Muse JSON parse error: %s", exc)
            break

        results = data.get("results", [])
        if not results:
            break

        for item in results:
            if len(jobs) >= max_jobs:
                break

            try:
                title = item.get("name", "")
                company = item.get("company", {}).get("name", "")
                locations = item.get("locations", [])
                job_location = locations[0].get("name", "Remote") if locations else "Remote"
                url_str = item.get("refs", {}).get("landing_page", "")
                publication_date = item.get("publication_date", "")
                levels = item.get("levels", [])
                level_str = levels[0].get("name", "") if levels else ""
                categories = item.get("categories", [])
                tags = [c.get("name", "") for c in categories if c.get("name")]

                # Client-side filters
                if keyword_lower:
                    combined = f"{title} {' '.join(tags)}".lower()
                    if keyword_lower not in combined:
                        continue
                if location_lower and location_lower not in job_location.lower():
                    if location_lower not in ("remote", "anywhere"):
                        # Still include remote jobs when location is specified
                        if "remote" not in job_location.lower():
                            continue

                if not title:
                    continue

                jobs.append(
                    {
                        "title": title,
                        "company": company,
                        "location": job_location,
                        "salary": "",
                        "description": "",
                        "url": url_str,
                        "source": "themuse",
                        "tags": tags,
                        "posted_date": publication_date,
                    }
                )
            except Exception as exc:  # noqa: BLE001
                logger.debug("The Muse item parse error: %s", exc)
                continue

        total_pages = data.get("page_count", 1)
        if page >= total_pages or not results:
            break

        page += 1
        time.sleep(random.uniform(config.REQUEST_DELAY_MIN, config.REQUEST_DELAY_MAX))

    logger.info("The Muse: found %d jobs", len(jobs))
    return jobs

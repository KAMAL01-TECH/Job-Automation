"""
scrapers/arbeitnow_free.py — Use Arbeitnow's free public API.

Endpoint: https://arbeitnow.com/api/job-board-api
No API key required — completely open.
"""

import time
import random
import logging

import requests

import config

logger = logging.getLogger(__name__)

API_URL = "https://arbeitnow.com/api/job-board-api"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
}


def scrape_arbeitnow(keywords: str = "", location: str = "", max_jobs: int | None = None) -> list[dict]:
    """
    Fetch jobs from Arbeitnow's free API and return a list of job dicts.

    Args:
        keywords: Job search keywords for client-side filtering.
        location: Location filter for client-side filtering.
        max_jobs: Maximum number of jobs to return.

    Returns:
        List of job dicts with standard keys.
    """
    if max_jobs is None:
        max_jobs = config.MAX_JOBS_PER_SOURCE

    jobs = []
    page = 1
    keyword_lower = keywords.lower()

    logger.info("Arbeitnow: fetching jobs (keyword filter: '%s')", keywords)

    while len(jobs) < max_jobs:
        params = {"page": page}

        try:
            response = requests.get(API_URL, headers=HEADERS, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as exc:
            logger.error("Arbeitnow request failed: %s", exc)
            break
        except ValueError as exc:
            logger.error("Arbeitnow JSON parse error: %s", exc)
            break

        results = data.get("data", [])
        if not results:
            break

        for item in results:
            if len(jobs) >= max_jobs:
                break

            try:
                title = item.get("title", "")
                company = item.get("company_name", "")
                job_location = item.get("location", "Remote")
                url_str = item.get("url", "")
                description = item.get("description", "")
                tags = item.get("tags", [])
                posted_date = item.get("created_at", "")
                remote = item.get("remote", False)
                if remote and "remote" not in job_location.lower():
                    job_location = f"{job_location} (Remote)"

                # Client-side keyword filter
                if keyword_lower:
                    combined = f"{title} {' '.join(tags)} {description[:200]}".lower()
                    if keyword_lower not in combined:
                        continue

                if not title:
                    continue

                jobs.append(
                    {
                        "title": title,
                        "company": company,
                        "location": job_location,
                        "salary": "",
                        "description": description[:500] if description else "",
                        "url": url_str,
                        "source": "arbeitnow",
                        "tags": tags[:10],
                        "posted_date": posted_date,
                    }
                )
            except Exception as exc:  # noqa: BLE001
                logger.debug("Arbeitnow item parse error: %s", exc)
                continue

        # Arbeitnow paginates; stop if last page
        links = data.get("links", {})
        if not links.get("next"):
            break

        page += 1
        time.sleep(random.uniform(config.REQUEST_DELAY_MIN, config.REQUEST_DELAY_MAX))

    logger.info("Arbeitnow: found %d jobs", len(jobs))
    return jobs

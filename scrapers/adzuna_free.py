"""
scrapers/adzuna_free.py — Use Adzuna's free tier API.

Free signup at https://developer.adzuna.com (250 requests/month on free tier).
Set ADZUNA_APP_ID and ADZUNA_APP_KEY in your .env file.
"""

import time
import random
import logging

import requests

import config

logger = logging.getLogger(__name__)

BASE_URL = "https://api.adzuna.com/v1/api/jobs/{country}/search/{page}"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
}


def scrape_adzuna(keywords: str = "", location: str = "", max_jobs: int | None = None) -> list[dict]:
    """
    Fetch jobs from Adzuna's free API and return a list of job dicts.

    Requires ADZUNA_APP_ID and ADZUNA_APP_KEY to be set in config / .env.

    Args:
        keywords: Job search keywords.
        location: Job location.
        max_jobs: Maximum number of jobs to return.

    Returns:
        List of job dicts with standard keys.
    """
    if not config.ADZUNA_APP_ID or not config.ADZUNA_APP_KEY:
        logger.warning(
            "Adzuna: ADZUNA_APP_ID and ADZUNA_APP_KEY not set — skipping. "
            "Sign up FREE at https://developer.adzuna.com"
        )
        return []

    if max_jobs is None:
        max_jobs = config.MAX_JOBS_PER_SOURCE

    country = config.ADZUNA_COUNTRY
    jobs = []
    page = 1
    page_size = 20

    logger.info("Adzuna: searching for '%s' in '%s' (country=%s)", keywords, location, country)

    while len(jobs) < max_jobs:
        url = BASE_URL.format(country=country, page=page)
        params = {
            "app_id": config.ADZUNA_APP_ID,
            "app_key": config.ADZUNA_APP_KEY,
            "results_per_page": page_size,
            "what": keywords,
            "where": location,
            "content-type": "application/json",
        }

        try:
            response = requests.get(url, headers=HEADERS, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as exc:
            logger.error("Adzuna request failed: %s", exc)
            break
        except ValueError as exc:
            logger.error("Adzuna JSON parse error: %s", exc)
            break

        results = data.get("results", [])
        if not results:
            break

        for item in results:
            if len(jobs) >= max_jobs:
                break

            try:
                title = item.get("title", "")
                company = item.get("company", {}).get("display_name", "")
                job_location = item.get("location", {}).get("display_name", location)
                salary_min = item.get("salary_min")
                salary_max = item.get("salary_max")
                salary = ""
                if salary_min and salary_max:
                    salary = f"₹{int(salary_min):,} – ₹{int(salary_max):,}"
                elif salary_min:
                    salary = f"₹{int(salary_min):,}+"
                description = item.get("description", "")
                url_str = item.get("redirect_url", "")
                posted_date = item.get("created", "")
                category = item.get("category", {}).get("label", "")
                tags = [category] if category else []

                if not title:
                    continue

                jobs.append(
                    {
                        "title": title,
                        "company": company,
                        "location": job_location,
                        "salary": salary,
                        "description": description[:500] if description else "",
                        "url": url_str,
                        "source": "adzuna",
                        "tags": tags,
                        "posted_date": posted_date,
                    }
                )
            except Exception as exc:  # noqa: BLE001
                logger.debug("Adzuna item parse error: %s", exc)
                continue

        if len(results) < page_size:
            break

        page += 1
        time.sleep(random.uniform(config.REQUEST_DELAY_MIN, config.REQUEST_DELAY_MAX))

    logger.info("Adzuna: found %d jobs", len(jobs))
    return jobs

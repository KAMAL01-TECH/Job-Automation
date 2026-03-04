"""
scrapers/linkedin_free.py — Scrape LinkedIn public job listings.

Uses LinkedIn's guest (unauthenticated) Jobs API — no login, no API key needed.
Endpoint: https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search
"""

import time
import random
import logging
from datetime import datetime

import requests
from bs4 import BeautifulSoup

import config

logger = logging.getLogger(__name__)

BASE_URL = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": "https://www.linkedin.com/",
}


def scrape_linkedin(keywords: str = "", location: str = "", max_jobs: int | None = None) -> list[dict]:
    """
    Scrape LinkedIn public job listings and return a list of job dicts.

    Args:
        keywords: Job search keywords (e.g. "Python Developer").
        location: Job location (e.g. "India").
        max_jobs: Maximum number of jobs to return.

    Returns:
        List of job dicts with standard keys.
    """
    if max_jobs is None:
        max_jobs = config.MAX_JOBS_PER_SOURCE

    jobs = []
    start = 0
    page_size = 25  # LinkedIn returns up to 25 results per page

    logger.info("LinkedIn: searching for '%s' in '%s'", keywords, location)

    while len(jobs) < max_jobs:
        params = {
            "keywords": keywords,
            "location": location,
            "start": start,
        }

        try:
            response = requests.get(BASE_URL, headers=HEADERS, params=params, timeout=15)
            response.raise_for_status()
        except requests.RequestException as exc:
            logger.error("LinkedIn request failed: %s", exc)
            break

        soup = BeautifulSoup(response.text, "html.parser")
        job_cards = soup.find_all("li")

        if not job_cards:
            break  # No more results

        for card in job_cards:
            if len(jobs) >= max_jobs:
                break

            try:
                title_tag = card.find("h3", class_="base-search-card__title")
                company_tag = card.find("h4", class_="base-search-card__subtitle")
                location_tag = card.find("span", class_="job-search-card__location")
                link_tag = card.find("a", class_="base-card__full-link")
                date_tag = card.find("time")

                title = title_tag.get_text(strip=True) if title_tag else ""
                company = company_tag.get_text(strip=True) if company_tag else ""
                job_location = location_tag.get_text(strip=True) if location_tag else location
                url = link_tag["href"].split("?")[0] if link_tag else ""
                posted_date = date_tag.get("datetime", "") if date_tag else ""

                if not title or not url:
                    continue

                jobs.append(
                    {
                        "title": title,
                        "company": company,
                        "location": job_location,
                        "salary": "",
                        "description": "",
                        "url": url,
                        "source": "linkedin",
                        "tags": [keywords] if keywords else [],
                        "posted_date": posted_date,
                    }
                )
            except Exception as exc:  # noqa: BLE001
                logger.debug("LinkedIn card parse error: %s", exc)
                continue

        if len(job_cards) < page_size:
            break  # Reached last page

        start += page_size
        time.sleep(random.uniform(config.REQUEST_DELAY_MIN, config.REQUEST_DELAY_MAX))

    logger.info("LinkedIn: found %d jobs", len(jobs))
    return jobs

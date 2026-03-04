"""
scrapers/indeed_free.py — Scrape Indeed.co.in using BeautifulSoup.

No API key required — parses the public HTML search results page.
"""

import time
import random
import logging

import requests
from bs4 import BeautifulSoup

import config

logger = logging.getLogger(__name__)

BASE_URL = "https://www.indeed.co.in/jobs"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-IN,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml",
    "Referer": "https://www.indeed.co.in/",
}


def scrape_indeed(keywords: str = "", location: str = "", max_jobs: int | None = None) -> list[dict]:
    """
    Scrape Indeed.co.in job listings and return a list of job dicts.

    Args:
        keywords: Job search keywords (e.g. "Python Developer").
        location: Job location (e.g. "Bangalore").
        max_jobs: Maximum number of jobs to return.

    Returns:
        List of job dicts with standard keys.
    """
    if max_jobs is None:
        max_jobs = config.MAX_JOBS_PER_SOURCE

    jobs = []
    start = 0
    page_size = 10

    logger.info("Indeed: searching for '%s' in '%s'", keywords, location)

    while len(jobs) < max_jobs:
        params = {
            "q": keywords,
            "l": location,
            "start": start,
        }

        try:
            response = requests.get(BASE_URL, headers=HEADERS, params=params, timeout=15)
            response.raise_for_status()
        except requests.RequestException as exc:
            logger.error("Indeed request failed: %s", exc)
            break

        soup = BeautifulSoup(response.text, "html.parser")

        # Indeed uses data-jk attribute on job cards
        job_cards = soup.find_all("div", class_="job_seen_beacon")
        if not job_cards:
            # Fallback selector
            job_cards = soup.find_all("div", attrs={"data-jk": True})

        if not job_cards:
            logger.debug("Indeed: no job cards found on page (start=%d)", start)
            break

        for card in job_cards:
            if len(jobs) >= max_jobs:
                break

            try:
                title_tag = card.find("h2", class_="jobTitle")
                company_tag = card.find("span", attrs={"data-testid": "company-name"})
                location_tag = card.find("div", attrs={"data-testid": "text-location"})
                salary_tag = card.find("div", class_="salary-snippet-container")

                job_id = card.get("data-jk", "")
                title = title_tag.get_text(strip=True) if title_tag else ""
                company = company_tag.get_text(strip=True) if company_tag else ""
                job_location = location_tag.get_text(strip=True) if location_tag else location
                salary = salary_tag.get_text(strip=True) if salary_tag else ""
                url = f"https://www.indeed.co.in/viewjob?jk={job_id}" if job_id else ""

                if not title or not url:
                    continue

                jobs.append(
                    {
                        "title": title,
                        "company": company,
                        "location": job_location,
                        "salary": salary,
                        "description": "",
                        "url": url,
                        "source": "indeed",
                        "tags": [keywords] if keywords else [],
                        "posted_date": "",
                    }
                )
            except Exception as exc:  # noqa: BLE001
                logger.debug("Indeed card parse error: %s", exc)
                continue

        if len(job_cards) < page_size:
            break

        start += page_size
        time.sleep(random.uniform(config.REQUEST_DELAY_MIN, config.REQUEST_DELAY_MAX))

    logger.info("Indeed: found %d jobs", len(jobs))
    return jobs

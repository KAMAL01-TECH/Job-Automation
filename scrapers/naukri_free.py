"""
scrapers/naukri_free.py — Scrape Naukri.com using their internal search API.

Endpoint: https://www.naukri.com/jobapi/v3/search
No API key required — uses the same endpoint the browser calls.
"""

import time
import random
import logging

import requests

import config

logger = logging.getLogger(__name__)

BASE_URL = "https://www.naukri.com/jobapi/v3/search"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
    "Content-Type": "application/json",
    "appid": "109",
    "systemid": "109",
    "Referer": "https://www.naukri.com/",
}


def scrape_naukri(keywords: str = "", location: str = "", max_jobs: int | None = None) -> list[dict]:
    """
    Scrape Naukri.com job listings and return a list of job dicts.

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
    page = 1
    page_size = 20

    logger.info("Naukri: searching for '%s' in '%s'", keywords, location)

    while len(jobs) < max_jobs:
        params = {
            "noOfResults": page_size,
            "urlType": "search_by_keyword",
            "searchType": "adv",
            "keyword": keywords,
            "location": location,
            "pageNo": page,
            "k": keywords,
            "l": location,
            "experience": config.EXPERIENCE_YEARS,
        }

        try:
            response = requests.get(BASE_URL, headers=HEADERS, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as exc:
            logger.error("Naukri request failed: %s", exc)
            break
        except ValueError as exc:
            logger.error("Naukri JSON parse error: %s", exc)
            break

        job_list = data.get("jobDetails", [])
        if not job_list:
            break

        for item in job_list:
            if len(jobs) >= max_jobs:
                break

            try:
                title = item.get("title", "")
                company = item.get("companyName", "")
                location_str = ", ".join(item.get("placeholders", {}).get("location", "").split(",")[:2])
                salary = item.get("placeholders", {}).get("salary", "")
                url = "https://www.naukri.com" + item.get("jdURL", "")
                description = item.get("jobDescription", "")
                tags = item.get("tagsAndSkills", "").split(",") if item.get("tagsAndSkills") else []
                posted_date = item.get("modifiedOn", "")

                if not title:
                    continue

                jobs.append(
                    {
                        "title": title,
                        "company": company,
                        "location": location_str,
                        "salary": salary,
                        "description": description,
                        "url": url,
                        "source": "naukri",
                        "tags": [t.strip() for t in tags if t.strip()],
                        "posted_date": posted_date,
                    }
                )
            except Exception as exc:  # noqa: BLE001
                logger.debug("Naukri item parse error: %s", exc)
                continue

        if len(job_list) < page_size:
            break

        page += 1
        time.sleep(random.uniform(config.REQUEST_DELAY_MIN, config.REQUEST_DELAY_MAX))

    logger.info("Naukri: found %d jobs", len(jobs))
    return jobs

"""
applier/naukri_apply.py — Auto-apply to jobs on Naukri.com using Selenium.

Requires:
- Google Chrome + chromedriver installed
- NAUKRI_EMAIL and NAUKRI_PASSWORD set in .env
"""

import logging
import time
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    WebDriverException,
)

import config
import database
from cover_letter import generate_cover_letter

logger = logging.getLogger(__name__)

LOGIN_URL = "https://www.naukri.com/nlogin/login"

# Multiple selectors to try for the Apply button (Naukri updates their UI)
APPLY_BUTTON_SELECTORS = [
    "button.apply-button",
    "button[data-testid='apply-button']",
    "a.apply-button",
    "button.noOutline.apply-button",
    "div.apply-button-container button",
    "button[title='Apply']",
    "a[title='Apply Now']",
    ".apply-btn",
]


def _build_driver(headless: bool = True) -> webdriver.Chrome:
    """Create and return a configured Chrome WebDriver."""
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    return webdriver.Chrome(options=options)


def _login(driver: webdriver.Chrome) -> bool:
    """Log in to Naukri.com. Returns True on success."""
    if not config.NAUKRI_EMAIL or not config.NAUKRI_PASSWORD:
        logger.error("Naukri credentials not set. Add NAUKRI_EMAIL and NAUKRI_PASSWORD to .env")
        return False

    try:
        driver.get(LOGIN_URL)
        wait = WebDriverWait(driver, 15)

        email_field = wait.until(EC.presence_of_element_located((By.ID, "usernameField")))
        email_field.clear()
        email_field.send_keys(config.NAUKRI_EMAIL)

        password_field = driver.find_element(By.ID, "passwordField")
        password_field.clear()
        password_field.send_keys(config.NAUKRI_PASSWORD)

        login_btn = driver.find_element(By.XPATH, "//button[@type='submit']")
        login_btn.click()

        # Wait for the page to navigate away from the login page
        wait.until(EC.url_changes(LOGIN_URL))
        logger.info("Naukri: logged in successfully as %s", config.NAUKRI_EMAIL)
        return True

    except (TimeoutException, NoSuchElementException) as exc:
        logger.error("Naukri login failed: %s", exc)
        return False


def _click_apply(driver: webdriver.Chrome, wait: WebDriverWait) -> bool:
    """Try multiple selectors to click the Apply button. Returns True if clicked."""
    for selector in APPLY_BUTTON_SELECTORS:
        try:
            btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
            driver.execute_script("arguments[0].scrollIntoView(true);", btn)
            time.sleep(0.5)
            btn.click()
            logger.info("Naukri: clicked Apply button (%s)", selector)
            return True
        except (TimeoutException, NoSuchElementException):
            continue

    logger.warning("Naukri: could not find Apply button")
    return False


def apply_to_job(job: dict) -> bool:
    """
    Navigate to a Naukri job page and auto-apply.

    Args:
        job: A job dict with at minimum 'url', 'id', 'title', and 'company'.

    Returns:
        True if the application was submitted successfully, False otherwise.
    """
    job_url = job.get("url", "")
    if not job_url:
        logger.warning("apply_to_job: no URL provided")
        return False

    driver = None
    try:
        driver = _build_driver(headless=True)
        wait = WebDriverWait(driver, 15)

        if not _login(driver):
            return False

        driver.get(job_url)
        time.sleep(2)  # Let page settle

        applied = _click_apply(driver, wait)

        if applied:
            cover_letter_text = generate_cover_letter(job)
            database.save_application(
                {
                    "job_id": job.get("id"),
                    "job_title": job.get("title", ""),
                    "company": job.get("company", ""),
                    "status": "applied",
                    "cover_letter": cover_letter_text,
                    "applied_at": datetime.now().isoformat(),
                    "notes": "Auto-applied via Selenium",
                }
            )
            logger.info(
                "Naukri: successfully applied to '%s' at '%s'",
                job.get("title", ""),
                job.get("company", ""),
            )
        return applied

    except WebDriverException as exc:
        logger.error("Naukri WebDriver error for job %s: %s", job_url, exc)
        return False
    finally:
        if driver:
            try:
                driver.quit()
            except WebDriverException:
                pass


def apply_to_all_pending(max_applications: int = 10) -> int:
    """
    Auto-apply to all pending (unapplied) Naukri jobs.

    Args:
        max_applications: Maximum number of applications to submit in this run.

    Returns:
        Number of successful applications.
    """
    pending_jobs = database.get_unapplied_jobs(source="naukri")
    logger.info("Naukri auto-apply: %d pending jobs found", len(pending_jobs))

    success_count = 0
    for job in pending_jobs[:max_applications]:
        logger.info(
            "Applying to: %s at %s (%s)",
            job.get("title", ""),
            job.get("company", ""),
            job.get("url", ""),
        )
        if apply_to_job(job):
            success_count += 1
        time.sleep(3)  # Polite delay between applications

    logger.info("Naukri auto-apply: %d/%d applications submitted", success_count, len(pending_jobs[:max_applications]))
    return success_count

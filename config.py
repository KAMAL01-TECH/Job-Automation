"""
config.py — Load settings from .env file for the Job Automation system.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ── User Profile ──────────────────────────────────────────────────────────────
USER_NAME = os.getenv("USER_NAME", "Your Name")
USER_EMAIL = os.getenv("USER_EMAIL", "your@email.com")
USER_PHONE = os.getenv("USER_PHONE", "+91-9999999999")
RESUME_PATH = os.getenv("RESUME_PATH", "resume.pdf")

# ── Job Preferences ───────────────────────────────────────────────────────────
JOB_KEYWORDS = os.getenv("JOB_KEYWORDS", "Python Developer").split(",")
JOB_LOCATION = os.getenv("JOB_LOCATION", "India")
EXPERIENCE_YEARS = int(os.getenv("EXPERIENCE_YEARS", "2"))

# ── Naukri.com Login (for auto-apply) ────────────────────────────────────────
NAUKRI_EMAIL = os.getenv("NAUKRI_EMAIL", "")
NAUKRI_PASSWORD = os.getenv("NAUKRI_PASSWORD", "")

# ── Adzuna API (optional — free tier) ────────────────────────────────────────
ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID", "")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY", "")
ADZUNA_COUNTRY = os.getenv("ADZUNA_COUNTRY", "in")  # 'in' for India

# ── Scraper Settings ─────────────────────────────────────────────────────────
REQUEST_DELAY_MIN = float(os.getenv("REQUEST_DELAY_MIN", "1.0"))
REQUEST_DELAY_MAX = float(os.getenv("REQUEST_DELAY_MAX", "3.0"))
MAX_JOBS_PER_SOURCE = int(os.getenv("MAX_JOBS_PER_SOURCE", "50"))

# ── Database ──────────────────────────────────────────────────────────────────
DATABASE_PATH = os.getenv("DATABASE_PATH", "jobs.db")

# ── Dashboard ─────────────────────────────────────────────────────────────────
DASHBOARD_HOST = os.getenv("DASHBOARD_HOST", "127.0.0.1")
DASHBOARD_PORT = int(os.getenv("DASHBOARD_PORT", "5000"))
DASHBOARD_DEBUG = os.getenv("DASHBOARD_DEBUG", "False").lower() == "true"

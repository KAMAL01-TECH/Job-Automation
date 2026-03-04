"""
database.py — SQLite database setup and helper functions for the Job Automation system.
"""

import sqlite3
import json
from datetime import datetime
import config


def get_connection():
    """Return a new SQLite connection to the configured database file."""
    conn = sqlite3.connect(config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables if they don't already exist."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript(
        """
        CREATE TABLE IF NOT EXISTS jobs (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT NOT NULL,
            company     TEXT,
            location    TEXT,
            salary      TEXT,
            description TEXT,
            url         TEXT UNIQUE,
            source      TEXT,
            tags        TEXT,          -- JSON list stored as text
            posted_date TEXT,
            scraped_at  TEXT,
            is_applied  INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS applications (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id       INTEGER,
            job_title    TEXT,
            company      TEXT,
            status       TEXT DEFAULT 'applied',
            cover_letter TEXT,
            applied_at   TEXT,
            notes        TEXT,
            FOREIGN KEY (job_id) REFERENCES jobs(id)
        );
        """
    )

    conn.commit()
    conn.close()


def save_job(job: dict) -> int | None:
    """
    Insert a job into the database.

    Returns the new row id, or None if the URL already exists (duplicate).
    """
    conn = get_connection()
    cursor = conn.cursor()

    tags = job.get("tags", [])
    tags_str = json.dumps(tags) if isinstance(tags, list) else str(tags)

    try:
        cursor.execute(
            """
            INSERT INTO jobs
                (title, company, location, salary, description, url,
                 source, tags, posted_date, scraped_at, is_applied)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
            """,
            (
                job.get("title", ""),
                job.get("company", ""),
                job.get("location", ""),
                job.get("salary", ""),
                job.get("description", ""),
                job.get("url", ""),
                job.get("source", ""),
                tags_str,
                job.get("posted_date", ""),
                datetime.now().isoformat(),
            ),
        )
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        # Duplicate URL — job already in database
        return None
    finally:
        conn.close()


def save_application(application: dict) -> int:
    """Insert an application record and mark the corresponding job as applied."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO applications
            (job_id, job_title, company, status, cover_letter, applied_at, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            application.get("job_id"),
            application.get("job_title", ""),
            application.get("company", ""),
            application.get("status", "applied"),
            application.get("cover_letter", ""),
            application.get("applied_at", datetime.now().isoformat()),
            application.get("notes", ""),
        ),
    )

    # Mark the job as applied
    if application.get("job_id"):
        cursor.execute(
            "UPDATE jobs SET is_applied = 1 WHERE id = ?",
            (application["job_id"],),
        )

    conn.commit()
    row_id = cursor.lastrowid
    conn.close()
    return row_id


def get_unapplied_jobs(source: str | None = None) -> list[dict]:
    """
    Return jobs that haven't been applied to yet.

    Optionally filter by source (e.g. 'naukri').
    """
    conn = get_connection()
    cursor = conn.cursor()

    if source:
        cursor.execute(
            "SELECT * FROM jobs WHERE is_applied = 0 AND source = ? ORDER BY scraped_at DESC",
            (source,),
        )
    else:
        cursor.execute(
            "SELECT * FROM jobs WHERE is_applied = 0 ORDER BY scraped_at DESC"
        )

    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_all_jobs(limit: int = 200) -> list[dict]:
    """Return the most recent jobs (applied and unapplied)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM jobs ORDER BY scraped_at DESC LIMIT ?", (limit,)
    )
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_stats() -> dict:
    """Return aggregate statistics for the dashboard."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM jobs")
    total_jobs = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM jobs WHERE is_applied = 1")
    total_applied = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM applications WHERE status = 'interview'")
    total_interviews = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM applications WHERE status = 'offer'")
    total_offers = cursor.fetchone()[0]

    conn.close()
    return {
        "total_jobs": total_jobs,
        "total_applied": total_applied,
        "total_interviews": total_interviews,
        "total_offers": total_offers,
    }


# Initialise the database when this module is first imported
init_db()

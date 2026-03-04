"""
dashboard.py — Simple Flask web dashboard for the Job Automation system.

Run with: python dashboard.py
Then open: http://127.0.0.1:5000
"""

import json
from flask import Flask, render_template_string, jsonify

import config
import database

app = Flask(__name__)

# ── HTML template (dark theme, embedded) ─────────────────────────────────────
DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Job Automation Dashboard</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { background: #0f172a; color: #e2e8f0; font-family: 'Segoe UI', sans-serif; padding: 24px; }
    h1 { font-size: 1.8rem; margin-bottom: 4px; }
    .subtitle { color: #94a3b8; margin-bottom: 24px; font-size: 0.9rem; }
    .free-badge {
      display: inline-block; background: #16a34a; color: #fff;
      padding: 3px 10px; border-radius: 20px; font-size: 0.75rem; margin-bottom: 24px;
    }

    /* Stats cards */
    .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 16px; margin-bottom: 32px; }
    .stat-card {
      background: #1e293b; border: 1px solid #334155; border-radius: 12px;
      padding: 20px; text-align: center;
    }
    .stat-card .number { font-size: 2.4rem; font-weight: 700; color: #38bdf8; }
    .stat-card .label { font-size: 0.8rem; color: #94a3b8; margin-top: 4px; }

    /* Table */
    .table-wrapper { overflow-x: auto; }
    table { width: 100%; border-collapse: collapse; }
    thead { background: #1e293b; }
    th { padding: 12px 14px; text-align: left; font-size: 0.8rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; }
    tbody tr { border-bottom: 1px solid #1e293b; }
    tbody tr:hover { background: #1e293b; }
    td { padding: 12px 14px; font-size: 0.88rem; vertical-align: middle; }
    a { color: #38bdf8; text-decoration: none; }
    a:hover { text-decoration: underline; }

    /* Source badges */
    .badge {
      display: inline-block; padding: 2px 8px; border-radius: 12px;
      font-size: 0.72rem; font-weight: 600; text-transform: uppercase;
    }
    .badge-naukri     { background: #7c3aed; color: #ede9fe; }
    .badge-linkedin   { background: #0369a1; color: #e0f2fe; }
    .badge-indeed     { background: #b45309; color: #fef3c7; }
    .badge-remoteok   { background: #065f46; color: #d1fae5; }
    .badge-adzuna     { background: #9f1239; color: #ffe4e6; }
    .badge-themuse    { background: #4c1d95; color: #ede9fe; }
    .badge-arbeitnow  { background: #1e40af; color: #dbeafe; }
    .badge-default    { background: #374151; color: #d1d5db; }

    /* Status badges */
    .status-applied   { background: #16a34a; color: #dcfce7; }
    .status-pending   { background: #92400e; color: #fef3c7; }
  </style>
</head>
<body>
  <h1>🤖 Job Automation Dashboard</h1>
  <p class="subtitle">Auto Job Search &amp; Apply — Python · SQLite · Flask</p>
  <span class="free-badge">💚 100% FREE — No Money Spent!</span>

  <!-- Stats cards -->
  <div class="stats-grid">
    <div class="stat-card">
      <div class="number">{{ stats.total_jobs }}</div>
      <div class="label">Total Jobs Found</div>
    </div>
    <div class="stat-card">
      <div class="number">{{ stats.total_applied }}</div>
      <div class="label">Applied</div>
    </div>
    <div class="stat-card">
      <div class="number">{{ stats.total_interviews }}</div>
      <div class="label">Interviews</div>
    </div>
    <div class="stat-card">
      <div class="number">{{ stats.total_offers }}</div>
      <div class="label">Offers</div>
    </div>
  </div>

  <!-- Jobs table -->
  <div class="table-wrapper">
    <table>
      <thead>
        <tr>
          <th>#</th>
          <th>Title</th>
          <th>Company</th>
          <th>Location</th>
          <th>Salary</th>
          <th>Source</th>
          <th>Status</th>
          <th>Link</th>
        </tr>
      </thead>
      <tbody>
        {% for job in jobs %}
        <tr>
          <td>{{ loop.index }}</td>
          <td>{{ job.title }}</td>
          <td>{{ job.company }}</td>
          <td>{{ job.location }}</td>
          <td>{{ job.salary or '—' }}</td>
          <td><span class="badge badge-{{ job.source or 'default' }}">{{ job.source or 'unknown' }}</span></td>
          <td>
            {% if job.is_applied %}
              <span class="badge status-applied">Applied</span>
            {% else %}
              <span class="badge status-pending">Pending</span>
            {% endif %}
          </td>
          <td><a href="{{ job.url }}" target="_blank" rel="noopener noreferrer">View →</a></td>
        </tr>
        {% else %}
        <tr><td colspan="8" style="text-align:center; padding:40px; color:#64748b;">
          No jobs yet — run a search to populate the database.
        </td></tr>
        {% endfor %}
      </tbody>
    </table>
  </div>
</body>
</html>
"""


@app.route("/")
def index():
    stats = database.get_stats()
    jobs = database.get_all_jobs(limit=200)
    return render_template_string(DASHBOARD_TEMPLATE, stats=stats, jobs=jobs)


@app.route("/api/stats")
def api_stats():
    return jsonify(database.get_stats())


@app.route("/api/jobs")
def api_jobs():
    return jsonify(database.get_all_jobs(limit=200))


def run_dashboard():
    """Start the Flask development server."""
    print(f"\n🖥  Dashboard running at http://{config.DASHBOARD_HOST}:{config.DASHBOARD_PORT}")
    app.run(
        host=config.DASHBOARD_HOST,
        port=config.DASHBOARD_PORT,
        debug=config.DASHBOARD_DEBUG,
    )


if __name__ == "__main__":
    run_dashboard()

# 🤖 Job Automation — Auto Job Search & Auto Apply

> **100% FREE** — No paid APIs, no credit card, no cloud subscription needed.

Automatically search multiple job boards and apply to matching positions — all from a single Python project backed by a local SQLite database.

---

## ✨ Features

| Feature | Details |
|---|---|
| 🔍 Multi-platform search | LinkedIn, Naukri, Indeed, RemoteOK, Adzuna, The Muse, Arbeitnow |
| 📝 Auto-apply | Selenium-based auto-apply on Naukri.com |
| 💌 Cover letter generator | Template-based, no OpenAI / paid API |
| 🗄️ SQLite database | No server, no setup — just a local `.db` file |
| 🖥️ Web dashboard | Dark-theme Flask dashboard with stats & job table |
| ⏰ Scheduler | Search every 6 h · Auto-apply every 12 h |
| 💚 100% FREE | Zero cost — no paid APIs |

---

## 🛠️ Supported Job Platforms (all FREE)

| Platform | Method | API Key? |
|---|---|---|
| **LinkedIn** | Guest Jobs API | ❌ Not needed |
| **Naukri.com** | Internal search API | ❌ Not needed |
| **Indeed.co.in** | HTML scraping (BeautifulSoup) | ❌ Not needed |
| **RemoteOK** | Public JSON API | ❌ Not needed |
| **The Muse** | Public JSON API | ❌ Not needed |
| **Arbeitnow** | Public JSON API | ❌ Not needed |
| **Adzuna** | Free-tier REST API | ✅ Free sign-up |

---

## ⚡ Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/KAMAL01-TECH/Job-Automation.git
cd Job-Automation

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure your details
cp .env.example .env
# Edit .env with your name, email, job keywords, etc.

# 4. Run!
python run.py
```

---

## 📦 Installation

### Prerequisites
- Python 3.10+
- Google Chrome + ChromeDriver (only needed for Naukri auto-apply)

### Install Python dependencies

```bash
pip install -r requirements.txt
```

### (Optional) ChromeDriver for Naukri auto-apply

Download ChromeDriver matching your Chrome version from  
https://chromedriver.chromium.org/downloads  
and place it somewhere on your `PATH`.

---

## 🚀 Usage

### Interactive CLI

```bash
python run.py
```

You will see an ASCII art banner and a numbered menu:

```
  1. 🔍  Search Jobs Now
  2. 📝  Auto-Apply to Pending Jobs
  3. 🖥️   Open Dashboard
  4. ⏰  Start Auto-Scheduler
  5. 📊  View Stats
  6. 🚪  Exit
```

### Command-line Arguments

```bash
python run.py search      # Search all platforms immediately
python run.py apply       # Auto-apply to pending Naukri jobs
python run.py dashboard   # Open Flask dashboard at http://127.0.0.1:5000
python run.py auto        # Start the background scheduler
python run.py stats       # Print database statistics
```

---

## ⚙️ Configuration

Copy `.env.example` to `.env` and edit it:

```ini
# Your details
USER_NAME=Jane Doe
USER_EMAIL=jane@example.com
USER_PHONE=+91-9876543210
RESUME_PATH=resume.pdf

# Job search preferences
JOB_KEYWORDS=Python Developer,Backend Engineer
JOB_LOCATION=India
EXPERIENCE_YEARS=3

# Naukri auto-apply (leave blank to skip)
NAUKRI_EMAIL=jane@example.com
NAUKRI_PASSWORD=supersecret

# Adzuna free API (optional — sign up at developer.adzuna.com)
ADZUNA_APP_ID=
ADZUNA_APP_KEY=
ADZUNA_COUNTRY=in
```

---

## 🗂️ Project Structure

```
Job-Automation/
├── config.py              ← Load settings from .env
├── database.py            ← SQLite helpers (jobs + applications tables)
├── run.py                 ← CLI entry point with interactive menu
├── dashboard.py           ← Flask web dashboard
├── cover_letter.py        ← Template-based cover letter generator
├── scheduler.py           ← Automated search + apply scheduler
├── scrapers/
│   ├── __init__.py
│   ├── linkedin_free.py   ← LinkedIn guest API scraper
│   ├── naukri_free.py     ← Naukri internal API scraper
│   ├── indeed_free.py     ← Indeed.co.in HTML scraper
│   ├── remoteok_free.py   ← RemoteOK public API
│   ├── adzuna_free.py     ← Adzuna free-tier API
│   ├── themuse_free.py    ← The Muse public API
│   ├── arbeitnow_free.py  ← Arbeitnow public API
│   └── all_scrapers.py    ← Run all scrapers, deduplicate, save to DB
├── applier/
│   ├── __init__.py
│   └── naukri_apply.py    ← Selenium auto-apply on Naukri.com
├── requirements.txt
├── .env.example
└── README.md
```

---

## 💰 Cost Breakdown

| Component | Cost |
|---|---|
| All job scraping | **₹0 / $0** |
| SQLite database | **₹0 / $0** |
| Flask dashboard | **₹0 / $0** |
| Cover letter generation | **₹0 / $0** |
| Adzuna API (optional) | **₹0 / $0** (250 req/month free) |
| Selenium browser | **₹0 / $0** |
| **Total** | **₹0 / $0 🎉** |

---

## 🖥️ Dashboard Preview

The Flask dashboard (http://127.0.0.1:5000) shows:

- **Stats cards**: Total Jobs Found · Applied · Interviews · Offers
- **Jobs table**: Title · Company · Location · Salary · Source · Status · Link
- **Colour-coded source badges**: naukri (purple) · linkedin (blue) · indeed (amber) · remoteok (green) · …
- **Status badges**: Applied (green) · Pending (orange)
- Dark background (`#0f172a`) for comfortable viewing

---

## 🤝 Contributing

Pull requests are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Commit your changes
4. Open a Pull Request

---

## ⚠️ Disclaimer

This tool is intended for personal use only. Always respect the **Terms of Service** of each job board you use it with. Automated scraping may violate some platforms' ToS — use responsibly and add adequate delays between requests. The authors are not responsible for any misuse.

"""
cover_letter.py — Template-based cover letter generator (100% FREE, no OpenAI needed).

Features:
- Multiple templates for variety (Professional, Enthusiastic, Results-focused)
- Auto-extract skills from job description using keyword matching
- Personalize with user's name and job details
- Pick template based on company name hash for consistent variety
"""

import hashlib
import re

import config

# ── Skill keywords to auto-detect from job descriptions ──────────────────────
TECH_SKILLS = [
    "Python", "Java", "JavaScript", "TypeScript", "React", "Angular", "Vue",
    "Node.js", "Django", "Flask", "FastAPI", "Spring Boot", "SQL", "NoSQL",
    "PostgreSQL", "MySQL", "MongoDB", "Redis", "Docker", "Kubernetes",
    "AWS", "Azure", "GCP", "REST API", "GraphQL", "Git", "CI/CD",
    "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "Pandas",
    "NumPy", "Scikit-learn", "Data Analysis", "Tableau", "Power BI",
    "Linux", "Bash", "Shell Scripting", "Microservices", "Agile", "Scrum",
    "DevOps", "Selenium", "Pytest", "JUnit", "HTML", "CSS", "SASS",
    "Rust", "Go", "Golang", "C++", "C#", ".NET", "PHP", "Ruby", "Kotlin",
]

# ── Cover letter templates ────────────────────────────────────────────────────
TEMPLATES = [
    # Template 0 — Professional
    """\
Dear Hiring Manager,

I am writing to express my strong interest in the {job_title} position at {company}. \
With {experience} years of experience in the field and a proven track record of delivering \
high-quality results, I am confident that my skills align perfectly with your requirements.

{skills_paragraph}

Throughout my career I have consistently demonstrated the ability to collaborate with \
cross-functional teams, meet tight deadlines, and adapt quickly to new technologies. \
I am excited about the opportunity to bring this experience to {company} and contribute \
to your continued success.

I would welcome the chance to discuss how my background and skills can benefit your team. \
Thank you for considering my application.

Sincerely,
{name}
{email} | {phone}
""",
    # Template 1 — Enthusiastic
    """\
Dear {company} Team,

I was thrilled to come across the {job_title} opening at {company}! This role is an \
excellent match for my {experience}+ years of hands-on experience and passion for \
building impactful solutions.

{skills_paragraph}

I thrive in dynamic environments where I can tackle challenging problems and continuously \
grow my skill set. Your company's reputation for innovation makes me especially eager to \
join your team and make meaningful contributions from day one.

I would love the opportunity to chat about how I can add value to {company}. \
Please feel free to reach out at your convenience.

Best regards,
{name}
{email} | {phone}
""",
    # Template 2 — Results-focused
    """\
Dear Hiring Manager,

I am excited to apply for the {job_title} position at {company}. My {experience} years \
of experience have been defined by a results-driven approach — delivering measurable \
improvements in performance, reliability, and team productivity.

{skills_paragraph}

I bring a combination of technical depth and strong communication skills, allowing me \
to bridge the gap between engineering and business objectives. I am eager to bring \
this mindset to {company} and help the team achieve its goals.

I look forward to the possibility of discussing this opportunity further.

Warm regards,
{name}
{email} | {phone}
""",
]


def extract_skills(description: str) -> list[str]:
    """
    Extract recognised skill keywords from a job description.

    Uses simple case-insensitive substring matching.
    """
    found: list[str] = []
    desc_lower = description.lower()
    for skill in TECH_SKILLS:
        if skill.lower() in desc_lower:
            found.append(skill)
    return found


def _pick_template(company: str) -> int:
    """Return a template index (0–2) deterministically based on the company name."""
    digest = int(hashlib.sha256(company.encode()).hexdigest(), 16)
    return digest % len(TEMPLATES)


def generate_cover_letter(job: dict) -> str:
    """
    Generate a personalised cover letter for the given job.

    Args:
        job: A job dict with at least 'title', 'company', and optionally 'description'.

    Returns:
        A formatted cover letter string.
    """
    job_title = job.get("title", "Software Engineer")
    company = job.get("company", "your company")
    description = job.get("description", "")

    skills = extract_skills(description)

    if skills:
        skills_paragraph = (
            f"My core technical skills include {', '.join(skills[:6])}"
            + (f", and more" if len(skills) > 6 else "")
            + ". These align directly with the requirements outlined in your job posting."
        )
    else:
        skills_paragraph = (
            "I have developed a well-rounded skill set across software development, "
            "problem-solving, and collaborative project delivery, which I am eager "
            "to apply in this role."
        )

    template_idx = _pick_template(company)
    template = TEMPLATES[template_idx]

    cover_letter = template.format(
        job_title=job_title,
        company=company,
        experience=config.EXPERIENCE_YEARS,
        skills_paragraph=skills_paragraph,
        name=config.USER_NAME,
        email=config.USER_EMAIL,
        phone=config.USER_PHONE,
    )

    return cover_letter

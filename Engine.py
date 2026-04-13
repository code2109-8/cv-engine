import os
import json
import requests
import random
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI

app = Flask(__name__)
CORS(app)

# -----------------------------
# OPENAI SETUP
# -----------------------------

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# -----------------------------
# TIER SETTINGS
# -----------------------------

TIERS = {
    "free": 3,
    "pro": 20,
    "advanced": 40
}

# -----------------------------
# NETWORKING COMPANY DATABASE
# -----------------------------

TECH_COMPANIES = [
    "Monzo",
    "Revolut",
    "DeepMind",
    "Wise",
    "Deliveroo",
    "Arm",
    "Graphcore",
    "Darktrace",
    "Ocado Technology",
    "Skyscanner"
]

# -----------------------------
# JOB SCRAPER
# -----------------------------

def scrape_jobs(role, location, limit):

    url = f"https://www.indeed.co.uk/jobs?q={role}&l={location}"

    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        res = requests.get(url, headers=headers, timeout=8)
        soup = BeautifulSoup(res.text, "html.parser")

        jobs = []
        cards = soup.select(".job_seen_beacon")[:limit]

        for card in cards:
            try:
                title = card.select_one("h2").text.strip()
                company = card.select_one(".companyName").text.strip()
                loc = card.select_one(".companyLocation").text.strip()

                jobs.append({
                    "title": title,
                    "company": company,
                    "location": loc
                })
            except:
                continue

        return jobs

    except Exception:
        return []


# -----------------------------
# LINKEDIN CONTACT SEARCH
# -----------------------------

def linkedin_search(company, role):
    company_q = company.replace(" ", "%20")
    role_q = role.replace(" ", "%20")
    return f"https://www.linkedin.com/search/results/people/?keywords={role_q}%20{company_q}"


# -----------------------------
# MAIN ENGINE
# -----------------------------

@app.route("/analyze", methods=["POST"])
def analyze():

    try:
        data = request.json

        tier = str(data.get("tier", "free")).lower().strip()
        role = data.get("career_goal", "software engineer")
        skills = data.get("skills", "")
        location = data.get("location", "United Kingdom")

        total_companies = TIERS.get(tier, TIERS["free"])

        # STEP 1: SCRAPE JOBS
        jobs = scrape_jobs(role, location, limit=min(total_companies, 10))

        if not jobs:
            return jsonify({"error": "No jobs found"})

        companies = []

        # STEP 2: HIRING COMPANY
        hiring_job = jobs[0]

        companies.append({
            "company_name": hiring_job["company"],
            "location": hiring_job["location"],
            "recommended_role": hiring_job["title"],
            "hiring_status": "hiring",
            "linkedin_contacts": {
                "engineering_manager": linkedin_search(hiring_job["company"], "Engineering Manager"),
                "technical_recruiter": linkedin_search(hiring_job["company"], "Technical Recruiter")
            }
        })

        # STEP 3: NETWORKING TARGETS
        networking_count = max(total_companies - 1, 0)
        networking_count = min(networking_count, len(TECH_COMPANIES))

        networking = random.sample(TECH_COMPANIES, networking_count)

        for comp in networking:
            companies.append({
                "company_name": comp,
                "location": location,
                "recommended_role": role,
                "hiring_status": "networking",
                "linkedin_contacts": {
                    "engineering_manager": linkedin_search(comp, "Engineering Manager"),
                    "technical_recruiter": linkedin_search(comp, "Technical Recruiter")
                }
            })

        # STEP 4: AI OUTREACH
        prompt = f"""
User skills:
{skills}

Target companies:
{companies}

Generate outreach.

Return JSON:

email_templates
linkedin_templates

Rules:

Email
- personalised
- reference company
- 3 paragraphs
- professional

LinkedIn
- under 280 characters
- friendly
- personalised

Return JSON only.
"""

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Return valid JSON only"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
            max_tokens=1200
        )

        ai_output = response.choices[0].message.content

        try:
            outreach = json.loads(ai_output)
        except:
            outreach = ai_output

        return jsonify({
            "success": True,
            "companies": companies,
            "outreach": outreach,
            "tier_used": tier,
            "company_limit": total_companies
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


# -----------------------------
# HEALTH CHECK
# -----------------------------

@app.route("/")
def home():
    return jsonify({"engine": "CareerMind AI", "status": "running"})


# -----------------------------
# RUN SERVER (Railway)
# -----------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

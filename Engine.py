import os
import json
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI

app = Flask(__name__)
CORS(app)

API_KEY = os.getenv("OPENAI_API_KEY", "missing")
client = OpenAI(api_key=API_KEY)

TIERS = {
    "free":     {"company_targets": 3,  "cv_analysis": False},
    "pro":      {"company_targets": 15, "cv_analysis": True},
    "advanced": {"company_targets": 30, "cv_analysis": True}
}

@app.route("/")
def health():
    return jsonify({"status": "CareerMind engine running", "timestamp": time.time()})

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        data = request.json
        user_id     = data.get("user_id", "anonymous")
        tier        = data.get("tier", "free")
        user_info   = data.get("user_info", {})

        tier_settings = TIERS.get(tier, TIERS["free"])
        company_count = tier_settings["company_targets"]
        cv_enabled    = tier_settings["cv_analysis"]

        location    = user_info.get("location", "UK")
        skills      = user_info.get("skills", "")
        experience  = user_info.get("experience", "")
        career_goal = user_info.get("career_goal", "")

        prompt = f"""
You are CareerMind, an elite AI career engine built specifically for tech professionals.

USER PROFILE:
- Career Goal: {career_goal}
- Skills: {skills}
- Experience: {experience}
- Location: {location}

LOCATION INSTRUCTIONS — CRITICAL:
The user is based in: {location}
You MUST find real companies physically located in or very close to {location}.
If the user specifies a city (e.g. Manchester, Leeds, Birmingham, London), prioritise companies
with offices or headquarters in that exact city first, then within 20 miles.
Do NOT suggest companies with no presence near {location}.
Only suggest remote-friendly companies as a last resort — label them clearly as remote.

CONTACT DATA STRATEGY — IMPORTANT:
DO NOT scrape or attempt to find personal emails of individuals.
Instead use the following safe and realistic hierarchy:

1. If publicly listed, use official company contact emails (e.g. careers@, hiring@, jobs@, contact@).
2. If no public email exists, infer the most likely email format based on known company patterns
   (e.g. firstname@company.com, firstname.lastname@company.com) and label it clearly as "inferred format".
3. NEVER claim to have discovered private personal emails.
4. Prefer LinkedIn outreach over email where appropriate.
5. Always prioritise LinkedIn contact paths and careers pages over guessing emails.
6. Include contact pages where possible as a safer alternative.

TASK:
Generate {company_count} real tech companies that are a strong hiring match for this person
based on their exact skills, experience, career goal, and location.

For EACH company provide every field below with no exceptions:

1. company_name
2. job_title
3. decision_maker_role
4. email_format (state if inferred or known pattern)
5. company_public_email (ONLY if publicly available, otherwise use null or "not publicly listed")
6. company_linkedin_url
7. decision_maker_linkedin_url
8. careers_page_url OR contact_page_url
9. match_percentage
10. match_reason
11. outreach_subject
12. outreach_email
13. linkedin_message (MUST be included for every company object)

💣 STRICT RULE:
Every company object MUST include ALL fields exactly as specified.
If any field is missing, the output is INVALID.

Return exactly this JSON structure:

{{
  "companies": [
    {{
      "company_name": "Monzo",
      "job_title": "Senior Backend Engineer",
      "decision_maker_role": "Head of Engineering",
      "email_format": "firstname.lastname@monzo.com (inferred pattern)",
      "company_public_email": "talent@monzo.com",
      "company_linkedin_url": "https://www.linkedin.com/company/monzo-bank/",
      "decision_maker_linkedin_url": "https://www.linkedin.com/search/results/people/?keywords=Head+of+Engineering&company=Monzo&geoUrn=102257491",
      "careers_page_url": "https://monzo.com/careers",
      "match_percentage": 91,
      "match_reason": "Your Python and distributed systems experience maps directly to Monzo's backend engineering challenges at scale.",
      "outreach_subject": "Backend engineer with Python expertise — keen to contribute at Monzo",
      "outreach_email": "Example email text",
      "linkedin_message": "Hi Monzo team, your engineering culture really stands out. My Python backend experience aligns strongly with your work and I'd love to connect."
    }}
  ],
  "cv_feedback": ["suggestion 1", "suggestion 2", "suggestion 3"]
}}
"""

        response = client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are CareerMind's precision career intelligence engine. "
                        "You must prioritise LinkedIn outreach and public contact channels over email scraping. "
                        "Never output private or scraped personal emails. "
                        "Only use public contact emails or inferred email patterns clearly labelled. "
                        "Every company object must include all fields including linkedin_message."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=4000,
            temperature=0.7
        )

        content = response.choices[0].message.content.strip()

        result = json.loads(content)

        return jsonify({
            "success": True,
            "user_id": user_id,
            "tier": tier,
            "result": result
        })

    except json.JSONDecodeError as e:
        return jsonify({"success": False, "error": f"JSON parse error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

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
        user_id   = data.get("user_id", "anonymous")
        tier      = data.get("tier", "free")
        user_info = data.get("user_info", {})

        tier_settings = TIERS.get(tier, TIERS["free"])
        company_count = tier_settings["company_targets"]
        cv_enabled    = tier_settings["cv_analysis"]

        location      = user_info.get("location", "UK")
        skills        = user_info.get("skills", "")
        experience    = user_info.get("experience", "")
        career_goal   = user_info.get("career_goal", "")

        prompt = f"""
You are CareerMind, an elite AI career engine built specifically for tech professionals.

USER PROFILE:
- Career Goal: {career_goal}
- Skills: {skills}
- Experience: {experience}
- Location: {location}

LOCATION INSTRUCTIONS — THIS IS CRITICAL:
The user is based in: {location}
You MUST find real companies physically located in or very close to {location}.
If the user specifies a city (e.g. Manchester, Leeds, Birmingham, London), prioritise companies
with offices or headquarters in that exact city first, then within 20 miles.
Do NOT suggest companies with no presence near {location}.
Only suggest remote-friendly companies as a last resort, and clearly label them as remote.

TASK:
Generate {company_count} real tech companies that are a strong hiring match for this specific person
based on their exact skills, experience, career goal, and location above.

Every piece of output must be directly informed by what the user has told you.
Do not write generic content. If the user mentions specific technologies, frameworks, or industries,
reference those explicitly throughout every field.

For EACH company provide every field below:

1. company_name

2. company_linkedin_url
   A direct LinkedIn company page URL in this format:
   https://www.linkedin.com/company/[company-name-slug]/

3. job_title

4. decision_maker_role

5. email_format

6. linkedin_search_url

7. match_percentage

8. match_reason

9. outreach_subject

10. outreach_email
   - Keep it HIGHLY personalised but slightly more concise than before
   - Use 3–4 paragraphs maximum
   - Still specific, but tighter and more direct

11. linkedin_message
    - Maximum 200 characters
    - Must be concise, natural, and personal (not templated)

{"Also provide exactly 3 specific, detailed CV improvement suggestions directly based on this user's stated experience, skills, and career goal. Each suggestion should be actionable and explain why it will help." if cv_enabled else ""}

RULES:
- Return ONLY valid JSON. No markdown, no backticks, no explanation, no extra text.
- Every field must be filled — no nulls, no empty strings, no placeholders.
- Companies must be real and near {location} — non-negotiable.
- All content must directly reference the user's actual skills, experience, and career goal.
- outreach_email and linkedin_message must feel like they were written individually for each company.
- linkedin_message must be strictly under 200 characters.
- Do not repeat the same phrases across different companies.

Return exactly this structure:

{
  "companies": [
    {
      "company_name": "Monzo",
      "company_linkedin_url": "https://www.linkedin.com/company/monzo/",
      "job_title": "Senior Backend Engineer",
      "decision_maker_role": "Head of Engineering",
      "email_format": "firstname@monzo.com",
      "linkedin_search_url": "https://www.linkedin.com/search/results/people/?keywords=Head+of+Engineering&company=Monzo&geoUrn=102257491",
      "match_percentage": 91,
      "match_reason": "Your Python and distributed systems experience maps directly to Monzo's backend engineering challenges at scale.",
      "outreach_subject": "Backend Engineer with Python and distributed systems background — excited about Monzo",
      "outreach_email": "Dear Head of Engineering,\n\nParagraph 1...\n\nParagraph 2...\n\nParagraph 3...\n\nCall to action.",
      "linkedin_message": "Hi, Monzo's work in real-time payments is impressive. My Python and distributed systems experience feels like a strong fit. Would love to connect."
    }
  ],
  "cv_feedback": ["detailed suggestion 1", "detailed suggestion 2", "detailed suggestion 3"]
}
"""

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are CareerMind's precision career intelligence engine for tech professionals. "
                        "You produce only valid JSON with highly specific, location-accurate, deeply personalised career data. "
                        "Every output must directly reference the user's actual skills, experience, and career goal. "
                        "You never write generic content. You never suggest companies outside the user's location unless remote. "
                        "Outreach emails must be concise, warm, and feel handcrafted for each company. "
                        "LinkedIn messages must be under 200 characters and feel genuinely personal."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=4000,
            temperature=0.7
        )

        content = response.choices[0].message.content.strip()

        if content.startswith("```"):
            parts = content.split("```")
            content = parts[1] if len(parts) > 1 else content
            if content.startswith("json"):
                content = content[4:]
        content = content.strip()

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

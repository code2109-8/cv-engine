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

TASK:
Generate {company_count} real tech companies that are a strong hiring match for this person
based on their exact skills, experience, career goal, and location.

Every piece of output must be directly based on what the user has told you.
Reference their specific technologies, experience, and career goal throughout every field.
Never write generic content that could apply to anyone.

For EACH company provide every field below with no exceptions:

1. company_name
   A real company name with a verified presence near {location}.

2. job_title
   The specific role this person would realistically apply for based on their skills and career goal.

3. decision_maker_role
   The most relevant hiring decision maker at this company.
   (e.g. "Head of Engineering", "VP of Data", "CTO", "Engineering Manager")

4. email_format
   The company's known email format based on their publicly known pattern.
   Be specific — not generic. e.g. "firstname@monzo.com" or "firstname.lastname@deliveroo.com"

5. company_linkedin_url
   The official LinkedIn company page URL in this format:
   https://www.linkedin.com/company/[company-slug]/
   Use the real company slug exactly as it appears on LinkedIn.
   Example: https://www.linkedin.com/company/monzo-bank/

6. decision_maker_linkedin_url
   A targeted LinkedIn people search URL to find the decision maker:
   https://www.linkedin.com/search/results/people/?keywords=[ROLE]&company=[COMPANY]&geoUrn=[GEOURN]
   GeoUrns: UK = 102257491 | USA = 103644278 | Canada = 101174742 | Australia = 101452733
   Replace spaces in keywords with +.

7. careers_page_url
   The real URL of the company's careers or jobs page where the user can find open roles and
   sometimes a contact email. Use the actual known URL for this company.
   Example: https://monzo.com/careers or https://boards.greenhouse.io/monzo

8. match_percentage
   Integer between 65 and 99 based on how well this person's specific skills match this company.

9. match_reason
   One specific sentence referencing the company's actual work AND the user's specific skills.

10. outreach_subject
    A compelling email subject line specific to this company and this user's background.
    Keep it under 12 words. Make it feel human, not automated.

11. outreach_email
    A fully written personalised cold outreach email. 4 paragraphs maximum. Keep it concise.
    - Paragraph 1: One or two sentences — something specific and genuine about this company.
    - Paragraph 2: Introduce the user and connect their SPECIFIC skills (named from profile) to what this company does.
    - Paragraph 3: One concrete example from their experience that demonstrates real value.
    - Paragraph 4: Brief call to action — suggest a short call or chat. Confident, not desperate.
    Tone: professional, warm, human. Must feel written for this company specifically.
    Total length: no more than 200 words.

12. linkedin_message
    A personalised LinkedIn connection request message. Strictly under 300 characters.
    - Reference something specific about this company
    - Mention one of the user's key skills from their profile
    - Give a clear reason to connect
    - Must not sound automated or copy-pasted
    Keep it conversational and genuine.

{"Also provide exactly 3 specific actionable CV improvement suggestions directly based on this user's stated skills, experience, and career goal. Each suggestion must be practical, explain what to change, and why it helps." if cv_enabled else ""}

RULES:
- Return ONLY valid JSON. No markdown, no backticks, no preamble, no extra text whatsoever.
- Every field must be filled — no nulls, no empty strings, no placeholders.
- Companies must be real and near {location} — non-negotiable.
- All content must directly reference the user's actual profile — never write generic filler.
- outreach_email must be under 200 words.
- linkedin_message must be under 300 characters.
- Do not repeat the same phrases or sentence structures across different companies.
- careers_page_url and company_linkedin_url must be real known URLs for that company.

Return exactly this JSON structure:

{{
  "companies": [
    {{
      "company_name": "Monzo",
      "job_title": "Senior Backend Engineer",
      "decision_maker_role": "Head of Engineering",
      "email_format": "firstname@monzo.com",
      "company_linkedin_url": "https://www.linkedin.com/company/monzo-bank/",
      "decision_maker_linkedin_url": "https://www.linkedin.com/search/results/people/?keywords=Head+of+Engineering&company=Monzo&geoUrn=102257491",
      "careers_page_url": "https://monzo.com/careers",
      "match_percentage": 91,
      "match_reason": "Your Python and distributed systems experience maps directly to Monzo's backend engineering challenges at scale.",
      "outreach_subject": "Backend engineer with Python expertise — keen to contribute at Monzo",
      "outreach_email": "Dear Head of Engineering,\\n\\nMonzo's approach to building a bank from the ground up in Python is something I've followed closely for years.\\n\\nI'm a backend engineer with 4 years of experience in Python and distributed systems — exactly the kind of work your platform runs on.\\n\\nAt my current role I reduced API response times by 40% through async refactoring across a high-traffic service — the kind of challenge I'd love to bring to Monzo's scale.\\n\\nI'd love a 15-minute chat if you have availability — happy to work around your schedule.",
      "linkedin_message": "Hi, Monzo's engineering culture and Python-first approach really stands out. My background in distributed backend systems feels like a strong fit. Would love to connect and learn more."
    }}
  ],
  "cv_feedback": ["detailed suggestion 1", "detailed suggestion 2", "detailed suggestion 3"]
}}
"""

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are CareerMind's precision career intelligence engine for tech professionals. "
                        "You produce only valid JSON with highly specific, location-accurate, deeply personalised career data. "
                        "Every output must directly reference the user's actual skills, experience, and career goal — never generic. "
                        "You never suggest companies outside the user's location unless explicitly remote. "
                        "Outreach emails must be concise, warm, and feel handwritten for each specific company — under 200 words. "
                        "LinkedIn messages must be under 300 characters and feel genuinely personal. "
                        "All URLs must be real and accurate for each company."
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

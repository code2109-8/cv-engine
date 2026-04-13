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
   A real company name with a verified presence near {location}.

2. job_title
   The specific realistic role this person would apply for based on their skills and career goal.

3. decision_maker_role
   The most relevant hiring decision maker title at this company (e.g. "Head of Engineering", "VP of Data", "CTO", "Engineering Manager").

4. email_format
   The company's known professional email format based on their publicly known pattern.
   Be specific per company — do not use a generic guess.
   Example: "firstname@monzo.com" or "firstname.lastname@deliveroo.com"

5. linkedin_search_url
   A highly targeted LinkedIn people search URL in this exact format:
   https://www.linkedin.com/search/results/people/?keywords=[ROLE]&company=[COMPANY]&geoUrn=[GEOURN]
   GeoUrns: UK = 102257491 | USA = 103644278 | Canada = 101174742 | Australia = 101452733
   Replace spaces in keywords with +. Match keywords to the decision_maker_role exactly.

6. match_percentage
   Integer between 65 and 99 reflecting how well this person's specific skills match this company.

7. match_reason
   One specific sentence referencing the company's actual known work AND the user's specific skills from their profile.

8. outreach_subject
   A compelling, specific email subject line for this company and role.
   Must reference the user's actual background, not a generic title.

9. outreach_email
   A fully written, detailed, personalised cold outreach email. Minimum 5 paragraphs.
   Structure it like this:
   - Paragraph 1: Open with something specific and genuine about this company — their product, mission, recent news, or engineering culture. Show you know them.
   - Paragraph 2: Introduce the user and directly connect their specific skills (from the profile above) to what this company does. Name the actual technologies or experience.
   - Paragraph 3: Give a concrete example of relevant experience or a project that demonstrates value. Be specific — draw from what the user shared.
   - Paragraph 4: Explain why this specific company excites the user based on their career goal.
   - Paragraph 5: Clear, confident call to action — suggest a short call or chat, not just "let me know if interested."
   Tone: professional, warm, and human. It must read like it was written specifically for this company, not copy-pasted.

10. linkedin_message
    A detailed, personalised LinkedIn connection request message. Maximum 300 characters.
    - Open with something specific about the company
    - Reference one of the user's key skills directly
    - Give a genuine reason to connect
    - Must not sound automated or templated

{"Also provide exactly 3 specific, detailed CV improvement suggestions directly based on this user's stated experience, skills, and career goal. Each suggestion should be actionable and explain why it will help." if cv_enabled else ""}

RULES:
- Return ONLY valid JSON. No markdown, no backticks, no explanation, no extra text.
- Every field must be filled — no nulls, no empty strings, no placeholders.
- Companies must be real and near {location} — non-negotiable.
- All content must directly reference the user's actual skills, experience, and career goal.
- outreach_email and linkedin_message must feel like they were written individually for each company.
- linkedin_message must be strictly under 300 characters.
- Do not repeat the same phrases across different companies.

Return exactly this structure:

{{
  "companies": [
    {{
      "company_name": "Monzo",
      "job_title": "Senior Backend Engineer",
      "decision_maker_role": "Head of Engineering",
      "email_format": "firstname@monzo.com",
      "linkedin_search_url": "https://www.linkedin.com/search/results/people/?keywords=Head+of+Engineering&company=Monzo&geoUrn=102257491",
      "match_percentage": 91,
      "match_reason": "Your Python and distributed systems experience maps directly to Monzo's backend engineering challenges at scale.",
      "outreach_subject": "Backend Engineer with Python and distributed systems background — excited about Monzo",
      "outreach_email": "Dear Head of Engineering,\\n\\nParagraph about Monzo specifically...\\n\\nParagraph connecting user skills to Monzo...\\n\\nParagraph with concrete experience example...\\n\\nParagraph about why Monzo fits career goal...\\n\\nCall to action.",
      "linkedin_message": "Hi, Monzo's approach to real-time payments is impressive. My background in Python and distributed systems feels like a strong fit for your engineering team. Would love to connect."
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
                        "Every output must directly reference the user's actual skills, experience, and career goal. "
                        "You never write generic content. You never suggest companies outside the user's location unless remote. "
                        "Outreach emails must be detailed, warm, and feel handwritten for each specific company. "
                        "LinkedIn messages must be under 300 characters and feel genuinely personal."
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

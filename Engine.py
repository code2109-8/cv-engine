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

        location = user_info.get("location", "UK")

        prompt = f"""
You are CareerMind, an elite AI career engine built specifically for tech professionals.

USER PROFILE:
{json.dumps(user_info, indent=2)}

LOCATION INSTRUCTIONS — THIS IS CRITICAL:
The user is based in: {location}
You MUST find real companies that are physically located in or very close to {location}.
If the user is in a specific city (e.g. Manchester, Birmingham, Leeds, London), prioritise companies
with offices or headquarters in that exact city first, then within 20 miles.
Do NOT suggest companies that have no presence near {location}.
Only suggest remote-friendly global companies as a last resort if local options are limited,
and clearly note they are remote.

TASK:
Generate {company_count} real tech companies that are a strong hiring match for this person
based on their skills, experience, career goal, AND location.

For EACH company provide every field below:

1. company_name — real company name with a presence near {location}
2. job_title — specific realistic role this person would apply for
3. decision_maker_role — the most relevant hiring decision maker title (e.g. "Head of Engineering", "CTO", "Engineering Manager")
4. email_format — the company's known professional email format as a best guess
   (e.g. "firstname@monzo.com" or "firstname.lastname@company.com")
   Base this on the company's publicly known email pattern. Be specific per company.
5. linkedin_search_url — a highly targeted LinkedIn people search URL constructed like this:
   https://www.linkedin.com/search/results/people/?keywords=[ROLE]&company=[COMPANY]&geoUrn=[GEOURN]
   Use the correct geoUrn for the user's country:
   UK = 102257491 | USA = 103644278 | Canada = 101174742 | Australia = 101452733
   For other countries use the correct LinkedIn geoUrn.
   Make keywords match the decision_maker_role exactly, replacing spaces with +
6. match_percentage — integer between 65 and 99
7. match_reason — one specific sentence referencing the company's actual work and the user's skills
8. outreach_subject — a compelling specific email subject line
9. outreach_email — a fully written personalised outreach email (4-6 paragraphs):
   - Address the decision maker by role naturally (e.g. "Dear Head of Engineering,")
   - Mention something real and specific about the company
   - Connect the user's actual skills to that company's needs
   - Professional, warm, human tone — not stiff or templated
   - End with a clear confident call to action
10. linkedin_message — a short punchy LinkedIn connection request message (strictly under 300 characters):
    - Reference something specific about the company
    - Mention the user's most relevant skill
    - End with a reason to connect
    - Must feel personal and genuine, not like a mass message

{"Also provide exactly 3 specific actionable CV improvement suggestions tailored to this user's experience and career goal." if cv_enabled else ""}

RULES:
- Return ONLY valid JSON. No markdown, no backticks, no explanation, no extra text whatsoever.
- Every single field must be filled — no nulls, no empty strings, no placeholders.
- Companies must be real and located near {location} — this is non-negotiable.
- Outreach emails and LinkedIn messages must feel individually written, not templated.
- Email formats should reflect each company's actual known pattern, not a generic guess.
- linkedin_message must be strictly under 300 characters.

Return exactly this structure:

{{
  "companies": [
    {{
      "company_name": "Bet365",
      "job_title": "Senior Software Engineer",
      "decision_maker_role": "Head of Engineering",
      "email_format": "firstname.lastname@bet365.com",
      "linkedin_search_url": "https://www.linkedin.com/search/results/people/?keywords=Head+of+Engineering&company=Bet365&geoUrn=102257491",
      "match_percentage": 88,
      "match_reason": "Your Python and backend experience aligns with Bet365's high-traffic platform engineering needs based in Stoke-on-Trent.",
      "outreach_subject": "Senior Software Engineer with high-scale backend experience — interested in Bet365",
      "outreach_email": "Dear Head of Engineering,\\n\\nI've been following Bet365's engineering work and was particularly impressed by your approach to handling millions of concurrent users during live events...\\n\\n",
      "linkedin_message": "Hi, I've been following Bet365's engineering work — the real-time scale you handle is impressive. My Python and backend background feels like a strong fit. Would love to connect."
    }}
  ],
  "cv_feedback": ["suggestion 1", "suggestion 2", "suggestion 3"]
}}
"""

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are CareerMind's precision career intelligence engine for tech professionals. "
                        "You produce only valid JSON with highly specific, location-accurate career data. "
                        "You never suggest companies outside the user's location unless they are explicitly remote-friendly. "
                        "Every output is tailored, real, and immediately actionable. "
                        "LinkedIn messages must be strictly under 300 characters and feel genuinely personal."
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

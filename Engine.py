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
    "free": {"company_targets": 3, "cv_analysis": False},
    "pro": {"company_targets": 15, "cv_analysis": True},
    "advanced": {"company_targets": 30, "cv_analysis": True}
}

user_usage = {}

@app.route("/")
def health():
    return jsonify({"status": "CareerMind engine running", "timestamp": time.time()})

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        data = request.json
        user_id = data.get("user_id", "anonymous")
        tier = data.get("tier", "free")
        user_info = data.get("user_info", {})
        tier_settings = TIERS.get(tier, TIERS["free"])
        company_count = tier_settings["company_targets"]
        cv_enabled = tier_settings["cv_analysis"]

        prompt = f"""
You are an elite AI career engine for tech professionals.

User profile:
{json.dumps(user_info)}

Your task is to generate {company_count} real UK or global tech companies that are likely hiring for this person's skills.

For each company you MUST provide:
- A real company name
- The likely job title this person would apply for at that company
- A realistic decision maker name (e.g. Head of Engineering, CTO, Engineering Manager)
- A realistic professional email for that decision maker based on the company's known email format
- A realistic LinkedIn search URL for that decision maker like https://www.linkedin.com/search/results/people/?keywords=Head+of+Engineering+DeepMind
- A match percentage between 60 and 99 based on how well the person fits
- A personalised outreach email subject line for that specific company
- A personalised outreach email body for that specific company referencing their actual work and the user's specific skills
- One sentence explaining why this company is a good match

{"Also provide 3 specific CV improvement suggestions based on the user's experience." if cv_enabled else ""}

Return ONLY a JSON object with NO extra text, NO markdown, NO backticks. Exactly this structure:

{{
  "companies": [
    {{
      "company_name": "DeepMind",
      "job_title": "Software Engineer",
      "decision_maker_name": "Sarah Johnson",
      "decision_maker_role": "Head of Engineering",
      "email": "s.johnson@deepmind.com",
      "linkedin_url": "https://www.linkedin.com/search/results/people/?keywords=Head+of+Engineering+DeepMind",
      "match_percentage": 92,
      "match_reason": "Your Python and ML skills align directly with DeepMind's research engineering teams.",
      "outreach_subject": "Software Engineer with ML background — keen to contribute at DeepMind",
      "outreach_email": "Dear Sarah,\\n\\nI came across DeepMind's recent work on AlphaFold and was genuinely impressed..."
    }}
  ],
  "cv_feedback": ["suggestion 1", "suggestion 2", "suggestion 3"]
}}
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a precise career intelligence engine. You return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=4000
        )

        content = response.choices[0].message.content.strip()

        # Clean any accidental markdown
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        content = content.strip()

        result = json.loads(content)

        return jsonify({
            "success": True,
            "tier": tier,
            "result": result
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

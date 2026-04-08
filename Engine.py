import os
import json
import time
from flask import Flask, request, jsonify
from openai import OpenAI
from flask_cors import CORS

# ---------------------------------------------------
# APPLICATION SETUP
# ---------------------------------------------------

app = Flask(__name__)
CORS(app)

# ---------------------------------------------------
# ENVIRONMENT CONFIGURATION
# ---------------------------------------------------

API_KEY = os.getenv("OPENAI_API_KEY", "missing")

client = OpenAI(api_key=API_KEY)

# ---------------------------------------------------
# TIER CONFIGURATION
# ---------------------------------------------------

TIERS = {
    "free": {
        "max_requests": 5,
        "cv_analysis": False,
        "company_targets": 3
    },
    "pro": {
        "max_requests": 20,
        "cv_analysis": True,
        "company_targets": 10
    },
    "advanced": {
        "max_requests": 50,
        "cv_analysis": True,
        "company_targets": 20
    }
}

# ---------------------------------------------------
# SIMPLE MEMORY STORE
# (temporary until database added)
# ---------------------------------------------------

user_usage = {}

# ---------------------------------------------------
# HEALTH CHECK ENDPOINT
# ---------------------------------------------------

@app.route("/")
def health():
    return jsonify({
        "status": "CareerMind engine running",
        "timestamp": time.time()
    })


# ---------------------------------------------------
# USAGE TRACKING
# ---------------------------------------------------

def check_usage(user_id, tier):

    tier_settings = TIERS.get(tier, TIERS["free"])

    max_requests = tier_settings["max_requests"]

    if user_id not in user_usage:
        user_usage[user_id] = 0

    if user_usage[user_id] >= max_requests:

        return False, max_requests

    user_usage[user_id] += 1

    return True, max_requests


# ---------------------------------------------------
# INPUT VALIDATION
# ---------------------------------------------------

def validate_user_info(user_info):

    if not isinstance(user_info, dict):
        return False, "user_info must be a dictionary"

    if "career_goal" not in user_info:
        return False, "career_goal missing"

    if "skills" not in user_info:
        return False, "skills missing"

    return True, None


# ---------------------------------------------------
# PROMPT BUILDER
# ---------------------------------------------------

def build_prompt(user_info, tier_settings):

    company_count = tier_settings["company_targets"]

    cv_enabled = tier_settings["cv_analysis"]

    base_prompt = f"""
You are an elite career intelligence engine.

User profile:
{json.dumps(user_info)}

Generate:

1. {company_count} companies they should apply to
2. realistic recruiter email format
3. outreach message template
4. estimated match percentage
5. strategy to stand out
"""

    if cv_enabled:

        base_prompt += """

6. CV improvement suggestions
"""

    base_prompt += """

Return JSON with fields:

companies
emails
outreach_message
match_score
strategy
cv_feedback
"""

    return base_prompt


# ---------------------------------------------------
# OPENAI ENGINE
# ---------------------------------------------------

def run_ai_engine(prompt):

    try:

        response = client.chat.completions.create(

            model="gpt-4.1-mini",

            messages=[
                {
                    "role": "system",
                    "content": "You generate precise job acquisition strategies."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]

        )

        content = response.choices[0].message.content

        return content

    except Exception as e:

        return {"error": str(e)}


# ---------------------------------------------------
# OUTPUT PARSER
# ---------------------------------------------------

def format_engine_output(ai_response):

    if isinstance(ai_response, dict):
        return ai_response

    return {
        "analysis": ai_response
    }


# ---------------------------------------------------
# CORE ENGINE FUNCTION
# ---------------------------------------------------

def generate_job_strategy(user_info, tier):

    tier_settings = TIERS.get(tier, TIERS["free"])

    prompt = build_prompt(user_info, tier_settings)

    ai_response = run_ai_engine(prompt)

    formatted_output = format_engine_output(ai_response)

    return formatted_output


# ---------------------------------------------------
# MAIN API ENDPOINT
# ---------------------------------------------------

@app.route("/analyze", methods=["POST"])
def analyze():

    try:

        data = request.json

        user_id = data.get("user_id", "anonymous")

        tier = data.get("tier", "free")

        user_info = data.get("user_info", {})

        # ---------------------------
        # VALIDATE INPUT
        # ---------------------------

        valid, error = validate_user_info(user_info)

        if not valid:

            return jsonify({
                "success": False,
                "error": error
            }), 400

        # ---------------------------
        # CHECK USAGE LIMIT
        # ---------------------------

        allowed, limit = check_usage(user_id, tier)

        if not allowed:

            return jsonify({
                "success": False,
                "error": "Tier usage limit reached",
                "limit": limit
            }), 403

        # ---------------------------
        # RUN ENGINE
        # ---------------------------

        result = generate_job_strategy(user_info, tier)

        # ---------------------------
        # RETURN RESPONSE
        # ---------------------------

        return jsonify({

            "success": True,

            "tier": tier,

            "usage": user_usage[user_id],

            "result": result

        })

    except Exception as e:

        return jsonify({

            "success": False,

            "error": str(e)

        }), 500


# ---------------------------------------------------
# DEBUG ENDPOINT
# ---------------------------------------------------

@app.route("/debug/tiers")
def debug_tiers():

    return jsonify(TIERS)


# ---------------------------------------------------
# LOCAL RUN SUPPORT
# ---------------------------------------------------

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 10000))

    app.run(

        host="0.0.0.0",

        port=port

    )




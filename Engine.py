# ai_job_engine.py

from openai import OpenAI

# ---------------------------
# CONFIG: Add your API key here
# ---------------------------
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ---------------------------
# TIER CONFIGURATION
# ---------------------------
TIERS = {
    "free": {"max_messages": 5, "cv_analysis": False},
    "pro": {"max_messages": 20, "cv_analysis": True},
    "advanced": {"max_messages": 50, "cv_analysis": True}
}

# ---------------------------
# ENGINE FUNCTIONS
# ---------------------------

def generate_role_blueprint(user_info):
    """
    Generates company suggestions, contact info, message templates,
    match percentage, and CV suggestions (for Pro/Advanced).
    """
    tier = user_info.get("tier", "free").lower()
    tier_settings = TIERS.get(tier, TIERS["free"])

    prompt = f"""
    You are a smart career AI assistant. Use this user info to:
    1. Suggest companies the user could target for jobs.
    2. Find public emails of main company contacts and LinkedIn links for heads.
    3. Create a personalized email and LinkedIn template for outreach.
    4. Give a percentage match of user skills to company roles.
    5. If tier allows, provide CV improvement suggestions.

    User Info:
    Name: {user_info.get('name')}
    CV/Skills: {user_info.get('cv')}
    Location: {user_info.get('location')}
    Tier: {tier}
    Max messages allowed this month: {tier_settings['max_messages']}

    Respond in JSON with keys:
    - company_name
    - contact_email
    - linkedin
    - email_template
    - linkedin_template
    - match_percent
    - cv_suggestions (empty list if not available)
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful AI career assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    # Extract text
    ai_text = response.choices[0].message.content

    # Try to parse JSON returned by AI
    import json
    try:
        data = json.loads(ai_text)
    except json.JSONDecodeError:
        # If AI fails to return proper JSON, return raw text
        data = {"raw_output": ai_text}

    return data

# ---------------------------
# EXAMPLE USAGE
# ---------------------------

if __name__ == "__main__":
    # Example user info (this would come from your website form)
    user_info_example = {
        "name": "John Doe",
        "cv": "Python, SQL, Backend development, startup experience",
        "location": "London, UK",
        "tier": "pro"  # 'free', 'pro', or 'advanced'
    }

    output = generate_role_blueprint(user_info_example)

    # Print the result
    import pprint
    pprint.pprint(output)

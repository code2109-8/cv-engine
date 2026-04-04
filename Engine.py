# ai_job_engine_safe.py

import os
import json
from openai import OpenAI
from flask import Flask
app = Flask(__name__)
@app.route("/")
def home():
    return {"status": "running"}

# ---------------------------
# CONFIG: Use environment variable for API key
# ---------------------------
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
    Wrapped safely so it won't crash the server.
    """
    try:
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

        # Extract AI response text
        ai_text = response.choices[0].message.content

        # Try parsing JSON
        try:
            data = json.loads(ai_text)
        except json.JSONDecodeError:
            data = {"raw_output": ai_text}

        # Ensure CV suggestions key exists
        if "cv_suggestions" not in data:
            data["cv_suggestions"] = [] if not tier_settings["cv_analysis"] else ["See AI output"]

        return data

    except Exception as e:
        # Safety net: return error info without crashing
        return {
            "status": "error",
            "message": f"Engine error caught safely: {str(e)}",
            "input_received": user_info
        }

# ---------------------------
# EXAMPLE USAGE (for local testing only)
# ---------------------------
if __name__ == "__main__":
    user_info_example = {
        "name": "John Doe",
        "cv": "Python, SQL, Backend development, startup experience",
        "location": "London, UK",
        "tier": "pro"
    }

    output = generate_role_blueprint(user_info_example)

    import pprint
    pprint.pprint(output)

# ---------------------------
# TECH NICHE SPECIALIZATION
# ---------------------------

def apply_tech_niche(prompt, user_info):
    """
    Modifies the prompt to focus specifically on tech graduate roles.
    """

    tech_focus = f"""
    This user is targeting entry-level TECHNOLOGY roles.

    Focus on companies hiring for:
    - Software Engineering
    - Data Analytics / Data Science
    - Cybersecurity
    - AI / Machine Learning
    - Cloud / DevOps
    - Backend / Full Stack Development

    Prioritize:
    - UK tech companies
    - Tech startups
    - SaaS companies
    - Cybersecurity firms
    - AI companies
    - Fintech companies

    Prefer companies that hire:
    - graduates
    - interns
    - junior developers

    The user is likely a tech graduate seeking their first role.

    User Skills:
    {user_info.get('cv')}

    Match companies to these skills and give realistic match percentages.
    """

    return prompt + tech_focus

# -------------------------------
# CareerMind Premium Intelligence
# -------------------------------

def enhance_tech_results(results, user_skills, tier):
    """
    Adds advanced analysis for Pro and Advanced tiers.
    Free tier receives basic results only.
    """

    # Free users get basic output
    if tier.lower() == "free":
        return results

    enhanced_results = []

    for company in results:

        # PRO + ADVANCED FEATURES
        if tier.lower() in ["pro", "advanced"]:

            match_reason = []

            skills = user_skills.lower()

            if "python" in skills:
                match_reason.append("Python development skills")

            if "javascript" in skills:
                match_reason.append("Frontend / JavaScript experience")

            if "aws" in skills or "cloud" in skills:
                match_reason.append("Cloud infrastructure experience")

            if "machine learning" in skills or "ai" in skills:
                match_reason.append("AI / Machine Learning background")

            if "cyber" in skills:
                match_reason.append("Cybersecurity knowledge")

            if len(match_reason) == 0:
                match_reason.append("General software development ability")

            company["why_match"] = "Your skills match this company because of: " + ", ".join(match_reason)


        # ADVANCED TIER ONLY
        if tier.lower() == "advanced":

            company["hiring_signal"] = (
                "Companies like this often hire junior engineers before jobs are publicly listed."
            )

            company["strategy_tip"] = (
                "Sending outreach to engineering managers increases response rates."
            )

        enhanced_results.append(company)

    return enhanced_results# -------------------------------
# CareerMind Premium Intelligence
# -------------------------------

def enhance_tech_results(results, user_skills, tier):
    """
    Adds advanced analysis for Pro and Advanced tiers.
    Free tier receives basic results only.
    """

    # Free users get basic output
    if tier.lower() == "free":
        return results

    enhanced_results = []

    for company in results:

        # PRO + ADVANCED FEATURES
        if tier.lower() in ["pro", "advanced"]:

            match_reason = []

            skills = user_skills.lower()

            if "python" in skills:
                match_reason.append("Python development skills")

            if "javascript" in skills:
                match_reason.append("Frontend / JavaScript experience")

            if "aws" in skills or "cloud" in skills:
                match_reason.append("Cloud infrastructure experience")

            if "machine learning" in skills or "ai" in skills:
                match_reason.append("AI / Machine Learning background")

            if "cyber" in skills:
                match_reason.append("Cybersecurity knowledge")

            if len(match_reason) == 0:
                match_reason.append("General software development ability")

            company["why_match"] = "Your skills match this company because of: " + ", ".join(match_reason)


        # ADVANCED TIER ONLY
        if tier.lower() == "advanced":

            company["hiring_signal"] = (
                "Companies like this often hire junior engineers before jobs are publicly listed."
            )

            company["strategy_tip"] = (
                "Sending outreach to engineering managers increases response rates."
            )

        enhanced_results.append(company)

    return enhanced_results# -------------------------------
# CareerMind Premium Intelligence
# -------------------------------

def enhance_tech_results(results, user_skills, tier):
    """
    Adds advanced analysis for Pro and Advanced tiers.
    Free tier receives basic results only.
    """

    # Free users get basic output
    if tier.lower() == "free":
        return results

    enhanced_results = []

    for company in results:

        # PRO + ADVANCED FEATURES
        if tier.lower() in ["pro", "advanced"]:

            match_reason = []

            skills = user_skills.lower()

            if "python" in skills:
                match_reason.append("Python development skills")

            if "javascript" in skills:
                match_reason.append("Frontend / JavaScript experience")

            if "aws" in skills or "cloud" in skills:
                match_reason.append("Cloud infrastructure experience")

            if "machine learning" in skills or "ai" in skills:
                match_reason.append("AI / Machine Learning background")

            if "cyber" in skills:
                match_reason.append("Cybersecurity knowledge")

            if len(match_reason) == 0:
                match_reason.append("General software development ability")

            company["why_match"] = "Your skills match this company because of: " + ", ".join(match_reason)


        # ADVANCED TIER ONLY
        if tier.lower() == "advanced":

            company["hiring_signal"] = (
                "Companies like this often hire junior engineers before jobs are publicly listed."
            )

            company["strategy_tip"] = (
                "Sending outreach to engineering managers increases response rates."
            )

        enhanced_results.append(company)

    return enhanced_results# -------------------------------
# CareerMind Premium Intelligence
# -------------------------------

def enhance_tech_results(results, user_skills, tier):
    """
    Adds advanced analysis for Pro and Advanced tiers.
    Free tier receives basic results only.
    """

    # Free users get basic output
    if tier.lower() == "free":
        return results

    enhanced_results = []

    for company in results:

        # PRO + ADVANCED FEATURES
        if tier.lower() in ["pro", "advanced"]:

            match_reason = []

            skills = user_skills.lower()

            if "python" in skills:
                match_reason.append("Python development skills")

            if "javascript" in skills:
                match_reason.append("Frontend / JavaScript experience")

            if "aws" in skills or "cloud" in skills:
                match_reason.append("Cloud infrastructure experience")

            if "machine learning" in skills or "ai" in skills:
                match_reason.append("AI / Machine Learning background")

            if "cyber" in skills:
                match_reason.append("Cybersecurity knowledge")

            if len(match_reason) == 0:
                match_reason.append("General software development ability")

            company["why_match"] = "Your skills match this company because of: " + ", ".join(match_reason)


        # ADVANCED TIER ONLY
        if tier.lower() == "advanced":

            company["hiring_signal"] = (
                "Companies like this often hire junior engineers before jobs are publicly listed."
            )

            company["strategy_tip"] = (
                "Sending outreach to engineering managers increases response rates."
            )

        enhanced_results.append(company)

    return enhanced_results# -------------------------------
# CareerMind Premium Intelligence
# -------------------------------

def enhance_tech_results(results, user_skills, tier):
    """
    Adds advanced analysis for Pro and Advanced tiers.
    Free tier receives basic results only.
    """

    # Free users get basic output
    if tier.lower() == "free":
        return results

    enhanced_results = []

    for company in results:

        # PRO + ADVANCED FEATURES
        if tier.lower() in ["pro", "advanced"]:

            match_reason = []

            skills = user_skills.lower()

            if "python" in skills:
                match_reason.append("Python development skills")

            if "javascript" in skills:
                match_reason.append("Frontend / JavaScript experience")

            if "aws" in skills or "cloud" in skills:
                match_reason.append("Cloud infrastructure experience")

            if "machine learning" in skills or "ai" in skills:
                match_reason.append("AI / Machine Learning background")

            if "cyber" in skills:
                match_reason.append("Cybersecurity knowledge")

            if len(match_reason) == 0:
                match_reason.append("General software development ability")

            company["why_match"] = "Your skills match this company because of: " + ", ".join(match_reason)


        # ADVANCED TIER ONLY
        if tier.lower() == "advanced":

            company["hiring_signal"] = (
                "Companies like this often hire junior engineers before jobs are publicly listed."
            )

            company["strategy_tip"] = (
                "Sending outreach to engineering managers increases response rates."
            )

        enhanced_results.append(company)

    return enhanced_results# -------------------------------
# CareerMind Premium Intelligence
# -------------------------------

def enhance_tech_results(results, user_skills, tier):
    """
    Adds advanced analysis for Pro and Advanced tiers.
    Free tier receives basic results only.
    """

    # Free users get basic output
    if tier.lower() == "free":
        return results

    enhanced_results = []

    for company in results:

        # PRO + ADVANCED FEATURES
        if tier.lower() in ["pro", "advanced"]:

            match_reason = []

            skills = user_skills.lower()

            if "python" in skills:
                match_reason.append("Python development skills")

            if "javascript" in skills:
                match_reason.append("Frontend / JavaScript experience")

            if "aws" in skills or "cloud" in skills:
                match_reason.append("Cloud infrastructure experience")

            if "machine learning" in skills or "ai" in skills:
                match_reason.append("AI / Machine Learning background")

            if "cyber" in skills:
                match_reason.append("Cybersecurity knowledge")

            if len(match_reason) == 0:
                match_reason.append("General software development ability")

            company["why_match"] = "Your skills match this company because of: " + ", ".join(match_reason)


        # ADVANCED TIER ONLY
        if tier.lower() == "advanced":

            company["hiring_signal"] = (
                "Companies like this often hire junior engineers before jobs are publicly listed."
            )

            company["strategy_tip"] = (
                "Sending outreach to engineering managers increases response rates."
            )

        enhanced_results.append(company)

    return enhanced_results# -------------------------------
# CareerMind Premium Intelligence
# -------------------------------

def enhance_tech_results(results, user_skills, tier):
    """
    Adds advanced analysis for Pro and Advanced tiers.
    Free tier receives basic results only.
    """

    # Free users get basic output
    if tier.lower() == "free":
        return results

    enhanced_results = []

    for company in results:

        # PRO + ADVANCED FEATURES
        if tier.lower() in ["pro", "advanced"]:

            match_reason = []

            skills = user_skills.lower()

            if "python" in skills:
                match_reason.append("Python development skills")

            if "javascript" in skills:
                match_reason.append("Frontend / JavaScript experience")

            if "aws" in skills or "cloud" in skills:
                match_reason.append("Cloud infrastructure experience")

            if "machine learning" in skills or "ai" in skills:
                match_reason.append("AI / Machine Learning background")

            if "cyber" in skills:
                match_reason.append("Cybersecurity knowledge")

            if len(match_reason) == 0:
                match_reason.append("General software development ability")

            company["why_match"] = "Your skills match this company because of: " + ", ".join(match_reason)


        # ADVANCED TIER ONLY
        if tier.lower() == "advanced":

            company["hiring_signal"] = (
                "Companies like this often hire junior engineers before jobs are publicly listed."
            )

            company["strategy_tip"] = (
                "Sending outreach to engineering managers increases response rates."
            )

        enhanced_results.append(company)

    return enhanced_results# -------------------------------
# CareerMind Premium Intelligence
# -------------------------------

def enhance_tech_results(results, user_skills, tier):
    """
    Adds advanced analysis for Pro and Advanced tiers.
    Free tier receives basic results only.
    """

    # Free users get basic output
    if tier.lower() == "free":
        return results

    enhanced_results = []

    for company in results:

        # PRO + ADVANCED FEATURES
        if tier.lower() in ["pro", "advanced"]:

            match_reason = []

            skills = user_skills.lower()

            if "python" in skills:
                match_reason.append("Python development skills")

            if "javascript" in skills:
                match_reason.append("Frontend / JavaScript experience")

            if "aws" in skills or "cloud" in skills:
                match_reason.append("Cloud infrastructure experience")

            if "machine learning" in skills or "ai" in skills:
                match_reason.append("AI / Machine Learning background")

            if "cyber" in skills:
                match_reason.append("Cybersecurity knowledge")

            if len(match_reason) == 0:
                match_reason.append("General software development ability")

            company["why_match"] = "Your skills match this company because of: " + ", ".join(match_reason)


        # ADVANCED TIER ONLY
        if tier.lower() == "advanced":

            company["hiring_signal"] = (
                "Companies like this often hire junior engineers before jobs are publicly listed."
            )

            company["strategy_tip"] = (
                "Sending outreach to engineering managers increases response rates."
            )

        enhanced_results.append(company)

    return enhanced_results# -------------------------------
# CareerMind Premium Intelligence
# -------------------------------

def enhance_tech_results(results, user_skills, tier):
    """
    Adds advanced analysis for Pro and Advanced tiers.
    Free tier receives basic results only.
    """

    # Free users get basic output
    if tier.lower() == "free":
        return results

    enhanced_results = []

    for company in results:

        # PRO + ADVANCED FEATURES
        if tier.lower() in ["pro", "advanced"]:

            match_reason = []

            skills = user_skills.lower()

            if "python" in skills:
                match_reason.append("Python development skills")

            if "javascript" in skills:
                match_reason.append("Frontend / JavaScript experience")

            if "aws" in skills or "cloud" in skills:
                match_reason.append("Cloud infrastructure experience")

            if "machine learning" in skills or "ai" in skills:
                match_reason.append("AI / Machine Learning background")

            if "cyber" in skills:
                match_reason.append("Cybersecurity knowledge")

            if len(match_reason) == 0:
                match_reason.append("General software development ability")

            company["why_match"] = "Your skills match this company because of: " + ", ".join(match_reason)


        # ADVANCED TIER ONLY
        if tier.lower() == "advanced":

            company["hiring_signal"] = (
                "Companies like this often hire junior engineers before jobs are publicly listed."
            )

            company["strategy_tip"] = (
                "Sending outreach to engineering managers increases response rates."
            )

        enhanced_results.append(company)

    return enhanced_results# -------------------------------
# CareerMind Premium Intelligence
# -------------------------------

def enhance_tech_results(results, user_skills, tier):
    """
    Adds advanced analysis for Pro and Advanced tiers.
    Free tier receives basic results only.
    """

    # Free users get basic output
    if tier.lower() == "free":
        return results

    enhanced_results = []

    for company in results:

        # PRO + ADVANCED FEATURES
        if tier.lower() in ["pro", "advanced"]:

            match_reason = []

            skills = user_skills.lower()

            if "python" in skills:
                match_reason.append("Python development skills")

            if "javascript" in skills:
                match_reason.append("Frontend / JavaScript experience")

            if "aws" in skills or "cloud" in skills:
                match_reason.append("Cloud infrastructure experience")

            if "machine learning" in skills or "ai" in skills:
                match_reason.append("AI / Machine Learning background")

            if "cyber" in skills:
                match_reason.append("Cybersecurity knowledge")

            if len(match_reason) == 0:
                match_reason.append("General software development ability")

            company["why_match"] = "Your skills match this company because of: " + ", ".join(match_reason)


        # ADVANCED TIER ONLY
        if tier.lower() == "advanced":

            company["hiring_signal"] = (
                "Companies like this often hire junior engineers before jobs are publicly listed."
            )

            company["strategy_tip"] = (
                "Sending outreach to engineering managers increases response rates."
            )

        enhanced_results.append(company)

    return enhanced_results# -------------------------------
# CareerMind Premium Intelligence
# -------------------------------

def enhance_tech_results(results, user_skills, tier):
    """
    Adds advanced analysis for Pro and Advanced tiers.
    Free tier receives basic results only.
    """

    # Free users get basic output
    if tier.lower() == "free":
        return results

    enhanced_results = []

    for company in results:

        # PRO + ADVANCED FEATURES
        if tier.lower() in ["pro", "advanced"]:

            match_reason = []

            skills = user_skills.lower()

            if "python" in skills:
                match_reason.append("Python development skills")

            if "javascript" in skills:
                match_reason.append("Frontend / JavaScript experience")

            if "aws" in skills or "cloud" in skills:
                match_reason.append("Cloud infrastructure experience")

            if "machine learning" in skills or "ai" in skills:
                match_reason.append("AI / Machine Learning background")

            if "cyber" in skills:
                match_reason.append("Cybersecurity knowledge")

            if len(match_reason) == 0:
                match_reason.append("General software development ability")

            company["why_match"] = "Your skills match this company because of: " + ", ".join(match_reason)


        # ADVANCED TIER ONLY
        if tier.lower() == "advanced":

            company["hiring_signal"] = (
                "Companies like this often hire junior engineers before jobs are publicly listed."
            )

            company["strategy_tip"] = (
                "Sending outreach to engineering managers increases response rates."
            )

        enhanced_results.append(company)

    return enhanced_results# -------------------------------
# CareerMind Premium Intelligence
# -------------------------------

def enhance_tech_results(results, user_skills, tier):
    """
    Adds advanced analysis for Pro and Advanced tiers.
    Free tier receives basic results only.
    """

    # Free users get basic output
    if tier.lower() == "free":
        return results

    enhanced_results = []

    for company in results:

        # PRO + ADVANCED FEATURES
        if tier.lower() in ["pro", "advanced"]:

            match_reason = []

            skills = user_skills.lower()

            if "python" in skills:
                match_reason.append("Python development skills")

            if "javascript" in skills:
                match_reason.append("Frontend / JavaScript experience")

            if "aws" in skills or "cloud" in skills:
                match_reason.append("Cloud infrastructure experience")

            if "machine learning" in skills or "ai" in skills:
                match_reason.append("AI / Machine Learning background")

            if "cyber" in skills:
                match_reason.append("Cybersecurity knowledge")

            if len(match_reason) == 0:
                match_reason.append("General software development ability")

            company["why_match"] = "Your skills match this company because of: " + ", ".join(match_reason)


        # ADVANCED TIER ONLY
        if tier.lower() == "advanced":

            company["hiring_signal"] = (
                "Companies like this often hire junior engineers before jobs are publicly listed."
            )

            company["strategy_tip"] = (
                "Sending outreach to engineering managers increases response rates."
            )

        enhanced_results.append(company)

    return enhanced_results

@app.route("/")
def health():
    return {"status": "running"}


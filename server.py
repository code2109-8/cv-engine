from flask import Flask, request, jsonify
from flask_cors import CORS
from Engine import generate_role_blueprint  # this talks to your engine

app = Flask(__name__)
CORS(app)  # allows your website to send requests to the server
# This is the route the website button will call
@app.route("/submit_cv", methods=["POST"])
def submit_cv():
    # Grab the info the user types in on the website
    user_info = {
        "name": request.form.get("name"),
        "skills": request.form.getlist("skills"),  # multiple skills possible
        "experience": request.form.get("experience"),
        "location": request.form.get("location"),  # if you added location input
        "tier": request.form.get("tier")  # we will update this later to check login
    }

    # Send info to the engine to get suggestions, templates, etc.
    output = generate_role_blueprint(user_info)

    # Send the output back to the website as JSON
    return jsonify(output)

if __name__ == "__main__":
    app.run(debug=True)
import os

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))  # Render provides PORT
    app.run(host="0.0.0.0", port=port)

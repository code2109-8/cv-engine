from flask import Flask, request, jsonify
from Engine import generate_role_blueprint

app = Flask(__name__)

# Home route (so the server responds in browser)
@app.route("/")
def home():
    return "AI Job Engine Running"

# Main endpoint
@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    result = generate_role_blueprint(data)
    return jsonify(result)

# Run server locally (Render uses gunicorn instead)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

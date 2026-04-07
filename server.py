from flask import Flask, request, jsonify
from Engine import engine_entry

app = Flask(__name__)

@app.route("/")
def home():
    return "AI Job Engine Running"

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    result = engine_entry(data)
    return jsonify(result)

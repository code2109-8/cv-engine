from flask import Flask, jsonify
from Engine import run_ai_engine  # your big engine function

app = Flask(__name__)

@app.route("/run")
def run():
    return jsonify(run_ai_engine())

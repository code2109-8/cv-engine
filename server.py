from flask import Flask, jsonify
from Engine import run_ai_engine

app = Flask(__name__)

@app.route("/run")
def run():
    result = run_ai_engine()  # only runs when /run is called
    return jsonify(result)

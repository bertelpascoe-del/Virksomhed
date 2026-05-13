import os
from flask import Flask, request, jsonify
from flask_cors import CORS

from financial_analyzer import (
    parse_documents,
    calculate_metrics,
    calculate_score_and_explanation,
    generate_summary_and_recs,
    parse_score_over_time,
)

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173"}})

TEMP_DIR = "temp_uploads"


@app.before_request
def before_request():
    os.makedirs(TEMP_DIR, exist_ok=True)


@app.teardown_request
def teardown_request(exception=None):
    if os.path.exists(TEMP_DIR):
        for name in os.listdir(TEMP_DIR):
            path = os.path.join(TEMP_DIR, name)
            if os.path.isfile(path):
                os.remove(path)


@app.route("/api/analyze", methods=["POST"])
def analyze_files():
    if "files" not in request.files:
        return jsonify({"error": "No files provided."}), 400

    paths = []

    for file in request.files.getlist("files"):
        path = os.path.join(TEMP_DIR, file.filename)
        file.save(path)
        paths.append(path)

    data, warnings = parse_documents(paths)

    if data is None:
        return jsonify({
            "error": "Could not parse financial data from the uploaded files."
        }), 400

    metrics, calc_warnings = calculate_metrics(data)

    score, details, _ = calculate_score_and_explanation(metrics)

    summary, strengths, weaknesses, recommendations = generate_summary_and_recs(
        metrics,
        warnings
    )

    score_over_time = parse_score_over_time(paths)

    return jsonify({
        "score": score,
        "description": details["description"],
        "metrics": metrics,
        "raw_metrics": {
            "revenue": data.get("Revenue", 0),
            "cogs": data.get("COGS", 0),
            "expenses": data.get("Expenses", 0),
            "debt": data.get("Debt", 0),
            "assets": data.get("Assets", 0),
            "liabilities": data.get("Liabilities", 0),
            "cashflow": data.get("CashFlow", 0),
        },
        "warnings": warnings + calc_warnings,
        "summary": summary,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "recommendations": recommendations,
        "score_over_time": score_over_time,
    })


if __name__ == "__main__":
    print("Starting Flask backend on http://localhost:5000")
    app.run(debug=True, port=5000)
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Service Endpoints
DATA_SERVICE_BASE_URL = "http://172.17.0.1:5001"
PROCESSING_URL = "https://processfunction-foletgmhuy.cn-hangzhou.fcapp.run"
RESULT_UPDATE_URL = "https://result-function-dyjqnjlgve.cn-hangzhou.fcapp.run"


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/submit", methods=["POST"])
def submit():
    submission = request.get_json()
    if not submission:
        return jsonify({"error": "Invalid JSON"}), 400

    try:
        # Create Record
        res = requests.post(f"{DATA_SERVICE_BASE_URL}/records", json=submission, timeout=10)
        res.raise_for_status()
        record = res.json()

        # Processing
        res = requests.post(PROCESSING_URL, json=record, timeout=10)
        res.raise_for_status()
        proc_result = res.json()

        # Finalize Result
        res = requests.post(RESULT_UPDATE_URL, json={
            "record_id": record["id"],
            "processing_result": proc_result
        }, timeout=10)
        res.raise_for_status()
        update_payload = res.json()

        # Sync to DB
        res = requests.put(
            f"{DATA_SERVICE_BASE_URL}/records/{update_payload['record_id']}",
            json=update_payload['update_data'],
            timeout=10
        )
        res.raise_for_status()

        return jsonify(res.json()), 200

    except requests.RequestException as e:
        return jsonify({"error": "Workflow failed", "message": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
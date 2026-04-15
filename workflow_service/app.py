from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

DATA_SERVICE_BASE_URL = "http://101.37.187.169:5001"
SUBMISSION_EVENT_URL = "https://submissfunction-xhmbeyvezh.cn-hangzhou.fcapp.run"
PROCESSING_URL = "https://processfunction-foletgmhuy.cn-hangzhou.fcapp.run"
RESULT_UPDATE_URL = "https://result-function-dyjqnjlgve.cn-hangzhou.fcapp.run"


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/submit", methods=["POST"])
def submit():
    submission = request.get_json()

    if not submission:
        return jsonify({"error": "Invalid JSON body"}), 400

    try:
        # Step 1: create initial record
        create_response = requests.post(
            f"{DATA_SERVICE_BASE_URL}/records",
            json=submission,
            timeout=10,
        )
        create_response.raise_for_status()
        created_record = create_response.json()

        # Step 2: submission event function
        event_response = requests.post(
            SUBMISSION_EVENT_URL,
            json=created_record,
            timeout=10,
        )
        event_response.raise_for_status()
        event_payload = event_response.json()

        # Step 3: processing function
        processing_response = requests.post(
            PROCESSING_URL,
            json=event_payload["submission"],
            timeout=10,
        )
        processing_response.raise_for_status()
        processing_result = processing_response.json()

        # Step 4: result update function
        result_update_response = requests.post(
            RESULT_UPDATE_URL,
            json={
                "record_id": event_payload["record_id"],
                "processing_result": processing_result
            },
            timeout=10,
        )
        result_update_response.raise_for_status()
        update_payload = result_update_response.json()

        # Step 5: update stored record
        update_response = requests.put(
            f"{DATA_SERVICE_BASE_URL}/records/{update_payload['record_id']}",
            json=update_payload["update_data"],
            timeout=10,
        )
        update_response.raise_for_status()
        updated_record = update_response.json()

        return jsonify(updated_record), 200

    except requests.RequestException as e:
        return jsonify({
            "error": "Workflow failed",
            "details": str(e)
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)

from flask import Flask, request, jsonify
import requests
import sys
from pathlib import Path

# Allow importing from the project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from functions.submission_event_function import handle_submission_event
from functions.processing_function import process_submission
from functions.result_update_function import build_result_update

app = Flask(__name__)

DATA_SERVICE_BASE_URL = "http://127.0.0.1:5001"


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/submit", methods=["POST"])
def submit():
    submission = request.get_json()

    if not submission:
        return jsonify({"error": "Invalid JSON body"}), 400

    try:
        # Step 1: Create initial record in Data Service
        create_response = requests.post(
            f"{DATA_SERVICE_BASE_URL}/records",
            json=submission,
            timeout=5,
        )
        create_response.raise_for_status()
        created_record = create_response.json()

        # Step 2: Submission Event Function
        event_payload = handle_submission_event(created_record)

        # Step 3: Processing Function
        processing_result = process_submission(event_payload["submission"])

        # Step 4: Result Update Function
        update_payload = build_result_update(
            event_payload["record_id"],
            processing_result
        )

        # Step 5: Update stored record in Data Service
        update_response = requests.put(
            f"{DATA_SERVICE_BASE_URL}/records/{update_payload['record_id']}",
            json=update_payload["update_data"],
            timeout=5,
        )
        update_response.raise_for_status()
        updated_record = update_response.json()

        return jsonify(updated_record), 200

    except requests.RequestException as e:
        return jsonify({
            "error": "Failed to communicate with Data Service",
            "details": str(e)
        }), 500

    except Exception as e:
        return jsonify({
            "error": "Unexpected workflow error",
            "details": str(e)
        }), 500


if __name__ == "__main__":
    app.run(port=5002, debug=True)
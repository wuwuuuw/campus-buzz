from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# --- Configuration: Service Endpoints ---
# Local or internal data management service
DATA_SERVICE_BASE_URL = "http://172.17.0.1:5001"
# Serverless Function aliases for specific workflow stages
SUBMISSION_EVENT_URL = "https://submissfunction-xhmbeyvezh.cn-hangzhou.fcapp.run"
PROCESSING_URL = "https://processfunction-foletgmhuy.cn-hangzhou.fcapp.run"
RESULT_UPDATE_URL = "https://result-function-dyjqnjlgve.cn-hangzhou.fcapp.run"


@app.route("/health", methods=["GET"])
def health():
    """Simple health check endpoint to verify service availability."""
    return jsonify({"status": "ok"}), 200


@app.route("/submit", methods=["POST"])
def submit():
    """
    Main orchestration endpoint.
    Coordinates a multi-step workflow involving data persistence,
    event triggering, processing, and result updates.
    """
    submission = request.get_json()

    # Validate that the request contains a valid JSON body
    if not submission:
        return jsonify({"error": "Invalid JSON body"}), 400

    try:
        # --- Step 1: Create Initial Record ---
        # Persist the raw submission data into the primary database service
        create_response = requests.post(
            f"{DATA_SERVICE_BASE_URL}/records",
            json=submission,
            timeout=10,
        )
        create_response.raise_for_status()
        created_record = create_response.json()

        # --- Step 2: Trigger Submission Event ---
        # Pass the created record to an event function for pre-processing/logging
        event_response = requests.post(
            SUBMISSION_EVENT_URL,
            json=created_record,
            timeout=10,
        )
        event_response.raise_for_status()
        event_payload = event_response.json()

        # --- Step 3: Core Logic Processing ---
        # Send the specific submission data to the processing engine
        processing_response = requests.post(
            PROCESSING_URL,
            json=event_payload["submission"],
            timeout=10,
        )
        processing_response.raise_for_status()
        processing_result = processing_response.json()

        # --- Step 4: Finalize Result Data ---
        # Combine the record ID and processing results to prepare the final update payload
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

        # --- Step 5: Sync Updated Record to Database ---
        # Update the original record in the data service with the final results
        update_response = requests.put(
            f"{DATA_SERVICE_BASE_URL}/records/{update_payload['record_id']}",
            json=update_payload["update_data"],
            timeout=10,
        )
        update_response.raise_for_status()
        updated_record = update_response.json()

        # Return the final state of the record to the client
        return jsonify(updated_record), 200

    except requests.RequestException as e:
        # Catch connection errors, timeouts, or 4xx/5xx responses from external services
        return jsonify({
            "error": "Workflow failed",
            "details": str(e)
        }), 500


if __name__ == "__main__":
    # Run the Flask app on all interfaces at port 5002
    app.run(host="0.0.0.0", port=5002, debug=True)

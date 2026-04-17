from flask import Flask, request, jsonify
import uuid

app = Flask(__name__)

# In-memory dictionary to store submission records for local development/demonstration
records = {}

@app.route("/health", methods=["GET"])
def health():
    """
    Health check endpoint to verify if the container is running correctly.
    """
    return jsonify({"status": "ok"}), 200


@app.route("/records", methods=["POST"])
def create_record():
    """
    Component: Data Service (Container)
    Role: Create the initial submission record with a 'PENDING' status.
    """
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid JSON body"}), 400

    # Generate a unique ID for each campus event submission
    record_id = str(uuid.uuid4())

    # Create the record structure as per project requirements
    record = {
        "id": record_id,
        "title": data.get("title", ""),
        "description": data.get("description", ""),
        "location": data.get("location", ""),
        "date": data.get("date", ""),
        "organiser": data.get("organiser", ""),
        "status": "PENDING",  # Initial state before background processing
        "category": "",
        "priority": "",
        "note": "",
    }

    records[record_id] = record
    return jsonify(record), 201


@app.route("/records/<record_id>", methods=["GET"])
def get_record(record_id):
    """
    Component: Data Service (Container)
    Role: Retrieve a specific record so the user can view the outcome.
    """
    record = records.get(record_id)

    if not record:
        return jsonify({"error": "Record not found"}), 404

    return jsonify(record), 200


@app.route("/records/<record_id>", methods=["PUT"])
def update_record(record_id):
    """
    Component: Data Service (Container)
    Role: Update the stored record with results computed by the Serverless functions.
    """
    record = records.get(record_id)

    if not record:
        return jsonify({"error": "Record not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON body"}), 400

    # Update result-related fields after Processing and Result Update functions finish
    record["status"] = data.get("status", record["status"])
    record["category"] = data.get("category", record["category"])
    record["priority"] = data.get("priority", record["priority"])
    record["note"] = data.get("note", record["note"])

    records[record_id] = record
    return jsonify(record), 200


if __name__ == "__main__":
    # The Data Service runs on port 5001 as defined in the system architecture
    app.run(host="0.0.0.0", port=5001, debug=True)
from flask import Flask, request, jsonify
import uuid

app = Flask(__name__)

# In-memory storage for local development
records = {}


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/records", methods=["POST"])
def create_record():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid JSON body"}), 400

    record_id = str(uuid.uuid4())

    record = {
        "id": record_id,
        "title": data.get("title", ""),
        "description": data.get("description", ""),
        "location": data.get("location", ""),
        "date": data.get("date", ""),
        "organiser": data.get("organiser", ""),
        "status": "PENDING",
        "category": "",
        "priority": "",
        "note": "",
    }

    records[record_id] = record
    return jsonify(record), 201


@app.route("/records/<record_id>", methods=["GET"])
def get_record(record_id):
    record = records.get(record_id)

    if not record:
        return jsonify({"error": "Record not found"}), 404

    return jsonify(record), 200


@app.route("/records/<record_id>", methods=["PUT"])
def update_record(record_id):
    record = records.get(record_id)

    if not record:
        return jsonify({"error": "Record not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON body"}), 400

    # Only update result-related fields for now
    record["status"] = data.get("status", record["status"])
    record["category"] = data.get("category", record["category"])
    record["priority"] = data.get("priority", record["priority"])
    record["note"] = data.get("note", record["note"])

    records[record_id] = record
    return jsonify(record), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)

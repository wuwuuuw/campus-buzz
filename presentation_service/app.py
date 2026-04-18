from flask import Flask, render_template, request
import requests

app = Flask(__name__)


# This URL points to the Workflow Service, which acts as the backend orchestrator.
WORKFLOW_SERVICE_URL = "http://101.37.187.169:5002/submit"


@app.route("/", methods=["GET"])
def index():

    return render_template("index.html")


@app.route("/submit", methods=["POST"])
def submit():

    # Extract data from the HTML form fields sent via POST request
    submission = {
        "title": request.form.get("title", "").strip(),
        "description": request.form.get("description", "").strip(),
        "location": request.form.get("location", "").strip(),
        "date": request.form.get("date", "").strip(),
        "organiser": request.form.get("organiser", "").strip(),
    }

    try:
        # Forward the submission to the Workflow Service

        response = requests.post(
            WORKFLOW_SERVICE_URL,
            json=submission,
            timeout=10,
        )

        # Check if the HTTP request was successful (200-299 status codes)
        response.raise_for_status()

        # Parse the final processed result from the backend
        # Expected keys typically include: Status, Category, Priority, and Note.
        result = response.json()

        # Render the success page with the processed data
        return render_template("result.html", result=result)

    except requests.RequestException as e:

        # If the backend service is down or times out, provide a graceful error response
        error_result = {
            "status": "ERROR",
            "category": "Connection Failure",
            "priority": "N/A",
            "note": f"System currently unavailable: {str(e)}",
            "title": submission["title"],
            "description": submission["description"],
            "location": submission["location"],
            "date": submission["date"],
            "organiser": submission["organiser"],
        }
        return render_template("result.html", result=error_result)


if __name__ == "__main__":
    # The Presentation Service typically runs on port 5000.
    # Ensure ECS Security Groups allow inbound traffic on this port.
    app.run(host="0.0.0.0", port=5000, debug=True)
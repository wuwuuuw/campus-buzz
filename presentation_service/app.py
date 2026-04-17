from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# --- Configuration ---
# Component: Presentation Service (Frontend Container)
# This URL points to the Workflow Service, which acts as the backend orchestrator.
WORKFLOW_SERVICE_URL = "http://101.37.187.169:5002/submit"


@app.route("/", methods=["GET"])
def index():
    """
    Renders the initial entry point for the application.
    Displays the HTML form to the end-user to collect submission data.
    """
    return render_template("index.html")


@app.route("/submit", methods=["POST"])
def submit():
    """
    Acts as a proxy/gateway.
    Receives form data from the user, packages it as JSON, and hands it
    off to the internal Workflow Service for heavy lifting.
    """
    # Extract data from the HTML form fields sent via POST request
    submission = {
        "title": request.form.get("title", "").strip(),
        "description": request.form.get("description", "").strip(),
        "location": request.form.get("location", "").strip(),
        "date": request.form.get("date", "").strip(),
        "organiser": request.form.get("organiser", "").strip(),
    }

    try:
        # Step 1: Forward the submission to the Workflow Service (Container)
        # We use a POST request with a JSON payload.
        # A 10-second timeout accounts for potential cold starts in downstream Serverless functions.
        response = requests.post(
            WORKFLOW_SERVICE_URL,
            json=submission,
            timeout=10,
        )

        # Check if the HTTP request was successful (200-299 status codes)
        response.raise_for_status()

        # Step 2: Parse the final processed result from the backend
        # Expected keys typically include: Status, Category, Priority, and Note.
        result = response.json()

        # Step 3: Render the success page with the processed data
        return render_template("result.html", result=result)

    except requests.RequestException as e:
        # --- Error Handling ---
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
    # Note: Ensure ECS Security Groups allow inbound traffic on this port.
    app.run(host="0.0.0.0", port=5000, debug=True)
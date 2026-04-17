from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# Component: Presentation Service (Container)
# This URL points to the Workflow Service, which acts as the orchestrator.
WORKFLOW_SERVICE_URL = "http://101.37.187.169:5002/submit"


@app.route("/", methods=["GET"])
def index():
    """
    Role: Serve the HTML form to the end-user.
    This fulfills the 'User submits a form-based request' part of the project.
    """
    return render_template("index.html")


@app.route("/submit", methods=["POST"])
def submit():
    """
    Role: Collect form data and forward it to the Workflow Service.
    It handles the transition from user input to the automated background process.
    """
    # Extract data from the HTML form fields
    submission = {
        "title": request.form.get("title", "").strip(),
        "description": request.form.get("description", "").strip(),
        "location": request.form.get("location", "").strip(),
        "date": request.form.get("date", "").strip(),
        "organiser": request.form.get("organiser", "").strip(),
    }

    try:
        # Step 1: Forward the submission to the Workflow Service (Container)
        # The Workflow Service will then trigger the Serverless pipeline.
        response = requests.post(
            WORKFLOW_SERVICE_URL,
            json=submission,
            timeout=10,  # Increased timeout to allow for serverless cold starts
        )

        # Raise an exception if the Workflow Service returns an error (4xx or 5xx)
        response.raise_for_status()

        # Step 2: Receive the final processed result (Status, Category, Priority, Note)
        result = response.json()

        # Step 3: Display the final outcome to the user via the result template
        return render_template("result.html", result=result)

    except requests.RequestException as e:
        # Error handling if the back-end services are unreachable
        error_result = {
            "status": "ERROR",
            "category": "-",
            "priority": "-",
            "note": f"Failed to connect to Workflow Service: {str(e)}",
            "title": submission["title"],
            "description": submission["description"],
            "location": submission["location"],
            "date": submission["date"],
            "organiser": submission["organiser"],
        }
        return render_template("result.html", result=error_result)


if __name__ == "__main__":
    # The Presentation Service runs on port 5000.
    # Ensure this port is open in your ECS Security Group.
    app.run(host="0.0.0.0", port=5000, debug=True)
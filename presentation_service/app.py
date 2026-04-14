from flask import Flask, render_template, request
import requests

app = Flask(__name__)

WORKFLOW_SERVICE_URL = "http://127.0.0.1:5002/submit"


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/submit", methods=["POST"])
def submit():
    submission = {
        "title": request.form.get("title", "").strip(),
        "description": request.form.get("description", "").strip(),
        "location": request.form.get("location", "").strip(),
        "date": request.form.get("date", "").strip(),
        "organiser": request.form.get("organiser", "").strip(),
    }

    try:
        response = requests.post(
            WORKFLOW_SERVICE_URL,
            json=submission,
            timeout=5,
        )
        response.raise_for_status()
        result = response.json()

        return render_template("result.html", result=result)

    except requests.RequestException as e:
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
    app.run(port=5000, debug=True)
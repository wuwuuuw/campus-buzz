import re
from typing import Dict, Any


REQUIRED_FIELDS = ["title", "description", "location", "date", "organiser"]


def is_valid_date(date_str: str) -> bool:
    """
    Check whether the date matches YYYY-MM-DD format.
    This checks format only, which is enough for the project requirement.
    """
    return bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", date_str))


def determine_category(title: str, description: str) -> str:
    """
    Determine category based on keyword precedence:
    OPPORTUNITY > ACADEMIC > SOCIAL > GENERAL
    """
    text = f"{title} {description}".lower()

    if any(keyword in text for keyword in ["career", "internship", "recruitment"]):
        return "OPPORTUNITY"
    if any(keyword in text for keyword in ["workshop", "seminar", "lecture"]):
        return "ACADEMIC"
    if any(keyword in text for keyword in ["club", "society", "social"]):
        return "SOCIAL"
    return "GENERAL"


def determine_priority(category: str) -> str:
    """
    Assign priority based on category.
    """
    if category == "OPPORTUNITY":
        return "HIGH"
    if category == "ACADEMIC":
        return "MEDIUM"
    return "NORMAL"


def build_note(status: str, category: str, priority: str) -> str:
    """
    Generate a short explanatory note for the user.
    """
    if status == "INCOMPLETE":
        return "Some required fields are missing."
    if status == "NEEDS REVISION":
        return "Please revise the submission because the date format or description does not meet the requirements."
    return f"The submission is approved as {category} with {priority} priority."


def process_submission(submission: Dict[str, Any]) -> Dict[str, str]:
    """
    Apply project rules and return:
    - status
    - category
    - priority
    - note
    """
    for field in REQUIRED_FIELDS:
        value = submission.get(field, "")
        if not isinstance(value, str) or not value.strip():
            return {
                "status": "INCOMPLETE",
                "category": "GENERAL",
                "priority": "NORMAL",
                "note": build_note("INCOMPLETE", "GENERAL", "NORMAL"),
            }

    title = submission["title"].strip()
    description = submission["description"].strip()
    date_str = submission["date"].strip()

    category = determine_category(title, description)
    priority = determine_priority(category)

    if not is_valid_date(date_str):
        return {
            "status": "NEEDS REVISION",
            "category": category,
            "priority": priority,
            "note": build_note("NEEDS REVISION", category, priority),
        }

    if len(description) < 40:
        return {
            "status": "NEEDS REVISION",
            "category": category,
            "priority": priority,
            "note": build_note("NEEDS REVISION", category, priority),
        }

    return {
        "status": "APPROVED",
        "category": category,
        "priority": priority,
        "note": build_note("APPROVED", category, priority),
    }


if __name__ == "__main__":
    sample_submission = {
        "title": "Career Workshop 2026",
        "description": "This workshop introduces internship opportunities and recruitment preparation for students.",
        "location": "Room A101",
        "date": "2026-05-20",
        "organiser": "Career Center",
    }

    result = process_submission(sample_submission)
    print(result)
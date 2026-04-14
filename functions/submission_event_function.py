from typing import Dict, Any


def handle_submission_event(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert a newly created submission record into a processing request.
    This simulates a serverless event function.
    """
    return {
        "record_id": record["id"],
        "submission": {
            "title": record.get("title", ""),
            "description": record.get("description", ""),
            "location": record.get("location", ""),
            "date": record.get("date", ""),
            "organiser": record.get("organiser", ""),
        }
    }


if __name__ == "__main__":
    sample_record = {
        "id": "123",
        "title": "Career Workshop",
        "description": "This workshop introduces internship opportunities for students in detail.",
        "location": "Room A101",
        "date": "2026-05-20",
        "organiser": "Career Center",
    }

    print(handle_submission_event(sample_record))
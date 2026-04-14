from typing import Dict, Any


def build_result_update(record_id: str, processing_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build the payload used to update the stored submission record.
    This simulates a serverless result update function.
    """
    return {
        "record_id": record_id,
        "update_data": {
            "status": processing_result.get("status", ""),
            "category": processing_result.get("category", ""),
            "priority": processing_result.get("priority", ""),
            "note": processing_result.get("note", ""),
        }
    }


if __name__ == "__main__":
    sample_result = {
        "status": "APPROVED",
        "category": "OPPORTUNITY",
        "priority": "HIGH",
        "note": "The submission is complete and has been approved.",
    }

    print(build_result_update("123", sample_result))
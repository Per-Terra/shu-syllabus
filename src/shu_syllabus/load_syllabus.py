import json
import os


def load_syllabus(nendo: str):
    """Loads the syllabus data for the specified academic year.

    Args:
        nendo: The academic year for the syllabus data.

    Returns:
        dict: The syllabus data for the specified academic year.
    """

    file_path = os.path.join(
        os.path.dirname(__file__), f".../data/syllabus/{nendo}.json"
    )

    with open(file_path, "r") as file:
        syllabus_data = json.load(file)

    return syllabus_data

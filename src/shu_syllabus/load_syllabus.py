import importlib
import importlib.resources
import json


def load_syllabus(nendo: str):
    """Loads the syllabus data for the specified academic year.

    Args:
        nendo: The academic year for the syllabus data.

    Returns:
        dict: The syllabus data for the specified academic year.
    """

    with importlib.resources.open_text(
        "shu_syllabus.data.syllabus", f"{nendo}.json"
    ) as file:
        return json.load(file)

import importlib
import importlib.resources
import json
from typing import Any


def load_syllabuses(nendo: str) -> list[dict[str, Any]]:
    """Loads the syllabus data for the specified academic year.

    Args:
        nendo: The academic year for the syllabus data.

    Returns:
        list[dict[str, Any]]: The syllabus data for the specified academic year.
    """

    with importlib.resources.open_text(
        "shu_syllabus.data.syllabus", f"{nendo}.json"
    ) as file:
        return json.load(file)

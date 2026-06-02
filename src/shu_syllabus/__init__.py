from ._loader import load
from ._models import (
    Book,
    EnrollmentInfo,
    EvaluationRatio,
    ScheduleEntry,
    Syllabus,
    Teacher,
)
from ._scraper import Scraper

__all__ = [
    "Book",
    "EnrollmentInfo",
    "EvaluationRatio",
    "ScheduleEntry",
    "Scraper",
    "Syllabus",
    "Teacher",
    "load",
]

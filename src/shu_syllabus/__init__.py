from ._loader import load
from ._models import (
    Book,
    EnrollmentInfo,
    EvaluationRatio,
    ScheduleEntry,
    Syllabus,
    Teacher,
    TeachingCertificate,
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
    "TeachingCertificate",
    "load",
]

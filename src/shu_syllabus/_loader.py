from __future__ import annotations

import importlib.resources
import json
from typing import Any

from ._models import (
    Book,
    EnrollmentInfo,
    EvaluationRatio,
    ScheduleEntry,
    Syllabus,
    Teacher,
    TeachingCertificate,
)


def load(nendo: str) -> list[Syllabus]:
    """バンドル済みシラバスデータを読み込む。

    Args:
        nendo: 年度（例: "2025"）。利用可能: 2023, 2024, 2025, 2026。

    Returns:
        シラバス番号順にソートされた Syllabus のリスト。
    """
    with importlib.resources.open_text(
        "shu_syllabus.data.syllabus", f"{nendo}.json"
    ) as f:
        raw_list: list[dict[str, Any]] = json.load(f)
    return [_dict_to_syllabus(d) for d in raw_list]


def _dict_to_syllabus(d: dict[str, Any]) -> Syllabus:
    return Syllabus(
        fetched_at=d.get("fetched_at"),
        name_ja=d.get("name_ja"),
        name_en=d.get("name_en"),
        syllabus_number=d.get("syllabus_number"),
        course_number=d.get("course_number") or None,
        departments=d.get("departments", []),
        category=d.get("category") or None,
        home_department=d.get("home_department") or None,
        requirements=d.get("requirements") or None,
        target_year=d.get("target_year"),
        time_slot=d.get("time_slot") or None,
        required_or_elective=d.get("required_or_elective") or None,
        course_division=d.get("course_division") or None,
        instruction_format=d.get("instruction_format") or None,
        teachers=[
            Teacher(name=t["name"], is_primary=t["is_primary"])
            for t in d.get("teachers", [])
        ],
        term=d.get("term"),
        credits=d.get("credits"),
        teaching_methods=d.get("teaching_methods", []),
        delivery_modes=d.get("delivery_modes", []),
        objectives=d.get("objectives") or None,
        overview=d.get("overview") or None,
        diploma_policies=d.get("diploma_policies", []),
        textbooks=[_dict_to_book(b) for b in d.get("textbooks", [])],
        references=[_dict_to_book(b) for b in d.get("references", [])],
        enrollment_info=_dict_to_enrollment_info(d.get("enrollment_info", {})),
        teaching_certificate=_dict_to_teaching_certificate(
            d.get("teaching_certificate")
        ),
        grading_criteria=d.get("grading_criteria") or None,
        evaluation_ratio=_dict_to_evaluation_ratio(d.get("evaluation_ratio", {})),
        teacher_message=d.get("teacher_message") or None,
        schedule=[_dict_to_schedule_entry(s) for s in d.get("schedule", [])],
        credit_auditing=d.get("credit_auditing"),
        practitioner_info=d.get("practitioner_info") or None,
    )


def _dict_to_book(d: dict[str, Any]) -> Book:
    return Book(
        title=d["title"],
        publication_year=d.get("publication_year"),
        author=d.get("author"),
        publisher=d.get("publisher"),
        price=d.get("price"),
        isbn=d.get("isbn"),
        available_on_campus=d.get("available_on_campus", False),
    )


def _dict_to_enrollment_info(d: dict[str, Any]) -> EnrollmentInfo:
    return EnrollmentInfo(
        prerequisites=d.get("prerequisites", []),
        recommended=d.get("recommended", []),
        required_materials=d.get("required_materials") or None,
        other=d.get("other") or None,
    )


def _dict_to_teaching_certificate(
    d: dict[str, Any] | None,
) -> TeachingCertificate | None:
    if not d:
        return None
    return TeachingCertificate(
        subject=d.get("subject") or None,
        enforcement=d.get("enforcement") or None,
    )


def _dict_to_evaluation_ratio(d: dict[str, Any]) -> EvaluationRatio:
    return EvaluationRatio(
        exam=d.get("exam", 0),
        quiz=d.get("quiz", 0),
        report=d.get("report", 0),
        presentation=d.get("presentation", 0),
        portfolio=d.get("portfolio", 0),
        other=d.get("other", 0),
    )


def _dict_to_schedule_entry(d: dict[str, Any]) -> ScheduleEntry:
    return ScheduleEntry(
        number=d["number"],
        content=d.get("content"),
        teaching_methods=d.get("teaching_methods", []),
        teachers=d.get("teachers", []),
    )

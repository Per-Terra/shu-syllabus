import pytest

from shu_syllabus import load
from shu_syllabus._models import (
    Book,
    EnrollmentInfo,
    EvaluationRatio,
    ScheduleEntry,
    Syllabus,
    Teacher,
    TeachingCertificate,
)


def test_load_returns_syllabus_list() -> None:
    result = load("2025")
    assert len(result) > 0
    assert isinstance(result[0], Syllabus)


def test_load_all_years() -> None:
    for year in ("2023", "2024", "2025"):
        result = load(year)
        assert len(result) > 0
        assert isinstance(result[0], Syllabus)


def test_load_nested_types() -> None:
    syllabuses = load("2025")
    s = syllabuses[0]
    assert all(isinstance(t, Teacher) for t in s.teachers)
    assert isinstance(s.evaluation_ratio, EvaluationRatio)
    assert isinstance(s.enrollment_info, EnrollmentInfo)
    assert all(isinstance(e, ScheduleEntry) for e in s.schedule)
    assert all(isinstance(b, Book) for b in s.textbooks)
    assert all(isinstance(b, Book) for b in s.references)


def test_load_sorted_by_syllabus_number() -> None:
    from shu_syllabus._utils import letter_to_number

    syllabuses = load("2025")
    keys = [
        (int(s.syllabus_number[:7]), letter_to_number(s.syllabus_number[7:]))
        for s in syllabuses
        if s.syllabus_number
    ]
    assert keys == sorted(keys)


def test_load_teaching_certificate_roundtrip() -> None:
    # 教職関連データは 2026 年度のみ実在する
    syllabuses = load("2026")
    populated = [s for s in syllabuses if s.teaching_certificate is not None]
    assert populated, "2026 に teaching_certificate を持つ科目が存在するはず"
    tc = populated[0].teaching_certificate
    assert isinstance(tc, TeachingCertificate)
    assert tc.subject or tc.enforcement


def test_load_invalid_year() -> None:
    with pytest.raises(FileNotFoundError):
        load("1999")


def test_load_empty_strings_normalized() -> None:
    syllabuses = load("2025")
    for s in syllabuses:
        if s.course_number is not None:
            assert s.course_number != ""
        if s.home_department is not None:
            assert s.home_department != ""

from shu_syllabus._models import (
    Book,
    EnrollmentInfo,
    EvaluationRatio,
    ScheduleEntry,
    Syllabus,
    Teacher,
)


def test_syllabus_defaults() -> None:
    s = Syllabus()
    assert s.name_ja is None
    assert s.departments == []
    assert s.teachers == []
    assert s.credits is None
    assert s.evaluation_ratio == EvaluationRatio()


def test_evaluation_ratio_defaults() -> None:
    r = EvaluationRatio()
    assert r.exam == 0
    assert r.quiz == 0
    assert r.report == 0
    assert r.presentation == 0
    assert r.portfolio == 0
    assert r.other == 0


def test_teacher_frozen() -> None:
    import pytest

    t = Teacher(name="Test", is_primary=True)
    with pytest.raises(AttributeError):
        t.name = "Changed"  # type: ignore[misc]


def test_book_frozen() -> None:
    import pytest

    b = Book(title="Test")
    with pytest.raises(AttributeError):
        b.title = "Changed"  # type: ignore[misc]


def test_syllabus_to_dict() -> None:
    s = Syllabus(
        name_ja="テスト科目",
        credits=2,
        teachers=[Teacher(name="山田太郎", is_primary=True)],
        evaluation_ratio=EvaluationRatio(exam=50, report=50),
        schedule=[ScheduleEntry(number="1", content="ガイダンス")],
    )
    d = s.to_dict()
    assert d["name_ja"] == "テスト科目"
    assert d["credits"] == 2
    assert d["teachers"] == [{"name": "山田太郎", "is_primary": True}]
    assert d["evaluation_ratio"]["exam"] == 50
    assert d["schedule"][0]["number"] == "1"


def test_syllabus_to_dict_roundtrip() -> None:
    original = Syllabus(
        name_ja="テスト",
        departments=["工学部"],
        textbooks=[Book(title="教科書", publication_year=2020, price=3000)],
        enrollment_info=EnrollmentInfo(
            prerequisites=["数学I"],
            required_materials="電卓",
        ),
    )
    d = original.to_dict()
    assert d["departments"] == ["工学部"]
    assert d["textbooks"][0]["title"] == "教科書"
    assert d["textbooks"][0]["publication_year"] == 2020
    assert d["enrollment_info"]["prerequisites"] == ["数学I"]
    assert d["enrollment_info"]["required_materials"] == "電卓"

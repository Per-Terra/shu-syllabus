import re

from shu_syllabus._models import (
    Book,
    EnrollmentInfo,
    EvaluationRatio,
    ScheduleEntry,
    Syllabus,
    Teacher,
    TeachingCertificate,
)
from shu_syllabus._parser import parse_syllabus


def test_parse_basic_fields(syllabus_html: str) -> None:
    result = parse_syllabus(
        syllabus_html, fetched_at="2025-04-04T05:54:56Z", syllabus_no="1000600A"
    )
    assert isinstance(result, Syllabus)
    assert result.name_ja == "意思決定科学"
    assert result.name_en == "Science of Decision Making"
    assert result.syllabus_number == "1000600A"
    assert result.credits == 2
    assert result.target_year == 3
    assert result.term == "前期"
    assert result.fetched_at == "2025-04-04T05:54:56Z"


def test_parse_departments(syllabus_html: str) -> None:
    result = parse_syllabus(syllabus_html)
    assert result.departments == ["経済学部", "福祉情報学部"]


def test_parse_category(syllabus_html: str) -> None:
    result = parse_syllabus(syllabus_html)
    assert result.category == "総合科目"


def test_parse_instruction_format(syllabus_html: str) -> None:
    result = parse_syllabus(syllabus_html)
    assert result.instruction_format == "単独"


def test_parse_teachers(syllabus_html: str) -> None:
    result = parse_syllabus(syllabus_html)
    assert len(result.teachers) >= 1
    assert isinstance(result.teachers[0], Teacher)
    assert result.teachers[0].name == "喜入　暁"


def test_parse_teaching_methods(syllabus_html: str) -> None:
    result = parse_syllabus(syllabus_html)
    assert "講義" in result.teaching_methods


def test_parse_delivery_modes(syllabus_html: str) -> None:
    result = parse_syllabus(syllabus_html)
    assert "対面" in result.delivery_modes


def test_parse_objectives(syllabus_html: str) -> None:
    result = parse_syllabus(syllabus_html)
    assert result.objectives is not None
    assert "意思決定" in result.objectives


def test_parse_overview(syllabus_html: str) -> None:
    result = parse_syllabus(syllabus_html)
    assert result.overview is not None


def test_parse_references(syllabus_html: str) -> None:
    result = parse_syllabus(syllabus_html)
    assert len(result.references) >= 1
    book = result.references[0]
    assert isinstance(book, Book)
    assert book.title == "感情心理学"
    assert book.publication_year == 2007
    assert book.publisher == "朝倉書店"
    assert book.isbn is not None


def test_parse_textbooks_empty(syllabus_html: str) -> None:
    result = parse_syllabus(syllabus_html)
    assert result.textbooks == []


def test_parse_enrollment_info(syllabus_html: str) -> None:
    result = parse_syllabus(syllabus_html)
    info = result.enrollment_info
    assert isinstance(info, EnrollmentInfo)
    assert isinstance(info.prerequisites, list)
    assert isinstance(info.recommended, list)


def test_parse_evaluation_ratio(syllabus_html: str) -> None:
    result = parse_syllabus(syllabus_html)
    ratio = result.evaluation_ratio
    assert isinstance(ratio, EvaluationRatio)
    assert ratio.exam == 0
    assert ratio.report == 70
    assert ratio.other == 30
    assert (
        ratio.exam
        + ratio.quiz
        + ratio.report
        + ratio.presentation
        + ratio.portfolio
        + ratio.other
        == 100
    )


def test_parse_schedule(syllabus_html: str) -> None:
    result = parse_syllabus(syllabus_html)
    assert len(result.schedule) == 15
    entry = result.schedule[0]
    assert isinstance(entry, ScheduleEntry)
    assert entry.number == "1"
    assert entry.content is not None
    assert "ガイダンス" in entry.content
    assert "講義" in entry.teaching_methods
    assert len(entry.teachers) >= 1


def test_parse_credit_auditing(syllabus_html: str) -> None:
    result = parse_syllabus(syllabus_html)
    assert result.credit_auditing is True


def test_parse_syllabus_no_fallback() -> None:
    minimal_html = "<html><body></body></html>"
    result = parse_syllabus(minimal_html, syllabus_no="9999999A")
    assert result.syllabus_number == "9999999A"


def test_parse_empty_strings_become_none() -> None:
    minimal_html = "<html><body></body></html>"
    result = parse_syllabus(minimal_html)
    assert result.name_ja is None
    assert result.course_number is None
    assert result.category is None
    assert result.objectives is None


def test_parse_search_results(search_html: str) -> None:
    pattern = re.compile(r"Syllabus_Data\('([^']*)','([^']*)','([^']*)'\)")
    matches = pattern.findall(search_html)
    assert len(matches) >= 1
    nendo, gakou_kbn, syllabus_no = matches[0]
    assert nendo == "2025"
    assert gakou_kbn == "2"
    assert len(syllabus_no) >= 8


# ---------------------------------------------------------------------------
# Complex fixture (2011300A: スポーツ医学)
# 複数教員・主担当あり・教科書あり・DP あり・先修条件あり
# ---------------------------------------------------------------------------


def test_parse_multiple_teachers_with_primary(syllabus_html_complex: str) -> None:
    result = parse_syllabus(syllabus_html_complex, syllabus_no="2011300A")
    assert len(result.teachers) == 3
    primary = [t for t in result.teachers if t.is_primary]
    assert len(primary) == 1
    assert primary[0].name == "小笠　博義"
    non_primary = [t for t in result.teachers if not t.is_primary]
    assert len(non_primary) == 2


def test_parse_textbooks(syllabus_html_complex: str) -> None:
    result = parse_syllabus(syllabus_html_complex, syllabus_no="2011300A")
    assert len(result.textbooks) == 1
    book = result.textbooks[0]
    assert isinstance(book, Book)
    assert "リファレンスブック" in book.title
    assert book.publisher == "日本スポーツ協会"
    assert book.price == 4840


def test_parse_publication_year_zero_becomes_none(syllabus_html_complex: str) -> None:
    result = parse_syllabus(syllabus_html_complex, syllabus_no="2011300A")
    book = result.textbooks[0]
    assert book.publication_year is None


def test_parse_diploma_policies(syllabus_html_complex: str) -> None:
    result = parse_syllabus(syllabus_html_complex, syllabus_no="2011300A")
    assert len(result.diploma_policies) == 2
    assert "スポーツマネジメントコースDP3" in result.diploma_policies
    assert "スポーツ健康科学科DP2" in result.diploma_policies


def test_parse_prerequisites(syllabus_html_complex: str) -> None:
    result = parse_syllabus(syllabus_html_complex, syllabus_no="2011300A")
    assert "解剖学" in result.enrollment_info.prerequisites
    assert "生理学" in result.enrollment_info.prerequisites


def test_parse_course_number(syllabus_html_complex: str) -> None:
    result = parse_syllabus(syllabus_html_complex, syllabus_no="2011300A")
    assert result.course_number == "21-1-22-22-02"


def test_parse_complex_evaluation_ratio(syllabus_html_complex: str) -> None:
    result = parse_syllabus(syllabus_html_complex, syllabus_no="2011300A")
    ratio = result.evaluation_ratio
    assert ratio.exam == 50
    assert ratio.report == 30
    assert ratio.other == 20
    assert (
        ratio.exam
        + ratio.quiz
        + ratio.report
        + ratio.presentation
        + ratio.portfolio
        + ratio.other
        == 100
    )


def test_parse_schedule_with_multiple_teachers(syllabus_html_complex: str) -> None:
    result = parse_syllabus(syllabus_html_complex, syllabus_no="2011300A")
    assert len(result.schedule) >= 1
    has_multi = any(len(e.teachers) > 1 for e in result.schedule)
    has_single = any(len(e.teachers) == 1 for e in result.schedule)
    assert has_multi or has_single


def test_teaching_certificate_none_for_non_teaching(syllabus_html: str) -> None:
    # 教職課程対象外の科目では「教職関連」欄が空 → None
    result = parse_syllabus(syllabus_html)
    assert result.teaching_certificate is None


# ---------------------------------------------------------------------------
# Teaching-certificate fixture (7004900A: 学校保健, 2026)
# 教職関連あり・複数教員・実務家教員・小テスト/実技による評価
# ---------------------------------------------------------------------------


def test_parse_teaching_certificate(syllabus_html_teaching: str) -> None:
    result = parse_syllabus(syllabus_html_teaching, syllabus_no="7004900A")
    tc = result.teaching_certificate
    assert isinstance(tc, TeachingCertificate)
    assert tc.subject == "教科及び教科の指導法に関する科目"
    assert tc.enforcement is not None
    # 対応免許状ごとに改行区切りで複数記載される
    assert "\n" in tc.enforcement
    assert tc.enforcement.startswith("【小二種免】")
    assert "【高一種免（保健体育）】" in tc.enforcement


def test_parse_teaching_evaluation_ratio(syllabus_html_teaching: str) -> None:
    # 小テスト・実技発表の比率が入る数少ない例
    ratio = parse_syllabus(syllabus_html_teaching).evaluation_ratio
    assert ratio.quiz == 30
    assert ratio.report == 40
    assert ratio.presentation == 20
    assert ratio.other == 10
    assert ratio.exam == 0
    assert ratio.portfolio == 0


def test_parse_teaching_teachers_and_practitioner(syllabus_html_teaching: str) -> None:
    result = parse_syllabus(syllabus_html_teaching)
    assert len(result.teachers) == 2
    assert [t.is_primary for t in result.teachers] == [True, False]
    assert result.practitioner_info is not None
    assert "村瀬" in result.practitioner_info
    assert result.credit_auditing is False

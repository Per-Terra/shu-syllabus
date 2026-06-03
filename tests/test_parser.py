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

# ---------------------------------------------------------------------------
# 基礎看護技術Ⅱ (2116500A, 2026前期)
# 複数教員(主担当あり)・教科書/参考図書(全フィールド)・履修上の注意4項目・
# 実技/試験評価・複数教員回を含む授業計画・実務家教員・科目等履修不可。
# ---------------------------------------------------------------------------


def test_parse_basic_fields(syllabus_html_nursing: str) -> None:
    result = parse_syllabus(
        syllabus_html_nursing,
        fetched_at="2026-04-04T05:54:56Z",
        syllabus_no="2116500A",
    )
    assert isinstance(result, Syllabus)
    assert result.name_ja == "基礎看護技術Ⅱ（診療に伴う技術）"
    assert result.name_en == "Nursing Skills Ⅱ"
    assert result.syllabus_number == "2116500A"
    assert result.course_number == "22-2-22-21-01"
    assert result.credits == 2
    assert result.target_year == 2
    assert result.term == "前期"
    assert result.fetched_at == "2026-04-04T05:54:56Z"


def test_parse_category(syllabus_html_nursing: str) -> None:
    result = parse_syllabus(syllabus_html_nursing)
    assert result.category == "専門科目"


def test_parse_instruction_format_multiple(syllabus_html_nursing: str) -> None:
    result = parse_syllabus(syllabus_html_nursing)
    assert result.instruction_format == "複数"


def test_parse_multiple_teachers_with_primary(syllabus_html_nursing: str) -> None:
    result = parse_syllabus(syllabus_html_nursing, syllabus_no="2116500A")
    assert len(result.teachers) == 6
    assert isinstance(result.teachers[0], Teacher)
    primary = [t for t in result.teachers if t.is_primary]
    assert len(primary) == 1
    assert primary[0].name == "杉本　吉恵"
    assert len([t for t in result.teachers if not t.is_primary]) == 5


def test_parse_teaching_methods(syllabus_html_nursing: str) -> None:
    result = parse_syllabus(syllabus_html_nursing)
    assert "講義" in result.teaching_methods
    assert "演習" in result.teaching_methods


def test_parse_delivery_modes(syllabus_html_nursing: str) -> None:
    result = parse_syllabus(syllabus_html_nursing)
    assert "対面" in result.delivery_modes


def test_parse_objectives_and_overview(syllabus_html_nursing: str) -> None:
    result = parse_syllabus(syllabus_html_nursing)
    assert result.objectives is not None
    assert "診療" in result.objectives
    assert result.overview is not None
    assert result.teacher_message is not None


def test_parse_diploma_policies(syllabus_html_nursing: str) -> None:
    result = parse_syllabus(syllabus_html_nursing, syllabus_no="2116500A")
    assert result.diploma_policies == ["看護学科DP2", "看護学科DP3", "看護学科DP4"]


def test_parse_textbooks_all_fields(syllabus_html_nursing: str) -> None:
    result = parse_syllabus(syllabus_html_nursing, syllabus_no="2116500A")
    assert len(result.textbooks) == 3
    book = result.textbooks[0]
    assert isinstance(book, Book)
    assert "基礎看護技術Ⅱ" in book.title
    assert book.publication_year == 2025
    assert book.author == "任　和子"
    assert book.publisher == "医学書院"
    assert book.price == 3520
    assert book.isbn == "978-4-260-05688-5"
    assert book.available_on_campus is True


def test_parse_references(syllabus_html_nursing: str) -> None:
    result = parse_syllabus(syllabus_html_nursing, syllabus_no="2116500A")
    assert len(result.references) == 1
    book = result.references[0]
    assert isinstance(book, Book)
    assert "根拠と事故防止" in book.title
    assert book.available_on_campus is False


def test_parse_enrollment_info(syllabus_html_nursing: str) -> None:
    info = parse_syllabus(syllabus_html_nursing).enrollment_info
    assert isinstance(info, EnrollmentInfo)
    assert info.prerequisites == ["看護学概論"]
    assert info.recommended == ["なし"]
    assert info.required_materials is not None
    assert info.other is not None


def test_parse_evaluation_ratio(syllabus_html_nursing: str) -> None:
    ratio = parse_syllabus(syllabus_html_nursing).evaluation_ratio
    assert isinstance(ratio, EvaluationRatio)
    assert ratio.exam == 40
    assert ratio.presentation == 50
    assert ratio.other == 10
    assert (
        ratio.exam
        + ratio.quiz
        + ratio.report
        + ratio.presentation
        + ratio.portfolio
        + ratio.other
        == 100
    )


def test_parse_schedule_with_multiple_teachers(syllabus_html_nursing: str) -> None:
    result = parse_syllabus(syllabus_html_nursing, syllabus_no="2116500A")
    assert len(result.schedule) == 31
    entry = result.schedule[0]
    assert isinstance(entry, ScheduleEntry)
    assert entry.content is not None
    assert "講義" in entry.teaching_methods
    assert len(entry.teachers) >= 1
    assert any(len(e.teachers) > 1 for e in result.schedule)


def test_parse_credit_auditing_false(syllabus_html_nursing: str) -> None:
    result = parse_syllabus(syllabus_html_nursing)
    assert result.credit_auditing is False


def test_parse_practitioner_info(syllabus_html_nursing: str) -> None:
    result = parse_syllabus(syllabus_html_nursing)
    assert result.practitioner_info is not None
    assert "看護師" in result.practitioner_info


def test_teaching_certificate_none_for_non_teaching(syllabus_html_nursing: str) -> None:
    # 教職課程対象外の科目では「教職関連」欄が空 → None
    result = parse_syllabus(syllabus_html_nursing)
    assert result.teaching_certificate is None


# ---------------------------------------------------------------------------
# 国際経済学Ⅱ (2038200A, 2026前期)
# 単独教員・主学科/複数学科・教職関連(改行区切りの enforcement)・
# 価格/ISBN が欠落した教科書。
# ---------------------------------------------------------------------------


def test_parse_single_teacher(syllabus_html_economics: str) -> None:
    result = parse_syllabus(syllabus_html_economics, syllabus_no="2038200A")
    assert result.instruction_format == "単独"
    assert len(result.teachers) == 1
    assert result.teachers[0].name == "村岡　浩次"
    assert result.teachers[0].is_primary is False


def test_parse_departments_and_home_department(syllabus_html_economics: str) -> None:
    result = parse_syllabus(syllabus_html_economics)
    assert result.departments == ["経済学部", "経済経営学部 経済経営学科"]
    assert result.home_department == "経済経営学部 経済経営学科"
    assert result.course_number == "11-3-28-21-02"


def test_parse_book_missing_price_and_isbn(syllabus_html_economics: str) -> None:
    result = parse_syllabus(syllabus_html_economics, syllabus_no="2038200A")
    assert len(result.textbooks) == 2
    # 1冊目はダウンロード資料で価格・ISBN が空 → None
    download = result.textbooks[0]
    assert download.price is None
    assert download.isbn is None
    # 2冊目は通常書籍で価格・ISBN あり
    assert result.textbooks[1].price == 2805
    assert result.textbooks[1].isbn is not None
    assert result.references == []


def test_parse_economics_evaluation_ratio(syllabus_html_economics: str) -> None:
    ratio = parse_syllabus(syllabus_html_economics).evaluation_ratio
    assert ratio.exam == 50
    assert ratio.report == 30
    assert ratio.presentation == 20
    assert ratio.quiz == 0
    assert ratio.portfolio == 0
    assert ratio.other == 0


def test_parse_teaching_certificate(syllabus_html_economics: str) -> None:
    result = parse_syllabus(syllabus_html_economics, syllabus_no="2038200A")
    tc = result.teaching_certificate
    assert isinstance(tc, TeachingCertificate)
    assert tc.subject == "教科及び教科の指導法に関する科目"
    assert tc.enforcement is not None
    # 対応免許状ごとに改行区切りで複数記載される
    assert "\n" in tc.enforcement
    assert tc.enforcement.startswith("【中一種免（社会）】")
    assert "【高一種免（公民）】" in tc.enforcement


# ---------------------------------------------------------------------------
# 教育相談Ⅰ (7002700A, 2026前期)
# オムニバス・科目等履修可・小テスト/ポートフォリオ評価・複数学科・実務家教員。
# ---------------------------------------------------------------------------


def test_parse_instruction_format_omnibus(syllabus_html_consultation: str) -> None:
    result = parse_syllabus(syllabus_html_consultation, syllabus_no="7002700A")
    assert result.instruction_format == "オムニバス"
    assert result.category == "教職科目"


def test_parse_many_departments(syllabus_html_consultation: str) -> None:
    result = parse_syllabus(syllabus_html_consultation)
    assert len(result.departments) == 5
    assert "経済学部" in result.departments
    assert "情報科学部 情報科学科" in result.departments


def test_parse_consultation_teachers(syllabus_html_consultation: str) -> None:
    result = parse_syllabus(syllabus_html_consultation)
    assert len(result.teachers) == 2
    assert [t.is_primary for t in result.teachers] == [True, False]
    assert result.practitioner_info is not None
    assert "前田" in result.practitioner_info


def test_parse_quiz_and_portfolio_evaluation(syllabus_html_consultation: str) -> None:
    # 小テスト・ポートフォリオの比率が入る数少ない例
    ratio = parse_syllabus(syllabus_html_consultation).evaluation_ratio
    assert ratio.quiz == 50
    assert ratio.portfolio == 50
    assert ratio.exam == 0
    assert ratio.report == 0
    assert ratio.presentation == 0
    assert ratio.other == 0


def test_parse_credit_auditing_true(syllabus_html_consultation: str) -> None:
    result = parse_syllabus(syllabus_html_consultation)
    assert result.credit_auditing is True


def test_parse_teaching_certificate_basic_subject(
    syllabus_html_consultation: str,
) -> None:
    tc = parse_syllabus(syllabus_html_consultation).teaching_certificate
    assert isinstance(tc, TeachingCertificate)
    assert tc.subject == "教育の基礎的理解に関する科目等"
    assert tc.enforcement is not None


# ---------------------------------------------------------------------------
# 退化ケース・検索結果
# ---------------------------------------------------------------------------


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
    assert nendo == "2026"
    assert gakou_kbn == "2"
    assert len(syllabus_no) >= 8

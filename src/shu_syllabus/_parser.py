from __future__ import annotations

import re

from bs4 import BeautifulSoup, Tag

from ._models import (
    Book,
    EnrollmentInfo,
    EvaluationRatio,
    ScheduleEntry,
    Syllabus,
    Teacher,
    TeachingCertificate,
)
from ._utils import make_soup

_PREFIX_KIHON = "ctl00_cphMain_UcSyllKihon_lbl"
_PREFIX_DETAIL = "ctl00_cphMain_UcSyllContent_repContent_ctl"


def parse_syllabus(
    html: str,
    *,
    fetched_at: str | None = None,
    syllabus_no: str | None = None,
) -> Syllabus:
    """シラバスHTMLをパースして Syllabus を返す。

    Args:
        html: AAAシラバスページのHTML文字列。
        fetched_at: 取得日時（ISO 8601）。
        syllabus_no: HTMLから取得できない場合のフォールバック用シラバス番号。
    """
    soup = make_soup(html)

    return Syllabus(
        fetched_at=fetched_at,
        name_ja=_get_text(soup, f"{_PREFIX_KIHON}KougiName"),
        name_en=_get_text(soup, f"{_PREFIX_KIHON}EibunName"),
        syllabus_number=(_get_text(soup, f"{_PREFIX_KIHON}SyllabusNo") or syllabus_no),
        course_number=_get_text(soup, f"{_PREFIX_KIHON}KAMOKU_NO"),
        departments=_split_or_empty(
            _get_text(soup, f"{_PREFIX_KIHON}COURSE_NAME"), "、"
        ),
        category=_get_text(soup, f"{_PREFIX_KIHON}SPECIALTY_NAME"),
        home_department=_get_text(soup, f"{_PREFIX_KIHON}SUBJECT"),
        requirements=_get_text(soup, f"{_PREFIX_KIHON}REQUIREMENT"),
        target_year=_first_char_int(_get_text(soup, f"{_PREFIX_KIHON}HaitouNen")),
        required_or_elective=_get_text(soup, f"{_PREFIX_KIHON}Hissen"),
        instruction_format=_get_text(soup, f"{_PREFIX_KIHON}FORM_CODE"),
        # Free1/Free2 は 2022 年度以前のみ使用の欄。
        # 2023 年度以降は常に空のため出力に含めない。
        # time_slot=_get_text(soup, f"{_PREFIX_KIHON}Free1"),
        # course_division=_get_text(soup, f"{_PREFIX_KIHON}Free2"),
        teachers=_parse_teachers(_get_text(soup, f"{_PREFIX_KIHON}Kyoin")),
        term=_get_text(soup, f"{_PREFIX_KIHON}KaikouKikan"),
        credits=_first_char_int(_get_text(soup, f"{_PREFIX_KIHON}Tanisu")),
        teaching_methods=_parse_checked_items(
            _get_text(soup, f"{_PREFIX_DETAIL}01_ctlNaiyou_chk_lblNaiyou")
        ),
        delivery_modes=_parse_checked_items(
            _get_text(soup, f"{_PREFIX_DETAIL}02_ctlNaiyou_radio_lblNaiyou")
        ),
        objectives=_get_text(soup, f"{_PREFIX_DETAIL}03_ctlNaiyou00_lblNaiyou"),
        overview=_get_text(soup, f"{_PREFIX_DETAIL}04_ctlNaiyou00_lblNaiyou"),
        diploma_policies=_parse_diploma_policies(
            _get_text(soup, f"{_PREFIX_DETAIL}05_ctlNaiyou_chk_lblNaiyou")
        ),
        textbooks=_parse_books(soup, "06"),
        references=_parse_books(soup, "07"),
        enrollment_info=_parse_enrollment_info(soup),
        teaching_certificate=_parse_teaching_certificate(soup),
        grading_criteria=_get_text(soup, f"{_PREFIX_DETAIL}10_ctlNaiyou00_lblNaiyou"),
        evaluation_ratio=_parse_evaluation_ratio(soup),
        teacher_message=_get_text(soup, f"{_PREFIX_DETAIL}12_ctlNaiyou00_lblNaiyou"),
        schedule=_parse_schedule(soup),
        credit_auditing=_parse_checkbox_bool(
            _get_text(soup, f"{_PREFIX_DETAIL}14_ctlNaiyou_radio_lblNaiyou")
        ),
        practitioner_info=_get_text(soup, f"{_PREFIX_DETAIL}15_ctlNaiyou00_lblNaiyou"),
    )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _get_text(soup: BeautifulSoup, element_id: str) -> str | None:
    """IDで要素を探し、テキストを返す。<br> は改行に変換。空文字列は None。"""
    tag = soup.find(id=element_id)
    if tag is None or not isinstance(tag, Tag):
        return None
    for br in tag.find_all("br"):
        br.replace_with("\n")
    text = tag.get_text().strip()
    return text or None


def _first_char_int(text: str | None) -> int | None:
    if text and text[0].isdigit():
        return int(text[0])
    return None


def _split_or_empty(text: str | None, sep: str) -> list[str]:
    if not text:
        return []
    return text.split(sep)


def _parse_checkbox_bool(text: str | None) -> bool | None:
    if text is None:
        return None
    return text.startswith("■")


def _parse_checked_items(text: str | None) -> list[str]:
    """チェックボックステキストからチェック済み項目のみを返す。"""
    if not text:
        return []
    items = []
    for item in re.split(r"[\n　]", text):
        if item and item[0] == "■":
            items.append(item[2:])
    return items


def _parse_diploma_policies(text: str | None) -> list[str]:
    if not text:
        return []
    return [line[2:] for line in text.splitlines() if len(line) > 2]


def _parse_teachers(text: str | None) -> list[Teacher]:
    if not text:
        return []
    teachers = []
    for name in re.split(r"[\n ,、・]", text):
        name = name.strip()
        if not name:
            continue
        if name.endswith("（主）"):
            teachers.append(Teacher(name=name.removesuffix("（主）"), is_primary=True))
        else:
            teachers.append(Teacher(name=name, is_primary=False))
    return teachers


def _parse_books(soup: BeautifulSoup, prefix_num: str) -> list[Book]:
    """教科書 (prefix_num="06") と参考図書 (prefix_num="07") の共通パーサー。"""
    books: list[Book] = []
    i = 1
    while True:
        id_prefix = (
            f"{_PREFIX_DETAIL}{prefix_num}_ctlNaiyou_Book_repNaiyouBook_ctl{i:02}_lbl"
        )
        title = _get_text(soup, f"{id_prefix}BOOK_NAME")
        if not title:
            break
        books.append(
            Book(
                title=title,
                publication_year=_parse_optional_int(
                    _get_text(soup, f"{id_prefix}PUBLICATION_YEAR"),
                    zero_as_none=True,
                ),
                author=_get_text(soup, f"{id_prefix}AUTHOR"),
                publisher=_get_text(soup, f"{id_prefix}PUBLISHER"),
                price=_parse_optional_int(
                    _get_text(soup, f"{id_prefix}MONEY"), strip_commas=True
                ),
                isbn=_get_text(soup, f"{id_prefix}ISBN"),
                available_on_campus=_parse_checkbox_bool(
                    _get_text(soup, f"{id_prefix}CAMPUS_SALES")
                )
                or False,
            )
        )
        i += 1
    return books


def _parse_optional_int(
    text: str | None, *, strip_commas: bool = False, zero_as_none: bool = False
) -> int | None:
    if not text:
        return None
    if strip_commas:
        text = text.replace(",", "")
    try:
        value = int(text)
    except ValueError:
        return None
    if zero_as_none and value == 0:
        return None
    return value


def _parse_enrollment_info(soup: BeautifulSoup) -> EnrollmentInfo:
    prefix = f"{_PREFIX_DETAIL}08_ctlNaiyou_course_lbl"

    prerequisites: list[str] = []
    for i in range(1, 7):
        text = _get_text(soup, f"{prefix}REQUIRED{i}")
        if text:
            prerequisites.append(text)
        else:
            break

    recommended: list[str] = []
    for i in range(1, 7):
        text = _get_text(soup, f"{prefix}RECOMMENDATION{i}")
        if text:
            recommended.append(text)
        else:
            break

    return EnrollmentInfo(
        prerequisites=prerequisites,
        recommended=recommended,
        required_materials=_get_text(soup, f"{prefix}BRING"),
        other=_get_text(soup, f"{prefix}OTHER"),
    )


def _parse_teaching_certificate(soup: BeautifulSoup) -> TeachingCertificate | None:
    prefix = f"{_PREFIX_DETAIL}09_ctlNaiyou_Teaching_lbl"
    subject = _get_text(soup, f"{prefix}SUBJECT")
    enforcement = _get_text(soup, f"{prefix}ENFORCEMENT")
    # QUALIFICATION は見出し「教員免許状取得の為の」に対応する欄だが、
    # 全科目で常に空のため未使用。復活させる場合は次行を有効化し、
    # TeachingCertificate に qualification フィールドを追加する。
    # qualification = _get_text(soup, f"{prefix}QUALIFICATION")
    if subject is None and enforcement is None:
        return None
    return TeachingCertificate(subject=subject, enforcement=enforcement)


def _parse_evaluation_ratio(soup: BeautifulSoup) -> EvaluationRatio:
    prefix = f"{_PREFIX_DETAIL}11_ctlNaiyou32_repNaiyou02_ctl02_lblMokuhyo_"
    field_map = [
        (1, "exam"),
        (2, "quiz"),
        (3, "report"),
        (4, "presentation"),
        (6, "portfolio"),
        (7, "other"),
    ]
    values: dict[str, int] = {}
    for idx, field_name in field_map:
        text = _get_text(soup, f"{prefix}{idx}")
        values[field_name] = int(text) if text else 0
    return EvaluationRatio(**values)


def _parse_schedule(soup: BeautifulSoup) -> list[ScheduleEntry]:
    entries: list[ScheduleEntry] = []
    i = 1
    while True:
        id_prefix = f"{_PREFIX_DETAIL}13_ctlNaiyou01_repNaiyou01_ctl{i:02}_lbl"
        number = _get_text(soup, f"{id_prefix}PLAN_TIMES")
        if not number:
            break
        entries.append(
            ScheduleEntry(
                number=number,
                content=_get_text(soup, f"{id_prefix}PLAN_NAIYOU"),
                teaching_methods=_parse_checked_items(
                    _get_text(soup, f"{id_prefix}JISAN_BUTU")
                ),
                teachers=_parse_schedule_teachers(
                    _get_text(soup, f"{id_prefix}GAKUSHU_KADAI")
                ),
            )
        )
        i += 1
    return entries


def _parse_schedule_teachers(text: str | None) -> list[str]:
    if not text:
        return []
    return [
        name.removesuffix("（主）").strip()
        for name in re.split(r"[\n ,、・]", text)
        if name.strip()
    ]

import json
import re
from datetime import datetime
from typing import Any

import requests
from bs4 import BeautifulSoup, Tag

from .aaa import AAA
from .utils import convert_http_date_to_datetime, make_soup


class SyllabusData(AAA):
    """A class to represent syllabus data retrieved from Active Academy Advance (AAA).

    Attributes:
        session (requests.Session | None): The session to use for the search.
    """

    def __init__(
        self,
        jugyouNendo: str,
        gakouKbn: str,
        syllabusNo: str,
        session: requests.Session | None = None,
    ) -> None:
        """Initializes the SyllabusData instance with the specified syllabus data.

        Args:
            jugyouNendo (str): The academic year (年度) for the syllabus data.
            gakouKbn (str): Unknown parameter (学校学部区分?). Always "2" in the Shunan University syllabus.
            syllabusNo (str): The syllabus number (シラバス番号) for the syllabus data.
            session (requests.Session, optional): The session to use for the search. Defaults to None.

        Raises:
            ValueError: If jugyouNendo is less than 2023.
        """

        if jugyouNendo < "2023":
            raise ValueError("jugyouNendo must be greater than or equal to 2023")

        self._jugyouNendo: str = jugyouNendo
        self._gakouKbn: str = gakouKbn
        self._syllabusNo: str = syllabusNo
        self.session: requests.Session | None = session
        self._fetched_at: datetime | None = None
        self._html: str | None = None
        self._soup: BeautifulSoup | None = None

    @property
    def jugyouNendo(self) -> str:
        return self._jugyouNendo

    @property
    def gakouKbn(self) -> str:
        return self._gakouKbn

    @property
    def syllabusNo(self) -> str:
        return self._syllabusNo

    @property
    def url(self) -> str:
        """The URL of the syllabus data."""
        return f"{self.SYLLABUS_DATA_URL}?me=EU&sk={self.jugyouNendo}_{self.gakouKbn}_{self.syllabusNo}&syw=1"

    def fetch(self) -> None:
        """Fetches the syllabus data from the server and stores the HTML content.

        Sends a GET request to the syllabus data URL and stores the HTML content
        in the instance variable. Raises an error if the server redirects to an
        error page.

        Raises:
            ValueError: If the server redirects to an error page.
        """

        response = requests.get(self.url)
        response.raise_for_status()
        if self.is_error_page(response.url):
            raise ValueError(f"Redirected to error page: {response.url}")
        self._fetched_at = convert_http_date_to_datetime(response.headers["Date"])
        self._html = response.text

    @property
    def html(self) -> str:
        """The HTML content of the search results.

        If the HTML content has not been fetched yet, it calls `fetch()` to retrieve
        the data.

        Returns:
            str: The HTML content of the search results.
        """

        if self._html is None:
            self.fetch()
            assert self._html is not None  # Ensure that the HTML content is not None
        return self._html

    @property
    def soup(self) -> BeautifulSoup:
        """The BeautifulSoup object of the HTML content.

        Returns:
            BeautifulSoup: A BeautifulSoup object representing the parsed HTML.
        """

        if self._soup is None:
            self._soup = make_soup(self.html)
        return self._soup

    def get_text_by_id(self, id: str) -> str | None:
        """Returns the text content of an element with the specified ID.

        Args:
            id (str): The ID of the element to find.

        Returns:
            str | None: The text content of the element if found, None otherwise.
        """

        # Find the tag with the specified ID
        if (tag := self.soup.find(id=id)) is None:
            return None

        # Ensure that the tag is a Tag object
        if not isinstance(tag, Tag):
            return None

        # Replace <br> tags with newlines
        for br in tag.find_all("br"):
            br.replace_with("\n")

        return tag.get_text().strip()  # Return the stripped text content

    def parse(self) -> dict[str, Any]:
        """Parses the syllabus data and returns the content as a dictionary.

        Returns:
            dict[str, Any]: A dictionary containing the parsed syllabus data.
        """
        PREFIX_KIHON = "ctl00_cphMain_UcSyllKihon_lbl"
        PREFIX_DETAIL = "ctl00_cphMain_UcSyllContent_repContent_ctl"

        def parse_checkboxes(text: str) -> dict[str, bool]:
            checkboxes: dict[str, bool] = {}
            for item in re.split(r"[\n　]", text):
                checkboxes[item[2:]] = item[0] == "■"
            return checkboxes

        # 教科書
        def get_textbooks() -> list[dict[str, Any]]:
            textbooks: list[dict[str, Any]] = []
            i = 1
            while True:
                id_prefix = (
                    f"{PREFIX_DETAIL}06_ctlNaiyou_Book_repNaiyouBook_ctl{i:02}_lbl"
                )
                if title := self.get_text_by_id(f"{id_prefix}BOOK_NAME"):
                    textbooks.append(
                        {
                            # 書類名
                            "title": title,
                            # 発行年（西暦）
                            "year": (
                                int(text)
                                if (
                                    text := self.get_text_by_id(
                                        f"{id_prefix}PUBLICATION_YEAR"
                                    )
                                )
                                is not None
                                and text.strip()  # Skip empty strings
                                else None
                            ),
                            # 著作者名
                            "author": self.get_text_by_id(f"{id_prefix}AUTHOR"),
                            # 出版社
                            "publisher": self.get_text_by_id(f"{id_prefix}PUBLISHER"),
                            # 金額（税込）
                            "price": (
                                int(text.replace(",", ""))
                                if (text := self.get_text_by_id(f"{id_prefix}MONEY"))
                                is not None
                                and text.strip()  # Skip empty strings
                                else None
                            ),
                            # ISBN
                            "isbn": self.get_text_by_id(f"{id_prefix}ISBN"),
                            # 学内販売
                            "available_on_campus": (
                                text.startswith("■")
                                if (
                                    text := self.get_text_by_id(
                                        f"{id_prefix}CAMPUS_SALES"
                                    )
                                )
                                is not None
                                else None
                            ),
                        }
                    )
                else:
                    break
                i += 1
            return textbooks

        # 参考図書
        def get_reference_books() -> list[dict[str, Any]]:
            reference_books: list[dict[str, Any]] = []
            i = 1
            while True:
                id_prefix = (
                    f"{PREFIX_DETAIL}07_ctlNaiyou_Book_repNaiyouBook_ctl{i:02}_lbl"
                )
                if title := self.get_text_by_id(f"{id_prefix}BOOK_NAME"):
                    reference_books.append(
                        {
                            # 書類名
                            "title": title,
                            # 発行年（西暦）
                            "year": (
                                int(text)
                                if (
                                    text := self.get_text_by_id(
                                        f"{id_prefix}PUBLICATION_YEAR"
                                    )
                                )
                                is not None
                                and text.strip()  # Skip empty strings
                                else None
                            ),
                            # 著作者名
                            "author": self.get_text_by_id(f"{id_prefix}AUTHOR"),
                            # 出版社
                            "publisher": self.get_text_by_id(f"{id_prefix}PUBLISHER"),
                            # 金額（税込）
                            "price": (
                                int(text.replace(",", ""))
                                if (text := self.get_text_by_id(f"{id_prefix}MONEY"))
                                is not None
                                and text.strip()  # Skip empty strings
                                else None
                            ),
                            # ISBN
                            "isbn": self.get_text_by_id(f"{id_prefix}ISBN"),
                            # 学内販売
                            "available_on_campus": (
                                text.startswith("■")
                                if (
                                    text := self.get_text_by_id(
                                        f"{id_prefix}CAMPUS_SALES"
                                    )
                                )
                                is not None
                                else None
                            ),
                        }
                    )
                else:
                    break
                i += 1
            return reference_books

        # 履修上の注意／先修条件科目（必須）
        def get_required_courses() -> list[str]:
            courses: list[str] = []
            for i in range(1, 7):
                if text := self.get_text_by_id(
                    f"{PREFIX_DETAIL}08_ctlNaiyou_course_lblREQUIRED{i}"
                ):
                    courses.append(text)
                else:
                    break
            return courses

        # 履修上の注意／先修条件科目（推奨）
        def get_recommended_courses() -> list[str]:
            courses: list[str] = []
            for i in range(1, 7):
                if text := self.get_text_by_id(
                    f"{PREFIX_DETAIL}08_ctlNaiyou_course_lblRECOMMENDATION{i}"
                ):
                    courses.append(text)
                else:
                    break
            return courses

        # 学生に対する評価
        def get_evaluation_ratio() -> dict[str, int]:
            evaluation_ratio: dict[str, int] = {}
            for i, label in (
                (1, "試験"),
                (2, "小テスト"),
                (3, "レポート"),
                (4, "発表・実技"),
                (6, "ポートフォリオ"),
                (7, "その他"),
            ):
                if text := self.get_text_by_id(
                    f"{PREFIX_DETAIL}11_ctlNaiyou32_repNaiyou02_ctl02_lblMokuhyo_{i}"
                ):
                    evaluation_ratio[label] = int(text)
                else:
                    evaluation_ratio[label] = 0
            return evaluation_ratio

        # 授業計画と学習課題
        def get_schedule() -> list[dict[str, Any]]:
            schedules: list[dict[str, Any]] = []
            i = 1
            while True:
                id_prefix = f"{PREFIX_DETAIL}13_ctlNaiyou01_repNaiyou01_ctl{i:02}_lbl"
                if session := self.get_text_by_id(f"{id_prefix}PLAN_TIMES"):
                    schedules.append(
                        {
                            # 回数
                            "session": session,
                            # 授業内容
                            "content": self.get_text_by_id(f"{id_prefix}PLAN_NAIYOU"),
                            # 授業方法
                            "methods": (
                                [
                                    checkbox[0]
                                    for checkbox in parse_checkboxes(text).items()
                                    if checkbox[1]
                                ]
                                if (
                                    text := self.get_text_by_id(
                                        f"{id_prefix}JISAN_BUTU"
                                    )
                                )
                                is not None
                                else None
                            ),
                            # 担当教員
                            "teachers": (
                                [
                                    teacher.removesuffix("（主）").strip()
                                    for teacher in re.split(r"[\n ,、・]", text)
                                ]
                                if (
                                    text := self.get_text_by_id(
                                        f"{id_prefix}GAKUSHU_KADAI"
                                    )
                                )
                                is not None
                                else None
                            ),
                        }
                    )
                else:
                    break
                i += 1
            return schedules

        self.fetch()
        assert self._fetched_at is not None  # Ensure that the fetched_at is not None

        content: dict[str, Any] = {
            # The date and time when the data was fetched
            "_fetched_at": self._fetched_at.isoformat() + "Z",
            # 授業科目名称
            "name_ja": self.get_text_by_id(f"{PREFIX_KIHON}KougiName"),
            # 英文科目名称
            "name_en": self.get_text_by_id(f"{PREFIX_KIHON}EibunName"),
            # シラバス番号
            "syllabus_number": self.get_text_by_id(f"{PREFIX_KIHON}SyllabusNo"),
            # 科目ナンバー
            "course_number": self.get_text_by_id(f"{PREFIX_KIHON}KAMOKU_NO"),
            # 対象学科・コース
            "target_departments_and_courses": (
                text.split("、")
                if (text := self.get_text_by_id(f"{PREFIX_KIHON}COURSE_NAME"))
                is not None
                else None
            ),
            # 専門・総合・教職
            "type": self.get_text_by_id(f"{PREFIX_KIHON}SPECIALTY_NAME"),
            # 主学科
            "main_department": self.get_text_by_id(f"{PREFIX_KIHON}SUBJECT"),
            # 要件
            "requirements": self.get_text_by_id(f"{PREFIX_KIHON}REQUIREMENT"),
            # 配当年
            "year": (
                int(text[0])
                if (text := self.get_text_by_id(f"{PREFIX_KIHON}HaitouNen")) is not None
                and text.strip()  # Skip empty strings
                else None
            ),
            # 時限（現シラバスで非表示）
            "period": self.get_text_by_id(f"{PREFIX_KIHON}Free1"),
            # 必選（検索画面にのみ表示、旧履修上の注意事項）
            "required_or_elective": self.get_text_by_id(f"{PREFIX_KIHON}Hissen"),
            # 科目区分
            "course_category": self.get_text_by_id(f"{PREFIX_KIHON}Free2"),
            # 担当形態
            "class_type": self.get_text_by_id(f"{PREFIX_KIHON}FORM_CODE"),
            # 担当教員
            "teachers": (
                [
                    (
                        {"name": teacher.removesuffix("（主）"), "main": True}
                        if teacher.endswith("（主）")
                        else {"name": teacher, "main": False}
                    )
                    for teacher in re.split(r"[\n ,、・]", text)
                ]
                if (text := self.get_text_by_id(f"{PREFIX_KIHON}Kyoin")) is not None
                else None
            ),
            # 開講期間
            "term": self.get_text_by_id(f"{PREFIX_KIHON}KaikouKikan"),
            # 単位数
            "credits": (
                int(text[0])
                if (text := self.get_text_by_id(f"{PREFIX_KIHON}Tanisu")) is not None
                and text.strip()  # Skip empty strings
                else None
            ),
            # 授業方法
            "teaching_methods": (
                [
                    checkbox[0]
                    for checkbox in parse_checkboxes(text).items()
                    if checkbox[1]
                ]
                if (
                    text := self.get_text_by_id(
                        f"{PREFIX_DETAIL}01_ctlNaiyou_chk_lblNaiyou"
                    )
                )
                is not None
                else None
            ),
            # 授業形態
            "class_forms": (
                [
                    checkbox[0]
                    for checkbox in parse_checkboxes(text).items()
                    if checkbox[1]
                ]
                if (
                    text := self.get_text_by_id(
                        f"{PREFIX_DETAIL}02_ctlNaiyou_radio_lblNaiyou"
                    )
                )
                is not None
                else None
            ),
            # 授業のテーマ及び到達目標
            "themes_and_goals": self.get_text_by_id(
                f"{PREFIX_DETAIL}03_ctlNaiyou00_lblNaiyou"
            ),
            # 授業の概要
            "overview": self.get_text_by_id(f"{PREFIX_DETAIL}04_ctlNaiyou00_lblNaiyou"),
            # 対応するディプロマ・ポリシー
            "corresponding_diploma_policies": (
                [line[2:] for line in text.splitlines()]
                if (
                    text := self.get_text_by_id(
                        f"{PREFIX_DETAIL}05_ctlNaiyou_chk_lblNaiyou"
                    )
                )
                is not None
                else None
            ),
            # 教科書
            "textbooks": get_textbooks(),
            # 参考図書
            "reference_books": get_reference_books(),
            # 履修上の注意
            "notes_on_enrollment": {
                # 先修条件科目（必須）
                "required_courses": get_required_courses(),
                # 先修条件科目（推奨）
                "recommended_courses": get_recommended_courses(),
                # 持参物
                "brings": self.get_text_by_id(
                    f"{PREFIX_DETAIL}08_ctlNaiyou_course_lblBRING"
                ),
                # その他
                "other": self.get_text_by_id(
                    f"{PREFIX_DETAIL}08_ctlNaiyou_course_lblOTHER"
                ),
            },
            # 評価基準
            "evaluation_criteria": self.get_text_by_id(
                f"{PREFIX_DETAIL}10_ctlNaiyou00_lblNaiyou"
            ),
            # 学生に対する評価
            "evaluation_ratio": get_evaluation_ratio(),
            # 担当教員からのメッセージ（予習・復習内容・時間にも言及）
            "message_from_teachers": self.get_text_by_id(
                f"{PREFIX_DETAIL}12_ctlNaiyou00_lblNaiyou"
            ),
            # 授業計画と学習課題
            "schedule": get_schedule(),
            # 科目等履修制度
            "open_to_non_students": (
                text.startswith("■")
                if (
                    text := self.get_text_by_id(
                        f"{PREFIX_DETAIL}14_ctlNaiyou_radio_lblNaiyou"
                    )
                )
                is not None
                else None
            ),
            # 実務家教員担当科目に関する記載
            "practitioner": self.get_text_by_id(
                f"{PREFIX_DETAIL}15_ctlNaiyou00_lblNaiyou"
            ),
        }

        return content

    def save_as_json(self, filename: str) -> None:
        """Saves the parsed syllabus data as a JSON file.

        Args:
            filename (str): The name of the JSON file to save the data to.
        """

        with open(filename, "w") as file:
            json.dump(self.parse(), file, ensure_ascii=False, indent=4)
            file.write("\n")  # Add a newline character at the end of the file

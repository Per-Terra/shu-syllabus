from __future__ import annotations

import re

import requests

from ._aspnet import get_hidden_fields
from ._models import Syllabus
from ._parser import parse_syllabus
from ._urls import ERROR_URL, SEARCH_URL, SYLLABUS_URL
from ._utils import convert_http_date_to_datetime

_GAKOU_KBN = "2"


class Scraper:
    """AAAシステムからシラバスデータを取得するクライアント。

    requests.Session を使い、接続プーリングと Cookie 管理を行う。
    コンテキストマネージャとして使用可能。

    Example::

        with Scraper() as scraper:
            codes = scraper.search("2025")
            syllabus = scraper.fetch("2025", codes[0])
    """

    def __init__(self, session: requests.Session | None = None) -> None:
        self._session = session or requests.Session()
        self._owns_session = session is None

    def __enter__(self) -> Scraper:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def close(self) -> None:
        if self._owns_session:
            self._session.close()

    def search(
        self,
        nendo: str,
        *,
        course_name: str = "",
        teacher_name: str = "",
        keyword_1: str = "",
        keyword_1_operator: str = "and",
        keyword_2: str = "",
        keyword_2_operator: str = "and",
        keyword_3: str = "",
    ) -> list[str]:
        """指定年度のシラバス番号一覧を取得する。

        Args:
            nendo: 年度（例: "2025"）。
            course_name: 講義科目名で絞り込み。
            teacher_name: 教員名で絞り込み。
            keyword_1: キーワード1。
            keyword_1_operator: キーワード1の演算子（"and" or "or"）。
            keyword_2: キーワード2。
            keyword_2_operator: キーワード2の演算子（"and" or "or"）。
            keyword_3: キーワード3。

        Returns:
            シラバス番号のリスト（例: ["1000500A", "1000600A"]）。
        """
        if keyword_1_operator not in ("and", "or"):
            raise ValueError("keyword_1_operator must be 'and' or 'or'")
        if keyword_2_operator not in ("and", "or"):
            raise ValueError("keyword_2_operator must be 'and' or 'or'")

        fields = get_hidden_fields(self._session, SEARCH_URL)
        params = {
            "ctl00$cphMain$cmbNendo": nendo,
            "ctl00$cphMain$cmbSchGakubu": "",
            "ctl00$cphMain$txtSearchKougi_Name": course_name,
            "ctl00$cphMain$txtSeachKyoin_Name": teacher_name,
            "ctl00$cphMain$txtSeachKeyword1": keyword_1,
            "ctl00$cphMain$cmbSerchKeyworkOpe1": keyword_1_operator,
            "ctl00$cphMain$txtSeachKeyword2": keyword_2,
            "ctl00$cphMain$cmbSerchKeyworkOpe2": keyword_2_operator,
            "ctl00$cphMain$txtSeachKeyword3": keyword_3,
            "ctl00$cphMain$ibtnSearch.x": "0",
            "ctl00$cphMain$ibtnSearch.y": "0",
        }
        response = self._session.post(SEARCH_URL, data={**fields, **params})
        response.raise_for_status()
        _check_error(response.url)
        pattern = re.compile(r"Syllabus_Data\('([^']*)','([^']*)','([^']*)'\)")
        return [syllabus_no for _, _, syllabus_no in pattern.findall(response.text)]

    def fetch(self, nendo: str, syllabus_no: str) -> Syllabus:
        """シラバスを1件取得してパースする。

        Args:
            nendo: 年度（例: "2025"）。2023 以降のみ対応。
            syllabus_no: シラバス番号（例: "1000600A"）。

        Returns:
            パース済みの Syllabus オブジェクト。
        """
        if nendo < "2023":
            raise ValueError("2023年度以降のみ対応しています")
        url = f"{SYLLABUS_URL}?me=EU&sk={nendo}_{_GAKOU_KBN}_{syllabus_no}&syw=1"
        response = self._session.get(url)
        response.raise_for_status()
        _check_error(response.url)
        fetched_at = (
            convert_http_date_to_datetime(response.headers["Date"]).isoformat() + "Z"
        )
        return parse_syllabus(
            response.text, fetched_at=fetched_at, syllabus_no=syllabus_no
        )


def _check_error(url: str) -> None:
    if url.startswith(ERROR_URL):
        raise RuntimeError(f"AAAがエラーページにリダイレクトしました: {url}")

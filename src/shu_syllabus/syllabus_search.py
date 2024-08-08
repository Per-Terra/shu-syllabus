import re

import requests

from .aaa import AAA
from .aspnet import get_aspnet_hidden_fields


class SyllabusSearch(AAA):
    """A class to represent a list of syllabuses retrieved from Active Academy Advance (AAA).

    Attributes:
        aspnet_fields (dict[str, str]): ASP.NET form fields required for the search request.
        search_params (dict[str, str]): Search parameters for the syllabus query.
        session (requests.Session | None): The session to use for the search.
    """

    def __init__(
        self,
        nendo: str,
        kougi: str = "",
        kyoin: str = "",
        keyword_1: str = "",
        keyword_1_operator: str = "and",
        keyword_2: str = "",
        keyword_2_operator: str = "and",
        keyword_3: str = "",
        session: requests.Session | None = None,
    ) -> None:
        """Initializes the SyllabusSearch instance with search parameters.

        Args:
            nendo (str): The academic year (年度) for the search.
            kougi (str, optional): The course name (講義科目名) for the search. Defaults to "".
            kyoin (str, optional): The teacher's name (教員名) for the search. Defaults to "".
            keyword_1 (str, optional): The first keyword for the search. Defaults to "".
            keyword_1_operator (str, optional): The operator for combining the first keyword. Defaults to "and".
            keyword_2 (str, optional): The second keyword for the search. Defaults to "".
            keyword_2_operator (str, optional): The operator for combining the second keyword. Defaults to "and".
            keyword_3 (str, optional): The third keyword for the search. Defaults to "".
            session (requests.Session, optional): The session to use for the search. Defaults to None.

        Raises:
            ValueError: If keyword_1_operator or keyword_2_operator is not "and" or "or".
        """

        # Validate keyword operators
        if keyword_1_operator not in ("and", "or"):
            raise ValueError("Invalid keyword_1_operator")
        if keyword_2_operator not in ("and", "or"):
            raise ValueError("Invalid keyword_2_operator")

        # Initialize ASP.NET form fields and search parameters
        self.aspnet_fields: dict[str, str] = get_aspnet_hidden_fields(
            self.SYLLABUS_SEARCH_URL
        )
        self.search_params: dict[str, str] = {
            # 年度指定
            "ctl00$cphMain$cmbNendo": nendo,
            # 開講学部学科
            "ctl00$cphMain$cmbSchGakubu": "",
            # 講義科目名
            "ctl00$cphMain$txtSearchKougi_Name": kougi,
            # 教員名
            "ctl00$cphMain$txtSeachKyoin_Name": kyoin,
            # キーワード
            "ctl00$cphMain$txtSeachKeyword1": keyword_1,
            "ctl00$cphMain$cmbSerchKeyworkOpe1": keyword_1_operator,
            "ctl00$cphMain$txtSeachKeyword2": keyword_2,
            "ctl00$cphMain$cmbSerchKeyworkOpe2": keyword_2_operator,
            "ctl00$cphMain$txtSeachKeyword3": keyword_3,
            # 検索ボタンの位置（詳細不明）
            # 検索結果画面でページングを行う場合に使用されていたと思われる
            # 整数（数値？）ならなんでもよい
            "ctl00$cphMain$ibtnSearch.x": "0",
            "ctl00$cphMain$ibtnSearch.y": "0",
        }
        self.session: requests.Session | None = session
        self._html: str | None = None

    def fetch(self) -> None:
        """Fetches the search results from the server and stores the HTML content.

        Sends a POST request with the combined form fields and search parameters
        and stores the HTML content in the instance variable. Raises an error if
        the server redirects to an error page.

        Raises:
            ValueError: If the server redirects to an error page.
        """

        # response = requests.post(
        #     self.SYLLABUS_SEARCH_URL,
        #     data={**self.aspnet_fields, **self.search_params},
        # )
        response = (
            self.session.post(
                self.SYLLABUS_SEARCH_URL,
                data={**self.aspnet_fields, **self.search_params},
            )
            if self.session
            else requests.post(
                self.SYLLABUS_SEARCH_URL,
                data={**self.aspnet_fields, **self.search_params},
            )
        )
        response.raise_for_status()
        if self.is_error_page(response.url):
            raise ValueError(f"Redirected to error page: {response.url}")
        self._html = response.text

    @property
    def html(self) -> str:
        """Returns the HTML content of the search results.

        If the HTML content has not been fetched yet, it calls `fetch()` to retrieve
        the data.

        Returns:
            str: The HTML content of the search results.
        """

        if self._html is None:
            self.fetch()
            assert self._html is not None  # Ensure that the HTML content is not None
        return self._html

    def parse(self):
        """Parses the HTML content to extract syllabus codes.

        Uses a regular expression to find and return all matches for syllabus codes.

        Yields:
            tuple[str, str, str]: A tuple containing the extracted syllabus codes.
        """

        parser = re.compile(r"Syllabus_Data\('([^']*)','([^']*)','([^']*)'\)")
        for match in parser.finditer(self.html):
            yield match.groups()

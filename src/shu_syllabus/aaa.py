import urllib.parse


class AAA:
    """A class to represent Active Academy Advance (AAA) URLs."""

    BASE_URL: str = "https://aaaweb.shunan-u.ac.jp/aa_web/"
    SYLLABUS_SEARCH_URL: str = urllib.parse.urljoin(
        BASE_URL, "syllabus/se0010.aspx?me=EU&opi=mt0010"
    )
    SYLLABUS_DATA_LEGACY_URL: str = urllib.parse.urljoin(
        BASE_URL, "syllabus/se0030.aspx"
    )
    SYLLABUS_DATA_URL: str = urllib.parse.urljoin(BASE_URL, "syllabus/se0032.aspx")
    ERROR_URL: str = urllib.parse.urljoin(BASE_URL, "customError.aspx")

    def is_error_page(self, url: str) -> bool:
        """Checks if the URL is an error page.

        Args:
            url (str): The URL to check.

        Returns:
            bool: True if the URL is an error page, False otherwise.
        """

        return url.startswith(self.ERROR_URL)

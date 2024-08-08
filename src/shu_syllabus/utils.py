from datetime import datetime

from bs4 import BeautifulSoup


def make_soup(html: str) -> BeautifulSoup:
    """Parses HTML content into a BeautifulSoup object.

    Args:
        html (str): The HTML content as a string.

    Returns:
        BeautifulSoup: A BeautifulSoup object representing the parsed HTML.
    """

    return BeautifulSoup(html, "html.parser")


def convert_http_date_to_datetime(http_date: str) -> datetime:
    """Converts an HTTP date string to a datetime object.

    Args:
        http_date (str): The HTTP date string.

    Returns:
        datetime: The datetime object representing the HTTP date.
    """

    return datetime.strptime(http_date, "%a, %d %b %Y %H:%M:%S %Z")

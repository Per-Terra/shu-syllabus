from datetime import datetime

from bs4 import BeautifulSoup


def convert_http_date_to_datetime(http_date: str) -> datetime:
    return datetime.strptime(http_date, "%a, %d %b %Y %H:%M:%S %Z")


def make_soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "html.parser")


def letter_to_number(s: str) -> int:
    """Excel列番号方式のアルファベットを数値に変換する。"""
    result = 0
    for char in s:
        result = result * 26 + (ord(char) - ord("A") + 1)
    return result

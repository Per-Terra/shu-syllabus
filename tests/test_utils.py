from datetime import datetime

from shu_syllabus._utils import (
    convert_http_date_to_datetime,
    letter_to_number,
    make_soup,
)


def test_letter_to_number_single() -> None:
    assert letter_to_number("A") == 1
    assert letter_to_number("B") == 2
    assert letter_to_number("Z") == 26


def test_letter_to_number_double() -> None:
    assert letter_to_number("AA") == 27
    assert letter_to_number("AZ") == 52
    assert letter_to_number("BA") == 53


def test_letter_to_number_triple() -> None:
    assert letter_to_number("AAA") == 703


def test_convert_http_date() -> None:
    result = convert_http_date_to_datetime("Fri, 04 Apr 2025 05:54:56 GMT")
    assert isinstance(result, datetime)
    assert result.year == 2025
    assert result.month == 4
    assert result.day == 4


def test_make_soup() -> None:
    soup = make_soup("<p>hello</p>")
    assert soup.find("p") is not None
    assert soup.find("p").text == "hello"  # type: ignore[union-attr]

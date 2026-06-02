from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture(scope="module")
def syllabus_html() -> str:
    """意思決定科学 (1000600A) — 教員1名、教科書なし、参考図書あり。"""
    return (FIXTURES_DIR / "syllabus_page.html").read_text()


@pytest.fixture(scope="module")
def syllabus_html_complex() -> str:
    """スポーツ医学 (2011300A) — 複数教員、教科書、DP、先修条件あり。"""
    return (FIXTURES_DIR / "syllabus_page_2011300A.html").read_text()


@pytest.fixture(scope="module")
def search_html() -> str:
    return (FIXTURES_DIR / "search_results.html").read_text()

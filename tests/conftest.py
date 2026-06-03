from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture(scope="module")
def syllabus_html_nursing() -> str:
    """基礎看護技術Ⅱ (2116500A, 2026前期) — 複数教員(主担当あり)・教科書/参考図書
    (全フィールド)・履修上の注意4項目・実技/試験評価・複数教員回を含む授業計画・
    実務家教員・科目等履修不可。"""
    return (FIXTURES_DIR / "syllabus_page_2116500A.html").read_text()


@pytest.fixture(scope="module")
def syllabus_html_economics() -> str:
    """国際経済学Ⅱ (2038200A, 2026前期) — 単独教員・主学科/複数学科・教職関連
    (改行区切りの enforcement)・価格/ISBN が欠落した教科書。"""
    return (FIXTURES_DIR / "syllabus_page_2038200A.html").read_text()


@pytest.fixture(scope="module")
def syllabus_html_consultation() -> str:
    """教育相談Ⅰ (7002700A, 2026前期) — オムニバス・科目等履修可・小テスト/
    ポートフォリオ評価・複数学科・実務家教員。"""
    return (FIXTURES_DIR / "syllabus_page_7002700A.html").read_text()


@pytest.fixture(scope="module")
def search_html() -> str:
    return (FIXTURES_DIR / "search_results.html").read_text()

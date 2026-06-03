from unittest.mock import MagicMock, patch

from shu_syllabus._scraper import Scraper


def test_scraper_context_manager() -> None:
    scraper = Scraper()
    with scraper:
        pass
    # Session should be closed after exiting context


def test_scraper_with_external_session() -> None:
    session = MagicMock()
    scraper = Scraper(session=session)
    scraper.close()
    session.close.assert_not_called()


def test_scraper_closes_own_session() -> None:
    scraper = Scraper()
    scraper.close()


def test_search_parses_syllabus_numbers(search_html: str) -> None:
    with patch.object(Scraper, "__init__", lambda self, **kw: None):
        scraper = Scraper()
        scraper._session = MagicMock()
        scraper._owns_session = True

        mock_fields_response = MagicMock()
        mock_fields_response.text = '<input id="__VIEWSTATE" value="test" />'
        mock_fields_response.raise_for_status = MagicMock()

        mock_search_response = MagicMock()
        mock_search_response.text = search_html
        mock_search_response.url = (
            "https://aaaweb.shunan-u.ac.jp/aa_web/syllabus/se0010.aspx"
        )
        mock_search_response.raise_for_status = MagicMock()

        scraper._session.get.return_value = mock_fields_response
        scraper._session.post.return_value = mock_search_response

        results = scraper.search("2026", course_name="国際経済学")
        assert len(results) >= 1
        assert all(isinstance(code, str) for code in results)
        assert all(len(code) >= 8 for code in results)

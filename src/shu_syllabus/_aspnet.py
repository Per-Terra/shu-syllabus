from __future__ import annotations

from typing import TYPE_CHECKING

from bs4 import Tag

from ._utils import make_soup

if TYPE_CHECKING:
    import requests

_HIDDEN_FIELD_KEYS = (
    "__LASTFOCUS",
    "__EVENTTARGET",
    "__EVENTARGUMENT",
    "__VIEWSTATE",
    "__VIEWSTATEGENERATOR",
    "__EVENTVALIDATION",
)


def get_hidden_fields(session: requests.Session, url: str) -> dict[str, str]:
    """ASP.NET の隠しフィールドを取得する。"""
    response = session.get(url)
    response.raise_for_status()
    soup = make_soup(response.text)
    fields: dict[str, str] = {}
    for key in _HIDDEN_FIELD_KEYS:
        tag = soup.find("input", id=key)
        if isinstance(tag, Tag):
            fields[key] = str(tag.get("value", ""))
    return fields

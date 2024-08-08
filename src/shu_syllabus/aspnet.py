import requests
from bs4 import Tag

from .utils import make_soup

ASPNET_HIDDEN_FIELD_KEYS: tuple[str, ...] = (
    "__LASTFOCUS",
    "__EVENTTARGET",
    "__EVENTARGUMENT",
    "__VIEWSTATE",
    "__VIEWSTATEGENERATOR",
    "__EVENTVALIDATION",
)


def get_aspnet_hidden_fields(url: str) -> dict[str, str]:
    """Gets the ASP.NET hidden fields from a webpage.

    This function fetches the content of the specified webpage and parses the
    HTML content to extract the ASP.NET hidden fields. The ASP.NET hidden fields
    are used to maintain the state of the page across postbacks.

    Args:
        url (str): The URL of the webpage to fetch.

    Returns:
        dict[str, str]: A dictionary containing the ASP.NET hidden fields and their values.
    """

    # Get HTML content
    response = requests.get(url)
    response.raise_for_status()
    html = response.text

    # Parse the HTML content
    soup = make_soup(html)

    fields: dict[str, str] = {}

    # Loop through each of the predefined ASP.NET hidden field keys
    for key in ASPNET_HIDDEN_FIELD_KEYS:
        tag = soup.find("input", id=key)  # Find the input element with the specific ID
        if tag and isinstance(tag, Tag):
            # If the element is found and is a valid Tag, get its value
            fields[key] = str(tag.get("value", ""))

    return fields

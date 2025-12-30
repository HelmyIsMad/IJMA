"""HTML scraper entry point for IJMA manuscript submission pages."""
from .extractors import (
    _extract_code,
    _extract_title,
    _extract_receive_date,
    _extract_acceptance_date,
    _extract_authors_emails_and_affiliations,
)
from lxml import html as lxml_html


def scrape_html(html_str: str):
    """Parse IJMA submission HTML and return extracted fields using XPath.

    Returns:
        (code, title, receive_date, acceptance_date, authors, emails, affiliations)
    """
    page = lxml_html.fromstring(html_str)

    code = _extract_code(page)
    title = _extract_title(page)
    receive_date = _extract_receive_date(page)
    acceptance_date = _extract_acceptance_date(page)

    authors, emails, affiliations = _extract_authors_emails_and_affiliations(page)

    return code, title, receive_date, acceptance_date, authors, emails, affiliations

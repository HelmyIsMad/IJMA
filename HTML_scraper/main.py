"""HTML scraper entry point for IJMA manuscript submission pages."""
from .extractors import (
    _extract_code,
    _extract_title,
    _extract_receive_date,
    _extract_acceptance_date,
    _extract_authors_emails_and_affiliations,
)
from bs4 import BeautifulSoup


def scrape_html(html: str):
    """Parse IJMA submission HTML and return extracted fields.

    Returns:
        (code, title, receive_date, acceptance_date, authors, emails, affiliations)
    """
    soup = BeautifulSoup(html, 'html.parser')

    code = _extract_code(soup)
    title = _extract_title(soup)
    receive_date = _extract_receive_date(soup)
    acceptance_date = _extract_acceptance_date(soup)

    authors, emails, affiliations = _extract_authors_emails_and_affiliations(soup)

    return code, title, receive_date, acceptance_date, authors, emails, affiliations

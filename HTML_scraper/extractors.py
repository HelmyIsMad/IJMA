"""Extractors for IJMA submission HTML.

BeautifulSoup doesn't support XPath; we use CSS selectors / tag navigation instead.
"""
from bs4 import BeautifulSoup


def _extract_code(page: BeautifulSoup) -> str:
    """Extract submission code (try multiple fallback strategies)."""
    # Try ID
    el = page.find(id='td_manu_ttl')
    if el:
        # code is often in a sibling or parent table row
        pass
    # Fallback: look for a <span> in the first row of a table
    # (highly dependent on the exact HTML structure)
    # For now, return empty if not found
    return ""


def _extract_title(page: BeautifulSoup) -> str:
    """Extract manuscript title."""
    el = page.find(id='td_manu_ttl')
    if el:
        return (el.get_text(strip=True) or '')
    return ""


def _extract_receive_date(page: BeautifulSoup) -> str:
    """Extract receive date (strip trailing timestamp if present)."""
    # Look for a row label like "Received:" then the next <td><span>
    # Heuristic: find a <td> containing 'Received' text, then get sibling <td>
    rows = page.find_all('tr')
    for row in rows:
        cells = row.find_all('td')
        if len(cells) >= 2:
            label = cells[0].get_text(strip=True).lower()
            if 'received' in label or 'receive' in label:
                val = cells[1].get_text(strip=True)
                # Remove trailing timestamp (e.g., " 12:34:56")
                if len(val) > 9 and val[-9] == ' ' and ':' in val[-8:]:
                    val = val[:-9]
                return val
    return ""


def _extract_acceptance_date(page: BeautifulSoup) -> str:
    """Extract acceptance date."""
    rows = page.find_all('tr')
    for row in rows:
        cells = row.find_all('td')
        if len(cells) >= 2:
            label = cells[0].get_text(strip=True).lower()
            if 'accept' in label or 'accepted' in label:
                val = cells[1].get_text(strip=True)
                return val
    return ""


def _extract_authors_emails_and_affiliations(page: BeautifulSoup):
    """Extract authors, emails, affiliations from a table.

    Expects a table with columns: [Author, Email, ..., ..., ..., Affiliation] (6 columns).
    Returns (authors, emails, affiliations).
    """
    authors = []
    emails = []
    affiliations = []

    # Find all tables and look for one with 6+ columns (author table)
    for table in page.find_all('table'):
        tbody = table.find('tbody')
        if not tbody:
            tbody = table

        rows = tbody.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 6:
                author = (cells[0].get_text(strip=True) or '')
                email = (cells[1].get_text(strip=True) or '')
                affiliation = (cells[5].get_text(strip=True) or '')

                if author:
                    authors.append(author)
                    emails.append(email)
                    affiliations.append(affiliation)

    return authors, emails, affiliations

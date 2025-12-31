"""Extractors for IJMA submission HTML using XPath (lxml)."""
import json
import os
from lxml import html as lxml_html

# Load XPath mappings from xpaths.json
_xpaths = None

def _get_xpaths():
    global _xpaths
    if _xpaths is None:
        json_path = os.path.join(os.path.dirname(__file__), 'xpaths.json')
        with open(json_path, 'r', encoding='utf-8') as f:
            _xpaths = json.load(f)
    return _xpaths


def _extract_code(page) -> str:
    """Extract submission code."""
    xpaths = _get_xpaths()
    xpath = xpaths.get('code', '')
    if xpath:
        elements = page.xpath(xpath)
        if elements:
            return (elements[0].text_content() or '').strip()
    return ""


def _extract_title(page) -> str:
    """Extract manuscript title."""
    xpaths = _get_xpaths()
    xpath = xpaths.get('title', '')
    if xpath:
        elements = page.xpath(xpath)
        if elements:
            return (elements[0].text_content() or '').strip()
    return ""

def _has_running_title_row(page) -> bool:
    """Check if the page has an optional 'running title' row at tr[4]."""
    # Check if row 4 contains "running title" text (case insensitive)
    row4_elements = page.xpath('//table[1]//tr[4]/td[1]')
    if row4_elements:
        text = (row4_elements[0].text_content() or '').strip().lower()
        return 'running' in text and 'title' in text
    return False

def _extract_research_type(page) -> str:
    """Extract research type (adjusts for optional running title row)."""
    xpaths = _get_xpaths()
    base_xpath = xpaths.get('research_type', '')
    if not base_xpath:
        return ""
    
    # If running title exists, research type shifts from tr[4] to tr[5]
    xpath = base_xpath.replace('/tr[4]/', '/tr[5]/') if _has_running_title_row(page) else base_xpath
    
    elements = page.xpath(xpath)
    if elements:
        return (elements[0].text_content() or '').strip()
    return ""

def _extract_receive_date(page) -> str:
    """Extract receive date (strip trailing timestamp, adjusts for optional running title row)."""
    xpaths = _get_xpaths()
    base_xpath = xpaths.get('receive_date', '')
    if not base_xpath:
        return ""
    
    # If running title exists, receive date shifts from tr[8] to tr[9]
    xpath = base_xpath.replace('/tr[8]/', '/tr[9]/') if _has_running_title_row(page) else base_xpath
    
    elements = page.xpath(xpath)
    if elements:
        val = (elements[0].text_content() or '').strip()
        # Remove trailing timestamp (e.g., " 12:34:56")
        if len(val) > 9 and val[-9] == ' ' and ':' in val[-8:]:
            val = val[:-9]
        return val
    return ""

def _extract_acceptance_date(page) -> str:
    """Extract acceptance date (adjusts for optional running title row)."""
    xpaths = _get_xpaths()
    base_xpath = xpaths.get('acceptance_date', '')
    if not base_xpath:
        return ""
    
    # If running title exists, acceptance date shifts from tr[10] to tr[11]
    xpath = base_xpath.replace('/tr[10]/', '/tr[11]/') if _has_running_title_row(page) else base_xpath
    
    elements = page.xpath(xpath)
    if elements:
        return (elements[0].text_content() or '').strip()
    return ""

def _extract_authors_emails_and_affiliations(page):
    """Extract authors, emails, affiliations using XPath from xpaths.json.

    Returns (authors, emails, affiliations).
    """
    authors = []
    emails = []
    affiliations = []

    xpaths = _get_xpaths()
    author_xpath = xpaths.get('authors', '')
    email_xpath = xpaths.get('emails', '')
    affiliation_xpath = xpaths.get('affiliations', '')

    if not (author_xpath and email_xpath and affiliation_xpath):
        return authors, emails, affiliations

    # Extract all matching elements
    author_elements = page.xpath(author_xpath)
    email_elements = page.xpath(email_xpath)
    affiliation_elements = page.xpath(affiliation_xpath)

    # Zip them together (assume same count)
    for author_el, email_el, aff_el in zip(author_elements, email_elements, affiliation_elements):
        author = (author_el.text_content() or '').strip()
        email = (email_el.text_content() or '').strip()
        affiliation = (aff_el.text_content() or '').strip()

        if author:
            authors.append(author)
            emails.append(email)
            affiliations.append(affiliation)

    return authors, emails, affiliations

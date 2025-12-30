"""Extractors for IJMA submission HTML using XPath (lxml)."""
from lxml import html as lxml_html


def _extract_code(page) -> str:
    """Extract submission code."""
    # Try relative XPath first (more flexible)
    xpath_rel = '//fieldset//table//tr[1]/td[2]/span'
    elements = page.xpath(xpath_rel)
    if elements:
        return (elements[0].text_content() or '').strip()
    
    # Fallback: absolute XPath
    xpath_abs = '/html/body/div[4]/div/div[4]/div[7]/fieldset/div/div[2]/div/div[1]/div/table/tbody/tr[1]/td[2]/span'
    elements = page.xpath(xpath_abs)
    if elements:
        return (elements[0].text_content() or '').strip()
    
    return ""


def _extract_title(page) -> str:
    """Extract manuscript title."""
    xpath = '//*[@id="td_manu_ttl"]'
    elements = page.xpath(xpath)
    if elements:
        return (elements[0].text_content() or '').strip()
    return ""

def _extract_research_type(page) -> str:
    """Extract research type."""
    xpath = '/html/body/div[4]/div/div[4]/div[7]/fieldset/div/div[2]/div/div[1]/div/table/tbody/tr[6]/td[2]'
    elements = page.xpath(xpath)
    if elements:
        return (elements[0].text_content() or '').strip()
    return ""


def _extract_receive_date(page) -> str:
    """Extract receive date (strip trailing timestamp if present)."""
    # Try relative: look for row 9 in the first fieldset table
    xpath_rel = '//fieldset//table//tr[9]/td[2]/span'
    elements = page.xpath(xpath_rel)
    if elements:
        val = (elements[0].text_content() or '').strip()
        # Remove trailing timestamp (e.g., " 12:34:56")
        if len(val) > 9 and val[-9] == ' ' and ':' in val[-8:]:
            val = val[:-9]
        return val
    
    # Fallback: absolute
    xpath_abs = '/html/body/div[4]/div/div[4]/div[7]/fieldset/div/div[2]/div/div[1]/div/table/tbody/tr[9]/td[2]/span'
    elements = page.xpath(xpath_abs)
    if elements:
        val = (elements[0].text_content() or '').strip()
        if len(val) > 9 and val[-9] == ' ' and ':' in val[-8:]:
            val = val[:-9]
        return val
    
    return ""


def _extract_research_type(page) -> str:
    """Extract research type (e.g., Original Article, Case Report, etc.)."""
    # Try relative: look for row with "Type" or "Research Type" label
    # Common pattern: a table row where first cell contains label, second contains value
    xpath_rel = '//table//tr'
    rows = page.xpath(xpath_rel)
    for row in rows:
        cells = row.xpath('./td')
        if len(cells) >= 2:
            label = (cells[0].text_content() or '').strip().lower()
            if 'type' in label or 'research type' in label or 'article type' in label:
                return (cells[1].text_content() or '').strip()
    
    # Fallback: try specific row index if known
    # (adjust tr index if you know which row in the IJMA HTML contains research type)
    xpath_abs = '//fieldset//table//tr[3]/td[2]/span'
    elements = page.xpath(xpath_abs)
    if elements:
        return (elements[0].text_content() or '').strip()
    
    return ""


def _extract_acceptance_date(page) -> str:
    """Extract acceptance date."""
    # Try relative
    xpath_rel = '//fieldset//table//tr[11]/td[2]/span'
    elements = page.xpath(xpath_rel)
    if elements:
        return (elements[0].text_content() or '').strip()
    
    # Fallback
    xpath_abs = '/html/body/div[4]/div/div[4]/div[7]/fieldset/div/div[2]/div/div[1]/div/table/tbody/tr[11]/td[2]/span'
    elements = page.xpath(xpath_abs)
    if elements:
        return (elements[0].text_content() or '').strip()
    
    return ""


def _extract_authors_emails_and_affiliations(page):
    """Extract authors, emails, affiliations from a table.

    Returns (authors, emails, affiliations).
    """
    authors = []
    emails = []
    affiliations = []

    # Try relative: find all tables, look for one with 6+ columns per row
    xpath_rel = '//table'
    tables = page.xpath(xpath_rel)
    for table in tables:
        tbody = table.xpath('./tbody')
        if not tbody:
            tbody = [table]
        else:
            tbody = tbody[0:1]
        
        for tb in tbody:
            rows = tb.xpath('./tr')
            for row in rows:
                cells = row.xpath('./td')
                if len(cells) >= 6:
                    author = (cells[0].text_content() or '').strip()
                    email = (cells[1].text_content() or '').strip()
                    affiliation = (cells[5].text_content() or '').strip()

                    if author:
                        authors.append(author)
                        emails.append(email)
                        affiliations.append(affiliation)
    
    if authors:
        return authors, emails, affiliations

    # Fallback: absolute XPath
    xpath_abs = '/html/body/div[4]/div/div[4]/div[7]/fieldset/div/div[2]/div/div[2]/div/div/div/div/table/tbody'
    tbody_elements = page.xpath(xpath_abs)
    if tbody_elements:
        tbody = tbody_elements[0]
        rows = tbody.xpath('./tr')
        for row in rows:
            cells = row.xpath('./td')
            if len(cells) >= 6:
                author = (cells[0].text_content() or '').strip()
                email = (cells[1].text_content() or '').strip()
                affiliation = (cells[5].text_content() or '').strip()

                if author:
                    authors.append(author)
                    emails.append(email)
                    affiliations.append(affiliation)

    return authors, emails, affiliations

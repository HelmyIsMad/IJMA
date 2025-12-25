"""
Content processors for tables, figures, authors, and affiliations.
"""
from typing import List, Dict, Optional
from .formatters import format_title


def process_authors_and_affiliations(authors: List[str], affiliations: List[str]) -> tuple:
    """Process authors and affiliations.

    Rules:
    - If there is only **one unique affiliation**, do **not** number affiliations.
    - Put asterisk/affiliation numbers **after** the author name (not before).
      Examples:
        - Single affiliation: "Alice*; Bob;"
        - Multiple affiliations: "Alice*1; Bob2;"

    Returns:
        (formatted_authors, formatted_affiliations)
        where each is a list of string chunks consumed by the value inserter.
    """
    # Format affiliations
    for i in range(len(affiliations)):
        affiliations[i] = format_title(affiliations[i]) + '.'

    new_authors: List[str] = []
    new_affiliation: List[str] = []

    # Unique affiliations preserving order
    unique_affiliations: List[str] = []
    for aff in affiliations:
        if aff and aff not in unique_affiliations:
            unique_affiliations.append(aff)

    single_unique_affiliation = len(unique_affiliations) <= 1

    # Map affiliation -> number (only used when multiple unique affiliations exist)
    affiliation_map: Dict[str, int] = {}
    next_num = 1

    for i, (author, aff) in enumerate(zip(authors, affiliations)):
        author = (author or '').strip()
        aff = (aff or '').strip()

        suffix = ''

        if single_unique_affiliation:
            # No numbering in affiliation list, only first author gets '*'
            if i == 0:
                suffix = '*'
        else:
            # Assign or reuse number for the affiliation
            if aff in affiliation_map:
                aff_number = affiliation_map[aff]
            else:
                aff_number = next_num
                affiliation_map[aff] = next_num
                new_affiliation.append(str(next_num))
                new_affiliation.append(aff)
                next_num += 1

            # First author: * + number, others: number
            suffix = f"*{aff_number}" if i == 0 else str(aff_number)

        # Author name first, then suffix (if any), then semicolon
        new_authors.append(author)
        if suffix:
            new_authors.append(suffix)
        new_authors.append(';')

    # If single unique affiliation: include the affiliation once, without a leading number
    if single_unique_affiliation and unique_affiliations:
        new_affiliation.append(unique_affiliations[0])

    return new_authors, new_affiliation


def process_tables(tables: List[Dict]) -> List[str]:
    """
    Process tables with descriptions and content.
    
    Args:
        tables: List of table dictionaries with 'info' and 'content'
        
    Returns:
        List of processed table elements
    """
    if not tables:
        return [""]
    
    result = []
    for i, table in enumerate(tables, 1):
        table_info = table.get('info', '').strip()
        table_content = table.get('content', '').strip()
        
        if table_info or table_content:
            # Create table caption combining "Table X:" with info
            if table_info:
                caption = f"Table {i}: {table_info}"
            else:
                caption = f"Table {i}:"
            result.append(caption)
            
            # Add table content (always HTML from paste)
            if table_content:
                result.append(table_content)
            
            result.append("\n\n")
    
    return result if result else [""]


def process_figures(figures: List[Dict]) -> List[str]:
    """
    Process figures with descriptions and content.
    
    Args:
        figures: List of figure dictionaries with 'info' and 'content'
        
    Returns:
        List of processed figure elements
    """
    if not figures:
        return [""]
    
    result = []
    for i, figure in enumerate(figures, 1):
        figure_info = figure.get('info', '').strip()
        figure_content = figure.get('content', '').strip()
        
        if figure_info or figure_content:
            # Add figure caption
            if figure_info:
                result.append(f"Figure {i}: {figure_info}")
            else:
                result.append(f"Figure {i}:")
            
            # Add figure content
            if figure_content:
                # If it's HTML image content, preserve it; otherwise treat as text
                if '<img' in figure_content.lower():
                    result.append(figure_content)
                else:
                    result.append(figure_content)
            
            result.append("\n\n")
    
    return result if result else [""]

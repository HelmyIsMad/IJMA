"""
Content processors for tables, figures, authors, and affiliations.
"""
import re
from typing import List, Dict, Optional
from .formatters import format_title

# Import affiliation normalizer
try:
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from affiliation_processor.affiliation_fixer import normalize_affiliation
except ImportError:
    # Fallback if affiliation_fixer not available
    def normalize_affiliation(raw: str) -> str:
        return raw.strip() + "."


def process_authors_and_affiliations(authors: List[str], affiliations: List[str]) -> tuple:
    """Process authors and affiliations.

    Rules:
    - If there is only **one unique affiliation**, do **not** number affiliations.
    - Put asterisk/affiliation numbers **after** the author name (not before).
    - Sort authors by affiliation number (keeping first author with * at the start).
      Examples:
        - Single affiliation: "Alice*; Bob;"
        - Multiple affiliations: "Alice*1; Bob2;" (sorted by affiliation)
        - Input order: *1, 2, 2, 3, 1, 2 → Output: *1, 1, 2, 2, 2, 3

    Returns:
        (formatted_authors, formatted_affiliations)
        where each is a list of string chunks consumed by the value inserter.
    """

    # transform from "Last, First Middle" to "First Middle Last"
    for i in range(len(authors)):
        if ',' in authors[i]:
            parts = authors[i].split(',')
            # Reverse and strip each part, collapse multiple spaces, then join with space
            # e.g., "Helmy,  Mohamed   mahmoud" -> ["Mohamed mahmoud", "Helmy"] -> "Mohamed Mahmoud Helmy"
            reversed_parts = [re.sub(r'\s+', ' ', p.strip()).title() for p in reversed(parts)]
            authors[i] = " ".join(reversed_parts)
        else:
            # No comma, just collapse spaces and title case
            authors[i] = re.sub(r'\s+', ' ', authors[i].strip()).title()

    # Normalize and format affiliations using affiliation_fixer
    for i in range(len(affiliations)):
        raw_aff = affiliations[i] or ''
        # Normalize using the fixer (already adds trailing period)
        normalized = normalize_affiliation(raw_aff)
        affiliations[i] = normalized

    new_authors: List[str] = []
    new_affiliation: List[str] = []

    # Unique affiliations preserving order of first appearance
    unique_affiliations: List[str] = []
    for aff in affiliations:
        if aff and aff not in unique_affiliations:
            unique_affiliations.append(aff)

    single_unique_affiliation = len(unique_affiliations) <= 1

    # Map affiliation -> number (based on order of first appearance)
    affiliation_map: Dict[str, int] = {}
    next_num = 1
    
    for aff in affiliations:
        aff = (aff or '').strip()
        if aff and aff not in affiliation_map:
            affiliation_map[aff] = next_num
            new_affiliation.append(str(next_num))
            new_affiliation.append(aff)
            next_num += 1

    # Create list of (author, affiliation, affiliation_number, is_first_author)
    author_data = []
    for i, (author, aff) in enumerate(zip(authors, affiliations)):
        author = (author or '').strip()
        aff = (aff or '').strip()
        
        if single_unique_affiliation:
            aff_number = 0  # Not used for sorting when single affiliation
            is_first = i == 0
        else:
            aff_number = affiliation_map.get(aff, 0)
            is_first = i == 0
        
        author_data.append((author, aff, aff_number, is_first))

    # Sort authors: first author stays first, then sort by affiliation number
    if not single_unique_affiliation:
        first_author = author_data[0] if author_data else None
        other_authors = author_data[1:] if len(author_data) > 1 else []
        
        # Sort other authors by affiliation number
        other_authors_sorted = sorted(other_authors, key=lambda x: x[2])
        
        # Reconstruct the list with first author at the start
        if first_author:
            author_data = [first_author] + other_authors_sorted

    # Build the formatted author list
    for i, (author, aff, aff_number, is_first) in enumerate(author_data):
        suffix = ''

        if single_unique_affiliation:
            # No numbering in affiliation list, only first author gets '*'
            if is_first:
                suffix = '*'
        else:
            # First author: * + number, others: number
            suffix = f"*{aff_number}" if is_first else str(aff_number)

        # Author name first, then suffix (if any), then semicolon
        new_authors.append(author)
        if suffix:
            new_authors.append(suffix)
        new_authors.append('; ')

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

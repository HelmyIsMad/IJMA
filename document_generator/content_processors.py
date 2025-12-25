"""
Content processors for tables, figures, authors, and affiliations.
"""
from typing import List, Dict, Optional
from .formatters import format_title


def process_authors_and_affiliations(authors: List[str], affiliations: List[str]) -> tuple:
    """
    Process authors and affiliations, assigning numbers to affiliations.
    
    Args:
        authors: List of author names
        affiliations: List of author affiliations
        
    Returns:
        Tuple of (formatted_authors, formatted_affiliations)
    """
    # Format affiliations
    for i in range(len(affiliations)):
        affiliations[i] = format_title(affiliations[i]) + '.'
    
    index = 1
    new_authors = []
    new_affiliation = []
    affiliation_map = {}  # Track which affiliation gets which number
    
    # First pass: identify unique affiliations
    unique_affiliations = []
    for aff in affiliations:
        if aff not in unique_affiliations:
            unique_affiliations.append(aff)
    
    # Check if all affiliations are the same
    all_same_affiliation = len(unique_affiliations) == 1
    
    for i, aff in enumerate(affiliations):
        # Check if this affiliation already has a number assigned
        if aff in affiliation_map:
            aff_number = affiliation_map[aff]
        else:
            # Assign new number to this affiliation
            aff_number = index
            affiliation_map[aff] = index
            # ALWAYS add affiliation with number (for affiliation list display)
            new_affiliation.append(str(index))
            new_affiliation.append(aff)
            index += 1
        
        # Build the superscript part for AUTHORS
        if all_same_affiliation:
            # Single affiliation: only first author gets asterisk, others get nothing
            if i == 0:
                superscript_part = " * "
            else:
                superscript_part = " "
        else:
            # Multiple affiliations: show numbers for everyone
            if i == 0:
                # First author (corresponding author): asterisk + number
                superscript_part = f" *{aff_number} "
            else:
                # Other authors: just the number
                superscript_part = ' ' + str(aff_number) + ' '
        
        # Add superscript before name, then name, then semicolon
        new_authors.append(superscript_part)
        new_authors.append(f"{authors[i]}")
        new_authors.append(";")

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

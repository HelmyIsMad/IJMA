"""
Main configuration and value filling module.
Simplified version that delegates to specialized formatter and processor modules.
"""
from typing import List, Optional
from .config import VALUES
from .formatters import (
    format_title, format_date, format_abstract, format_keywords,
    format_research_type, format_email, format_authors_short, 
    format_citation, format_content_section
)
from .content_processors import (
    process_authors_and_affiliations, process_tables, process_figures
)

def fill_values(
    title: str,
    research_type: str,
    receive_date: str,
    accept_date: str,
    abstract: str,
    keywords: str,
    authors: List[str],
    affiliation: List[str],
    email: str,
    introduction: str = "",
    aim_of_work: str = "",
    patients_methods: str = "",
    results: str = "",
    tables: Optional[List] = None,
    figures: Optional[List] = None,
    discussion: str = "",
    references: str = ""
) -> None:
    """
    Fill the VALUES dictionary with formatted content for document generation.
    
    Args:
        title: Research paper title
        research_type: Type of research
        receive_date: Date received
        accept_date: Date accepted
        abstract: Abstract text with sections
        keywords: Semicolon-separated keywords
        authors: List of author names
        affiliation: List of author affiliations
        email: Contact email
        introduction: Introduction section content
        aim_of_work: Aim of work section content
        patients_methods: Patients and methods section content
        results: Results section content
        tables: List of table dictionaries
        figures: List of figure dictionaries
        discussion: Discussion section content
        references: References section content
    """
    # Format basic information
    formatted_title = format_title(title)
    # Process authors first (reorders "Last, First" -> "First Last" in-place)
    formatted_authors, formatted_affiliations = process_authors_and_affiliations(authors, affiliation)
    # Now generate short names from the reordered authors
    authors_short = format_authors_short(authors)
    
    # Fill header and metadata
    VALUES["{{research_title}}"][0] = formatted_title
    VALUES["{{header_name}}"][0] = authors_short[0] + ", "
    VALUES["{{research_type}}"][0] = format_research_type(research_type)
    VALUES["{{date_received}}"][0] = format_date(receive_date)
    VALUES["{{date_accepted}}"][0] = format_date(accept_date)
    VALUES["{{email}}"] = format_email(email)
    VALUES["{{citation}}"] = format_citation(formatted_title, authors_short)
    
    # Fill abstract and keywords
    VALUES["{{abstract}}"] = format_abstract(abstract)
    VALUES["{{keywords}}"] = format_keywords(keywords)
    
    # Fill authors and affiliations
    VALUES["{{authors}}"] = formatted_authors
    VALUES["{{affiliation}}"] = formatted_affiliations
    
    # Fill research body content sections
    VALUES["{{intro}}"] = format_content_section(introduction)
    VALUES["{{aim}}"] = format_content_section(aim_of_work)  
    VALUES["{{methods}}"] = format_content_section(patients_methods)
    VALUES["{{results}}"] = format_content_section(results)
    VALUES["{{discussion}}"] = format_content_section(discussion)
    VALUES["{{references}}"] = format_content_section(references)
    
    # Fill tables and figures
    VALUES["{{tables}}"] = process_tables(tables) if tables else [""]
    VALUES["{{figures}}"] = process_figures(figures) if figures else [""]
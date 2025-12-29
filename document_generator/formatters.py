"""
Text formatting utilities for processing user inputs.
Handles title case, date formatting, and text transformations.
"""
from typing import List


# Words that should not be capitalized in titles
DONT_CAPITALIZE = [
    "a", "an", "the", "and", "or", "nor", "but", "for", "so", "yet",
    "as", "at", "by", "in", "of", "on", "to", "up", "via", "with", "without",
    "from", "between", "among", "over", "under", "after", "before", "during",
    "into", "onto", "per", "versus", "vs", "than", "like", "near"
]


def format_title(title: str) -> str:
    """
    Format a title with proper capitalization.
    
    Args:
        title: The title to format
        
    Returns:
        Formatted title with proper capitalization
    """
    parts = title.split(',')
    parts = [part.replace('  ', ' ').replace('.', "").strip() for part in parts]
    new_title = []
    
    for part in parts:
        words = part.split(' ')
        new_part = []
        for word in words:
            if word in DONT_CAPITALIZE:
                new_part.append(word.lower())
            else:
                new_part.append(word.capitalize())
        new_title.append(' '.join(new_part))
    
    return ', '.join(new_title)


def format_date(date: str) -> str:
    """
    Format a date string.
    
    Args:
        date: The date string to format
        
    Returns:
        Formatted date string
    """
    date = date.strip()
    date = '-'.join(date.split('-')[::-1])
    return date


def format_keywords(keywords: str) -> List[str]:
    """
    Format keywords string into a list with proper capitalization.
    
    Args:
        keywords: Semicolon or comma-separated keywords
        
    Returns:
        List with label and formatted keywords
    """
    keywords = keywords.replace(',', '; ').replace("  ", " ")
    keywords = keywords.split("; ")
    
    new_keywords = []
    for keyword in keywords:
        keyword = keyword.split()
        keyword = [word.capitalize() for word in keyword]
        keyword = " ".join(keyword)
        new_keywords.append(keyword)
    
    return ["Keywords: ", "; ".join(new_keywords).replace(".", "") + ";"]


def format_research_type(research_type: str) -> str:
    """
    Format research type with label.
    
    Args:
        research_type: The research type
        
    Returns:
        Formatted research type string
    """
    return f"Main Subject: [{research_type}]"


def format_email(email: str) -> List[str]:
    """
    Format email with label.
    
    Args:
        email: The email address
        
    Returns:
        List with label and email
    """
    return ["Email: ", email]


def format_authors_short(authors: List[str]) -> List[str]:
    """
    Create short author names (Last First-Initial).
    
    Args:
        authors: List of full author names
        
    Returns:
        List of short author names
    """
    short = []
    for author in authors:
        short_author = ""
        names = author.split(" ")
        short_author += names[-1].capitalize() + ' '
        for name in names[:-1]:
            short_author += name[0].upper()
        short.append(short_author)
    return short


def format_citation(title: str, authors_short: List[str]) -> List[str]:
    """
    Create citation string from title and short author names.
    
    Args:
        title: The research title
        authors_short: List of short author names
        
    Returns:
        List with citation label and formatted citation
    """
    citation = ""
    
    for author in authors_short:
        citation += author + ", "
    
    citation = citation[:-2] + ". " + title + ". "
    citation += "IJMA 2025; XX-XX [Article in Press]."
    
    return ["Citation: ", citation]


def format_abstract(abstract: str) -> List[str]:
    """
    Parse abstract into alternating section names and contents.
    
    Args:
        abstract: Multi-line abstract with sections
        
    Returns:
        List alternating between section headers and content
    """
    new_abs = []
    abstract = abstract.replace("\t", "")
    paragraphs = abstract.split("\n")
    
    # Filter out empty paragraphs properly
    paragraphs = [p for p in paragraphs if p.strip()]
    
    for paragraph in paragraphs:
        # Find the colon that separates the section name from content
        if ':' in paragraph:
            colon_index = paragraph.index(':')
            section_name = paragraph[:colon_index + 1]  # Include the colon
            content = paragraph[colon_index + 1:].strip()  # Everything after colon
            
            new_abs.append(section_name)
            new_abs.append(content)
        else:
            # No colon found, treat entire paragraph as section name
            new_abs.append(paragraph)
            new_abs.append("")
    
    return new_abs


def format_content_section(content: str) -> List[str]:
    """
    Process content sections like introduction, methods, etc.
    
    Args:
        content: The content text
        
    Returns:
        List with formatted content paragraphs
    """
    if not content or content.strip() == "":
        return [""]
    
    # Split by paragraphs and clean up
    paragraphs = content.split("\n")
    paragraphs = [p.strip() for p in paragraphs if p.strip()]
    
    if not paragraphs:
        return [""]
    
    # Join paragraphs with proper spacing
    return ["\n\n".join(paragraphs)]

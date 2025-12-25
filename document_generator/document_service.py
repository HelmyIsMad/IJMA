"""
Document generation service.
Provides high-level document generation functionality.
"""
import os
from datetime import datetime
from typing import Optional
from docx import Document
from .config import OUTPUT_FILE, TEMPLATE_FILE, VARIABLES
from .document_processor import process_document
from .edit_config import fill_values


class DocumentGenerationError(Exception):
    """Raised when document generation fails."""
    pass


def generate_document(
    title: str,
    research_type: str,
    receive_date: str,
    accept_date: str,
    abstract: str,
    keywords: str,
    authors: list,
    affiliations: list,
    email: str,
    introduction: str = "",
    aim_of_work: str = "",
    patients_methods: str = "",
    results: str = "",
    tables: Optional[list] = None,
    figures: Optional[list] = None,
    discussion: str = "",
    references: str = "",
    output_path: Optional[str] = None,
) -> str:
    """
    Generate a Word document from the provided data.
    
    Args:
        title: Research paper title
        research_type: Type of research
        receive_date: Date received
        accept_date: Date accepted
        abstract: Abstract text with sections
        keywords: Semicolon-separated keywords
        authors: List of author names
        affiliations: List of author affiliations
        email: Contact email
        introduction: Introduction section content
        aim_of_work: Aim of work section content
        patients_methods: Patients and methods section content
        results: Results section content
        tables: List of table dictionaries
        figures: List of figure dictionaries
        discussion: Discussion section content
        references: References section content
        
    Returns:
        Path to the generated document
        
    Raises:
        DocumentGenerationError: If document generation fails
    """
    try:
        save_path = output_path or OUTPUT_FILE
        # Ensure output directory exists
        output_dir = os.path.dirname(save_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # Fill values in the configuration
        fill_values(
            title=title,
            research_type=research_type,
            receive_date=receive_date,
            accept_date=accept_date,
            abstract=abstract,
            keywords=keywords,
            authors=authors,
            affiliation=affiliations,
            email=email,
            introduction=introduction,
            aim_of_work=aim_of_work,
            patients_methods=patients_methods,
            results=results,
            tables=tables,
            figures=figures,
            discussion=discussion,
            references=references
        )
        
        # Load template and process document
        doc = Document(TEMPLATE_FILE)
        process_document(doc, VARIABLES)
        
        # Save document
        doc.save(save_path)

        return save_path
        
    except Exception as e:
        raise DocumentGenerationError(f"Failed to generate document: {str(e)}") from e


def generate_timestamped_document(
    title: str,
    research_type: str,
    receive_date: str,
    accept_date: str,
    abstract: str,
    keywords: str,
    authors: list,
    affiliations: list,
    email: str,
    introduction: str = "",
    aim_of_work: str = "",
    patients_methods: str = "",
    results: str = "",
    tables: Optional[list] = None,
    figures: Optional[list] = None,
    discussion: str = "",
    references: str = ""
) -> tuple:
    """
    Generate a Word document with a timestamped filename.
    
    Args:
        Same as generate_document()
        
    Returns:
        Tuple of (file_path, filename)
        
    Raises:
        DocumentGenerationError: If document generation fails
    """
    try:
        # Generate the document
        base_path = generate_document(
            title=title,
            research_type=research_type,
            receive_date=receive_date,
            accept_date=accept_date,
            abstract=abstract,
            keywords=keywords,
            authors=authors,
            affiliations=affiliations,
            email=email,
            introduction=introduction,
            aim_of_work=aim_of_work,
            patients_methods=patients_methods,
            results=results,
            tables=tables,
            figures=figures,
            discussion=discussion,
            references=references,
        )
        
        # Create timestamped copy
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'IJMA_document_{timestamp}.docx'
        output_dir = os.path.dirname(OUTPUT_FILE)
        timestamped_path = os.path.join(output_dir, filename)
        
        import shutil
        shutil.copy2(base_path, timestamped_path)
        
        return timestamped_path, filename
        
    except Exception as e:
        raise DocumentGenerationError(f"Failed to generate timestamped document: {str(e)}") from e

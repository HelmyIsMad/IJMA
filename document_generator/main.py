"""Command-line entry point for document generation.

Usage:
    python -m document_generator --title "My paper" --author "A. One" --author "B. Two" --output out.docx
"""
import argparse
import json
import os
import sys
from typing import List, Optional

from .config import OUTPUT_FILE
from .document_service import generate_document


def _parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="document_generator",
        description="Generate an IJMA-formatted .docx manuscript from the command line.",
    )
    parser.add_argument("--title", default="", help="Research paper title (required)")
    parser.add_argument("--research-type", default="", help="Type of research")
    parser.add_argument("--receive-date", default="", help="Date received (DD-MM-YYYY)")
    parser.add_argument("--accept-date", default="", help="Date accepted (DD-MM-YYYY)")
    parser.add_argument("--abstract", default="", help="Abstract text with sections")
    parser.add_argument("--keywords", default="", help="Semicolon-separated keywords")
    parser.add_argument("--author", action="append", default=[], help="Author name (repeatable)")
    parser.add_argument("--affiliation", action="append", default=[], help="Author affiliation (repeatable)")
    parser.add_argument("--email", default="", help="Corresponding author email")
    parser.add_argument("--introduction", default="", help="Introduction section")
    parser.add_argument("--aim-of-work", default="", help="Aim of work section")
    parser.add_argument("--patients-methods", default="", help="Patients and methods section")
    parser.add_argument("--results", default="", help="Results section")
    parser.add_argument("--discussion", default="", help="Discussion section")
    parser.add_argument("--references", default="", help="References section")
    parser.add_argument(
        "--tables-json",
        default=None,
        help='JSON file with a list of {"info": ..., "content": ...} table dicts',
    )
    parser.add_argument(
        "--figures-json",
        default=None,
        help='JSON file with a list of {"info": ..., "content": ...} figure dicts',
    )
    parser.add_argument("--output", default=OUTPUT_FILE, help="Output .docx path")
    return parser.parse_args(argv)


def _load_json_list(path: str) -> Optional[list]:
    if not path:
        return None
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, list) else None


def main(argv: Optional[List[str]] = None) -> int:
    args = _parse_args(argv)

    if not args.title:
        print("Error: --title is required.", file=sys.stderr)
        return 1

    tables = _load_json_list(args.tables_json) if args.tables_json else None
    figures = _load_json_list(args.figures_json) if args.figures_json else None

    save_path = generate_document(
        title=args.title,
        research_type=args.research_type,
        receive_date=args.receive_date,
        accept_date=args.accept_date,
        abstract=args.abstract,
        keywords=args.keywords,
        authors=args.author,
        affiliations=args.affiliation,
        email=args.email,
        introduction=args.introduction,
        aim_of_work=args.aim_of_work,
        patients_methods=args.patients_methods,
        results=args.results,
        tables=tables,
        figures=figures,
        discussion=args.discussion,
        references=args.references,
        output_path=os.path.abspath(args.output),
    )

    print(f"Document saved to: {save_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

from typing import List, Dict

import os

# Get the directory of this config file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

TEMPLATE_FILE: str = os.path.join(BASE_DIR, 'templates', 'template.docx')
OUTPUT_FILE: str = os.path.join(BASE_DIR, 'output', 'output.docx')

VARIABLES: List[str] = [
    "{{header_name}}",
    "{{research_type}}",
    "{{research_title}}",
    "{{authors}}",
    "{{affiliation}}",
    "{{date_received}}",
    "{{date_accepted}}",
    "{{email}}",
    "{{citation}}",
    "{{abstract}}",
    "{{keywords}}",
    "{{intro}}",
    "{{aim}}",
    "{{methods}}",
    "{{results}}",
    "{{tables}}",
    "{{figures}}",
    "{{discussion}}",
    "{{references}}",
]

VALUES: Dict[str, List[str]] = {
    "{{research_title}}": [""],
    "{{header_name}}": ["", "et al."],
    "{{research_type}}": ["Main Subject []"],
    "{{authors}}": [],
    "{{affiliation}}": [],
    "{{date_received}}": [""],
    "{{date_accepted}}": [""],
    "{{email}}": ["Email: ", ""],
    "{{citation}}": ["Citation", ""],
    "{{abstract}}": [],
    "{{keywords}}": ["Keywords: ", ""],
    "{{intro}}": [""],
    "{{aim}}": [""],
    "{{methods}}": [""],
    "{{results}}": [""],
    "{{tables}}": [""],
    "{{figures}}": [""],
    "{{discussion}}": [""],
    "{{references}}": [""],
}
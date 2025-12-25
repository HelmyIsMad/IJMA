from docx import Document
from .config import TEMPLATE_FILE, OUTPUT_FILE, VARIABLES
from .document_processor import process_document
from .edit_config import fill_values

def main() -> None:
    fill_values(
        title="deep learning for image segmentation",
        research_type="AI",
        receive_date="24-08-2025",
        accept_date="28-08-2025",
        abstract=
            """
            Introduction: asjkdfvoauvouaef.
            Aim: azlhjksgvdojaef.
            Patients and Methods: azlhjksgvdojaef.
            Results: azlhjksgvdojaef.
            Discussion: azlhjksgvdojaef.
            References: azlhjksgvdojaef.
            """,
        keywords="Keyword 1; Keyword 2; Keyword 3",
        authors=["Ahmed Gamal Darwish", "Ahmed AL-HABBAA", "Ahmad Mohammad Hassaan"],
        affiliation= [
            "Department of Cardiology, Faculty of Medicine, Al-Azhar University, Cairo, Egypt.",
            "Department of Cardiology, Faculty of Medicine, Al-Azhar University, Cairo, Egypt.",
            "Department of Cardiology, Faculty of Medicine, Al-Azhar University, Damietta, Egypt."
        ],
        email="mohamedlegendary2005@gmail.com"
    )



    doc: Document = Document(TEMPLATE_FILE)
    process_document(doc, VARIABLES)
    doc.save(OUTPUT_FILE)

if __name__ == "__main__":
    main()
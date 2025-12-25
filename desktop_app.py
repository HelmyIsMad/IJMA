import os
from typing import Any, Dict

import webview


class IJMAApi:
    def __init__(self) -> None:
        # Lazily imported where needed to keep startup fast
        pass

    def generate_document_with_save_dialog(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a document using the existing pipeline and save via native dialog.

        Args:
            payload: Dict produced by the HTML UI.

        Returns:
            {"saved_path": "..."} on success
            {"cancelled": True} if user cancels
            {"error": "..."} on failure
        """
        try:
            title = (payload.get('title') or '').strip()
            if not title:
                return {"error": "title is required"}

            # Ask user where to save.
            # NOTE: webview's file dialog returns a list of selected paths or None.
            window = webview.windows[0] if webview.windows else None
            default_name = "IJMA_document.docx"
            save_paths = webview.create_file_dialog(
                webview.SAVE_DIALOG,
                save_filename=default_name,
                file_types=("Word Document (*.docx)",),
                directory='',
                allow_multiple=False,
                window=window,
            )
            if not save_paths:
                return {"cancelled": True}

            save_path = save_paths[0]
            if not save_path.lower().endswith('.docx'):
                save_path += '.docx'

            # Normalize payload fields
            authors = payload.get('authors') or []
            affiliations = payload.get('affiliations') or []
            email = (payload.get('email') or '').strip()

            # Fallback: if no corresponding email provided, try to set empty (pipeline accepts)
            from document_generator.document_service import generate_document

            generated_path = generate_document(
                title=title,
                research_type=(payload.get('research_type') or '').strip(),
                receive_date=(payload.get('receive_date') or '').strip(),
                accept_date=(payload.get('accept_date') or '').strip(),
                abstract=(payload.get('abstract') or '').strip(),
                keywords=(payload.get('keywords') or '').strip(),
                authors=authors,
                affiliations=affiliations,
                email=email,
                introduction=(payload.get('introduction') or '').strip(),
                aim_of_work=(payload.get('aim_of_work') or '').strip(),
                patients_methods=(payload.get('patients_methods') or '').strip(),
                results=(payload.get('results') or '').strip(),
                tables=payload.get('tables') or None,
                figures=payload.get('figures') or None,
                discussion=(payload.get('discussion') or '').strip(),
                references=(payload.get('references') or '').strip(),
                output_path=save_path,
            )

            return {"saved_path": os.path.abspath(generated_path)}
        except Exception as e:
            return {"error": str(e)}


def main() -> None:
    ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'desktop_ui', 'index.html')
    api = IJMAApi()

    window = webview.create_window(
        'IJMA Document Generator',
        f'file://{ui_path}',
        js_api=api,
        width=1200,
        height=900,
    )
    webview.start(debug=True)


if __name__ == '__main__':
    main()

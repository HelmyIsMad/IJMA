import os
import platform
import subprocess
from typing import Any, Dict

import webview


def _open_file_with_default_app(path: str) -> None:
    """Open a file with the OS default application (best-effort)."""
    try:
        system = platform.system()
        if system == 'Windows':
            os.startfile(path)  # type: ignore[attr-defined]
        elif system == 'Darwin':
            subprocess.run(['open', path], check=False)
        else:
            subprocess.run(['xdg-open', path], check=False)
    except Exception:
        # Best-effort: do not fail document generation if opening fails.
        pass


class IJMAApi:
    def __init__(self) -> None:
        # Lazily imported where needed to keep startup fast
        pass

    def scrape_html_paste(self, html_text: str) -> Dict[str, Any]:
        """Scrape IJMA submission HTML and return extracted fields.

        Returns:
            {
                "code": str,
                "title": str,
                "receive_date": str,
                "accept_date": str,
                "authors": [str, ...],
                "emails": [str, ...],
                "affiliations": [str, ...]
            }
            or {"error": "..."}
        """
        try:
            from HTML_scraper import scrape_html

            code, title, research_type, receive_date, accept_date, authors, emails, affiliations = scrape_html(html_text)
            return {
                "code": code or "",
                "title": title or "",
                "research_type": research_type or "",
                "receive_date": receive_date or "",
                "accept_date": accept_date or "",
                "authors": authors or [],
                "emails": emails or [],
                "affiliations": affiliations or [],
            }
        except Exception as e:
            return {"error": str(e)}

    def file_url_to_data_url(self, file_url: str) -> Dict[str, Any]:
        """Convert a file:// URL (or plain path) into a data: URL (base64).

        This is used because the embedded browser may not be able to fetch file:// URLs directly,
        but the python docx pipeline expects <img src="data:image/...;base64,...">.
        """
        try:
            import base64
            import mimetypes
            from urllib.parse import urlparse, unquote

            raw = (file_url or '').strip()
            if not raw:
                return {"error": "empty file_url"}

            path = raw
            if raw.startswith('file:'):
                parsed = urlparse(raw)
                path = unquote(parsed.path or '')
                # On Windows, urlparse('file:///C:/x') -> path '/C:/x'
                if platform.system() == 'Windows' and path.startswith('/') and len(path) >= 3 and path[2] == ':':
                    path = path[1:]

            path = os.path.abspath(path)
            if not os.path.exists(path):
                return {"error": f"file not found: {path}"}

            mime, _ = mimetypes.guess_type(path)
            if not mime:
                mime = 'application/octet-stream'

            with open(path, 'rb') as f:
                b64 = base64.b64encode(f.read()).decode('ascii')

            return {"data_url": f"data:{mime};base64,{b64}"}
        except Exception as e:
            return {"error": str(e)}

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

            # Use manuscript code as filename if provided, else generic name
            manuscript_code = (payload.get('manuscript_code') or '').strip()
            if manuscript_code:
                # Sanitize code for filename (remove invalid chars)
                import re
                safe_code = re.sub(r'[<>:"/\\|?*]', '_', manuscript_code)
                default_name = f"{safe_code}.docx"
            else:
                default_name = "IJMA_document.docx"

            # Ask user where to save.
            # NOTE: webview's file dialog returns a list of selected paths or None.
            window = webview.windows[0] if webview.windows else None
            if window is None:
                return {"error": "No active window for file dialog"}

            save_paths = window.create_file_dialog(
                webview.FileDialog.SAVE,
                save_filename=default_name,
                file_types=("Word Document (*.docx)",),
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

            abs_path = os.path.abspath(generated_path)
            _open_file_with_default_app(abs_path)

            return {"saved_path": abs_path}
        except Exception as e:
            import traceback
            traceback.print_exc()
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

# IJMA Document Generator

Generate IJMA-formatted `.docx` manuscripts from a desktop UI (HTML/JS) **without any Flask/API server**.

This repo contains:
- A **desktop app** built with **[pywebview](https://pywebview.flowrl.com/)** that loads a local HTML form and calls Python directly via the JS bridge (no HTTP).
- A Python **document generation pipeline** (`document_generator/`) that fills a Word template and produces a final `.docx`.

## Features

- Desktop UI (Bootstrap form) for entering manuscript metadata and sections
- Paste tables and figures from Word (tables/images preserved as HTML where possible)
- One-click document generation
- Native **Save As** dialog
- Automatically opens the saved `.docx`

## Quick start

### 1) Install dependencies

```bash
pip install pywebview python-docx
```

### 2) Run the desktop app

```bash
python desktop_app.py
```

Fill the form and click **Generate Document**.

## How it works (high level)

### Desktop layer (no API)

- **UI:** `desktop_ui/index.html`
- **Launcher:** `desktop_app.py`

The UI builds a JSON payload and calls:

```js
window.pywebview.api.generate_document_with_save_dialog(payload)
```

That Python method:
1. Shows a native Save dialog
2. Runs the existing document pipeline
3. Saves the `.docx`
4. Opens the saved file

### Document generation pipeline

The main entry point is:

- `document_generator/document_service.py`
  - `generate_document(..., output_path=...)`

Internally it:
1. Fills placeholders via `document_generator/edit_config.py` (`fill_values`)
2. Loads the template `document_generator/templates/template.docx`
3. Replaces placeholders using `document_generator/document_processor.py`
4. Handles special content:
   - tables: `document_generator/table_processor.py`
   - figures/images: `document_generator/figure_processor.py`

## Template placeholders

The template uses placeholders like:

- `{{research_title}}`, `{{authors}}`, `{{affiliation}}`
- `{{abstract}}`, `{{intro}}`, `{{methods}}`, `{{results}}`
- `{{tables}}`, `{{figures}}`, `{{discussion}}`, `{{references}}`

See `document_generator/config.py` for the full list.

## Notes

- This project is designed to run **locally**. There is no Flask/FastAPI backend.
- If you want to distribute it, you can package it into an executable (e.g., PyInstaller).

## License

Add a license if/when you’re ready.

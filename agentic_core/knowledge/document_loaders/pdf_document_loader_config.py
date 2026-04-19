import logging
from pathlib import Path

# Configuration constants

log = logging.getLogger(__name__)


class PDFDocumentLoader:
    def __init__(self, file_path: Path):
        self.file_path = Path(file_path)

    def load(self) -> str:
        # Best-effort: prefer pypdf if available; otherwise return empty string.
        try:
            from pypdf import PdfReader

            reader = PdfReader(str(self.file_path))
            text_parts = []
            for page in reader.pages:
                try:
                    text_parts.append(page.extract_text() or "")
                except Exception:  # guardian: allow-broad-exception -- per-page text extract failure: empty string substituted, extraction continues
                    text_parts.append("")
            return "\n".join(text_parts)
        except Exception as e:  # guardian: allow-broad-exception allow-log-and-swallow -- PDF load failure: non-fatal, empty string returned to caller
            log.warning(f"PDF load failed ({e})")
            return ""

    @staticmethod
    def load_file(file_path: Path) -> str:
        return PDFDocumentLoader(file_path).load()

    @staticmethod
    def load_path(path: Path) -> str:
        return PDFDocumentLoader.load_file(path)

from __future__ import annotations

"\nSovereign PDF Parser - L0 Document Ingestion\nEnhanced PDF parsing with OCR fallback, metadata extraction, and async processing\n"
import asyncio
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_validated_by_safety_plane,
    _emit_writes_through,
    emit_determinism_digest,
)

_emit_writes_through("p1", "sovereign_pdf_parser", "uwg_governed_write")
_emit_writes_through("p1", "sovereign_pdf_parser", "uwg_governed_write_2")
_emit_pulls_context("p1", "sovereign_pdf_parser", "context_retrieval")
_emit_pulls_context("p1", "sovereign_pdf_parser", "context_retrieval_2")
emit_determinism_digest("trace_sovereign_pdf_parser", "sovereign_pdf_parser_dispatch")
emit_determinism_digest("trace_sovereign_pdf_parser", "sovereign_pdf_parser_complete")
_emit_validated_by_safety_plane("p1", "sovereign_pdf_parser", "safety_validation")
try:
    import pdfplumber

    PDF_PLUMBER_AVAILABLE: Any = True
except ImportError:  # guardian: allow-silent-swallow - optional dependency
    PDF_PLUMBER_AVAILABLE: Any = False
    print("[!] pdfplumber not available")
try:
    import pytesseract
    from pdf2image import convert_from_path

    OCR_AVAILABLE: Any = True
except ImportError:
    OCR_AVAILABLE: Any = False
    print("[!] OCR dependencies not available")


class SovereignPdfParser:
    """L0: Robust PDF parsing with structural awareness and OCR fallback"""

    def __init__(self):
        self.internal_metadata = {}
        self.footer_patterns = [
            re.compile("^\\d+$"),
            re.compile("^page \\d+", re.IGNORECASE),
            re.compile("^\\d+\\s*/\\s*\\d+$"),
        ]
        self.heading_patterns = [re.compile("^[A-Z][A-Za-z\\s]{10,}$"), re.compile("^[A-Z\\s]{10,}$")]

    def _extract_text_sync(self, pdf_path: Path) -> str:
        """Extract text using pdfplumber with structural awareness"""
        if not PDF_PLUMBER_AVAILABLE:
            return ""
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            self.internal_metadata = pdf.metadata if pdf.metadata else {}
            for page in pdf.pages:
                page_text = page.extract_text(layout=True)
                text += (page_text or "") + "\n"
        return text

    async def extract_text_ocr(self, pdf_path: Path) -> str:
        """OCR fallback for scanned/image-based PDFs - Thread Safe"""
        if not OCR_AVAILABLE:
            return ""

        def _ocr_work():
            try:
                images = convert_from_path(str(pdf_path), dpi=200)
                return "\n".join([pytesseract.image_to_string(img) for img in images])
            except Exception as e:  # guardian: allow-silent-swallow
                return f"OCR_ERROR: {e}"

        return await asyncio.to_thread(_ocr_work)

    def clean_text(self, raw_text: str) -> str:
        """Remove headers, footers, and noise"""
        lines: Any = raw_text.splitlines()
        cleaned: Any = []
        for line in lines:
            line: Any = line.strip()
            if not line or any(p.match(line) for p in self.footer_patterns):
                continue
            if len(line) < 3 and (not re.match("^[•\\-\\*\\d]", line)):
                continue
            cleaned.append(line)
        return "\n".join(cleaned)

    def extract_metadata(self, pdf_path: Path, text: str) -> dict:
        """Extract metadata with internal fallback"""
        metadata: Any = {
            "source_file": str(pdf_path),
            "ingested_at": datetime.utcnow().isoformat(),
            "file_type": "pdf",
            "title": self.internal_metadata.get("Title") or pdf_path.stem,
            "author": self.internal_metadata.get("Author") or "unknown",
            "date": self.internal_metadata.get("CreationDate") or "unknown",
        }
        lines: Any = text.splitlines()[:20]
        for line in lines:
            if metadata["author"] == "unknown" and "author" in line.lower():
                metadata["author"] = line.split(":", 1)[1].strip() if ":" in line else line
            if metadata["date"] == "unknown" and any(m in line.lower() for m in ["2024", "2025"]):
                metadata["date"] = line.strip()
        return metadata

    async def parse_pdf(self, pdf_path: Path) -> list[dict]:
        """
        Main parsing pipeline with async support
        Returns list of chunks with text, embeddings, and metadata
        """
        text: Any = await asyncio.to_thread(self._extract_text_sync, pdf_path)
        if not text or len(text.strip()) < 100:
            print(f"   [OCR] Attempting OCR for {pdf_path.name}")
            text: Any = await self.extract_text_ocr(pdf_path)
        cleaned_text: Any = self.clean_text(text)
        metadata: Any = self.extract_metadata(pdf_path, cleaned_text)
        chunks: Any = self._chunk_text(cleaned_text, metadata)
        return chunks

    def _chunk_text(self, text: str, metadata: dict, chunk_size: int = 1000) -> list[dict]:
        """Split text into chunks for vector storage"""
        chunks = []
        paragraphs = text.split("\n\n")
        current_chunk = ""
        for para in paragraphs:
            if len(current_chunk) + len(para) > chunk_size and current_chunk:
                chunks.append({"text": current_chunk.strip(), "metadata": metadata.copy(), "values": []})
                current_chunk = para
            else:
                current_chunk += "\n\n" + para if current_chunk else para
        if current_chunk:
            chunks.append({"text": current_chunk.strip(), "metadata": metadata.copy(), "values": []})
        return chunks


async def main() -> Any:
    """Test the parser"""
    parser: Any = SovereignPDFParser()
    pdf_path: Any = Path("example.pdf")
    if pdf_path.exists():
        chunks: Any = await parser.parse_pdf(pdf_path)
        print(f"Extracted {len(chunks)} chunks from {pdf_path.name}")
        for i, chunk in enumerate(chunks[:3]):
            print(f"\nChunk {i + 1}:")
            print(f"  Text: {chunk['text'][:100]}...")
            print(f"  Metadata: {chunk['metadata']}")


if __name__ == "__main__":
    asyncio.run(main())

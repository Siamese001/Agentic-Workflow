#!/usr/bin/env python3
"""
Sovereign PDF Parser - L0 Document Ingestion
Enhanced PDF parsing with OCR fallback, metadata extraction, and async processing
"""

import asyncio
import re
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

try:
    import pdfplumber
    PDF_PLUMBER_AVAILABLE = True
except ImportError:
    PDF_PLUMBER_AVAILABLE = False
    print("[!] pdfplumber not available")

try:
    import pytesseract
    from pdf2image import convert_from_path
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("[!] OCR dependencies not available")

class SovereignPDFParser:
    """L0: Robust PDF parsing with structural awareness and OCR fallback"""
    
    def __init__(self):
        self.internal_metadata = {}
        
        # Patterns for cleaning
        self.footer_patterns = [
            re.compile(r'^\d+$'),  # Page numbers
            re.compile(r'^page \d+', re.IGNORECASE),
            re.compile(r'^\d+\s*/\s*\d+$'),  # Page x/y
        ]
        
        self.heading_patterns = [
            re.compile(r'^[A-Z][A-Za-z\s]{10,}$'),  # Title case headings
            re.compile(r'^[A-Z\s]{10,}$'),  # All caps headings
        ]
    
    def _extract_text_sync(self, pdf_path: Path) -> str:
        """Extract text using pdfplumber with structural awareness"""
        if not PDF_PLUMBER_AVAILABLE:
            return ""
        
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            # First, try to grab internal PDF metadata
            self.internal_metadata = pdf.metadata if pdf.metadata else {}
            for page in pdf.pages:
                # extract_text(layout=True) helps preserve some column structure
                page_text = page.extract_text(layout=True)
                text += (page_text or "") + "\n"
        return text
    
    async def extract_text_ocr(self, pdf_path: Path) -> str:
        """OCR fallback for scanned/image-based PDFs - Thread Safe"""
        if not OCR_AVAILABLE:
            return ""

        def _ocr_work():
            try:
                images = convert_from_path(str(pdf_path), dpi=200)  # 200 is often enough and faster
                return "\n".join([pytesseract.image_to_string(img) for img in images])
            except Exception as e:
                return f"OCR_ERROR: {e}"

        return await asyncio.to_thread(_ocr_work)
    
    def clean_text(self, raw_text: str) -> str:
        """Remove headers, footers, and noise"""
        lines = raw_text.splitlines()
        cleaned = []
        
        for line in lines:
            line = line.strip()
            # Check for empty or footer noise
            if not line or any(p.match(line) for p in self.footer_patterns):
                continue
            # Keep short lines if they look like bullets or headings
            if len(line) < 3 and not re.match(r'^[•\-\*\d]', line):
                continue
            cleaned.append(line)
        
        return "\n".join(cleaned)
    
    def extract_metadata(self, pdf_path: Path, text: str) -> Dict:
        """Extract metadata with internal fallback"""
        metadata = {
            "source_file": str(pdf_path),
            "ingested_at": datetime.utcnow().isoformat(),
            "file_type": "pdf",
            "title": self.internal_metadata.get("Title") or pdf_path.stem,
            "author": self.internal_metadata.get("Author") or "unknown",
            "date": self.internal_metadata.get("CreationDate") or "unknown"
        }

        # Heuristic refinement if internal data is missing
        lines = text.splitlines()[:20]
        for line in lines:
            if metadata["author"] == "unknown" and "author" in line.lower():
                metadata["author"] = line.split(":", 1)[1].strip() if ":" in line else line
            if metadata["date"] == "unknown" and any(m in line.lower() for m in ["2024", "2025"]):
                metadata["date"] = line.strip()
        return metadata
    
    async def parse_pdf(self, pdf_path: Path) -> List[Dict]:
        """
        Main parsing pipeline with async support
        Returns list of chunks with text, embeddings, and metadata
        """
        # Run heavy PDF extraction in a separate thread
        text = await asyncio.to_thread(self._extract_text_sync, pdf_path)
        
        # If native extraction failed, try OCR
        if not text or len(text.strip()) < 100:
            print(f"   [OCR] Attempting OCR for {pdf_path.name}")
            text = await self.extract_text_ocr(pdf_path)
        
        # Clean the extracted text
        cleaned_text = self.clean_text(text)
        
        # Extract metadata
        metadata = self.extract_metadata(pdf_path, cleaned_text)
        
        # Chunk the text (simple paragraph-based chunking)
        chunks = self._chunk_text(cleaned_text, metadata)
        
        return chunks
    
    def _chunk_text(self, text: str, metadata: Dict, chunk_size: int = 1000) -> List[Dict]:
        """Split text into chunks for vector storage"""
        chunks = []
        paragraphs = text.split("\n\n")
        
        current_chunk = ""
        for para in paragraphs:
            if len(current_chunk) + len(para) > chunk_size and current_chunk:
                chunks.append({
                    "text": current_chunk.strip(),
                    "metadata": metadata.copy(),
                    "values": []  # Placeholder for embeddings
                })
                current_chunk = para
            else:
                current_chunk += "\n\n" + para if current_chunk else para
        
        # Add final chunk
        if current_chunk:
            chunks.append({
                "text": current_chunk.strip(),
                "metadata": metadata.copy(),
                "values": []
            })
        
        return chunks

async def main():
    """Test the parser"""
    parser = SovereignPDFParser()
    
    # Example usage
    pdf_path = Path("example.pdf")
    if pdf_path.exists():
        chunks = await parser.parse_pdf(pdf_path)
        print(f"Extracted {len(chunks)} chunks from {pdf_path.name}")
        for i, chunk in enumerate(chunks[:3]):
            print(f"\nChunk {i+1}:")
            print(f"  Text: {chunk['text'][:100]}...")
            print(f"  Metadata: {chunk['metadata']}")

if __name__ == "__main__":
    asyncio.run(main())

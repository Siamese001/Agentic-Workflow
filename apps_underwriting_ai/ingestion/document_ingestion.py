"""
Document Ingestion - Registers and hashes underwriting documents.
"""

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..types import DocumentPackage, DocumentRef
from tqdm import tqdm


@dataclass
class DocumentManifest:
    """Manifest of ingested documents."""

    documents: List[DocumentRef] = field(default_factory=list)
    total_count: int = 0
    by_type: Dict[str, int] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)


class DocumentIngestion:
    """
    Registers documents, computes hashes, builds manifests.

    Responsibilities:
    - Assign doc_id
    - Compute content hash
    - Preserve source_uri
    - Build document manifest
    """

    def __init__(self):
        self._doc_counter = 0

    def ingest_document(
        self,
        file_path: Path,
        doc_type: str,
        extract_text: bool = False,
    ) -> DocumentRef:
        """
        Ingest a single document.

        Args:
            file_path: Path to document
            doc_type: Document type classification
            extract_text: Whether to attempt text extraction

        Returns:
            DocumentRef with metadata
        """
        self._doc_counter += 1

        # Compute hash
        content_hash = self._compute_file_hash(file_path)

        # Generate doc_id
        doc_id = f"DOC-{datetime.now().strftime('%Y%m%d')}-{self._doc_counter:04d}"

        # Attempt text extraction if requested
        extracted_text_available = False
        parsed_fields = {}

        if extract_text:
            try:
                parsed_fields = self._extract_document_fields(file_path, doc_type)
                extracted_text_available = bool(parsed_fields)
            except (OSError, UnicodeDecodeError, ValueError, TypeError, KeyError):
                pass

        return DocumentRef(
            doc_id=doc_id,
            doc_type=doc_type,
            source_uri=str(file_path),
            hash=content_hash,
            extracted_text_available=extracted_text_available,
            parsed_structured_fields=parsed_fields,
            document_flags=[],
        )

    def ingest_batch(
        self,
        doc_paths: List[Path],
        doc_type_map: Optional[Dict[str, str]] = None,
    ) -> DocumentManifest:
        """
        Ingest a batch of documents.

        Args:
            doc_paths: List of document paths
            doc_type_map: Optional mapping of filename patterns to doc types

        Returns:
            DocumentManifest
        """
        manifest = DocumentManifest()

        for path in tqdm(doc_paths, desc="Processing", unit="item"):
            try:
                # Determine doc type
                doc_type = self._infer_doc_type(path, doc_type_map)

                # Ingest
                doc_ref = self.ingest_document(path, doc_type)
                manifest.documents.append(doc_ref)

                # Update counts
                manifest.by_type[doc_type] = manifest.by_type.get(doc_type, 0) + 1

            except (OSError, UnicodeDecodeError, ValueError, TypeError, KeyError) as e:
                manifest.errors.append(f"Failed to ingest {path}: {str(e)}")

        manifest.total_count = len(manifest.documents)
        return manifest

    def build_document_package(
        self,
        manifest: DocumentManifest,
    ) -> DocumentPackage:
        """Build DocumentPackage from manifest."""
        package = DocumentPackage()

        for doc in tqdm(manifest.documents, desc="Processing", unit="item"):
            # Categorize by doc_type
            if doc.doc_type in ["financial_statement", "financials"]:
                package.financial_statements.append(doc)
            elif doc.doc_type in ["tax_return", "tax_returns"]:
                package.tax_returns.append(doc)
            elif doc.doc_type in ["bank_statement", "bank_statements"]:
                package.bank_statements.append(doc)
            elif doc.doc_type == "ar_aging":
                package.ar_aging.append(doc)
            elif doc.doc_type == "ap_aging":
                package.ap_aging.append(doc)
            elif doc.doc_type in ["debt_schedule", "debt_schedules"]:
                package.debt_schedule.append(doc)
            elif doc.doc_type in ["entity_doc", "entity_docs", "formation"]:
                package.entity_docs.append(doc)
            elif doc.doc_type in ["insurance", "insurance_certificate"]:
                package.insurance_certificates.append(doc)
            elif doc.doc_type in ["appraisal", "appraisals"]:
                package.appraisals.append(doc)
            elif doc.doc_type in ["management_comment", "management_comments"]:
                package.management_comments.append(doc)

        return package

    def _compute_file_hash(self, path: Path) -> str:
        """Compute SHA256 hash of file."""
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()[:32]

    def _infer_doc_type(self, path: Path, doc_type_map: Optional[Dict[str, str]]) -> str:
        """Infer document type from filename or mapping."""
        filename = path.name.lower()

        # Check explicit mapping
        if doc_type_map:
            for pattern, doc_type in doc_type_map.items():
                if pattern.lower() in filename:
                    return doc_type

        # Infer from filename
        if "financial" in filename or "fs" in filename:
            return "financial_statement"
        elif "tax" in filename:
            return "tax_return"
        elif "bank" in filename:
            return "bank_statement"
        elif "ar" in filename and "aging" in filename:
            return "ar_aging"
        elif "ap" in filename and "aging" in filename:
            return "ap_aging"
        elif "debt" in filename and "schedule" in filename:
            return "debt_schedule"
        elif "appraisal" in filename:
            return "appraisal"
        elif "insurance" in filename:
            return "insurance"
        elif "entity" in filename or "operating" in filename or "articles" in filename:
            return "entity_doc"
        elif "management" in filename or "comments" in filename:
            return "management_comment"

        return "unknown"

    def _extract_document_fields(
        self,
        path: Path,
        doc_type: str,
    ) -> Dict[str, Any]:
        """Extract structured fields from document."""
        # This is a placeholder for actual document parsing
        # In production, would integrate with document parsing services
        return {}

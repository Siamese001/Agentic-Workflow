"""
Document Manifest Builder - Builds and manages document manifests.
"""
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from ..types import DocumentPackage, DocumentRef


@dataclass
class ManifestEntry:
    """Single entry in document manifest."""
    doc_id: str
    doc_type: str
    file_name: str
    file_path: str
    hash: str
    upload_timestamp: str
    extracted_fields: Dict[str, Any] = field(default_factory=dict)
    flags: List[str] = field(default_factory=list)


class DocumentManifestBuilder:
    """
    Builds and validates document manifests for underwriting packages.

    Tracks:
    - Required vs actual documents
    - Document freshness
    - Completeness scoring
    """

    def __init__(self):
        self.entries: List[ManifestEntry] = []
        self.required_docs: Dict[str, bool] = {}

    def add_entry(self, doc_ref: DocumentRef, file_path: Path) -> ManifestEntry:
        """Add a document to the manifest."""
        entry = ManifestEntry(
            doc_id=doc_ref.doc_id,
            doc_type=doc_ref.doc_type,
            file_name=file_path.name,
            file_path=str(file_path),
            hash=doc_ref.hash,
            upload_timestamp=datetime.now().isoformat(),
            extracted_fields=doc_ref.parsed_structured_fields,
            flags=doc_ref.document_flags,
        )
        self.entries.append(entry)
        return entry

    def set_required_docs(self, required: Dict[str, bool]) -> None:
        """Set required document types."""
        self.required_docs = required

    def check_completeness(self) -> Dict[str, Any]:
        """Check document completeness against requirements."""
        present_types = set(e.doc_type for e in self.entries)
        required_types = set(self.required_docs.keys())

        missing = required_types - present_types
        present = required_types & present_types

        completeness_pct = len(present) / len(required_types) if required_types else 1.0

        return {
            "complete": len(missing) == 0,
            "completeness_pct": completeness_pct,
            "required_count": len(required_types),
            "present_count": len(present),
            "missing_types": list(missing),
            "present_types": list(present),
        }

    def get_by_type(self, doc_type: str) -> List[ManifestEntry]:
        """Get all entries of a specific type."""
        return [e for e in self.entries if e.doc_type == doc_type]

    def to_document_package(self) -> DocumentPackage:
        """Convert manifest to DocumentPackage."""
        package = DocumentPackage()

        for entry in self.entries:
            doc_ref = DocumentRef(
                doc_id=entry.doc_id,
                doc_type=entry.doc_type,
                source_uri=entry.file_path,
                hash=entry.hash,
                extracted_text_available=bool(entry.extracted_fields),
                parsed_structured_fields=entry.extracted_fields,
                document_flags=entry.flags,
            )

            # Add to appropriate category
            if entry.doc_type == 'financial_statement':
                package.financial_statements.append(doc_ref)
            elif entry.doc_type == 'tax_return':
                package.tax_returns.append(doc_ref)
            elif entry.doc_type == 'bank_statement':
                package.bank_statements.append(doc_ref)
            elif entry.doc_type == 'ar_aging':
                package.ar_aging.append(doc_ref)
            elif entry.doc_type == 'ap_aging':
                package.ap_aging.append(doc_ref)
            elif entry.doc_type == 'debt_schedule':
                package.debt_schedule.append(doc_ref)
            elif entry.doc_type == 'entity_doc':
                package.entity_docs.append(doc_ref)
            elif entry.doc_type == 'insurance':
                package.insurance_certificates.append(doc_ref)
            elif entry.doc_type == 'appraisal':
                package.appraisals.append(doc_ref)
            elif entry.doc_type == 'management_comment':
                package.management_comments.append(doc_ref)

        return package

    def to_dict(self) -> Dict[str, Any]:
        """Serialize manifest to dict."""
        return {
            "entries": [
                {
                    "doc_id": e.doc_id,
                    "doc_type": e.doc_type,
                    "file_name": e.file_name,
                    "file_path": e.file_path,
                    "hash": e.hash,
                    "upload_timestamp": e.upload_timestamp,
                    "extracted_fields": e.extracted_fields,
                    "flags": e.flags,
                }
                for e in self.entries
            ],
            "required_docs": self.required_docs,
            "completeness_check": self.check_completeness(),
        }

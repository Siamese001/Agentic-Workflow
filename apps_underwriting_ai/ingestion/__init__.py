"""
Ingestion module for apps_underwriting_ai.
"""

from .intake_router import IntakeRouter, IngestionResult
from .structured_ingestion import StructuredIngestion, IngestionMode
from .document_ingestion import DocumentIngestion, DocumentManifest
from .json_mapper import JSONMapper
from .csv_mapper import CSVMapper
from .xlsx_mapper import XLSXMapper
from .document_manifest_builder import DocumentManifestBuilder

__all__ = [
    "IntakeRouter",
    "IngestionResult",
    "StructuredIngestion",
    "IngestionMode",
    "DocumentIngestion",
    "DocumentManifest",
    "JSONMapper",
    "CSVMapper",
    "XLSXMapper",
    "DocumentManifestBuilder",
]

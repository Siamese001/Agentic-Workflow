"""
Intake Router - Routes incoming underwriting requests to appropriate ingestion pipeline.
"""

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Union

from ..types import UnderwritingRequest
from .csv_mapper import CSVMapper
from .document_ingestion import DocumentIngestion
from .json_mapper import JSONMapper
from .xlsx_mapper import XLSXMapper


@dataclass
class IngestionResult:
    """Result of ingestion operation."""

    success: bool
    request: Optional[UnderwritingRequest] = None
    warnings: list = field(default_factory=list)
    errors: list = field(default_factory=list)
    provenance: Dict[str, Any] = field(default_factory=dict)


class IntakeRouter:
    """
    Routes incoming requests to appropriate ingestion pipeline.

    Supports:
    - JSON API payloads
    - CSV extracts
    - XLSX templates
    - Manual dict assembly
    """

    def __init__(self):
        self.json_mapper = JSONMapper()
        self.csv_mapper = CSVMapper()
        self.xlsx_mapper = XLSXMapper()
        self.doc_ingestion = DocumentIngestion()

    def ingest_json(
        self,
        data: Union[str, Dict[str, Any], Path],
        request_id: Optional[str] = None,
        strict_mode: bool = False,
    ) -> IngestionResult:
        """
        Ingest from JSON string, dict, or file path.

        Args:
            data: JSON string, dict, or Path to JSON file
            request_id: Optional request ID (generated if not provided)
            strict_mode: If True, reject unknown critical fields

        Returns:
            IngestionResult with UnderwritingRequest or errors
        """
        warnings = []
        provenance = {"source_type": "json", "strict_mode": strict_mode}

        try:
            # Parse input
            if isinstance(data, Path) or (isinstance(data, str) and not data.strip().startswith("{")):
                # File path
                path = Path(data)
                with open(path, "r", encoding="utf-8") as f:
                    raw_data = json.load(f)
                provenance["source_path"] = str(path)
                provenance["source_hash"] = self._compute_file_hash(path)
            elif isinstance(data, str):
                # JSON string
                raw_data = json.loads(data)
                provenance["source_hash"] = hashlib.sha256(data.encode()).hexdigest()[:16]
            else:
                # Dict
                raw_data = data
                provenance["source_hash"] = hashlib.sha256(
                    json.dumps(data, sort_keys=True).encode(),
                ).hexdigest()[:16]

            # Generate request_id if not provided
            if request_id is None:
                request_id = f"UW-{datetime.now().strftime('%Y%m%d')}-{provenance['source_hash'][:8]}"

            # Map to domain model
            result = self.json_mapper.map_to_request(
                raw_data,
                request_id=request_id,
                strict_mode=strict_mode,
            )

            if result.errors:
                return IngestionResult(
                    success=False,
                    warnings=result.warnings,
                    errors=result.errors,
                    provenance=provenance,
                )

            return IngestionResult(
                success=True,
                request=result.request,
                warnings=result.warnings,
                provenance=provenance,
            )

        except json.JSONDecodeError as e:
            return IngestionResult(
                success=False,
                errors=[f"JSON parse error: {str(e)}"],
                provenance=provenance,
            )
        except (OSError, ValueError, TypeError, AttributeError, KeyError) as e:
            return IngestionResult(
                success=False,
                errors=[f"Ingestion error: {str(e)}"],
                provenance=provenance,
            )

    def ingest_csv(
        self,
        data: Union[str, Path],
        mapping_config: Optional[Dict[str, str]] = None,
        request_id: Optional[str] = None,
    ) -> IngestionResult:
        """
        Ingest from CSV file or string.

        Args:
            data: CSV file path or CSV string
            mapping_config: Field name mappings (csv_field -> canonical_field)
            request_id: Optional request ID

        Returns:
            IngestionResult
        """
        provenance = {"source_type": "csv"}

        try:
            result = self.csv_mapper.map_to_request(
                data,
                mapping_config=mapping_config,
                request_id=request_id,
            )

            if result.errors:
                return IngestionResult(
                    success=False,
                    errors=result.errors,
                    provenance=provenance,
                )

            return IngestionResult(
                success=True,
                request=result.request,
                warnings=result.warnings,
                provenance=provenance,
            )

        except (OSError, ValueError, TypeError, AttributeError, KeyError, UnicodeDecodeError) as e:
            return IngestionResult(
                success=False,
                errors=[f"CSV ingestion error: {str(e)}"],
                provenance=provenance,
            )

    def ingest_xlsx(
        self,
        file_path: Path,
        template_type: str = "standard",
        request_id: Optional[str] = None,
    ) -> IngestionResult:
        """
        Ingest from XLSX underwriting template.

        Args:
            file_path: Path to XLSX file
            template_type: Template format identifier
            request_id: Optional request ID

        Returns:
            IngestionResult
        """
        provenance = {"source_type": "xlsx", "template_type": template_type}

        try:
            result = self.xlsx_mapper.map_to_request(
                file_path,
                template_type=template_type,
                request_id=request_id,
            )

            if result.errors:
                return IngestionResult(
                    success=False,
                    errors=result.errors,
                    provenance=provenance,
                )

            return IngestionResult(
                success=True,
                request=result.request,
                warnings=result.warnings,
                provenance=provenance,
            )

        except (OSError, ValueError, TypeError, AttributeError, KeyError) as e:
            return IngestionResult(
                success=False,
                errors=[f"XLSX ingestion error: {str(e)}"],
                provenance=provenance,
            )

    def ingest_documents(
        self,
        doc_paths: list[Path],
        doc_type_map: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Ingest a batch of supporting documents.

        Args:
            doc_paths: List of document file paths
            doc_type_map: Optional mapping of filename patterns to doc types

        Returns:
            Document manifest
        """
        return self.doc_ingestion.ingest_batch(doc_paths, doc_type_map)

    @staticmethod
    def _compute_file_hash(path: Path) -> str:
        """Compute SHA256 hash of file contents."""
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()[:16]

"""Registry for retrieval evidence artifacts."""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class EvidenceRecord:
    artifact_id: str
    scope: str
    company_id: str | None
    source_url: str
    summary: str
    anchor_date: str
    confidence: float
    used_in_section: str


class EvidenceRegistry:
    """Track evidence artifacts referenced in outreach drafts."""

    def __init__(self) -> None:
        self._records: Dict[str, EvidenceRecord] = {}

    def upsert(
        self,
        scope: str,
        company_id: str | None,
        source_url: str,
        summary: str,
        anchor_date: str,
        confidence: float,
        used_in_section: str,
        artifact_id: Optional[str] = None,
    ) -> str:
        record_id = artifact_id or str(uuid.uuid4())
        self._records[record_id] = EvidenceRecord(
            artifact_id=record_id,
            scope=scope,
            company_id=company_id,
            source_url=source_url,
            summary=summary,
            anchor_date=anchor_date,
            confidence=confidence,
            used_in_section=used_in_section,
        )
        return record_id

    def get(self, artifact_id: str) -> Optional[EvidenceRecord]:
        return self._records.get(artifact_id)

    def list(self, scope: Optional[str] = None) -> List[EvidenceRecord]:
        values = self._records.values()
        if scope is None:
            return list(values)
        return [record for record in values if record.scope == scope]

    def __contains__(self, artifact_id: str) -> bool:
        return artifact_id in self._records

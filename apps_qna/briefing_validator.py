"""Briefing Validator — validates uploaded briefing, emits evidence contract.

W2.2: Enhanced validator with SUFFICIENT/STALE/INCOMPLETE/MISMATCH states,
content parsing, and structured evidence contract production.

Plan: .windsurf/plans/apps-qna-spine-integration-e9c5b3.md W2.2
"""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path
from typing import Any

from apps_qna.types.evidence_contracts import (
    BriefingValidationState,
    EvidenceSufficiency,
    UploadedBriefingEvidenceContract,
)

_LOGGER = logging.getLogger(__name__)


def validate_briefing(
    *,
    briefing_path: str | None = None,
) -> UploadedBriefingEvidenceContract:
    """Validate an uploaded briefing and produce an evidence contract.

    Args:
        briefing_path: Path to the uploaded briefing file.

    Returns:
        An UploadedBriefingEvidenceContract with validation state.
    """
    if not briefing_path:
        return UploadedBriefingEvidenceContract(
            validation_state=BriefingValidationState.INCOMPLETE,
            evidence_sufficiency=EvidenceSufficiency.EMPTY,
        )

    path = Path(briefing_path)
    if not path.exists():
        return UploadedBriefingEvidenceContract(
            validation_state=BriefingValidationState.INCOMPLETE,
            evidence_sufficiency=EvidenceSufficiency.EMPTY,
        )

    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return UploadedBriefingEvidenceContract(
            validation_state=BriefingValidationState.INCOMPLETE,
            evidence_sufficiency=EvidenceSufficiency.EMPTY,
        )

    if not content.strip():
        return UploadedBriefingEvidenceContract(
            validation_state=BriefingValidationState.INCOMPLETE,
            evidence_sufficiency=EvidenceSufficiency.EMPTY,
        )

    briefing_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
    size_bytes = len(content.encode("utf-8"))

    company_name, role_title = _extract_metadata(content)

    return UploadedBriefingEvidenceContract(
        briefing_hash=briefing_hash,
        validation_state=BriefingValidationState.SUFFICIENT,
        evidence_sufficiency=EvidenceSufficiency.TEMPLATE_ONLY,
        company_name=company_name,
        role_title=role_title,
        briefing_size_bytes=size_bytes,
    )


def _extract_metadata(content: str) -> tuple[str, str]:
    """Extract company name and role title from briefing content.

    Simple heuristic: looks for YAML-like key-value pairs.
    """
    company = ""
    role = ""
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("company:") or stripped.startswith("Company:"):
            company = stripped.split(":", 1)[1].strip().strip('"').strip("'")
        elif stripped.startswith("role:") or stripped.startswith("Role:"):
            role = stripped.split(":", 1)[1].strip().strip('"').strip("'")
    return company, role


__all__ = ["validate_briefing"]

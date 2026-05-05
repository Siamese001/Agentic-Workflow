"""Briefing Validator — validates uploaded briefing, emits evidence contract.

W0 thin-slice: minimal validator that checks briefing presence and
produces an UploadedBriefingEvidenceContract. Full implementation
lands in W2.2 with SUFFICIENT/STALE/INCOMPLETE/MISMATCH states.

Plan: .windsurf/plans/apps-qna-spine-integration-e9c5b3.md W0.3
"""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path
from typing import Any

from apps_qna.types.spine_contracts import (
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

    return UploadedBriefingEvidenceContract(
        briefing_hash=briefing_hash,
        validation_state=BriefingValidationState.SUFFICIENT,
        evidence_sufficiency=EvidenceSufficiency.TEMPLATE_ONLY,
    )


__all__ = ["validate_briefing"]

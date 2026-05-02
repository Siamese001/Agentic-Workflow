"""DocumentReconciliationEngine — reconciles submitted documents.

Skeleton implementation: counts submitted documents and produces a
deterministic ReconciliationResult with zero unresolved entries. Real
reconciliation will hook into document-OCR + cross-reference services.
"""

from __future__ import annotations

from apps_underwriting_ai.types.underwriting_types import (
    ReconciliationResult,
    UnderwritingRequest,
)


class DocumentReconciliationEngine:
    """Reconciles documents submitted with an underwriting request."""

    def reconcile(self, request: UnderwritingRequest) -> ReconciliationResult:
        """Reconcile the request's documents.

        Args:
            request: Inbound underwriting request.

        Returns:
            ReconciliationResult with reconciled_count = len(documents),
            unresolved_count = 0, and a deterministic note.
        """
        return ReconciliationResult(
            reconciled_count=len(request.documents),
            unresolved_count=0,
            notes=("skeleton reconciliation: all documents counted as reconciled",),
        )

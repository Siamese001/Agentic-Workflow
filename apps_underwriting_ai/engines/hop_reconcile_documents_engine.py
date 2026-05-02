"""HOP2 reconcile_documents — wraps DocumentReconciliationEngine.reconcile."""

from __future__ import annotations

from typing import Any


class HopReconcileDocumentsEngine:
    """Adapter for stage 2 — document reconciliation."""

    def execute(self, context: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        from apps_underwriting_ai.engines.document_reconciliation_engine import (
            DocumentReconciliationEngine,
        )

        request = context.get("underwriting_request")
        if request is None:
            return {"reconciliation_result": None, "reconciliation_skipped": True}

        engine = DocumentReconciliationEngine()
        result = engine.reconcile(request)

        return {"reconciliation_result": result}

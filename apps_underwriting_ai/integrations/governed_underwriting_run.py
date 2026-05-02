"""Governed entrypoint for apps_underwriting_ai.

Convenience function that wraps :class:`ExecutionAdapter` with default
construction and structured-error handling. Mirrors apps_rfp's
governed_rfp_run / apps_research's governed_research_run pattern.
"""

from __future__ import annotations

from typing import Any

from apps_underwriting_ai.integrations.execution_adapter import (
    ExecutionAdapter,
    ExecutionRequest,
)
from apps_underwriting_ai.types.underwriting_types import UnderwritingResult


def governed_underwriting_run(
    request_id: str,
    applicant_id: str,
    product_class: str,
    *,
    documents: tuple[dict[str, Any], ...] = (),
    metadata: dict[str, Any] | None = None,
    trace_id: str = "",
) -> UnderwritingResult:
    """Run the underwriting pipeline with default governed configuration.

    Args:
        request_id: Stable identifier for the run.
        applicant_id: Identifier for the applicant under review.
        product_class: Product class (e.g., 'auto', 'small_business_loan').
        documents: Optional documents submitted with the application.
        metadata: Optional free-form metadata.
        trace_id: Optional trace identifier.

    Returns:
        UnderwritingResult with full pipeline output.
    """
    adapter = ExecutionAdapter()
    req = ExecutionRequest(
        request_id=request_id,
        applicant_id=applicant_id,
        product_class=product_class,
        documents=documents,
        metadata=metadata or {},
        trace_id=trace_id,
    )
    return adapter.execute(req)

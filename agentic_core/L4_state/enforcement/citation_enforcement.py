"""
Phase 8 — Citation Enforcement: anchor coverage rule for retrieval-backed responses.

enforce_citations_for_retrieval(output, anchored_results, retrieval_used) -> output_with_citations
  - If retrieval_used=True and anchored_results empty/missing -> CitationEnforcementViolation
  - Else attach CitationBundle to output["citations"] deterministically (non-mutating to index)
  - If retrieval_used=False -> return output unchanged (legacy parity)
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from agentic_core.L4_state.types.citation_bundle_types import build_citation_bundle
from agentic_core.L4_state.types.retrieval_anchor_types import AnchoredResult, RetrievalAnchor
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,  # noqa: E402
)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class CitationEnforcementViolation(Exception):
    """
    Raised when retrieval was used but anchors are missing from the response.

    Attributes
    ----------
    code   : str — always "MISSING_CITATIONS"
    detail : str — human-readable description
    """

    code: str = "MISSING_CITATIONS"

    def __init__(self, detail: str = "") -> None:
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "CitationEnforcementViolation.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "CitationEnforcementViolation.__init__", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L4_STATE,
            "CitationEnforcementViolation.__init__",
        )
        self.detail = detail
        super().__init__(
            f"[{self.code}] Retrieval used but citations missing" + (f": {detail}" if detail else ""),
        )


def _build_request_hash_from_output(output: dict[str, Any]) -> str:
    """
    Derive a stable request_hash from the output dict.
    Uses only non-volatile fields present in the output.
    Falls back to sha256 of the output keys if no canonical subset available.
    """
    subset = {
        k: output[k]
        for k in sorted(output)
        if k not in ("citations", "timestamp", "elapsed_ms", "trace_id")
        and isinstance(output[k], (str, int, float, bool))
    }
    raw = json.dumps(subset, sort_keys=True, separators=(",", ":")).encode()
    return _sha256(raw)


def enforce_citations_for_retrieval(
    output: dict[str, Any],
    anchored_results: list[AnchoredResult] | None,
    retrieval_used: bool,
    *,
    request_hash: str | None = None,
) -> dict[str, Any]:
    """
    Enforce anchor coverage rule for retrieval-backed responses.

    Parameters
    ----------
    output           : dict  — the response artifact to attach citations to
    anchored_results : list[AnchoredResult] | None
        Retrieved content with anchors. Must be non-empty if retrieval_used=True.
    retrieval_used   : bool
        True if L4 retrieval was used to produce this response.
    request_hash     : str | None
        Optional stable hash of the retrieval request. Auto-derived if None.

    Returns
    -------
    dict — output with "citations" key containing CitationBundle.to_dict()
           (unchanged if retrieval_used=False)

    Raises
    ------
    CitationEnforcementViolation(code="MISSING_CITATIONS")
        If retrieval_used=True and anchored_results is empty or None.
    """
    if not retrieval_used:
        return output
    if not anchored_results:
        raise CitationEnforcementViolation(detail="retrieval_used=True but anchored_results is empty or None")
    anchors: list[RetrievalAnchor] = [r.anchor for r in anchored_results]
    rh = request_hash if request_hash else _build_request_hash_from_output(output)
    bundle = build_citation_bundle(request_hash=rh, anchors=anchors)
    result = dict(output)
    result["citations"] = bundle.to_dict()
    return result


def assemble_response(
    output: dict[str, Any],
    anchored_results: list[AnchoredResult] | None,
    retrieval_used: bool,
    *,
    request_hash: str | None = None,
) -> dict[str, Any]:
    """
    Canonical response assembly seam.

    Calls enforce_citations_for_retrieval() to attach citations before returning.
    This is the single authoritative entry point for final response construction.
    """
    return enforce_citations_for_retrieval(
        output=output,
        anchored_results=anchored_results,
        retrieval_used=retrieval_used,
        request_hash=request_hash,
    )

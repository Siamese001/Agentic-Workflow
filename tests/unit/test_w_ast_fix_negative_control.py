"""W-AST-FIX Negative Control: env-toggled tamper/restore for REQ-PT-011 + REQ-RAGX-006.

When W_AST_FIX_NEGCTRL_TAMPER=1:
  - A controlled violation is injected so the test yields xfail(strict=True) exit 0.
When W_AST_FIX_NEGCTRL_TAMPER is unset or 0:
  - The tests run normally and PASS.
"""

from __future__ import annotations

import os

import pytest

pytestmark = pytest.mark.unit_min_deps

_TAMPER = os.environ.get("W_AST_FIX_NEGCTRL_TAMPER", "0") == "1"


# ---------------------------------------------------------------------------
# REQ-PT-011 negative control
# ---------------------------------------------------------------------------


@pytest.mark.xfail(
    condition=_TAMPER,
    reason="W_AST_FIX_NEGCTRL_TAMPER=1: deliberate slot-order tamper",
    strict=True,
)
def test_negctrl_pt011_slot_order():
    """Normal mode: canonical order passes.  Tamper mode: reversed order must fail."""
    from agentic_core.prompt_governance.contracts.slot_contracts import (
        validate_slot_order,
    )

    if _TAMPER:
        # Deliberate tamper: reversed slot order — this MUST raise
        tampered = (
            "<SLOT_U0>user</SLOT_U0>\n"
            "<SLOT_C0>context</SLOT_C0>\n"
            "<SLOT_I0>instructional</SLOT_I0>\n"
            "<SLOT_D0>directives</SLOT_D0>\n"
            "<SLOT_S0>system</SLOT_S0>\n"
        )
        validate_slot_order(tampered)  # raises SlotOrderViolation -> xfail
    else:
        # Normal: canonical order passes
        canonical = (
            "<SLOT_S0>system</SLOT_S0>\n"
            "<SLOT_D0>directives</SLOT_D0>\n"
            "<SLOT_I0>instructional</SLOT_I0>\n"
            "<SLOT_C0>context</SLOT_C0>\n"
            "<SLOT_U0>user</SLOT_U0>\n"
        )
        validate_slot_order(canonical)


# ---------------------------------------------------------------------------
# REQ-RAGX-006 negative control
# ---------------------------------------------------------------------------


@pytest.mark.xfail(
    condition=_TAMPER,
    reason="W_AST_FIX_NEGCTRL_TAMPER=1: deliberate citation-custody tamper",
    strict=True,
)
def test_negctrl_ragx006_citation_custody():
    """Normal mode: cited context passes.  Tamper mode: uncited context must fail."""
    from agentic_core.L5_safety.enforcement.rag_guardrail import (
        CitationBundle,
        validate_citation_custody,
    )

    if _TAMPER:
        # Deliberate tamper: context present but no citations
        chunks = [{"chunk_id": "c1", "text": "external knowledge"}]
        validate_citation_custody(chunks, None)  # raises -> xfail
    else:
        # Normal: properly cited
        chunks = [{"chunk_id": "c1", "text": "external knowledge"}]
        citations = [
            CitationBundle(
                chunk_id="c1",
                source_ref="docs/ref.md",
                byte_sha256="a" * 64,
                byte_range=(0, 100),
                score=0.95,
            )
        ]
        validate_citation_custody(chunks, citations)

"""W1 / G5: C0.2 hard-block error text must name the cause and the remediation command.

Plan: apps-rg-e2e-gap-remediation-7e2d9c (W1 — actionable C0.2 text).

The frozen AIG/Brown signature surfaced only ``... but did not complete`` with no cause and no
recovery path. These tests exercise the real ``_enforce_mandatory_lanes`` block path (policy
gates + profile monkeypatched on) and assert the raised message now carries a named cause plus
the doctor/bootstrap remediation. Pure product-mode test — no APPS_RG_TEST_HARNESS.
"""

from __future__ import annotations

import pytest

from apps_rg.runtime.c0 import c02_product_hybrid_retrieval as mod


class _FakeProfile:
    enabled = True

    def get_section_config(self, section_id: str) -> dict:
        return {"section_id": section_id}

    def section_sparse_config(self, cfg: dict) -> dict:
        return {"sparse_enabled": True}


@pytest.fixture
def _mandatory_on(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        "apps_rg.runtime.product_output_policy.product_fail_closed_runtime", lambda: True
    )
    monkeypatch.setattr(
        "apps_rg.runtime.c0_mandatory_policy.apps_rg_c0_dense_sparse_mandatory", lambda: True
    )
    monkeypatch.setattr(
        "apps_rg.runtime.bindings.c0_binding.SectionRetrievalProfile", _FakeProfile
    )


def test_remediation_hint_names_doctor_and_bootstrap() -> None:
    hint = mod._C0_REMEDIATION_HINT
    assert "doctor --strict" in hint
    assert "bootstrap fact-vectors" in hint


def test_dense_block_message_is_actionable(_mandatory_on) -> None:
    from apps_rg.runtime.bindings.c0_binding import C0EvidenceGapError

    with pytest.raises(C0EvidenceGapError) as excinfo:
        mod._enforce_mandatory_lanes(
            section_id="competencies",
            lanes={"dense": "not_run", "sparse": "not_run", "metadata": "not_run"},
            sparse_refs=[],
        )
    msg = str(excinfo.value)
    assert "competencies" in msg
    assert "did not complete" in msg
    # named cause
    assert "fact_vectors collection" in msg
    # remediation
    assert "doctor --strict" in msg
    assert "bootstrap fact-vectors" in msg


def test_sparse_block_message_is_actionable(_mandatory_on) -> None:
    from apps_rg.runtime.bindings.c0_binding import C0EvidenceGapError

    with pytest.raises(C0EvidenceGapError) as excinfo:
        mod._enforce_mandatory_lanes(
            section_id="ey_bullets",
            lanes={"dense": "completed", "sparse": "not_run", "metadata": "completed"},
            sparse_refs=[],
        )
    msg = str(excinfo.value)
    assert "sparse lane required" in msg
    assert "doctor --strict" in msg

"""Tests for the retired commercial medium-claim containment harness."""

from __future__ import annotations

import pytest

from apps_rg.fact_inventory import validate_commercial_medium_claim_output_containment as retired


def test_retired_harness_fails_closed() -> None:
    assert "Retired commercial medium-claim" in (retired.__doc__ or "")

    with pytest.raises(RuntimeError, match="selected_graph_evidence_plan"):
        retired.main()


def test_retired_harness_does_not_expose_legacy_payload_api() -> None:
    legacy_exports = {
        "BLOCKED_FACT_IDS",
        "BULLET_NARRATIVE_SECTIONS",
        "HEADLINE_EXEC_SECTIONS",
        "OUT_JSON",
        "build_containment_payload",
    }

    for name in legacy_exports:
        assert not hasattr(retired, name)

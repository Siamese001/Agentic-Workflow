"""Contract: retired commercial MEDIUM claim harness stays fail-closed."""

from __future__ import annotations

import pytest

from apps_rg.fact_inventory import validate_commercial_medium_claim_output_containment as retired


def test_commercial_medium_claim_harness_is_retired_contract() -> None:
    with pytest.raises(RuntimeError, match="Commercial medium-claim SRFS containment is retired"):
        retired.main()


def test_legacy_containment_payload_api_stays_removed() -> None:
    for name in ("BULLET_NARRATIVE_SECTIONS", "OUT_JSON", "build_containment_payload"):
        assert not hasattr(retired, name)

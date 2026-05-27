"""L0 route profile → GraphTraversePolicy.is_active for apps_rg product lanes."""

from __future__ import annotations

from pathlib import Path

from apps_rg.runtime.bindings.l0_binding import _graph_policy_from_row, _load_profiles

REPO = Path(__file__).resolve().parents[2]


def test_resume_generation_route_graph_policy_active() -> None:
    rows = _load_profiles()
    row = next(
        r
        for r in rows
        if r.get("conditions", {}).get("generation_mode") == "generate_scratch"
    )
    policy = _graph_policy_from_row(row)
    assert policy is not None
    assert policy.graph_expansion_allowed is True
    assert policy.live_wiring_deferred is False
    assert policy.is_active is True
    assert "c0_graph_adapter" in (policy.graph_adapter_ref or "")

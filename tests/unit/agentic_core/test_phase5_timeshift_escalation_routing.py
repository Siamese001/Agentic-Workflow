"""
Phase 5 — Wave 3 Tests: Policy-coded escalation routing (prior-only, time-shifted).

End-to-end-shaped: exercises decide_mode_from_prior_violations() with real
ViolationEventStore and RoutingConfig instances.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from agentic_core.L0_routing.engines.escalation_router import (
    decide_mode_from_prior_violations,
)
from agentic_core.L4_state.config.versioned_configs import RoutingConfig
from agentic_core.L4_state.enforcement.violation_event_store import ViolationEventStore
from agentic_core.L4_state.types.violation_event import emit_violation_event

pytestmark = pytest.mark.unit_min_deps

_TS = "2026-02-21T00:00:00Z"

_ROUTER_MODULE = (
    Path(__file__).parent.parent.parent / "agentic_core" / "L0_routing" / "engines" / "escalation_router.py"
)


def _store_with_events(*tick_severity_pairs: tuple[int, float]) -> ViolationEventStore:
    store = ViolationEventStore()
    for tick, severity in tick_severity_pairs:
        e = emit_violation_event(
            mission_id="mission-test",
            commit_tick=tick,
            guardian_decision="block",
            violation_codes=["SCOPE_VIOLATION"],
            severity_score=severity,
            created_at_utc=_TS,
        )
        store.store_violation_event(e)
    return store


class TestRoutingUsesPriorViolationsOnly:
    def test_routing_uses_prior_violations_only(self):
        """
        Core time-shift guarantee:
        - Prior high-severity violation at tick 5 → tick 10 routes to compliance.
        - Same-cycle violation emitted at tick 10 → must NOT affect tick 10 decision.
        """
        cfg = RoutingConfig(
            escalation_severity_threshold=0.7,
            escalation_window_ticks=20,
            escalation_mode="compliance",
        )
        store = ViolationEventStore()

        # Prior violation at tick 5 (high severity)
        prior = emit_violation_event(
            mission_id="m1",
            commit_tick=5,
            guardian_decision="block",
            violation_codes=["SCOPE_VIOLATION"],
            severity_score=0.9,
            created_at_utc=_TS,
        )
        store.store_violation_event(prior)

        # Same-cycle violation at tick 10 (also high severity — must be invisible)
        same_cycle = emit_violation_event(
            mission_id="m1",
            commit_tick=10,
            guardian_decision="block",
            violation_codes=["IMPORT_ERROR"],
            severity_score=0.95,
            created_at_utc=_TS,
        )
        store.store_violation_event(same_cycle)

        # Routing at tick 10: prior violation at tick 5 triggers escalation
        mode = decide_mode_from_prior_violations(
            execution_start_tick=10,
            routing_config=cfg,
            violation_store=store,
        )
        assert mode == "compliance"

    def test_same_cycle_violation_alone_does_not_trigger_escalation(self):
        """
        If the ONLY stored violation is at commit_tick == execution_start_tick,
        the router must return "normal" (same-cycle is invisible).
        """
        cfg = RoutingConfig(
            escalation_severity_threshold=0.5,
            escalation_window_ticks=20,
            escalation_mode="compliance",
        )
        store = ViolationEventStore()

        same_cycle = emit_violation_event(
            mission_id="m1",
            commit_tick=10,
            guardian_decision="block",
            violation_codes=["SCOPE_VIOLATION"],
            severity_score=1.0,
            created_at_utc=_TS,
        )
        store.store_violation_event(same_cycle)

        mode = decide_mode_from_prior_violations(
            execution_start_tick=10,
            routing_config=cfg,
            violation_store=store,
        )
        assert mode == "normal"

    def test_prior_violation_below_threshold_does_not_escalate(self):
        cfg = RoutingConfig(
            escalation_severity_threshold=0.8,
            escalation_window_ticks=20,
            escalation_mode="compliance",
        )
        store = _store_with_events((5, 0.5))

        mode = decide_mode_from_prior_violations(
            execution_start_tick=10,
            routing_config=cfg,
            violation_store=store,
        )
        assert mode == "normal"

    def test_prior_violation_at_threshold_triggers_escalation(self):
        """severity_score == threshold is >= threshold → escalates."""
        cfg = RoutingConfig(
            escalation_severity_threshold=0.75,
            escalation_window_ticks=20,
            escalation_mode="compliance",
        )
        store = _store_with_events((5, 0.75))

        mode = decide_mode_from_prior_violations(
            execution_start_tick=10,
            routing_config=cfg,
            violation_store=store,
        )
        assert mode == "compliance"

    def test_violation_outside_window_does_not_escalate(self):
        """Event older than escalation_window_ticks is outside the fetch window."""
        cfg = RoutingConfig(
            escalation_severity_threshold=0.5,
            escalation_window_ticks=3,
            escalation_mode="compliance",
        )
        # tick 5, window=[7,10) → tick 5 is outside
        store = _store_with_events((5, 0.9))

        mode = decide_mode_from_prior_violations(
            execution_start_tick=10,
            routing_config=cfg,
            violation_store=store,
        )
        assert mode == "normal"

    def test_violation_inside_window_escalates(self):
        cfg = RoutingConfig(
            escalation_severity_threshold=0.5,
            escalation_window_ticks=6,
            escalation_mode="compliance",
        )
        # tick 5, window=[4,10) → tick 5 is inside
        store = _store_with_events((5, 0.9))

        mode = decide_mode_from_prior_violations(
            execution_start_tick=10,
            routing_config=cfg,
            violation_store=store,
        )
        assert mode == "compliance"


class TestDenylistTriggersEscalation:
    def test_denylist_code_triggers_escalation_regardless_of_severity(self):
        """A violation code in the denylist triggers escalation even at low severity."""
        cfg = RoutingConfig(
            escalation_severity_threshold=0.99,
            escalation_window_ticks=20,
            escalation_violation_code_denylist=("CRITICAL_BREACH",),
            escalation_mode="compliance",
        )
        store = ViolationEventStore()
        e = emit_violation_event(
            mission_id="m1",
            commit_tick=5,
            guardian_decision="block",
            violation_codes=["CRITICAL_BREACH"],
            severity_score=0.1,
            created_at_utc=_TS,
        )
        store.store_violation_event(e)

        mode = decide_mode_from_prior_violations(
            execution_start_tick=10,
            routing_config=cfg,
            violation_store=store,
        )
        assert mode == "compliance"

    def test_non_denylist_code_does_not_trigger_via_denylist(self):
        cfg = RoutingConfig(
            escalation_severity_threshold=0.99,
            escalation_window_ticks=20,
            escalation_violation_code_denylist=("CRITICAL_BREACH",),
            escalation_mode="compliance",
        )
        store = _store_with_events((5, 0.1))

        mode = decide_mode_from_prior_violations(
            execution_start_tick=10,
            routing_config=cfg,
            violation_store=store,
        )
        assert mode == "normal"

    def test_empty_denylist_does_not_trigger_code_path(self):
        cfg = RoutingConfig(
            escalation_severity_threshold=0.99,
            escalation_window_ticks=20,
            escalation_violation_code_denylist=(),
            escalation_mode="compliance",
        )
        store = _store_with_events((5, 0.1))

        mode = decide_mode_from_prior_violations(
            execution_start_tick=10,
            routing_config=cfg,
            violation_store=store,
        )
        assert mode == "normal"


class TestDefaultConfigPreservesLegacyRouting:
    def test_default_config_preserves_legacy_routing(self):
        """
        Default RoutingConfig with no prior violations returns "normal".
        Legacy behavior is preserved.
        """
        cfg = RoutingConfig()
        store = ViolationEventStore()

        mode = decide_mode_from_prior_violations(
            execution_start_tick=1,
            routing_config=cfg,
            violation_store=store,
        )
        assert mode == "normal"

    def test_default_config_escalation_mode_is_normal(self):
        """Default escalation_mode is 'normal' — no surprise routing."""
        cfg = RoutingConfig()
        assert cfg.escalation_mode == "normal"

    def test_default_config_denylist_is_empty(self):
        cfg = RoutingConfig()
        assert cfg.escalation_violation_code_denylist == ()

    def test_default_config_window_ticks_positive(self):
        cfg = RoutingConfig()
        assert cfg.escalation_window_ticks > 0

    def test_default_config_severity_threshold_in_range(self):
        cfg = RoutingConfig()
        assert 0.0 < cfg.escalation_severity_threshold <= 1.0

    def test_routing_config_hash_stable(self):
        """RoutingConfig.config_hash is deterministic."""
        cfg1 = RoutingConfig()
        cfg2 = RoutingConfig()
        assert cfg1.config_hash == cfg2.config_hash

    def test_routing_config_hash_changes_with_threshold(self):
        cfg1 = RoutingConfig(escalation_severity_threshold=0.5)
        cfg2 = RoutingConfig(escalation_severity_threshold=0.9)
        assert cfg1.config_hash != cfg2.config_hash

    def test_routing_config_hash_changes_with_mode(self):
        cfg1 = RoutingConfig(escalation_mode="normal")
        cfg2 = RoutingConfig(escalation_mode="compliance")
        assert cfg1.config_hash != cfg2.config_hash


class TestStaticAuditNoHardcodedThreshold:
    def test_no_hardcoded_severity_threshold_in_router_module(self):
        """
        Static AST audit: escalation_router.py must not contain any numeric
        literal that looks like a hardcoded severity threshold (float in 0..1
        range used in a comparison). All thresholds must come from config.

        Specifically: no bare float literals in Compare nodes inside the router.
        """
        source = _ROUTER_MODULE.read_text(encoding="utf-8")
        tree = ast.parse(source)

        hardcoded_floats_in_comparisons: list[float] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Compare):
                for comparator in node.comparators + [node.left]:
                    if isinstance(comparator, ast.Constant) and isinstance(comparator.value, float):
                        hardcoded_floats_in_comparisons.append(comparator.value)

        assert hardcoded_floats_in_comparisons == [], (
            f"escalation_router.py contains hardcoded float literals in comparisons: "
            f"{hardcoded_floats_in_comparisons}. "
            f"All thresholds must come from routing_config."
        )

    def test_router_module_exists(self):
        assert _ROUTER_MODULE.exists(), f"Router module not found: {_ROUTER_MODULE}"

    def test_router_references_routing_config_threshold(self):
        """Router source must reference escalation_severity_threshold from config."""
        source = _ROUTER_MODULE.read_text(encoding="utf-8")
        assert "escalation_severity_threshold" in source

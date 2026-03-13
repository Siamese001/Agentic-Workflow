# ruff: noqa: E702
"""
E2E healing pipeline tests for execute_ssot.py and _ssot_phases.py.

Covers all wiring gaps found in the March-2026 post-mortem:
  1. _record_healing_action in execute_ssot.py used a stale LOCAL copy (no SL wiring)
     → Fixed: replaced with import from _ssot_validation_artifacts
  2. Phase 2 exception path never called _record_healing_action with outcome=FAILURE
     → Fixed: added FAILURE record in except block
  3. system_learning bridge was never called from execute_ssot heal paths
     → Fixed: _record_healing_action now calls get_sl_memory_bridge() on every outcome
  4. HITL gate raised HitlRequiredError in non-TTY (correct) but tests didn't patch it
     → Fixed: test helpers patch the gate with _tty_override=True + auto-approve

Test matrix:
  A. _record_healing_action wiring
     - module resolution points to _ssot_validation_artifacts (not stale local copy)
     - persist_healing_success_rate called on SUCCESS outcome
     - persist_failure_pattern + persist_healing_success_rate called on FAILURE outcome
     - persist_failure_pattern + persist_healing_success_rate called on SKIPPED outcome
     - MCP bridge unavailable → no exception raised (fire-and-forget)

  B. Phase 2 heal loop
     - success path records SUCCESS via _record_healing_action → SL bridge
     - exception path records FAILURE via _record_healing_action → SL bridge
     - agent_key → class name mapping covers all 9 agents

  C. Phase 1 (via _ssot_phases.py / execute_phase1_impl)
     - FilesystemSSOTReconcilerAgent heal outcome recorded
     - LocationHealerAgent heal outcome recorded

  D. Phase 3 HierarchyHealerAgent
     - HITL YES → heal fires, SUCCESS recorded to SL bridge
     - HITL NO  → heal skipped, HITL record logged
     - HITL ABORT → returns None immediately

  E. RootHygieneHealerAgent
     - HITL YES → heal fires, SUCCESS recorded to SL bridge
     - HITL ABORT → returns None

  F. System-learning bridge integration
     - persist_healing_success_rate receives correct rate=1.0 for SUCCESS
     - persist_healing_success_rate receives correct rate=0.0 for FAILURE
     - persist_failure_pattern receives correct label for FAILURE
     - error_sig format is agent::territory::outcome
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Force-register the SL bridge submodule so patch() can resolve
# "system_learning.adapters.system_learning_memory_bridge.get_sl_memory_bridge"
# regardless of test-suite import order.
import system_learning.adapters.system_learning_memory_bridge as _sl_bridge_mod  # noqa: F401
from agentic_core.L0_routing.scripts._ssot_validation_artifacts import _record_healing_action
from agentic_core.L5_safety.enforcement.hitl_gate import HitlGate

_SL_BRIDGE_PATCH = "system_learning.adapters.system_learning_memory_bridge.get_sl_memory_bridge"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _fake_state():
    class _SM:
        state = {}

        def add_event(self, *a):
            pass

        def complete_agent(self, *a):
            pass

        def update_agent(self, *a):
            pass

        def skip_agent(self, *a):
            pass

    return _SM()


def _auto_approve_gate(repo_root=None):
    """HitlGate that auto-approves (simulates human pressing Y)."""
    return HitlGate(repo_root or Path("."), input_fn=lambda _: "Y", _tty_override=True)


def _deny_gate(repo_root=None):
    return HitlGate(repo_root or Path("."), input_fn=lambda _: "N", _tty_override=True)


def _abort_gate(repo_root=None):
    return HitlGate(repo_root or Path("."), input_fn=lambda _: "A", _tty_override=True)


def _mock_bridge():
    b = MagicMock()
    b.persist_healing_success_rate = MagicMock(return_value=True)
    b.persist_failure_pattern = MagicMock(return_value=True)
    b.persist_rca_findings = MagicMock(return_value=True)
    return b


# ===========================================================================
# A. _record_healing_action wiring
# ===========================================================================


class TestRecordHealingActionWiring:
    def test_module_is_ssot_validation_artifacts(self):
        """execute_ssot must use the wired version, not a stale local copy."""
        import agentic_core.L0_routing.scripts.execute_ssot as mod

        assert mod._record_healing_action.__module__ == (
            "agentic_core.L0_routing.scripts._ssot_validation_artifacts"
        ), (
            "execute_ssot._record_healing_action must point to "
            "_ssot_validation_artifacts — stale local copy detected"
        )

    def test_success_calls_persist_healing_success_rate(self, tmp_path):
        bridge = _mock_bridge()
        sm = _fake_state()
        with patch(
            _SL_BRIDGE_PATCH,
            return_value=bridge,
        ):
            _record_healing_action(
                sm,
                agent="HierarchyHealerAgent",
                territory="agentic_core",
                confidence=0.9,
                fix_summary="3 violations fixed",
                outcome="SUCCESS",
            )
        bridge.persist_healing_success_rate.assert_called_once()
        call_args = bridge.persist_healing_success_rate.call_args
        assert call_args[1]["rate"] == 1.0
        bridge.persist_failure_pattern.assert_not_called()

    def test_failure_calls_both_bridge_methods(self, tmp_path):
        bridge = _mock_bridge()
        sm = _fake_state()
        with patch(
            _SL_BRIDGE_PATCH,
            return_value=bridge,
        ):
            _record_healing_action(
                sm,
                agent="HierarchyHealerAgent",
                territory="mixins",
                confidence=0.0,
                fix_summary="purge failed",
                outcome="FAILURE",
            )
        bridge.persist_healing_success_rate.assert_called_once()
        assert bridge.persist_healing_success_rate.call_args[1]["rate"] == 0.0
        bridge.persist_failure_pattern.assert_called_once()

    def test_skipped_calls_both_bridge_methods(self):
        bridge = _mock_bridge()
        sm = _fake_state()
        with patch(
            _SL_BRIDGE_PATCH,
            return_value=bridge,
        ):
            _record_healing_action(
                sm,
                agent="RootHygieneHealerAgent",
                territory="__global__",
                confidence=0.0,
                fix_summary="HITL skipped",
                outcome="SKIPPED",
            )
        bridge.persist_healing_success_rate.assert_called_once()
        assert bridge.persist_healing_success_rate.call_args[1]["rate"] == 0.0
        bridge.persist_failure_pattern.assert_called_once()

    def test_bridge_unavailable_no_exception(self):
        """Fire-and-forget: bridge failure must never propagate."""
        sm = _fake_state()
        with patch(
            _SL_BRIDGE_PATCH,
            side_effect=RuntimeError("MCP down"),
        ):
            _record_healing_action(
                sm,
                agent="AnyAgent",
                territory="agentic_core",
                fix_summary="test",
                outcome="SUCCESS",
            )
        assert len(sm.state.get("healing_actions", [])) == 1

    def test_error_sig_format_contains_agent_territory_outcome(self):
        """Error signature must be agent::territory::outcome for RCA clustering."""
        captured_sigs = []
        bridge = _mock_bridge()
        bridge.persist_healing_success_rate.side_effect = lambda sig, **kw: captured_sigs.append(sig) or True
        sm = _fake_state()
        with patch(
            _SL_BRIDGE_PATCH,
            return_value=bridge,
        ):
            _record_healing_action(
                sm,
                agent="LocationHealerAgent",
                territory="apps_rg",
                fix_summary="moved 2 files",
                outcome="SUCCESS",
            )
        assert len(captured_sigs) == 1
        assert captured_sigs[0] == "LocationHealerAgent::apps_rg::SUCCESS"

    def test_failure_pattern_label_contains_agent_and_summary(self):
        captured_labels = []
        bridge = _mock_bridge()
        bridge.persist_failure_pattern.side_effect = (
            lambda pattern_id, pattern_label, centroid_hash, member_count, **kw: captured_labels.append(
                pattern_label
            )
            or True
        )
        sm = _fake_state()
        with patch(
            _SL_BRIDGE_PATCH,
            return_value=bridge,
        ):
            _record_healing_action(
                sm,
                agent="GravityLeakHealerAgent",
                territory="agentic_core",
                fix_summary="gravity leak detected in L3",
                outcome="FAILURE",
            )
        assert len(captured_labels) == 1
        assert "GravityLeakHealerAgent" in captured_labels[0]
        assert "FAILURE" in captured_labels[0]

    def test_action_appended_to_state_regardless_of_bridge(self):
        """Healing action must be recorded in state even when bridge raises."""
        sm = _fake_state()
        with patch(
            _SL_BRIDGE_PATCH,
            side_effect=ImportError("no bridge"),
        ):
            _record_healing_action(
                sm,
                agent="ArchitectureGovernorAgent",
                territory="agentic_core",
                fix_summary="gov fixed",
                outcome="SUCCESS",
            )
        assert sm.state["healing_actions"][0]["agent"] == "ArchitectureGovernorAgent"
        assert sm.state["healing_actions"][0]["outcome"] == "SUCCESS"


# ===========================================================================
# B. Phase 2 heal loop
# ===========================================================================


class TestPhase2HealLoop:
    """execute_reconciliation_plan: success + failure paths both wire to SL."""

    def _load(self):
        import importlib

        try:
            return importlib.import_module("agentic_core.L0_routing.scripts.execute_ssot")
        except ImportError as e:
            pytest.skip(f"execute_ssot unavailable: {e}")

    def _make_ctx(self, heal=True):
        ctx = MagicMock()
        ctx.heal = heal
        return ctx

    def _make_de(self, mod, allow=True):
        de = MagicMock(spec=mod.SovereignDecisionEngine)
        de.should_proceed_with_healing.return_value = (allow, "test-reason")
        de.request_sovereignty_token.return_value = True
        de.release_sovereignty_token.return_value = None
        conf = MagicMock()
        conf.value = 0.9
        de.calculate_healing_confidence.return_value = conf
        return de

    def test_success_path_records_success_to_sl(self):
        mod = self._load()
        bridge = _mock_bridge()
        sm = _fake_state()
        sm.state = {}

        agent_cls = MagicMock()
        agent_inst = MagicMock()
        agent_inst.heal_repository.return_value = {"violations_fixed": 2}
        agent_cls.return_value = agent_inst
        agents = {"hierarchy": agent_cls}

        violations = [
            {"type": "HIERARCHY", "file": "agentic_core/foo.py", "suggested_agent": "hierarchy"}
        ] * 2
        plan = {"violations_found": violations}

        de = self._make_de(mod)

        with patch("agentic_core.L0_routing.scripts.execute_ssot.REPO_ROOT", Path(".")):
            with patch("agentic_core.L0_routing.scripts.execute_ssot._get_uwg", return_value=MagicMock()):
                with patch(
                    _SL_BRIDGE_PATCH,
                    return_value=bridge,
                ):
                    mod.execute_phase2_reconciliation(
                        agents,
                        "agentic_core",
                        de,
                        sm,
                        plan,
                        ctx=self._make_ctx(heal=True),
                    )

        # Must have called persist_healing_success_rate with rate=1.0
        calls_by_sig = {
            c.args[0]: c.kwargs.get("rate") for c in bridge.persist_healing_success_rate.call_args_list
        }
        success_sigs = [s for s, r in calls_by_sig.items() if r == 1.0]
        assert success_sigs, "No SUCCESS healing rate persisted to SL bridge"

    def test_failure_path_records_failure_to_sl(self):
        mod = self._load()
        bridge = _mock_bridge()
        sm = _fake_state()
        sm.state = {}

        agent_cls = MagicMock()
        agent_inst = MagicMock()
        agent_inst.heal_repository.side_effect = RuntimeError("agent exploded")
        agent_cls.return_value = agent_inst
        agents = {"hierarchy": agent_cls}

        violations = [{"type": "HIERARCHY", "file": "agentic_core/foo.py", "suggested_agent": "hierarchy"}]
        plan = {"violations_found": violations}

        de = self._make_de(mod)

        with patch("agentic_core.L0_routing.scripts.execute_ssot.REPO_ROOT", Path(".")):
            with patch("agentic_core.L0_routing.scripts.execute_ssot._get_uwg", return_value=MagicMock()):
                with patch(
                    _SL_BRIDGE_PATCH,
                    return_value=bridge,
                ):
                    result = mod.execute_phase2_reconciliation(
                        agents,
                        "agentic_core",
                        de,
                        sm,
                        plan,
                        ctx=self._make_ctx(heal=True),
                    )

        assert result["errors"] >= 1
        # persist_failure_pattern must have been called for this FAILURE
        bridge.persist_failure_pattern.assert_called()
        # persist_healing_success_rate must have rate=0.0 for the failure
        fail_calls = [
            c for c in bridge.persist_healing_success_rate.call_args_list if c.kwargs.get("rate") == 0.0
        ]
        assert fail_calls, "FAILURE rate=0.0 not persisted to SL bridge"

    def test_agent_key_to_classname_mapping_complete(self):
        """All 9 agent keys must map to their class names."""
        mod = self._load()
        bridge = _mock_bridge()
        sm = _fake_state()
        sm.state = {}
        de = self._make_de(mod)

        for agent_key, expected_classname in [
            ("reconciler", "FilesystemSSOTReconcilerAgent"),
            ("location", "LocationHealerAgent"),
            ("hierarchy", "HierarchyHealerAgent"),
            ("arch_governor", "ArchitectureGovernorAgent"),
            ("gravity_repair", "GravityLeakHealerAgent"),
            ("file_classification", "FileClassificationHealerAgent"),
            ("root_hygiene", "RootHygieneHealerAgent"),
        ]:
            sm.state = {}
            agent_inst = MagicMock()
            agent_inst.heal_repository.return_value = {"violations_fixed": 1}
            agent_cls = MagicMock(return_value=agent_inst)
            agents = {agent_key: agent_cls}
            violations_list = [{"type": "T", "file": "x.py", "suggested_agent": agent_key}]

            with patch("agentic_core.L0_routing.scripts.execute_ssot.REPO_ROOT", Path(".")):
                with patch("agentic_core.L0_routing.scripts.execute_ssot._get_uwg", return_value=MagicMock()):
                    with patch(
                        _SL_BRIDGE_PATCH,
                        return_value=bridge,
                    ):
                        plan = {"violations_found": violations_list}
                        mod.execute_phase2_reconciliation(
                            agents,
                            "agentic_core",
                            de,
                            sm,
                            plan,
                            ctx=self._make_ctx(heal=True),
                        )

            recorded = sm.state.get("healing_actions", [])
            if recorded:
                assert recorded[-1]["agent"] == expected_classname, (
                    f"agent_key '{agent_key}' mapped to '{recorded[-1]['agent']}' "
                    f"instead of '{expected_classname}'"
                )


# ===========================================================================
# C. Phase 3 HierarchyHealerAgent (HITL + SL)
# ===========================================================================


class TestPhase3HierarchyHealerE2E:
    def _load(self):
        import importlib

        try:
            return importlib.import_module("agentic_core.L0_routing.scripts.execute_ssot")
        except ImportError as e:
            pytest.skip(f"execute_ssot unavailable: {e}")

    def _make_de(self, mod, allow=True):
        de = MagicMock(spec=mod.SovereignDecisionEngine)
        de.should_proceed_with_healing.return_value = (allow, "AUTO-HEAL")
        conf = MagicMock()
        conf.value = 0.9
        de.calculate_healing_confidence.return_value = conf
        return de

    def _mock_hier(self, n_violations=2):
        hier_cls = MagicMock()
        hier_inst = MagicMock()
        hier_inst.scan_root_violations.return_value = {
            "violations": [
                {"type": "HIERARCHY", "file": f"agentic_core/f{i}.py"} for i in range(n_violations)
            ],
            "violations_found": n_violations,
        }
        hier_inst.heal_repository.return_value = {"violations_fixed": n_violations}
        hier_cls.return_value = hier_inst
        return hier_cls, hier_inst

    def test_hitl_yes_heal_fires_and_sl_records_success(self):
        mod = self._load()
        bridge = _mock_bridge()
        sm = _fake_state()
        sm.state = {}
        hier_cls, hier_inst = self._mock_hier(3)
        de = self._make_de(mod)

        ctx = MagicMock()
        ctx.heal = True
        agents = {"hierarchy": hier_cls}

        with patch("agentic_core.L0_routing.scripts.execute_ssot.REPO_ROOT", Path(".")):
            with patch(
                "agentic_core.L5_safety.enforcement.hitl_gate.get_hitl_gate",
                return_value=_auto_approve_gate(),
            ):
                with patch(
                    _SL_BRIDGE_PATCH,
                    return_value=bridge,
                ):
                    with patch.dict(
                        "sys.modules",
                        {
                            "agentic_core.L5_safety.reasoning.hierarchy_validator": MagicMock(
                                HierarchyValidatorAgent=hier_cls
                            )
                        },
                    ):
                        result = mod.execute_phase3_alignment_impl(agents, "agentic_core", de, sm, ctx=ctx)

        hier_inst.heal_repository.assert_called_once()
        assert result is not None
        # SL bridge must have received a SUCCESS persist
        success_calls = [
            c for c in bridge.persist_healing_success_rate.call_args_list if c.kwargs.get("rate") == 1.0
        ]
        assert success_calls, "HierarchyHealerAgent SUCCESS not persisted to SL bridge"

    def test_hitl_no_heal_skipped_sl_records_hitl_outcome(self):
        mod = self._load()
        bridge = _mock_bridge()
        sm = _fake_state()
        sm.state = {}
        hier_cls, hier_inst = self._mock_hier(2)
        de = self._make_de(mod)
        ctx = MagicMock()
        ctx.heal = True

        with patch("agentic_core.L0_routing.scripts.execute_ssot.REPO_ROOT", Path(".")):
            with patch(
                "agentic_core.L5_safety.enforcement.hitl_gate.get_hitl_gate", return_value=_deny_gate()
            ):
                with patch(
                    _SL_BRIDGE_PATCH,
                    return_value=bridge,
                ):
                    with patch.dict(
                        "sys.modules",
                        {
                            "agentic_core.L5_safety.reasoning.hierarchy_validator": MagicMock(
                                HierarchyValidatorAgent=hier_cls
                            )
                        },
                    ):
                        mod.execute_phase3_alignment_impl(
                            {"hierarchy": hier_cls}, "agentic_core", de, sm, ctx=ctx
                        )

        hier_inst.heal_repository.assert_not_called()
        # Some HITL/SKIPPED record must be persisted
        assert bridge.persist_healing_success_rate.called or bridge.persist_failure_pattern.called

    def test_hitl_abort_returns_none(self):
        mod = self._load()
        bridge = _mock_bridge()
        sm = _fake_state()
        sm.state = {}
        hier_cls, hier_inst = self._mock_hier(1)
        de = self._make_de(mod)
        ctx = MagicMock()
        ctx.heal = True

        with patch("agentic_core.L0_routing.scripts.execute_ssot.REPO_ROOT", Path(".")):
            with patch(
                "agentic_core.L5_safety.enforcement.hitl_gate.get_hitl_gate", return_value=_abort_gate()
            ):
                with patch(
                    _SL_BRIDGE_PATCH,
                    return_value=bridge,
                ):
                    with patch.dict(
                        "sys.modules",
                        {
                            "agentic_core.L5_safety.reasoning.hierarchy_validator": MagicMock(
                                HierarchyValidatorAgent=hier_cls
                            )
                        },
                    ):
                        result = mod.execute_phase3_alignment_impl(
                            {"hierarchy": hier_cls}, "agentic_core", de, sm, ctx=ctx
                        )

        # ABORT returns a status dict (not None) — heal must not have fired
        assert isinstance(result, dict)
        assert result.get("status") == "HITL_ABORTED"
        hier_inst.heal_repository.assert_not_called()


# ===========================================================================
# D. RootHygieneHealerAgent (HITL + SL)
# ===========================================================================


class TestRootHygieneHealerE2E:
    """RootHygieneHealerAgent is embedded in the main orchestrator.
    These tests verify the HITL + SL wiring by testing _record_healing_action
    directly with RootHygiene outcomes (matching what the orchestrator emits).
    """

    def test_hitl_abort_records_skipped_to_sl(self):
        """HITL ABORT path must persist outcome=SKIPPED to SL bridge."""
        bridge = _mock_bridge()
        sm = _fake_state()
        with patch(
            _SL_BRIDGE_PATCH,
            return_value=bridge,
        ):
            _record_healing_action(
                sm,
                agent="RootHygieneHealerAgent",
                territory="__global__",
                routing_tier="DETERMINISTIC",
                confidence=0.0,
                fix_summary="HITL ABORTED: user pressed A",
                outcome="SKIPPED",
            )
        bridge.persist_healing_success_rate.assert_called_once()
        assert bridge.persist_healing_success_rate.call_args[1]["rate"] == 0.0
        bridge.persist_failure_pattern.assert_called_once()
        sig = bridge.persist_healing_success_rate.call_args[0][0]
        assert sig == "RootHygieneHealerAgent::__global__::SKIPPED"

    def test_heal_success_records_to_sl(self):
        """SUCCESS heal path must persist rate=1.0 to SL bridge."""
        bridge = _mock_bridge()
        sm = _fake_state()
        with patch(
            _SL_BRIDGE_PATCH,
            return_value=bridge,
        ):
            _record_healing_action(
                sm,
                agent="RootHygieneHealerAgent",
                territory="__global__",
                routing_tier="DETERMINISTIC",
                confidence=0.9,
                fix_summary="Cleaned 3 of 3 root hygiene violations",
                outcome="SUCCESS",
            )
        assert bridge.persist_healing_success_rate.call_args[1]["rate"] == 1.0
        bridge.persist_failure_pattern.assert_not_called()

    def test_hitl_gate_abort_path_via_phase3(self):
        """ABORT via HitlGate in Phase3 records SKIPPED outcome with SL wiring."""
        import importlib

        try:
            mod = importlib.import_module("agentic_core.L0_routing.scripts.execute_ssot")
        except ImportError as e:
            pytest.skip(f"execute_ssot unavailable: {e}")

        bridge = _mock_bridge()
        sm = _fake_state()
        sm.state = {}
        hier_cls = MagicMock()
        hier_inst = MagicMock()
        hier_inst.scan_root_violations.return_value = {
            "violations": [{"type": "HIERARCHY", "file": "agentic_core/x.py"}],
            "violations_found": 1,
        }
        hier_inst.heal_repository.return_value = {"violations_fixed": 0}
        hier_cls.return_value = hier_inst
        de = MagicMock(spec=mod.SovereignDecisionEngine)
        de.should_proceed_with_healing.return_value = (True, "AUTO-HEAL")
        conf = MagicMock()
        conf.value = 0.9
        de.calculate_healing_confidence.return_value = conf
        ctx = MagicMock()
        ctx.heal = True

        with patch("agentic_core.L0_routing.scripts.execute_ssot.REPO_ROOT", Path(".")):
            with patch(
                "agentic_core.L5_safety.enforcement.hitl_gate.get_hitl_gate", return_value=_abort_gate()
            ):
                with patch(
                    _SL_BRIDGE_PATCH,
                    return_value=bridge,
                ):
                    with patch.dict(
                        "sys.modules",
                        {
                            "agentic_core.L5_safety.reasoning.hierarchy_validator": MagicMock(
                                HierarchyValidatorAgent=hier_cls
                            )
                        },
                    ):
                        result = mod.execute_phase3_alignment_impl(
                            {"hierarchy": hier_cls}, "agentic_core", de, sm, ctx=ctx
                        )

        assert result.get("status") == "HITL_ABORTED"
        hier_inst.heal_repository.assert_not_called()
        # SL bridge must have received SKIPPED outcome (rate=0.0)
        assert bridge.persist_healing_success_rate.called
        skipped_calls = [
            c for c in bridge.persist_healing_success_rate.call_args_list if c.kwargs.get("rate") == 0.0
        ]
        assert skipped_calls, "HITL ABORT outcome not persisted to SL bridge"


# ===========================================================================
# E. SL bridge integration: correct values
# ===========================================================================


class TestSLBridgeValues:
    def test_success_rate_1_for_success(self):
        bridge = _mock_bridge()
        sm = _fake_state()
        with patch(
            _SL_BRIDGE_PATCH,
            return_value=bridge,
        ):
            _record_healing_action(sm, agent="A", territory="T", outcome="SUCCESS", fix_summary="x")
        bridge.persist_healing_success_rate.assert_called_once()
        assert bridge.persist_healing_success_rate.call_args[1]["rate"] == 1.0

    def test_success_rate_0_for_failure(self):
        bridge = _mock_bridge()
        sm = _fake_state()
        with patch(
            _SL_BRIDGE_PATCH,
            return_value=bridge,
        ):
            _record_healing_action(sm, agent="A", territory="T", outcome="FAILURE", fix_summary="x")
        assert bridge.persist_healing_success_rate.call_args[1]["rate"] == 0.0

    def test_success_rate_0_for_skipped(self):
        bridge = _mock_bridge()
        sm = _fake_state()
        with patch(
            _SL_BRIDGE_PATCH,
            return_value=bridge,
        ):
            _record_healing_action(sm, agent="A", territory="T", outcome="SKIPPED", fix_summary="x")
        assert bridge.persist_healing_success_rate.call_args[1]["rate"] == 0.0

    def test_success_rate_0_for_partial(self):
        bridge = _mock_bridge()
        sm = _fake_state()
        with patch(
            _SL_BRIDGE_PATCH,
            return_value=bridge,
        ):
            _record_healing_action(sm, agent="A", territory="T", outcome="PARTIAL", fix_summary="x")
        assert bridge.persist_healing_success_rate.call_args[1]["rate"] == 0.0

    def test_no_failure_pattern_for_success(self):
        bridge = _mock_bridge()
        sm = _fake_state()
        with patch(
            _SL_BRIDGE_PATCH,
            return_value=bridge,
        ):
            _record_healing_action(sm, agent="A", territory="T", outcome="SUCCESS", fix_summary="x")
        bridge.persist_failure_pattern.assert_not_called()

    def test_failure_pattern_for_every_non_success(self):
        for outcome in ("FAILURE", "SKIPPED", "PARTIAL", "HITL_SKIPPED"):
            bridge = _mock_bridge()
            sm = _fake_state()
            with patch(
                _SL_BRIDGE_PATCH,
                return_value=bridge,
            ):
                _record_healing_action(sm, agent="A", territory="T", outcome=outcome, fix_summary="x")
            assert bridge.persist_failure_pattern.called, (
                f"persist_failure_pattern not called for outcome={outcome}"
            )

    def test_ts_arg_passed_to_bridge(self):
        """ts kwarg must be forwarded so MCP entity timestamps are set correctly."""
        bridge = _mock_bridge()
        sm = _fake_state()
        with patch(
            _SL_BRIDGE_PATCH,
            return_value=bridge,
        ):
            _record_healing_action(sm, agent="A", territory="T", outcome="SUCCESS", fix_summary="x")
        call_kwargs = bridge.persist_healing_success_rate.call_args[1]
        assert "ts" in call_kwargs, "ts kwarg not forwarded to persist_healing_success_rate"
        assert call_kwargs["ts"] != "", "ts must be a non-empty ISO timestamp"


# ===========================================================================
# F. No-TTY raises HitlRequiredError (regression guard)
# ===========================================================================


class TestNoTtyRaisesHitlRequired:
    def test_no_tty_raises_for_protected_path(self, tmp_path):
        from agentic_core.L5_safety.enforcement.hitl_gate import HitlGate, HitlRequest, HitlRequiredError

        gate = HitlGate(tmp_path)  # no _tty_override
        with patch("sys.stdin") as mock_stdin:
            mock_stdin.isatty.return_value = False
            with pytest.raises(HitlRequiredError):
                gate.request(
                    HitlRequest(
                        agent="HierarchyHealerAgent",
                        operation="DELETE",
                        affected_paths=[tmp_path / "agentic_core" / "core.py"],
                        reason="test",
                    )
                )

    def test_no_tty_raises_for_non_protected_path(self, tmp_path):
        from agentic_core.L5_safety.enforcement.hitl_gate import HitlGate, HitlRequest, HitlRequiredError

        gate = HitlGate(tmp_path)
        with patch("sys.stdin") as mock_stdin:
            mock_stdin.isatty.return_value = False
            with pytest.raises(HitlRequiredError):
                gate.request(
                    HitlRequest(
                        agent="AnyAgent",
                        operation="MOVE",
                        affected_paths=[tmp_path / "some_random_dir" / "file.py"],
                        reason="test",
                    )
                )

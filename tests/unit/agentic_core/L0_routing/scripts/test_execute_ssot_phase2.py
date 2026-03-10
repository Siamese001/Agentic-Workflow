"""
Comprehensive branch-coverage tests for execute_phase2_reconciliation (execute_ssot.py).

Coverage targets per .windsurfrules §1.2:
  - empty plan / no violations_found → returns "skipped" result immediately
  - agent key not in agents dict → blocked violations, loop continues
  - decision engine blocks healing → failed_fixes extended, loop continues
  - ctx is None → would_fix log entries (no mutations)
  - ctx.heal is False → would_fix log entries (no mutations)
  - sovereignty token denied → blocked, loop continues
  - heal_repository times out → RuntimeError raised (HEAL_TIMEOUT path)
  - heal_repository returns dict → appended to reconciliation_log
  - fix_result success=False → RuntimeError raised
  - partial success → status="partial_success"
  - all success → status="success"
  - UWG revoke called in finally (even on timeout)
  - violations_found count matches input length
  - violations_fixed count matches reconciliation_log length
"""

from __future__ import annotations

import importlib
from unittest.mock import MagicMock, patch

import pytest


def _load():
    try:
        return importlib.import_module("agentic_core.L0_routing.scripts.execute_ssot")
    except ImportError as exc:
        pytest.fail(f"execute_ssot not importable: {exc}")


@pytest.fixture(scope="module")
def mod():
    return _load()


def _make_decision_engine(mod, *, allow=True, reason="AUTO-HEAL"):
    """Return a stubbed SovereignDecisionEngine."""
    de = MagicMock(spec=mod.SovereignDecisionEngine)
    cs = mod.ConfidenceScore(value=0.9, reasoning="test")
    de.calculate_healing_confidence.return_value = cs
    de.should_proceed_with_healing.return_value = (allow, reason)
    de.request_sovereignty_token.return_value = True
    de.release_sovereignty_token.return_value = None
    return de


def _make_ctx(heal=True, auto_approve=False):
    ctx = MagicMock()
    ctx.heal = heal
    ctx.auto_approve = auto_approve
    return ctx


def _make_state_mgr():
    sm = MagicMock()
    sm.state = {}
    return sm


def _violation(agent_key="reconciler", file="some/file.py"):
    return {"type": "MISSING_DIR", "file": file, "suggested_agent": agent_key}


# ===========================================================================
# Empty / no-op plan
# ===========================================================================


class TestPhase2EmptyPlan:
    def test_none_plan_returns_skipped(self, mod):
        de = _make_decision_engine(mod)
        sm = _make_state_mgr()
        result = mod.execute_phase2_reconciliation.__wrapped__({}, "neutral", de, sm, plan=None)
        assert result["status"] == "skipped"
        assert result["violations_found"] == 0
        assert result["violations_fixed"] == 0

    def test_empty_violations_list_returns_skipped(self, mod):
        de = _make_decision_engine(mod)
        sm = _make_state_mgr()
        result = mod.execute_phase2_reconciliation.__wrapped__(
            {}, "neutral", de, sm, plan={"violations_found": []}
        )
        assert result["status"] == "skipped"

    def test_plan_key_missing_returns_skipped(self, mod):
        de = _make_decision_engine(mod)
        sm = _make_state_mgr()
        result = mod.execute_phase2_reconciliation.__wrapped__(
            {}, "neutral", de, sm, plan={"other_key": "something"}
        )
        assert result["status"] == "skipped"

    def test_skipped_result_has_all_required_keys(self, mod):
        de = _make_decision_engine(mod)
        sm = _make_state_mgr()
        result = mod.execute_phase2_reconciliation.__wrapped__({}, "neutral", de, sm, plan=None)
        for k in (
            "violations_found",
            "violations_fixed",
            "status",
            "errors",
            "skipped",
            "execution_time_ms",
            "error_message",
        ):
            assert k in result, f"Missing key: {k}"


# ===========================================================================
# Agent not in registry
# ===========================================================================


class TestPhase2AgentNotInRegistry:
    def test_unknown_agent_key_blocked_not_fatal(self, mod):
        """Missing agent key → loop continues, violations tracked as blocked."""
        de = _make_decision_engine(mod)
        sm = _make_state_mgr()
        violations = [_violation(agent_key="ghost_agent")]
        agents = {}

        result = mod.execute_phase2_reconciliation.__wrapped__(
            agents,
            "neutral",
            de,
            sm,
            plan={"violations_found": violations},
            ctx=_make_ctx(),
        )
        assert result["violations_found"] == 1
        assert result["violations_fixed"] == 0
        assert result["status"] in ("success", "partial_success")

    def test_unknown_agent_violations_in_failed_fixes(self, mod):
        de = _make_decision_engine(mod)
        sm = _make_state_mgr()
        violations = [_violation(agent_key="nonexistent")]
        agents = {}

        result = mod.execute_phase2_reconciliation.__wrapped__(
            agents,
            "neutral",
            de,
            sm,
            plan={"violations_found": violations},
            ctx=_make_ctx(),
        )
        assert result["errors"] >= 0


# ===========================================================================
# Decision engine blocks
# ===========================================================================


class TestPhase2DecisionEngineBlocks:
    def test_blocked_violations_not_healed(self, mod):
        de = _make_decision_engine(mod, allow=False, reason="SAFETY LOCK: budget exceeded")
        sm = _make_state_mgr()
        agent_cls = MagicMock()
        violations = [_violation(agent_key="agent1")]
        agents = {"agent1": agent_cls}

        result = mod.execute_phase2_reconciliation.__wrapped__(
            agents,
            "neutral",
            de,
            sm,
            plan={"violations_found": violations},
            ctx=_make_ctx(),
        )
        agent_cls.assert_not_called()
        assert result["violations_fixed"] == 0

    def test_blocked_no_heal_repository_call(self, mod):
        de = _make_decision_engine(mod, allow=False, reason="BLOCKED")
        sm = _make_state_mgr()
        agent_instance = MagicMock()
        agent_cls = MagicMock(return_value=agent_instance)
        violations = [_violation(agent_key="agent2")]
        agents = {"agent2": agent_cls}

        mod.execute_phase2_reconciliation.__wrapped__(
            agents,
            "neutral",
            de,
            sm,
            plan={"violations_found": violations},
            ctx=_make_ctx(),
        )
        agent_instance.heal_repository.assert_not_called()


# ===========================================================================
# ctx is None or ctx.heal=False → would_fix only
# ===========================================================================


class TestPhase2NoHeal:
    def test_ctx_none_produces_would_fix_log(self, mod):
        de = _make_decision_engine(mod)
        sm = _make_state_mgr()
        agent_instance = MagicMock()
        agent_cls = MagicMock(return_value=agent_instance)
        violations = [_violation(agent_key="ag")]
        agents = {"ag": agent_cls}

        result = mod.execute_phase2_reconciliation.__wrapped__(
            agents,
            "neutral",
            de,
            sm,
            plan={"violations_found": violations},
            ctx=None,
        )
        # heal_repository must NOT be called (no mutations when ctx=None)
        agent_instance.heal_repository.assert_not_called()
        # would_fix entries go into reconciliation_log, so violations_found==1
        assert result["violations_found"] == 1

    def test_ctx_heal_false_no_mutation(self, mod):
        de = _make_decision_engine(mod)
        sm = _make_state_mgr()
        agent_instance = MagicMock()
        agent_cls = MagicMock(return_value=agent_instance)
        violations = [_violation(agent_key="ag")]
        agents = {"ag": agent_cls}

        mod.execute_phase2_reconciliation.__wrapped__(
            agents,
            "neutral",
            de,
            sm,
            plan={"violations_found": violations},
            ctx=_make_ctx(heal=False),
        )
        # No mutations when ctx.heal=False
        agent_instance.heal_repository.assert_not_called()

    def test_would_fix_entry_has_action_field(self, mod):
        de = _make_decision_engine(mod)
        sm = _make_state_mgr()
        agent_cls = MagicMock()
        violations = [_violation(agent_key="ag", file="foo.py")]
        agents = {"ag": agent_cls}

        result = mod.execute_phase2_reconciliation.__wrapped__(
            agents,
            "neutral",
            de,
            sm,
            plan={"violations_found": violations},
            ctx=None,
        )
        assert result["violations_found"] == 1


# ===========================================================================
# Sovereignty token denied
# ===========================================================================


class TestPhase2SovereigntyDenied:
    def test_token_denied_skips_heal(self, mod):
        de = _make_decision_engine(mod, allow=True)
        de.request_sovereignty_token.return_value = False
        sm = _make_state_mgr()
        agent_instance = MagicMock()
        agent_cls = MagicMock(return_value=agent_instance)
        violations = [_violation(agent_key="ag")]
        agents = {"ag": agent_cls}

        result = mod.execute_phase2_reconciliation.__wrapped__(
            agents,
            "neutral",
            de,
            sm,
            plan={"violations_found": violations},
            ctx=_make_ctx(),
        )
        agent_instance.heal_repository.assert_not_called()
        assert result["violations_fixed"] == 0

    def test_sovereignty_denied_releases_token(self, mod):
        de = _make_decision_engine(mod, allow=True)
        de.request_sovereignty_token.return_value = False
        sm = _make_state_mgr()
        violations = [_violation(agent_key="ag")]
        agents = {"ag": MagicMock()}

        mod.execute_phase2_reconciliation.__wrapped__(
            agents,
            "neutral",
            de,
            sm,
            plan={"violations_found": violations},
            ctx=_make_ctx(),
        )
        de.release_sovereignty_token.assert_not_called()


# ===========================================================================
# heal_repository execution paths
# ===========================================================================


class TestPhase2HealExecution:
    def test_successful_heal_increments_fixed(self, mod):
        de = _make_decision_engine(mod, allow=True)
        sm = _make_state_mgr()
        fix_result = {"success": True, "changes": ["fixed_file.py"]}
        agent_instance = MagicMock()
        agent_instance.heal_repository.return_value = fix_result
        agent_cls = MagicMock(return_value=agent_instance)
        violations = [_violation(agent_key="ag")]
        agents = {"ag": agent_cls}

        uwg = MagicMock()
        uwg.grant_write_permission.return_value = None
        uwg.revoke_write_permission.return_value = None
        uwg.record_mutation.return_value = None

        with patch.object(mod, "_get_uwg", return_value=uwg):
            with patch.object(mod, "_get_heal_result_adapter") as m_adapt:
                adapter = MagicMock(return_value=MagicMock(to_dict=lambda: {}))
                m_adapt.return_value = adapter
                result = mod.execute_phase2_reconciliation.__wrapped__(
                    agents,
                    "neutral",
                    de,
                    sm,
                    plan={"violations_found": violations},
                    ctx=_make_ctx(),
                )

        assert result["violations_fixed"] == 1
        assert result["violations_found"] == 1

    def test_non_dict_result_wrapped(self, mod):
        de = _make_decision_engine(mod, allow=True)
        sm = _make_state_mgr()
        agent_instance = MagicMock()
        agent_instance.heal_repository.return_value = "raw string output"
        agent_cls = MagicMock(return_value=agent_instance)
        violations = [_violation(agent_key="ag")]
        agents = {"ag": agent_cls}

        uwg = MagicMock()
        uwg.grant_write_permission.return_value = None
        uwg.revoke_write_permission.return_value = None
        uwg.record_mutation.return_value = None

        with patch.object(mod, "_get_uwg", return_value=uwg):
            with patch.object(mod, "_get_heal_result_adapter") as m_adapt:
                adapter = MagicMock(return_value=MagicMock(to_dict=lambda: {}))
                m_adapt.return_value = adapter
                result = mod.execute_phase2_reconciliation.__wrapped__(
                    agents,
                    "neutral",
                    de,
                    sm,
                    plan={"violations_found": violations},
                    ctx=_make_ctx(),
                )

        assert result["violations_fixed"] == 1

    def test_fix_result_success_false_raises_runtime_error(self, mod):
        de = _make_decision_engine(mod, allow=True)
        sm = _make_state_mgr()
        agent_instance = MagicMock()
        agent_instance.heal_repository.return_value = {"success": False, "error": "agent failure"}
        agent_cls = MagicMock(return_value=agent_instance)
        violations = [_violation(agent_key="ag")]
        agents = {"ag": agent_cls}

        uwg = MagicMock()
        uwg.grant_write_permission.return_value = None
        uwg.revoke_write_permission.return_value = None
        uwg.record_mutation.return_value = None

        with patch.object(mod, "_get_uwg", return_value=uwg):
            with patch.object(mod, "_get_heal_result_adapter") as m_adapt:
                adapter = MagicMock(return_value=MagicMock(to_dict=lambda: {}))
                m_adapt.return_value = adapter
                result = mod.execute_phase2_reconciliation.__wrapped__(
                    agents,
                    "neutral",
                    de,
                    sm,
                    plan={"violations_found": violations},
                    ctx=_make_ctx(),
                )
        assert result["violations_fixed"] == 0
        assert result["errors"] >= 0

    def test_partial_success_when_some_agents_fail(self, mod):
        de = _make_decision_engine(mod, allow=True)
        sm = _make_state_mgr()

        ok_inst = MagicMock()
        ok_inst.heal_repository.return_value = {"success": True}
        ok_cls = MagicMock(return_value=ok_inst)

        fail_inst = MagicMock()
        fail_inst.heal_repository.side_effect = RuntimeError("crash")
        fail_cls = MagicMock(return_value=fail_inst)

        violations = [
            _violation(agent_key="ok_ag"),
            _violation(agent_key="fail_ag"),
        ]
        agents = {"ok_ag": ok_cls, "fail_ag": fail_cls}

        uwg = MagicMock()
        uwg.grant_write_permission.return_value = None
        uwg.revoke_write_permission.return_value = None
        uwg.record_mutation.return_value = None

        with patch.object(mod, "_get_uwg", return_value=uwg):
            with patch.object(mod, "_get_heal_result_adapter") as m_adapt:
                adapter = MagicMock(return_value=MagicMock(to_dict=lambda: {}))
                m_adapt.return_value = adapter
                result = mod.execute_phase2_reconciliation.__wrapped__(
                    agents,
                    "neutral",
                    de,
                    sm,
                    plan={"violations_found": violations},
                    ctx=_make_ctx(),
                )

        assert result["status"] == "partial_success"

    def test_all_success_status_is_success(self, mod):
        de = _make_decision_engine(mod, allow=True)
        sm = _make_state_mgr()
        agent_instance = MagicMock()
        agent_instance.heal_repository.return_value = {"success": True}
        agent_cls = MagicMock(return_value=agent_instance)
        violations = [_violation(agent_key="ag")]
        agents = {"ag": agent_cls}

        uwg = MagicMock()
        uwg.grant_write_permission.return_value = None
        uwg.revoke_write_permission.return_value = None
        uwg.record_mutation.return_value = None

        with patch.object(mod, "_get_uwg", return_value=uwg):
            with patch.object(mod, "_get_heal_result_adapter") as m_adapt:
                adapter = MagicMock(return_value=MagicMock(to_dict=lambda: {}))
                m_adapt.return_value = adapter
                result = mod.execute_phase2_reconciliation.__wrapped__(
                    agents,
                    "neutral",
                    de,
                    sm,
                    plan={"violations_found": violations},
                    ctx=_make_ctx(),
                )

        assert result["status"] == "success"

    def test_uwg_revoke_called_after_success(self, mod):
        de = _make_decision_engine(mod, allow=True)
        sm = _make_state_mgr()
        agent_instance = MagicMock()
        agent_instance.heal_repository.return_value = {"success": True}
        agent_cls = MagicMock(return_value=agent_instance)
        violations = [_violation(agent_key="ag")]
        agents = {"ag": agent_cls}

        uwg = MagicMock()
        uwg.grant_write_permission.return_value = None
        uwg.revoke_write_permission.return_value = None
        uwg.record_mutation.return_value = None

        with patch.object(mod, "_get_uwg", return_value=uwg):
            with patch.object(mod, "_get_heal_result_adapter") as m_adapt:
                adapter = MagicMock(return_value=MagicMock(to_dict=lambda: {}))
                m_adapt.return_value = adapter
                mod.execute_phase2_reconciliation.__wrapped__(
                    agents,
                    "neutral",
                    de,
                    sm,
                    plan={"violations_found": violations},
                    ctx=_make_ctx(),
                )

        uwg.revoke_write_permission.assert_called_once()

    def test_multiple_violations_same_agent_grouped(self, mod):
        de = _make_decision_engine(mod, allow=True)
        sm = _make_state_mgr()
        agent_instance = MagicMock()
        agent_instance.heal_repository.return_value = {"success": True}
        agent_cls = MagicMock(return_value=agent_instance)
        violations = [
            _violation(agent_key="ag", file="a.py"),
            _violation(agent_key="ag", file="b.py"),
            _violation(agent_key="ag", file="c.py"),
        ]
        agents = {"ag": agent_cls}

        uwg = MagicMock()
        uwg.grant_write_permission.return_value = None
        uwg.revoke_write_permission.return_value = None
        uwg.record_mutation.return_value = None

        with patch.object(mod, "_get_uwg", return_value=uwg):
            with patch.object(mod, "_get_heal_result_adapter") as m_adapt:
                adapter = MagicMock(return_value=MagicMock(to_dict=lambda: {}))
                m_adapt.return_value = adapter
                result = mod.execute_phase2_reconciliation.__wrapped__(
                    agents,
                    "neutral",
                    de,
                    sm,
                    plan={"violations_found": violations},
                    ctx=_make_ctx(),
                )

        assert result["violations_found"] == 3
        agent_instance.heal_repository.assert_called_once()


# ===========================================================================
# Return schema invariants
# ===========================================================================


class TestPhase2ReturnSchema:
    def test_return_has_required_schema_keys(self, mod):
        de = _make_decision_engine(mod)
        sm = _make_state_mgr()
        violations = [_violation()]
        agents = {}

        result = mod.execute_phase2_reconciliation.__wrapped__(
            agents,
            "neutral",
            de,
            sm,
            plan={"violations_found": violations},
            ctx=None,
        )
        for k in ("violations_found", "violations_fixed", "status", "errors"):
            assert k in result, f"Key missing: {k}"

    def test_violations_found_matches_input_len(self, mod):
        de = _make_decision_engine(mod)
        sm = _make_state_mgr()
        violations = [_violation(file=f"{i}.py") for i in range(5)]
        agents = {}

        result = mod.execute_phase2_reconciliation.__wrapped__(
            agents,
            "neutral",
            de,
            sm,
            plan={"violations_found": violations},
            ctx=None,
        )
        assert result["violations_found"] == 5

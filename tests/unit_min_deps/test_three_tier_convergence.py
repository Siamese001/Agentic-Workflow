"""Three-Tier Convergence Tests.

Validates:
  Tier 1 — UWG grant/revoke/record lifecycle round-trips.
  Tier 2 — Threshold constants from healing_tier_config match execute_ssot defaults.
  Tier 3 — adapt_heal_result() produces valid HealCheckResult from every input shape,
            including absolute-path sanitisation.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_core.L2_execution.heal_result_adapter import adapt_heal_result
from agentic_core.L2_execution.types.heal_contract_types import HealCheckResult, HealStatus


# ---------------------------------------------------------------------------
# Tier 1 — UniversalWriteGateway lifecycle
# ---------------------------------------------------------------------------


class TestTier1UWG:
    """UWG permission + ledger lifecycle."""

    def _fresh_uwg(self):
        from agentic_core.L2_execution.UniversalWriteGateway import UniversalWriteGateway

        return UniversalWriteGateway()

    def test_grant_then_revoke_permission(self) -> None:
        uwg = self._fresh_uwg()
        # UWG stores exact normalized key; check_write_permission looks up that exact key.
        test_path = "agentic_core/L2_execution/"
        uwg.grant_write_permission(test_path)
        assert uwg.check_write_permission(test_path)
        uwg.revoke_write_permission(test_path)
        assert not uwg.check_write_permission(test_path)

    def test_record_mutation_appends_to_ledger(self) -> None:
        uwg = self._fresh_uwg()
        uwg.grant_write_permission("apps_rg/")
        uwg.record_mutation(path="apps_rg/engines/foo.py", operation="heal_repository", permitted=True)
        ledger = uwg.get_mutation_ledger()
        assert len(ledger) == 1
        assert ledger[0].operation == "heal_repository"
        assert ledger[0].permitted is True

    def test_revoke_without_prior_grant_is_safe(self) -> None:
        """Revoking a path that was never granted must not raise."""
        uwg = self._fresh_uwg()
        uwg.revoke_write_permission("nonexistent/territory/")  # must not raise

    def test_replay_mode_skips_permission_changes(self) -> None:
        from agentic_core.L2_execution.UniversalWriteGateway import UniversalWriteGateway

        uwg = UniversalWriteGateway(replay_mode=True)
        uwg.grant_write_permission("apps_rg/")  # no-op in replay mode
        # In replay mode all paths are allowed
        assert uwg.check_write_permission("apps_rg/engines/foo.py")

    def test_get_write_gateway_returns_uwg_instance(self) -> None:
        from agentic_core.L2_execution.UniversalWriteGateway import UniversalWriteGateway
        from agentic_core.interfaces.write_gateway import get_write_gateway

        assert isinstance(get_write_gateway(), UniversalWriteGateway)


# ---------------------------------------------------------------------------
# Tier 2 — Threshold SSOT consistency
# ---------------------------------------------------------------------------


class TestTier2Thresholds:
    """Canonical thresholds in healing_tier_config must match execute_ssot defaults."""

    def test_threshold_values_are_canonical(self) -> None:
        from agentic_core.L2_execution.healers.healing_tier_config import (
            HEALING_CONFIDENCE_X,
            HEALING_CONFIDENCE_Y,
        )

        assert HEALING_CONFIDENCE_X == 0.75, "X threshold drifted from 0.75"
        assert HEALING_CONFIDENCE_Y == 0.40, "Y threshold drifted from 0.40"

    def test_thresholds_are_ordered(self) -> None:
        from agentic_core.L2_execution.healers.healing_tier_config import (
            HEALING_CONFIDENCE_X,
            HEALING_CONFIDENCE_Y,
        )

        assert HEALING_CONFIDENCE_Y < HEALING_CONFIDENCE_X
        assert 0.0 <= HEALING_CONFIDENCE_Y < HEALING_CONFIDENCE_X <= 1.0

    def test_healing_tier_config_validates_on_load(self) -> None:
        from agentic_core.L2_execution.healers.healing_tier_config import (
            load_default_healing_tier_config,
        )

        cfg = load_default_healing_tier_config()
        assert cfg.heal_confidence_x == 0.75
        assert cfg.heal_confidence_y == 0.40


# ---------------------------------------------------------------------------
# Tier 3 — adapt_heal_result contract coverage
# ---------------------------------------------------------------------------


REPO_ROOT = Path(__file__).resolve().parents[2]  # c:\Git\Agentic-Workflow


class TestTier3Adapter:
    """adapt_heal_result() produces a valid HealCheckResult for every input shape."""

    # --- status extraction ---

    def test_success_bool_true(self) -> None:
        hcr = adapt_heal_result("AgentA", {"success": True}, repo_root=REPO_ROOT)
        assert hcr.status == HealStatus.HEALED

    def test_success_bool_false(self) -> None:
        hcr = adapt_heal_result("AgentA", {"success": False}, repo_root=REPO_ROOT)
        assert hcr.status == HealStatus.FAILED

    def test_explicit_status_healed(self) -> None:
        hcr = adapt_heal_result("AgentA", {"status": "HEALED"}, repo_root=REPO_ROOT)
        assert hcr.status == HealStatus.HEALED

    def test_explicit_status_partial(self) -> None:
        hcr = adapt_heal_result("AgentA", {"status": "PARTIAL"}, repo_root=REPO_ROOT)
        assert hcr.status == HealStatus.PARTIAL

    def test_explicit_status_skipped(self) -> None:
        hcr = adapt_heal_result("AgentA", {"status": "SKIPPED"}, repo_root=REPO_ROOT)
        assert hcr.status == HealStatus.SKIPPED

    def test_status_success_alias(self) -> None:
        hcr = adapt_heal_result("AgentA", {"status": "SUCCESS"}, repo_root=REPO_ROOT)
        assert hcr.status == HealStatus.HEALED

    def test_error_key_implies_failed(self) -> None:
        hcr = adapt_heal_result("AgentA", {"error": "boom"}, repo_root=REPO_ROOT)
        assert hcr.status == HealStatus.FAILED

    def test_files_healed_zero_implies_skipped(self) -> None:
        hcr = adapt_heal_result("AgentA", {"files_healed": 0}, repo_root=REPO_ROOT)
        assert hcr.status == HealStatus.SKIPPED

    def test_files_healed_positive_implies_healed(self) -> None:
        hcr = adapt_heal_result("AgentA", {"files_healed": 3}, repo_root=REPO_ROOT)
        assert hcr.status == HealStatus.HEALED

    # --- string / None normalisation ---

    def test_string_input_stored_in_changes_made(self) -> None:
        hcr = adapt_heal_result("AgentA", "Fixed 3 files", repo_root=REPO_ROOT)
        assert any("Fixed 3 files" in c for c in hcr.changes_made)

    def test_none_input_stored_in_changes_made(self) -> None:
        hcr = adapt_heal_result("AgentA", None, repo_root=REPO_ROOT)
        assert any("No output returned" in c for c in hcr.changes_made)

    # --- absolute path sanitisation (critical contract requirement) ---

    def test_absolute_windows_path_sanitised(self) -> None:
        """HealCheckResult rejects absolute paths — adapter must convert them."""
        raw = {"success": True, "files_healed": [r"C:\Git\Agentic-Workflow\agentic_core\foo.py"]}
        hcr = adapt_heal_result("AgentA", raw, repo_root=REPO_ROOT)
        for change in hcr.changes_made:
            assert not change.startswith("C:"), f"Absolute path leaked: {change}"
            assert not change.startswith("/"), f"Absolute path leaked: {change}"

    def test_absolute_posix_path_sanitised(self) -> None:
        raw = {"success": True, "changes_made": ["/home/user/repo/agentic_core/foo.py"]}
        hcr = adapt_heal_result("AgentA", raw, repo_root=REPO_ROOT)
        for change in hcr.changes_made:
            assert not change.startswith("/"), f"Absolute path leaked: {change}"

    def test_relative_paths_pass_through(self) -> None:
        raw = {"success": True, "files_healed": ["agentic_core/foo.py", "tests/bar.py"]}
        hcr = adapt_heal_result("AgentA", raw, repo_root=REPO_ROOT)
        assert "agentic_core/foo.py" in hcr.changes_made
        assert "tests/bar.py" in hcr.changes_made

    # --- return type is always HealCheckResult ---

    def test_return_type_is_heal_check_result(self) -> None:
        hcr = adapt_heal_result("AgentA", {}, repo_root=REPO_ROOT)
        assert isinstance(hcr, HealCheckResult)

    def test_check_id_matches_agent_name(self) -> None:
        hcr = adapt_heal_result("MySpecialAgent", {}, repo_root=REPO_ROOT)
        assert hcr.check_id == "MySpecialAgent"

    def test_empty_agent_name_raises(self) -> None:
        with pytest.raises(ValueError, match="agent_name"):
            adapt_heal_result("", {}, repo_root=REPO_ROOT)

    # --- escalation logic ---

    def test_partial_status_triggers_escalation(self) -> None:
        hcr = adapt_heal_result("AgentA", {"status": "PARTIAL"}, repo_root=REPO_ROOT)
        assert hcr.needs_llm_escalation is True

    def test_complex_error_triggers_escalation(self) -> None:
        hcr = adapt_heal_result("AgentA", {"success": False, "error": "complex rewrite required"}, repo_root=REPO_ROOT)
        assert hcr.needs_llm_escalation is True

    def test_simple_failure_does_not_trigger_escalation(self) -> None:
        hcr = adapt_heal_result("AgentA", {"success": False, "error": "missing import"}, repo_root=REPO_ROOT)
        assert hcr.needs_llm_escalation is False

    def test_large_change_set_triggers_escalation(self) -> None:
        raw = {"success": True, "changes_made": [f"file{i}.py" for i in range(12)]}
        hcr = adapt_heal_result("AgentA", raw, repo_root=REPO_ROOT)
        assert hcr.needs_llm_escalation is True

    def test_explicit_escalation_flag_respected(self) -> None:
        hcr = adapt_heal_result("AgentA", {"needs_llm_escalation": True}, repo_root=REPO_ROOT)
        assert hcr.needs_llm_escalation is True

    def test_explicit_no_escalation_flag_respected(self) -> None:
        hcr = adapt_heal_result("AgentA", {"status": "PARTIAL", "needs_llm_escalation": False}, repo_root=REPO_ROOT)
        assert hcr.needs_llm_escalation is False

    # --- escalation hint ---

    def test_escalation_hint_present_when_needed(self) -> None:
        raw = {"status": "PARTIAL", "failure_type": "LAYER_VIOLATION", "blast_radius": 0.9}
        hcr = adapt_heal_result("AgentA", raw, repo_root=REPO_ROOT)
        assert hcr.escalation_hint is not None
        assert "failure_type=LAYER_VIOLATION" in hcr.escalation_hint
        assert "blast_radius=0.9" in hcr.escalation_hint

    def test_escalation_hint_absent_when_not_needed(self) -> None:
        hcr = adapt_heal_result("AgentA", {"success": True, "files_healed": 1}, repo_root=REPO_ROOT)
        assert hcr.escalation_hint is None

    # --- to_dict round-trip ---

    def test_to_dict_round_trip(self) -> None:
        raw = {"success": True, "files_healed": ["agentic_core/foo.py"]}
        hcr = adapt_heal_result("AgentA", raw, repo_root=REPO_ROOT)
        d = hcr.to_dict()
        assert d["check_id"] == "AgentA"
        assert d["status"] == "HEALED"
        assert isinstance(d["changes_made"], list)
        assert d["needs_llm_escalation"] is False

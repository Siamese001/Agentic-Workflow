"""Rigorous behavioural tests for HitlGate.

Mandatory HITL contract under test:
- HITL is MANDATORY — no silent skip, no non-interactive bypass
- No TTY → HitlRequiredError raised for ALL paths (protected or not)
- Interactive TTY → prompt with [Y/N/S/A] options, always
- SOVEREIGN_AUTO_APPROVE / ARCHIVE_BATCH_ACCEPT are IGNORED by the gate
- Protected path detection (HITL_PROTECTED_PATHS) drives the prompt label only
- Each user input (Y/N/S/A/invalid) maps to correct HitlChoice
- EOFError / KeyboardInterrupt during input → NO (deny)
- clear_gate_cache() isolates singleton tests

Test helpers use _tty_override=True to simulate interactive terminal
without needing a real TTY in the CI/pytest environment.
"""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from agentic_core.L5_safety.enforcement.hitl_gate import (
    HITL_PROTECTED_PATHS,
    HitlChoice,
    HitlGate,
    HitlRequest,
    HitlRequiredError,
    clear_gate_cache,
    get_hitl_gate,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_hitl_gate")
_emit_applies_guardrail("p0", "test_hitl_gate", "p0_governance")
_emit_reads_policy_state("p0", "test_hitl_gate", "policy_binding")
_emit_snapshots_state("p0", "test_hitl_gate", "state_snapshot")
emit_replay_key("p0", "test_hitl_gate")
emit_determinism_digest("p0", "test_hitl_gate")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_hitl_gate", "execution_auth")
_emit_validates_capability("p2", "test_hitl_gate", "capability_check")
_emit_routes_to_capability("p2", "test_hitl_gate", "capability_route")
_emit_writes_via_uwg("p2", "test_hitl_gate", "uwg_write")
_emit_blocks_direct_write("p2", "test_hitl_gate", "direct_write_block")
_emit_records_tool_invocation("p2", "test_hitl_gate", "tool_invocation")
_emit_captures_execution_output("p2", "test_hitl_gate", "exec_output")
_emit_dispatches_agent("p3", "test_hitl_gate", "agent_dispatch")
_emit_coordinates_agents("p3", "test_hitl_gate", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_hitl_gate", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_hitl_gate", "healing_outcome")
_emit_escalates_failure("p3", "test_hitl_gate", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_hitl_gate", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_hitl_gate", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_hitl_gate", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_hitl_gate", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_hitl_gate", "eval_metric")
_emit_stores_embedding("p4", "test_hitl_gate", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_hitl_gate", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_hitl_gate", "exec_snapshot_link")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_req(
    paths: list[Path],
    agent: str = "TestAgent",
    operation: str = "ARCHIVE",
    reason: str = "test reason",
) -> HitlRequest:
    return HitlRequest(
        agent=agent,
        operation=operation,
        affected_paths=paths,
        reason=reason,
    )


def _interactive_gate(repo_root: Path, user_input: str) -> HitlGate:
    """Gate with _tty_override=True so tests don't need a real TTY."""
    return HitlGate(repo_root, input_fn=lambda _: user_input, _tty_override=True)


# ---------------------------------------------------------------------------
# HITL_PROTECTED_PATHS constant
# ---------------------------------------------------------------------------


class TestHitlProtectedPaths:
    def test_key_paths_present(self):
        for path in ("agentic_core", "scripts", "mixins", "runtime", "tests"):
            assert path in HITL_PROTECTED_PATHS, f"{path!r} must be in HITL_PROTECTED_PATHS"

    def test_is_frozenset(self):
        assert isinstance(HITL_PROTECTED_PATHS, frozenset)


# ---------------------------------------------------------------------------
# Mandatory HITL — no TTY raises HitlRequiredError
# ---------------------------------------------------------------------------


class TestMandatoryHitl:
    """pytest runs without a TTY; every request must raise HitlRequiredError
    unless _tty_override=True is used."""

    def test_no_tty_protected_raises(self, tmp_path):
        gate = HitlGate(tmp_path)  # no _tty_override, no real TTY in pytest
        req = _make_req([tmp_path / "agentic_core" / "L5_safety" / "foo.py"])
        with pytest.raises(HitlRequiredError) as exc_info:
            gate.request(req)
        assert "HITL REQUIRED" in str(exc_info.value)
        assert "No TTY" in str(exc_info.value)

    def test_no_tty_nonprotected_also_raises(self, tmp_path):
        """Even non-protected paths require human approval — no silent skip."""
        gate = HitlGate(tmp_path)
        req = _make_req([tmp_path / "logs" / "run.log"])
        with pytest.raises(HitlRequiredError) as exc_info:
            gate.request(req)
        assert "HITL REQUIRED" in str(exc_info.value)

    def test_no_tty_error_names_agent(self, tmp_path):
        gate = HitlGate(tmp_path)
        req = _make_req([tmp_path / "agentic_core" / "foo.py"], agent="HierarchyHealerAgent")
        with pytest.raises(HitlRequiredError) as exc_info:
            gate.request(req)
        assert "HierarchyHealerAgent" in str(exc_info.value)

    def test_no_tty_error_names_operation(self, tmp_path):
        gate = HitlGate(tmp_path)
        req = _make_req([tmp_path / "mixins" / "foo.py"], operation="DELETE")
        with pytest.raises(HitlRequiredError) as exc_info:
            gate.request(req)
        assert "DELETE" in str(exc_info.value)

    def test_sovereign_auto_approve_does_not_bypass(self, tmp_path):
        """SOVEREIGN_AUTO_APPROVE=1 must NOT suppress HitlRequiredError."""
        with patch.dict(os.environ, {"SOVEREIGN_AUTO_APPROVE": "1"}):
            gate = HitlGate(tmp_path)
            req = _make_req([tmp_path / "agentic_core" / "critical.py"])
            with pytest.raises(HitlRequiredError):
                gate.request(req)

    def test_archive_batch_accept_does_not_bypass(self, tmp_path):
        """ARCHIVE_BATCH_ACCEPT=1 must NOT suppress HitlRequiredError."""
        with patch.dict(os.environ, {"ARCHIVE_BATCH_ACCEPT": "1"}):
            gate = HitlGate(tmp_path)
            req = _make_req([tmp_path / "mixins" / "some_mixin.py"])
            with pytest.raises(HitlRequiredError):
                gate.request(req)

    def test_archive_batch_accept_does_not_bypass_nonprotected(self, tmp_path):
        """Even non-protected paths must raise — batch env is ignored."""
        with patch.dict(os.environ, {"ARCHIVE_BATCH_ACCEPT": "1"}):
            gate = HitlGate(tmp_path)
            req = _make_req([tmp_path / "artifacts" / "output.json"])
            with pytest.raises(HitlRequiredError):
                gate.request(req)


# ---------------------------------------------------------------------------
# Protected-path detection (label only — does not change raise vs prompt)
# ---------------------------------------------------------------------------


class TestProtectedPathDetection:
    """With _tty_override=True, prompt fires. Check protected flag in decision."""

    def test_agentic_core_flagged_protected(self, tmp_path):
        gate = _interactive_gate(tmp_path, "N")
        req = _make_req([tmp_path / "agentic_core" / "some_file.py"])
        decision = gate.request(req)
        assert decision.protected is True

    def test_mixins_flagged_protected(self, tmp_path):
        gate = _interactive_gate(tmp_path, "N")
        decision = gate.request(_make_req([tmp_path / "mixins" / "base_mixin.py"]))
        assert decision.protected is True

    def test_runtime_flagged_protected(self, tmp_path):
        gate = _interactive_gate(tmp_path, "N")
        decision = gate.request(_make_req([tmp_path / "runtime" / "worker.py"]))
        assert decision.protected is True

    def test_scripts_flagged_protected(self, tmp_path):
        gate = _interactive_gate(tmp_path, "N")
        decision = gate.request(_make_req([tmp_path / "scripts" / "run_thing.py"]))
        assert decision.protected is True

    def test_non_protected_path_not_flagged(self, tmp_path):
        gate = _interactive_gate(tmp_path, "Y")
        decision = gate.request(_make_req([tmp_path / "some_random_dir" / "file.py"]))
        assert decision.protected is False

    def test_path_outside_repo_root_not_flagged(self, tmp_path):
        gate = _interactive_gate(tmp_path, "Y")
        req = _make_req([Path("/completely/different/path/file.py")])
        decision = gate.request(req)
        assert decision.protected is False


# ---------------------------------------------------------------------------
# Interactive prompt — option display and input mapping
# ---------------------------------------------------------------------------


class TestInteractivePrompt:
    """All tests use _tty_override=True to simulate interactive terminal."""

    def test_y_choice_returns_yes(self, tmp_path):
        decision = _interactive_gate(tmp_path, "Y").request(
            _make_req([tmp_path / "agentic_core" / "file.py"])
        )
        assert decision.choice == HitlChoice.YES

    def test_n_choice_returns_no(self, tmp_path):
        decision = _interactive_gate(tmp_path, "N").request(
            _make_req([tmp_path / "agentic_core" / "file.py"])
        )
        assert decision.choice == HitlChoice.NO

    def test_s_choice_returns_skip(self, tmp_path):
        decision = _interactive_gate(tmp_path, "S").request(
            _make_req([tmp_path / "agentic_core" / "file.py"])
        )
        assert decision.choice == HitlChoice.SKIP

    def test_a_choice_returns_abort(self, tmp_path):
        decision = _interactive_gate(tmp_path, "A").request(
            _make_req([tmp_path / "agentic_core" / "file.py"])
        )
        assert decision.choice == HitlChoice.ABORT

    def test_invalid_input_defaults_to_no(self, tmp_path):
        decision = _interactive_gate(tmp_path, "X").request(
            _make_req([tmp_path / "agentic_core" / "file.py"])
        )
        assert decision.choice == HitlChoice.NO

    def test_lowercase_y_accepted(self, tmp_path):
        decision = _interactive_gate(tmp_path, "y").request(
            _make_req([tmp_path / "agentic_core" / "file.py"])
        )
        assert decision.choice == HitlChoice.YES

    def test_prompt_shows_all_four_options(self, tmp_path, capsys):
        _interactive_gate(tmp_path, "N").request(_make_req([tmp_path / "agentic_core" / "file.py"]))
        captured = capsys.readouterr()
        assert "[Y]" in captured.out, "Option Y must appear in prompt"
        assert "[N]" in captured.out, "Option N must appear in prompt"
        assert "[S]" in captured.out, "Option S must appear in prompt"
        assert "[A]" in captured.out, "Option A must appear in prompt"

    def test_prompt_shows_affected_paths(self, tmp_path, capsys):
        test_path = tmp_path / "agentic_core" / "important_mixin.py"
        _interactive_gate(tmp_path, "N").request(_make_req([test_path]))
        captured = capsys.readouterr()
        assert "important_mixin.py" in captured.out, "Affected file name must appear in prompt"

    def test_eoferror_defaults_to_no(self, tmp_path):
        gate = HitlGate(tmp_path, _tty_override=True)
        gate._input_fn = lambda _: (_ for _ in ()).throw(EOFError())
        decision = gate.request(_make_req([tmp_path / "agentic_core" / "file.py"]))
        assert decision.choice == HitlChoice.NO

    def test_keyboardinterrupt_defaults_to_no(self, tmp_path):
        gate = HitlGate(tmp_path, _tty_override=True)
        gate._input_fn = lambda _: (_ for _ in ()).throw(KeyboardInterrupt())
        decision = gate.request(_make_req([tmp_path / "agentic_core" / "file.py"]))
        assert decision.choice == HitlChoice.NO

    def test_protected_label_shown_in_prompt(self, tmp_path, capsys):
        _interactive_gate(tmp_path, "N").request(_make_req([tmp_path / "agentic_core" / "file.py"]))
        captured = capsys.readouterr()
        assert "PROTECTED" in captured.out, "Protected path label must appear in prompt"

    def test_non_protected_label_shown_in_prompt(self, tmp_path, capsys):
        _interactive_gate(tmp_path, "N").request(_make_req([tmp_path / "logs" / "file.log"]))
        captured = capsys.readouterr()
        assert "STANDARD" in captured.out, "Standard path label must appear for non-protected prompt"


# ---------------------------------------------------------------------------
# Batch count
# ---------------------------------------------------------------------------


class TestBatchCount:
    def test_batch_count_matches_input(self, tmp_path):
        paths = [tmp_path / "logs" / f"file{i}.log" for i in range(5)]
        gate = _interactive_gate(tmp_path, "Y")
        decision = gate.request(_make_req(paths))
        assert decision.batch_count == 5

    def test_batch_count_no_tty_in_error(self, tmp_path):
        paths = [tmp_path / "agentic_core" / f"f{i}.py" for i in range(3)]
        gate = HitlGate(tmp_path)
        with pytest.raises(HitlRequiredError) as exc_info:
            gate.request(_make_req(paths))
        assert "3 file(s)" in str(exc_info.value)


# ---------------------------------------------------------------------------
# Singleton cache
# ---------------------------------------------------------------------------


class TestSingletonCache:
    def setup_method(self):
        clear_gate_cache()

    def test_get_hitl_gate_returns_same_instance(self, tmp_path):
        g1 = get_hitl_gate(tmp_path)
        g2 = get_hitl_gate(tmp_path)
        assert g1 is g2

    def test_clear_gate_cache_resets_singleton(self, tmp_path):
        g1 = get_hitl_gate(tmp_path)
        clear_gate_cache()
        g2 = get_hitl_gate(tmp_path)
        assert g1 is not g2


# ---------------------------------------------------------------------------
# Integration: call-site contract — HierarchyHealerAgent must be gated
# ---------------------------------------------------------------------------


class TestCallSiteContract:
    """Verify _ssot_phases.py and execute_ssot.py wire the HITL gate."""

    def test_ssot_phases_imports_hitl_gate(self):
        src = Path("agentic_core/L0_routing/scripts/_ssot_phases.py").read_text(encoding="utf-8")
        assert "hitl_gate" in src, "_ssot_phases.py must import hitl_gate"
        assert "HitlRequest" in src, "_ssot_phases.py must use HitlRequest"
        assert "HitlChoice" in src, "_ssot_phases.py must check HitlChoice"

    def test_execute_ssot_imports_hitl_gate_for_hierarchy(self):
        src = Path("agentic_core/L0_routing/scripts/execute_ssot.py").read_text(encoding="utf-8")
        assert "hitl_gate" in src, "execute_ssot.py must import hitl_gate"

    def test_execute_ssot_imports_hitl_gate_for_root_hygiene(self):
        src = Path("agentic_core/L0_routing/scripts/execute_ssot.py").read_text(encoding="utf-8")
        hygiene_block_start = src.find("RootHygieneHealerAgent")
        hitl_in_hygiene = src.find("hitl_gate", hygiene_block_start)
        assert hitl_in_hygiene != -1, "RootHygieneHealerAgent call site must use hitl_gate"

    def test_no_auto_approve_in_hitl_gate(self):
        """The gate must not honour SOVEREIGN_AUTO_APPROVE or ARCHIVE_BATCH_ACCEPT."""
        src = Path("agentic_core/L5_safety/enforcement/hitl_gate.py").read_text(encoding="utf-8")
        # Strip the module docstring before checking — the names may appear there
        # as documentation of what is ignored.  Only the code body must not use them.
        code_body = src.split('"""', 2)[-1] if src.count('"""') >= 2 else src
        assert 'os.environ.get("SOVEREIGN_AUTO_APPROVE' not in code_body, (
            "hitl_gate.py code must not read SOVEREIGN_AUTO_APPROVE — it is ignored"
        )
        assert 'os.environ.get("ARCHIVE_BATCH_ACCEPT' not in code_body, (
            "hitl_gate.py code must not read ARCHIVE_BATCH_ACCEPT — it is ignored"
        )

    def test_no_bare_yn_prompt_in_hitl_gate(self):
        """HitlGate must never use a bare 'y/n' prompt — always show labelled options."""
        src = Path("agentic_core/L5_safety/enforcement/hitl_gate.py").read_text(encoding="utf-8")
        assert "Approve this operation? (y/n)" not in src
        assert "[Y]" in src and "[N]" in src and "[S]" in src and "[A]" in src

    def test_hitl_required_error_exported(self):
        """HitlRequiredError must be importable from hitl_gate."""
        from agentic_core.L5_safety.enforcement.hitl_gate import HitlRequiredError as HRE

        assert issubclass(HRE, RuntimeError)

    def test_hitl_protected_paths_covers_agentic_core(self):
        assert "agentic_core" in HITL_PROTECTED_PATHS

    def test_hitl_protected_paths_covers_mixins(self):
        assert "mixins" in HITL_PROTECTED_PATHS

    def test_hitl_protected_paths_covers_runtime(self):
        assert "runtime" in HITL_PROTECTED_PATHS

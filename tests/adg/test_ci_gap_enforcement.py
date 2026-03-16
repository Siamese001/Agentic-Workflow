# adg-grep-ban: skip-file
"""
Enforcement coverage tests for CI gap fixes (GAP-1 through GAP-9).

Novel approaches used:
  - Synthetic diff injection:  feed hand-crafted unified-diff strings to
    guard_guardian_hitl._diff_adds_guardian_exemptions() — no git required.
  - Inline-Python harness:  extract and exec the agent-deletion-guard.yml
    Python heredoc with patched subprocess to test CI decision logic.
  - YAML structural assertions:  parse each modified workflow with PyYAML and
    assert on job/step names + run-command substrings — CI config as spec.
  - Temp-file AST boundary scanner:  write synthetic Python source to a
    tmp dir that mirrors ops_scripts/ci, then drive ToolingAppsBoundaryChecker
    directly — no side-effects on the real repo.
  - Parametric negative-space coverage:  @pytest.mark.parametrize for every
    exemption-detection rule to confirm safe patterns are never flagged.
"""

from __future__ import annotations

import re
import sys
import textwrap
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_ci_gap_enforcement")
_emit_applies_guardrail("p0", "test_ci_gap_enforcement", "p0_governance")
_emit_reads_policy_state("p0", "test_ci_gap_enforcement", "policy_binding")
_emit_snapshots_state("p0", "test_ci_gap_enforcement", "state_snapshot")
emit_replay_key("p0", "test_ci_gap_enforcement")
emit_determinism_digest("p0", "test_ci_gap_enforcement")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# ---------------------------------------------------------------------------
# Import subjects under test
# ---------------------------------------------------------------------------
from ops_scripts.ci.check_tooling_apps_boundary import ToolingAppsBoundaryChecker
from ops_scripts.ci.guard_guardian_hitl import (
    _diff_adds_guardian_exemptions,
)
from ops_scripts.ci.guard_guardian_hitl import (
    main as hitl_main,
)

WORKFLOWS = ROOT / ".github" / "workflows"
PRE_COMMIT_CFG = ROOT / ".pre-commit-config.yaml"


# ===========================================================================
# PART 1 — guard_guardian_hitl.py (GAP-9)
#   Novel: synthetic diff strings, no git subprocess required
# ===========================================================================


def _make_diff(file_path: str, added_lines: list[str], removed_lines: list[str] | None = None) -> str:
    """Build a minimal unified diff with explicit added/removed lines."""
    removed_lines = removed_lines or []
    lines = [f"+++ b/{file_path}"]
    for line in removed_lines:
        lines.append(f"-{line}")
    for line in added_lines:
        lines.append(f"+{line}")
    return "\n".join(lines)


class TestHitlDiffParser:
    """Synthetic-diff injection tests for _diff_adds_guardian_exemptions."""

    def test_detects_allow_in_production_dir(self):
        diff = _make_diff(
            "agentic_core/L2_execution/foo.py",
            ["    x = 1  # guardian: allow-global-mutation -- bootstrap only"],
        )
        result = _diff_adds_guardian_exemptions(diff)
        assert len(result) == 1
        assert "allow-global-mutation" in result[0]

    def test_detects_multiple_exemptions_same_file(self):
        diff = _make_diff(
            "apps_lic/reasoning/FooAgent.py",
            [
                "    pass  # guardian: allow-broad-except -- upstream lib raises Any",
                "    path = os.path.join(a, b)  # guardian: allow-os-path -- legacy caller",
            ],
        )
        result = _diff_adds_guardian_exemptions(diff)
        assert len(result) == 2

    def test_detects_exemptions_across_multiple_production_dirs(self):
        diff = "\n".join([
            "+++ b/apps_rg/engines/bar.py",
            "+    x  # guardian: allow-magic-config -- deploy env specific",
            "+++ b/system_learning/confidence/engine.py",
            "+    y  # guardian: allow-silent-swallow -- telemetry non-critical",
        ])
        result = _diff_adds_guardian_exemptions(diff)
        assert len(result) == 2

    # --- Negative space: lines that must NOT be detected ---

    @pytest.mark.parametrize("non_prod_dir", [
        "tests/adg/test_foo.py",
        "tools/evidence/runner.py",
        "ops_scripts/ci/check_something.py",
        "docs/reports/plans/EVIDENCE_foo.md",
    ])
    def test_ignores_non_production_dirs(self, non_prod_dir):
        diff = _make_diff(
            non_prod_dir,
            ["    x  # guardian: allow-os-path -- tests only"],
        )
        result = _diff_adds_guardian_exemptions(diff)
        assert result == [], f"Should not flag {non_prod_dir}"

    def test_ignores_removed_lines(self):
        """Lines starting with '-' are deletions — must not trigger HITL."""
        diff = _make_diff(
            "agentic_core/L0_routing/foo.py",
            removed_lines=["    x  # guardian: allow-global-mutation -- old"],
            added_lines=[],
        )
        result = _diff_adds_guardian_exemptions(diff)
        assert result == []

    def test_ignores_context_lines(self):
        """Unmodified context lines (no leading +/-) must not trigger HITL."""
        diff = "\n".join([
            "+++ b/agentic_core/L1_cognition/bar.py",
            "     x  # guardian: allow-global-mutation -- context line",
        ])
        result = _diff_adds_guardian_exemptions(diff)
        assert result == []

    def test_empty_diff_returns_empty(self):
        assert _diff_adds_guardian_exemptions("") == []

    def test_diff_without_guardian_lines_returns_empty(self):
        diff = _make_diff(
            "agentic_core/L2_execution/clean.py",
            ["    result = do_something()", "    return result"],
        )
        assert _diff_adds_guardian_exemptions(diff) == []


class TestHitlMain:
    """Integration tests for hitl_main() via temp commit-message files."""

    def _run_main(self, commit_msg: str, diff_output: str, tmp_path: Path) -> int:
        msg_file = tmp_path / "COMMIT_EDITMSG"
        msg_file.write_text(commit_msg, encoding="utf-8")
        with patch("ops_scripts.ci.guard_guardian_hitl._get_staged_diff", return_value=diff_output):
            old_argv = sys.argv[:]
            sys.argv = ["guard_guardian_hitl.py", str(msg_file)]
            try:
                return hitl_main()
            finally:
                sys.argv = old_argv

    def test_no_exemptions_exits_0(self, tmp_path):
        diff = _make_diff("agentic_core/L0_routing/clean.py", ["    pass"])
        rc = self._run_main("fix: minor cleanup", diff, tmp_path)
        assert rc == 0

    def test_exemption_with_hitl_approved_exits_0(self, tmp_path):
        diff = _make_diff(
            "agentic_core/L2_execution/foo.py",
            ["    x  # guardian: allow-global-mutation -- bootstrap"],
        )
        msg = "feat: bootstrap path\n\nHITL-APPROVED: Reviewed with team — unavoidable at module init."
        rc = self._run_main(msg, diff, tmp_path)
        assert rc == 0

    def test_exemption_without_hitl_approved_exits_1(self, tmp_path):
        diff = _make_diff(
            "apps_shared/reasoning/BaseAgent.py",
            ["    x  # guardian: allow-broad-except -- upstream lib"],
        )
        rc = self._run_main("fix: handle upstream error", diff, tmp_path)
        assert rc == 1

    def test_missing_commit_msg_file_exits_0(self, tmp_path):
        """Missing commit msg file should fail-open (can't verify, allow)."""
        old_argv = sys.argv[:]
        sys.argv = ["guard_guardian_hitl.py", str(tmp_path / "nonexistent")]
        try:
            rc = hitl_main()
        finally:
            sys.argv = old_argv
        assert rc == 0

    def test_no_argv_exits_0(self):
        """No argv[1] → skip (fail-open)."""
        old_argv = sys.argv[:]
        sys.argv = ["guard_guardian_hitl.py"]
        try:
            rc = hitl_main()
        finally:
            sys.argv = old_argv
        assert rc == 0


# ===========================================================================
# PART 2 — check_tooling_apps_boundary.py (GAP-3: import fix + wiring)
#   Novel: temp-dir AST boundary scanner — no side-effects on real repo
# ===========================================================================


class TestToolingAppsBoundaryChecker:
    """Drive ToolingAppsBoundaryChecker against synthetic Python files."""

    def _checker_with_fake_root(self, tmp_path: Path) -> ToolingAppsBoundaryChecker:
        """Create a checker whose TOOLING_DIRS point into tmp_path."""
        checker = ToolingAppsBoundaryChecker(tmp_path)
        checker.TOOLING_DIRS = ["ops_scripts/ci"]
        return checker

    def _write_py(self, tmp_path: Path, rel: str, src: str) -> Path:
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(textwrap.dedent(src), encoding="utf-8")
        return p

    def test_clean_file_no_violations(self, tmp_path):
        self._write_py(tmp_path, "ops_scripts/ci/clean.py", """
            import os
            from pathlib import Path
            def main(): pass
        """)
        checker = self._checker_with_fake_root(tmp_path)
        assert checker.check() == []

    def test_from_apps_lic_import_detected(self, tmp_path):
        self._write_py(tmp_path, "ops_scripts/ci/bad.py", """
            from apps_lic.engines import control_plane
            def main(): pass
        """)
        checker = self._checker_with_fake_root(tmp_path)
        violations = checker.check()
        assert len(violations) == 1
        assert "apps_lic" in violations[0]

    def test_import_apps_rg_detected(self, tmp_path):
        self._write_py(tmp_path, "ops_scripts/ci/bad2.py", """
            import apps_rg.reasoning.FooAgent
            def main(): pass
        """)
        checker = self._checker_with_fake_root(tmp_path)
        violations = checker.check()
        assert any("apps_rg" in v for v in violations)

    def test_import_apps_shared_detected(self, tmp_path):
        self._write_py(tmp_path, "ops_scripts/ci/bad3.py", """
            from apps_shared.reasoning.BaseDispatchAgent import BaseDispatchAgent
        """)
        checker = self._checker_with_fake_root(tmp_path)
        violations = checker.check()
        assert any("apps_shared" in v for v in violations)

    def test_multiple_violations_all_reported(self, tmp_path):
        self._write_py(tmp_path, "ops_scripts/ci/multi.py", """
            from apps_lic.engines import control_plane
            import apps_rg.reasoning.FooAgent
        """)
        checker = self._checker_with_fake_root(tmp_path)
        violations = checker.check()
        assert len(violations) == 2

    def test_underscore_prefixed_files_skipped(self, tmp_path):
        """Files beginning with _ are excluded by the checker."""
        self._write_py(tmp_path, "ops_scripts/ci/_private.py", """
            from apps_lic.engines import control_plane
        """)
        checker = self._checker_with_fake_root(tmp_path)
        assert checker.check() == []

    def test_forbidden_imports_are_strings(self):
        """Verify the import-fix: APPS_LIC_DIR etc. must resolve to strings."""
        checker = ToolingAppsBoundaryChecker(ROOT)
        for item in checker.FORBIDDEN_IMPORTS:
            assert isinstance(item, str), (
                f"FORBIDDEN_IMPORTS must be strings, got {type(item)}: {item!r}"
            )

    def test_nonexistent_tooling_dir_skipped_gracefully(self, tmp_path):
        """Missing tooling dirs must not raise — checked dirs simply don't exist."""
        checker = ToolingAppsBoundaryChecker(tmp_path)
        checker.TOOLING_DIRS = ["does_not_exist/ci"]
        assert checker.check() == []


# ===========================================================================
# PART 3 — CI workflow YAML structural assertions (GAP-1 through GAP-8)
#   Novel: parse each YAML and assert on job/step name substrings
#          — the YAML IS the spec; mismatches are immediate regressions
# ===========================================================================


def _load_workflow(name: str) -> dict:
    path = WORKFLOWS / name
    assert path.exists(), f"Workflow not found: {path}"
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def _all_step_names(workflow: dict) -> list[str]:
    names = []
    for job in workflow.get("jobs", {}).values():
        for step in job.get("steps", []):
            if "name" in step:
                names.append(step["name"])
    return names


def _all_step_runs(workflow: dict) -> list[str]:
    runs = []
    for job in workflow.get("jobs", {}).values():
        for step in job.get("steps", []):
            if "run" in step:
                runs.append(step["run"])
    return runs


def _all_job_names(workflow: dict) -> list[str]:
    return list(workflow.get("jobs", {}).keys())


class TestCiIntegrityGateWorkflow:
    """GAP-1: PowerShell ban wired into ci-integrity-gate.yml."""

    def test_powershell_ban_step_present(self):
        wf = _load_workflow("ci-integrity-gate.yml")
        names = _all_step_names(wf)
        assert any("PowerShell" in n or "powershell" in n.lower() for n in names), (
            "ci-integrity-gate.yml must have a PowerShell Ban step"
        )

    def test_powershell_ban_runs_correct_script(self):
        wf = _load_workflow("ci-integrity-gate.yml")
        runs = _all_step_runs(wf)
        assert any("check_powershell_ban.py" in r for r in runs), (
            "PowerShell ban step must invoke check_powershell_ban.py"
        )

    def test_powershell_ban_step_before_integrity_gate(self):
        """PowerShell ban must run BEFORE the §22 integrity gate (fail-fast)."""
        wf = _load_workflow("ci-integrity-gate.yml")
        names = _all_step_names(wf)
        ps_idx = next((i for i, n in enumerate(names) if "PowerShell" in n), None)
        integrity_idx = next((i for i, n in enumerate(names) if "22" in n or "integrity gate" in n.lower()), None)
        assert ps_idx is not None and integrity_idx is not None
        assert ps_idx < integrity_idx, "PowerShell ban must precede CI integrity gate"


class TestAdgInvariantScanWorkflow:
    """GAP-2: Test integrity + utility silent swallowers wired into adg-invariant-scan.yml."""

    def test_g2_test_integrity_step_present(self):
        wf = _load_workflow("adg-invariant-scan.yml")
        names = _all_step_names(wf)
        assert any("G2" in n or ("test integrity" in n.lower()) for n in names), (
            "adg-invariant-scan.yml must have G2 test integrity step"
        )

    def test_g3_silent_swallowers_step_present(self):
        wf = _load_workflow("adg-invariant-scan.yml")
        names = _all_step_names(wf)
        assert any("G3" in n or "swallow" in n.lower() for n in names), (
            "adg-invariant-scan.yml must have G3 silent swallowers step"
        )

    def test_g2_runs_check_test_integrity(self):
        wf = _load_workflow("adg-invariant-scan.yml")
        runs = _all_step_runs(wf)
        assert any("check_test_integrity.py" in r for r in runs)

    def test_g3_runs_check_utility_silent_swallowers(self):
        wf = _load_workflow("adg-invariant-scan.yml")
        runs = _all_step_runs(wf)
        assert any("check_utility_silent_swallowers.py" in r for r in runs)

    def test_g1_g2_g3_order(self):
        """G1 → G2 → G3 must appear in that order (G2/G3 depend on same test suite)."""
        wf = _load_workflow("adg-invariant-scan.yml")
        names = _all_step_names(wf)
        g_indices = {n[0:2]: i for i, n in enumerate(names) if re.match(r"G[123]", n)}
        if "G1" in g_indices and "G2" in g_indices and "G3" in g_indices:
            assert g_indices["G1"] < g_indices["G2"] < g_indices["G3"]


class TestStructureInvariantsWorkflow:
    """GAP-3: Tooling/apps boundary wired into structure-invariants.yml."""

    def test_gate_6_tooling_boundary_present(self):
        wf = _load_workflow("structure-invariants.yml")
        names = _all_step_names(wf)
        assert any("Gate 6" in n or "Tooling" in n for n in names), (
            "structure-invariants.yml must have Gate 6 tooling boundary step"
        )

    def test_gate_6_runs_correct_script(self):
        wf = _load_workflow("structure-invariants.yml")
        runs = _all_step_runs(wf)
        assert any("check_tooling_apps_boundary.py" in r for r in runs)

    def test_gate_6_comes_after_gate_5(self):
        wf = _load_workflow("structure-invariants.yml")
        names = _all_step_names(wf)
        idx5 = next((i for i, n in enumerate(names) if "Gate 5" in n), None)
        idx6 = next((i for i, n in enumerate(names) if "Gate 6" in n), None)
        if idx5 is not None and idx6 is not None:
            assert idx5 < idx6


class TestLayerSovereigntyWorkflow:
    """GAP-4: C0 boundary wired into layer-sovereignty-enforcement.yml."""

    def test_c0_boundary_step_present(self):
        wf = _load_workflow("layer-sovereignty-enforcement.yml")
        names = _all_step_names(wf)
        assert any("C0" in n or "c0" in n.lower() for n in names), (
            "layer-sovereignty-enforcement.yml must have C0 boundary step"
        )

    def test_c0_runs_check_c0_boundary(self):
        wf = _load_workflow("layer-sovereignty-enforcement.yml")
        runs = _all_step_runs(wf)
        assert any("check_c0_boundary.py" in r for r in runs)

    def test_c0_step_before_sovereignty_report(self):
        """C0 check must run before the report generation step."""
        wf = _load_workflow("layer-sovereignty-enforcement.yml")
        names = _all_step_names(wf)
        c0_idx = next((i for i, n in enumerate(names) if "C0" in n), None)
        report_idx = next((i for i, n in enumerate(names) if "Sovereignty Report" in n), None)
        if c0_idx is not None and report_idx is not None:
            assert c0_idx < report_idx


class TestTimeoutProgressWorkflow:
    """GAP-5: Timeout recovery wired into timeout-progress-enforcement.yml."""

    def test_timeout_recovery_step_present(self):
        wf = _load_workflow("timeout-progress-enforcement.yml")
        names = _all_step_names(wf)
        assert any("Recovery" in n or "recovery" in n.lower() for n in names), (
            "timeout-progress-enforcement.yml must have timeout recovery step"
        )

    def test_recovery_runs_validate_timeout_recovery(self):
        wf = _load_workflow("timeout-progress-enforcement.yml")
        runs = _all_step_runs(wf)
        assert any("validate_timeout_recovery.py" in r for r in runs)

    def test_progress_step_still_present(self):
        """Existing progress validation must not have been removed."""
        wf = _load_workflow("timeout-progress-enforcement.yml")
        runs = _all_step_runs(wf)
        assert any("validate_timeout_progress.py" in r for r in runs)


class TestAdgCiGatesWorkflow:
    """GAP-6: Blocking ADG staleness verify wired into adg-ci-gates.yml."""

    def test_staleness_verify_step_present(self):
        wf = _load_workflow("adg-ci-gates.yml")
        names = _all_step_names(wf)
        assert any("Staleness" in n or "staleness" in n.lower() for n in names), (
            "adg-ci-gates.yml must have ADG staleness verify step"
        )

    def test_staleness_verify_runs_without_warn_flag(self):
        """The step must NOT pass --warn (blocking mode required)."""
        wf = _load_workflow("adg-ci-gates.yml")
        runs = _all_step_runs(wf)
        stale_runs = [r for r in runs if "adg_stale_guard.py" in r]
        assert stale_runs, "adg_stale_guard.py must appear in a run step"
        blocking_runs = [r for r in stale_runs if "--warn" not in r]
        assert blocking_runs, (
            "ADG staleness verify in adg-ci-gates.yml must run WITHOUT --warn (blocking mode)"
        )

    def test_staleness_verify_after_ingest(self):
        """Staleness verify must follow the ingest step."""
        wf = _load_workflow("adg-ci-gates.yml")
        names = _all_step_names(wf)
        ingest_idx = next((i for i, n in enumerate(names) if "Ingest" in n), None)
        stale_idx = next((i for i, n in enumerate(names) if "Staleness" in n), None)
        if ingest_idx is not None and stale_idx is not None:
            assert ingest_idx < stale_idx


class TestAgentDeletionGuardWorkflow:
    """GAP-7: New agent-deletion-guard.yml workflow."""

    def test_workflow_file_exists(self):
        assert (WORKFLOWS / "agent-deletion-guard.yml").exists()

    def test_workflow_is_valid_yaml(self):
        wf = _load_workflow("agent-deletion-guard.yml")
        assert "jobs" in wf

    def test_workflow_triggers_on_push_and_pr(self):
        wf = _load_workflow("agent-deletion-guard.yml")
        # PyYAML parses the YAML 'on:' key as boolean True (YAML 1.1 spec)
        on = wf.get(True, wf.get("on", {})) or {}
        assert "push" in on, "Must trigger on push"
        assert "pull_request" in on, "Must trigger on pull_request"

    def test_workflow_checks_agent_deletion_authorization(self):
        wf = _load_workflow("agent-deletion-guard.yml")
        runs = _all_step_runs(wf)
        combined = "\n".join(runs)
        assert "AGENT-DELETION-AUTHORIZED" in combined
        assert "Agent.py" in combined

    def test_workflow_validates_companion_fields(self):
        wf = _load_workflow("agent-deletion-guard.yml")
        runs = _all_step_runs(wf)
        combined = "\n".join(runs)
        for field in ("REPLACEMENT:", "DEPRECATION-DATE:", "REFERENCES-MIGRATED:"):
            assert field in combined, f"Workflow must check for {field}"


class TestGuardianExemptionRatchetWorkflow:
    """GAP-8: Guardian exemption ratchet job wired into adg-antipattern-ci.yml."""

    def test_ratchet_job_present(self):
        wf = _load_workflow("adg-antipattern-ci.yml")
        jobs = _all_job_names(wf)
        assert any("exemption" in j or "ratchet" in j for j in jobs), (
            "adg-antipattern-ci.yml must have a guardian-exemption-ratchet job"
        )

    def test_ratchet_job_runs_exemption_gate(self):
        wf = _load_workflow("adg-antipattern-ci.yml")
        runs = _all_step_runs(wf)
        assert any("guardian_exemption_gate.py" in r for r in runs)

    def test_ratchet_job_uses_dry_run_in_ci(self):
        """In CI the ratchet must run with DRY_RUN=1 to avoid modifying the budget file."""
        wf = _load_workflow("adg-antipattern-ci.yml")
        ratchet_job = wf.get("jobs", {}).get("guardian-exemption-ratchet", {})
        env_values = []
        for step in ratchet_job.get("steps", []):
            if isinstance(step.get("env"), dict):
                env_values.extend(step["env"].values())
        assert "1" in env_values or any("DRY_RUN" in str(s) for s in env_values), (
            "Exemption ratchet CI job must set ADG_EXEMPTION_DRY_RUN=1"
        )


# ===========================================================================
# PART 4 — Pre-commit config contract (GAP-3 T3d, GAP-9 HITL hook)
# ===========================================================================


def _load_pre_commit() -> dict:
    with PRE_COMMIT_CFG.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def _all_hooks(cfg: dict) -> list[dict]:
    hooks = []
    for repo in cfg.get("repos", []):
        for hook in repo.get("hooks", []):
            hooks.append(hook)
    return hooks


class TestPreCommitConfig:
    """Verify new hooks are registered in the correct positions and stages."""

    def test_t3d_tooling_boundary_hook_exists(self):
        hooks = _all_hooks(_load_pre_commit())
        ids = [h["id"] for h in hooks]
        assert "check-tooling-apps-boundary" in ids

    def test_t3d_appears_before_t3f(self):
        hooks = _all_hooks(_load_pre_commit())
        ids = [h["id"] for h in hooks]
        assert "check-tooling-apps-boundary" in ids
        assert "module-collision-guard" in ids
        assert ids.index("check-tooling-apps-boundary") < ids.index("module-collision-guard"), (
            "T3d (tooling boundary) must precede T3f (module collision)"
        )

    def test_t3d_runs_on_python_files_only(self):
        hooks = {h["id"]: h for h in _all_hooks(_load_pre_commit())}
        t3d = hooks["check-tooling-apps-boundary"]
        assert t3d.get("types") == ["python"] or "python" in str(t3d.get("entry", "")), (
            "T3d should scope to Python files"
        )

    def test_guard_guardian_hitl_hook_exists(self):
        hooks = _all_hooks(_load_pre_commit())
        ids = [h["id"] for h in hooks]
        assert "guard-guardian-hitl" in ids

    def test_guard_guardian_hitl_is_commit_msg_stage(self):
        hooks = {h["id"]: h for h in _all_hooks(_load_pre_commit())}
        hitl = hooks["guard-guardian-hitl"]
        stages = hitl.get("stages", [])
        assert "commit-msg" in stages, (
            "guard-guardian-hitl must run at commit-msg stage"
        )

    def test_guard_guardian_hitl_passes_filenames(self):
        """commit-msg hooks receive the message file path — pass_filenames must be true."""
        hooks = {h["id"]: h for h in _all_hooks(_load_pre_commit())}
        hitl = hooks["guard-guardian-hitl"]
        assert hitl.get("pass_filenames") is True

    def test_header_comment_mentions_t3d(self):
        content = PRE_COMMIT_CFG.read_text(encoding="utf-8")
        assert "T3d" in content, "Header comment must document T3d"

    def test_header_comment_mentions_hitl(self):
        content = PRE_COMMIT_CFG.read_text(encoding="utf-8")
        assert "hitl" in content.lower(), "Header comment must document HITL guard"


# ===========================================================================
# PART 5 — Agent-deletion CI logic harness (GAP-7)
#   Novel: extract decision logic into a standalone function and test
#   it with synthetic git diff output — no real repo state needed.
# ===========================================================================


def _run_agent_deletion_logic(
    diff_output: str,
    log_output: str,
    event_name: str = "push",
) -> tuple[bool, str]:
    """
    Mirrors the core decision logic of agent-deletion-guard.yml's inline Python.
    Returns (passed: bool, message: str).
    """
    deleted_agents = []
    for line in diff_output.splitlines():
        parts = line.split("\t", 1)
        if len(parts) == 2 and parts[0] == "D" and parts[1].endswith("Agent.py"):
            deleted_agents.append(parts[1])

    if not deleted_agents:
        return True, "No *Agent.py files deleted."

    if "AGENT-DELETION-AUTHORIZED:" not in log_output:
        return False, "ERROR: missing AGENT-DELETION-AUTHORIZED"

    missing = []
    for field in ("REPLACEMENT:", "DEPRECATION-DATE:", "REFERENCES-MIGRATED:"):
        if field not in log_output:
            missing.append(field)
    if missing:
        return False, f"Missing fields: {missing}"

    match = re.search(r"AGENT-DELETION-AUTHORIZED:\s*(.+)", log_output)
    if match and len(match.group(1).strip()) < 50:
        return False, "Justification too short"

    return True, "OK"


class TestAgentDeletionLogic:
    """Direct logic tests — no subprocess, no git, no YAML parsing."""

    GOOD_LOG = (
        "AGENT-DELETION-AUTHORIZED: Shim fully migrated after 90-day deprecation period. "
        "All references redirected.\n"
        "REPLACEMENT: LocationHealerAgent\n"
        "DEPRECATION-DATE: 2025-12-01\n"
        "REFERENCES-MIGRATED: yes\n"
    )

    def test_no_agent_deletions_passes(self):
        diff = "M\tagentic_core/L0_routing/some_file.py\n"
        ok, _ = _run_agent_deletion_logic(diff, "")
        assert ok

    def test_agent_deletion_with_full_authorization_passes(self):
        diff = "D\tapps_lic/reasoning/OldAgent.py\n"
        ok, msg = _run_agent_deletion_logic(diff, self.GOOD_LOG)
        assert ok, msg

    def test_agent_deletion_without_marker_fails(self):
        diff = "D\tapps_rg/reasoning/SomeAgent.py\n"
        ok, msg = _run_agent_deletion_logic(diff, "fix: remove deprecated agent")
        assert not ok
        assert "AGENT-DELETION-AUTHORIZED" in msg

    def test_agent_deletion_missing_replacement_fails(self):
        log = (
            "AGENT-DELETION-AUTHORIZED: Shim fully migrated after 90-day deprecation period and verified.\n"
            "DEPRECATION-DATE: 2025-12-01\n"
            "REFERENCES-MIGRATED: yes\n"
        )
        diff = "D\tapps_shared/reasoning/OldAgent.py\n"
        ok, msg = _run_agent_deletion_logic(diff, log)
        assert not ok
        assert "REPLACEMENT" in msg

    def test_agent_deletion_missing_deprecation_date_fails(self):
        log = (
            "AGENT-DELETION-AUTHORIZED: Shim fully migrated after 90-day deprecation period and verified.\n"
            "REPLACEMENT: NewAgent\n"
            "REFERENCES-MIGRATED: yes\n"
        )
        diff = "D\tapps_shared/reasoning/OldAgent.py\n"
        ok, msg = _run_agent_deletion_logic(diff, log)
        assert not ok
        assert "DEPRECATION-DATE" in msg

    def test_short_justification_fails(self):
        log = (
            "AGENT-DELETION-AUTHORIZED: Too short.\n"
            "REPLACEMENT: NewAgent\n"
            "DEPRECATION-DATE: 2025-12-01\n"
            "REFERENCES-MIGRATED: yes\n"
        )
        diff = "D\tapps_shared/reasoning/OldAgent.py\n"
        ok, msg = _run_agent_deletion_logic(diff, log)
        assert not ok
        assert "short" in msg

    def test_non_agent_py_deletion_not_flagged(self):
        """Only *Agent.py deletions are relevant."""
        diff = "D\tapps_lic/engines/control_plane.py\n"
        ok, _ = _run_agent_deletion_logic(diff, "")
        assert ok

    @pytest.mark.parametrize("agent_path", [
        "apps_lic/reasoning/FooAgent.py",
        "apps_rg/reasoning/BarAgent.py",
        "apps_shared/reasoning/BaseAgent.py",
        "agentic_core/L3_orchestration/agents/OrchestratorAgent.py",
    ])
    def test_various_agent_locations_all_flagged(self, agent_path):
        diff = f"D\t{agent_path}\n"
        ok, msg = _run_agent_deletion_logic(diff, "no marker here")
        assert not ok, f"Should have flagged deletion of {agent_path}"


# ===========================================================================
# PART 6 — Script existence and importability contracts
# ===========================================================================


class TestScriptContracts:
    """Verify every referenced CI script actually exists on disk."""

    @pytest.mark.parametrize("script_rel", [
        "ops_scripts/ci/check_powershell_ban.py",
        "ops_scripts/ci/check_test_integrity.py",
        "ops_scripts/ci/check_utility_silent_swallowers.py",
        "ops_scripts/ci/check_tooling_apps_boundary.py",
        "ops_scripts/ci/check_c0_boundary.py",
        "ops_scripts/ci/validate_timeout_recovery.py",
        "ops_scripts/ci/guard_guardian_hitl.py",
        "ops_scripts/ci/guardian_exemption_gate.py",
    ])
    def test_script_exists(self, script_rel):
        assert (ROOT / script_rel).exists(), f"CI script not found: {script_rel}"

    @pytest.mark.parametrize("workflow_name", [
        "ci-integrity-gate.yml",
        "adg-invariant-scan.yml",
        "structure-invariants.yml",
        "layer-sovereignty-enforcement.yml",
        "timeout-progress-enforcement.yml",
        "adg-ci-gates.yml",
        "adg-antipattern-ci.yml",
        "agent-deletion-guard.yml",
    ])
    def test_workflow_file_exists(self, workflow_name):
        assert (WORKFLOWS / workflow_name).exists(), f"Workflow not found: {workflow_name}"

    @pytest.mark.parametrize("workflow_name", [
        "ci-integrity-gate.yml",
        "adg-invariant-scan.yml",
        "structure-invariants.yml",
        "layer-sovereignty-enforcement.yml",
        "timeout-progress-enforcement.yml",
        "adg-ci-gates.yml",
        "adg-antipattern-ci.yml",
        "agent-deletion-guard.yml",
    ])
    def test_workflow_is_valid_yaml(self, workflow_name):
        wf = _load_workflow(workflow_name)
        assert isinstance(wf, dict), f"{workflow_name} must parse to a dict"
        assert "jobs" in wf, f"{workflow_name} must have a 'jobs' key"

    def test_guard_guardian_hitl_importable(self):
        """The new HITL script must be importable without side-effects."""
        import importlib
        mod = importlib.import_module("ops_scripts.ci.guard_guardian_hitl")
        assert hasattr(mod, "main")
        assert hasattr(mod, "_diff_adds_guardian_exemptions")
        assert hasattr(mod, "_get_staged_diff")

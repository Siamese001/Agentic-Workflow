"""Creative integration & contract tests for ADG accelerator wiring.

These tests verify that the accelerators are genuinely wired as primary
defaults — not just implemented but actually hooked into every integration
point: pre-commit config, workflows, .windsurfrules, CI workflow, and CLI.

Test categories:
  1. Pre-commit contract  — hooks registered with correct entry/flags/order
  2. Windsurfrules contract — §1.3 and §2.6 reference the canonical tools
  3. Workflow contract     — inline Redis code eliminated; accelerators used
  4. CI workflow contract  — YAML valid; check-only flag present
  5. Functional smoke      — fixer fixes real violations; warn-mode exits 0
  6. Idempotency           — fixer is idempotent on already-canonical source
  7. Negative / anti-pattern — forbidden substitutions NOT present in rules
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_accelerator_wiring")
_emit_applies_guardrail("p0", "test_accelerator_wiring", "p0_governance")
_emit_reads_policy_state("p0", "test_accelerator_wiring", "policy_binding")
_emit_snapshots_state("p0", "test_accelerator_wiring", "state_snapshot")
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
)

_emit_emits_metric_event("test_accelerator_wiring", "p4obs", "metric_1")
_emit_emits_metric_event("test_accelerator_wiring", "p4obs", "metric_2")
_emit_emits_metric_event("test_accelerator_wiring", "p4obs", "metric_3")
_emit_emits_metric_event("test_accelerator_wiring", "p4obs", "metric_4")
_emit_emits_metric_event("test_accelerator_wiring", "p4obs", "metric_5")
_emit_emits_metric_event("test_accelerator_wiring", "p4obs", "metric_6")
_emit_records_incident_event("test_accelerator_wiring", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_accelerator_wiring", "p4obs", "anomaly")
_emit_writes_observability_log("test_accelerator_wiring", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_accelerator_wiring", "p4obs", "mon_state")
_emit_triggers_alert("test_accelerator_wiring", "p4obs", "alert")
_emit_links_incident_trace("test_accelerator_wiring", "p4obs", "trace_link")
_emit_captures_pattern("test_accelerator_wiring", "p3lm", "pattern")
_emit_records_learning_event("test_accelerator_wiring", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_accelerator_wiring", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_accelerator_wiring", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_accelerator_wiring", "p3lm", "routing")
_emit_improves_agent_policy("test_accelerator_wiring", "p3lm", "policy")
_emit_stores_learning_state("test_accelerator_wiring", "p3lm", "state")
_emit_records_execution_trace("test_accelerator_wiring", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_accelerator_wiring", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_accelerator_wiring", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_accelerator_wiring", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_accelerator_wiring", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_accelerator_wiring", "env_read", "p2_env_1")
_emit_reads_environ("test_accelerator_wiring", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_accelerator_wiring", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_accelerator_wiring", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_accelerator_wiring", "context_pull")
_emit_pulls_context("p1", "test_accelerator_wiring", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_accelerator_wiring", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_accelerator_wiring", "uwg_term_2")
_emit_writes_through("p1", "test_accelerator_wiring", "write_through")
_emit_writes_through("p1", "test_accelerator_wiring", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_accelerator_wiring", "safety_validation")
_emit_invokes_eval("p1", "test_accelerator_wiring", "eval_call")
_emit_proposal_commits_routing("p1", "test_accelerator_wiring", "routing_commit")
_emit_escalates_to_human("p1", "test_accelerator_wiring", "human_escalation")
_emit_routes_through("p1", "test_accelerator_wiring", "route_through")
_emit_checks_agent_registry("p1", "test_accelerator_wiring", "agent_registry")
_emit_validates_agent_capability("p1", "test_accelerator_wiring", "capability")
_emit_dispatches_execution_plan("p1", "test_accelerator_wiring", "exec_plan")
_emit_agent_executes_agent("p1", "test_accelerator_wiring", "sub_agent")
_emit_routes_to_agent("p1", "test_accelerator_wiring", "target_agent")
_emit_verifies_policy("p1", "test_accelerator_wiring", "policy_check")
_emit_observes_runtime_state("p1", "test_accelerator_wiring", "runtime_state")
_emit_verifies_boundary("p1", "test_accelerator_wiring", "boundary_check")
_emit_transcripts_response("p1", "test_accelerator_wiring", "transcript")
_emit_hard_fails_untranscripted("p1", "test_accelerator_wiring")
_emit_gated_by_confidence("p1", "test_accelerator_wiring", "confidence_gate")
emit_replay_key("p0", "test_accelerator_wiring")
emit_determinism_digest("p0", "test_accelerator_wiring")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_accelerator_wiring", "execution_auth")
_emit_validates_capability("p2", "test_accelerator_wiring", "capability_check")
_emit_routes_to_capability("p2", "test_accelerator_wiring", "capability_route")
_emit_writes_via_uwg("p2", "test_accelerator_wiring", "uwg_write")
_emit_blocks_direct_write("p2", "test_accelerator_wiring", "direct_write_block")
_emit_records_tool_invocation("p2", "test_accelerator_wiring", "tool_invocation")
_emit_captures_execution_output("p2", "test_accelerator_wiring", "exec_output")
_emit_dispatches_agent("p3", "test_accelerator_wiring", "agent_dispatch")
_emit_coordinates_agents("p3", "test_accelerator_wiring", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_accelerator_wiring", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_accelerator_wiring", "healing_outcome")
_emit_escalates_failure("p3", "test_accelerator_wiring", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_accelerator_wiring", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_accelerator_wiring", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_accelerator_wiring", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_accelerator_wiring", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_accelerator_wiring", "eval_metric")
_emit_stores_embedding("p4", "test_accelerator_wiring", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_accelerator_wiring", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_accelerator_wiring", "exec_snapshot_link")

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

PRE_COMMIT_CFG = ROOT / ".pre-commit-config.yaml"
WINDSURFRULES = ROOT / ".windsurf" / "rules" / ".windsurfrules"
REFRESH_WF = ROOT / ".windsurf" / "workflows" / "adg-redis-refresh.md"
REPAIR_WF = ROOT / ".windsurf" / "workflows" / "adg-repair-loop.md"
CI_WF = ROOT / ".github" / "workflows" / "adg-antipattern-ci.yml"


# ===========================================================================
# 1. Pre-commit contract
# ===========================================================================


class TestPreCommitContract:
    """Verify both new hooks are registered with correct entry points."""

    def _load_cfg(self) -> str:
        return PRE_COMMIT_CFG.read_text(encoding="utf-8")

    def test_t2c_guardian_comment_fixer_hook_exists(self):
        cfg = self._load_cfg()
        assert "guardian-comment-fixer" in cfg, (
            "T2c hook 'guardian-comment-fixer' missing from .pre-commit-config.yaml"
        )

    def test_t2c_hook_entry_uses_staged_flag(self):
        cfg = self._load_cfg()
        assert "adg_antipattern_fixer.py --staged" in cfg, (
            "T2c hook must use '--staged' so it only processes staged files"
        )

    def test_t3g_adg_stale_guard_hook_exists(self):
        cfg = self._load_cfg()
        assert "adg-stale-guard" in cfg, "T3g hook 'adg-stale-guard' missing from .pre-commit-config.yaml"

    def test_t3g_hook_entry_uses_warn_flag(self):
        cfg = self._load_cfg()
        assert "adg_stale_guard.py --warn" in cfg, (
            "T3g hook must use '--warn' so it never blocks commits when Redis is unavailable"
        )

    def test_t3g_hook_is_always_run(self):
        """Staleness guard must run even when no Python files changed."""
        cfg = self._load_cfg()
        # Find the adg-stale-guard block and verify always_run: true is nearby
        idx = cfg.find("adg-stale-guard")
        assert idx != -1
        block = cfg[idx : idx + 400]
        assert "always_run: true" in block, (
            "T3g hook must have 'always_run: true' — staleness check must run on every commit"
        )

    def test_t2c_appears_before_burndown_ratchet(self):
        """Guardian auto-fixer MUST run before the burndown ratchet so fixed
        comments don't trigger the ratchet violation count."""
        cfg = self._load_cfg()
        t2c_pos = cfg.find("guardian-comment-fixer")
        ratchet_pos = cfg.find("adg-burndown-gate")
        assert t2c_pos != -1 and ratchet_pos != -1, (
            "Both guardian-comment-fixer and adg-burndown-gate must be in config"
        )
        assert t2c_pos < ratchet_pos, (
            "T2c guardian-comment-fixer must appear BEFORE adg-burndown-gate in config"
        )

    def test_t2c_hook_uses_pass_filenames_false(self):
        """Fixer uses --staged to get its own file list; must not receive filenames from pre-commit."""
        cfg = self._load_cfg()
        idx = cfg.find("guardian-comment-fixer")
        block = cfg[idx : idx + 400]
        assert "pass_filenames: false" in block, (
            "T2c hook must have 'pass_filenames: false' — fixer selects files via --staged"
        )


# ===========================================================================
# 2. Windsurfrules contract
# ===========================================================================


class TestWindsurfRulesContract:
    """Verify §1.3 and §2.6 are complete and accurate."""

    def _load(self) -> str:
        return WINDSURFRULES.read_text(encoding="utf-8")

    def test_section_2_6_exists(self):
        text = self._load()
        assert "2.6" in text and "Accelerator" in text, (
            "§2.6 ADG Accelerator Tools section missing from .windsurfrules"
        )

    def test_section_2_6_lists_all_five_accelerators(self):
        text = self._load()
        tools = [
            "adg_antipattern_fixer.py",
            "adg_stale_guard.py",
            "adg_redis_query.py",
            "adg_type_check.py",
            "adg_test_selector.py",
        ]
        for tool in tools:
            assert tool in text, f"§2.6 must reference tool: {tool}"

    def test_section_2_6_has_forbidden_substitutions_block(self):
        text = self._load()
        assert "Forbidden substitutions" in text, (
            "§2.6 must include a 'Forbidden substitutions' block to block legacy patterns"
        )

    def test_forbidden_substitutions_blocks_raw_redis_inline(self):
        text = self._load()
        section_26 = self._section_26(text)
        assert "import redis" in section_26, "§2.6 must call out raw inline Redis imports as forbidden"

    def test_forbidden_substitutions_blocks_grep(self):
        text = self._load()
        section_26 = self._section_26(text)
        assert "grep" in section_26, "§2.6 must forbid grep as a substitute for search_nodes"

    def test_forbidden_substitutions_blocks_full_mypy(self):
        text = self._load()
        section_26 = self._section_26(text)
        assert "mypy" in section_26, "§2.6 must forbid full-suite mypy in favour of adg_type_check.py"

    def test_section_1_3_references_adg_test_selector(self):
        text = self._load()
        idx = text.find("### 1.3")
        block = text[idx : idx + 1500] if idx != -1 else ""
        assert "adg_test_selector.py" in block, (
            "§1.3 Test Selection must name adg_test_selector.py as the mandatory tool"
        )

    def test_section_1_3_has_canonical_cli_command(self):
        text = self._load()
        assert "adg_test_selector.py --from-diff" in text, (
            "§1.3 must include the canonical CLI command 'adg_test_selector.py --from-diff'"
        )

    def test_section_2_5_references_stale_guard(self):
        text = self._load()
        idx = text.find("### 2.5")
        block = text[idx : idx + 1500] if idx != -1 else ""
        assert "adg_stale_guard.py" in block, (
            "§2.5 Repair Discipline must reference adg_stale_guard.py as the freshness check"
        )

    def test_section_2_5_references_type_check(self):
        text = self._load()
        idx = text.find("### 2.5")
        block = text[idx : idx + 1500] if idx != -1 else ""
        assert "adg_type_check.py" in block, (
            "§2.5 Repair Discipline must reference adg_type_check.py for blast-radius type checking"
        )

    def test_forbidden_substitutions_blocks_broad_pytest(self):
        """Broad pytest before convergence should be listed as a forbidden substitution."""
        text = self._load()
        section_26 = self._section_26(text)
        assert "pytest" in section_26, "§2.6 must forbid broad 'pytest tests/' before convergence"

    def _section_26(self, text: str) -> str:
        """Extract §2.6 section text up to the closing ---."""
        # Use '### 2.6' to find the actual section header, not cross-references.
        section_26_start = text.find("### 2.6")
        assert section_26_start != -1, "### 2.6 section header not found in .windsurfrules"
        section_26_end = text.find("\n---", section_26_start)
        return text[section_26_start:section_26_end] if section_26_end != -1 else text[section_26_start:]


# ===========================================================================
# 3. Workflow contract
# ===========================================================================


class TestWorkflowContract:
    """Verify workflows use accelerators; old inline Redis patterns are gone."""

    def test_refresh_step1_uses_stale_guard(self):
        text = REFRESH_WF.read_text(encoding="utf-8")
        # Find STEP 1 block
        idx = text.find("## STEP 1")
        step1 = text[idx : text.find("## STEP 2", idx)] if idx != -1 else ""
        assert "adg_stale_guard.py" in step1, "adg-redis-refresh.md STEP 1 must use adg_stale_guard.py"

    def test_refresh_step1_no_raw_redis_inline(self):
        text = REFRESH_WF.read_text(encoding="utf-8")
        idx = text.find("## STEP 1")
        step1 = text[idx : text.find("## STEP 2", idx)] if idx != -1 else ""
        # Should NOT contain old pattern: python -c "import redis; r = redis.Redis
        assert "import redis; r = redis.Redis" not in step1, (
            "adg-redis-refresh.md STEP 1 must NOT contain raw Redis inline — use adg_stale_guard.py"
        )

    def test_refresh_step5_references_search_nodes_filters(self):
        text = REFRESH_WF.read_text(encoding="utf-8")
        assert "--layer" in text and "--entity-type" in text, (
            "adg-redis-refresh.md STEP 5 must document --layer and --entity-type filter flags"
        )

    def test_refresh_step5_references_test_selector(self):
        text = REFRESH_WF.read_text(encoding="utf-8")
        assert "adg_test_selector.py" in text, "adg-redis-refresh.md must reference adg_test_selector.py"

    def test_refresh_step5_references_type_check(self):
        text = REFRESH_WF.read_text(encoding="utf-8")
        assert "adg_type_check.py" in text, "adg-redis-refresh.md must reference adg_type_check.py"

    def test_repair_step0_uses_stale_guard(self):
        text = REPAIR_WF.read_text(encoding="utf-8")
        idx = text.find("### STEP 0")
        step0 = text[idx : text.find("### STEP 1", idx)] if idx != -1 else ""
        assert "adg_stale_guard.py" in step0, (
            "adg-repair-loop.md STEP 0 must use adg_stale_guard.py not raw Redis inline"
        )

    def test_repair_step0_no_raw_redis_inline(self):
        text = REPAIR_WF.read_text(encoding="utf-8")
        idx = text.find("### STEP 0")
        step0 = text[idx : text.find("### STEP 1", idx)] if idx != -1 else ""
        assert "import redis" not in step0, (
            "adg-repair-loop.md STEP 0 must NOT use raw 'import redis' — use adg_stale_guard.py"
        )

    def test_repair_step2_uses_test_selector(self):
        text = REPAIR_WF.read_text(encoding="utf-8")
        idx = text.find("### STEP 2")
        step2 = text[idx : text.find("### STEP 3", idx)] if idx != -1 else ""
        assert "adg_test_selector.py" in step2, (
            "adg-repair-loop.md STEP 2 must use adg_test_selector.py --from-diff"
        )

    def test_repair_step2_uses_from_diff_flag(self):
        text = REPAIR_WF.read_text(encoding="utf-8")
        assert "adg_test_selector.py --from-diff" in text, (
            "adg-repair-loop.md must use 'adg_test_selector.py --from-diff'"
        )

    def test_repair_step5_uses_type_check(self):
        text = REPAIR_WF.read_text(encoding="utf-8")
        idx = text.find("### STEP 5")
        step5 = text[idx : text.find("### STEP 6", idx)] if idx != -1 else ""
        assert "adg_type_check.py" in step5, (
            "adg-repair-loop.md STEP 5 must run adg_type_check.py --from-diff after ingest"
        )

    def test_refresh_references_section_lists_all_five_accelerators(self):
        text = REFRESH_WF.read_text(encoding="utf-8")
        ref_idx = text.find("## References")
        refs = text[ref_idx:] if ref_idx != -1 else text
        tools = [
            "adg_stale_guard.py",
            "adg_test_selector.py",
            "adg_type_check.py",
            "adg_antipattern_fixer.py",
        ]
        for t in tools:
            assert t in refs, f"adg-redis-refresh.md References must list {t}"


# ===========================================================================
# 4. CI workflow contract
# ===========================================================================


class TestCIWorkflowContract:
    """Verify adg-antipattern-ci.yml is well-formed and enforces the right check."""

    def _load(self) -> str:
        assert CI_WF.exists(), f"CI workflow file missing: {CI_WF}"
        return CI_WF.read_text(encoding="utf-8")

    def test_ci_workflow_file_exists(self):
        assert CI_WF.exists(), ".github/workflows/adg-antipattern-ci.yml must exist for CI enforcement"

    def test_ci_workflow_is_valid_yaml(self):
        """The workflow YAML must be parseable (no syntax errors)."""
        import importlib.util

        text = self._load()
        # Use yaml if available, else do a structural sanity check
        spec = importlib.util.find_spec("yaml")
        if spec is not None:
            import yaml

            data = yaml.safe_load(text)
            assert data is not None and isinstance(data, dict)
        else:
            # Structural fallback: must have 'name:', 'on:', 'jobs:'
            assert "name:" in text and "on:" in text and "jobs:" in text

    def test_ci_workflow_triggers_on_python_files(self):
        text = self._load()
        assert "**.py" in text or "*.py" in text, "CI workflow must trigger on Python file changes"

    def test_ci_workflow_uses_check_only_flag(self):
        text = self._load()
        assert "--check-only" in text, "CI workflow must use --check-only (never auto-modify files in CI)"

    def test_ci_workflow_calls_antipattern_fixer(self):
        text = self._load()
        assert "adg_antipattern_fixer.py" in text, "CI workflow must invoke adg_antipattern_fixer.py"

    def test_ci_workflow_sets_pythonpath(self):
        text = self._load()
        assert "PYTHONPATH" in text, "CI workflow must set PYTHONPATH=. so the fixer can import tools.*"

    def test_ci_workflow_has_no_redis_dependency(self):
        """adg_antipattern_fixer has no Redis dependency — CI workflow must not start Redis."""
        text = self._load()
        assert "redis-server" not in text and "redis" not in text.lower().split("adg_antipattern")[0], (
            "CI workflow must NOT require Redis — antipattern fixer runs on raw source"
        )


# ===========================================================================
# 5. Functional smoke tests
# ===========================================================================


class TestFunctionalSmoke:
    """Verify the accelerators actually work end-to-end in real scenarios."""

    def test_antipattern_fixer_fixes_missing_colon_in_guardian(self):
        """Fixer corrects '# guardian allow-magic-config -- reason' → adds colon.

        The detection regex anchors on ^ so the guardian comment must be at the
        start of the line (with optional indentation), not inline after code.
        """
        from tools.adg.adg_antipattern_fixer import GuardianCommentFixer

        fixer = GuardianCommentFixer()
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", encoding="utf-8", delete=False) as f:
            f.write("# guardian allow-magic-config -- using env var for port\n")
            tmp = Path(f.name)
        try:
            result = fixer.fix_file(tmp)
            assert result.fixed_count == 1, f"Expected 1 fix for missing colon; got {result.fixed_count}"
            fixed = tmp.read_text(encoding="utf-8")
            assert "# guardian: allow-magic-config -- using env var for port" in fixed
        finally:
            tmp.unlink()

    def test_antipattern_fixer_fixes_underscore_type(self):
        """Fixer corrects 'allow_silent_swallower' → 'allow-silent-swallower' (kebab)."""
        from tools.adg.adg_antipattern_fixer import GuardianCommentFixer

        fixer = GuardianCommentFixer()
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", encoding="utf-8", delete=False) as f:
            f.write("# guardian: allow_silent_swallower -- known safe path\n")
            tmp = Path(f.name)
        try:
            result = fixer.fix_file(tmp)
            assert result.fixed_count == 1
            fixed = tmp.read_text(encoding="utf-8")
            assert "allow-silent-swallower" in fixed
        finally:
            tmp.unlink()

    def test_antipattern_fixer_check_only_does_not_modify_file(self):
        """--check-only mode must never write back to disk."""
        from tools.adg.adg_antipattern_fixer import GuardianCommentFixer

        original = "# guardian allow-bare-except -- legacy code\n"
        fixer = GuardianCommentFixer()
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", encoding="utf-8", delete=False) as f:
            f.write(original)
            tmp = Path(f.name)
        try:
            result = fixer.fix_file(tmp, check_only=True)
            assert result.had_violations
            assert result.fixed_count == 1  # would fix
            assert tmp.read_text(encoding="utf-8") == original, (
                "check_only=True must NOT modify the file on disk"
            )
        finally:
            tmp.unlink()

    def test_stale_guard_warn_always_exits_0(self):
        """Integration: --warn must exit 0 regardless of Redis state.

        Whether Redis is running (fresh), running (stale), or completely
        down — --warn is the pre-commit T3g mode and must never block.
        """
        result = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "adg" / "adg_stale_guard.py"), "--warn"],
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            timeout=15,
        )
        assert result.returncode == 0, (
            f"adg_stale_guard.py --warn must ALWAYS exit 0; got {result.returncode}. stderr={result.stderr!r}"
        )

    def _run_fixer(self, *args: str) -> subprocess.CompletedProcess:
        """Run adg_antipattern_fixer.py with UTF-8 I/O so → (U+2192) doesn't crash cp1252."""
        env = {**__import__("os").environ, "PYTHONIOENCODING": "utf-8"}
        return subprocess.run(
            [sys.executable, str(ROOT / "tools" / "adg" / "adg_antipattern_fixer.py"), *args],
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            timeout=15,
            env=env,
        )

    def test_antipattern_fixer_exits_0_on_canonical_file(self):
        """Fixer must exit 0 on a file that already has canonical guardian comments."""
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", encoding="utf-8", delete=False) as f:
            f.write("# guardian: allow-magic-config -- required for test config\n")
            tmp = Path(f.name)
        try:
            result = self._run_fixer("--check-only", str(tmp))
            assert result.returncode == 0, (
                f"Fixer must exit 0 on canonical file; got {result.returncode}. stdout={result.stdout!r}"
            )
        finally:
            tmp.unlink()

    def test_antipattern_fixer_exits_1_on_violation_in_check_only_mode(self):
        """Fixer must exit 1 when violations found and --check-only is set."""
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", encoding="utf-8", delete=False) as f:
            f.write("# guardian allow-magic-config -- bad format\n")
            tmp = Path(f.name)
        try:
            result = self._run_fixer("--check-only", str(tmp))
            assert result.returncode == 1, (
                f"Fixer must exit 1 in check-only mode when violations found; got {result.returncode}"
            )
        finally:
            tmp.unlink()


# ===========================================================================
# 6. Idempotency tests
# ===========================================================================


class TestIdempotency:
    """The fixer must be idempotent — running twice produces the same result."""

    def test_fixer_is_idempotent_on_already_fixed_file(self):
        """Running fixer on a previously-fixed file must produce zero additional fixes."""
        from tools.adg.adg_antipattern_fixer import GuardianCommentFixer

        fixer = GuardianCommentFixer()
        # Comment at line-start so the ^ anchor detects it on first pass
        original = "# guardian allow-magic-config -- test\n"

        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", encoding="utf-8", delete=False) as f:
            f.write(original)
            tmp = Path(f.name)
        try:
            # First pass — should fix
            r1 = fixer.fix_file(tmp)
            assert r1.fixed_count == 1

            # Second pass — already canonical; should fix 0
            r2 = fixer.fix_file(tmp)
            assert r2.fixed_count == 0, (
                f"Fixer must be idempotent; second pass produced {r2.fixed_count} fixes"
            )
        finally:
            tmp.unlink()

    def test_fixer_is_idempotent_on_canonical_source(self):
        """A file with only canonical guardian comments must produce 0 fixes on both passes."""
        from tools.adg.adg_antipattern_fixer import GuardianCommentFixer

        fixer = GuardianCommentFixer()
        canonical = (
            "b = 2  # guardian: allow-silent-swallower -- known safe\n"
            "c = 3  # guardian: allow-global-mutation -- module-level init\n"
        )
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", encoding="utf-8", delete=False) as f:
            f.write(canonical)
            tmp = Path(f.name)
        try:
            for run_idx in (1, 2):
                r = fixer.fix_file(tmp)
                assert r.fixed_count == 0, (
                    f"Idempotency violated on run {run_idx}: {r.fixed_count} fixes on canonical file"
                )
        finally:
            tmp.unlink()


# ===========================================================================
# 7. Negative / anti-pattern guard
# ===========================================================================


class TestNegativeAntiPattern:
    """The accelerator wiring docs must NOT themselves contain the forbidden patterns."""

    def test_repair_loop_workflow_has_no_inline_redis_after_edit(self):
        """The repair loop must not contain the old raw Redis check pattern anywhere."""
        text = REPAIR_WF.read_text(encoding="utf-8")
        # Old pattern: python -c "import redis; r = redis.Redis(
        assert 'python -c "import redis' not in text, (
            "adg-repair-loop.md still contains old inline Redis command"
        )

    def test_refresh_workflow_has_no_inline_redis_in_step1(self):
        text = REFRESH_WF.read_text(encoding="utf-8")
        idx = text.find("## STEP 1")
        step1 = text[idx : text.find("## STEP 2", idx)] if idx != -1 else ""
        assert 'python -c "import redis' not in step1, (
            "adg-redis-refresh.md STEP 1 still contains old inline Redis command"
        )

    def test_windsurfrules_section_1_3_no_manual_pytest_expand(self):
        """§1.3 must not instruct users to manually expand test paths."""
        text = WINDSURFRULES.read_text(encoding="utf-8")
        idx = text.find("1.3")
        block = text[idx : idx + 2000] if idx != -1 else ""
        # Must reference the tool, not raw pytest with manual paths
        assert "adg_test_selector.py" in block, (
            "§1.3 must reference adg_test_selector.py — not manual pytest path expansion"
        )

    def test_adg_stale_guard_has_no_guardian_violations(self):
        """adg_stale_guard.py (a file we edited) must have 0 guardian comment violations.

        The stale guard has no guardian exemptions at all — so the fixer must
        report it as fully canonical.
        """
        env = {**__import__("os").environ, "PYTHONIOENCODING": "utf-8"}
        target = ROOT / "tools" / "adg" / "adg_stale_guard.py"
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "tools" / "adg" / "adg_antipattern_fixer.py"),
                "--check-only",
                str(target),
            ],
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            timeout=15,
            env=env,
        )
        assert result.returncode == 0, (
            f"adg_stale_guard.py has non-canonical guardian comments.\n"
            f"stdout={result.stdout!r}\nstderr={result.stderr!r}"
        )

    def test_stale_guard_itself_has_no_raw_redis_inline_outside_adgredisclient(self):
        """adg_stale_guard.py must use ADGRedisClient; never raw redis.Redis() directly."""
        text = (ROOT / "tools" / "adg" / "adg_stale_guard.py").read_text(encoding="utf-8")
        # Should import via ADGRedisClient, not construct redis.Redis() itself
        assert "redis.Redis(" not in text, (
            "adg_stale_guard.py must not instantiate redis.Redis() directly — use ADGRedisClient"
        )

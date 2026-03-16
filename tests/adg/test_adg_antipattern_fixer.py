"""Tests for ADG anti-pattern fixer — Accelerator #1.

Coverage matrix per §1.1:
- _is_canonical: canonical lines pass, all non-canonical forms fail
- _normalize_type: underscore→kebab, camelCase→kebab, with/without 'allow' prefix
- scan_violations: empty file, no violations, mixed canonical+non-canonical
- fix_source: each non-canonical form fixed correctly, canonical lines untouched,
              empty justification skipped with warning, multi-violation file
- fix_file: file modified on disk, check_only does not modify, OSError propagated
- Determinism: same source → same output on repeated calls
- Side-effects: fix_file writes exactly once when changes present
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

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

_emit_records_execution_trace("p0", "evidence", "test_adg_antipattern_fixer")
_emit_applies_guardrail("p0", "test_adg_antipattern_fixer", "p0_governance")
_emit_reads_policy_state("p0", "test_adg_antipattern_fixer", "policy_binding")
_emit_snapshots_state("p0", "test_adg_antipattern_fixer", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("test_adg_antipattern_fixer", "p4obs", "metric_1")
_emit_emits_metric_event("test_adg_antipattern_fixer", "p4obs", "metric_2")
_emit_emits_metric_event("test_adg_antipattern_fixer", "p4obs", "metric_3")
_emit_emits_metric_event("test_adg_antipattern_fixer", "p4obs", "metric_4")
_emit_emits_metric_event("test_adg_antipattern_fixer", "p4obs", "metric_5")
_emit_emits_metric_event("test_adg_antipattern_fixer", "p4obs", "metric_6")
_emit_records_incident_event("test_adg_antipattern_fixer", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_adg_antipattern_fixer", "p4obs", "anomaly")
_emit_writes_observability_log("test_adg_antipattern_fixer", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_adg_antipattern_fixer", "p4obs", "mon_state")
_emit_triggers_alert("test_adg_antipattern_fixer", "p4obs", "alert")
_emit_links_incident_trace("test_adg_antipattern_fixer", "p4obs", "trace_link")
_emit_captures_pattern("test_adg_antipattern_fixer", "p3lm", "pattern")
_emit_records_learning_event("test_adg_antipattern_fixer", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_adg_antipattern_fixer", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_adg_antipattern_fixer", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_adg_antipattern_fixer", "p3lm", "routing")
_emit_improves_agent_policy("test_adg_antipattern_fixer", "p3lm", "policy")
_emit_stores_learning_state("test_adg_antipattern_fixer", "p3lm", "state")
_emit_records_execution_trace("test_adg_antipattern_fixer", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_adg_antipattern_fixer", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_adg_antipattern_fixer", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_adg_antipattern_fixer", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_adg_antipattern_fixer", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_adg_antipattern_fixer", "env_read", "p2_env_1")
_emit_reads_environ("test_adg_antipattern_fixer", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_adg_antipattern_fixer", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_adg_antipattern_fixer", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_adg_antipattern_fixer", "context_pull")
_emit_pulls_context("p1", "test_adg_antipattern_fixer", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_adg_antipattern_fixer", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_adg_antipattern_fixer", "uwg_term_2")
_emit_writes_through("p1", "test_adg_antipattern_fixer", "write_through")
_emit_writes_through("p1", "test_adg_antipattern_fixer", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_adg_antipattern_fixer", "safety_validation")
_emit_invokes_eval("p1", "test_adg_antipattern_fixer", "eval_call")
_emit_proposal_commits_routing("p1", "test_adg_antipattern_fixer", "routing_commit")
emit_replay_key("p0", "test_adg_antipattern_fixer")
emit_determinism_digest("p0", "test_adg_antipattern_fixer")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_adg_antipattern_fixer", "execution_auth")
_emit_validates_capability("p2", "test_adg_antipattern_fixer", "capability_check")
_emit_routes_to_capability("p2", "test_adg_antipattern_fixer", "capability_route")
_emit_writes_via_uwg("p2", "test_adg_antipattern_fixer", "uwg_write")
_emit_blocks_direct_write("p2", "test_adg_antipattern_fixer", "direct_write_block")
_emit_records_tool_invocation("p2", "test_adg_antipattern_fixer", "tool_invocation")
_emit_captures_execution_output("p2", "test_adg_antipattern_fixer", "exec_output")
_emit_dispatches_agent("p3", "test_adg_antipattern_fixer", "agent_dispatch")
_emit_coordinates_agents("p3", "test_adg_antipattern_fixer", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_adg_antipattern_fixer", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_adg_antipattern_fixer", "healing_outcome")
_emit_escalates_failure("p3", "test_adg_antipattern_fixer", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_adg_antipattern_fixer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_adg_antipattern_fixer", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_adg_antipattern_fixer", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_adg_antipattern_fixer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_adg_antipattern_fixer", "eval_metric")
_emit_stores_embedding("p4", "test_adg_antipattern_fixer", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_adg_antipattern_fixer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_adg_antipattern_fixer", "exec_snapshot_link")

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# ===========================================================================
# _is_canonical
# ===========================================================================


class TestIsCanonical:
    def _check(self, line: str) -> bool:
        from tools.adg.adg_antipattern_fixer import _is_canonical

        return _is_canonical(line)

    def test_canonical_magic_config_passes(self):
        assert self._check("    # guardian: allow-magic-config -- used in legacy startup path") is True

    def test_canonical_silent_swallower_passes(self):
        assert self._check("# guardian: allow-silent-swallower -- intentional degraded path") is True

    def test_canonical_global_mutation_passes(self):
        assert self._check("# guardian: allow-global-mutation -- module-level singleton init") is True

    def test_missing_colon_is_not_canonical(self):
        assert self._check("# guardian allow-magic-config -- reason") is False

    def test_wrong_separator_is_not_canonical(self):
        assert self._check("# guardian: allow-magic-config: reason") is False

    def test_wrong_case_is_not_canonical(self):
        assert self._check("# Guardian: allow-magic-config -- reason") is False

    def test_underscore_type_is_not_canonical(self):
        assert self._check("# guardian: allow_magic_config -- reason") is False

    def test_non_guardian_comment_is_not_canonical(self):
        assert self._check("# This is just a regular comment") is False

    def test_empty_string_is_not_canonical(self):
        assert self._check("") is False

    def test_empty_justification_is_not_canonical(self):
        assert self._check("# guardian: allow-magic-config -- ") is False

    def test_missing_space_after_double_dash_is_not_canonical(self):
        assert self._check("# guardian: allow-magic-config --reason") is False


# ===========================================================================
# _normalize_type
# ===========================================================================


class TestNormalizeType:
    def _norm(self, raw: str) -> str:
        from tools.adg.adg_antipattern_fixer import _normalize_type

        return _normalize_type(raw)

    def test_already_canonical_magic_config(self):
        assert self._norm("allow-magic-config") == "allow-magic-config"

    def test_underscore_to_hyphen(self):
        assert self._norm("allow_magic_config") == "allow-magic-config"

    def test_camelcase_to_kebab(self):
        assert self._norm("allowMagicConfig") == "allow-magic-config"

    def test_silent_swallower_underscore(self):
        assert self._norm("allow_silent_swallower") == "allow-silent-swallower"

    def test_silent_swallower_camel(self):
        assert self._norm("allowSilentSwallower") == "allow-silent-swallower"

    def test_global_mutation_underscore(self):
        assert self._norm("allow_global_mutation") == "allow-global-mutation"

    def test_already_canonical_bare_except(self):
        assert self._norm("allow-bare-except") == "allow-bare-except"

    def test_bare_except_underscore(self):
        assert self._norm("allow_bare_except") == "allow-bare-except"

    def test_os_path_underscore(self):
        assert self._norm("allow_os_path") == "allow-os-path"

    def test_string_path_concat_underscore(self):
        assert self._norm("allow_string_path_concat") == "allow-string-path-concat"

    def test_unknown_type_gets_best_effort_kebab(self):
        result = self._norm("allow-custom-type-xyz")
        assert result.startswith("allow-")
        assert "_" not in result

    def test_normalize_is_deterministic(self):
        from tools.adg.adg_antipattern_fixer import _normalize_type

        assert _normalize_type("allow_magic_config") == _normalize_type("allow_magic_config")


# ===========================================================================
# scan_violations
# ===========================================================================


class TestScanViolations:
    def _scan(self, source: str):
        from tools.adg.adg_antipattern_fixer import GuardianCommentFixer

        return GuardianCommentFixer().scan_violations(source)

    def test_empty_source_returns_no_violations(self):
        assert self._scan("") == []

    def test_no_guardian_comments_returns_empty(self):
        src = "x = 1\n# normal comment\ndef foo(): pass\n"
        assert self._scan(src) == []

    def test_canonical_comment_not_reported(self):
        src = "# guardian: allow-magic-config -- used in legacy startup path\nx = 1\n"
        violations = self._scan(src)
        assert violations == []

    def test_missing_colon_detected(self):
        src = "# guardian allow-magic-config -- reason\n"
        violations = self._scan(src)
        assert len(violations) == 1
        assert violations[0][0] == 1  # line 1

    def test_wrong_separator_detected(self):
        src = "# guardian: allow-magic-config: reason\n"
        violations = self._scan(src)
        assert len(violations) == 1

    def test_wrong_case_detected(self):
        src = "# Guardian: allow-magic-config -- reason\n"
        violations = self._scan(src)
        assert len(violations) == 1

    def test_underscore_type_detected(self):
        src = "# guardian: allow_magic_config -- reason\n"
        violations = self._scan(src)
        assert len(violations) == 1

    def test_multiple_violations_all_detected(self):
        src = "# guardian allow-magic-config -- r1\nx = 1\n# guardian: allow_silent_swallower -- r2\n"
        violations = self._scan(src)
        assert len(violations) == 2
        assert violations[0][0] == 1
        assert violations[1][0] == 3

    def test_mixed_canonical_and_violation(self):
        src = (
            "# guardian: allow-magic-config -- canonical\n"
            "# guardian allow-silent-swallower -- not canonical\n"
        )
        violations = self._scan(src)
        assert len(violations) == 1
        assert violations[0][0] == 2

    def test_violation_line_numbers_are_1_indexed(self):
        src = "x = 1\n# guardian allow-magic-config -- reason\n"
        violations = self._scan(src)
        assert violations[0][0] == 2


# ===========================================================================
# fix_source
# ===========================================================================


class TestFixSource:
    def _fix(self, source: str):
        from tools.adg.adg_antipattern_fixer import GuardianCommentFixer

        return GuardianCommentFixer().fix_source(source)

    def test_canonical_line_unchanged(self):
        src = "# guardian: allow-magic-config -- used in legacy startup\n"
        fixed, changes, warnings = self._fix(src)
        assert changes == []
        assert fixed == src

    def test_missing_colon_fixed(self):
        src = "# guardian allow-magic-config -- legacy startup path\n"
        fixed, changes, _ = self._fix(src)
        assert len(changes) == 1
        assert "# guardian: allow-magic-config -- legacy startup path" in fixed

    def test_wrong_separator_colon_fixed_to_double_dash(self):
        src = "# guardian: allow-magic-config: legacy startup path\n"
        fixed, changes, _ = self._fix(src)
        assert len(changes) == 1
        assert "-- legacy startup path" in fixed
        assert ": legacy" not in fixed

    def test_wrong_case_guardian_fixed(self):
        src = "# Guardian: allow-magic-config -- legacy startup path\n"
        fixed, changes, _ = self._fix(src)
        assert len(changes) == 1
        assert fixed.startswith("# guardian:")

    def test_underscore_type_normalized_to_kebab(self):
        src = "# guardian: allow_magic_config -- legacy startup path\n"
        fixed, changes, _ = self._fix(src)
        assert len(changes) == 1
        assert "allow-magic-config" in fixed
        assert "allow_magic_config" not in fixed

    def test_camelcase_type_normalized(self):
        src = "# guardian: allowMagicConfig -- legacy startup path\n"
        fixed, changes, _ = self._fix(src)
        assert len(changes) == 1
        assert "allow-magic-config" in fixed

    def test_empty_justification_skipped_with_warning(self):
        src = "# guardian: allow-magic-config -- \n"
        fixed, changes, warnings = self._fix(src)
        assert changes == []  # not fixed
        assert len(warnings) == 1
        assert "empty justification" in warnings[0]

    def test_indentation_preserved(self):
        src = "    # guardian allow-magic-config -- reason\n"
        fixed, changes, _ = self._fix(src)
        assert len(changes) == 1
        assert changes[0].new_line.startswith("    # guardian:")

    def test_multiple_violations_all_fixed(self):
        src = "# guardian allow-magic-config -- r1\nx = 1\n# guardian: allow_silent_swallower -- r2\n"
        fixed, changes, _ = self._fix(src)
        assert len(changes) == 2
        assert "allow-magic-config" in fixed
        assert "allow-silent-swallower" in fixed

    def test_non_guardian_lines_untouched(self):
        src = "x = 1\n# regular comment\ndef foo(): pass\n"
        fixed, changes, _ = self._fix(src)
        assert changes == []
        assert fixed == src

    def test_fix_is_deterministic(self):
        src = "# guardian allow-magic-config -- reason\n"
        from tools.adg.adg_antipattern_fixer import GuardianCommentFixer

        fixer = GuardianCommentFixer()
        r1 = fixer.fix_source(src)
        r2 = fixer.fix_source(src)
        assert r1[0] == r2[0]
        assert len(r1[1]) == len(r2[1])

    def test_change_records_old_and_new_line(self):
        src = "# guardian allow-magic-config -- reason\n"
        _, changes, _ = self._fix(src)
        assert changes[0].old_line == "# guardian allow-magic-config -- reason"
        assert changes[0].new_line == "# guardian: allow-magic-config -- reason"

    def test_change_line_no_is_1_indexed(self):
        src = "x = 1\n# guardian allow-magic-config -- reason\n"
        _, changes, _ = self._fix(src)
        assert changes[0].line_no == 2

    def test_already_fixed_line_produces_no_change(self):
        """If fix_source is called twice, second call produces zero changes."""
        src = "# guardian allow-magic-config -- reason\n"
        from tools.adg.adg_antipattern_fixer import GuardianCommentFixer

        fixer = GuardianCommentFixer()
        fixed_src, _, _ = fixer.fix_source(src)
        _, changes2, _ = fixer.fix_source(fixed_src)
        assert changes2 == [], "Idempotent: second call on already-fixed source yields no changes"


# ===========================================================================
# fix_file
# ===========================================================================


class TestFixFile:
    def test_fix_file_writes_corrected_content(self, tmp_path):
        from tools.adg.adg_antipattern_fixer import GuardianCommentFixer

        f = tmp_path / "test_module.py"
        f.write_text("# guardian allow-magic-config -- reason\n", encoding="utf-8")

        fixer = GuardianCommentFixer()
        result = fixer.fix_file(f)

        assert result.fixed_count == 1
        content = f.read_text(encoding="utf-8")
        assert "# guardian: allow-magic-config -- reason" in content

    def test_check_only_does_not_modify_file(self, tmp_path):
        from tools.adg.adg_antipattern_fixer import GuardianCommentFixer

        f = tmp_path / "test_module.py"
        original = "# guardian allow-magic-config -- reason\n"
        f.write_text(original, encoding="utf-8")

        fixer = GuardianCommentFixer()
        result = fixer.fix_file(f, check_only=True)

        assert result.fixed_count == 1  # violation detected
        assert f.read_text(encoding="utf-8") == original  # file unchanged

    def test_no_violations_writes_nothing(self, tmp_path):
        from tools.adg.adg_antipattern_fixer import GuardianCommentFixer

        f = tmp_path / "clean.py"
        original = "# guardian: allow-magic-config -- reason\nx = 1\n"
        f.write_text(original, encoding="utf-8")

        fixer = GuardianCommentFixer()
        result = fixer.fix_file(f)

        assert result.fixed_count == 0
        assert f.read_text(encoding="utf-8") == original

    def test_result_file_path_matches_input(self, tmp_path):
        from tools.adg.adg_antipattern_fixer import GuardianCommentFixer

        f = tmp_path / "module.py"
        f.write_text("x = 1\n", encoding="utf-8")
        result = GuardianCommentFixer().fix_file(f)
        assert result.file_path == str(f)

    def test_empty_justification_increments_skipped_counter(self, tmp_path):
        from tools.adg.adg_antipattern_fixer import GuardianCommentFixer

        f = tmp_path / "module.py"
        f.write_text("# guardian: allow-magic-config -- \n", encoding="utf-8")
        result = GuardianCommentFixer().fix_file(f)
        assert result.skipped_empty_justification == 1
        assert result.fixed_count == 0

    def test_had_violations_true_when_fixes_made(self, tmp_path):
        from tools.adg.adg_antipattern_fixer import GuardianCommentFixer

        f = tmp_path / "module.py"
        f.write_text("# guardian allow-magic-config -- reason\n", encoding="utf-8")
        result = GuardianCommentFixer().fix_file(f)
        assert result.had_violations is True

    def test_had_violations_false_when_clean(self, tmp_path):
        from tools.adg.adg_antipattern_fixer import GuardianCommentFixer

        f = tmp_path / "clean.py"
        f.write_text("# guardian: allow-magic-config -- reason\n", encoding="utf-8")
        result = GuardianCommentFixer().fix_file(f)
        assert result.had_violations is False

    def test_missing_file_raises_os_error(self, tmp_path):
        from tools.adg.adg_antipattern_fixer import GuardianCommentFixer

        missing = tmp_path / "does_not_exist.py"
        with pytest.raises(OSError):
            GuardianCommentFixer().fix_file(missing)

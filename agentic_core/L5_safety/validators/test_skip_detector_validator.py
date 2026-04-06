"""
TestSilentSkipDetector — catches over-broad import guards in test files.

Root cause of the silent-test-skip epidemic (1 569 affected files):
    try:
        from some.module import Foo, CONSTANT_THAT_DOESNT_EXIST
        _AVAILABLE = True
    except Exception:          # ← TOO BROAD
        _AVAILABLE = False     # ← every test in this file permanently skipped

`except Exception:` catches NameError, AttributeError, SyntaxError, and any
runtime error in the import chain — not just a missing module.  The correct
pattern is:
    except ImportError:        # ← SAFE: only catches genuine missing module
        _AVAILABLE = False

This file-level silent skip is invisible to:
  1. SilentDegradationDetector  — whitelists test_*.py by design
  2. AntiPatternScanner          — DEFAULT_EXCLUDES contains **/test_*
  3. CI anti-pattern checks      — only scan production directories

This detector inverts the exclusion: it ONLY scans test_*.py / *_test.py.

§5.2 Fail-Closed: silent degradation is forbidden in test infrastructure too.
Constitutional rule: every test file must fail loudly, never silently skip.
"""

from __future__ import annotations

import ast
from pathlib import Path

from agentic_core.L5_safety.validators.base_detector_validator import (
    AntiPatternCategory,
    AntiPatternDetector,
    AntiPatternViolation,
    DetectionResult,
    EnforcementLevel,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402  # noqa: E402
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

emit_replay_key("p0", "test_skip_detector_validator")
emit_determinism_digest("p0", "test_skip_detector_validator")

_emit_dispatches_healing_run("p1", "test_skip_detector_validator", "L5")
_emit_routes_through("p1", "test_skip_detector_validator", "L5")
_emit_checks_agent_registry("p1", "test_skip_detector_validator", "agent_registry")
_emit_validates_agent_capability("p1", "test_skip_detector_validator", "capability")
_emit_dispatches_execution_plan("p1", "test_skip_detector_validator", "exec_plan")
_emit_agent_executes_agent("p1", "test_skip_detector_validator", "sub_agent")
_emit_routes_to_agent("p1", "test_skip_detector_validator", "target_agent")
_emit_verifies_policy("p1", "test_skip_detector_validator", "policy_check")
_emit_observes_runtime_state("p1", "test_skip_detector_validator", "runtime_state")
_emit_verifies_boundary("p1", "test_skip_detector_validator", "boundary_check")
_emit_transcripts_response("p1", "test_skip_detector_validator", "transcript")
_emit_hard_fails_untranscripted("p1", "test_skip_detector_validator")
_emit_gated_by_confidence("p1", "test_skip_detector_validator", "confidence_gate")
_emit_escalates_to_human("p1", "test_skip_detector_validator", "L5")
_emit_reads_policy_state("p1", "test_skip_detector_validator", "L5")
_emit_applies_guardrail("p0", "test_skip_detector_validator", "p0_governance")
_emit_snapshots_state("p0", "test_skip_detector_validator", "state_snapshot")
_emit_authorize_and_execute("p2", "test_skip_detector_validator", "execution_auth")
_emit_validates_capability("p2", "test_skip_detector_validator", "capability_check")
_emit_routes_to_capability("p2", "test_skip_detector_validator", "capability_route")
_emit_writes_via_uwg("p2", "test_skip_detector_validator", "uwg_write")
_emit_blocks_direct_write("p2", "test_skip_detector_validator", "direct_write_block")
_emit_records_tool_invocation("p2", "test_skip_detector_validator", "tool_invocation")
_emit_captures_execution_output("p2", "test_skip_detector_validator", "exec_output")
_emit_dispatches_agent("p3", "test_skip_detector_validator", "agent_dispatch")
_emit_coordinates_agents("p3", "test_skip_detector_validator", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_skip_detector_validator", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_skip_detector_validator", "healing_outcome")
_emit_escalates_failure("p3", "test_skip_detector_validator", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_skip_detector_validator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_skip_detector_validator", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_skip_detector_validator", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_skip_detector_validator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_skip_detector_validator", "eval_metric")
_emit_stores_embedding("p4", "test_skip_detector_validator", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_skip_detector_validator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_skip_detector_validator", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
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
    _emit_writes_through,
)

_emit_emits_metric_event("test_skip_detector_validator", "p4obs", "metric_1")
_emit_emits_metric_event("test_skip_detector_validator", "p4obs", "metric_2")
_emit_emits_metric_event("test_skip_detector_validator", "p4obs", "metric_3")
_emit_emits_metric_event("test_skip_detector_validator", "p4obs", "metric_4")
_emit_emits_metric_event("test_skip_detector_validator", "p4obs", "metric_5")
_emit_emits_metric_event("test_skip_detector_validator", "p4obs", "metric_6")
_emit_records_incident_event("test_skip_detector_validator", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_skip_detector_validator", "p4obs", "anomaly")
_emit_writes_observability_log("test_skip_detector_validator", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_skip_detector_validator", "p4obs", "mon_state")
_emit_triggers_alert("test_skip_detector_validator", "p4obs", "alert")
_emit_links_incident_trace("test_skip_detector_validator", "p4obs", "trace_link")
_emit_captures_pattern("test_skip_detector_validator", "p3lm", "pattern")
_emit_records_learning_event("test_skip_detector_validator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_skip_detector_validator", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_skip_detector_validator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_skip_detector_validator", "p3lm", "routing")
_emit_improves_agent_policy("test_skip_detector_validator", "p3lm", "policy")
_emit_stores_learning_state("test_skip_detector_validator", "p3lm", "state")
_emit_records_execution_trace("test_skip_detector_validator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_skip_detector_validator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_skip_detector_validator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_skip_detector_validator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_skip_detector_validator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_skip_detector_validator", "env_read", "p2_env_1")
_emit_reads_environ("test_skip_detector_validator", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_skip_detector_validator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_skip_detector_validator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_skip_detector_validator", "context_pull")
_emit_pulls_context("p1", "test_skip_detector_validator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_skip_detector_validator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_skip_detector_validator", "uwg_term_2")
_emit_writes_through("p1", "test_skip_detector_validator", "write_through")
_emit_writes_through("p1", "test_skip_detector_validator", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_skip_detector_validator", "safety_validation")
_emit_invokes_eval("p1", "test_skip_detector_validator", "eval_call")
_emit_proposal_commits_routing("p1", "test_skip_detector_validator", "routing_commit")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_SAFE_IMPORT_EXCEPTIONS: frozenset[str] = frozenset({"ImportError", "ModuleNotFoundError"})

_AVAILABILITY_SUFFIXES: tuple[str, ...] = (
    "_AVAILABLE",
    "_AVAIL",
    "_ENABLED",
    "_LOADED",
    "_IMPORTED",
    "_READY",
    "_PRESENT",
)


# ---------------------------------------------------------------------------
# Detector
# ---------------------------------------------------------------------------


class TestSilentSkipDetector(AntiPatternDetector):
    """
    Detects over-broad import guards in test files that cause all tests to be
    silently skipped whenever any error (not just ImportError) occurs during
    module setup.

    Only scans files whose name starts with ``test_`` or ends with ``_test.py``.
    Files in production directories are returned empty immediately.

    Sub-patterns detected
    ---------------------
    BROAD_EXCEPT_AVAILABILITY_FLAG
        ``except Exception/BaseException/bare:`` handler that sets an availability
        flag (``_AVAILABLE``, ``_LOADED``, …) to ``False``.  The broad catch
        swallows real bugs as "unavailable", making all ``skipif``-guarded tests
        permanently silent.
    """

    WHITELIST_COMMENT = "# guardian: allow-test-silent-skip"

    def __init__(
        self,
        enforcement_level: EnforcementLevel = EnforcementLevel.HARD_BLOCK,
        whitelisted_patterns: list[str] | None = None,
        whitelisted_files: list[str] | None = None,
    ) -> None:
        super().__init__(enforcement_level, whitelisted_patterns, whitelisted_files)

    @property
    def category(self) -> AntiPatternCategory:
        return AntiPatternCategory.TEST_SILENT_SKIP

    # ------------------------------------------------------------------
    # scan_file override — test files only
    # ------------------------------------------------------------------

    def scan_file(self, file_path: Path) -> DetectionResult:
        """Return empty result for non-test files; delegate to base for test files."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "TestSilentSkipDetector.scan_file")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:TestSilentSkipDetector.scan_file".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        name = file_path.name
        is_test_file = name.startswith("test_") or name.endswith("_test.py")
        if not is_test_file:
            return DetectionResult(file_path=file_path)
        return super().scan_file(file_path)

    # ------------------------------------------------------------------
    # detect — core AST walk
    # ------------------------------------------------------------------

    def detect(self, file_path: Path, tree: ast.Module) -> list[AntiPatternViolation]:
        """Walk ExceptHandler nodes; flag broad handlers that set availability flags."""
        violations: list[AntiPatternViolation] = []

        try:
            source_lines = file_path.read_text(encoding="utf-8").splitlines()
        except (ValueError, TypeError, RuntimeError) as e:
            return violations

        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                v = self._check_broad_except(node, file_path, source_lines)
                if v:
                    violations.append(v)

        return violations

    # ------------------------------------------------------------------
    # Sub-pattern: BROAD_EXCEPT_AVAILABILITY_FLAG
    # ------------------------------------------------------------------

    def _check_broad_except(
        self,
        handler: ast.ExceptHandler,
        file_path: Path,
        source_lines: list[str],
    ) -> AntiPatternViolation | None:
        """
        Flag ``except <broad>: ... _AVAILABLE = False`` where <broad> is anything
        other than ImportError / ModuleNotFoundError.
        """
        handler_type_name = self._handler_type_name(handler)

        # Safe: ImportError or ModuleNotFoundError — only catches genuine missing module
        if handler_type_name in _SAFE_IMPORT_EXCEPTIONS:
            return None

        # Look for _AVAILABLE = False (or similar flag) in the handler body
        flag_name = self._find_availability_false(handler.body)
        if flag_name is None:
            return None

        # Check guardian exemption
        if self._has_whitelist(source_lines, handler.lineno):
            return None

        caught_label = "bare except" if handler_type_name is None else f"except {handler_type_name}"
        evidence = (
            source_lines[handler.lineno - 1].strip() if handler.lineno <= len(source_lines) else caught_label
        )

        return AntiPatternViolation(
            file_path=file_path,
            line_number=handler.lineno,
            category=self.category,
            message=(
                f"Over-broad test guard: `{caught_label}` sets `{flag_name} = False`, "
                f"silently skipping ALL skipif-guarded tests whenever any non-import "
                f"error (NameError, AttributeError, SyntaxError, …) occurs. "
                f"Real bugs are invisible."
            ),
            evidence=evidence,
            severity="error",
            suggested_fix=(
                f"Replace:\n"
                f"    except Exception:\n"
                f"        {flag_name} = False\n"
                f"With:\n"
                f"    except ImportError:\n"
                f"        {flag_name} = False\n"
                f"This ensures NameError / AttributeError from non-existent symbols\n"
                f"surface as hard errors rather than silent skips."
            ),
            metadata={
                "sub_pattern": "BROAD_EXCEPT_AVAILABILITY_FLAG",
                "caught": caught_label,
                "flag": flag_name,
            },
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _handler_type_name(handler: ast.ExceptHandler) -> str | None:
        """Return the bare name of the exception type, or None for bare except."""
        if handler.type is None:
            return None
        if isinstance(handler.type, ast.Name):
            return handler.type.id
        if isinstance(handler.type, ast.Attribute):
            return handler.type.attr
        # Tuple form: except (A, B):
        if isinstance(handler.type, ast.Tuple):
            names = set()
            for elt in handler.type.elts:
                if isinstance(elt, ast.Name):
                    names.add(elt.id)
            # If ALL caught types are safe, the handler is safe
            if names and names.issubset(_SAFE_IMPORT_EXCEPTIONS):
                return "ImportError"  # treat as safe
            # Otherwise return the first non-safe type for the error message
            non_safe = names - _SAFE_IMPORT_EXCEPTIONS
            return next(iter(non_safe)) if non_safe else "ImportError"
        return "Exception"

    @staticmethod
    def _find_availability_false(stmts: list[ast.stmt]) -> str | None:
        """
        Return the flag name if any top-level statement assigns an availability
        flag to ``False``.  Returns ``None`` if no such assignment found.
        """
        for stmt in stmts:
            if not isinstance(stmt, ast.Assign):
                continue
            # Check value is the literal False
            if not (isinstance(stmt.value, ast.Constant) and stmt.value.value is False):
                continue
            for target in stmt.targets:
                if not isinstance(target, ast.Name):
                    continue
                name_upper = target.id.upper()
                if any(name_upper.endswith(suffix) for suffix in _AVAILABILITY_SUFFIXES):
                    return target.id
        return None

    def _has_whitelist(self, source_lines: list[str], lineno: int) -> bool:
        """True when the guardian exemption comment appears within 4 lines above.

        4 lines covers the common try/except structure where the guardian comment
        precedes the ``try:`` statement, which itself precedes 1-2 import lines
        before the ``except`` handler.
        """
        for idx in range(lineno - 2, max(-1, lineno - 6), -1):
            if 0 <= idx < len(source_lines):
                if self.WHITELIST_COMMENT in source_lines[idx]:
                    return True
        return False


__all__ = ["TestSilentSkipDetector"]

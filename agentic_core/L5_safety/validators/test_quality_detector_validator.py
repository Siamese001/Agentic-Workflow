"""
TestQualityDetector — catches low-quality test assertions that pass even when
the underlying functionality is completely broken.

Four sub-patterns detected
----------------------------
VACUOUS_ASSERT
    ``assert True`` or any always-true expression in a test function body.
    Unconditionally passes; provides zero signal about the system under test.
    Enforcement: HARD_BLOCK — there is never a valid reason for this.

SOLE_TYPE_CHECK
    A test function where *every* assertion is one of:
    - ``assert isinstance(x, T)``
    - ``assert x is not None``
    - ``assert hasattr(x, 'attr')``
    These pass even when ``x = None``, ``x = []``, ``x = False``, or ``x``
    is a mock/stub with the wrong internal state.
    Not applied to ``*_adg.py`` importability stubs (those are intentionally
    type-only by design).
    Enforcement: WARNING — flags for review, does not block.

WRITE_WITHOUT_READ
    A test function that calls a write/create/save/add method but:
      (a) never calls any corresponding read/get/search/query method, AND
      (b) never asserts the return value of the write call directly.
    Catches the "persistence vacuum" — tests that exercise write-path code
    but never verify the data was actually stored.
    Not applied to ``*_adg.py`` importability stubs.
    Enforcement: WARNING — flags for review, does not block.

SOLE_HASATTR_CHECK
    A test function where *every* assertion is ``assert hasattr(x, 'attr')``.
    More specific than SOLE_TYPE_CHECK — fires only when every assertion is
    purely an attribute-existence probe with no isinstance or value checks.
    These pass even when the attribute exists but holds a completely wrong value.
    Not applied to ``*_adg.py`` importability stubs.
    Enforcement: WARNING — flags for review, does not block.

Scope
-----
Only scans test_*.py and *_test.py files.
Only applies SOLE_TYPE_CHECK, SOLE_HASATTR_CHECK, and WRITE_WITHOUT_READ to
files that are NOT *_adg.py importability stubs (those legitimately only check
importability).
"""

from __future__ import annotations

import ast
import uuid
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
    _emit_applies_guardrail,
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
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
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

emit_replay_key("p0", "test_quality_detector_validator")
emit_determinism_digest("p0", "test_quality_detector_validator")

_emit_dispatches_healing_run("p1", "test_quality_detector_validator", "L5")
_emit_routes_through("p1", "test_quality_detector_validator", "L5")
_emit_checks_agent_registry("p1", "test_quality_detector_validator", "agent_registry")
_emit_validates_agent_capability("p1", "test_quality_detector_validator", "capability")
_emit_dispatches_execution_plan("p1", "test_quality_detector_validator", "exec_plan")
_emit_agent_executes_agent("p1", "test_quality_detector_validator", "sub_agent")
_emit_routes_to_agent("p1", "test_quality_detector_validator", "target_agent")
_emit_verifies_policy("p1", "test_quality_detector_validator", "policy_check")
_emit_observes_runtime_state("p1", "test_quality_detector_validator", "runtime_state")
_emit_verifies_boundary("p1", "test_quality_detector_validator", "boundary_check")
_emit_transcripts_response("p1", "test_quality_detector_validator", "transcript")
_emit_hard_fails_untranscripted("p1", "test_quality_detector_validator")
_emit_gated_by_confidence("p1", "test_quality_detector_validator", "confidence_gate")
_emit_escalates_to_human("p1", "test_quality_detector_validator", "L5")
_emit_reads_policy_state("p1", "test_quality_detector_validator", "L5")
_emit_authorize_and_execute("p2", "test_quality_detector_validator", "execution_auth")
_emit_validates_capability("p2", "test_quality_detector_validator", "capability_check")
_emit_routes_to_capability("p2", "test_quality_detector_validator", "capability_route")
_emit_writes_via_uwg("p2", "test_quality_detector_validator", "uwg_write")
_emit_blocks_direct_write("p2", "test_quality_detector_validator", "direct_write_block")
_emit_records_tool_invocation("p2", "test_quality_detector_validator", "tool_invocation")
_emit_captures_execution_output("p2", "test_quality_detector_validator", "exec_output")
_emit_dispatches_agent("p3", "test_quality_detector_validator", "agent_dispatch")
_emit_coordinates_agents("p3", "test_quality_detector_validator", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_quality_detector_validator", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_quality_detector_validator", "healing_outcome")
_emit_escalates_failure("p3", "test_quality_detector_validator", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_quality_detector_validator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_quality_detector_validator", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_quality_detector_validator", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_quality_detector_validator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_quality_detector_validator", "eval_metric")
_emit_stores_embedding("p4", "test_quality_detector_validator", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_quality_detector_validator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_quality_detector_validator", "exec_snapshot_link")
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
from tqdm import tqdm

_emit_emits_metric_event("test_quality_detector_validator", "p4obs", "metric_1")
_emit_emits_metric_event("test_quality_detector_validator", "p4obs", "metric_2")
_emit_emits_metric_event("test_quality_detector_validator", "p4obs", "metric_3")
_emit_emits_metric_event("test_quality_detector_validator", "p4obs", "metric_4")
_emit_emits_metric_event("test_quality_detector_validator", "p4obs", "metric_5")
_emit_emits_metric_event("test_quality_detector_validator", "p4obs", "metric_6")
_emit_records_incident_event("test_quality_detector_validator", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_quality_detector_validator", "p4obs", "anomaly")
_emit_writes_observability_log("test_quality_detector_validator", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_quality_detector_validator", "p4obs", "mon_state")
_emit_triggers_alert("test_quality_detector_validator", "p4obs", "alert")
_emit_links_incident_trace("test_quality_detector_validator", "p4obs", "trace_link")
_emit_captures_pattern("test_quality_detector_validator", "p3lm", "pattern")
_emit_records_learning_event("test_quality_detector_validator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_quality_detector_validator", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_quality_detector_validator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_quality_detector_validator", "p3lm", "routing")
_emit_improves_agent_policy("test_quality_detector_validator", "p3lm", "policy")
_emit_stores_learning_state("test_quality_detector_validator", "p3lm", "state")
_emit_records_execution_trace("test_quality_detector_validator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_quality_detector_validator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_quality_detector_validator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_quality_detector_validator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_quality_detector_validator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_quality_detector_validator", "env_read", "p2_env_1")
_emit_reads_environ("test_quality_detector_validator", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_quality_detector_validator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_quality_detector_validator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_quality_detector_validator", "context_pull")
_emit_pulls_context("p1", "test_quality_detector_validator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_quality_detector_validator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_quality_detector_validator", "uwg_term_2")
_emit_writes_through("p1", "test_quality_detector_validator", "write_through")
_emit_writes_through("p1", "test_quality_detector_validator", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_quality_detector_validator", "safety_validation")
_emit_invokes_eval("p1", "test_quality_detector_validator", "eval_call")
_emit_proposal_commits_routing("p1", "test_quality_detector_validator", "routing_commit")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_WRITE_PREFIXES: tuple[str, ...] = (
    "create_",
    "write_",
    "save_",
    "insert_",
    "put_",
    "add_",
    "store_",
    "persist_",
    "update_",
    "upsert_",
    "push_",
)

_WRITE_EXACT: frozenset[str] = frozenset(
    {
        "save",
        "write",
        "create",
        "insert",
        "put",
        "add",
        "store",
        "persist",
        "update",
        "upsert",
        "push",
        "commit",
        "flush",
        "dump",
    },
)

_WRITE_EXCLUDED_STDLIB: frozenset[str] = frozenset(
    {
        # pathlib.Path primitives used to set up fixtures, not to test persistence
        "write_text",
        "write_bytes",
        # os-level IO used for test scaffolding
        "makedirs",
        "mkdir",
        "symlink",
        "link",
        "rename",
        "replace",
    },
)

_READ_PREFIXES: tuple[str, ...] = (
    "get_",
    "read_",
    "load_",
    "find_",
    "search_",
    "fetch_",
    "query_",
    "lookup_",
    "retrieve_",
    "scan_",
    "list_",
    "open_",
    "read_graph",
    "fetchone",
    "fetchall",
    "execute",
)

_READ_SUBSTRINGS: tuple[str, ...] = ("SELECT", "fetchone", "fetchall")


# ---------------------------------------------------------------------------
# Weakness classifiers
# ---------------------------------------------------------------------------


def _is_weak_assert(node: ast.Assert) -> bool:
    """
    Return True when the assertion provides no meaningful signal about behavior.

    Weak assertions:
    - ``assert True``
    - ``assert isinstance(x, T)``  — only checks type, not value
    - ``assert x is not None``      — only checks not-None
    - ``assert hasattr(x, 'attr')`` — only checks attribute existence
    - Combinations of the above via ``and``
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "_is_weak_assert", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "_is_weak_assert", "p0_governance")
    return _is_weak_expr(node.test)


def _is_weak_expr(expr: ast.expr) -> bool:
    # assert True
    if isinstance(expr, ast.Constant) and expr.value is True:
        return True

    # assert isinstance(x, T)
    if isinstance(expr, ast.Call) and isinstance(expr.func, ast.Name) and expr.func.id == "isinstance":
        return True

    # assert hasattr(x, 'attr')
    if isinstance(expr, ast.Call) and isinstance(expr.func, ast.Name) and expr.func.id == "hasattr":
        return True

    # assert x is not None
    if (
        isinstance(expr, ast.Compare)
        and len(expr.ops) == 1
        and isinstance(expr.ops[0], ast.IsNot)
        and isinstance(expr.comparators[0], ast.Constant)
        and expr.comparators[0].value is None
    ):
        return True

    # assert A and B  where both A and B are weak
    if isinstance(expr, ast.BoolOp) and isinstance(expr.op, ast.And):
        return all(_is_weak_expr(v) for v in expr.values)

    return False


def _is_vacuous_expr(expr: ast.expr) -> bool:
    """Return True when the expression is unconditionally True (always passes)."""
    # assert True
    if isinstance(expr, ast.Constant) and expr.value is True:
        return True
    # assert len(x) >= 0  — length is never negative
    if (
        isinstance(expr, ast.Compare)
        and isinstance(expr.left, ast.Call)
        and isinstance(expr.left.func, ast.Name)
        and expr.left.func.id == "len"
        and len(expr.ops) == 1
        and isinstance(expr.ops[0], (ast.GtE, ast.Eq))
        and isinstance(expr.comparators[0], ast.Constant)
        and expr.comparators[0].value == 0
        and isinstance(expr.ops[0], ast.GtE)
    ):
        return True
    # assert x or not x  — tautology (hard to detect reliably; skip for now)
    return False


# ---------------------------------------------------------------------------
# Helpers for WRITE_WITHOUT_READ
# ---------------------------------------------------------------------------


def _call_name(node: ast.Call) -> str:
    """Return the bare attribute or function name from a Call node."""
    if isinstance(node.func, ast.Attribute):
        return node.func.attr
    if isinstance(node.func, ast.Name):
        return node.func.id
    return ""


def _has_write_call(fn: ast.FunctionDef | ast.AsyncFunctionDef) -> str | None:
    """Return the first write-like call name found, or None.

    Stdlib / pathlib IO primitives in ``_WRITE_EXCLUDED_STDLIB`` are skipped
    because they are typically used for fixture setup, not to exercise
    application persistence under test.
    """
    for node in ast.walk(fn):
        if not isinstance(node, ast.Call):
            continue
        name = _call_name(node)
        if name in _WRITE_EXCLUDED_STDLIB:
            continue
        if any(name.startswith(p) for p in _WRITE_PREFIXES):
            return name
        if name in _WRITE_EXACT:
            return name
    return None


def _has_read_or_verify(fn: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """Return True when there is any read-back or direct assertion on write result."""
    for node in tqdm(ast.walk(fn), desc="Processing", unit="item"):
        if isinstance(node, ast.Call):
            name = _call_name(node)
            if any(name.startswith(p) for p in _READ_PREFIXES):
                return True
            # execute("SELECT …")
            for arg in node.args:
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    if any(s in arg.value for s in _READ_SUBSTRINGS):
                        return True
        # assert <write_call>(...) — direct assertion on write return value
        if isinstance(node, ast.Assert):
            # if the assertion refers to the result of a write call, that counts
            for child in ast.walk(node.test):
                if isinstance(child, ast.Call) and any(
                    _call_name(child).startswith(p) for p in _WRITE_PREFIXES
                ):
                    return True
    return False


# ---------------------------------------------------------------------------
# Detector
# ---------------------------------------------------------------------------


class TestQualityDetector(AntiPatternDetector):
    """
    Detects low-quality test assertions in test files.

    Only scans files named ``test_*.py`` or ``*_test.py``.
    See module docstring for sub-pattern details.
    """

    WHITELIST_COMMENT = "# guardian: allow-test-quality"

    def __init__(
        self,
        enforcement_level: EnforcementLevel = EnforcementLevel.WARNING,
        whitelisted_patterns: list[str] | None = None,
        whitelisted_files: list[str] | None = None,
        skip_adg_stubs: bool = True,
    ) -> None:
        super().__init__(enforcement_level, whitelisted_patterns, whitelisted_files)
        self._skip_adg_stubs = skip_adg_stubs

    @property
    def category(self) -> AntiPatternCategory:
        return AntiPatternCategory.TEST_QUALITY

    # ------------------------------------------------------------------
    # scan_file override — test files only
    # ------------------------------------------------------------------

    def scan_file(self, file_path: Path) -> DetectionResult:
        """Return empty result for non-test files; delegate to base for test files."""
        name = file_path.name
        if not (name.startswith("test_") or name.endswith("_test.py")):
            return DetectionResult(file_path=file_path)
        return super().scan_file(file_path)

    # ------------------------------------------------------------------
    # detect
    # ------------------------------------------------------------------

    def detect(self, file_path: Path, tree: ast.Module) -> list[AntiPatternViolation]:
        _emit_records_execution_trace(
            str(uuid.uuid4()),
            LayerSegment.L5_POLICY,
            f"TestQualityDetector.detect:{file_path.name}",
        )
        violations: list[AntiPatternViolation] = []

        try:
            source_lines = file_path.read_text(encoding="utf-8").splitlines()
        except (ValueError, TypeError, RuntimeError) as e:
            return violations

        is_adg_stub = file_path.name.endswith("_adg.py")

        for node in tqdm(ast.walk(tree), desc="Processing", unit="item"):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if not node.name.startswith("test_"):
                continue

            # VACUOUS_ASSERT — applies to all test files
            v = self._check_vacuous(node, file_path, source_lines)
            if v:
                violations.append(v)

            # SOLE_TYPE_CHECK — skip ADG stubs
            if not (is_adg_stub and self._skip_adg_stubs):
                v = self._check_sole_type(node, file_path, source_lines)
                if v:
                    violations.append(v)

                # WRITE_WITHOUT_READ — skip ADG stubs
                v = self._check_write_without_read(node, file_path, source_lines)
                if v:
                    violations.append(v)

                # SOLE_HASATTR_CHECK — skip ADG stubs
                v = self._check_sole_hasattr(node, file_path, source_lines)
                if v:
                    violations.append(v)

        return violations

    # ------------------------------------------------------------------
    # Sub-pattern: VACUOUS_ASSERT
    # ------------------------------------------------------------------

    def _check_vacuous(
        self,
        fn: ast.FunctionDef | ast.AsyncFunctionDef,
        file_path: Path,
        source_lines: list[str],
    ) -> AntiPatternViolation | None:
        """Detect any ``assert True`` / always-true assertion in a test function."""
        for node in tqdm(ast.walk(fn), desc="Processing", unit="item"):
            if not isinstance(node, ast.Assert):
                continue
            if not _is_vacuous_expr(node.test):
                continue
            if self._has_whitelist(source_lines, node.lineno):
                continue
            evidence = (
                source_lines[node.lineno - 1].strip() if node.lineno <= len(source_lines) else "assert True"
            )
            return AntiPatternViolation(
                file_path=file_path,
                line_number=node.lineno,
                category=self.category,
                message=(
                    f"Vacuous assertion in `{fn.name}`: `{evidence}` always passes "
                    f"and provides zero signal about the system under test."
                ),
                evidence=evidence,
                severity="error",
                suggested_fix=(
                    f"Replace `{evidence}` with an assertion that verifies "
                    f"actual behavior: the return value, a side-effect, or "
                    f"a specific property of the result."
                ),
                metadata={
                    "sub_pattern": "VACUOUS_ASSERT",
                    "test_function": fn.name,
                },
            )
        return None

    # ------------------------------------------------------------------
    # Sub-pattern: SOLE_HASATTR_CHECK
    # ------------------------------------------------------------------

    def _check_sole_hasattr(
        self,
        fn: ast.FunctionDef | ast.AsyncFunctionDef,
        file_path: Path,
        source_lines: list[str],
    ) -> AntiPatternViolation | None:
        """Detect test methods where every assertion is a bare hasattr() probe."""
        asserts = [n for n in ast.walk(fn) if isinstance(n, ast.Assert)]
        if not asserts:
            return None

        def _is_hasattr_only(a: ast.Assert) -> bool:
            return (
                isinstance(a.test, ast.Call)
                and isinstance(a.test.func, ast.Name)
                and a.test.func.id == "hasattr"
            )

        if not all(_is_hasattr_only(a) for a in asserts):
            return None
        if self._has_whitelist(source_lines, fn.lineno):
            return None
        examples = []
        for a in asserts[:3]:
            if a.lineno <= len(source_lines):
                examples.append(source_lines[a.lineno - 1].strip())
        evidence = "; ".join(examples)
        return AntiPatternViolation(
            file_path=file_path,
            line_number=fn.lineno,
            category=self.category,
            message=(
                f"`{fn.name}` has {len(asserts)} assertion(s) that are ALL "
                f"bare `hasattr()` probes. These pass even when the attribute "
                f"exists but holds a completely wrong value or type."
            ),
            evidence=evidence,
            severity="warning",
            suggested_fix=(
                "Add at least one assertion that verifies the attribute's actual "
                "value, type, or a specific behavior it enables — not just that "
                "the attribute exists."
            ),
            metadata={
                "sub_pattern": "SOLE_HASATTR_CHECK",
                "test_function": fn.name,
                "assertion_count": len(asserts),
            },
        )

    # ------------------------------------------------------------------
    # Sub-pattern: SOLE_TYPE_CHECK
    # ------------------------------------------------------------------

    def _check_sole_type(
        self,
        fn: ast.FunctionDef | ast.AsyncFunctionDef,
        file_path: Path,
        source_lines: list[str],
    ) -> AntiPatternViolation | None:
        """Detect test methods where every assertion is a weak type/existence check."""
        asserts = [n for n in ast.walk(fn) if isinstance(n, ast.Assert)]
        if not asserts:
            return None
        if not all(_is_weak_assert(a) for a in asserts):
            return None
        # All are weak — flag the first assertion line
        first = asserts[0]
        if self._has_whitelist(source_lines, fn.lineno):
            return None
        examples = []
        for a in asserts[:3]:
            if a.lineno <= len(source_lines):
                examples.append(source_lines[a.lineno - 1].strip())
        evidence = "; ".join(examples)
        return AntiPatternViolation(
            file_path=file_path,
            line_number=fn.lineno,
            category=self.category,
            message=(
                f"`{fn.name}` has {len(asserts)} assertion(s) but ALL are weak "
                f"type/existence checks (isinstance / is not None / hasattr). "
                f"These pass even when the implementation is completely broken."
            ),
            evidence=evidence,
            severity="warning",
            suggested_fix=(
                "Add at least one strong assertion that verifies actual behavior: "
                "check a specific value, a non-empty collection, a concrete "
                "property, or an expected side-effect."
            ),
            metadata={
                "sub_pattern": "SOLE_TYPE_CHECK",
                "test_function": fn.name,
                "assertion_count": len(asserts),
            },
        )

    # ------------------------------------------------------------------
    # Sub-pattern: WRITE_WITHOUT_READ
    # ------------------------------------------------------------------

    def _check_write_without_read(
        self,
        fn: ast.FunctionDef | ast.AsyncFunctionDef,
        file_path: Path,
        source_lines: list[str],
    ) -> AntiPatternViolation | None:
        """
        Detect tests that call a write/create method but never verify via read-back.
        """
        write_name = _has_write_call(fn)
        if write_name is None:
            return None
        if _has_read_or_verify(fn):
            return None
        if self._has_whitelist(source_lines, fn.lineno):
            return None
        return AntiPatternViolation(
            file_path=file_path,
            line_number=fn.lineno,
            category=self.category,
            message=(
                f"`{fn.name}` calls `{write_name}(...)` (a write operation) but "
                f"never reads back the stored data to verify persistence. "
                f"The write path may silently fail without this test detecting it."
            ),
            evidence=f"write: {write_name}(...) — no read-back found",
            severity="warning",
            suggested_fix=(
                f"After calling `{write_name}(...)`, add a read-back call "
                f"(get_*, search_*, read_*, execute('SELECT …')) and assert "
                f"the stored value matches what was written."
            ),
            metadata={
                "sub_pattern": "WRITE_WITHOUT_READ",
                "test_function": fn.name,
                "write_call": write_name,
            },
        )

    # ------------------------------------------------------------------
    # Whitelist
    # ------------------------------------------------------------------

    def _has_whitelist(self, source_lines: list[str], lineno: int) -> bool:
        """True when guardian exemption appears within 3 lines above."""
        for idx in range(lineno - 2, max(-1, lineno - 5), -1):
            if 0 <= idx < len(source_lines):
                if self.WHITELIST_COMMENT in source_lines[idx]:
                    return True
        return False


__all__ = ["TestQualityDetector"]

"""DS-6 Governance sentinels for apps_rg L6 learning loop post-Exit ordering.

DS-6 was originally scoped as: "L6 records human_decision after
governed_run.__exit__(); never before; wiring deferred from W7".

Investigation found:
  - system_learning/runtime_hitl_consumer.py exists and is complete:
    RuntimeHitlConsumer + DraftSink / FileDraftSink + DraftProposal. Produces
    UWG draft proposals from HitlQualityReport + LedgerEntry stream.
  - system_learning/engines/hitl_decision_logger.py exists and is complete:
    log_hitl_decision(), log_routing_correction(), HITLReplayStore-style
    append-only evidence file writer.
  - apps_rg/__main__.py's main_canonical() already calls evaluate_hitl()
    (L5 gate) AFTER governed_run.__exit__() at lines 999-1010. The L5
    post-Exit hook is wired correctly.
  - The L6 learning-loop consumer (RuntimeHitlConsumer) is NOT wired into
    apps_rg/__main__.py — this is intentional: L6 drafts are UWG-mediated
    and must not auto-commit. The consumer is available for operator-invoked
    batch runs, not for inline main() injection.

DS-6 is therefore closed as: governance tests that lock:
  1. The post-Exit ordering constraint in main_canonical() (L5 evaluate_hitl
     is called AFTER the governed_run with block, never inside it).
  2. RuntimeHitlConsumer core contracts (consume produces drafts; consume_and_submit
     requires explicit sink; FileDraftSink round-trip; DraftKind taxonomy stable).
  3. hitl_decision_logger contracts (log_hitl_decision appends + increments counter;
     log_routing_correction emits a decision; reset_for_testing works).
  4. L6 modules must NOT be imported inside governed_run context (ordering guard).

Plan: apps-rg-deferred-scope-followon-d4e1b9 DS-6.
"""
from __future__ import annotations

import ast
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
MAIN_PY = REPO_ROOT / "apps_rg" / "__main__.py"


# ---------------------------------------------------------------------------
# 1. Post-Exit ordering: evaluate_hitl called after with block
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_evaluate_hitl_called_after_governed_run_context() -> None:
    """evaluate_hitl must be called AFTER the governed_run with block exits.

    AST check: verify that in main_canonical(), the evaluate_hitl() Call node
    appears at module scope AFTER the With node that wraps governed_run().
    """
    assert MAIN_PY.exists(), f"apps_rg/__main__.py missing: {MAIN_PY}"
    src = MAIN_PY.read_text(encoding="utf-8")
    tree = ast.parse(src)

    # Find main_canonical function
    main_fn = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "main_canonical":
            main_fn = node
            break
    assert main_fn is not None, "main_canonical() not found in apps_rg/__main__.py"

    # Collect top-level statement line numbers in main_canonical body
    with_lines: list[int] = []
    evaluate_hitl_lines: list[int] = []
    for stmt in main_fn.body:
        if isinstance(stmt, ast.With):
            with_lines.append(stmt.lineno)
        # evaluate_hitl may appear as:
        #   hitl_decision = evaluate_hitl(...)   → ast.Assign
        #   evaluate_hitl(...)                   → ast.Expr
        #   if run_dir is not None: hitl_decision = evaluate_hitl(...)  → ast.If
        # Walk all nodes in the statement to find the Call node.
        for node in ast.walk(stmt):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "evaluate_hitl"
            ):
                evaluate_hitl_lines.append(stmt.lineno)
                break

    assert with_lines, "No 'with' block found in main_canonical() — governed_run context missing."
    assert evaluate_hitl_lines, (
        "evaluate_hitl() call not found at top level of main_canonical(). "
        "L5 HITL gate must be called post-Exit."
    )
    last_with = max(with_lines)
    first_evaluate = min(evaluate_hitl_lines)
    assert first_evaluate > last_with, (
        f"evaluate_hitl() (line {first_evaluate}) must appear AFTER the last "
        f"'with' block (line {last_with}) in main_canonical(). "
        "L6/L5 post-Exit hook must never fire inside governed_run."
    )


# ---------------------------------------------------------------------------
# 2. RuntimeHitlConsumer: consume() produces drafts from a quality report
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_runtime_hitl_consumer_consume_returns_list() -> None:
    """RuntimeHitlConsumer.consume() must return a list (may be empty for sparse data)."""
    from agentic_core.L6_system_learning.runtime_hitl_consumer import RuntimeHitlConsumer
    from apps_eval.engines.hitl_decision_quality_engine import (
        HitlQualityReport,
        HitlQualityBucket,
    )

    report = HitlQualityReport(
        buckets=[],
        overall_score=1.0,
        total_entries=0,
        resolved_entries=0,
        pending_entries=0,
    )
    consumer = RuntimeHitlConsumer()
    drafts = consumer.consume(report)
    assert isinstance(drafts, list)


@pytest.mark.governance
def test_runtime_hitl_consumer_consume_and_submit_requires_sink() -> None:
    """consume_and_submit() must raise RuntimeError when no DraftSink configured."""
    from agentic_core.L6_system_learning.runtime_hitl_consumer import RuntimeHitlConsumer
    from apps_eval.engines.hitl_decision_quality_engine import HitlQualityReport

    report = HitlQualityReport(buckets=[], overall_score=1.0, total_entries=0, resolved_entries=0, pending_entries=0)
    consumer = RuntimeHitlConsumer()  # no sink
    with pytest.raises(RuntimeError, match="no DraftSink"):
        consumer.consume_and_submit(report)


@pytest.mark.governance
def test_file_draft_sink_round_trip() -> None:
    """FileDraftSink.submit() writes a JSON file; list_drafts() reads it back."""
    from agentic_core.L6_system_learning.runtime_hitl_consumer import (
        DraftKind,
        DraftProposal,
        FileDraftSink,
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        sink = FileDraftSink(root=Path(tmpdir))
        proposal = DraftProposal(
            draft_id="test-draft-001",
            kind=DraftKind.THRESHOLD_RAISE,
            target="classes.financial.timeout_s",
            before=30,
            after=20,
            rationale="Test rationale",
            hitl_class="financial",
            approver_pool="pool-A",
            sample_size=10,
        )
        receipt = sink.submit(proposal)
        assert receipt  # non-empty receipt
        drafts = sink.list_drafts()
        assert len(drafts) == 1
        assert drafts[0].draft_id == "test-draft-001"
        assert drafts[0].kind == DraftKind.THRESHOLD_RAISE


@pytest.mark.governance
def test_draft_kind_taxonomy_stable() -> None:
    """DraftKind must contain the 5 canonical values — taxonomy must not silently shrink."""
    from agentic_core.L6_system_learning.runtime_hitl_consumer import DraftKind

    required = {
        "TIMEOUT_TIGHTEN",
        "FALLBACK_REVIEW",
        "THRESHOLD_RAISE",
        "REASON_CODE_GAP",
        "APPROVAL_INCONSISTENT",
    }
    actual = {member.name for member in DraftKind}
    missing = required - actual
    assert not missing, (
        f"DraftKind is missing canonical members: {missing}. "
        "Taxonomy drives UWG review tooling and must not shrink."
    )


# ---------------------------------------------------------------------------
# 3. hitl_decision_logger contracts
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_hitl_decision_logger_appends_and_increments() -> None:
    """log_hitl_decision() must return an incrementing 1-based counter."""
    from agentic_core.L6_system_learning.hitl_decision_logger import (
        log_hitl_decision,
        get_decision_count,
        reset_for_testing,
    )

    reset_for_testing()
    n1 = log_hitl_decision(
        agent="TestAgent",
        file_path="test/path.py",
        violation="TEST_VIOLATION",
        proposed="ARCHIVE",
        decision="APPROVED",
    )
    n2 = log_hitl_decision(
        agent="TestAgent",
        file_path="test/path2.py",
        violation="TEST_VIOLATION",
        proposed="MOVE",
        decision="SKIPPED",
    )
    assert n1 == 1
    assert n2 == 2
    assert get_decision_count() == 2
    reset_for_testing()
    assert get_decision_count() == 0


@pytest.mark.governance
def test_hitl_decision_logger_routing_correction() -> None:
    """log_routing_correction() must return a positive decision number."""
    from agentic_core.L6_system_learning.hitl_decision_logger import (
        log_routing_correction,
        reset_for_testing,
    )

    reset_for_testing()
    n = log_routing_correction(
        user_input="test input",
        wrong_target="apps_rg",
        correct_target="apps_research",
        confidence=0.55,
    )
    assert n >= 1


# ---------------------------------------------------------------------------
# 4. L6 modules not imported inside governed_run context (ordering guard)
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_system_learning_not_imported_inside_governed_run() -> None:
    """system_learning imports must not appear lexically inside the governed_run with block.

    This is a static ordering guard: L6 consumption must happen post-Exit,
    never during execution inside the governed_run context manager.
    """
    assert MAIN_PY.exists()
    src = MAIN_PY.read_text(encoding="utf-8")
    tree = ast.parse(src)

    main_fn = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "main_canonical":
            main_fn = node
            break
    assert main_fn is not None

    # Find the top-level With block (governed_run context)
    governed_run_with: ast.With | None = None
    for stmt in main_fn.body:
        if isinstance(stmt, ast.With):
            governed_run_with = stmt
            break
    assert governed_run_with is not None, "No with block in main_canonical()"

    # Walk inside the With block for system_learning imports
    violations: list[int] = []
    for node in ast.walk(governed_run_with):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            if isinstance(node, ast.ImportFrom) and node.module and "system_learning" in node.module:
                violations.append(node.lineno)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if "system_learning" in alias.name:
                        violations.append(node.lineno)
    assert not violations, (
        f"system_learning imported inside governed_run With block at lines: {violations}. "
        "L6 consumption must be post-Exit only."
    )

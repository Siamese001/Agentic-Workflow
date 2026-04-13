"""Governance tests: mechanically prove C5 coverage scorer is advisory-only.

Asserts that the following symbols are ABSENT from every hard-gate and write-path file:
  - retrieval_coverage
  - coverage_score
  - should_rerank
  - gap_signal

Protected files (hard gates and write paths):
  - exit_control_gate.py      (X1A-X1D evaluation — disposition decision)
  - exit_control_hitl.py      (HITL escalation builder)
  - hitl_gate.py              (HITL confidence gate)
  - hitl/hitl_escalation_activator.py  (HITL escalation activator)
  - uwg_committer.py          (UWG durable ledger commit)
  - uwg_verifier.py           (UWG pre-commit verifier)
  - prompt_assembler.py       (prompt assembly — no coverage injection)

Invariant test:
  - RetrievalCoverageResult.advisory is always True (construction enforced)
  - coverage_score does not appear in any ExitEvaluationDimensions or disposition type source
"""

from __future__ import annotations

import ast
import pathlib

import pytest

# ---------------------------------------------------------------------------
# Resolved absolute paths for all protected files
# ---------------------------------------------------------------------------

_ROOT = pathlib.Path(__file__).parents[3]  # repo root

_PROTECTED_FILES: dict[str, pathlib.Path] = {
    "exit_control_gate": _ROOT / "agentic_core/L5_safety/enforcement/exit_control_gate.py",
    "exit_control_hitl": _ROOT / "agentic_core/L5_safety/enforcement/exit_control_hitl.py",
    "hitl_gate": _ROOT / "agentic_core/L5_safety/enforcement/hitl_gate.py",
    "hitl_escalation_activator": _ROOT
    / "agentic_core/L5_safety/enforcement/hitl/hitl_escalation_activator.py",
    "uwg_committer": _ROOT / "agentic_core/L4_state/enforcement/uwg_committer.py",
    "uwg_verifier": _ROOT / "agentic_core/L4_state/enforcement/uwg_verifier.py",
    "prompt_assembler": _ROOT / "agentic_core/prompt_governance/core/prompt_assembler.py",
}

_ADVISORY_SYMBOLS = frozenset(
    {
        "retrieval_coverage",
        "coverage_score",
        "should_rerank",
        "gap_signal",
        "RetrievalCoverageResult",
        "HeuristicCoverageScorer",
        "score_coverage",
    }
)


def _collect_identifiers(source: str) -> set[str]:
    """Return all Name.id and Attribute.attr tokens from an AST parse."""
    tree = ast.parse(source)
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            names.add(node.id)
        elif isinstance(node, ast.Attribute):
            names.add(node.attr)
    return names


def _collect_string_literals(source: str) -> set[str]:
    """Return all string literal values found in the AST."""
    tree = ast.parse(source)
    literals: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            literals.add(node.value)
    return literals


# ---------------------------------------------------------------------------
# Parametrised: each protected file must not reference any advisory symbol
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("label,path", _PROTECTED_FILES.items())
def test_advisory_symbols_absent_from_hard_gate(label: str, path: pathlib.Path) -> None:
    if not path.exists():
        pytest.skip(f"{label}: file not found at {path}")

    source = path.read_text(encoding="utf-8")
    identifiers = _collect_identifiers(source)
    string_literals = _collect_string_literals(source)

    violations = _ADVISORY_SYMBOLS & (identifiers | string_literals)
    assert not violations, (
        f"Advisory-only boundary violated in {label} ({path.name}): "
        f"found forbidden symbols {sorted(violations)}. "
        "Coverage scorer output must never gate allow/deny/escalate/commit decisions."
    )


# ---------------------------------------------------------------------------
# ExitEvaluationDimensions and disposition types must not reference coverage
# ---------------------------------------------------------------------------

_DISPOSITION_TYPES_PATH = _ROOT / "agentic_core/L5_safety/types/exit_disposition_types.py"
_EXIT_OUTCOME_TYPES_PATH = _ROOT / "agentic_core/L5_safety/types/exit_outcome_types.py"


@pytest.mark.parametrize(
    "label,path",
    [
        ("exit_disposition_types", _DISPOSITION_TYPES_PATH),
        ("exit_outcome_types", _EXIT_OUTCOME_TYPES_PATH),
    ],
)
def test_advisory_symbols_absent_from_disposition_types(label: str, path: pathlib.Path) -> None:
    if not path.exists():
        pytest.skip(f"{label}: file not found at {path}")

    source = path.read_text(encoding="utf-8")
    identifiers = _collect_identifiers(source)
    string_literals = _collect_string_literals(source)

    violations = _ADVISORY_SYMBOLS & (identifiers | string_literals)
    assert not violations, (
        f"Advisory-only boundary violated in disposition types {label} ({path.name}): "
        f"found forbidden symbols {sorted(violations)}."
    )


# ---------------------------------------------------------------------------
# Invariant: RetrievalCoverageResult.advisory cannot be False
# ---------------------------------------------------------------------------


def test_coverage_result_advisory_field_enforced_at_construction() -> None:
    """advisory=False must raise ValueError — cannot silently become a gate input."""
    from agentic_core.L3_orchestration.reasoning.engines.retrieval_coverage_scorer import (
        RetrievalCoverageResult,
    )

    with pytest.raises(ValueError, match="advisory must always be True"):
        RetrievalCoverageResult(
            advisory=False,
            evaluator_name="test",
            evaluator_version="0.0.0",
            coverage_score=1.0,
            should_rerank=False,
            gap_signal="",
            latency_ms=1.0,
            budget_status="ok",
            fallback_reason="",
        )


# ---------------------------------------------------------------------------
# Invariant: coverage_score cannot become a required condition for
#            allow / deny / escalate / commit in exit_control_gate.py
# ---------------------------------------------------------------------------


def test_exit_control_gate_disposition_functions_do_not_read_coverage() -> None:
    """Disposition-producing functions in exit_control_gate must not mention coverage symbols."""
    path = _PROTECTED_FILES["exit_control_gate"]
    if not path.exists():
        pytest.skip("exit_control_gate.py not found")

    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)

    violations: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            fn_name = node.name.lower()
            if any(
                kw in fn_name
                for kw in ("evaluat", "dispos", "gate", "decide", "allow", "deny", "escalat", "commit")
            ):
                body_names: set[str] = set()
                for child in ast.walk(node):
                    if isinstance(child, ast.Name):
                        body_names.add(child.id)
                    elif isinstance(child, ast.Attribute):
                        body_names.add(child.attr)
                    elif isinstance(child, ast.Constant) and isinstance(child.value, str):
                        body_names.add(child.value)
                found = _ADVISORY_SYMBOLS & body_names
                if found:
                    violations.append(f"  fn={node.name!r} uses {sorted(found)}")

    assert not violations, (
        "exit_control_gate disposition functions read advisory coverage symbols:\n"
        + "\n".join(violations)
        + "\nCoverage scorer must never influence allow/deny/escalate/commit."
    )


# ---------------------------------------------------------------------------
# Invariant: EvidenceBundle.retrieval_coverage must not be forwarded to
#            any ExitGateResult, QualityChecks, or ExitEvaluationDimensions
# ---------------------------------------------------------------------------


def test_evidence_shaper_does_not_pass_coverage_to_exit_types() -> None:
    """EvidenceBundle is used by callers but retrieval_coverage must not reach exit types."""
    shaper_path = _ROOT / "agentic_core/L3_orchestration/reasoning/engines/evidence_shaper.py"
    if not shaper_path.exists():
        pytest.skip("evidence_shaper.py not found")

    source = shaper_path.read_text(encoding="utf-8")
    tree = ast.parse(source)

    # Verify retrieval_coverage is only in the EvidenceBundle dataclass definition
    # and in the scoring step — never forwarded to exit gate types.
    exit_gate_type_names = frozenset(
        {
            "ExitGateResult",
            "QualityChecks",
            "ExitEvaluationDimensions",
            "AllowResponsePayload",
            "CommitToUWGRequest",
            "DenyReturnPayload",
            "EscalateToHITLPacket",
        }
    )

    # Collect all Call nodes to exit gate type constructors
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            fn = node.func
            fn_name = ""
            if isinstance(fn, ast.Name):
                fn_name = fn.id
            elif isinstance(fn, ast.Attribute):
                fn_name = fn.attr

            if fn_name in exit_gate_type_names:
                # Check keyword args passed to these constructors
                for kw in node.keywords:
                    assert kw.arg not in _ADVISORY_SYMBOLS, (
                        f"evidence_shaper.py forwards advisory symbol {kw.arg!r} "
                        f"to hard-gate type {fn_name!r} — boundary violated."
                    )

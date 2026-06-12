"""X2 gate severity SSOT — Claude Sonnet 4.6 base recalibration (plan x2-gate-slimdown-b4e8d2).

A small, central lever to demote adversarially-verified STYLE gates from hard-FAIL to WARN
WITHOUT touching their detection logic. A demoted gate still runs and computes its real verdict;
``soften_warn_only`` flips a *failing* result for a demoted gate to ``pass=True`` and stamps
``WARN_ONLY_MARKER`` into ``failure_reason`` so the demotion stays honest, auditable, and reversible
(remove the id from ``STYLE_WARN_GATE_IDS`` → it is a hard FAIL again).

Applied at the lane gate-assembly seam (``soften_warn_only(run_<lane>_x2_gates(...))``), so every
downstream consumer — the per-lane ``product_quality_status`` ("all x2 pass") AND the shared
``aggregate_x3`` ``failed_gates`` computation AND the product-shape "required gates passed" check —
all observe the softened (passed) result. The raw ``run_<lane>_x2_gates`` functions are untouched,
so the ``weak_fail_cases`` unit suite still exercises real detection and acts as a tripwire: if a
CORRECTNESS gate were ever mis-added here, that raw-detection test would flip and fail.

INVARIANT (constitutional — do not weaken a gate to make a bad output pass): only gates that
survived adversarial refutation in workflow ``x2-gate-triage`` (CONFIRM verdict) appear here. NEVER
add a CORRECTNESS gate (grounding / cross-employer or cross-section leakage / fabrication /
metric-fidelity / schema-count / REAL_LLM / graph-skill binding). See plans/x2-gate-slimdown-b4e8d2.md.
"""

from __future__ import annotations

from dataclasses import is_dataclass, replace
from typing import Any, Iterable

# Adversarially-verified STYLE gates safe to run-but-not-block (workflow x2-gate-triage CONFIRM).
# Each is cosmetic prose/format hygiene whose failure is not a correctness/safety loss.
STYLE_WARN_GATE_IDS: frozenset[str] = frozenset(
    {
        "x2_no_em_dash",  # em-dash (—) formatting ban — not a grounding/safety concern
        "x2_no_first_person",  # third-person convention — a slipped pronoun is cosmetic
        "x2_ibm_narrative_forbidden_opener",  # mechanical-opener style (currently declared-only; no-op)
        "x2_narrative_base_prose_ngram_overlap",  # soft anti-hydration heuristic; the HARD structural
        #   anti-hydration gate (graph_only_no_base_resume) remains a FAIL, so this is calibration-tolerant
    }
)

WARN_ONLY_MARKER = "[WARN_ONLY] would_fail:"


def _gate_id(result: Any) -> str:
    if is_dataclass(result):
        return str(getattr(result, "gate_id", "") or "")
    if isinstance(result, dict):
        return str(result.get("gate_id") or "")
    return ""


def _is_fail(result: Any) -> bool:
    if is_dataclass(result):
        return getattr(result, "pass_", True) is False
    if isinstance(result, dict):
        return result.get("pass") is False or result.get("pass_") is False
    return False


def soften_warn_only(results: Iterable[Any]) -> list[Any]:
    """Return ``results`` with STYLE_WARN_GATE_IDS *failures* flipped to pass=True + WARN marker.

    Severity-only: detection is untouched (the gate already ran). Correctness gates are never in the
    set, so they are never softened. Works across every per-lane ``X2GateResult`` dataclass (they all
    share ``gate_id`` / ``pass_`` / ``failure_reason``) and across dict-shaped results.
    """
    out: list[Any] = []
    for result in results:
        if _gate_id(result) in STYLE_WARN_GATE_IDS and _is_fail(result):
            if is_dataclass(result):
                reason = str(getattr(result, "failure_reason", "") or "")
                out.append(
                    replace(result, pass_=True, failure_reason=f"{WARN_ONLY_MARKER} {reason}".strip())
                )
                continue
            if isinstance(result, dict):
                reason = str(result.get("failure_reason") or "")
                softened = dict(result)
                softened["pass"] = True
                softened["pass_"] = True
                softened["failure_reason"] = f"{WARN_ONLY_MARKER} {reason}".strip()
                out.append(softened)
                continue
        out.append(result)
    return out


def warn_only_fires(results: Iterable[Any]) -> list[str]:
    """Telemetry: gate_ids of demoted gates that ACTUALLY fired (would have failed) this run.

    The presence of ``WARN_ONLY_MARKER`` in a result's ``failure_reason`` is the durable, grep-able
    evidence used to decide (after N runs, plan W4) whether a demoted gate can be retired outright.
    """
    fires: list[str] = []
    for result in results:
        rid = _gate_id(result)
        if rid not in STYLE_WARN_GATE_IDS:
            continue
        reason = ""
        if is_dataclass(result):
            reason = str(getattr(result, "failure_reason", "") or "")
        elif isinstance(result, dict):
            reason = str(result.get("failure_reason") or "")
        if reason.startswith(WARN_ONLY_MARKER):
            fires.append(rid)
    return fires


__all__ = ["STYLE_WARN_GATE_IDS", "WARN_ONLY_MARKER", "soften_warn_only", "warn_only_fires"]

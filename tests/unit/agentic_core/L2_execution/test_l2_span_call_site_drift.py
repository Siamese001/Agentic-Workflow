"""AST-based guard against L2 span call-site drift.

Walks every Python file under ``agentic_core/L2_execution/`` (production
code, not tests) and finds every literal string passed as the first
positional argument to a call whose attribute is ``.span(...)``. Asserts
that every such literal is in ``all_l2_span_names()``.

Why this exists
---------------
On 2026-04-26, three E1 spans in ``l2_phase_pipeline.py`` were renamed
from canonical ``l2.e1.prep.{receive,authority_bind,environment_freeze}``
to non-existent ``l2.e1.prep.{frozen_inputs,frozen_caps,frozen_budget}``
between commits. The behavioral OTEL emission tests still passed because
they only sampled a few span names per phase. The drift was caught only
when a human reviewer noticed.

This test closes the gap: every literal call-site is checked against the
canonical registry. A future typo or unauthorized rename fails the test
at collection time, before it can ship.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from agentic_core.L2_execution.observability.l2_spans import all_l2_span_names

REPO_ROOT = Path(__file__).resolve().parents[4]
L2_PROD_ROOT = REPO_ROOT / "agentic_core" / "L2_execution"
assert L2_PROD_ROOT.exists(), (
    f"L2_PROD_ROOT not found at {L2_PROD_ROOT}. parents[4] resolved "
    f"REPO_ROOT={REPO_ROOT} which is wrong; fix the parent count."
)

# Files that legitimately contain string literals matching the L2 span
# regex but are NOT call-sites (the registry itself, the producer-list
# constants in the emitter, and the docstring in the emitter module).
_NON_CALLSITE_FILES = frozenset(
    {
        # Vocabulary registry — the canonical source.
        "agentic_core/L2_execution/observability/l2_spans.py",
        # Emitter producer-list constants intentionally hold literals so
        # the matrix sees this file as a real producer; they are NOT
        # `.span()` call-sites — the AST walker only checks calls.
        "agentic_core/L2_execution/observability/l2_otel_emitter.py",
    }
)


def _iter_l2_python_files() -> list[Path]:
    return [
        p for p in L2_PROD_ROOT.rglob("*.py")
        if "__pycache__" not in p.parts
    ]


def _extract_span_call_literals(path: Path) -> list[tuple[str, int]]:
    """Return (literal, line_number) pairs for every `.span("...")` call."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError):
        return []
    out: list[tuple[str, int]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        # Match emitter.span("...") / emt.span("...") / self._emitter.span("...")
        if not (isinstance(func, ast.Attribute) and func.attr == "span"):
            continue
        if not node.args:
            continue
        first = node.args[0]
        # Only flag literal strings — variables (e.g. iterating a tuple)
        # are checked at the tuple-literal level by another sweep below.
        if isinstance(first, ast.Constant) and isinstance(first.value, str):
            out.append((first.value, first.lineno))
    return out


_L2_SPAN_RE = __import__("re").compile(r"^l2\.[a-z][a-z0-9_\.]+$")


def _extract_l2_span_shaped_literals(path: Path) -> list[tuple[str, int]]:
    """Return (literal, line) for every string in the AST that matches the L2 span regex.

    Producer detection is intentionally permissive: any string literal in
    production code that looks like ``l2.<group>.<name>`` counts as
    evidence the span has a producer. This catches both
    ``emitter.span("l2.e1.prep.receive")`` and the more common
    ``for span_name in ("l2.e1.prep.receive", ...): with emitter.span(...)``
    pattern without needing per-pattern AST heuristics.
    """
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError):
        return []
    out: list[tuple[str, int]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if _L2_SPAN_RE.match(node.value):
                out.append((node.value, node.lineno))
    return out


def _all_call_site_literals() -> list[tuple[str, str, int]]:
    """Strict call-site sweep: only literals passed directly to `.span()`.

    Used by :func:`test_every_l2_span_call_site_uses_canonical_name` to
    catch typos at the exact emit point.
    """
    results: list[tuple[str, str, int]] = []
    for p in _iter_l2_python_files():
        rel = p.relative_to(REPO_ROOT).as_posix()
        if rel in _NON_CALLSITE_FILES:
            continue
        for literal, lineno in _extract_span_call_literals(p):
            results.append((rel, literal, lineno))
    return results


def _all_producer_literals() -> set[str]:
    """Permissive sweep: every L2-span-shaped string in production code.

    Catches `for span_name in ("l2....", ...):` patterns plus direct
    `.span()` literals plus producer-list constants. Used by the
    SHADOW_ONLY guard.
    """
    out: set[str] = set()
    for p in _iter_l2_python_files():
        rel = p.relative_to(REPO_ROOT).as_posix()
        if rel == "agentic_core/L2_execution/observability/l2_spans.py":
            continue  # exclude the registry — that's the source of truth
        for literal, _lineno in _extract_l2_span_shaped_literals(p):
            out.add(literal)
    return out


# ---------------------------------------------------------------------- tests
def test_every_l2_span_call_site_uses_canonical_name():
    """Every literal in `.span(...)` must be in `all_l2_span_names()`.

    A failure here means a producer is calling
    ``emitter.span("typo.name")`` for a span that is not in the canonical
    vocabulary. The L2SpanEmitter would raise
    ``L2SpanAttributeViolation`` at runtime, but only if that path is
    exercised by a test — this guard catches it deterministically.
    """
    canonical = set(all_l2_span_names())
    sites = _all_call_site_literals()
    violations: list[str] = [
        f"{path}:{line}: {literal!r} is not in the L2 span registry"
        for path, literal, line in sites
        if literal not in canonical
    ]
    assert not violations, (
        "L2 span call-site drift detected — every literal passed to "
        "emitter.span() must be in agentic_core.L2_execution.observability."
        "l2_spans.all_l2_span_names():\n  " + "\n  ".join(violations)
    )


def test_every_canonical_span_has_at_least_one_call_site():
    """Inverse guard: every span in the registry must have a producer.

    Without this assertion, a span could be added to the registry but
    never emitted — that exact case is what the cross-check audit
    surfaced as ``SHADOW_ONLY``. Producer detection is permissive: any
    L2-span-shaped literal anywhere in production code counts (covers
    ``.span(literal)`` direct calls, ``for x in (literal, ...):`` loops,
    and producer-list constants in :mod:`l2_otel_emitter`).
    """
    canonical = set(all_l2_span_names())
    producers = _all_producer_literals()
    unemitted = sorted(canonical - producers)
    assert not unemitted, (
        "Canonical L2 spans declared in l2_spans.py but never emitted by "
        "any producer (SHADOW_ONLY drift):\n  " + "\n  ".join(unemitted)
    )


@pytest.mark.parametrize("path,literal,line", _all_call_site_literals())
def test_each_call_site_literal_is_canonical(path, literal, line):
    """One assertion per call-site for granular failure messages."""
    assert literal in set(all_l2_span_names()), (
        f"{path}:{line}: span literal {literal!r} is not in the L2 "
        "span registry. Add it to l2_spans.py or fix the typo."
    )

"""
tests/runtime/test_otel_emitter_adapter.py

W7 acceptance: validates the OTEL emitter adapter is plug-and-play
ready -- a future Author-Gate session can drop it into a live runtime
layer without modifying the contract or breaking Phase 5/6/7 proofs.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_core.runtime.prove_requirements.otel_contract import (
    RUNTIME_SPAN_NAMES,
    validate_trace,
)
from agentic_core.runtime.prove_requirements.otel_emitter import RuntimeSpanEmitter


def test_emitter_constructible() -> None:
    e = RuntimeSpanEmitter.for_request(scenario="live_test")
    trace = e.finalize()
    assert trace.scenario == "live_test"
    assert trace.spans == []  # no spans emitted yet


def test_emitter_emits_canonical_span() -> None:
    e = RuntimeSpanEmitter.for_request()
    with e.span("runtime.request"):
        with e.span("u0.intake", policy_hash="abc"):
            pass
    trace = e.finalize()
    assert len(trace.spans) == 2
    names = {s.name for s in trace.spans}
    assert names == {"runtime.request", "u0.intake"}


def test_emitter_rejects_unknown_span_name() -> None:
    e = RuntimeSpanEmitter.for_request()
    with pytest.raises(ValueError, match="unknown runtime span name"):
        with e.span("evil.bypass"):
            pass


def test_emitter_produces_validatable_trace() -> None:
    """A trace produced by the emitter must pass validate_trace -- proving
    plug-and-play compatibility with Phase 5 contract checks."""
    e = RuntimeSpanEmitter.for_request(scenario="live_smoke")
    with e.span("runtime.request", route_id="R3_SIMPLE_GROUNDED_READ"):
        with e.span("u0.intake", policy_hash="ph"):
            pass
        with e.span("l1.plan"):
            pass
    trace = e.finalize().to_dict()
    ok, errs = validate_trace(trace)
    assert ok, f"emitter-produced trace failed validation: {errs}"


def test_emitter_flush_writes_disk(tmp_path: Path) -> None:
    e = RuntimeSpanEmitter.for_request(scenario="live_flush_test")
    with e.span("runtime.request"):
        with e.span("u0.intake"):
            pass
    out = e.flush(traces_dir=tmp_path)
    assert out is not None
    assert out.exists()
    assert out.parent == tmp_path
    assert out.name.startswith("live_live_flush_test_")


def test_emitter_flush_without_dir_returns_none() -> None:
    e = RuntimeSpanEmitter.for_request()
    with e.span("runtime.request"):
        pass
    assert e.flush() is None


def test_emitter_canonical_vocabulary_alignment() -> None:
    """The emitter must reject any name outside RUNTIME_SPAN_NAMES so
    drift between contract + live runtime is impossible."""
    e = RuntimeSpanEmitter.for_request()
    # A handful of canonical names round-trip through the emitter.
    for name in ("u0.intake", "l0.route_decision", "exit.x3.disposition", "uwg.commit_request"):
        assert name in RUNTIME_SPAN_NAMES
        with e.span(name):
            pass
    trace = e.finalize()
    assert len(trace.spans) == 4


def test_no_unexpected_live_wirings(repo_root: Path) -> None:
    """Constitutional honesty pin (updated W8).

    The proof-OTEL emitter is intentionally wired into a deliberately
    SHORT allow-list of production files. Any new wire-up MUST update
    this allow-list AND deliver its own ``test_l*_live_wireup.py``
    acceptance test (per author-gate-enforcement.md ADR-class
    decisions).

    W7 (initial): empty allow-list (adapter-only delivery).
    W8: adds `agentic_core/L6_observability/flywheel_promoter.py`
        with proof at `tests/runtime/test_l6_live_wireup.py`.
    W9 (this build): adds
        `agentic_core/L6_observability/execution/observability_recorder.py`
        with proof at `tests/runtime/test_l6_observability_recorder_wireup.py`.
    W10 (this build): adds
        `agentic_core/L0_routing/intake/pipeline.py` (u0.intake target)
        with proof at `tests/runtime/test_u0_intake_pipeline_wireup.py`.
    Future waves: extend the allow-list and add a corresponding
        live-wireup test per layer.
    """
    import re
    pattern = re.compile(r"from agentic_core\.runtime\.prove_requirements\.otel_emitter import")
    expected_wired = {
        # W8
        repo_root / "agentic_core" / "L6_observability" / "flywheel_promoter.py",
        # W9
        repo_root / "agentic_core" / "L6_observability" / "execution" / "observability_recorder.py",
        # W10
        repo_root / "agentic_core" / "L0_routing" / "intake" / "pipeline.py",
        # W11
        repo_root / "agentic_core" / "L0_routing" / "reasoning" / "v15_route_selector.py",
        # W12
        repo_root / "agentic_core" / "L0_routing" / "c0_retrieval" / "preflight.py",
        # W13
        repo_root / "agentic_core" / "L3_orchestration" / "exit_eval" / "v6" / "x3_dispositions.py",
    }
    layers = [
        repo_root / "agentic_core" / "L0_routing",
        repo_root / "agentic_core" / "L1_cognition",
        repo_root / "agentic_core" / "L2_execution",
        repo_root / "agentic_core" / "L3_orchestration",
        repo_root / "agentic_core" / "L4_state",
        repo_root / "agentic_core" / "L5_safety",
        repo_root / "agentic_core" / "L6_observability",
    ]
    found_wired: set[Path] = set()
    for layer_dir in layers:
        if not layer_dir.exists():
            continue
        for py in layer_dir.rglob("*.py"):
            try:
                txt = py.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            if pattern.search(txt):
                found_wired.add(py)
    unexpected = found_wired - expected_wired
    missing = expected_wired - found_wired
    assert not unexpected, (
        f"unexpected live wirings landed without updating this test: {sorted(unexpected)}"
    )
    assert not missing, (
        f"expected wirings missing -- did flywheel_promoter.py drop the import? {sorted(missing)}"
    )

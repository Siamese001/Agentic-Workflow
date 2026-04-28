"""Tests for factory X1G enable-flag semantics (v5 §X1G harness parity).

Plan ``exit-eval-v5-test-harden-1cb78d``.

``build_pipeline`` must accept ``"X1G"`` in ``gate_ids`` as a request to
enable the commit-path pass^k policy. The factory:

- MUST NOT try to build a grader-based Gate for X1G (it's pipeline-level).
- MUST require both ``consistency_store`` and ``consistency_policy`` when
  X1G is enabled.
- MUST still honor back-compat for ``["X1A","X1B","X1F"]``-style calls
  that don't include X1G.
- MUST validate that the ``x1g_v1.yaml`` governance rubric is present.
"""

from __future__ import annotations

import pytest

from agentic_core.L3_orchestration.exit_eval.bus import BusEmitter
from agentic_core.L3_orchestration.exit_eval.consistency import PassKStore
from agentic_core.L3_orchestration.exit_eval.factory import build_pipeline
from agentic_core.L3_orchestration.exit_eval.pipeline import ConsistencyPolicy


def _stub_bus() -> BusEmitter:
    captured: list = []
    return BusEmitter(sink=captured.append)


def test_x1g_alone_is_rejected():
    """X1G is a modifier — an X1G-only pipeline has nothing to gate."""
    bus = _stub_bus()
    with pytest.raises(KeyError, match="cannot be the only gate"):
        build_pipeline(
            ["X1G"],
            bus_emitter=bus,
            consistency_store=PassKStore(),
            consistency_policy=ConsistencyPolicy(k=3, theta=0.8),
        )


def test_x1g_with_missing_policy_raises():
    bus = _stub_bus()
    with pytest.raises(KeyError, match="consistency_store and/or consistency_policy"):
        build_pipeline(
            ["X1A", "X1G"],
            bus_emitter=bus,
            consistency_store=PassKStore(),
            # consistency_policy omitted
            grader_overrides={"policy_match": _PolicyMatchStub()},
        )


def test_x1g_with_missing_store_raises():
    bus = _stub_bus()
    with pytest.raises(KeyError, match="consistency_store and/or consistency_policy"):
        build_pipeline(
            ["X1A", "X1G"],
            bus_emitter=bus,
            consistency_policy=ConsistencyPolicy(k=3, theta=0.8),
            grader_overrides={"policy_match": _PolicyMatchStub()},
        )


class _PolicyMatchStub:
    """Minimal duck-typed Grader that always passes.

    The factory stores grader_overrides and the Gate consumes them via the
    structural Grader contract (``.grade(dimension, context) -> GraderOutput``
    and a ``grader_class`` attribute). Duck-typing avoids pulling the ABC
    registration into this test surface.
    """

    def __init__(self):
        from agentic_core.L3_orchestration.exit_eval.dimension import GraderClass

        self.grader_class = GraderClass.CODE_BASED

    def grade(self, dimension, context):  # noqa: ANN001
        from agentic_core.L3_orchestration.exit_eval.graders.base import GraderOutput

        return GraderOutput(score=1.0, abstain=False, evidence={})


def test_x1a_plus_x1g_builds_gate_for_x1a_only():
    """Mixed gate_ids must keep X1A as a Gate and enable X1G as policy."""
    bus = _stub_bus()
    store = PassKStore()
    policy = ConsistencyPolicy(k=2, theta=0.5)
    bundle = build_pipeline(
        ["X1A", "X1G"],
        bus_emitter=bus,
        consistency_store=store,
        consistency_policy=policy,
        grader_overrides={"policy_match": _PolicyMatchStub()},
    )
    assert len(bundle.gates) == 1
    assert bundle.gates[0].rubric.gate == "X1A"
    assert bundle.consistency_store is store


def test_x1g_without_request_does_not_require_store():
    """Back-compat: legacy callers without X1G never had to supply a store."""
    bus = _stub_bus()
    bundle = build_pipeline(
        ["X1A"],
        bus_emitter=bus,
        grader_overrides={"policy_match": _PolicyMatchStub()},
    )
    assert bundle.consistency_store is None
    assert len(bundle.gates) == 1

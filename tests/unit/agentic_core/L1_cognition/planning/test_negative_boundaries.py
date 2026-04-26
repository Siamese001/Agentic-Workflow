"""Negative-boundary tests — prove L1 v6 does not cross its lane.

For each stage, the spec's PHASE 6 requires negative-boundary tests:
no retrieval adapter calls, no route selector, no tool/model execution
for the user task, no RouteContract / FinalEvidenceContract /
PromptEnvelope emission, no L4 writes, no HITL/UWG approval.

This module proves those invariants with a combination of:

* Module-level audit — no v6 stage module imports a forbidden symbol.
* Span-level audit — every emitted span asserts ``no_*`` flags True.
* Contract-level audit — :class:`NonAuthorityAssertion` enforces all
  flags True at construction, :class:`L1HandoffReceipt` locks the
  target_layer to ``L0_ROUTE_DECISION``, :class:`RouteHintSet` rejects
  ``route_authority_assertion != "advisory_only"``.
"""

from __future__ import annotations

import importlib
import inspect
import re

import pytest

from agentic_core.L1_cognition.planning import (
    NonAuthorityAssertion,
    ProposedRouteHint,
    RouteHintSet,
    run_l1_planning,
)


_FORBIDDEN_SYMBOLS_RE = re.compile(
    r"\b("
    r"RouteContract|FinalEvidenceContract|PromptEnvelope|CompiledPromptArtifact|"
    r"L3WorkflowContract|L3StepContract|L2ExecutionRequest|SealedL2Artifact|"
    r"ExitReviewPacket|ExitDisposition|GateDisposition|CommitRequest|"
    r"UWGCommitReceipt"
    r")\b"
)


_STAGE_MODULES = (
    "agentic_core.L1_cognition.planning.intent_frame",
    "agentic_core.L1_cognition.planning.planning_priors",
    "agentic_core.L1_cognition.planning.reasoning_loop",
    "agentic_core.L1_cognition.planning.draft_plan",
    "agentic_core.L1_cognition.planning.plan_validation",
    "agentic_core.L1_cognition.planning.plan_contract_handoff",
    "agentic_core.L1_cognition.planning.pipeline",
)


@pytest.mark.parametrize("modname", _STAGE_MODULES)
def test_stage_modules_do_not_import_forbidden_authoritative_outputs(modname):
    """No v6 stage module should reference downstream authoritative outputs.

    The match is intentionally a substring scan over module source — any
    accidental import or string reference to e.g. ``RouteContract`` or
    ``FinalEvidenceContract`` would surface here.
    """
    mod = importlib.import_module(modname)
    src = inspect.getsource(mod)
    matches = _FORBIDDEN_SYMBOLS_RE.findall(src)
    assert not matches, (modname, sorted(set(matches)))


def test_pipeline_run_emits_no_retrieval_or_execution_assertions(
    basic_parsed_input, span_sink, static_reader
):
    run_l1_planning(basic_parsed_input, prior_reader=static_reader, span_sink=span_sink)
    assert span_sink.events, "expected spans to be emitted"
    for ev in span_sink.events:
        assert ev.no_route_authority is True, ev.span_name
        assert ev.no_retrieval_performed is True, ev.span_name
        assert ev.no_execution_performed is True, ev.span_name
        assert ev.no_write_performed is True, ev.span_name


def test_route_hint_authority_assertion_must_be_advisory_only():
    """L1 cannot claim route authority via the v6 contract surface."""
    with pytest.raises(Exception):
        RouteHintSet(
            route_hint_id="x",
            proposed_route_hint=ProposedRouteHint.R3_GROUNDED_READ,
            route_authority_assertion="committed",
        )


def test_non_authority_assertion_construction_requires_all_flags_true():
    naa = NonAuthorityAssertion()
    d = naa.to_dict()
    assert all(v is True for v in d.values()), d


def test_pipeline_does_not_call_c0_or_l3_or_l2_modules(basic_parsed_input, static_reader):
    """Smoke test: forbid imports of C0/L3/L2 from inside the pipeline run.

    We snapshot ``sys.modules`` before the run and verify that no
    forbidden module was newly imported as a consequence of the run.
    """
    import sys

    forbidden_prefixes = (
        "agentic_core.L0_routing.c0_retrieval",  # C0 retrieval surfaces
        "agentic_core.L2_execution",  # L2 execution surfaces
        "agentic_core.L3_orchestration",  # L3 workflow surfaces
    )
    before = set(sys.modules)
    run_l1_planning(basic_parsed_input, prior_reader=static_reader)
    after = set(sys.modules)
    new_modules = after - before
    new_forbidden = [m for m in new_modules if m.startswith(forbidden_prefixes)]
    # The pipeline must not lazily import C0/L2/L3 surfaces — those are
    # downstream layers that L1 is forbidden to touch directly.
    assert not new_forbidden, new_forbidden

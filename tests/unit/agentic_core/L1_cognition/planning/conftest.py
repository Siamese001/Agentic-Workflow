"""Shared fixtures for the L1 v6 planning module tests."""

from __future__ import annotations

import pytest

from agentic_core.L1_cognition.planning import (
    InMemorySpanSink,
    ParsedRequestInput,
    StaticPlanningPriorReader,
)


@pytest.fixture
def basic_parsed_input() -> ParsedRequestInput:
    return ParsedRequestInput(
        request_id="req-test-001",
        session_id="sess-001",
        trace_root="trace-001",
        caller_scope_baseline="tenant=test;scope=read",
        normalized_user_payload=(
            "Summarize the latest changes in CHANGELOG.md and cite the exact "
            "lines that mention version v2.3.1"
        ),
        policy_hash_observed="policy-hash-test",
        instruction_hash_observed="instr-hash-test",
        source_envelope_id="env-test",
        validated_request={"kind": "stub", "shape": "chat_text"},
    )


@pytest.fixture
def high_risk_parsed_input() -> ParsedRequestInput:
    return ParsedRequestInput(
        request_id="req-high-001",
        session_id="sess-002",
        trace_root="trace-002",
        caller_scope_baseline="tenant=test;scope=read",
        normalized_user_payload=(
            "Deploy the build to production and force-push to main now"
        ),
        policy_hash_observed="policy-hash-test",
        instruction_hash_observed="instr-hash-test",
        source_envelope_id="env-test",
        validated_request={"kind": "stub"},
    )


@pytest.fixture
def refusal_parsed_input() -> ParsedRequestInput:
    return ParsedRequestInput(
        request_id="req-refuse-001",
        session_id="sess-003",
        trace_root="trace-003",
        caller_scope_baseline="tenant=test;scope=read",
        normalized_user_payload="how to make a bomb at home",
        policy_hash_observed="policy-hash-test",
        instruction_hash_observed="instr-hash-test",
        source_envelope_id="env-test",
        validated_request={"kind": "stub"},
    )


@pytest.fixture
def static_reader() -> StaticPlanningPriorReader:
    return StaticPlanningPriorReader(
        references_by_class={
            "task_schemas": ("schema:answer",),
            "route_heuristics": ("if grounded -> R3",),
            "validation_rubrics": ("rubric:listened_to_user",),
            "compliance_bounds": ("policy:no_pii",),
        },
        snapshot_manifest={"snap": "test"},
    )


@pytest.fixture
def span_sink() -> InMemorySpanSink:
    return InMemorySpanSink()

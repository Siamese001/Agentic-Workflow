"""Observability events module — C0Event, FORBIDDEN_EVENT_FIELDS, metrics."""

from __future__ import annotations

import pytest

from agentic_core.L0_routing.c0_retrieval.events import (
    C0_METRIC_NAMES,
    C0Event,
    C0EventRecord,
    FORBIDDEN_EVENT_FIELDS,
)


class TestC0EventEnum:
    def test_all_pipeline_stages_have_events(self):
        # Stage transitions: preflight, plan, fetch, hydrate, graph, shape,
        # conflicts, score, gate, refine, contract emit/reject.
        names = {e.value for e in C0Event}
        for needle in (
            "PreflightEvaluated", "PreflightBlocked",
            "RetrievalPlanBuilt",
            "EvidenceFetched", "EvidenceHydrated",
            "GraphTraversed", "EvidenceShaped",
            "ConflictsDetected", "EvidenceScored",
            "GateFired",
            "RefineAttempted",
            "ContractEmitted", "ContractRejected",
        ):
            assert any(needle in n for n in names), f"missing event {needle}"

    def test_events_are_str_typed(self):
        for e in C0Event:
            assert isinstance(e.value, str)
            assert e.value.startswith("C0")


class TestForbiddenEventFields:
    def test_critical_payload_keys_forbidden(self):
        for k in (
            "evidence_text", "raw_text", "user_task_text",
            "credential", "auth_token", "api_key",
            "password", "secret",
            "answer", "answer_text", "model_response",
        ):
            assert k in FORBIDDEN_EVENT_FIELDS

    def test_event_record_rejects_forbidden_field(self):
        with pytest.raises(ValueError):
            C0EventRecord(
                event=C0Event.EVIDENCE_FETCHED,
                contract_id="c1", route_id="R3",
                fields={"evidence_text": "leaked!"},
            )

    def test_event_record_accepts_safe_fields(self):
        rec = C0EventRecord(
            event=C0Event.EVIDENCE_FETCHED,
            contract_id="c1", route_id="R3",
            fields={"chunk_count": 5, "latency_ms": 42},
        )
        assert rec.event == C0Event.EVIDENCE_FETCHED


class TestEventRecordTyping:
    def test_event_must_be_C0Event_enum(self):
        with pytest.raises(TypeError):
            C0EventRecord(
                event="not_an_enum",  # type: ignore[arg-type]
                contract_id="c1", route_id="R3",
            )


class TestMetricNames:
    def test_metric_names_non_empty(self):
        assert len(C0_METRIC_NAMES) > 0

    def test_all_metrics_prefixed(self):
        for name in C0_METRIC_NAMES:
            assert name.startswith("c0_")
            assert name.islower()
            assert " " not in name

"""Fail-closed and threading edge cases for RuntimeExhaustBundle l5_certification_ref."""

from __future__ import annotations

import pytest

from agentic_core.L6_observability.runtime_trace.runtime_exhaust_bundle import (
    RuntimeExhaustBundle,
    RuntimeExhaustCollector,
)


def _minimal_record(*, l5_ref: str = "") -> dict:
    return {
        "record_id": "rec-edge-1",
        "run_id": "run-edge",
        "stage": "test",
        "l5_certification_ref": l5_ref,
        "span_end_epoch": 1000.0,
    }


class TestRuntimeExhaustL5CertRefFailClosed:
    def test_bundle_constructor_rejects_empty_ref(self) -> None:
        with pytest.raises(ValueError, match="l5_certification_ref"):
            RuntimeExhaustBundle(
                raw_evidence_refs=("rec-1",),
                lineage_manifest={},
                stage_map={"rec-1": "test"},
                artifact_inventory=(),
                gap_report=(),
                ingest_quality_score=1.0,
                newest_span_age_seconds=0.0,
                bundle_id="bundle-edge",
                l5_certification_ref="",
            )

    def test_collect_without_ref_kwarg_or_record_fails(self) -> None:
        collector = RuntimeExhaustCollector()
        with pytest.raises(ValueError, match="l5_certification_ref"):
            collector.collect([_minimal_record()], now_epoch=1100.0)

    def test_collect_kwarg_ref_satisfies_post_init(self) -> None:
        collector = RuntimeExhaustCollector()
        bundle = collector.collect(
            [_minimal_record()],
            now_epoch=1100.0,
            l5_certification_ref="l5:test:binding:kwarg",
        )
        assert bundle.l5_certification_ref == "l5:test:binding:kwarg"

    def test_collect_reads_ref_from_first_record_with_value(self) -> None:
        collector = RuntimeExhaustCollector()
        records = [
            _minimal_record(),
            _minimal_record(l5_ref="l5:test:binding:from-record"),
        ]
        bundle = collector.collect(records, now_epoch=1100.0)
        assert bundle.l5_certification_ref == "l5:test:binding:from-record"

    def test_collect_kwarg_overrides_empty_record_field(self) -> None:
        collector = RuntimeExhaustCollector()
        bundle = collector.collect(
            [_minimal_record(l5_ref="")],
            now_epoch=1100.0,
            l5_certification_ref="l5:test:binding:override",
        )
        assert bundle.l5_certification_ref == "l5:test:binding:override"

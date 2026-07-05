from __future__ import annotations

import json
from pathlib import Path

from apps_rg.runtime.observability.trace_reconciliation import (
    TRACE_RECONCILED,
    TRACE_UNAVAILABLE,
    build_trace_reconciliation,
    emit_trace_reconciliation_artifacts,
)


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _provider_span() -> dict:
    return {
        "schema_version": "apps_rg_provider_attempt_span_v1",
        "span_kind": "provider_attempt",
        "attempt_kind": "requested",
        "attempt_index": 0,
        "provider": "external_claude",
        "model": "claude-sonnet-5",
        "provider_attempted": True,
        "provider_available": True,
        "runtime_generation_status": "REAL_LLM",
        "started_at_utc": "2026-06-20T16:00:00+00:00",
        "completed_at_utc": "2026-06-20T16:00:02+00:00",
        "duration_seconds": 2.0,
        "output_accepted": True,
    }


def test_reconciliation_warns_when_otel_unavailable_but_keeps_local_receipts(tmp_path: Path) -> None:
    _write_json(
        tmp_path / "provider_response.json",
        {"provider_attempt_spans": [_provider_span()]},
    )
    _write_json(tmp_path / "x3_disposition.json", {"x3_code": "X3_ALLOW"})

    doc = build_trace_reconciliation(
        artifact_dir=tmp_path,
        repo_root=tmp_path,
        section_id="executive_summary",
        run_id="run-1",
    )

    assert doc["trace_verdict"] == TRACE_UNAVAILABLE
    assert doc["otel_snapshot_available"] is False
    assert doc["local_provider_attempt_span_count"] == 1
    assert doc["summary"]["future_run_only"] is True
    assert any(row["check_id"] == "l7_provider_attempts.otel_mirror" for row in doc["rows"])


def test_reconciliation_records_malformed_local_json_issue(tmp_path: Path) -> None:
    (tmp_path / "provider_response.json").write_text("{", encoding="utf-8")

    doc = build_trace_reconciliation(
        artifact_dir=tmp_path,
        repo_root=tmp_path,
        section_id="executive_summary",
        run_id="run-1",
    )

    assert doc["local_json_load_issues"][0]["artifact"] == "provider_response.json"
    assert doc["local_json_load_issues"][0]["status"] == "parse_error"
    assert any(row["check_id"] == "local_json.provider_response.json" for row in doc["rows"])


def test_reconciliation_passes_when_otel_provider_mirror_matches(tmp_path: Path) -> None:
    _write_json(
        tmp_path / "provider_response.json",
        {"provider_attempt_spans": [_provider_span()]},
    )
    _write_json(tmp_path / "x3_disposition.json", {"x3_code": "X3_ALLOW"})

    doc = build_trace_reconciliation(
        artifact_dir=tmp_path,
        repo_root=tmp_path,
        section_id="executive_summary",
        run_id="run-1",
        otel_trace_snapshot={
            "trace_id": "trace-1",
            "spans": [
                {
                    "name": "apps_rg.provider_attempt",
                    "attributes": {
                        "span_kind": "provider_attempt",
                        "attempt_index": 0,
                        "provider": "external_claude",
                        "model": "claude-sonnet-5",
                        "duration_seconds": 2.0,
                    },
                },
                {
                    "name": "exit.x3.disposition_select",
                    "attributes": {"x3_disposition": "X3_ALLOW"},
                },
            ],
        },
    )

    assert doc["trace_verdict"] == TRACE_RECONCILED
    assert doc["otel_provider_attempt_span_count"] == 1
    assert doc["summary"]["fail_count"] == 0
    assert doc["summary"]["warn_count"] == 0


def test_emit_writes_json_and_jsonl(tmp_path: Path) -> None:
    paths = emit_trace_reconciliation_artifacts(
        artifact_dir=tmp_path,
        repo_root=tmp_path,
        section_id="summary",
        run_id="run-2",
    )

    assert paths["trace_reconciliation"].is_file()
    assert paths["trace_reconciliation_rows"].is_file()
    doc = json.loads(paths["trace_reconciliation"].read_text(encoding="utf-8"))
    assert doc["row_export_ref"] == "trace_reconciliation_rows.jsonl"

"""Post-run reconciliation between local apps_rg receipts and OTel snapshots.

The reconciliation artifact is consumed by apps_eval and L6. It never controls
the current run: local receipts stay authoritative, and unavailable OTel becomes
an observability gap instead of a product-path failure.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from apps_rg.runtime.providers.provider_attempt_spans import (
    TIMING_SUMMARY_SCHEMA_VERSION,
    summarize_provider_attempt_spans,
)

TRACE_RECONCILIATION_ARTIFACT = "trace_reconciliation.json"
TRACE_RECONCILIATION_ROWS_ARTIFACT = "trace_reconciliation_rows.jsonl"
L6_TRACE_OBSERVABILITY_SUMMARY_ARTIFACT = "l6_trace_observability_summary.json"
TRACE_RECONCILIATION_SCHEMA_VERSION = "apps_rg.trace_reconciliation.v1"
TRACE_RECONCILIATION_ROW_SCHEMA_VERSION = "apps_rg.trace_reconciliation.row.v1"
L6_TRACE_OBSERVABILITY_SUMMARY_SCHEMA_VERSION = "apps_rg.l6_trace_observability_summary.v1"

TRACE_RECONCILED = "TRACE_RECONCILED"
TRACE_PARTIAL = "TRACE_PARTIAL"
TRACE_MISMATCH = "TRACE_MISMATCH"
TRACE_UNAVAILABLE = "TRACE_UNAVAILABLE"

_NUMERIC_TEXT = re.compile(r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)$")

OTEL_SNAPSHOT_CANDIDATES = (
    "otel_trace_snapshot.json",
    "runtime_trace_snapshot.json",
    "trace_snapshot.json",
)

_UWG_LOCAL_ARTIFACTS = (
    "commit_request.json",
    "uwg_commit_receipt.json",
    "uwg_block_receipt.json",
    "uwg_validation_receipt.json",
    "state_commit_receipt.json",
)


@dataclass(frozen=True, slots=True)
class _JsonLoadResult:
    payload: Any
    status: str
    path: str
    error_type: str = ""
    error: str = ""

    def issue(self, *, artifact_name: str) -> dict[str, str]:
        return {
            "artifact": artifact_name,
            "path": self.path,
            "status": self.status,
            "error_type": self.error_type,
            "error": self.error,
        }


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical_digest(payload: Any) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return "sha256:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _repo_rel(repo_root: Path, path: Path) -> str | None:
    if not path.is_file():
        return None
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix().replace("\\", "/")


def _load_json(path: Path) -> Any:
    return _load_json_result(path).payload


def _load_json_result(path: Path) -> _JsonLoadResult:
    if not path.is_file():
        return _JsonLoadResult(payload=None, status="missing", path=path.as_posix())
    try:
        return _JsonLoadResult(
            payload=json.loads(path.read_text(encoding="utf-8")),
            status="loaded",
            path=path.as_posix(),
        )
    except OSError as exc:
        return _JsonLoadResult(
            payload=None,
            status="read_error",
            path=path.as_posix(),
            error_type=type(exc).__name__,
            error=str(exc),
        )
    except (json.JSONDecodeError, TypeError) as exc:
        return _JsonLoadResult(
            payload=None,
            status="parse_error",
            path=path.as_posix(),
            error_type=type(exc).__name__,
            error=str(exc),
        )


def _write_json(path: Path, payload: Mapping[str, Any]) -> Path:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return path


def _write_jsonl(path: Path, rows: list[Mapping[str, Any]]) -> Path:
    path.write_text(
        "".join(json.dumps(row, sort_keys=True, default=str) + "\n" for row in rows),
        encoding="utf-8",
        newline="\n",
    )
    return path


def _span_list(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [dict(item) for item in value if isinstance(item, Mapping)]


def _provider_attempt_spans_from_provider_response(
    doc: Mapping[str, Any] | None,
) -> tuple[list[dict[str, Any]], str]:
    if not isinstance(doc, Mapping):
        return [], "absent"
    reasoning_receipt = doc.get("reasoning_execution_receipt")
    if isinstance(reasoning_receipt, Mapping):
        fallback = reasoning_receipt.get("apps_rg_availability_fallback")
        if isinstance(fallback, Mapping):
            spans = _span_list(fallback.get("provider_attempt_spans"))
            if spans:
                return spans, "reasoning_execution_receipt.apps_rg_availability_fallback"

    provider_response = doc.get("provider_response")
    if isinstance(provider_response, Mapping):
        fallback = provider_response.get("apps_rg_availability_fallback")
        if isinstance(fallback, Mapping):
            spans = _span_list(fallback.get("provider_attempt_spans"))
            if spans:
                return spans, "provider_response.apps_rg_availability_fallback"
        spans = _span_list(provider_response.get("provider_attempt_spans"))
        if spans:
            return spans, "provider_response.provider_attempt_spans"

    spans = _span_list(doc.get("provider_attempt_spans"))
    if spans:
        return spans, "provider_attempt_spans"
    return [], "absent"


def _load_local_provider_attempt_spans(
    artifact_dir: Path,
) -> tuple[list[dict[str, Any]], str, list[dict[str, str]]]:
    issues: list[dict[str, str]] = []
    provider_result = _load_json_result(artifact_dir / "provider_response.json")
    if provider_result.status not in {"loaded", "missing"}:
        issues.append(provider_result.issue(artifact_name="provider_response.json"))
    provider_doc = provider_result.payload
    spans, source = _provider_attempt_spans_from_provider_response(
        provider_doc if isinstance(provider_doc, Mapping) else None
    )
    if spans:
        return spans, source, issues
    manifest_result = _load_json_result(artifact_dir / "section_l7_binding_manifest.json")
    if manifest_result.status not in {"loaded", "missing"}:
        issues.append(manifest_result.issue(artifact_name="section_l7_binding_manifest.json"))
    manifest = manifest_result.payload
    if isinstance(manifest, Mapping):
        manifest_spans = _span_list(manifest.get("provider_attempt_spans"))
        if manifest_spans:
            return manifest_spans, "section_l7_binding_manifest.provider_attempt_spans", issues
    return [], "absent", issues


def _load_otel_snapshot(
    artifact_dir: Path,
    repo_root: Path,
    otel_trace_snapshot: Mapping[str, Any] | None,
) -> tuple[dict[str, Any] | None, str | None]:
    if otel_trace_snapshot is not None:
        return dict(otel_trace_snapshot), "provided"
    for name in OTEL_SNAPSHOT_CANDIDATES:
        path = artifact_dir / name
        doc = _load_json(path)
        if isinstance(doc, Mapping):
            return dict(doc), _repo_rel(repo_root, path)
    return None, None


def _otel_attr_value(value: Any) -> Any:
    if not isinstance(value, Mapping):
        return value
    for key in (
        "stringValue",
        "intValue",
        "doubleValue",
        "boolValue",
        "arrayValue",
    ):
        if key in value:
            return value[key]
    return value


def _normalize_attrs(value: Any) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return {str(k): v for k, v in value.items()}
    if isinstance(value, list):
        attrs: dict[str, Any] = {}
        for item in value:
            if not isinstance(item, Mapping):
                continue
            key = str(item.get("key") or "")
            if not key:
                continue
            attrs[key] = _otel_attr_value(item.get("value"))
        return attrs
    return {}


def _span_name(span: Mapping[str, Any]) -> str:
    return str(span.get("name") or span.get("span_name") or "")


def _span_attrs(span: Mapping[str, Any]) -> dict[str, Any]:
    attrs = _normalize_attrs(span.get("attributes"))
    if not attrs and isinstance(span.get("attrs"), Mapping):
        attrs = _normalize_attrs(span.get("attrs"))
    return attrs


def _extract_scope_spans(resource_spans: Any) -> list[dict[str, Any]]:
    spans: list[dict[str, Any]] = []
    if not isinstance(resource_spans, list):
        return spans
    for resource in resource_spans:
        if not isinstance(resource, Mapping):
            continue
        scopes = resource.get("scopeSpans") or resource.get("scope_spans") or []
        if not isinstance(scopes, list):
            continue
        for scope in scopes:
            if not isinstance(scope, Mapping):
                continue
            for span in scope.get("spans") or []:
                if isinstance(span, Mapping):
                    spans.append(dict(span))
    return spans


def _extract_packet_spans(otel_spans: Any) -> list[dict[str, Any]]:
    spans: list[dict[str, Any]] = []
    if not isinstance(otel_spans, Mapping):
        return spans
    for bucket in otel_spans.values():
        if not isinstance(bucket, Mapping):
            continue
        for name, records in bucket.items():
            if not isinstance(records, list):
                continue
            for record in records:
                if isinstance(record, Mapping):
                    rec = dict(record)
                    rec.setdefault("name", str(name))
                    spans.append(rec)
    return spans


def _extract_otel_spans(snapshot: Mapping[str, Any] | None) -> list[dict[str, Any]]:
    if not isinstance(snapshot, Mapping):
        return []
    direct = snapshot.get("spans")
    if isinstance(direct, list):
        return [dict(item) for item in direct if isinstance(item, Mapping)]
    nested_trace = snapshot.get("trace")
    if isinstance(nested_trace, Mapping) and isinstance(nested_trace.get("spans"), list):
        return [dict(item) for item in nested_trace["spans"] if isinstance(item, Mapping)]
    resource_spans = _extract_scope_spans(snapshot.get("resourceSpans") or snapshot.get("resource_spans"))
    if resource_spans:
        return resource_spans
    packet_spans = _extract_packet_spans(snapshot.get("otel_spans"))
    if packet_spans:
        return packet_spans
    return []


def _attr(attrs: Mapping[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in attrs and attrs[key] not in (None, ""):
            return attrs[key]
    return None


def _is_provider_attempt_span(span: Mapping[str, Any]) -> bool:
    name = _span_name(span).lower()
    attrs = _span_attrs(span)
    if "provider_attempt" in name:
        return True
    kind = str(_attr(attrs, "span_kind", "apps_rg.span_kind") or "").lower()
    if kind == "provider_attempt":
        return True
    provider = _attr(attrs, "provider", "apps_rg.provider")
    attempt_index = _attr(attrs, "attempt_index", "apps_rg.attempt_index")
    return provider not in (None, "") and attempt_index not in (None, "")


def _provider_key(span: Mapping[str, Any], *, from_otel: bool = False) -> tuple[str, str, str]:
    if from_otel:
        attrs = _span_attrs(span)
        attempt_index = _attr(attrs, "attempt_index", "apps_rg.attempt_index")
        return (
            str(attempt_index if attempt_index is not None else ""),
            str(_attr(attrs, "provider", "apps_rg.provider") or ""),
            str(_attr(attrs, "model", "apps_rg.model") or ""),
        )
    return (
        str(span.get("attempt_index") if span.get("attempt_index") is not None else ""),
        str(span.get("provider") or ""),
        str(span.get("model") or ""),
    )


def _as_seconds(value: Any, *, millis: bool = False) -> float | None:
    if not isinstance(value, (int, float)):
        text = str(value).strip()
        if not _NUMERIC_TEXT.fullmatch(text):
            return None
        value = float(text)
    seconds = float(value) / 1000.0 if millis else float(value)
    return round(max(seconds, 0.0), 6)


def _otel_duration_seconds(span: Mapping[str, Any]) -> float | None:
    attrs = _span_attrs(span)
    direct = _as_seconds(_attr(attrs, "duration_seconds", "apps_rg.duration_seconds"))
    if direct is not None:
        return direct
    latency = _as_seconds(
        _attr(attrs, "latency_ms", "apps_rg.latency_ms") or span.get("latency_ms"),
        millis=True,
    )
    return latency


def _row(
    *,
    run_id: str,
    section_id: str,
    stage_id: str,
    check_id: str,
    verdict: str,
    severity: str,
    reason: str,
    observed_value: Any = None,
    expected_value: Any = None,
    source_refs: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    row_key = f"{run_id}|{section_id}|{stage_id}|{check_id}"
    return {
        "schema_version": TRACE_RECONCILIATION_ROW_SCHEMA_VERSION,
        "row_id": hashlib.sha256(row_key.encode("utf-8")).hexdigest()[:20],
        "run_id": run_id,
        "section_id": section_id,
        "stage_id": stage_id,
        "check_id": check_id,
        "verdict": verdict,
        "severity": severity,
        "reason": reason,
        "observed_value": observed_value,
        "expected_value": expected_value,
        "source_refs": dict(source_refs or {}),
        "future_run_only": True,
    }


def _local_artifact_refs(repo_root: Path, artifact_dir: Path) -> dict[str, str | None]:
    names = (
        "provider_response.json",
        "x1d_llm_judge_outputs.json",
        "x2_gate_outputs.json",
        "x3_disposition.json",
        "exit_review_packet.json",
        "l6_v40_shadow_eval_package.json",
        *_UWG_LOCAL_ARTIFACTS,
    )
    return {name: _repo_rel(repo_root, artifact_dir / name) for name in names}


def _x3_code(artifact_dir: Path) -> str:
    x3 = _load_json(artifact_dir / "x3_disposition.json")
    if isinstance(x3, Mapping):
        return str(x3.get("x3_code") or x3.get("disposition") or "")
    return ""


def _otel_x3_values(spans: list[Mapping[str, Any]]) -> list[str]:
    values: list[str] = []
    for span in spans:
        attrs = _span_attrs(span)
        value = _attr(attrs, "x3_disposition", "apps_rg.x3_disposition")
        if value:
            values.append(str(value))
    return values


def build_trace_reconciliation(
    *,
    artifact_dir: Path,
    repo_root: Path,
    section_id: str,
    run_id: str = "",
    otel_trace_snapshot: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the reconciliation payload without writing files."""
    artifact_dir = Path(artifact_dir)
    repo_root = Path(repo_root)
    effective_run_id = run_id or artifact_dir.name
    local_refs = _local_artifact_refs(repo_root, artifact_dir)
    local_provider_spans, local_provider_source, local_json_issues = _load_local_provider_attempt_spans(
        artifact_dir
    )
    local_timing_summary = summarize_provider_attempt_spans(local_provider_spans)
    otel_snapshot, otel_snapshot_ref = _load_otel_snapshot(artifact_dir, repo_root, otel_trace_snapshot)
    otel_spans = _extract_otel_spans(otel_snapshot)
    otel_provider_spans = [span for span in otel_spans if _is_provider_attempt_span(span)]
    otel_available = otel_snapshot is not None

    rows: list[dict[str, Any]] = []
    rows.append(
        _row(
            run_id=effective_run_id,
            section_id=section_id,
            stage_id="L7",
            check_id="otel_snapshot.available",
            verdict="PASS" if otel_available else "WARN",
            severity="WARN",
            reason=(
                "OTel snapshot available for post-run reconciliation"
                if otel_available
                else "OTel snapshot unavailable; local receipts remain authoritative"
            ),
            observed_value={"span_count": len(otel_spans), "snapshot_ref": otel_snapshot_ref},
            expected_value="bounded OTel trace snapshot or explicit unavailable receipt",
            source_refs={"otel_snapshot_ref": otel_snapshot_ref},
        )
    )

    for issue in local_json_issues:
        rows.append(
            _row(
                run_id=effective_run_id,
                section_id=section_id,
                stage_id="L7",
                check_id=f"local_json.{issue['artifact']}",
                verdict="WARN",
                severity="WARN",
                reason="local JSON artifact could not be loaded; reconciliation continues from available receipts",
                observed_value=issue,
                expected_value="valid JSON or intentionally absent optional artifact",
                source_refs={"artifact_path": issue["path"]},
            )
        )

    rows.append(
        _row(
            run_id=effective_run_id,
            section_id=section_id,
            stage_id="L7",
            check_id="l7_provider_attempts.local_receipts",
            verdict="PASS" if local_provider_spans else "WARN",
            severity="WARN",
            reason=(
                "local provider-attempt receipts present"
                if local_provider_spans
                else "no local provider-attempt receipts found"
            ),
            observed_value=local_timing_summary,
            expected_value=TIMING_SUMMARY_SCHEMA_VERSION,
            source_refs={"provider_attempt_span_source": local_provider_source},
        )
    )

    local_provider_keys = [_provider_key(span) for span in local_provider_spans]
    otel_provider_keys = [_provider_key(span, from_otel=True) for span in otel_provider_spans]
    if not local_provider_spans:
        provider_verdict = "NOT_APPLICABLE"
        provider_reason = "no local provider-attempt receipts to mirror"
    elif not otel_available:
        provider_verdict = "WARN"
        provider_reason = "OTel unavailable; provider-attempt mirror could not be checked"
    elif local_provider_keys == otel_provider_keys:
        provider_verdict = "PASS"
        provider_reason = "OTel provider-attempt spans match local receipt order"
    else:
        provider_verdict = "FAIL"
        provider_reason = "OTel provider-attempt spans do not match local receipt order"
    rows.append(
        _row(
            run_id=effective_run_id,
            section_id=section_id,
            stage_id="L7",
            check_id="l7_provider_attempts.otel_mirror",
            verdict=provider_verdict,
            severity="MAJOR",
            reason=provider_reason,
            observed_value={
                "local_provider_keys": local_provider_keys,
                "otel_provider_keys": otel_provider_keys,
            },
            expected_value="same provider attempt identity/order",
            source_refs={"provider_attempt_span_source": local_provider_source},
        )
    )

    timing_drifts: list[dict[str, Any]] = []
    if otel_available and local_provider_keys == otel_provider_keys:
        for local_span, otel_span in zip(local_provider_spans, otel_provider_spans, strict=False):
            local_duration = _as_seconds(local_span.get("duration_seconds"))
            otel_duration = _otel_duration_seconds(otel_span)
            if local_duration is None or otel_duration is None:
                continue
            drift = round(abs(local_duration - otel_duration), 6)
            if drift > 0.25:
                timing_drifts.append(
                    {
                        "provider": local_span.get("provider"),
                        "attempt_index": local_span.get("attempt_index"),
                        "local_duration_seconds": local_duration,
                        "otel_duration_seconds": otel_duration,
                        "drift_seconds": drift,
                    }
                )
    rows.append(
        _row(
            run_id=effective_run_id,
            section_id=section_id,
            stage_id="L7",
            check_id="l7_provider_attempts.timing_drift",
            verdict="FAIL" if timing_drifts else "PASS" if otel_available and local_provider_keys == otel_provider_keys else "NOT_APPLICABLE",
            severity="MAJOR",
            reason=(
                "provider-attempt timing drift exceeds tolerance"
                if timing_drifts
                else "provider-attempt timing drift not observed or not applicable"
            ),
            observed_value=timing_drifts,
            expected_value="<=0.25s duration drift when both sides expose timing",
            source_refs={"provider_attempt_span_source": local_provider_source},
        )
    )

    local_x3 = _x3_code(artifact_dir)
    otel_x3 = _otel_x3_values(otel_spans)
    if not local_x3:
        x3_verdict = "NOT_APPLICABLE"
        x3_reason = "local X3 artifact not present in this artifact directory"
    elif not otel_available:
        x3_verdict = "WARN"
        x3_reason = "OTel unavailable; X3 span mirror could not be checked"
    elif local_x3 in otel_x3:
        x3_verdict = "PASS"
        x3_reason = "OTel X3 disposition attribute matches local X3"
    else:
        x3_verdict = "FAIL"
        x3_reason = "OTel X3 disposition attribute missing or mismatched"
    rows.append(
        _row(
            run_id=effective_run_id,
            section_id=section_id,
            stage_id="X3",
            check_id="x3_disposition.otel_mirror",
            verdict=x3_verdict,
            severity="MAJOR",
            reason=x3_reason,
            observed_value={"local_x3": local_x3, "otel_x3_values": otel_x3},
            expected_value="local X3 code present in OTel span attributes",
            source_refs={"x3_disposition_ref": local_refs.get("x3_disposition.json")},
        )
    )

    uwg_refs = {name: ref for name, ref in local_refs.items() if name in _UWG_LOCAL_ARTIFACTS and ref}
    uwg_otel = [
        _span_name(span)
        for span in otel_spans
        if "uwg" in _span_name(span).lower()
    ]
    rows.append(
        _row(
            run_id=effective_run_id,
            section_id=section_id,
            stage_id="UWG",
            check_id="uwg_handoff.otel_mirror",
            verdict=(
                "PASS"
                if uwg_refs and (uwg_otel or not otel_available)
                else "NOT_APPLICABLE"
                if not uwg_refs
                else "WARN"
            ),
            severity="WARN",
            reason=(
                "UWG local refs present and OTel unavailable or mirrored"
                if uwg_refs and (uwg_otel or not otel_available)
                else "no UWG refs in this artifact directory"
                if not uwg_refs
                else "UWG refs present but no OTel UWG span found"
            ),
            observed_value={"uwg_local_refs": uwg_refs, "uwg_otel_spans": uwg_otel},
            expected_value="UWG local receipt plus optional mirrored OTel span",
            source_refs=uwg_refs,
        )
    )

    fail_count = sum(1 for row in rows if row["verdict"] == "FAIL")
    warn_count = sum(1 for row in rows if row["verdict"] == "WARN")
    if not otel_available:
        trace_verdict = TRACE_UNAVAILABLE
    elif fail_count:
        trace_verdict = TRACE_MISMATCH
    elif warn_count:
        trace_verdict = TRACE_PARTIAL
    else:
        trace_verdict = TRACE_RECONCILED

    return {
        "schema_version": TRACE_RECONCILIATION_SCHEMA_VERSION,
        "generated_at_utc": _utc_now(),
        "producer": "apps_rg.runtime.observability.trace_reconciliation",
        "run_id": effective_run_id,
        "section_id": section_id,
        "trace_root": str((otel_snapshot or {}).get("trace_root") or (otel_snapshot or {}).get("trace_id") or ""),
        "trace_verdict": trace_verdict,
        "otel_snapshot_available": otel_available,
        "otel_snapshot_ref": otel_snapshot_ref,
        "otel_span_count": len(otel_spans),
        "otel_provider_attempt_span_count": len(otel_provider_spans),
        "local_provider_attempt_span_count": len(local_provider_spans),
        "local_provider_attempt_span_source": local_provider_source,
        "local_json_load_issues": local_json_issues,
        "local_provider_attempt_timing_summary": local_timing_summary,
        "local_artifact_refs": local_refs,
        "summary": {
            "row_count": len(rows),
            "fail_count": fail_count,
            "warn_count": warn_count,
            "not_applicable_count": sum(1 for row in rows if row["verdict"] == "NOT_APPLICABLE"),
            "proof_authority": "local_receipts",
            "current_run_mutation_assertion": False,
            "future_run_only": True,
        },
        "rows_digest": _canonical_digest(rows),
        "rows": rows,
    }


def emit_trace_reconciliation_artifacts(
    *,
    artifact_dir: Path,
    repo_root: Path,
    section_id: str,
    run_id: str = "",
    otel_trace_snapshot: Mapping[str, Any] | None = None,
) -> dict[str, Path]:
    """Write reconciliation JSON + JSONL row artifacts and return their paths."""
    artifact_dir = Path(artifact_dir)
    artifact_dir.mkdir(parents=True, exist_ok=True)
    doc = build_trace_reconciliation(
        artifact_dir=artifact_dir,
        repo_root=repo_root,
        section_id=section_id,
        run_id=run_id,
        otel_trace_snapshot=otel_trace_snapshot,
    )
    rows = [dict(row) for row in doc["rows"]]
    rows_path = _write_jsonl(artifact_dir / TRACE_RECONCILIATION_ROWS_ARTIFACT, rows)
    doc = {
        **doc,
        "row_export_ref": TRACE_RECONCILIATION_ROWS_ARTIFACT,
        "row_export_digest": _canonical_digest(rows),
    }
    doc_path = _write_json(artifact_dir / TRACE_RECONCILIATION_ARTIFACT, doc)
    summary_path = _write_json(
        artifact_dir / L6_TRACE_OBSERVABILITY_SUMMARY_ARTIFACT,
        build_l6_trace_observability_summary(doc),
    )
    return {
        "trace_reconciliation": doc_path,
        "trace_reconciliation_rows": rows_path,
        "l6_trace_observability_summary": summary_path,
    }


def _row_verdict_by_check(rows: list[Mapping[str, Any]], check_id: str) -> str:
    for row in rows:
        if str(row.get("check_id") or "") == check_id:
            return str(row.get("verdict") or "UNKNOWN")
    return "NOT_OBSERVED"


def build_l6_trace_observability_summary(reconciliation: Mapping[str, Any]) -> dict[str, Any]:
    """Build a compact L6-only trace health rollup from reconciliation evidence."""
    rows = [dict(row) for row in reconciliation.get("rows", []) if isinstance(row, Mapping)]
    summary = reconciliation.get("summary")
    summary_doc = dict(summary) if isinstance(summary, Mapping) else {}
    return {
        "schema_version": L6_TRACE_OBSERVABILITY_SUMMARY_SCHEMA_VERSION,
        "run_id": str(reconciliation.get("run_id") or ""),
        "section_id": str(reconciliation.get("section_id") or ""),
        "trace_verdict": str(reconciliation.get("trace_verdict") or TRACE_UNAVAILABLE),
        "otel_snapshot_available": bool(reconciliation.get("otel_snapshot_available") is True),
        "provider_attempt_mirror_status": _row_verdict_by_check(rows, "l7_provider_attempts.otel_mirror"),
        "x3_mirror_status": _row_verdict_by_check(rows, "x3_disposition.otel_mirror"),
        "uwg_mirror_status": _row_verdict_by_check(rows, "uwg_handoff.otel_mirror"),
        "warn_count": int(summary_doc.get("warn_count") or 0),
        "fail_count": int(summary_doc.get("fail_count") or 0),
        "row_count": int(summary_doc.get("row_count") or len(rows)),
        "proof_authority": "local_receipts",
        "current_run_mutation_assertion": False,
        "direct_l4_write_assertion": False,
        "durable_write_assertion": False,
        "future_run_only": True,
    }


__all__ = [
    "TRACE_MISMATCH",
    "TRACE_PARTIAL",
    "TRACE_RECONCILED",
    "TRACE_RECONCILIATION_ARTIFACT",
    "TRACE_RECONCILIATION_ROWS_ARTIFACT",
    "TRACE_RECONCILIATION_ROW_SCHEMA_VERSION",
    "TRACE_RECONCILIATION_SCHEMA_VERSION",
    "TRACE_UNAVAILABLE",
    "L6_TRACE_OBSERVABILITY_SUMMARY_ARTIFACT",
    "L6_TRACE_OBSERVABILITY_SUMMARY_SCHEMA_VERSION",
    "build_l6_trace_observability_summary",
    "build_trace_reconciliation",
    "emit_trace_reconciliation_artifacts",
]

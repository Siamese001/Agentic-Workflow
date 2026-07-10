"""Aggregate app-owned generation and judge attempt evidence for core L2."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping


def _read_json_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"unreadable attempt evidence {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"attempt evidence must be a JSON object: {path}")
    return value


def _first_attempt_spans(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, Mapping):
        spans = value.get("provider_attempt_spans")
        if isinstance(spans, list):
            return [dict(item) for item in spans if isinstance(item, Mapping)]
        for nested in value.values():
            found = _first_attempt_spans(nested)
            if found:
                return found
    elif isinstance(value, list):
        for nested in value:
            found = _first_attempt_spans(nested)
            if found:
                return found
    return []


def _validate_judge_attempts(path: Path, attempts: Any) -> list[dict[str, Any]]:
    if not isinstance(attempts, list):
        raise ValueError(f"judge attempt ledger attempts must be a list: {path}")
    rows = [dict(item) for item in attempts if isinstance(item, Mapping)]
    by_provider: dict[str, list[int]] = {}
    for row in rows:
        provider = str(row.get("provider_key") or "").strip()
        attempt = row.get("attempt")
        if not provider or isinstance(attempt, bool) or not isinstance(attempt, int):
            raise ValueError(f"invalid judge attempt identity in {path}")
        by_provider.setdefault(provider, []).append(attempt)
    for provider, observed in by_provider.items():
        expected = list(range(1, len(observed) + 1))
        if observed != expected:
            raise ValueError(
                f"noncontiguous judge attempts for {provider} in {path}: "
                f"observed={observed} expected={expected}"
            )
    return rows


def build_runtime_execution_witness(
    *,
    artifact_dir: Any,
    step_results: list[dict[str, Any]],
    context: Mapping[str, Any],
) -> dict[str, Any]:
    """Build the generic witness mapping consumed by the core L2 entrypoint."""
    _ = step_results, context
    root = Path(artifact_dir) if artifact_dir else None
    if root is None or not root.is_dir():
        return {
            "attempt_evidence_status": "NOT_OBSERVED",
            "generation_provider_attempt_count": 0,
            "judge_attempt_count": 0,
            "attempt_evidence_refs": [],
        }

    refs: list[str] = []
    judge_count = 0
    for path in sorted(root.rglob("judge_attempt_ledger.json")):
        payload = _read_json_object(path)
        if payload.get("schema_version") != "apps_rg.judge_attempt_ledger.v1":
            raise ValueError(f"unexpected judge attempt ledger schema: {path}")
        judge_count += len(_validate_judge_attempts(path, payload.get("attempts")))
        refs.append(path.relative_to(root).as_posix())

    generation_ids: set[str] = set()
    for path in sorted(root.rglob("provider_response.json")):
        payload = _read_json_object(path)
        spans = _first_attempt_spans(payload)
        if not spans:
            continue
        for index, span in enumerate(spans, start=1):
            stable_id = str(
                span.get("attempt_id")
                or span.get("span_id")
                or f"{path.relative_to(root).as_posix()}#{index}"
            )
            generation_ids.add(stable_id)
        refs.append(path.relative_to(root).as_posix())

    return {
        "attempt_evidence_status": "COMPLETE" if refs else "NOT_OBSERVED",
        "generation_provider_attempt_count": len(generation_ids),
        "judge_attempt_count": judge_count,
        "attempt_evidence_refs": sorted(set(refs)),
    }


__all__ = ["build_runtime_execution_witness"]

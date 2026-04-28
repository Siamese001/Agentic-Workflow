"""Tier 6 enforcement readiness gate.

Aggregates Tier 6 metadata blockers and linkage statuses across the four
generated surface files. Returns READY only when all 21 selected Tier 6
rows are LINKED_LITERAL with no blockers; otherwise BLOCKED.

Metadata-only gate. Does NOT execute tests, replay machinery, OTEL
exporters, or the proof harness. Does NOT claim proof or coverage.

Status vocabulary: READY | BLOCKED | LINKED_LITERAL | LINKED_CONCEPTUAL
| PARTIAL_LINK | NO_LINK.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Set

REPO_ROOT = Path(__file__).resolve().parents[3]
ARTIFACTS_DIR = REPO_ROOT / "artifacts" / "runtime" / "requirements_proof"

SOURCE_FILES = (
    "tier6_requirements_index.generated.json",
    "tier6_coverage_matrix.generated.json",
    "tier6_implementation_map.generated.json",
    "tier6_artifact_linkage.generated.json",
)

OUT_RESULT = "tier6_enforcement_gate_result.json"
OUT_REPORT = "tier6_enforcement_gate_report.md"

GATE_NAME = "tier6_enforcement_readiness"
EXPECTED_TIER6_TOTAL = 21
ACCEPTABLE_FOR_READY = {"LINKED_LITERAL"}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(name: str) -> Dict[str, Any]:
    path = ARTIFACTS_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"Required source not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def evaluate() -> Dict[str, Any]:
    blockers_by_req: Dict[str, Set[str]] = defaultdict(set)
    statuses_by_req: Dict[str, Set[str]] = defaultdict(set)
    seen_req_ids: Set[str] = set()
    source_files_loaded: List[str] = []
    missing_sources: List[str] = []

    for fname in SOURCE_FILES:
        try:
            payload = _load_json(fname)
        except FileNotFoundError:
            missing_sources.append(fname)
            continue
        source_files_loaded.append(fname)
        for row in payload.get("rows", []):
            rid = row.get("step1_req_id") or ""
            if not rid:
                continue
            seen_req_ids.add(rid)
            for b in row.get("blockers") or []:
                blockers_by_req[rid].add(b)
            ls = row.get("linkage_status") or ""
            if ls:
                statuses_by_req[rid].add(ls)

    if missing_sources:
        return {
            "gate_name": GATE_NAME,
            "result": "BLOCKED",
            "tier6_total": EXPECTED_TIER6_TOTAL,
            "tier6_seen": 0,
            "blocked_count": EXPECTED_TIER6_TOTAL,
            "blocker_counts": {},
            "blocking_status_counts": {},
            "linkage_status_counts": {},
            "blocking_reasons": [f"Missing required source file: {fname}" for fname in missing_sources],
            "evaluated_at_utc": _utc_now_iso(),
            "source_files_checked": source_files_loaded,
            "per_req_detail": [],
        }

    blocking_req_ids: Set[str] = set()
    blocker_counts: Counter = Counter()
    blocking_status_counts: Counter = Counter()
    linkage_status_counts: Counter = Counter()

    for rid in seen_req_ids:
        rid_blockers = blockers_by_req.get(rid, set())
        rid_statuses = statuses_by_req.get(rid, set())
        for b in rid_blockers:
            blocker_counts[b] += 1
        for s in rid_statuses:
            linkage_status_counts[s] += 1
        is_blocked = bool(rid_blockers) or any(s not in ACCEPTABLE_FOR_READY for s in rid_statuses)
        if is_blocked:
            blocking_req_ids.add(rid)
            for s in rid_statuses:
                if s not in ACCEPTABLE_FOR_READY:
                    blocking_status_counts[s] += 1

    if len(seen_req_ids) != EXPECTED_TIER6_TOTAL:
        for rid in seen_req_ids - blocking_req_ids:
            blocking_req_ids.add(rid)

    result_status = (
        "READY" if (len(seen_req_ids) == EXPECTED_TIER6_TOTAL and not blocking_req_ids) else "BLOCKED"
    )

    per_req_detail: List[Dict[str, Any]] = []
    for rid in sorted(seen_req_ids):
        per_req_detail.append(
            {
                "step1_req_id": rid,
                "linkage_statuses": sorted(statuses_by_req.get(rid, set())),
                "blockers": sorted(blockers_by_req.get(rid, set())),
                "blocked": rid in blocking_req_ids,
            }
        )

    return {
        "gate_name": GATE_NAME,
        "result": result_status,
        "tier6_total": EXPECTED_TIER6_TOTAL,
        "tier6_seen": len(seen_req_ids),
        "blocked_count": len(blocking_req_ids),
        "blocker_counts": dict(blocker_counts),
        "blocking_status_counts": dict(blocking_status_counts),
        "linkage_status_counts": dict(linkage_status_counts),
        "blocking_reasons": _build_blocking_reasons(
            len(seen_req_ids),
            blocker_counts,
            blocking_status_counts,
        ),
        "evaluated_at_utc": _utc_now_iso(),
        "source_files_checked": source_files_loaded,
        "per_req_detail": per_req_detail,
    }


def _build_blocking_reasons(
    seen_count: int,
    blocker_counts: Mapping[str, int],
    blocking_status_counts: Mapping[str, int],
) -> List[str]:
    reasons: List[str] = []
    if seen_count != EXPECTED_TIER6_TOTAL:
        reasons.append(f"Tier 6 row count mismatch: seen={seen_count} expected={EXPECTED_TIER6_TOTAL}")
    for b, n in sorted(blocker_counts.items()):
        reasons.append(f"Blocker {b} present on {n} row(s)")
    for s, n in sorted(blocking_status_counts.items()):
        reasons.append(f"Linkage status {s} present on {n} row(s) (not LINKED_LITERAL)")
    return reasons


def write_result(result: Mapping[str, Any]) -> Path:
    path = ARTIFACTS_DIR / OUT_RESULT
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return path


def write_report(result: Mapping[str, Any]) -> Path:
    lines: List[str] = []
    lines.append("# Tier 6 Enforcement Readiness Gate Report")
    lines.append("")
    lines.append(f"- Gate: `{result['gate_name']}`")
    lines.append(f"- Result: **{result['result']}**")
    lines.append(f"- Evaluated at: {result['evaluated_at_utc']}")
    lines.append(f"- Tier 6 seen / expected: {result['tier6_seen']} / {result['tier6_total']}")
    lines.append(f"- Blocked count: {result['blocked_count']}")
    lines.append("")
    lines.append("## Linkage status counts")
    for k, v in sorted(result.get("linkage_status_counts", {}).items()):
        lines.append(f"- {k}: {v}")
    lines.append("")
    lines.append("## Blocker counts")
    for k, v in sorted(result.get("blocker_counts", {}).items()):
        lines.append(f"- {k}: {v}")
    lines.append("")
    if result.get("blocking_reasons"):
        lines.append("## Blocking reasons")
        for r in result["blocking_reasons"]:
            lines.append(f"- {r}")
        lines.append("")
    lines.append("## Source files checked")
    for f in result.get("source_files_checked", []):
        lines.append(f"- {f}")
    lines.append("")
    lines.append("## Statement")
    lines.append("")
    lines.append(
        "Metadata-only gate. No tests, no proof harness, no replay machinery, "
        "no OTEL exporter, and no runtime behavior was executed. "
        "BLOCKED is the expected first-pass result and is preferred over "
        "fake readiness."
    )
    path = ARTIFACTS_DIR / OUT_REPORT
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def main() -> int:
    result = evaluate()
    write_result(result)
    write_report(result)
    print(f"Gate: {result['gate_name']}")
    print(f"Result: {result['result']}")
    print(f"Tier 6 seen / expected: {result['tier6_seen']} / {result['tier6_total']}")
    print(f"Blocked count: {result['blocked_count']}")
    print(f"Blocker counts: {result['blocker_counts']}")
    print(f"Linkage status counts: {result['linkage_status_counts']}")
    return 0 if result["result"] == "READY" else 2


if __name__ == "__main__":
    raise SystemExit(main())

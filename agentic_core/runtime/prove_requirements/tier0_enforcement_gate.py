"""
Tier 0 enforcement readiness gate.

Fail-closed gate over the Tier 0 generated metadata files. READY only when
all 17 Tier 0 rows are present, every row carries a non-blank ``step1_req_id``,
no row is ``PARTIAL_LINK`` or ``NO_LINK``, and no blockers remain across any
of the four surfaces (requirements_index, coverage_matrix, implementation_map,
artifact_linkage). Otherwise BLOCKED.

This gate is metadata-only. It does not execute runtime code, tests, proof
harnesses, replay, or OTEL exporters. It does not modify source files.
"""

from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Sequence, Set


GATE_NAME = "tier0_enforcement_readiness"

_ARTIFACTS_DIR = Path("artifacts/runtime/requirements_proof")

_SOURCE_FILES: Sequence[str] = (
    "tier0_requirements_index.generated.json",
    "tier0_coverage_matrix.generated.json",
    "tier0_implementation_map.generated.json",
    "tier0_artifact_linkage.generated.json",
)

_OUT_RESULT = "tier0_enforcement_gate_result.json"
_OUT_REPORT = "tier0_enforcement_gate_report.md"

# Status values accepted for enforcement readiness. PARTIAL_LINK and NO_LINK
# are explicitly NOT accepted; LINKED_LITERAL is the canonical READY state.
ACCEPTABLE_FOR_READY: Set[str] = {"LINKED_LITERAL"}

# Statuses that must trigger BLOCKED.
BLOCKING_STATUSES: Set[str] = {"PARTIAL_LINK", "NO_LINK"}

# Blocker tags that, if present on any row in any source file, force BLOCKED.
BLOCKING_BLOCKERS: Set[str] = {
    "NEEDS_RUNTIME_FIELD",
    "NEEDS_ARTIFACT_FIELD",
    "NEEDS_REPLAY_FIELD",
    "NEEDS_EXPECTED_FAIL_REASON",
    "NEEDS_TEST_MAPPING",
}

EXPECTED_TIER0_TOTAL = 17


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(name: str) -> Dict[str, Any]:
    path = _ARTIFACTS_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"Required source not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def evaluate() -> Dict[str, Any]:
    """Aggregate blockers and statuses across the four source files."""
    # Per-REQ aggregation across all source surfaces.
    blockers_by_req: Dict[str, Set[str]] = defaultdict(set)
    blocking_status_by_req: Dict[str, Set[str]] = defaultdict(set)
    seen_req_ids_per_file: Dict[str, Set[str]] = {}
    file_row_counts: Dict[str, int] = {}
    blank_step1_violations: List[str] = []

    for fname in _SOURCE_FILES:
        payload = _load_json(fname)
        rows = payload.get("rows", [])
        file_row_counts[fname] = len(rows)
        seen: Set[str] = set()
        for row in rows:
            sid = row.get("step1_req_id") or ""
            if not sid.strip():
                blank_step1_violations.append(f"{fname}: blank step1_req_id row")
                continue
            seen.add(sid)
            for blk in row.get("blockers", []) or []:
                if blk in BLOCKING_BLOCKERS:
                    blockers_by_req[sid].add(blk)
            ls = row.get("linkage_status")
            if ls in BLOCKING_STATUSES:
                blocking_status_by_req[sid].add(ls)
            elif ls not in ACCEPTABLE_FOR_READY:
                # any non-LINKED_LITERAL status is a non-ready signal
                blocking_status_by_req[sid].add(ls or "MISSING_STATUS")
        seen_req_ids_per_file[fname] = seen

    # The set of REQ_IDs present in ANY of the four files.
    union_req_ids: Set[str] = set().union(*seen_req_ids_per_file.values())

    # Cross-file presence: a REQ_ID must appear in ALL four files.
    intersect_req_ids: Set[str] = set(union_req_ids)
    for ids in seen_req_ids_per_file.values():
        intersect_req_ids &= ids
    missing_in_some_file = sorted(union_req_ids - intersect_req_ids)

    # Aggregate blocker counts.
    blocker_counts: Dict[str, int] = defaultdict(int)
    for blks in blockers_by_req.values():
        for b in blks:
            blocker_counts[b] += 1

    # Status-based blocked count is derived from union of REQs with any
    # blocking_status OR any blocker.
    blocked_req_ids = sorted(set(blockers_by_req.keys()) | set(blocking_status_by_req.keys()))

    tier0_total = len(union_req_ids)

    # Determine result.
    reasons: List[str] = []
    if tier0_total != EXPECTED_TIER0_TOTAL:
        reasons.append(f"tier0_total={tier0_total} expected={EXPECTED_TIER0_TOTAL}")
    if blank_step1_violations:
        reasons.extend(blank_step1_violations)
    if missing_in_some_file:
        reasons.append(f"req_ids missing in some source file: {missing_in_some_file}")
    if blocked_req_ids:
        reasons.append(f"{len(blocked_req_ids)} REQ_IDs have blockers or non-ready linkage_status")

    result = "READY" if not reasons else "BLOCKED"

    return {
        "gate_name": GATE_NAME,
        "result": result,
        "evaluated_at": _utc_now_iso(),
        "tier0_total": tier0_total,
        "tier0_total_expected": EXPECTED_TIER0_TOTAL,
        "blocked_count": len(blocked_req_ids),
        "blocker_counts": dict(blocker_counts),
        "blocking_status_counts": _count_statuses(blocking_status_by_req),
        "blocked_req_ids": blocked_req_ids,
        "blocked_req_id_details": _detail_per_req(blockers_by_req, blocking_status_by_req),
        "missing_in_some_file": missing_in_some_file,
        "blank_step1_violations": blank_step1_violations,
        "file_row_counts": file_row_counts,
        "source_files_checked": list(_SOURCE_FILES),
        "reasons": reasons,
    }


def _count_statuses(statuses_by_req: Mapping[str, Set[str]]) -> Dict[str, int]:
    counter: Dict[str, int] = defaultdict(int)
    seen: Dict[str, Set[str]] = defaultdict(set)
    for sid, sset in statuses_by_req.items():
        for s in sset:
            if s not in seen[sid]:
                counter[s] += 1
                seen[sid].add(s)
    return dict(counter)


def _detail_per_req(
    blockers_by_req: Mapping[str, Set[str]],
    statuses_by_req: Mapping[str, Set[str]],
) -> List[Dict[str, Any]]:
    all_ids = sorted(set(blockers_by_req.keys()) | set(statuses_by_req.keys()))
    return [
        {
            "step1_req_id": sid,
            "blockers": sorted(blockers_by_req.get(sid, set())),
            "blocking_statuses": sorted(statuses_by_req.get(sid, set())),
        }
        for sid in all_ids
    ]


def write_result(result: Mapping[str, Any]) -> Path:
    path = _ARTIFACTS_DIR / _OUT_RESULT
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return path


def write_report(result: Mapping[str, Any]) -> Path:
    lines: List[str] = []
    lines.append("# Tier 0 Enforcement Readiness Gate Report")
    lines.append("")
    lines.append(f"Gate name: `{result['gate_name']}`")
    lines.append(f"Evaluated at: {result['evaluated_at']}")
    lines.append("")
    lines.append(f"## Result: **{result['result']}**")
    lines.append("")
    lines.append(
        "Fail-closed metadata gate. Result depends only on linkage metadata; no runtime proof was executed."
    )
    lines.append("")

    lines.append("## Counts")
    lines.append("")
    lines.append(
        f"- Tier 0 total observed: {result['tier0_total']} (expected: {result['tier0_total_expected']})"
    )
    lines.append(f"- Blocked REQ count: {result['blocked_count']}")
    lines.append("")

    lines.append("### Source File Row Counts")
    lines.append("")
    lines.append("| file | rows |")
    lines.append("|---|---:|")
    for f, n in result["file_row_counts"].items():
        lines.append(f"| {f} | {n} |")
    lines.append("")

    lines.append("### Blocker Counts (REQ_IDs with each blocker)")
    lines.append("")
    if result["blocker_counts"]:
        lines.append("| blocker | reqs |")
        lines.append("|---|---:|")
        for k in sorted(result["blocker_counts"].keys()):
            lines.append(f"| {k} | {result['blocker_counts'][k]} |")
    else:
        lines.append("(none)")
    lines.append("")

    lines.append("### Blocking-Status Counts (REQ_IDs with each non-ready linkage_status)")
    lines.append("")
    if result["blocking_status_counts"]:
        lines.append("| status | reqs |")
        lines.append("|---|---:|")
        for k in sorted(result["blocking_status_counts"].keys()):
            lines.append(f"| {k} | {result['blocking_status_counts'][k]} |")
    else:
        lines.append("(none)")
    lines.append("")

    # Group blocked REQ_IDs by blocker.
    grouped: Dict[str, List[str]] = defaultdict(list)
    for d in result["blocked_req_id_details"]:
        sid = d["step1_req_id"]
        for b in d["blockers"]:
            grouped[b].append(sid)
        for s in d["blocking_statuses"]:
            grouped[f"status:{s}"].append(sid)

    lines.append("## Blocked Tier 0 REQ_IDs by Blocker")
    lines.append("")
    if grouped:
        for key in sorted(grouped.keys()):
            lines.append(f"### {key}")
            for sid in grouped[key]:
                lines.append(f"- {sid}")
            lines.append("")
    else:
        lines.append("(none)")
        lines.append("")

    lines.append("## Reasons")
    lines.append("")
    if result["reasons"]:
        for r in result["reasons"]:
            lines.append(f"- {r}")
    else:
        lines.append("(none — gate is READY)")
    lines.append("")

    lines.append("## Statement")
    lines.append("")
    lines.append(
        "No runtime proof was executed. No tests, pytest runs, proof harnesses, replay, or OTEL exporters were invoked. This gate evaluates only the Tier 0 metadata under `artifacts/runtime/requirements_proof/`."
    )
    lines.append("")

    path = _ARTIFACTS_DIR / _OUT_REPORT
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def main() -> int:
    result = evaluate()
    result_path = write_result(result)
    report_path = write_report(result)

    print(f"Gate: {result['gate_name']}")
    print(f"Result: {result['result']}")
    print(f"Tier 0 total: {result['tier0_total']} / {result['tier0_total_expected']}")
    print(f"Blocked count: {result['blocked_count']}")
    print(f"Blocker counts: {result['blocker_counts']}")
    print(f"Blocking-status counts: {result['blocking_status_counts']}")
    print(f"Result file: {result_path}")
    print(f"Report file: {report_path}")
    # Fail-closed: BLOCKED -> non-zero exit. The expected outcome at this
    # stage is BLOCKED, so a non-zero exit code is the correct demonstration
    # that the gate fails closed.
    return 0 if result["result"] == "READY" else 2


if __name__ == "__main__":
    raise SystemExit(main())

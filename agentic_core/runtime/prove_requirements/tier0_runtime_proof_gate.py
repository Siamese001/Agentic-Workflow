"""Tier 0 runtime-proof gate.

Validates targeted runtime-proof evidence (static artifacts, replay-pair
fixtures, and targeted test files) for the 17 Tier 0 REQ_IDs.

This gate inspects on-disk artifacts only. It does NOT execute replay
machinery, OTEL exporters, the proof harness, or any runtime services.
It does NOT claim production runtime proof.

Status vocabulary: READY | BLOCKED.
"""

from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from agentic_core.runtime.prove_requirements.tier0_step1_metadata import (
    TIER0_REQ_IDS,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
ARTIFACTS_DIR = REPO_ROOT / "artifacts" / "runtime" / "requirements_proof"

SOURCE_FILES: Tuple[str, ...] = (
    "tier0_requirements_index.generated.json",
    "tier0_coverage_matrix.generated.json",
    "tier0_implementation_map.generated.json",
    "tier0_artifact_linkage.generated.json",
)

OUT_RESULT = "tier0_runtime_proof_gate_result.json"
OUT_REPORT = "tier0_runtime_proof_gate_report.md"

GATE_NAME = "tier0_runtime_proof_gate"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _row_iter(payload: Any) -> Sequence[Mapping[str, Any]]:
    if isinstance(payload, dict):
        for key in ("rows", "tier0_rows", "items", "entries"):
            value = payload.get(key)
            if isinstance(value, list):
                return value
        return []
    if isinstance(payload, list):
        return payload
    return []


def _resolve(repo_relative: str) -> Path:
    return REPO_ROOT / repo_relative


def _check_row(
    req_id: str,
    rows_per_surface: Mapping[str, Mapping[str, Any]],
    artifacts_seen: set,
    replay_pairs_seen: set,
) -> Tuple[List[str], int, int]:
    """Run all 11 checks for one REQ_ID across its four surface rows."""
    failures: List[str] = []
    canonical = set(TIER0_REQ_IDS)

    surfaces = list(rows_per_surface.values())
    if not surfaces:
        return [f"{req_id}: no rows found in any source surface"], 0, 0

    # Check 1: step1_req_id present (and canonical)
    if not req_id or req_id not in canonical:
        failures.append(f"{req_id}: not in canonical Tier 0 REQ_IDs")

    # Per-surface invariants (checks 1-4)
    for surface_name, row in rows_per_surface.items():
        if not row.get("step1_req_id"):
            failures.append(f"{req_id} [{surface_name}]: missing step1_req_id")
        if row.get("linkage_status") != "LINKED_LITERAL":
            failures.append(
                f"{req_id} [{surface_name}]: linkage_status="
                f"{row.get('linkage_status')!r} (expected LINKED_LITERAL)"
            )
        if row.get("blockers"):
            failures.append(f"{req_id} [{surface_name}]: non-empty blockers={row.get('blockers')}")
        if not (row.get("expected_fail_reason") or "").strip():
            failures.append(f"{req_id} [{surface_name}]: missing expected_fail_reason")

    # Use the index surface as the canonical row for ref lists.
    primary = rows_per_surface.get("index") or surfaces[0]
    expected_efr = (primary.get("expected_fail_reason") or "").strip()

    # Checks 5-7: ref paths exist on disk.
    for kind in ("test_refs", "artifact_refs", "replay_refs"):
        for ref in primary.get(kind) or []:
            if not _resolve(ref).is_file():
                failures.append(f"{req_id}: missing {kind} on disk: {ref}")

    # Checks 8-9 + 11: artifact / replay JSON content checks (when applicable).
    for ref in primary.get("artifact_refs") or []:
        path = _resolve(ref)
        if not path.is_file():
            continue
        artifacts_seen.add(ref)
        try:
            data = _load_json(path)
        except (OSError, json.JSONDecodeError) as exc:
            failures.append(f"{req_id}: cannot parse artifact {ref}: {exc}")
            continue
        if isinstance(data, dict):
            if "step1_req_id" in data and data["step1_req_id"] != req_id:
                failures.append(
                    f"{req_id}: artifact {ref} step1_req_id={data['step1_req_id']!r} (expected {req_id!r})"
                )
            if (
                "expected_fail_reason" in data
                and expected_efr
                and data["expected_fail_reason"] != expected_efr
            ):
                failures.append(
                    f"{req_id}: artifact {ref} expected_fail_reason="
                    f"{data['expected_fail_reason']!r} (expected {expected_efr!r})"
                )

    # Replay refs: per-file step1_req_id/EFR check (Check 9 + 11) and
    # per-pair invariant_digest match (Check 10).
    replay_paths = list(primary.get("replay_refs") or [])
    replay_payloads: Dict[str, Mapping[str, Any]] = {}
    for ref in replay_paths:
        path = _resolve(ref)
        if not path.is_file():
            continue
        try:
            data = _load_json(path)
        except (OSError, json.JSONDecodeError) as exc:
            failures.append(f"{req_id}: cannot parse replay {ref}: {exc}")
            continue
        if not isinstance(data, dict):
            continue
        replay_payloads[ref] = data
        if "step1_req_id" in data and data["step1_req_id"] != req_id:
            failures.append(
                f"{req_id}: replay {ref} step1_req_id={data['step1_req_id']!r} (expected {req_id!r})"
            )
        if "expected_fail_reason" in data and expected_efr and data["expected_fail_reason"] != expected_efr:
            failures.append(
                f"{req_id}: replay {ref} expected_fail_reason="
                f"{data['expected_fail_reason']!r} (expected {expected_efr!r})"
            )

    # Pair the replay files by run_id stem (run_1 / run_2) and verify
    # invariant_digest matches across the pair when both files carry it.
    pair_groups: Dict[str, List[Tuple[str, Mapping[str, Any]]]] = defaultdict(list)
    for ref, data in replay_payloads.items():
        stem = ref.replace("_run_1.json", "").replace("_run_2.json", "")
        pair_groups[stem].append((ref, data))
    for stem, members in pair_groups.items():
        if len(members) < 2:
            continue
        digests = [m[1].get("invariant_digest") for m in members]
        digests = [d for d in digests if d]
        if len(digests) < 2:
            continue
        replay_pairs_seen.add(stem)
        if len(set(digests)) != 1:
            failures.append(f"{req_id}: replay pair {stem} invariant_digest mismatch: {digests}")

    return failures, len(replay_payloads), len([v for v in pair_groups.values() if len(v) >= 2])


def evaluate(
    metadata_gate_status: Optional[str] = None,
    targeted_tests_status: Optional[str] = None,
    targeted_tests_run: Optional[Sequence[str]] = None,
) -> Dict[str, Any]:
    """Validate runtime-proof evidence for the 17 Tier 0 REQ_IDs."""
    source_files_checked: List[str] = []
    surfaces: Dict[str, Sequence[Mapping[str, Any]]] = {}
    for fname in SOURCE_FILES:
        path = ARTIFACTS_DIR / fname
        if not path.is_file():
            return {
                "gate_name": GATE_NAME,
                "result": "BLOCKED",
                "tier0_total": len(TIER0_REQ_IDS),
                "failed_count": len(TIER0_REQ_IDS),
                "failed_req_ids": list(TIER0_REQ_IDS),
                "checks_performed": 0,
                "artifacts_checked": [],
                "replay_pairs_checked": [],
                "targeted_tests_run": list(targeted_tests_run or ()),
                "source_files_checked": source_files_checked,
                "evaluated_at_utc": _utc_now_iso(),
                "blocking_reasons": [
                    f"Required source file missing: {path}",
                ],
                "metadata_gate_status": metadata_gate_status,
                "targeted_tests_status": targeted_tests_status,
            }
        source_files_checked.append(fname)
        surface_name = fname.split("_", 2)[1].split(".")[0]
        surfaces[surface_name] = _row_iter(_load_json(path))

    # Index rows by req_id per surface.
    rows_by_req: Dict[str, Dict[str, Mapping[str, Any]]] = defaultdict(dict)
    for surface_name, rows in surfaces.items():
        for row in rows:
            rid = row.get("step1_req_id") or ""
            if rid:
                rows_by_req[rid][surface_name] = row

    failed_req_ids: List[str] = []
    failure_detail: List[str] = []
    artifacts_checked: set = set()
    replay_pairs_checked: set = set()
    checks_performed = 0

    for req_id in TIER0_REQ_IDS:
        per_surface = rows_by_req.get(req_id, {})
        failures, _n_artifacts, _n_pairs = _check_row(
            req_id, per_surface, artifacts_checked, replay_pairs_checked
        )
        # 4 surface invariant checks * 4 fields + per-row evidence existence
        # checks + content checks. The exact count is bookkeeping only; we
        # report the number of (req_id, check-class) tuples evaluated.
        checks_performed += 11
        if failures:
            failed_req_ids.append(req_id)
            failure_detail.extend(failures)

    # Roll in metadata-gate and targeted-test outcomes.
    blocking_reasons: List[str] = list(failure_detail)
    if metadata_gate_status and metadata_gate_status != "READY":
        blocking_reasons.append(f"Metadata enforcement gate not READY (status={metadata_gate_status})")
        if "metadata_gate" not in failed_req_ids:
            failed_req_ids.append("metadata_gate")
    if targeted_tests_status and targeted_tests_status != "PASSED":
        blocking_reasons.append(f"Targeted tests not PASSED (status={targeted_tests_status})")
        if "targeted_tests" not in failed_req_ids:
            failed_req_ids.append("targeted_tests")

    result = "READY" if not blocking_reasons else "BLOCKED"

    return {
        "gate_name": GATE_NAME,
        "result": result,
        "tier0_total": len(TIER0_REQ_IDS),
        "failed_count": len(failed_req_ids),
        "failed_req_ids": failed_req_ids,
        "checks_performed": checks_performed,
        "artifacts_checked": sorted(artifacts_checked),
        "replay_pairs_checked": sorted(replay_pairs_checked),
        "targeted_tests_run": list(targeted_tests_run or ()),
        "source_files_checked": source_files_checked,
        "metadata_gate_status": metadata_gate_status,
        "targeted_tests_status": targeted_tests_status,
        "blocking_reasons": blocking_reasons,
        "evaluated_at_utc": _utc_now_iso(),
    }


def write_result(result: Mapping[str, Any]) -> Path:
    path = ARTIFACTS_DIR / OUT_RESULT
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return path


def write_report(result: Mapping[str, Any]) -> Path:
    lines: List[str] = []
    lines.append("# Tier 0 Runtime Proof Gate Report")
    lines.append("")
    lines.append(f"- Gate: `{result['gate_name']}`")
    lines.append(f"- Result: **{result['result']}**")
    lines.append(f"- Evaluated at: {result['evaluated_at_utc']}")
    lines.append(f"- Tier 0 total: {result['tier0_total']}")
    lines.append(f"- Failed count: {result['failed_count']}")
    lines.append(f"- Checks performed: {result['checks_performed']}")
    lines.append(f"- Metadata gate status: {result.get('metadata_gate_status')}")
    lines.append(f"- Targeted tests status: {result.get('targeted_tests_status')}")
    lines.append("")
    lines.append("## Source files checked")
    for f in result["source_files_checked"]:
        lines.append(f"- {f}")
    lines.append("")
    lines.append("## Artifacts checked")
    for a in result["artifacts_checked"]:
        lines.append(f"- {a}")
    lines.append("")
    lines.append("## Replay pairs checked")
    for p in result["replay_pairs_checked"]:
        lines.append(f"- {p}")
    lines.append("")
    lines.append("## Targeted tests run")
    for t in result["targeted_tests_run"]:
        lines.append(f"- {t}")
    lines.append("")
    if result["failed_req_ids"]:
        lines.append("## Failed REQ_IDs")
        for rid in result["failed_req_ids"]:
            lines.append(f"- {rid}")
        lines.append("")
    if result.get("blocking_reasons"):
        lines.append("## Blocking reasons")
        for reason in result["blocking_reasons"]:
            lines.append(f"- {reason}")
        lines.append("")
    path = ARTIFACTS_DIR / OUT_REPORT
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def main() -> int:
    result = evaluate()
    write_result(result)
    write_report(result)
    print(f"Gate: {result['gate_name']}")
    print(f"Result: {result['result']}")
    print(f"Failed REQ_IDs: {result['failed_req_ids']}")
    return 0 if result["result"] == "READY" else 1


if __name__ == "__main__":
    raise SystemExit(main())

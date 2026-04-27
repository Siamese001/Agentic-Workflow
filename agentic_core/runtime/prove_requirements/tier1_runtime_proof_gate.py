"""Tier 1 runtime-proof gate.

Validates targeted static evidence consistency for the 15 Tier 1 REQ_IDs
across the four generated metadata surfaces, the on-disk code/validator/
test/artifact/replay/negative-control references they declare, and the
JSON content of any artifact/replay payloads that carry ``step1_req_id``
or ``expected_fail_reason``.

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

REPO_ROOT = Path(__file__).resolve().parents[3]
ARTIFACTS_DIR = REPO_ROOT / "artifacts" / "runtime" / "requirements_proof"
SELECTION_PATH = (
    REPO_ROOT / "docs" / "reference" / "contracts" / "tier1" / "TIER1_SELECTION.json"
)

SOURCE_FILES: Tuple[str, ...] = (
    "tier1_requirements_index.generated.json",
    "tier1_coverage_matrix.generated.json",
    "tier1_implementation_map.generated.json",
    "tier1_artifact_linkage.generated.json",
)

OUT_RESULT = "tier1_runtime_proof_gate_result.json"
OUT_REPORT = "tier1_runtime_proof_gate_report.md"

GATE_NAME = "tier1_runtime_proof_gate"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _row_iter(payload: Any) -> Sequence[Mapping[str, Any]]:
    if isinstance(payload, dict):
        for key in ("rows", "tier1_rows", "items", "entries"):
            value = payload.get(key)
            if isinstance(value, list):
                return value
        return []
    if isinstance(payload, list):
        return payload
    return []


def _resolve(repo_relative: str) -> Path:
    return REPO_ROOT / repo_relative


def _load_tier1_req_ids() -> Tuple[str, ...]:
    if not SELECTION_PATH.is_file():
        return ()
    try:
        data = _load_json(SELECTION_PATH)
    except (OSError, json.JSONDecodeError):
        return ()
    selected = data.get("selected") if isinstance(data, dict) else None
    if not isinstance(selected, list):
        return ()
    return tuple(r.get("req_id", "") for r in selected if r.get("req_id"))


def _check_row(
    req_id: str,
    rows_per_surface: Mapping[str, Mapping[str, Any]],
    canonical: set,
    artifacts_seen: set,
    replay_pairs_seen: set,
    negative_controls_seen: set,
) -> Tuple[List[str], int, int, int]:
    """Run the 17-class checks for one Tier 1 REQ_ID."""
    failures: List[str] = []

    surfaces = list(rows_per_surface.values())
    if not surfaces:
        return [f"{req_id}: no rows found in any source surface"], 0, 0, 0

    # Check 1: step1_req_id canonical
    if not req_id or req_id not in canonical:
        failures.append(f"{req_id}: not in canonical Tier 1 REQ_IDs")

    # Per-surface invariants (checks 1-5)
    for surface_name, row in rows_per_surface.items():
        if not row.get("step1_req_id"):
            failures.append(f"{req_id} [{surface_name}]: missing step1_req_id")
        tier_val = (row.get("tier") or "").upper()
        if tier_val and tier_val != "TIER1":
            failures.append(f"{req_id} [{surface_name}]: tier={tier_val!r} (expected TIER1)")
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

    # Checks 6-12: ref paths exist on disk.
    for kind in (
        "code_refs",
        "validator_refs",
        "otel_span_refs",
        "test_refs",
        "artifact_refs",
        "replay_refs",
        "negative_control_refs",
    ):
        for ref in primary.get(kind) or []:
            if not _resolve(ref).is_file():
                failures.append(f"{req_id}: missing {kind} on disk: {ref}")

    # Check 8 secondary: declared span references must be non-empty
    if not (primary.get("otel_span_refs") or []):
        failures.append(f"{req_id}: no otel_span_refs declared")

    # Checks 13-14: artifact JSON content.
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
                    f"{req_id}: artifact {ref} step1_req_id={data['step1_req_id']!r} "
                    f"(expected {req_id!r})"
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

    # Checks 15-16: replay JSON content + invariant_digest pair stability.
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
                f"{req_id}: replay {ref} step1_req_id={data['step1_req_id']!r} "
                f"(expected {req_id!r})"
            )
        if (
            "expected_fail_reason" in data
            and expected_efr
            and data["expected_fail_reason"] != expected_efr
        ):
            failures.append(
                f"{req_id}: replay {ref} expected_fail_reason="
                f"{data['expected_fail_reason']!r} (expected {expected_efr!r})"
            )

    pair_groups: Dict[str, List[Tuple[str, Mapping[str, Any]]]] = defaultdict(list)
    for ref, data in replay_payloads.items():
        stem = ref.replace("_run_1.json", "").replace("_run_2.json", "")
        pair_groups[stem].append((ref, data))
    pairs_checked = 0
    for stem, members in pair_groups.items():
        if len(members) < 2:
            continue
        digests = [m[1].get("invariant_digest") for m in members]
        digests = [d for d in digests if d]
        if len(digests) < 2:
            continue
        replay_pairs_seen.add(stem)
        pairs_checked += 1
        if len(set(digests)) != 1:
            failures.append(f"{req_id}: replay pair {stem} invariant_digest mismatch: {digests}")

    # Check 17: negative-control artifact refs (when JSON) carry expected_fail_reason
    for ref in primary.get("negative_control_refs") or []:
        path = _resolve(ref)
        if not path.is_file():
            continue
        negative_controls_seen.add(ref)
        if not ref.endswith(".json"):
            continue
        try:
            data = _load_json(path)
        except (OSError, json.JSONDecodeError) as exc:
            failures.append(f"{req_id}: cannot parse negative_control {ref}: {exc}")
            continue
        if isinstance(data, dict) and "expected_fail_reason" in data:
            if expected_efr and data["expected_fail_reason"] != expected_efr:
                failures.append(
                    f"{req_id}: negative_control {ref} expected_fail_reason="
                    f"{data['expected_fail_reason']!r} (expected {expected_efr!r})"
                )

    return failures, len(replay_payloads), pairs_checked, len(primary.get("negative_control_refs") or [])


def evaluate(
    metadata_gate_status: Optional[str] = None,
    targeted_tests_status: Optional[str] = None,
    targeted_tests_run: Optional[Sequence[str]] = None,
) -> Dict[str, Any]:
    """Validate static-evidence consistency for the 15 Tier 1 REQ_IDs."""
    tier1_req_ids = _load_tier1_req_ids()
    canonical = set(tier1_req_ids)

    source_files_checked: List[str] = []
    surfaces: Dict[str, Sequence[Mapping[str, Any]]] = {}
    for fname in SOURCE_FILES:
        path = ARTIFACTS_DIR / fname
        if not path.is_file():
            return {
                "gate_name": GATE_NAME,
                "result": "BLOCKED",
                "tier1_total": len(tier1_req_ids),
                "failed_count": len(tier1_req_ids),
                "failed_req_ids": list(tier1_req_ids),
                "checks_performed": 0,
                "artifacts_checked": [],
                "replay_pairs_checked": [],
                "negative_controls_checked": [],
                "targeted_tests_run": list(targeted_tests_run or ()),
                "source_files_checked": source_files_checked,
                "metadata_gate_status": metadata_gate_status,
                "targeted_tests_status": targeted_tests_status,
                "blocking_reasons": [f"Required source file missing: {path}"],
                "evaluated_at_utc": _utc_now_iso(),
            }
        source_files_checked.append(fname)
        # tier1_<surface>.generated.json -> surface key is segment after "tier1_"
        # up to "_" before "generated" (e.g. "requirements", "coverage", ...).
        # Use the same convention as tier0: split('_',2)[1].split('.')[0]
        surface_name = fname.split("_", 2)[1].split(".")[0]
        surfaces[surface_name] = _row_iter(_load_json(path))

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
    negative_controls_checked: set = set()
    checks_performed = 0

    for req_id in tier1_req_ids:
        per_surface = rows_by_req.get(req_id, {})
        failures, _n_artifacts, _n_pairs, _n_neg = _check_row(
            req_id,
            per_surface,
            canonical,
            artifacts_checked,
            replay_pairs_checked,
            negative_controls_checked,
        )
        # 17 check classes per REQ_ID (bookkeeping only).
        checks_performed += 17
        if failures:
            failed_req_ids.append(req_id)
            failure_detail.extend(failures)

    blocking_reasons: List[str] = list(failure_detail)
    if metadata_gate_status and metadata_gate_status != "READY":
        blocking_reasons.append(
            f"Metadata enforcement gate not READY (status={metadata_gate_status})"
        )
        if "metadata_gate" not in failed_req_ids:
            failed_req_ids.append("metadata_gate")
    if targeted_tests_status and targeted_tests_status not in ("PASSED", "SKIPPED"):
        blocking_reasons.append(
            f"Targeted tests not PASSED (status={targeted_tests_status})"
        )
        if "targeted_tests" not in failed_req_ids:
            failed_req_ids.append("targeted_tests")

    result = "READY" if not blocking_reasons else "BLOCKED"

    return {
        "gate_name": GATE_NAME,
        "result": result,
        "tier1_total": len(tier1_req_ids),
        "failed_count": len(failed_req_ids),
        "failed_req_ids": failed_req_ids,
        "checks_performed": checks_performed,
        "artifacts_checked": sorted(artifacts_checked),
        "replay_pairs_checked": sorted(replay_pairs_checked),
        "negative_controls_checked": sorted(negative_controls_checked),
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
    lines.append("# Tier 1 Runtime Proof Gate Report")
    lines.append("")
    lines.append(f"- Gate: `{result['gate_name']}`")
    lines.append(f"- Result: **{result['result']}**")
    lines.append(f"- Evaluated at: {result['evaluated_at_utc']}")
    lines.append(f"- Tier 1 total: {result['tier1_total']}")
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
    lines.append("## Negative controls checked")
    for n in result["negative_controls_checked"]:
        lines.append(f"- {n}")
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

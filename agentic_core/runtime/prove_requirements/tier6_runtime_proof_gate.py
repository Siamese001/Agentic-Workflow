"""Tier 6 runtime/static proof gate.

Validates static-evidence consistency for all 21 Tier 6 REQ_IDs across
the four generated metadata surfaces, the Tier 6 reference-only policy
artifact, and the on-disk code/validator/test/artifact/replay/
negative-control references they declare.

Tier 6 is split-mode:

* **Mode A -- 6 MUST / RELEASE_BLOCKING rows**
  Full static evidence consistency: code/validator/test/artifact/
  replay/negative-control refs must exist on disk; artifact + replay
  JSONs that carry ``step1_req_id`` / ``expected_fail_reason`` must
  match the row; replay pairs (run_1/run_2) must share the same
  ``invariant_digest``.

* **Mode B -- 15 REFERENCE / NON_BLOCKING_REFERENCE rows**
  Reference-only consistency: ``release_gate_rule`` must be
  ``NON_BLOCKING_REFERENCE``; ``requirement_strength`` must be
  ``REFERENCE``; ``code_refs``/``validator_refs`` must point at
  ``reference_only_policy_refs.py``; ``artifact_refs`` must include
  ``tier6_reference_only_policy.json``; the policy artifact must
  itself be valid (correct ``policy_name``, ``total_reference_only_rows``,
  membership of the row's REQ_ID in ``reference_only_req_ids``, and the
  documented rule + caveat strings).

This gate inspects on-disk artifacts only. It does NOT execute replay
machinery, OTEL exporters, the proof harness, or any runtime services.
It does NOT claim production runtime proof. Reference-only rows are NOT
treated as runtime-proof rows.

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
SELECTION_PATH = REPO_ROOT / "docs" / "reference" / "contracts" / "tier6" / "TIER6_SELECTION.json"

SOURCE_FILES: Tuple[str, ...] = (
    "tier6_requirements_index.generated.json",
    "tier6_coverage_matrix.generated.json",
    "tier6_implementation_map.generated.json",
    "tier6_artifact_linkage.generated.json",
)

POLICY_ARTIFACT_REL = "artifacts/runtime/requirements_proof/tier6_reference_only_policy.json"
POLICY_NAME = "TIER6_NON_BLOCKING_REFERENCE_POLICY"
EXPECTED_REFERENCE_ONLY_TOTAL = 15
REFERENCE_ONLY_POLICY_REFS_PATH = (
    "agentic_core/runtime/prove_requirements/tier6_refs/reference_only_policy_refs.py"
)
TIER6_TARGETED_TEST = "tests/runtime/test_tier6_final_rows_fixtures.py"

OUT_RESULT = "tier6_runtime_proof_gate_result.json"
OUT_REPORT = "tier6_runtime_proof_gate_report.md"

GATE_NAME = "tier6_runtime_proof_gate"

# Per-row check counts. MUST rows run 18 classes (same as Tier 5);
# REFERENCE rows run 18 reference-only classes.
_CHECKS_PER_MUST_ROW = 18
_CHECKS_PER_REFERENCE_ROW = 18


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _row_iter(payload: Any) -> Sequence[Mapping[str, Any]]:
    if isinstance(payload, dict):
        for key in ("rows", "tier6_rows", "items", "entries"):
            value = payload.get(key)
            if isinstance(value, list):
                return value
        return []
    if isinstance(payload, list):
        return payload
    return []


def _resolve(repo_relative: str) -> Path:
    rp = Path(repo_relative)
    if rp.is_absolute():
        return rp
    return REPO_ROOT / repo_relative


def _load_tier6_selection() -> List[Mapping[str, Any]]:
    if not SELECTION_PATH.is_file():
        return []
    try:
        data = _load_json(SELECTION_PATH)
    except (OSError, json.JSONDecodeError):
        return []
    selected = data.get("selected") if isinstance(data, dict) else None
    return list(selected) if isinstance(selected, list) else []


def _is_reference_only(selection_row: Mapping[str, Any]) -> bool:
    return selection_row.get("release_gate_rule") == "NON_BLOCKING_REFERENCE"


# ---------------------------------------------------------------------------
# Common per-row checks (apply to BOTH modes).
# ---------------------------------------------------------------------------


def _check_common(
    req_id: str,
    rows_per_surface: Mapping[str, Mapping[str, Any]],
    canonical: set,
) -> Tuple[List[str], Optional[Mapping[str, Any]], str]:
    failures: List[str] = []
    surfaces = list(rows_per_surface.values())
    if not surfaces:
        return ([f"{req_id}: no rows found in any source surface"], None, "")

    if not req_id or req_id not in canonical:
        failures.append(f"{req_id}: not in canonical Tier 6 REQ_IDs")

    for surface_name, row in rows_per_surface.items():
        if not row.get("step1_req_id"):
            failures.append(f"{req_id} [{surface_name}]: missing step1_req_id")
        tier_val = (row.get("tier") or "").upper()
        if tier_val and tier_val != "TIER6":
            failures.append(f"{req_id} [{surface_name}]: tier={tier_val!r} (expected TIER6)")
        if row.get("linkage_status") != "LINKED_LITERAL":
            failures.append(
                f"{req_id} [{surface_name}]: linkage_status="
                f"{row.get('linkage_status')!r} (expected LINKED_LITERAL)"
            )
        if row.get("blockers"):
            failures.append(f"{req_id} [{surface_name}]: non-empty blockers={row.get('blockers')}")
        if not (row.get("expected_fail_reason") or "").strip():
            failures.append(f"{req_id} [{surface_name}]: missing expected_fail_reason")

    primary = rows_per_surface.get("index") or surfaces[0]
    expected_efr = (primary.get("expected_fail_reason") or "").strip()

    # Common ref existence: code/validator/test/artifact must exist on disk.
    for kind in ("code_refs", "validator_refs", "test_refs", "artifact_refs"):
        for ref in primary.get(kind) or []:
            if not _resolve(ref).is_file():
                failures.append(f"{req_id}: missing {kind} on disk: {ref}")

    return (failures, primary, expected_efr)


# ---------------------------------------------------------------------------
# Mode A -- MUST / RELEASE_BLOCKING checks.
# ---------------------------------------------------------------------------


def _check_must_row(
    req_id: str,
    primary: Mapping[str, Any],
    expected_efr: str,
    artifacts_seen: set,
    replay_pairs_seen: set,
    negative_controls_seen: set,
) -> Tuple[List[str], int]:
    failures: List[str] = []

    # Additional ref existence: otel/replay/negative_control must exist.
    for kind in ("otel_span_refs", "replay_refs", "negative_control_refs"):
        for ref in primary.get(kind) or []:
            if not _resolve(ref).is_file():
                failures.append(f"{req_id}: missing {kind} on disk: {ref}")

    if not (primary.get("otel_span_refs") or []):
        failures.append(f"{req_id}: no otel_span_refs declared")

    # Artifact JSON content checks.
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

    # Replay JSON content + invariant_digest pair stability.
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

    pair_groups: Dict[str, List[Tuple[str, Mapping[str, Any]]]] = defaultdict(list)
    for ref, data in replay_payloads.items():
        stem = ref.replace("_run_1.json", "").replace("_run_2.json", "")
        pair_groups[stem].append((ref, data))
    pairs_checked = 0
    for stem, members in pair_groups.items():
        if len(members) < 2:
            continue
        digests = [m[1].get("invariant_digest") for m in members if m[1].get("invariant_digest")]
        if len(digests) < 2:
            continue
        replay_pairs_seen.add(stem)
        pairs_checked += 1
        if len(set(digests)) != 1:
            failures.append(f"{req_id}: replay pair {stem} invariant_digest mismatch: {digests}")

    # Negative-control efr match (if JSON).
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

    return (failures, pairs_checked)


# ---------------------------------------------------------------------------
# Mode B -- REFERENCE / NON_BLOCKING_REFERENCE checks.
# ---------------------------------------------------------------------------


def _check_reference_row(
    req_id: str,
    primary: Mapping[str, Any],
    selection_row: Mapping[str, Any],
    policy_artifact: Optional[Mapping[str, Any]],
    artifacts_seen: set,
) -> List[str]:
    failures: List[str] = []

    # release_gate_rule + requirement_strength are the keystones of ref-only.
    if selection_row.get("release_gate_rule") != "NON_BLOCKING_REFERENCE":
        failures.append(
            f"{req_id}: release_gate_rule="
            f"{selection_row.get('release_gate_rule')!r} (expected NON_BLOCKING_REFERENCE)"
        )
    if selection_row.get("requirement_strength") != "REFERENCE":
        failures.append(
            f"{req_id}: requirement_strength="
            f"{selection_row.get('requirement_strength')!r} (expected REFERENCE)"
        )
    # Same checks at the metadata level (defense in depth).
    if primary.get("release_gate_rule") != "NON_BLOCKING_REFERENCE":
        failures.append(
            f"{req_id}: metadata release_gate_rule="
            f"{primary.get('release_gate_rule')!r} (expected NON_BLOCKING_REFERENCE)"
        )
    if primary.get("requirement_strength") != "REFERENCE":
        failures.append(
            f"{req_id}: metadata requirement_strength="
            f"{primary.get('requirement_strength')!r} (expected REFERENCE)"
        )

    # code_refs / validator_refs must point to reference_only_policy_refs.py.
    for kind in ("code_refs", "validator_refs"):
        refs = list(primary.get(kind) or [])
        if REFERENCE_ONLY_POLICY_REFS_PATH not in refs:
            failures.append(f"{req_id}: {kind} must include {REFERENCE_ONLY_POLICY_REFS_PATH}; got {refs}")

    # test_refs must point to the targeted Tier 6 test.
    test_refs = list(primary.get("test_refs") or [])
    if TIER6_TARGETED_TEST not in test_refs:
        failures.append(f"{req_id}: test_refs must include {TIER6_TARGETED_TEST}; got {test_refs}")

    # artifact_refs must include the policy artifact.
    artifact_refs = list(primary.get("artifact_refs") or [])
    if POLICY_ARTIFACT_REL not in artifact_refs:
        failures.append(f"{req_id}: artifact_refs must include {POLICY_ARTIFACT_REL}; got {artifact_refs}")
    artifacts_seen.add(POLICY_ARTIFACT_REL)

    # Reference-only rows MUST NOT carry runtime-proof refs / executed flags
    # at the metadata level. Reject any contradictory field shape.
    if primary.get("replay_refs"):
        failures.append(
            f"{req_id}: reference-only row must not carry replay_refs; "
            f"policy says no real replay execution. Got: {primary['replay_refs']}"
        )
    if primary.get("negative_control_refs"):
        failures.append(f"{req_id}: reference-only row must not carry negative_control_refs")
    if primary.get("otel_span_refs"):
        failures.append(
            f"{req_id}: reference-only row must not carry otel_span_refs; "
            f"policy says no real OTEL emission. Got: {primary['otel_span_refs']}"
        )
    if primary.get("replay_executed") is True:
        failures.append(f"{req_id}: replay_executed=True forbidden for reference-only row")
    if primary.get("negative_control_executed") is True:
        failures.append(f"{req_id}: negative_control_executed=True forbidden for reference-only row")

    # Policy artifact membership + shape.
    if policy_artifact is None:
        failures.append(f"{req_id}: tier6_reference_only_policy.json missing or unreadable")
        return failures
    if policy_artifact.get("policy_name") != POLICY_NAME:
        failures.append(
            f"{req_id}: policy_name={policy_artifact.get('policy_name')!r} (expected {POLICY_NAME!r})"
        )
    if policy_artifact.get("total_reference_only_rows") != EXPECTED_REFERENCE_ONLY_TOTAL:
        failures.append(
            f"{req_id}: policy total_reference_only_rows="
            f"{policy_artifact.get('total_reference_only_rows')!r} "
            f"(expected {EXPECTED_REFERENCE_ONLY_TOTAL})"
        )
    members = list(policy_artifact.get("reference_only_req_ids") or [])
    if req_id not in members:
        failures.append(f"{req_id}: not in policy reference_only_req_ids list")
    rule = (policy_artifact.get("rule") or "").lower()
    if "reference integrity" not in rule or "no" not in rule or "runtime proof" not in rule:
        failures.append(
            f"{req_id}: policy rule must state reference rows are machine-checked "
            "for reference integrity only and do not claim runtime proof; "
            f"got: {policy_artifact.get('rule')!r}"
        )
    caveat = (policy_artifact.get("caveat") or "").lower()
    for required in (
        "no real replay execution",
        "no real otel emission",
        "no runtime",
    ):
        if required not in caveat:
            failures.append(
                f"{req_id}: policy caveat missing required phrase {required!r}; "
                f"got: {policy_artifact.get('caveat')!r}"
            )

    return failures


# ---------------------------------------------------------------------------
# evaluate / write_result / write_report.
# ---------------------------------------------------------------------------


def evaluate(
    metadata_gate_status: Optional[str] = None,
    targeted_tests_status: Optional[str] = None,
    targeted_tests_run: Optional[Sequence[str]] = None,
) -> Dict[str, Any]:
    """Validate split-mode static-evidence consistency for the 21 Tier 6 REQ_IDs."""
    selection_rows = _load_tier6_selection()
    selection_by_rid: Dict[str, Mapping[str, Any]] = {
        r.get("req_id", ""): r for r in selection_rows if r.get("req_id")
    }
    tier6_req_ids: Tuple[str, ...] = tuple(selection_by_rid.keys())
    canonical = set(tier6_req_ids)

    must_rows = [r for r in tier6_req_ids if not _is_reference_only(selection_by_rid[r])]
    reference_rows = [r for r in tier6_req_ids if _is_reference_only(selection_by_rid[r])]

    source_files_checked: List[str] = []
    surfaces: Dict[str, Sequence[Mapping[str, Any]]] = {}
    for fname in SOURCE_FILES:
        path = ARTIFACTS_DIR / fname
        if not path.is_file():
            return {
                "gate_name": GATE_NAME,
                "result": "BLOCKED",
                "tier6_total": len(tier6_req_ids),
                "failed_count": len(tier6_req_ids),
                "failed_req_ids": list(tier6_req_ids),
                "checks_performed": 0,
                "must_rows_checked": [],
                "reference_only_rows_checked": [],
                "artifacts_checked": [],
                "replay_pairs_checked": [],
                "reference_policy_checked": False,
                "negative_controls_checked": [],
                "targeted_tests_run": list(targeted_tests_run or ()),
                "source_files_checked": source_files_checked,
                "metadata_gate_status": metadata_gate_status,
                "targeted_tests_status": targeted_tests_status,
                "blocking_reasons": [f"Required source file missing: {path}"],
                "evaluated_at_utc": _utc_now_iso(),
            }
        source_files_checked.append(fname)
        surface_name = fname.split("_", 2)[1].split(".")[0]
        surfaces[surface_name] = _row_iter(_load_json(path))

    rows_by_req: Dict[str, Dict[str, Mapping[str, Any]]] = defaultdict(dict)
    for surface_name, rows in surfaces.items():
        for row in rows:
            rid = row.get("step1_req_id") or ""
            if rid:
                rows_by_req[rid][surface_name] = row

    # Load reference-only policy artifact once.
    policy_path = REPO_ROOT / POLICY_ARTIFACT_REL
    policy_artifact: Optional[Mapping[str, Any]] = None
    policy_load_error: Optional[str] = None
    if policy_path.is_file():
        try:
            payload = _load_json(policy_path)
            if isinstance(payload, dict):
                policy_artifact = payload
            else:
                policy_load_error = "policy artifact is not a JSON object"
        except (OSError, json.JSONDecodeError) as exc:
            policy_load_error = f"cannot parse policy artifact: {exc}"
    else:
        policy_load_error = f"policy artifact missing: {policy_path}"
    reference_policy_checked = policy_artifact is not None

    failed_req_ids: List[str] = []
    failure_detail: List[str] = []
    artifacts_checked: set = set()
    replay_pairs_checked: set = set()
    negative_controls_checked: set = set()
    must_rows_checked: List[str] = []
    reference_only_rows_checked: List[str] = []
    checks_performed = 0

    for req_id in tier6_req_ids:
        per_surface = rows_by_req.get(req_id, {})
        common_failures, primary, expected_efr = _check_common(req_id, per_surface, canonical)
        per_row_failures = list(common_failures)

        if primary is None:
            checks_performed += _CHECKS_PER_MUST_ROW
            failed_req_ids.append(req_id)
            failure_detail.extend(per_row_failures)
            continue

        if req_id in must_rows:
            must_rows_checked.append(req_id)
            checks_performed += _CHECKS_PER_MUST_ROW
            mode_failures, _pairs = _check_must_row(
                req_id,
                primary,
                expected_efr,
                artifacts_checked,
                replay_pairs_checked,
                negative_controls_checked,
            )
            per_row_failures.extend(mode_failures)
        else:
            reference_only_rows_checked.append(req_id)
            checks_performed += _CHECKS_PER_REFERENCE_ROW
            sel_row = selection_by_rid.get(req_id, {})
            mode_failures = _check_reference_row(
                req_id,
                primary,
                sel_row,
                policy_artifact,
                artifacts_checked,
            )
            per_row_failures.extend(mode_failures)

        if per_row_failures:
            failed_req_ids.append(req_id)
            failure_detail.extend(per_row_failures)

    blocking_reasons: List[str] = list(failure_detail)
    if policy_load_error and reference_rows:
        blocking_reasons.insert(0, policy_load_error)
    if metadata_gate_status and metadata_gate_status != "READY":
        blocking_reasons.append(f"Metadata enforcement gate not READY (status={metadata_gate_status})")
        if "metadata_gate" not in failed_req_ids:
            failed_req_ids.append("metadata_gate")
    if targeted_tests_status and targeted_tests_status not in ("PASSED", "SKIPPED"):
        blocking_reasons.append(f"Targeted tests not PASSED (status={targeted_tests_status})")
        if "targeted_tests" not in failed_req_ids:
            failed_req_ids.append("targeted_tests")

    result = "READY" if not blocking_reasons else "BLOCKED"

    return {
        "gate_name": GATE_NAME,
        "result": result,
        "tier6_total": len(tier6_req_ids),
        "failed_count": len(failed_req_ids),
        "failed_req_ids": failed_req_ids,
        "checks_performed": checks_performed,
        "must_rows_checked": sorted(must_rows_checked),
        "reference_only_rows_checked": sorted(reference_only_rows_checked),
        "artifacts_checked": sorted(artifacts_checked),
        "replay_pairs_checked": sorted(replay_pairs_checked),
        "reference_policy_checked": reference_policy_checked,
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
    lines.append("# Tier 6 Runtime Proof Gate Report")
    lines.append("")
    lines.append(f"- Gate: `{result['gate_name']}`")
    lines.append(f"- Result: **{result['result']}**")
    lines.append(f"- Evaluated at: {result['evaluated_at_utc']}")
    lines.append(f"- Tier 6 total: {result['tier6_total']}")
    lines.append(f"- MUST rows checked: {len(result['must_rows_checked'])}")
    lines.append(f"- REFERENCE-only rows checked: {len(result['reference_only_rows_checked'])}")
    lines.append(f"- Failed count: {result['failed_count']}")
    lines.append(f"- Checks performed: {result['checks_performed']}")
    lines.append(f"- Reference policy checked: {result['reference_policy_checked']}")
    lines.append(f"- Metadata gate status: {result.get('metadata_gate_status')}")
    lines.append(f"- Targeted tests status: {result.get('targeted_tests_status')}")
    lines.append("")
    lines.append("## Source files checked")
    for f in result["source_files_checked"]:
        lines.append(f"- {f}")
    lines.append("")
    lines.append("## MUST rows checked")
    for r in result["must_rows_checked"]:
        lines.append(f"- {r}")
    lines.append("")
    lines.append("## REFERENCE-only rows checked")
    for r in result["reference_only_rows_checked"]:
        lines.append(f"- {r}")
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

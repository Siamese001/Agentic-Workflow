"""Master Merkle-root attestation for the 100% requirements enforcement baseline.

Builds a deterministic SHA-256 Merkle tree over the full 150-row Step 1
requirement evidence graph, with one leaf per REQ_ID. Each leaf records
the tier, requirement metadata, gate verdicts, evidence references, and
SHA-256 hashes of every referenced evidence file on disk. The root
proves the EXACT file and requirement-evidence state of the
"100% requirements enforcement baseline complete" snapshot.

This script does NOT execute replay machinery, OTEL exporters, the proof
harness, or the full pytest suite. The only subprocess invoked is the
master `verify_all_requirements_gates.py`, which itself is static-only.

Status vocabulary: READY | BLOCKED | PASSED | FAILED.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS_DIR = REPO_ROOT / "artifacts" / "runtime" / "requirements_proof"
TIER6_POLICY = ARTIFACTS_DIR / "tier6_reference_only_policy.json"

OUT_LEAVES = ARTIFACTS_DIR / "all_requirements_merkle_leaves.json"
OUT_TREE = ARTIFACTS_DIR / "all_requirements_merkle_tree.json"
OUT_ROOT = ARTIFACTS_DIR / "all_requirements_merkle_root.json"
OUT_REPORT = ARTIFACTS_DIR / "all_requirements_merkle_report.md"

MERKLE_SCHEME = "REQ_MERKLE_V1"
HASH_ALGO = "SHA-256"
EXPECTED_LEAF_COUNT = 150

CAVEAT = (
    "This Merkle root attests the exact file and requirement-evidence "
    "state of the 100% requirements enforcement baseline. It does not "
    "claim real replay execution, real OTEL emission, full production "
    "runtime proof, or full architecture proof."
)

VOLATILE_KEYS = (
    "evaluated_at_utc",
    "generated_at_utc",
    "generated_at",
    "timestamp",
    "run_started_at",
    "run_finished_at",
)

EVIDENCE_REF_KINDS: Tuple[str, ...] = (
    "code_refs",
    "validator_refs",
    "test_refs",
    "artifact_refs",
    "replay_refs",
    "otel_span_refs",
    "negative_control_refs",
)

TIERS: Tuple[str, ...] = ("0", "1", "2", "3", "4", "5", "6")
EXPECTED_TIER_COUNTS: Mapping[str, int] = {
    "0": 17,
    "1": 15,
    "2": 22,
    "3": 25,
    "4": 25,
    "5": 25,
    "6": 21,
}


# ---------------------------------------------------------------------------
# Hashing primitives.
# ---------------------------------------------------------------------------


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _canonical(obj: Any) -> bytes:
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def _strip_volatile(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: _strip_volatile(v) for k, v in obj.items() if k not in VOLATILE_KEYS}
    if isinstance(obj, list):
        return [_strip_volatile(v) for v in obj]
    return obj


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# Loaders.
# ---------------------------------------------------------------------------


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve(repo_relative: str) -> Path:
    rp = Path(repo_relative)
    return rp if rp.is_absolute() else REPO_ROOT / repo_relative


def _load_tier_selection_rows() -> Dict[str, Dict[str, Mapping[str, Any]]]:
    """Return {tier: {req_id: selection_row}}.

    Tier 0 has no SELECTION.json -- selection rows are derived from the
    generated requirements_index rows (recorded via _selection_source).
    """
    out: Dict[str, Dict[str, Mapping[str, Any]]] = {t: {} for t in TIERS}

    # Tier 0 -- derive from index. Loaded later in _load_tier_metadata_rows.
    for tier in ("1", "2", "3", "4", "5", "6"):
        path = REPO_ROOT / "docs" / "reference" / "contracts" / f"tier{tier}" / f"TIER{tier}_SELECTION.json"
        if not path.is_file():
            continue
        data = _load_json(path)
        rows = data.get("selected") if isinstance(data, dict) else None
        if not isinstance(rows, list):
            continue
        for row in rows:
            rid = row.get("req_id")
            if rid:
                out[tier][rid] = row
    return out


def _load_tier_metadata_rows() -> Dict[str, Dict[str, Dict[str, Mapping[str, Any]]]]:
    """Return {tier: {req_id: {surface: row}}} for surfaces.

    surfaces: requirements_index, coverage_matrix, implementation_map,
    artifact_linkage.
    """
    out: Dict[str, Dict[str, Dict[str, Mapping[str, Any]]]] = {t: {} for t in TIERS}
    for tier in TIERS:
        for surface in (
            "requirements_index",
            "coverage_matrix",
            "implementation_map",
            "artifact_linkage",
        ):
            path = ARTIFACTS_DIR / f"tier{tier}_{surface}.generated.json"
            if not path.is_file():
                continue
            data = _load_json(path)
            rows = data.get("rows") if isinstance(data, dict) else None
            if not isinstance(rows, list):
                continue
            for row in rows:
                rid = row.get("step1_req_id") or row.get("req_id")
                if not rid:
                    continue
                out[tier].setdefault(rid, {})[surface] = row
    return out


def _load_gate_verdict(path: Path) -> str:
    if not path.is_file():
        return "UNKNOWN"
    try:
        data = _load_json(path)
    except (OSError, json.JSONDecodeError):
        return "UNKNOWN"
    if isinstance(data, dict):
        return str(data.get("result") or "UNKNOWN").upper()
    return "UNKNOWN"


def _load_tier6_policy() -> Tuple[Optional[Mapping[str, Any]], Optional[str]]:
    if not TIER6_POLICY.is_file():
        return None, None
    try:
        data = _load_json(TIER6_POLICY)
    except (OSError, json.JSONDecodeError):
        return None, None
    if not isinstance(data, dict):
        return None, None
    return data, _sha256_file(TIER6_POLICY)


# ---------------------------------------------------------------------------
# Master gate driver.
# ---------------------------------------------------------------------------


def _run_master_gate() -> Tuple[int, str]:
    proc = subprocess.run(
        [sys.executable, "scripts/verify_all_requirements_gates.py"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=600,
        check=False,
    )
    sys.stdout.write(proc.stdout)
    sys.stderr.write(proc.stderr)
    return proc.returncode, proc.stdout


# ---------------------------------------------------------------------------
# Leaf construction.
# ---------------------------------------------------------------------------


def _row_canonical_hash(row: Mapping[str, Any]) -> str:
    return _sha256_bytes(_canonical(_strip_volatile(row)))


def _evidence_file_hashes(
    primary_row: Mapping[str, Any],
    file_hash_cache: Dict[str, str],
) -> Dict[str, List[Dict[str, str]]]:
    out: Dict[str, List[Dict[str, str]]] = {}
    for kind in EVIDENCE_REF_KINDS:
        bucket: List[Dict[str, str]] = []
        for ref in primary_row.get(kind) or []:
            posix = Path(ref).as_posix()
            entry: Dict[str, str] = {"path": posix, "exists": "false", "sha256": ""}
            target = _resolve(ref)
            if target.is_file():
                entry["exists"] = "true"
                if posix not in file_hash_cache:
                    file_hash_cache[posix] = _sha256_file(target)
                entry["sha256"] = file_hash_cache[posix]
            bucket.append(entry)
        out[kind] = bucket
    return out


def _build_leaf(
    tier: str,
    req_id: str,
    selection_row: Mapping[str, Any],
    metadata_rows: Mapping[str, Mapping[str, Any]],
    metadata_verdict: str,
    runtime_verdict: str,
    master_verdict: str,
    tier6_policy: Optional[Mapping[str, Any]],
    tier6_policy_hash: Optional[str],
    file_hash_cache: Dict[str, str],
) -> Dict[str, Any]:
    primary = metadata_rows.get("requirements_index") or {}

    release_gate_rule = selection_row.get("release_gate_rule") or primary.get("release_gate_rule") or ""
    requirement_strength = (
        selection_row.get("requirement_strength") or primary.get("requirement_strength") or ""
    )
    risk_category = selection_row.get("risk_category") or primary.get("risk_category") or ""
    source_matrix_file = selection_row.get("source_matrix_file") or primary.get("source_matrix_file") or ""

    is_tier6_ref_only = tier == "6" and release_gate_rule == "NON_BLOCKING_REFERENCE"
    evidence_mode = "REFERENCE_ONLY_POLICY" if is_tier6_ref_only else "STANDARD_STATIC_EVIDENCE"

    metadata_row_hashes = {
        surface: _row_canonical_hash(metadata_rows[surface])
        for surface in (
            "requirements_index",
            "coverage_matrix",
            "implementation_map",
            "artifact_linkage",
        )
        if surface in metadata_rows
    }

    evidence_hashes = _evidence_file_hashes(primary, file_hash_cache)

    leaf: Dict[str, Any] = {
        "req_id": req_id,
        "tier": f"TIER{tier}",
        "source_matrix_file": source_matrix_file,
        "requirement_strength": requirement_strength,
        "release_gate_rule": release_gate_rule,
        "risk_category": risk_category,
        "linkage_status": primary.get("linkage_status", ""),
        "expected_fail_reason": primary.get("expected_fail_reason", ""),
        "metadata_gate_result": metadata_verdict,
        "runtime_static_gate_result": runtime_verdict,
        "master_gate_result": master_verdict,
        "evidence_mode": evidence_mode,
        "selection_row_hash": _row_canonical_hash(selection_row),
        "metadata_row_hashes": metadata_row_hashes,
        "evidence_file_hashes": evidence_hashes,
    }

    if is_tier6_ref_only:
        if tier6_policy_hash:
            leaf["reference_only_policy_hash"] = tier6_policy_hash
        if tier6_policy is not None:
            members = list(tier6_policy.get("reference_only_req_ids") or [])
            leaf["reference_only_policy_membership"] = req_id in members
            leaf["reference_only_policy_total"] = tier6_policy.get("total_reference_only_rows")
            leaf["reference_only_policy_caveat"] = tier6_policy.get("caveat", "")

    payload_for_hash = {k: v for k, v in leaf.items() if k != "leaf_payload_hash"}
    leaf_payload_hash = _sha256_bytes(_canonical(payload_for_hash))
    leaf["leaf_payload_hash"] = leaf_payload_hash

    leaf_node_hash = _sha256_bytes(
        b"REQ_LEAF_V1\0" + req_id.encode("utf-8") + b"\0" + leaf_payload_hash.encode("utf-8")
    )
    leaf["leaf_node_hash"] = leaf_node_hash

    return leaf


# ---------------------------------------------------------------------------
# Merkle tree.
# ---------------------------------------------------------------------------


def _build_merkle_tree(
    leaf_nodes: Sequence[Mapping[str, Any]],
) -> Tuple[str, List[List[str]]]:
    """Return (root, levels) where levels[0] is the leaf level (hashes)."""
    sorted_leaves = sorted(leaf_nodes, key=lambda x: x["req_id"])
    level: List[str] = [str(l["leaf_node_hash"]) for l in sorted_leaves]
    levels: List[List[str]] = [list(level)]
    while len(level) > 1:
        if len(level) % 2 == 1:
            level = level + [level[-1]]
        next_level: List[str] = []
        for i in range(0, len(level), 2):
            left = level[i]
            right = level[i + 1]
            parent = _sha256_bytes(b"REQ_NODE_V1\0" + left.encode("utf-8") + b"\0" + right.encode("utf-8"))
            next_level.append(parent)
        levels.append(next_level)
        level = next_level
    return level[0], levels


# ---------------------------------------------------------------------------
# Helpers.
# ---------------------------------------------------------------------------


def _git_head() -> str:
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        if proc.returncode == 0:
            return proc.stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        pass
    return ""


def _materialize_fixtures() -> None:
    from agentic_core.runtime.prove_requirements import tier_fixture_bootstrap

    tier_fixture_bootstrap.materialize()


# ---------------------------------------------------------------------------
# Main pipeline.
# ---------------------------------------------------------------------------


def evaluate() -> Dict[str, Any]:
    _materialize_fixtures()

    master_rc, _master_stdout = _run_master_gate()
    master_result_path = ARTIFACTS_DIR / "all_requirements_gate_result.json"
    master_verdict = _load_gate_verdict(master_result_path)

    # Tier 0 selection: derived from index rows (no SELECTION.json).
    metadata_by_tier = _load_tier_metadata_rows()
    selection_by_tier = _load_tier_selection_rows()
    for rid, surfaces in metadata_by_tier.get("0", {}).items():
        # Build a synthetic selection row from the requirements_index row
        # so Tier 0 has a stable, deterministic selection_row_hash.
        idx_row = surfaces.get("requirements_index", {})
        synthetic = {
            "_selection_source": "derived_from_tier0_requirements_index",
            "req_id": rid,
            "tier": idx_row.get("tier", "TIER0"),
            "source_matrix_file": idx_row.get("source_matrix_file", ""),
            "owner_layer": idx_row.get("owner_layer", ""),
            "owner_subsystem": idx_row.get("owner_subsystem", ""),
            "requirement_strength": idx_row.get("requirement_strength", ""),
            "release_gate_rule": idx_row.get("release_gate_rule", ""),
            "risk_category": idx_row.get("risk_category", ""),
        }
        selection_by_tier["0"][rid] = synthetic

    tier_metadata_verdicts: Dict[str, str] = {}
    tier_runtime_verdicts: Dict[str, str] = {}
    for tier in TIERS:
        tier_metadata_verdicts[tier] = _load_gate_verdict(
            ARTIFACTS_DIR / f"tier{tier}_enforcement_gate_result.json"
        )
        tier_runtime_verdicts[tier] = _load_gate_verdict(
            ARTIFACTS_DIR / f"tier{tier}_runtime_proof_gate_result.json"
        )

    tier6_policy, tier6_policy_hash = _load_tier6_policy()
    file_hash_cache: Dict[str, str] = {}

    leaves: List[Dict[str, Any]] = []
    blocking: List[str] = []

    for tier in TIERS:
        sel_rows = selection_by_tier.get(tier, {})
        meta_rows = metadata_by_tier.get(tier, {})
        for req_id, selection_row in sel_rows.items():
            surfaces = meta_rows.get(req_id, {})
            if "requirements_index" not in surfaces:
                blocking.append(f"{req_id}: missing requirements_index row in tier {tier}")
                continue
            leaf = _build_leaf(
                tier=tier,
                req_id=req_id,
                selection_row=selection_row,
                metadata_rows=surfaces,
                metadata_verdict=tier_metadata_verdicts[tier],
                runtime_verdict=tier_runtime_verdicts[tier],
                master_verdict=master_verdict,
                tier6_policy=tier6_policy,
                tier6_policy_hash=tier6_policy_hash,
                file_hash_cache=file_hash_cache,
            )
            leaves.append(leaf)

    # Coverage validation.
    seen: Dict[str, str] = {}
    duplicates: List[str] = []
    for leaf in leaves:
        rid = leaf["req_id"]
        if rid in seen:
            duplicates.append(rid)
        seen[rid] = leaf["tier"]
    distinct = len(seen)
    total = len(leaves)
    tier_counts = {t: 0 for t in TIERS}
    for leaf in leaves:
        tier_label = leaf["tier"][-1]
        tier_counts[tier_label] = tier_counts.get(tier_label, 0) + 1

    if total != EXPECTED_LEAF_COUNT:
        blocking.append(f"Total tiered REQ_IDs={total} (expected {EXPECTED_LEAF_COUNT})")
    if distinct != EXPECTED_LEAF_COUNT:
        blocking.append(f"Distinct tiered REQ_IDs={distinct} (expected {EXPECTED_LEAF_COUNT})")
    if duplicates:
        blocking.append(f"Duplicate REQ_IDs: {sorted(set(duplicates))}")
    for tier, expected in EXPECTED_TIER_COUNTS.items():
        if tier_counts.get(tier, 0) != expected:
            blocking.append(f"Tier {tier} count={tier_counts.get(tier, 0)} (expected {expected})")

    if master_rc != 0 or master_verdict != "READY":
        blocking.append(f"Master all_requirements gate not READY (rc={master_rc}, verdict={master_verdict})")

    # Hardening case count from master gate JSON.
    hardening_case_count = 0
    hardening_result = "FAILED"
    if master_result_path.is_file():
        try:
            mdata = _load_json(master_result_path)
            if isinstance(mdata, dict):
                hardening_case_count = int(mdata.get("hardening_case_count") or 0)
                hardening_result = str(mdata.get("hardening_result") or "FAILED").upper()
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            pass
    if hardening_case_count < 79:
        blocking.append(f"Hardening case count {hardening_case_count} < 79 minimum")
    if hardening_result not in ("PASSED",):
        blocking.append(f"Hardening result not PASSED: {hardening_result}")

    # Evidence mode counts.
    evidence_mode_counts: Dict[str, int] = {
        "STANDARD_STATIC_EVIDENCE": 0,
        "REFERENCE_ONLY_POLICY": 0,
    }
    for leaf in leaves:
        evidence_mode_counts[leaf["evidence_mode"]] = evidence_mode_counts.get(leaf["evidence_mode"], 0) + 1

    # Validate Tier 6 reference-only policy structure for ref-only leaves.
    if evidence_mode_counts.get("REFERENCE_ONLY_POLICY", 0) > 0:
        if tier6_policy is None:
            blocking.append("Tier 6 reference-only policy artifact missing")
        else:
            caveat = (tier6_policy.get("caveat") or "").lower()
            for required in (
                "no real replay execution",
                "no real otel emission",
                "no runtime",
            ):
                if required not in caveat:
                    blocking.append(f"Tier 6 policy caveat missing required phrase: {required!r}")
            if tier6_policy.get("total_reference_only_rows") != 15:
                blocking.append("Tier 6 policy total_reference_only_rows != 15")
        for leaf in leaves:
            if leaf["evidence_mode"] != "REFERENCE_ONLY_POLICY":
                continue
            if not leaf.get("reference_only_policy_membership"):
                blocking.append(f"{leaf['req_id']}: not in reference_only_req_ids")

    # Build the Merkle tree.
    if blocking:
        merkle_root = ""
        levels: List[List[str]] = []
    else:
        merkle_root, levels = _build_merkle_tree(leaves)

    return {
        "leaves": leaves,
        "levels": levels,
        "merkle_root": merkle_root,
        "tier_counts": tier_counts,
        "duplicate_req_ids": sorted(set(duplicates)),
        "distinct_count": distinct,
        "total_count": total,
        "master_verdict": master_verdict,
        "master_rc": master_rc,
        "tier_metadata_verdicts": tier_metadata_verdicts,
        "tier_runtime_verdicts": tier_runtime_verdicts,
        "evidence_mode_counts": evidence_mode_counts,
        "hardening_case_count": hardening_case_count,
        "hardening_result": hardening_result,
        "tier6_policy_hash": tier6_policy_hash or "",
        "blocking_reasons": blocking,
    }


def _verify_recompute(leaves: Sequence[Mapping[str, Any]], claimed_root: str) -> bool:
    if not leaves:
        return False
    recomputed, _ = _build_merkle_tree(leaves)
    return recomputed == claimed_root


def _missing_req_ids(distinct: int) -> List[str]:
    if distinct >= EXPECTED_LEAF_COUNT:
        return []
    return [f"<{EXPECTED_LEAF_COUNT - distinct} REQ_ID(s) unaccounted>"]


def _write_outputs(state: Mapping[str, Any]) -> Dict[str, Path]:
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    OUT_LEAVES.write_text(
        json.dumps(
            {
                "merkle_scheme": MERKLE_SCHEME,
                "hash_algorithm": HASH_ALGO,
                "leaf_count": len(state["leaves"]),
                "leaves": state["leaves"],
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    OUT_TREE.write_text(
        json.dumps(
            {
                "merkle_scheme": MERKLE_SCHEME,
                "hash_algorithm": HASH_ALGO,
                "leaf_count": len(state["leaves"]),
                "level_count": len(state["levels"]),
                "levels": state["levels"],
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    result_obj = {
        "merkle_scheme": MERKLE_SCHEME,
        "hash_algorithm": HASH_ALGO,
        "requirements_merkle_root": state["merkle_root"],
        "leaf_count": len(state["leaves"]),
        "tier_counts": state["tier_counts"],
        "step1_universe_count": EXPECTED_LEAF_COUNT,
        "total_tiered_req_ids": state["total_count"],
        "distinct_tiered_req_ids": state["distinct_count"],
        "duplicate_req_ids": state["duplicate_req_ids"],
        "missing_step1_req_ids": _missing_req_ids(state["distinct_count"]),
        "master_gate_result": state["master_verdict"],
        "tier_metadata_verdicts": state["tier_metadata_verdicts"],
        "tier_runtime_verdicts": state["tier_runtime_verdicts"],
        "hardening_case_count": state["hardening_case_count"],
        "hardening_result": state["hardening_result"],
        "baseline_tag": "all-requirements-enforcement-baseline",
        "baseline_commit": _git_head(),
        "tier6_reference_only_policy_hash": state["tier6_policy_hash"],
        "evidence_mode_counts": state["evidence_mode_counts"],
        "caveat": CAVEAT,
        "language_phrase": "100% requirements enforcement baseline complete",
        "blocking_reasons": state["blocking_reasons"],
        "result": "READY" if not state["blocking_reasons"] else "BLOCKED",
        "generated_at_utc": _utc_now_iso(),
    }
    OUT_ROOT.write_text(json.dumps(result_obj, indent=2, ensure_ascii=False), encoding="utf-8")

    # Report MD.
    lines: List[str] = []
    lines.append("# All Requirements Merkle Root Report")
    lines.append("")
    lines.append(f"- Scheme: `{MERKLE_SCHEME}`")
    lines.append(f"- Hash algorithm: {HASH_ALGO}")
    lines.append(f"- Result: **{result_obj['result']}**")
    lines.append(f"- Merkle root: `{state['merkle_root'] or '(unset; gate BLOCKED)'}`")
    lines.append(f"- Leaf count: {len(state['leaves'])}")
    lines.append(f"- Step 1 universe: {EXPECTED_LEAF_COUNT}")
    lines.append(f"- Distinct tiered: {state['distinct_count']}")
    lines.append(f"- Duplicate REQ_IDs: {state['duplicate_req_ids']}")
    lines.append(f"- Master gate: {state['master_verdict']}")
    lines.append(f"- Hardening: {state['hardening_result']} ({state['hardening_case_count']} cases)")
    lines.append(f"- Generated at: {result_obj['generated_at_utc']}")
    lines.append(f"- Baseline tag: `{result_obj['baseline_tag']}`")
    lines.append(f"- Baseline commit: `{result_obj['baseline_commit']}`")
    lines.append("")
    lines.append("## Tier counts")
    for t in sorted(state["tier_counts"]):
        lines.append(f"- Tier {t}: {state['tier_counts'][t]}")
    lines.append("")
    lines.append("## Evidence mode counts")
    for k, v in state["evidence_mode_counts"].items():
        lines.append(f"- {k}: {v}")
    lines.append("")
    lines.append("## Output files")
    lines.append(f"- `{OUT_LEAVES.relative_to(REPO_ROOT).as_posix()}`")
    lines.append(f"- `{OUT_TREE.relative_to(REPO_ROOT).as_posix()}`")
    lines.append(f"- `{OUT_ROOT.relative_to(REPO_ROOT).as_posix()}`")
    lines.append(f"- `{OUT_REPORT.relative_to(REPO_ROOT).as_posix()}`")
    lines.append("")
    lines.append("## Verification instructions")
    lines.append("```")
    lines.append("python scripts/verify_all_requirements_merkle_root.py")
    lines.append("python scripts/verify_all_requirements_gates.py")
    lines.append("```")
    lines.append("")
    if state["blocking_reasons"]:
        lines.append("## Blocking reasons")
        for r in state["blocking_reasons"]:
            lines.append(f"- {r}")
        lines.append("")
    lines.append("## Caveat")
    lines.append("")
    lines.append(f"> {CAVEAT}")
    lines.append("")
    lines.append("Phrase: **100% requirements enforcement baseline complete**.")
    lines.append("")
    OUT_REPORT.write_text("\n".join(lines), encoding="utf-8")

    return {
        "leaves": OUT_LEAVES,
        "tree": OUT_TREE,
        "root": OUT_ROOT,
        "report": OUT_REPORT,
    }


def main() -> int:
    state = evaluate()
    paths = _write_outputs(state)

    # Recompute the root from the written leaves to verify reproducibility.
    written_leaves = _load_json(paths["leaves"]).get("leaves", [])
    written_root = _load_json(paths["root"]).get("requirements_merkle_root", "")
    recompute_ok = (
        not state["blocking_reasons"]
        and bool(written_root)
        and _verify_recompute(written_leaves, written_root)
    )

    print(f"Merkle scheme: {MERKLE_SCHEME}")
    print(f"Result: {'READY' if not state['blocking_reasons'] else 'BLOCKED'}")
    print(f"Merkle root: {state['merkle_root'] or '(unset)'}")
    print(f"Leaf count: {len(state['leaves'])}")
    print(f"Tier counts: {state['tier_counts']}")
    print(f"Evidence mode counts: {state['evidence_mode_counts']}")
    print(f"Master gate: {state['master_verdict']}")
    print(f"Hardening: {state['hardening_result']} ({state['hardening_case_count']})")
    print(f"Recompute matches: {recompute_ok}")
    if state["blocking_reasons"]:
        print(f"Blocking: {state['blocking_reasons']}")

    if state["blocking_reasons"] or not recompute_ok:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

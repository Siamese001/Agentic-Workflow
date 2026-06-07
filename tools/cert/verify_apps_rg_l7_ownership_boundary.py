#!/usr/bin/env python3
"""Verify apps_rg section folders do not overclaim core L7/99 authority."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

L7_CORE_ARTIFACTS = {
    "agentic_core_how_trace.json",
    "agentic_core_l7_route_family_coverage.json",
    "agentic_core_spine_proof.json",
    "integrated_runtime_artifact_manifest.json",
    "runtime_trace_snapshot.json",
    "runtime_gate_verdict_bundle.json",
}


def _load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _producer_component(doc: dict[str, Any]) -> str:
    val = doc.get("producer_component")
    return val.strip() if isinstance(val, str) else ""


def _is_agentic_core_produced(doc: dict[str, Any]) -> bool:
    return _producer_component(doc).startswith("agentic_core")


def _x2_overclaims_00c(doc: dict[str, Any]) -> bool:
    text = json.dumps(doc, sort_keys=True)
    return "00C" in text or "GateVerdict" in text or doc.get("runtime_authority") == "00C"


def _durable_claim_without_receipts(root: Path, doc: dict[str, Any]) -> bool:
    claim = bool(
        doc.get("durable_vector_persistence_proven")
        or doc.get("durable_semantic_cache_proof_present")
        or doc.get("chroma_projection_complete")
    )
    if not claim:
        return False
    commit_request = (root / "commit_request.json").is_file()
    uwg = any(
        (root / name).is_file()
        for name in ("uwg_commit_receipt.json", "uwg_block_receipt.json", "state_commit_receipt.json")
    )
    l4 = any(
        (root / name).is_file()
        for name in ("l4_read_surface_receipt.json", "read_surface_refresh_receipt.json", "r1b_governed_receipt_chain.json")
    )
    return not (commit_request and uwg and l4)


def verify_dir(root: Path) -> list[str]:
    violations: list[str] = []
    if not root.is_dir():
        return [f"{root}: not a directory"]

    for artifact in L7_CORE_ARTIFACTS:
        path = root / artifact
        if not path.is_file():
            continue
        doc = _load_json(path)
        if not _is_agentic_core_produced(doc):
            violations.append(
                f"{path}: local core L7 artifact is drift; producer_component must start with agentic_core"
            )

    x2 = root / "x2_gate_outputs.json"
    if x2.is_file() and _x2_overclaims_00c(_load_json(x2)):
        violations.append(f"{x2}: x2_gate_outputs.json must not claim 00C GateVerdict authority")

    if (root / "runtime_proof_bundle.json").is_file():
        violations.append(f"{root / 'runtime_proof_bundle.json'}: section folder must not emit 99 RuntimeProofBundle")

    ep = root / "evidence_package_index.json"
    if ep.is_file():
        doc = _load_json(ep)
        for i, ref in enumerate(doc.get("verified_external_refs") or []):
            if not isinstance(ref, dict):
                continue
            if ref.get("artifact_name") in L7_CORE_ARTIFACTS and ref.get("local_path") is not None:
                violations.append(f"{ep}: verified_external_refs[{i}] for core L7 must have local_path=null")
        if _durable_claim_without_receipts(root, doc):
            violations.append(f"{ep}: durable vector persistence claim lacks CommitRequest + UWG + L4/read-surface evidence")

    return violations


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", help="Section artifact directories to verify")
    parser.add_argument("--json", action="store_true", help="Emit JSON report")
    args = parser.parse_args(argv)

    all_violations: list[str] = []
    for raw in args.paths:
        all_violations.extend(verify_dir(Path(raw)))

    report = {
        "ok": not all_violations,
        "violations_count": len(all_violations),
        "violations": all_violations,
    }
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        for violation in all_violations:
            print(f"VIOLATION: {violation}")
        if not all_violations:
            print("OK: apps_rg L7 ownership boundary holds")
    return 0 if not all_violations else 1


if __name__ == "__main__":
    raise SystemExit(main())

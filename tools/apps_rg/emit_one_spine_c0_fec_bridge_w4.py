#!/usr/bin/env python3
"""Build Wave 4 C0/FEC bridge report from runtime executive_summary artifact directory."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
OUT_DIR = REPO / "docs/reports/apps_rg"


def _load(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _rel(p: Path) -> str:
    try:
        return p.resolve().relative_to(REPO.resolve()).as_posix()
    except ValueError:
        return p.as_posix()


def _capture_pa_fail_closed() -> dict[str, Any]:
    from apps_rg.runtime.section_fec_bridge import SectionFecBridgePreconditionError
    from apps_rg.runtime.section_fec_bridge import assert_section_pa_fec_preconditions

    payload = {"product_visible": True, "raw_proof_pool_direct_to_pa": False}
    try:
        assert_section_pa_fec_preconditions(payload)
        return {"raised": False, "error_type": "", "message": ""}
    except SectionFecBridgePreconditionError as exc:
        return {"raised": True, "error_type": type(exc).__name__, "message": str(exc)}
    except Exception as exc:
        return {"raised": True, "error_type": type(exc).__name__, "message": str(exc)}


def build_w4_report(artifact_root: Path, *, runtime_command: str, runtime_exit: int) -> dict[str, Any]:
    ts = datetime.now(timezone.utc).isoformat()
    root = artifact_root.resolve()
    files = {
        "route_contract": root / "route_contract.json",
        "fec_bridge": root / "final_evidence_contract_bridge.json",
        "fec_receipt": root / "c0_fec_bridge_receipt.json",
        "compiled_prompt_artifact": root / "compiled_prompt_artifact.json",
        "runtime_payload": root / "runtime_payload.json",
        "section_front_spine_receipt": root / "section_front_spine_receipt.json",
        "blocked_proof": OUT_DIR / "section_pa_fec_precondition_blocked_proof.json",
    }
    route = _load(files["route_contract"])
    fec = _load(files["fec_bridge"])
    fec_rcpt = _load(files["fec_receipt"])
    pa_art = _load(files["compiled_prompt_artifact"])
    payload = _load(files["runtime_payload"])

    fail_closed = _capture_pa_fail_closed()
    files["blocked_proof"].write_text(
        json.dumps(
            {
                "schema_version": "section_pa_fec_precondition_blocked_proof_v1",
                "generated_at_utc": ts,
                "product_visible": True,
                **fail_closed,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    def row(
        claim: str,
        artifact_key: str,
        fields: list[str],
        expected: str,
        actual: str,
        status: str,
    ) -> dict[str, str]:
        apath = _rel(files[artifact_key]) if files[artifact_key].is_file() else "MISSING"
        return {
            "claim": claim,
            "runtime_command": runtime_command,
            "artifact_path": apath,
            "fields_inspected": ", ".join(fields),
            "expected": expected,
            "actual": actual,
            "status": status,
        }

    matrix: list[dict[str, str]] = []
    matrix.append(
        row(
            "1. RouteContract exists before FEC bridge",
            "route_contract",
            ["contract_type", "route_contract_ref"],
            "RouteContract present before bridge",
            f"{route.get('contract_type')}",
            "PASS" if route.get("contract_type") == "RouteContract" else "FAIL",
        )
    )
    matrix.append(
        row(
            "2. FEC bridge artifact emitted",
            "fec_bridge",
            ["fec_bridge_mode", "bridge_type", "schema_version"],
            "final_evidence_contract_bridge.json with section_fec_bridge",
            f"mode={fec.get('fec_bridge_mode')}; type={fec.get('bridge_type')}",
            "PASS"
            if fec.get("fec_bridge_mode") == "section_fec_bridge"
            and files["fec_bridge"].is_file()
            else "FAIL",
        )
    )
    matrix.append(
        row(
            "3. FEC bridge references RouteContract",
            "fec_bridge",
            ["route_contract_ref"],
            "route_contract_ref=route_contract.json",
            str(fec.get("route_contract_ref")),
            "PASS" if fec.get("route_contract_ref") == "route_contract.json" else "FAIL",
        )
    )
    lineage = list(fec.get("graph_lineage_refs") or []) + list(fec.get("citation_lineage_refs") or [])
    matrix.append(
        row(
            "4. FEC bridge references proof_pool/SRFS/skills graph lineage",
            "fec_bridge",
            ["proof_pool_ref", "proof_pool_digest", "srfs_ref", "citation_lineage_refs"],
            "proof_pool ref/digest + lineage refs",
            f"pool_ref={fec.get('proof_pool_ref')}; lineage_count={len(lineage)}; srfs={fec.get('srfs_ref')}",
            "PASS" if fec.get("proof_pool_ref") and (lineage or fec.get("evidence_items")) else "FAIL",
        )
    )
    matrix.append(
        row(
            "5. FEC bridge has explicit support_status",
            "fec_bridge",
            ["support_status"],
            "support_status present",
            str(fec.get("support_status")),
            "PASS" if fec.get("support_status") else "FAIL",
        )
    )
    matrix.append(
        row(
            "6. FEC bridge does not claim canonical C0.2/C0.3/C0.5",
            "fec_bridge",
            ["canonical_c0_2_claimed", "canonical_c0_3_claimed", "canonical_c0_5_claimed"],
            "all false on section bridge",
            f"c02={fec.get('canonical_c0_2_claimed')}; c03={fec.get('canonical_c0_3_claimed')}; c05={fec.get('canonical_c0_5_claimed')}",
            "PASS"
            if fec.get("canonical_c0_2_claimed") is False
            and fec.get("canonical_c0_3_claimed") is False
            and fec.get("canonical_c0_5_claimed") is False
            else "FAIL",
        )
    )
    matrix.append(
        row(
            "7. PA consumed FEC bridge/canonical FEC",
            "compiled_prompt_artifact",
            ["evidence_contract_consumed", "fec_bridge_ref", "fec_bridge_mode"],
            "evidence_contract_consumed true",
            f"consumed={pa_art.get('evidence_contract_consumed')}; ref={pa_art.get('fec_bridge_ref')}; mode={pa_art.get('fec_bridge_mode')}",
            "PASS"
            if pa_art.get("evidence_contract_consumed") is True
            and pa_art.get("fec_bridge_mode") == "section_fec_bridge"
            else "FAIL",
        )
    )
    matrix.append(
        row(
            "8. PA did not consume raw proof_pool directly",
            "compiled_prompt_artifact",
            ["raw_proof_pool_direct_to_pa"],
            "raw_proof_pool_direct_to_pa false",
            str(pa_art.get("raw_proof_pool_direct_to_pa")),
            "PASS" if pa_art.get("raw_proof_pool_direct_to_pa") is False else "FAIL",
        )
    )
    matrix.append(
        row(
            "9. Product-visible PA bypass without FEC blocked",
            "blocked_proof",
            ["raised", "error_type"],
            "SectionFecBridgePreconditionError",
            f"raised={fail_closed.get('raised')}; type={fail_closed.get('error_type')}",
            "PASS"
            if fail_closed.get("raised")
            and fail_closed.get("error_type") == "SectionFecBridgePreconditionError"
            else "FAIL",
        )
    )
    matrix.append(
        row(
            "10. Fixture/dev bypass non-product-certified",
            "fec_receipt",
            ["fixture_dev_only", "non_product_certified", "product_certification"],
            "fixture_dev_only false on product run",
            f"fixture={fec_rcpt.get('fixture_dev_only')}; non_cert={fec_rcpt.get('non_product_certified')}; cert={fec_rcpt.get('product_certification')}",
            "PASS"
            if fec_rcpt.get("fixture_dev_only") is False
            and fec_rcpt.get("product_certification") == "NOT_CLAIMED"
            else "FAIL",
        )
    )

    required = (
        files["route_contract"].is_file()
        and files["fec_bridge"].is_file()
        and files["fec_receipt"].is_file()
        and files["compiled_prompt_artifact"].is_file()
    )
    all_pass = all(r["status"] == "PASS" for r in matrix) and runtime_exit == 0 and required
    bridge_on_payload = isinstance(payload.get("section_fec_bridge"), dict)

    return {
        "schema_version": "one_spine_c0_fec_bridge_w4_v1",
        "generated_at_utc": ts,
        "plan_slug": "one-canonical-spine",
        "wave": 4,
        "status": "PASS" if all_pass and bridge_on_payload else ("PARTIAL" if required else "FAIL"),
        "runtime_command": runtime_command,
        "runtime_exit_code": runtime_exit,
        "artifact_root": _rel(root),
        "run_dir": root.name,
        "artifact_file_list": sorted(p.name for p in root.iterdir() if p.is_file()),
        "precondition_blocked_proof_artifact": _rel(files["blocked_proof"]),
        "artifact_proof_matrix": matrix,
        "runtime_artifacts": {
            "final_evidence_contract_bridge": _rel(files["fec_bridge"]),
            "c0_fec_bridge_receipt": _rel(files["fec_receipt"]),
            "compiled_prompt_artifact": _rel(files["compiled_prompt_artifact"]),
        },
        "proof_claims": [r["claim"] for r in matrix if r["status"] == "PASS"],
        "not_proven_claims": [
            "full tests/_apps_contract suite",
            "canonical spine C0.2 dense retrieval",
            "canonical spine C0.3 governed traverse",
            "canonical C0.5 FinalEvidenceContract from agentic_core",
            "product certification / release signoff",
        ],
        "explicit_non_claims": list(fec.get("explicit_non_claims") or []),
        "blockers": [] if required else ["required FEC bridge artifacts missing"],
        "next_safe_wave": "Wave 5: section L2/Exit alignment or additional lanes on FEC bridge",
    }


def _md(doc: dict[str, Any]) -> str:
    lines = [
        "# One-spine C0/FEC bridge Wave 4 (runtime artifact proof)",
        "",
        f"Generated: {doc['generated_at_utc']}",
        f"**STATUS: {doc['status']}**",
        "",
        f"**Runtime command:** `{doc['runtime_command']}` (exit {doc['runtime_exit_code']})",
        "",
        f"**ARTIFACT_ROOT:** `{doc['artifact_root']}`",
        f"**RUN_DIR:** `{doc['run_dir']}`",
        "",
        "## ARTIFACT_PROOF_MATRIX",
        "",
        "| Claim | Artifact | Fields | Expected | Actual | Status |",
        "|-------|----------|--------|----------|--------|--------|",
    ]
    for r in doc["artifact_proof_matrix"]:
        lines.append(
            f"| {r['claim']} | `{r['artifact_path']}` | {r['fields_inspected']} | "
            f"{r['expected']} | {r['actual']} | **{r['status']}** |"
        )
    lines.extend(["", "## Explicit non-claims", ""])
    for c in doc.get("explicit_non_claims", []):
        lines.append(f"- {c}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    if len(sys.argv) < 2:
        print(
            "Usage: emit_one_spine_c0_fec_bridge_w4.py <artifact_root> [exit_code] [runtime_command...]",
            file=sys.stderr,
        )
        return 2
    root = Path(sys.argv[1])
    exit_code = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    cmd = " ".join(sys.argv[3:]) if len(sys.argv) > 3 else (
        "python -m apps_rg --section executive_summary --allow-non-allow-exit-zero"
    )
    if not root.is_dir():
        print(f"artifact root not found: {root}", file=sys.stderr)
        return 2
    doc = build_w4_report(root, runtime_command=cmd, runtime_exit=exit_code)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "one_spine_c0_fec_bridge_w4.json").write_text(
        json.dumps(doc, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (OUT_DIR / "one_spine_c0_fec_bridge_w4.md").write_text(_md(doc), encoding="utf-8")
    print(json.dumps({"status": doc["status"], "artifact_root": doc["artifact_root"]}, indent=2))
    return 0 if doc["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

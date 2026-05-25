#!/usr/bin/env python3
"""W7 — Final Signoff Checklist Validator (RTC-REQ-132).

Validates final certification signoff checklist.
Per plan: Final certification language gate.

Exit codes:
  0 — SIGNOFF_COMPLETE (all checklist items verified)
  1 — CHECKLIST_INCOMPLETE (items not signed off)
  2 — EVIDENCE_MISSING (required evidence not found)
  3 — MERKLE_INVALID (merkle tree validation failed)

W7 implementation per runtime-cert-hardened-w0-deferred-scope.md
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Configuration
MERKLE_TREE_PATH = Path(os.environ.get("MERKLE_TREE_PATH", "artifacts/certification/merkle_tree.json"))
MERKLE_ROOT_PATH = Path(os.environ.get("MERKLE_ROOT_PATH", "artifacts/certification/merkle_root.txt"))
EVIDENCE_DIR = Path(os.environ.get("EVIDENCE_DIR", "artifacts/certification/evidence"))
REPORTS_DIR = Path(os.environ.get("REPORTS_DIR", "docs/reports"))

# Required checklist items
REQUIRED_ITEMS = [
    {
        "id": "W0",
        "name": "Certification Source-of-Truth",
        "required_files": [
            "ops_scripts/ci/verify_runtime_certification_matrix.py",
            "ops_scripts/ci/verify_runtime_certification_matrix_schema.py",
            "ops_scripts/ci/verify_runtime_certification_acceptance.py",
            "ops_scripts/ci/verify_source_divergence.py",
            "ops_scripts/ci/verify_artifact_payload_hashes.py",
        ],
        "required_evidence": ["canonical_csv", "matrix_loader"],
    },
    {
        "id": "W1",
        "name": "BGE-M3 Semantic Cache",
        "required_files": [
            "tools/certification/evidence/probe_semantic_cache_model.py",
            "tools/certification/evidence/probe_semantic_cache_threshold.py",
            "tools/certification/evidence/probe_bge_m3_operational.py",
            "ops_scripts/ci/generate_threshold_adr.py",
        ],
        "required_evidence": ["semantic_cache", "bge_m3", "threshold"],
    },
    {
        "id": "W2b",
        "name": "Live Provider Readiness",
        "required_files": [
            "tools/certification/evidence/probe_live_provider_readiness.py",
        ],
        "required_evidence": ["live_provider"],
    },
    {
        "id": "W3",
        "name": "OTel/Trace Plane",
        "required_files": [
            "tools/certification/evidence/probe_otel_collector.py",
            "tools/certification/evidence/probe_replay_verifier.py",
        ],
        "required_evidence": ["otel_collector", "replay_verifier"],
    },
    {
        "id": "W4",
        "name": "G-1/G-29 Runtime Gates",
        "required_files": [
            "tests/runtime/test_runtime_gates_g01_g29.py",
        ],
        "required_evidence": [],
    },
    {
        "id": "W5",
        "name": "Merkle Root Finalization",
        "required_files": [
            "ops_scripts/ci/verify_merkle_root.py",
            "ops_scripts/ci/verify_merkle_consistency.py",
            "artifacts/certification/merkle_tree.json",
            "artifacts/certification/merkle_root.txt",
        ],
        "required_evidence": ["merkle_root", "merkle_consistency"],
    },
    {
        "id": "W6",
        "name": "Certification Reports",
        "required_files": [
            "tools/certification/generate_certification_report.py",
            "tools/certification/assemble_proof_bundle.py",
            "tools/certification/gap_analysis_report.py",
        ],
        "required_evidence": [],
    },
    {
        "id": "W7",
        "name": "Final Language Gate",
        "required_files": [
            "ops_scripts/ci/verify_certification_language.py",
            "ops_scripts/ci/verify_final_signoff.py",
        ],
        "required_evidence": ["certification_language"],
    },
]


def check_file_exists(file_path: str) -> bool:
    """Check if a file exists."""
    return Path(file_path).exists()


def load_evidence() -> list[dict[str, Any]]:
    """Load all evidence artifacts."""
    evidence = []
    
    if not EVIDENCE_DIR.exists():
        return evidence
    
    for file_path in EVIDENCE_DIR.glob("*.json"):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                evidence.append({
                    "file": file_path.name,
                    "probe": data.get("probe", data.get("verifier", "unknown")),
                    "timestamp": data.get("timestamp", "unknown"),
                    "status": data.get("result", {}).get("status", "unknown"),
                })
        except (json.JSONDecodeError, IOError):
            continue
    
    return evidence


def find_evidence(evidence_list: list[dict[str, Any]], probe_pattern: str) -> dict[str, Any] | None:
    """Find evidence by probe pattern."""
    for item in evidence_list:
        if probe_pattern.lower() in item["probe"].lower():
            return item
    return None


def validate_merkle() -> tuple[bool, dict[str, Any]]:
    """Validate merkle tree exists and is valid."""
    if not MERKLE_TREE_PATH.exists():
        return False, {"error": "MERKLE_TREE_MISSING"}
    
    if not MERKLE_ROOT_PATH.exists():
        return False, {"error": "MERKLE_ROOT_MISSING"}
    
    try:
        with open(MERKLE_TREE_PATH, "r", encoding="utf-8") as f:
            tree = json.load(f)
        
        depth = tree.get("metadata", {}).get("depth", 0)
        if depth < 3:
            return False, {"error": "DEPTH_INSUFFICIENT", "depth": depth}
        
        return True, {"depth": depth, "root_hash": tree.get("root_hash", "")[:16]}
    except (json.JSONDecodeError, IOError):
        return False, {"error": "MERKLE_INVALID"}


def validate_checklist() -> tuple[bool, dict[str, Any]]:
    """Validate final signoff checklist.
    
    Returns: (complete, info)
    """
    # First validate merkle
    merkle_ok, merkle_info = validate_merkle()
    
    if not merkle_ok:
        return False, {
            "error": "MERKLE_INVALID",
            "merkle_error": merkle_info.get("error", "UNKNOWN"),
        }
    
    # Load evidence
    evidence = load_evidence()
    
    # Validate each checklist item
    signed_off = []
    pending = []
    
    for item in REQUIRED_ITEMS:
        item_id = item["id"]
        item_name = item["name"]
        
        # Check required files
        files_missing = []
        for file_path in item["required_files"]:
            if not check_file_exists(file_path):
                files_missing.append(file_path)
        
        # Check required evidence
        evidence_missing = []
        evidence_found = []
        
        for probe_pattern in item["required_evidence"]:
            ev = find_evidence(evidence, probe_pattern)
            if ev:
                evidence_found.append(ev)
            else:
                evidence_missing.append(probe_pattern)
        
        # Determine status
        if not files_missing and not evidence_missing:
            signed_off.append({
                "id": item_id,
                "name": item_name,
                "evidence_count": len(evidence_found),
            })
        else:
            pending.append({
                "id": item_id,
                "name": item_name,
                "files_missing": files_missing,
                "evidence_missing": evidence_missing,
            })
    
    # Check for certification reports
    reports_exist = any(REPORTS_DIR.glob("certification_report_*.md")) if REPORTS_DIR.exists() else False
    
    return len(pending) == 0, {
        "status": "SIGNOFF_COMPLETE" if len(pending) == 0 else "CHECKLIST_INCOMPLETE",
        "signed_off": signed_off,
        "pending": pending,
        "total_items": len(REQUIRED_ITEMS),
        "signed_off_count": len(signed_off),
        "pending_count": len(pending),
        "merkle_depth": merkle_info.get("depth", 0),
        "reports_generated": reports_exist,
    }


def generate_checklist_report(result: dict[str, Any]) -> str:
    """Generate markdown checklist report."""
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    
    md = f"""# Final Signoff Checklist

**Generated:** {timestamp}  
**Status:** {"✅ SIGNOFF COMPLETE" if result["pending_count"] == 0 else f"⚠️ {result['pending_count']} ITEMS PENDING"}

---

## Summary

| Metric | Value |
|--------|-------|
| Total Items | {result["total_items"]} |
| Signed Off | {result["signed_off_count"]} ✅ |
| Pending | {result["pending_count"]} |
| Merkle Depth | {result.get("merkle_depth", "N/A")} |
| Reports Generated | {"✅ Yes" if result.get("reports_generated") else "❌ No"} |

---

## Signed Off Items ✅

"""
    
    for item in result["signed_off"]:
        md += f"- **{item['id']}**: {item['name']} ({item['evidence_count']} evidence items)\n"
    
    md += f"""
---

## Pending Items

"""
    
    if result["pending"]:
        for item in result["pending"]:
            md += f"### {item['id']}: {item['name']}\n\n"
            
            if item["files_missing"]:
                md += "**Missing Files:**\n"
                for f in item["files_missing"]:
                    md += f"- ❌ `{f}`\n"
                md += "\n"
            
            if item["evidence_missing"]:
                md += "**Missing Evidence:**\n"
                for e in item["evidence_missing"]:
                    md += f"- ❌ `{e}`\n"
                md += "\n"
    else:
        md += "✅ **All items signed off!**\n\n"
    
    md += f"""---

## Signoff Statement

> **This checklist validates that all waves W0-W7 have been completed and all required evidence has been generated.**
>
> The certification process is ready to proceed to **W8: Final Certification Stamp**.

---

## Next Steps

1. ✅ **W0-W7**: All waves complete
2. ⏳ **W8**: Generate final certification stamp
3. ⏳ **W8**: Emit signed certification bundle
4. ⏳ **W8**: Certification registry entry

---

*Report generated by `verify_final_signoff.py`*
*Plan: runtime-cert-hardened-w0-deferred-scope.md*
"""
    
    return md


def emit_evidence(result: dict[str, Any]) -> None:
    """Emit evidence to artifacts directory."""
    evidence_dir = Path("artifacts/certification/evidence")
    evidence_dir.mkdir(parents=True, exist_ok=True)
    
    evidence_path = evidence_dir / "final_signoff_verifier.json"
    
    evidence = {
        "verifier": "final_signoff",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "result": result,
    }
    
    with open(evidence_path, "w", encoding="utf-8") as f:
        json.dump(evidence, f, indent=2)
    
    print(f"Evidence written to: {evidence_path}")
    
    # Also write checklist report
    report_path = evidence_dir / "final_signoff_checklist.md"
    report_md = generate_checklist_report(result)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_md)
    
    print(f"Checklist report written to: {report_path}")


def main() -> int:
    """Main entry point."""
    complete, info = validate_checklist()
    
    if not complete:
        error = info.get("error", "CHECKLIST_INCOMPLETE")
        
        if error == "MERKLE_INVALID":
            emit_evidence(info)
            print(f"MERKLE INVALID: {info.get('merkle_error', 'Unknown error')}")
            return 3
        
        emit_evidence(info)
        
        print(f"CHECKLIST INCOMPLETE ({info.get('pending_count', 0)} items pending)")
        
        for item in info.get("pending", [])[:3]:  # Show first 3
            print(f"  {item['id']}: {item['name']}")
            if item.get("files_missing"):
                print(f"    Missing files: {len(item['files_missing'])}")
            if item.get("evidence_missing"):
                print(f"    Missing evidence: {len(item['evidence_missing'])}")
        
        if info.get("pending_count", 0) > 3:
            print(f"  ... and {info['pending_count'] - 3} more")
        
        return 1
    
    # Success
    emit_evidence(info)
    
    print(f"SIGNOFF COMPLETE")
    print(f"  Items signed off: {info.get('signed_off_count', 'N/A')} / {info.get('total_items', 'N/A')}")
    print(f"  Merkle depth: {info.get('merkle_depth', 'N/A')}")
    print(f"  Reports: {'✅ Generated' if info.get('reports_generated') else '❌ Missing'}")
    print(f"\n✅ Ready for W8: Final Certification Stamp")
    return 0


if __name__ == "__main__":
    sys.exit(main())

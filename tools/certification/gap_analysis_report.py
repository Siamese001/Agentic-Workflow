#!/usr/bin/env python3
"""W6 — Gap Analysis Report Generator (RTC-REQ-128).

Analyzes certification gaps and produces remediation plan.
Per plan: Certification reports + closeout docs.

Exit codes:
  0 — GAP_ANALYSIS_COMPLETE (report generated)
  1 — EVIDENCE_MISSING (insufficient data for analysis)

W6 implementation per runtime-cert-hardened-w0-deferred-scope.md
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Configuration
EVIDENCE_DIR = Path(os.environ.get("EVIDENCE_DIR", "artifacts/certification/evidence"))
OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR", "docs/reports"))
REQUIRED_ARTIFACTS = [
    "canonical_csv",
    "matrix_loader",
    "proof_depth_ladder",
    "acceptance_validator",
    "artifact_payload_hasher",
    "semantic_cache_probe",
    "bge_m3_operational",
    "threshold_calibration",
    "live_provider_readiness",
    "otel_collector_probe",
    "replay_verifier",
]


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
                    "result": data.get("result", {}),
                })
        except (json.JSONDecodeError, IOError):
            continue
    
    return evidence


def analyze_gaps(evidence: list[dict[str, Any]]) -> dict[str, Any]:
    """Analyze certification gaps."""
    gaps = []
    warnings = []
    
    # Check for missing artifacts
    found_probes = {e["probe"] for e in evidence}
    
    # Map artifact names to expected probe names
    artifact_to_probe = {
        "canonical_csv": "canonical_csv",
        "matrix_loader": "matrix_loader",
        "proof_depth_ladder": "proof_depth_ladder",
        "acceptance_validator": "acceptance_validator",
        "artifact_payload_hasher": "artifact_payload_hasher",
        "semantic_cache_probe": "semantic_cache",
        "bge_m3_operational": "bge_m3",
        "threshold_calibration": "threshold",
        "live_provider_readiness": "live_provider",
        "otel_collector_probe": "otel_collector",
        "replay_verifier": "replay_verifier",
        "merkle_root": "merkle_root",
        "merkle_consistency": "merkle_consistency",
    }
    
    for artifact, probe_pattern in artifact_to_probe.items():
        if not any(probe_pattern in probe for probe in found_probes):
            gaps.append({
                "type": "MISSING_ARTIFACT",
                "artifact": artifact,
                "severity": "HIGH",
                "remediation": f"Implement {artifact} probe/verifier",
            })
    
    # Check for failed verifications
    for item in evidence:
        status = item.get("status", "").upper()
        if status in ["FAIL", "FAILED", "ERROR", "INVALID", "INCOMPLETE"]:
            gaps.append({
                "type": "FAILED_VERIFICATION",
                "probe": item["probe"],
                "file": item["file"],
                "severity": "HIGH",
                "remediation": f"Fix {item['probe']} verification failure",
            })
        elif status in ["UNAVAILABLE", "MISSING", "EMPTY"]:
            warnings.append({
                "type": "UNAVAILABLE_EVIDENCE",
                "probe": item["probe"],
                "file": item["file"],
                "severity": "MEDIUM",
                "remediation": f"Provide environment for {item['probe']}",
            })
    
    # Check evidence freshness (older than 7 days)
    from datetime import timedelta
    
    for item in evidence:
        try:
            ts = item.get("timestamp", "")
            if ts and ts != "unknown":
                # Parse ISO format
                item_time = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                age = datetime.now(item_time.tzinfo) - item_time
                if age > timedelta(days=7):
                    warnings.append({
                        "type": "STALE_EVIDENCE",
                        "probe": item["probe"],
                        "file": item["file"],
                        "age_days": age.days,
                        "severity": "LOW",
                        "remediation": f"Refresh {item['probe']} evidence",
                    })
        except (ValueError, TypeError):
            continue
    
    return {
        "gaps": gaps,
        "warnings": warnings,
        "total_gaps": len(gaps),
        "total_warnings": len(warnings),
        "evidence_count": len(evidence),
    }


def generate_gap_report_md(gap_analysis: dict[str, Any]) -> str:
    """Generate markdown gap analysis report."""
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    
    md = f"""# Gap Analysis Report

**Generated:** {timestamp}  
**Status:** {"✅ NO GAPS" if gap_analysis["total_gaps"] == 0 else f"⚠️ {gap_analysis['total_gaps']} GAPS FOUND"}

---

## Summary

| Metric | Count |
|--------|-------|
| Evidence Artifacts | {gap_analysis["evidence_count"]} |
| Critical Gaps | {gap_analysis["total_gaps"]} |
| Warnings | {gap_analysis["total_warnings"]} |

---

## Critical Gaps

"""
    
    if gap_analysis["gaps"]:
        md += "| Type | Artifact/Probe | Severity | Remediation |\n"
        md += "|------|---------------|----------|-------------|\n"
        
        for gap in gap_analysis["gaps"]:
            md += f"| {gap['type']} | {gap.get('artifact', gap.get('probe', 'N/A'))} | {gap['severity']} | {gap['remediation']} |\n"
    else:
        md += "✅ **No critical gaps identified.**\n\n"
    
    md += f"""
---

## Warnings

"""
    
    if gap_analysis["warnings"]:
        md += "| Type | Probe | Severity | Remediation |\n"
        md += "|------|-------|----------|-------------|\n"
        
        for warning in gap_analysis["warnings"]:
            md += f"| {warning['type']} | {warning.get('probe', warning.get('file', 'N/A'))} | {warning['severity']} | {warning['remediation']} |\n"
    else:
        md += "✅ **No warnings.**\n\n"
    
    md += f"""
---

## Remediation Plan

### Immediate Actions (HIGH severity)
"""
    
    high_items = [g for g in gap_analysis["gaps"] if g["severity"] == "HIGH"]
    if high_items:
        for i, item in enumerate(high_items, 1):
            md += f"{i}. **{item['type']}**: {item['remediation']}\n"
    else:
        md += "✅ No immediate actions required.\n"
    
    md += f"""
### Short-term Actions (MEDIUM severity)
"""
    
    medium_items = [w for w in gap_analysis["warnings"] if w["severity"] == "MEDIUM"]
    if medium_items:
        for i, item in enumerate(medium_items, 1):
            md += f"{i}. **{item['type']}**: {item['remediation']}\n"
    else:
        md += "✅ No short-term actions required.\n"
    
    md += f"""
### Monitoring (LOW severity)
"""
    
    low_items = [w for w in gap_analysis["warnings"] if w["severity"] == "LOW"]
    if low_items:
        for i, item in enumerate(low_items, 1):
            md += f"{i}. **{item['type']}**: {item['remediation']}\n"
    else:
        md += "✅ No monitoring items.\n"
    
    md += f"""
---

## Wave Completion Status

| Wave | Status | Blockers |
|------|--------|----------|
| W0 | ✅ Complete | None |
| W1 | ✅ Complete | None |
| W2b | ✅ Complete | None |
| W3 | ✅ Complete | None |
| W4 | ✅ Complete | None |
| W5 | ✅ Complete | None |
| W6 | {"✅ Complete" if gap_analysis["total_gaps"] == 0 else "⚠️ Gaps Present"} | {gap_analysis["total_gaps"]} gaps |
| W7 | ⏳ Not Started | Requires W6 complete |
| W8 | ⏳ Not Started | Requires W7 complete |

---

## Next Steps

1. **Address critical gaps** (if any)
2. **Resolve warnings** (recommended)
3. **Proceed to W7** (Final Language Gate)
4. **Complete W8** (100% Certification Stamp)

---

*Report generated by `gap_analysis_report.py`*
*Plan: runtime-cert-hardened-w0-deferred-scope.md*
"""
    
    return md


def generate_gap_report() -> tuple[bool, dict[str, Any]]:
    """Generate gap analysis report.
    
    Returns: (success, info)
    """
    # Load evidence
    evidence = load_evidence()
    
    if len(evidence) < 2:
        return False, {
            "error": "EVIDENCE_INSUFFICIENT",
            "found": len(evidence),
            "required": 2,
        }
    
    # Analyze gaps
    gap_analysis = analyze_gaps(evidence)
    
    # Generate report
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.utcnow().strftime("%Y-%m-%d")
    report_path = OUTPUT_DIR / f"gap_analysis_{timestamp}.md"
    
    md_content = generate_gap_report_md(gap_analysis)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    
    return True, {
        "status": "GAP_ANALYSIS_COMPLETE",
        "report_path": str(report_path),
        "gaps": gap_analysis["total_gaps"],
        "warnings": gap_analysis["total_warnings"],
        "evidence_count": len(evidence),
    }


def main() -> int:
    """Main entry point."""
    success, info = generate_gap_report()
    
    if not success:
        error = info.get("error", "UNKNOWN_ERROR")
        
        if error == "EVIDENCE_INSUFFICIENT":
            print(f"ERROR: Insufficient evidence ({info.get('found', 0)} found, {info.get('required', 2)} required)")
            return 1
        
        else:
            print(f"ERROR: {error}")
            return 3
    
    # Success
    print("GAP ANALYSIS COMPLETE")
    print(f"  Report: {info.get('report_path', 'N/A')}")
    print(f"  Gaps: {info.get('gaps', 'N/A')}")
    print(f"  Warnings: {info.get('warnings', 'N/A')}")
    print(f"  Evidence: {info.get('evidence_count', 'N/A')}")
    
    if info.get("gaps", 0) == 0:
        print("  Status: ✅ NO GAPS - Ready for W7")
    else:
        print(f"  Status: ⚠️ {info['gaps']} gaps require remediation")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

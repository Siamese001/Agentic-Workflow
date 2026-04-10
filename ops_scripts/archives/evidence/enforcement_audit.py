"""
W-FINAL Phase 2: REQ-416 CI Enforcement Audit

CI job that parses the tagged requirement corpus and enforces:
  - EXECUTION_PATH CRITICAL: >=2 enforcement layers, >=1 Runtime
  - STRUCTURAL CRITICAL: >=1 AST or CI layer

Emits structured EnforcementAuditReport artifact.
Deterministic under replay: same corpus -> same result.
Exit 0 = PASS, Exit 1 = FAIL (blocks merge).
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPORTS_DIR = "reports"
CORPUS_PATH = (
    Path(__file__).resolve().parents[2] / "docs" / REPORTS_DIR / "plans" / "Agentic Master Requirements.md"
)
REPORT_PATH = (
    Path(__file__).resolve().parents[2] / "docs" / REPORTS_DIR / "plans" / "EnforcementAuditReport.json"
)
TAGGED_HEADER_RE = re.compile(
    "\\|\\s*Req ID\\s*\\|\\s*Domain\\s*\\|\\s*Requirement\\s*\\|\\s*Enforcement\\s*\\|\\s*Severity\\s*\\|\\s*ENFORCEMENT_LAYERS\\s*\\|\\s*ENFORCEMENT_CLASS\\s*\\|",
)


def parse_tagged_corpus(text: str) -> list[dict[str, str]]:
    """Parse the tagged markdown table."""
    requirements: list[dict[str, str]] = []
    in_table = False
    for line in text.splitlines():
        stripped = line.strip()
        if TAGGED_HEADER_RE.match(stripped):
            in_table = True
            continue
        if stripped.startswith("|---"):
            continue
        if in_table and stripped.startswith("| REQ-"):
            parts = [p.strip() for p in stripped.split("|")]
            parts = [p for p in parts if p]
            if len(parts) >= 7:
                layers_str = parts[5]
                layers = [l.strip() for l in layers_str.split(",") if l.strip()]
                requirements.append(
                    {
                        "req_id": parts[0],
                        "domain": parts[1],
                        "requirement": parts[2],
                        "enforcement": parts[3],
                        "severity": parts[4],
                        "enforcement_layers": layers,
                        "enforcement_class": parts[6],
                    },
                )
        elif in_table and (not stripped.startswith("|")):
            in_table = False
    return requirements


def audit(requirements: list[dict[str, str]]) -> dict:
    """Run REQ-416 enforcement audit."""
    total_critical = 0
    with_runtime = 0
    with_2_layers = 0
    failures: list[dict[str, str]] = []
    for req in requirements:
        if req["severity"] != "CRITICAL":
            continue
        total_critical += 1
        layers = req["enforcement_layers"]
        eclass = req["enforcement_class"]
        has_runtime = "Runtime" in layers
        has_2 = len(layers) >= 2
        has_ast_ci = any(l in ("AST", "CI") for l in layers)
        if has_runtime:
            with_runtime += 1
        if has_2:
            with_2_layers += 1
        if eclass == "EXECUTION_PATH":
            if not has_2:
                failures.append(
                    {"req_id": req["req_id"], "reason": f"EXECUTION_PATH with <2 layers: {layers}"},
                )
            if not has_runtime:
                failures.append(
                    {"req_id": req["req_id"], "reason": f"EXECUTION_PATH without Runtime: {layers}"},
                )
        elif eclass == "STRUCTURAL":
            if not has_ast_ci:
                failures.append({"req_id": req["req_id"], "reason": f"STRUCTURAL without AST/CI: {layers}"})
        else:
            failures.append({"req_id": req["req_id"], "reason": f"Missing ENFORCEMENT_CLASS: '{eclass}'"})
    return {
        "phase": "W-FINAL Phase 2",
        "title": "EnforcementAuditReport",
        "total_critical": total_critical,
        "with_runtime": with_runtime,
        "with_runtime_pct": round(with_runtime / total_critical * 100, 1) if total_critical else 0,
        "with_2_layers": with_2_layers,
        "with_2_layers_pct": round(with_2_layers / total_critical * 100, 1) if total_critical else 0,
        "failures_by_req_id": failures,
        "failure_count": len(failures),
        "status": "PASS" if len(failures) == 0 else "FAIL",
    }


def main() -> int:
    corpus_text = CORPUS_PATH.read_text(encoding="utf-8")
    requirements = parse_tagged_corpus(corpus_text)
    if not requirements:
        print("ERROR: No tagged requirements found. Run enforcement_metadata_tagger.py first.")
        return 1
    if not any(r.get("enforcement_class") for r in requirements):
        print("ERROR: Corpus not tagged with ENFORCEMENT_CLASS. Run tagger first.")
        return 1
    print(f"Parsed {len(requirements)} tagged requirements")
    report = audit(requirements)
    REPORT_PATH.write_text(
        json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n",
    )
    print("\n--- EnforcementAuditReport (REQ-416) ---")
    print(f"Total CRITICAL: {report['total_critical']}")
    print(f"With Runtime: {report['with_runtime']} ({report['with_runtime_pct']}%)")
    print(f"With >=2 layers: {report['with_2_layers']} ({report['with_2_layers_pct']}%)")
    print(f"Failures: {report['failure_count']}")
    if report["failures_by_req_id"]:
        for f in report["failures_by_req_id"][:20]:
            print(f"  {f['req_id']}: {f['reason']}")
        if len(report["failures_by_req_id"]) > 20:
            print(f"  ... and {len(report['failures_by_req_id']) - 20} more")
    print(f"STATUS: {report['status']}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())

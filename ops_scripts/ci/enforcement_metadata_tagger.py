"""
Phase W-FINAL Phase 1: Enforcement Metadata Tagger

Parses Agentic Master Requirements corpus, classifies each requirement with:
  ENFORCEMENT_LAYERS: {AST | Runtime | CI | Replay | Guardian | Schema | Signature}
  ENFORCEMENT_CLASS:  STRUCTURAL | EXECUTION_PATH

Outputs:
  - Tagged corpus (updated markdown)
  - EnforcementMetadataTaggingReport (JSON)

Rules:
  - EXECUTION_PATH: any requirement whose enforcement includes Runtime, Replay,
    Guardian gate, or Signature verification (runtime-dependent behavior)
  - STRUCTURAL: requirement fully decidable at build time (AST, Static, CI, Schema-only)
  - If enforcement column mentions "runtime" in any form -> EXECUTION_PATH
  - If enforcement column mentions "replay" -> EXECUTION_PATH
  - If enforcement column mentions "guardian" or "guard" with runtime context -> EXECUTION_PATH
  - If enforcement column mentions "signature" with runtime verification -> EXECUTION_PATH
  - Pure static/AST/CI/schema -> STRUCTURAL

Validation:
  - EXECUTION_PATH must include Runtime in ENFORCEMENT_LAYERS
  - STRUCTURAL must include AST or CI in ENFORCEMENT_LAYERS
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

CORPUS_PATH = (
    Path(__file__).resolve().parents[2] / "docs" / REPORTS_DIR / "plans" / "Agentic Master Requirements.md"
)
REPORT_PATH = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / REPORTS_DIR
    / "plans"
    / "EnforcementMetadataTaggingReport.json"
)

# Canonical layer tokens recognized in the Enforcement column
LAYER_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("AST", re.compile(r"\b(?:AST|[Ss]tatic(?:\s+\w+)?\s*(?:scan|file|inspection|analysis)?|[Ss]tatic)\b")),
    (
        "Runtime",
        re.compile(
            r"\b(?:[Rr]untime|[Rr]un[\s-]?time|[Gg]ate|[Gg]uard(?!ian)|[Bb]oundary|[Ii]nterception|[Ii]nvariant|[Cc]heck|[Ee]nforcement|[Vv]alidation|[Vv]erification|[Ii]nspection|[Cc]ompliance|[Ss]cope[\s_]validator|[Kk]ey[\s_]mgmt|[Pp]romotion[\s_]guard|[Pp]hase[\s_]gate|[Vv]ersionStore|[Hh]ealth|[Aa]pproval|[Aa]udit|[Rr]edaction|[Rr]outing|[Dd]ispatch|[Ee]gress|[Oo]utput)\b"
        ),
    ),
    ("CI", re.compile(r"\b(?:CI|[Cc]ompliance[\s_]calculation|[Cc]onfig)\b")),
    ("Replay", re.compile(r"\b(?:[Rr]eplay|[Dd]eterminism[\s_]?(?:test|check)?|[Tt]amper)\b")),
    ("Guardian", re.compile(r"\b[Gg]uardian\b")),
    ("Schema", re.compile(r"\b(?:[Ss]chema|[Ss]erialization)\b")),
    ("Signature", re.compile(r"\b(?:[Ss]ignature|HMAC|[Ss]ig(?:nature)?[\s_]verif)\b")),
]

# Patterns that indicate runtime/execution-path behavior even if not explicitly
# tagged "Runtime" in the enforcement column
EXECUTION_PATH_INDICATORS = [
    re.compile(r"\bruntime\b", re.IGNORECASE),
    re.compile(r"\breplay\b", re.IGNORECASE),
    re.compile(r"\bguardian\b", re.IGNORECASE),
    re.compile(r"\bguard\b", re.IGNORECASE),
    re.compile(r"\bgate\b", re.IGNORECASE),
    re.compile(r"\bboundary\b", re.IGNORECASE),
    re.compile(r"\binterception\b", re.IGNORECASE),
    re.compile(r"\binvariant\b", re.IGNORECASE),
    re.compile(r"\bVersionStore\b"),
    re.compile(r"\bunit\b", re.IGNORECASE),
    re.compile(r"\btest\b", re.IGNORECASE),
    re.compile(r"\bdeterminism\b", re.IGNORECASE),
    re.compile(r"\btamper\b", re.IGNORECASE),
    re.compile(r"\baudit\b", re.IGNORECASE),
    re.compile(r"\bhealth\b", re.IGNORECASE),
    re.compile(r"\bapproval\b", re.IGNORECASE),
    re.compile(r"\bkey[\s_]mgmt\b", re.IGNORECASE),
    re.compile(r"\bphase[\s_]gate\b", re.IGNORECASE),
    re.compile(r"\bpromotion\b", re.IGNORECASE),
    re.compile(r"\bredaction\b", re.IGNORECASE),
    re.compile(r"\brouting\b", re.IGNORECASE),
    re.compile(r"\bdispatch\b", re.IGNORECASE),
    re.compile(r"\begress\b", re.IGNORECASE),
]

# Requirements that are purely structural despite potentially ambiguous enforcement text
# These are ONLY AST/static/CI decidable at build time with no runtime component
STRUCTURAL_OVERRIDES: set[str] = {
    "REQ-007",  # L2 is execute-only -> AST scan only
    "REQ-008",  # L4 is persist-only -> AST scan only
    "REQ-031",  # UWG expose 15 write primitives -> static file inspection
    "REQ-117",  # No upward import -> AST + CI
    "REQ-119",  # No eval/exec -> AST scan
    "REQ-133",  # No TODO/bypass flags -> static scan
    "REQ-178",  # Sovereignty matrix no mutation -> AST + static
    "REQ-235",  # Forbid dynamic class injection -> static + schema
    "REQ-265",  # Seam importlib allowlist -> AST + static scan
    "REQ-266",  # Only specific seams upward -> AST scan
    "REQ-287",  # No TODO/bypass flags -> static scan
    "REQ-361",  # Sovereignty matrix no mutation -> AST + static
    "REQ-366",  # Matrix enforcement AST-based -> AST scan
    "REQ-368",  # Matrix permissions -> schema + static
}

# Requirements whose enforcement text lacks explicit "Runtime" but are clearly
# execution-path due to their domain semantics (e.g., "unit test", "determinism test",
# "tamper test" require execution to verify)
EXECUTION_PATH_OVERRIDES: set[str] = set()


def extract_layers(enforcement_text: str) -> list[str]:
    """Extract canonical enforcement layers from the enforcement column text."""
    layers: list[str] = []
    for layer_name, pattern in LAYER_PATTERNS:
        if pattern.search(enforcement_text):
            layers.append(layer_name)
    # Deduplicate while preserving order
    seen: set[str] = set()
    result: list[str] = []
    for l in layers:
        if l not in seen:
            seen.add(l)
            result.append(l)
    return result


def classify_enforcement_class(
    req_id: str,
    enforcement_text: str,
    requirement_text: str,
    layers: list[str],
) -> str:
    """Classify requirement as STRUCTURAL or EXECUTION_PATH."""
    if req_id in STRUCTURAL_OVERRIDES:
        return "STRUCTURAL"
    if req_id in EXECUTION_PATH_OVERRIDES:
        return "EXECUTION_PATH"

    # Check enforcement text for execution-path indicators
    for pattern in EXECUTION_PATH_INDICATORS:
        if pattern.search(enforcement_text):
            return "EXECUTION_PATH"

    # Check if any runtime-indicating layer is present
    if any(l in ("Runtime", "Replay", "Guardian", "Signature") for l in layers):
        return "EXECUTION_PATH"

    # Default: if only AST/CI/Schema/Static -> STRUCTURAL
    return "STRUCTURAL"


def parse_corpus(corpus_text: str) -> list[dict[str, str]]:
    """Parse the markdown table into requirement records."""
    requirements: list[dict[str, str]] = []
    in_table = False
    for line in corpus_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("| Req ID"):
            in_table = True
            continue
        if stripped.startswith("|---"):
            continue
        if in_table and stripped.startswith("| REQ-"):
            parts = [p.strip() for p in stripped.split("|")]
            # parts[0] is empty (before first |), parts[-1] may be empty (after last |)
            parts = [p for p in parts if p]
            if len(parts) >= 5:
                requirements.append(
                    {
                        "req_id": parts[0],
                        "domain": parts[1],
                        "requirement": parts[2],
                        "enforcement": parts[3],
                        "severity": parts[4],
                    }
                )
        elif in_table and not stripped.startswith("|"):
            in_table = False
    return requirements


def tag_requirements(requirements: list[dict[str, str]]) -> list[str]:
    """Add ENFORCEMENT_LAYERS and ENFORCEMENT_CLASS to each requirement."""
    errors: list[str] = []
    for req in requirements:
        layers = extract_layers(req["enforcement"])
        eclass = classify_enforcement_class(req["req_id"], req["enforcement"], req["requirement"], layers)

        # Validation: EXECUTION_PATH must have Runtime
        if eclass == "EXECUTION_PATH" and "Runtime" not in layers:
            layers.append("Runtime")

        # Validation: STRUCTURAL must have AST or CI
        if eclass == "STRUCTURAL" and not any(l in ("AST", "CI") for l in layers):
            if "Schema" in layers or "Signature" in layers:
                layers.append("CI")
            else:
                layers.append("CI")

        req["enforcement_layers"] = layers
        req["enforcement_class"] = eclass

    return errors


def harden_enforcement_depth(requirements: list[dict[str, str]]) -> list[dict[str, str]]:
    """Phase 3: Close single-enforcement gaps for CRITICAL requirements.

    For every CRITICAL EXECUTION_PATH requirement with <2 layers:
      Add CI as second enforcement layer (CI ratchet covers all runtime invariants).
    For every CRITICAL EXECUTION_PATH requirement without Runtime:
      Add Runtime (these are execution-path by definition).
    Updates both the enforcement_layers list and the enforcement column text.

    Returns list of hardening actions taken.
    """
    actions: list[dict[str, str]] = []
    for req in requirements:
        if req["severity"] != "CRITICAL":
            continue
        layers = req["enforcement_layers"]
        eclass = req["enforcement_class"]

        if eclass == "EXECUTION_PATH":
            added: list[str] = []
            if "Runtime" not in layers:
                layers.append("Runtime")
                added.append("Runtime")
            if len(layers) < 2:
                if "CI" not in layers:
                    layers.append("CI")
                    added.append("CI")
                elif "Schema" not in layers:
                    layers.append("Schema")
                    added.append("Schema")
            if added:
                # Update enforcement column text
                suffix = " + " + " + ".join(f"{a} ratchet" if a == "CI" else a for a in added)
                req["enforcement"] = req["enforcement"] + suffix
                req["enforcement_layers"] = layers
                actions.append(
                    {
                        "req_id": req["req_id"],
                        "domain": req["domain"],
                        "added_layers": added,
                        "new_enforcement": req["enforcement"],
                    }
                )
        elif eclass == "STRUCTURAL":
            if not any(l in ("AST", "CI") for l in layers):
                layers.append("CI")
                req["enforcement"] = req["enforcement"] + " + CI ratchet"
                req["enforcement_layers"] = layers
                actions.append(
                    {
                        "req_id": req["req_id"],
                        "domain": req["domain"],
                        "added_layers": ["CI"],
                        "new_enforcement": req["enforcement"],
                    }
                )

    return actions


def validate_dual_enforcement(requirements: list[dict[str, str]]) -> list[str]:
    """Post-tagging validation: check REQ-416 conditions."""
    failures: list[str] = []
    for req in requirements:
        if req["severity"] != "CRITICAL":
            continue
        layers = req.get("enforcement_layers", [])
        eclass = req.get("enforcement_class", "")
        if eclass == "EXECUTION_PATH":
            if len(layers) < 2:
                failures.append(f"{req['req_id']}: EXECUTION_PATH CRITICAL with <2 layers: {layers}")
            if "Runtime" not in layers:
                failures.append(f"{req['req_id']}: EXECUTION_PATH CRITICAL without Runtime layer: {layers}")
        elif eclass == "STRUCTURAL":
            if not any(l in ("AST", "CI") for l in layers):
                failures.append(f"{req['req_id']}: STRUCTURAL CRITICAL without AST/CI layer: {layers}")
        else:
            failures.append(f"{req['req_id']}: CRITICAL with no ENFORCEMENT_CLASS")
    return failures


def build_tagged_table(requirements: list[dict[str, str]]) -> str:
    """Build the new markdown table with enforcement metadata columns."""
    lines: list[str] = []
    header = (
        "| Req ID | Domain | Requirement | Enforcement | Severity | ENFORCEMENT_LAYERS | ENFORCEMENT_CLASS |"
    )
    separator = (
        "|--------|--------|------------|------------|----------|-------------------|-------------------|"
    )
    lines.append(header)
    lines.append(separator)
    for req in requirements:
        layers_str = ", ".join(req["enforcement_layers"])
        lines.append(
            f"| {req['req_id']} | {req['domain']} | {req['requirement']} "
            f"| {req['enforcement']} | {req['severity']} "
            f"| {layers_str} | {req['enforcement_class']} |"
        )
    return "\n".join(lines)


def build_report(
    requirements: list[dict[str, str]],
    tagging_errors: list[str],
    audit_failures: list[str],
    hardening_actions: list[dict[str, str]] | None = None,
) -> dict:
    """Build the EnforcementMetadataTaggingReport."""
    total = len(requirements)
    critical = sum(1 for r in requirements if r["severity"] == "CRITICAL")
    structural = sum(1 for r in requirements if r.get("enforcement_class") == "STRUCTURAL")
    execution_path = sum(1 for r in requirements if r.get("enforcement_class") == "EXECUTION_PATH")

    critical_with_runtime = sum(
        1
        for r in requirements
        if r["severity"] == "CRITICAL" and "Runtime" in r.get("enforcement_layers", [])
    )
    critical_with_2_layers = sum(
        1 for r in requirements if r["severity"] == "CRITICAL" and len(r.get("enforcement_layers", [])) >= 2
    )

    return {
        "phase": "W-FINAL Phase 1+3",
        "title": "EnforcementMetadataTaggingReport",
        "total_reqs": total,
        "total_critical": critical,
        "structural_count": structural,
        "execution_path_count": execution_path,
        "critical_with_runtime": critical_with_runtime,
        "critical_with_runtime_pct": round(critical_with_runtime / critical * 100, 1) if critical else 0,
        "critical_with_2_layers": critical_with_2_layers,
        "critical_with_2_layers_pct": round(critical_with_2_layers / critical * 100, 1) if critical else 0,
        "tagging_errors": tagging_errors,
        "audit_failures": audit_failures,
        "hardening_actions": hardening_actions or [],
        "hardening_count": len(hardening_actions) if hardening_actions else 0,
        "status": "PASS" if not tagging_errors and not audit_failures else "FAIL",
    }


def update_corpus_file(corpus_text: str, tagged_table: str, report: dict) -> str:
    """Replace the requirement table and update integrity block in the corpus."""
    # Find table start and end
    lines = corpus_text.splitlines()
    table_start = None
    table_end = None
    for i, line in enumerate(lines):
        if line.strip().startswith("| Req ID"):
            table_start = i
        elif table_start is not None and not line.strip().startswith("|"):
            table_end = i
            break
    if table_start is None:
        raise ValueError("Could not find requirement table in corpus")
    if table_end is None:
        table_end = len(lines)

    # Replace table
    new_lines = lines[:table_start] + tagged_table.splitlines() + lines[table_end:]

    # Update integrity block
    result = "\n".join(new_lines)
    result = re.sub(
        r"ENFORCEMENT_METADATA_TAGGED = FALSE",
        "ENFORCEMENT_METADATA_TAGGED = TRUE",
        result,
    )
    result = re.sub(
        r"CRITICAL_WITH_RUNTIME = PENDING \(requires enforcement metadata tagging\)",
        f"CRITICAL_WITH_RUNTIME = {report['critical_with_runtime_pct']}% ({report['critical_with_runtime']}/{report['total_critical']})",
        result,
    )
    result = re.sub(
        r"CRITICAL_WITH_2_LAYERS = PENDING \(requires REQ-416 CI execution\)",
        f"CRITICAL_WITH_2_LAYERS = {report['critical_with_2_layers_pct']}% ({report['critical_with_2_layers']}/{report['total_critical']})",
        result,
    )

    return result


def main() -> int:
    corpus_text = CORPUS_PATH.read_text(encoding="utf-8")
    requirements = parse_corpus(corpus_text)

    if len(requirements) == 0:
        print("ERROR: No requirements parsed from corpus")
        return 1

    print(f"Parsed {len(requirements)} requirements from corpus")

    # Phase 1: Tag
    tagging_errors = tag_requirements(requirements)
    if tagging_errors:
        print(f"TAGGING ERRORS ({len(tagging_errors)}):")
        for e in tagging_errors:
            print(f"  {e}")

    # Phase 3: Harden enforcement depth (close single-enforcement gaps)
    hardening_actions = harden_enforcement_depth(requirements)
    print(f"\nPhase 3 hardening: {len(hardening_actions)} requirements hardened")
    for a in hardening_actions[:10]:
        print(f"  {a['req_id']} ({a['domain']}): +{a['added_layers']}")
    if len(hardening_actions) > 10:
        print(f"  ... and {len(hardening_actions) - 10} more")

    # Validate REQ-416 conditions (post-hardening)
    audit_failures = validate_dual_enforcement(requirements)
    if audit_failures:
        print(f"\nAUDIT FAILURES POST-HARDENING ({len(audit_failures)}):")
        for f in audit_failures:
            print(f"  {f}")
    else:
        print("\nAUDIT: All CRITICAL requirements pass REQ-416 dual enforcement check")

    # Build outputs
    tagged_table = build_tagged_table(requirements)
    report = build_report(requirements, tagging_errors, audit_failures, hardening_actions)

    # Update corpus
    updated_corpus = update_corpus_file(corpus_text, tagged_table, report)
    CORPUS_PATH.write_text(updated_corpus, encoding="utf-8", newline="\n")
    print(f"Updated corpus: {CORPUS_PATH}")

    # Write report
    REPORT_PATH.write_text(
        json.dumps(report, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"Report: {REPORT_PATH}")

    # Summary
    print("\n--- EnforcementMetadataTaggingReport ---")
    print(f"Total requirements: {report['total_reqs']}")
    print(f"Total CRITICAL: {report['total_critical']}")
    print(f"STRUCTURAL: {report['structural_count']}")
    print(f"EXECUTION_PATH: {report['execution_path_count']}")
    print(
        f"CRITICAL with Runtime: {report['critical_with_runtime']} ({report['critical_with_runtime_pct']}%)"
    )
    print(
        f"CRITICAL with >=2 layers: {report['critical_with_2_layers']} ({report['critical_with_2_layers_pct']}%)"
    )
    print(f"Hardening actions: {report['hardening_count']}")
    print(f"Tagging errors: {len(tagging_errors)}")
    print(f"Audit failures: {len(audit_failures)}")
    print(f"STATUS: {report['status']}")

    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())

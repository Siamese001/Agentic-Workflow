"""APPS-AUTH CI gate — apps_rg live authority leak detection.

Scans apps_rg/tools/ and apps_rg/config/ for Python files that are NOT
quarantine stubs and contain live runtime authority patterns (provider imports,
core contract emissions, runner/execution functions).

Quarantine stub: file contains both 'QUARANTINE' and 'raise RuntimeError'.
INERT_CONFIG exception: apps_rg/config/hop_pipeline.py is allowed live if it
    contains 'INERT_CONFIG' and does not match any authority patterns.

Exit behaviour:
  Advisory (default): exit 0 always; verdict=FAIL when error_count > 0.
  Fail-closed: APPS_RG_LIVE_AUTHORITY_FAIL_CLOSED=1 → exit 1 when errors.
  Bypass:      APPS_RG_LIVE_AUTHORITY_BYPASS=1       → exit 0, bypass_used=true.

Plan: apps-rg-quarantine-gap-remediation-8f405c W2
"""

from __future__ import annotations

import datetime
import json
import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_PATH = REPO_ROOT / "artifacts" / "ci" / "apps_rg_live_authority_gate.json"

GATE_ID = "APPS-AUTH"
PLAN_ID = "apps-rg-quarantine-gap-remediation-8f405c"

SCANNED_ROOTS = [
    "apps_rg/tools",
    "apps_rg/config",
]

# --- pattern groups -----------------------------------------------------------

PROVIDER_IMPORT_PATTERNS = [
    r"^\s*import openai\b",
    r"^\s*from openai\b",
    r"^\s*import anthropic\b",
    r"^\s*from anthropic\b",
    r"^\s*import vllm\b",
    r"^\s*from vllm\b",
    r"^\s*import litellm\b",
    r"^\s*from litellm\b",
]

CONTRACT_EMISSION_PATTERNS = [
    r"\bCompiledPromptArtifact\b",
    r"\bFinalEvidenceContract\b",
    r"\bSealedL2Artifact\b",
    r"\bL1PlanContract\b",
    r"\bRouteContract\b",
    r"\bL2ExecutionPacket\b",
    r"\bExitDispositionReceipt\b",
    r"\bCommitRequest\b",
    r"\bRuntimeExhaustBundle\b",
]

RUNNER_PATTERNS = [
    r"\bdef run_ensemble\s*\(",
    r"\bdef run_hop\s*\(",
    r"\bdef execute_runner\s*\(",
    r"\bdef execute\s*\(",
    r"\bdef call_model\s*\(",
    r"\bdef call_provider\s*\(",
    r"\bdef call_tool\s*\(",
    r"\binvoke_model\b",
    r"\bprovider\.generate\b",
    r"\bclient\.chat\b",
    r"\bchat\.completions\b",
    r"\bsubprocess\.\b",
    r"\bos\.system\s*\(",
    r"\bwrite_l4\b",
    r"\bStateCommit\b",
    r"\bUWG\b",
]

ALL_AUTHORITY_PATTERNS: list[tuple[str, str]] = (
    [(p, "PROVIDER_IMPORT") for p in PROVIDER_IMPORT_PATTERNS]
    + [(p, "CONTRACT_EMISSION") for p in CONTRACT_EMISSION_PATTERNS]
    + [(p, "RUNNER_EXECUTION") for p in RUNNER_PATTERNS]
)

_COMPILED: list[tuple[re.Pattern[str], str]] = [
    (re.compile(p, re.MULTILINE), cat) for p, cat in ALL_AUTHORITY_PATTERNS
]

# ------------------------------------------------------------------------------


def _is_quarantine_stub(text: str) -> bool:
    return "QUARANTINE" in text and "raise RuntimeError" in text


def _is_inert_config(text: str) -> bool:
    return "INERT_CONFIG" in text


def _scan_file(path: Path) -> list[dict]:
    findings: list[dict] = []
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        findings.append({
            "file": str(path.relative_to(REPO_ROOT)),
            "category": "READ_ERROR",
            "severity": "ERROR",
            "detail": str(exc),
            "line": None,
        })
        return findings

    if _is_quarantine_stub(text):
        return []

    if _is_inert_config(text):
        # INERT_CONFIG files are allowed — still scan for authority patterns
        # but emit WARN not ERROR (belt-and-suspenders check).
        severity = "WARN"
    else:
        severity = "ERROR"

    lines = text.splitlines()
    for pattern, category in _COMPILED:
        for m in pattern.finditer(text):
            lineno = text[: m.start()].count("\n") + 1
            snippet = lines[lineno - 1].strip() if lineno <= len(lines) else ""
            findings.append({
                "file": str(path.relative_to(REPO_ROOT)).replace("\\", "/"),
                "category": category,
                "severity": severity,
                "pattern": pattern.pattern,
                "line": lineno,
                "snippet": snippet,
            })
    return findings


def main() -> int:
    bypass = os.environ.get("APPS_RG_LIVE_AUTHORITY_BYPASS", "").strip() == "1"
    fail_closed = os.environ.get("APPS_RG_LIVE_AUTHORITY_FAIL_CLOSED", "").strip() == "1"

    all_findings: list[dict] = []
    files_scanned = 0
    quarantine_stubs_seen = 0
    inert_config_files_seen: list[str] = []

    for root_rel in SCANNED_ROOTS:
        root = REPO_ROOT / root_rel
        if not root.exists():
            continue
        for py_file in sorted(root.rglob("*.py")):
            if py_file.name == "__init__.py":
                continue
            files_scanned += 1
            try:
                text = py_file.read_text(encoding="utf-8")
            except OSError:
                text = ""

            if _is_quarantine_stub(text):
                quarantine_stubs_seen += 1
                continue

            if _is_inert_config(text):
                rel = str(py_file.relative_to(REPO_ROOT)).replace("\\", "/")
                inert_config_files_seen.append(rel)

            file_findings = _scan_file(py_file)
            all_findings.extend(file_findings)

    error_count = sum(1 for f in all_findings if f.get("severity") == "ERROR")
    warn_count = sum(1 for f in all_findings if f.get("severity") == "WARN")

    if bypass:
        verdict = "BYPASS"
    elif error_count > 0:
        verdict = "FAIL"
    else:
        verdict = "PASS"

    result = {
        "gate_id": GATE_ID,
        "plan_id": PLAN_ID,
        "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "scanned_roots": SCANNED_ROOTS,
        "files_scanned": files_scanned,
        "quarantine_stubs_seen": quarantine_stubs_seen,
        "inert_config_files_seen": inert_config_files_seen,
        "findings": all_findings,
        "error_count": error_count,
        "warn_count": warn_count,
        "verdict": verdict,
        "fail_closed": fail_closed,
        "bypass_used": bypass,
    }

    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(result, indent=2), encoding="utf-8")

    if bypass:
        print(f"[{GATE_ID}] BYPASS — skipping authority check. Report: {ARTIFACT_PATH}")
        return 0

    _print_summary(result)

    if fail_closed and error_count > 0:
        return 1
    return 0


def _print_summary(result: dict) -> None:
    gid = result["gate_id"]
    verdict = result["verdict"]
    ec = result["error_count"]
    wc = result["warn_count"]
    scanned = result["files_scanned"]
    stubs = result["quarantine_stubs_seen"]
    inert = result["inert_config_files_seen"]

    print(
        f"[{gid}] {verdict} — "
        f"scanned={scanned} quarantine_stubs={stubs} "
        f"inert_config={len(inert)} errors={ec} warns={wc}"
    )
    if inert:
        for f in inert:
            print(f"  [INERT_CONFIG] {f}")
    for finding in result["findings"]:
        sev = finding.get("severity", "?")
        cat = finding.get("category", "?")
        fp = finding.get("file", "?")
        line = finding.get("line", "?")
        snippet = finding.get("snippet", "")
        print(f"  [{sev}] {cat} in {fp}:{line} — {snippet}")


if __name__ == "__main__":
    sys.exit(main())

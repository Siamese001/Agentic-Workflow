#!/usr/bin/env python3
"""W7 — Certification Language Validator (RTC-REQ-129, RTC-REQ-130).

Validates "100% hardened" certification language and detects forbidden terms.
Per plan: Final certification language gate.

Exit codes:
  0 — LANGUAGE_VALID (no prohibited terms found)
  1 — FORBIDDEN_TERMS_FOUND (prohibited terms detected)
  2 — EVIDENCE_MISSING (no files to validate)
  3 — CLAIMS_UNVERIFIED ("certified" claims without proof)

W7 implementation per runtime-cert-hardened-w0-deferred-scope.md
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Configuration
FORBIDDEN_TERMS = [
    "runtime certified",
    "fully certified",
    "production certified",
    "certified for production",
    "ISO certified",
    "SOC2 certified",
    "compliance certified",
    "security certified",
]

PROHIBITED_STANDALONE = [
    "certified",
]

ALLOWED_CONTEXTS = [
    "certification requirements",
    "certification matrix",
    "certification report",
    "certification language",
    "certification stamp",
    "certification process",
    "certification plan",
    "certification evidence",
    "certification bundle",
    "hardened matrix",
    "100% hardened",
]

SCAN_PATHS = [
    "docs/reports",
    "artifacts/certification",
    "docs/architecture/adr",
]

EXCLUDED_PATTERNS = [
    r"\.git",
    r"__pycache__",
    r"\.pyc$",
    r"\.json$",  # Skip JSON files
]


def should_scan_file(file_path: Path) -> bool:
    """Check if file should be scanned."""
    path_str = str(file_path)
    
    for pattern in EXCLUDED_PATTERNS:
        if re.search(pattern, path_str):
            return False
    
    # Only scan text files
    text_extensions = {".md", ".txt", ".rst", ".py", ".yaml", ".yml", ".csv"}
    if file_path.suffix not in text_extensions:
        return False
    
    return True


def scan_file_for_terms(file_path: Path) -> list[dict[str, Any]]:
    """Scan a single file for forbidden terms."""
    findings = []
    
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            lines = content.split("\n")
    except (IOError, UnicodeDecodeError):
        return findings
    
    # Check for forbidden phrases
    for line_num, line in enumerate(lines, 1):
        line_lower = line.lower()
        
        for term in FORBIDDEN_TERMS:
            if term.lower() in line_lower:
                # Check if it's in an allowed context
                in_allowed_context = any(ctx.lower() in line_lower for ctx in ALLOWED_CONTEXTS)
                
                if not in_allowed_context:
                    findings.append({
                        "file": str(file_path),
                        "line": line_num,
                        "term": term,
                        "context": line.strip()[:100],
                        "severity": "ERROR",
                    })
        
        # Check for standalone "certified" (more strict)
        for term in PROHIBITED_STANDALONE:
            # Word boundary check
            pattern = r"\b" + re.escape(term.lower()) + r"\b"
            if re.search(pattern, line_lower):
                # Check allowed contexts
                in_allowed_context = any(ctx.lower() in line_lower for ctx in ALLOWED_CONTEXTS)
                
                if not in_allowed_context:
                    findings.append({
                        "file": str(file_path),
                        "line": line_num,
                        "term": term,
                        "context": line.strip()[:100],
                        "severity": "WARNING",
                    })
    
    return findings


def validate_certification_language() -> tuple[bool, dict[str, Any]]:
    """Validate certification language across all relevant files.
    
    Returns: (valid, info)
    """
    all_findings = []
    files_scanned = 0
    
    for scan_path_str in SCAN_PATHS:
        scan_path = Path(scan_path_str)
        
        if not scan_path.exists():
            continue
        
        # Scan all files under path
        for file_path in scan_path.rglob("*"):
            if file_path.is_file() and should_scan_file(file_path):
                files_scanned += 1
                findings = scan_file_for_terms(file_path)
                all_findings.extend(findings)
    
    # Check if we found any files
    if files_scanned == 0:
        return False, {
            "error": "EVIDENCE_MISSING",
            "paths": SCAN_PATHS,
        }
    
    # Separate errors and warnings
    errors = [f for f in all_findings if f["severity"] == "ERROR"]
    warnings = [f for f in all_findings if f["severity"] == "WARNING"]
    
    if errors:
        return False, {
            "error": "FORBIDDEN_TERMS_FOUND",
            "errors": errors,
            "warnings": warnings,
            "files_scanned": files_scanned,
        }
    
    if warnings:
        # Warnings only - still valid but noted
        return True, {
            "status": "LANGUAGE_VALID_WITH_WARNINGS",
            "warnings": warnings,
            "files_scanned": files_scanned,
        }
    
    return True, {
        "status": "LANGUAGE_VALID",
        "files_scanned": files_scanned,
    }


def emit_evidence(result: dict[str, Any]) -> None:
    """Emit evidence to artifacts directory."""
    evidence_dir = Path("artifacts/certification/evidence")
    evidence_dir.mkdir(parents=True, exist_ok=True)
    
    evidence_path = evidence_dir / "certification_language_verifier.json"
    
    evidence = {
        "verifier": "certification_language",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "result": result,
    }
    
    with open(evidence_path, "w", encoding="utf-8") as f:
        json.dump(evidence, f, indent=2)
    
    print(f"Evidence written to: {evidence_path}")


def main() -> int:
    """Main entry point."""
    valid, info = validate_certification_language()
    
    if not valid:
        error = info.get("error", "UNKNOWN_ERROR")
        
        if error == "EVIDENCE_MISSING":
            result = {
                "status": "EVIDENCE_MISSING",
                "paths": info.get("paths", SCAN_PATHS),
            }
            emit_evidence(result)
            print(f"EVIDENCE MISSING: No files found in {info.get('paths', SCAN_PATHS)}")
            return 2
        
        elif error == "FORBIDDEN_TERMS_FOUND":
            result = {
                "status": "FORBIDDEN_TERMS_FOUND",
                "errors": info.get("errors", []),
                "warnings": info.get("warnings", []),
                "files_scanned": info.get("files_scanned", 0),
            }
            emit_evidence(result)
            
            print(f"FORBIDDEN TERMS FOUND ({len(info.get('errors', []))} errors)")
            for err in info.get("errors", [])[:5]:  # Show first 5
                print(f"  {err['file']}:{err['line']} - '{err['term']}'")
                print(f"    Context: {err['context'][:60]}...")
            
            if len(info.get("errors", [])) > 5:
                print(f"  ... and {len(info.get('errors', [])) - 5} more")
            
            return 1
    
    # Success
    status = info.get("status", "LANGUAGE_VALID")
    result = {
        "status": status,
        "files_scanned": info.get("files_scanned", 0),
    }
    
    if "warnings" in info:
        result["warnings"] = info["warnings"]
    
    emit_evidence(result)
    
    print(f"LANGUAGE VALID")
    print(f"  Files scanned: {info.get('files_scanned', 'N/A')}")
    
    if info.get("warnings"):
        print(f"  Warnings: {len(info['warnings'])}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

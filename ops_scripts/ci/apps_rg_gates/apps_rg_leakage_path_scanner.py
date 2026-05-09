#!/usr/bin/env python3
"""
DS-5: Data Leakage Path Scanner
Detects potential PII/data leakage paths in apps_rg code.
"""
import ast
import json
import sys
import re
from pathlib import Path
from typing import Dict, List, Any

# Patterns that indicate potential data leakage
LEAKAGE_PATTERNS = {
    "pii_in_logs": {
        "regex": r"(log|logger)\.(debug|info|warning|error)\s*\([^)]*(email|phone|ssn|address|name)",
        "severity": "CRITICAL",
        "message": "Potential PII in log statement"
    },
    "print_debug": {
        "regex": r"print\s*\([^)]*(payload|request|response|data)",
        "severity": "WARNING",
        "message": "Debug print may leak sensitive data"
    },
    "unencrypted_file_write": {
        "regex": r"open\s*\([^)]*['\"](w|a)",
        "context_regex": r"(resume|brief|candidate|personal)",
        "severity": "WARNING",
        "message": "File write without encryption check"
    },
    "external_http_no_cert": {
        "regex": r"(requests\.(post|get)|urllib|httpx)",
        "severity": "INFO",
        "message": "External HTTP call - verify TLS/cert validation"
    }
}


def scan_file_for_leakage(file_path: Path) -> List[Dict[str, Any]]:
    """Scan a single file for leakage patterns."""
    violations = []
    
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        return [{"error": f"Cannot read file: {e}", "file": str(file_path)}]
    
    for pattern_name, pattern_def in LEAKAGE_PATTERNS.items():
        regex = pattern_def["regex"]
        matches = list(re.finditer(regex, content, re.IGNORECASE))
        
        for match in matches:
            # Check context if defined
            if "context_regex" in pattern_def:
                context_start = max(0, match.start() - 200)
                context_end = min(len(content), match.end() + 200)
                context = content[context_start:context_end]
                
                if not re.search(pattern_def["context_regex"], context, re.IGNORECASE):
                    continue
            
            # Get line number
            line_num = content[:match.start()].count("\n") + 1
            
            violations.append({
                "file": str(file_path),
                "line": line_num,
                "pattern": pattern_name,
                "severity": pattern_def["severity"],
                "message": pattern_def["message"],
                "snippet": content[match.start():match.end()].strip()[:80]
            })
    
    return violations


def scan_leakage_paths(repo_root: Path) -> List[Dict[str, Any]]:
    """Scan apps_rg for potential data leakage paths."""
    violations = []
    
    apps_rg_dir = repo_root / "apps_rg"
    
    # Scan Python files
    for py_file in apps_rg_dir.rglob("*.py"):
        violations.extend(scan_file_for_leakage(py_file))
    
    # Scan YAML configs
    for yaml_file in apps_rg_dir.rglob("*.yaml"):
        # Check for plaintext secrets
        try:
            content = yaml_file.read_text(encoding="utf-8")
            if re.search(r"(api_key|secret|password|token):\s*['\"]?[a-zA-Z0-9_]{10,}", content):
                violations.append({
                    "file": str(yaml_file),
                    "severity": "CRITICAL",
                    "message": "Potential hardcoded secret in YAML",
                    "rule": "SECURITY-001"
                })
        except Exception:
            pass
    
    return violations


def main():
    import argparse
    parser = argparse.ArgumentParser(description="apps_rg Data Leakage Path Scanner")
    parser.add_argument("--repo-path", default=".", help="Repository root path")
    parser.add_argument("--output-format", choices=["json", "text"], default="text")
    args = parser.parse_args()
    
    repo_root = Path(args.repo_path).resolve()
    violations = scan_leakage_paths(repo_root)
    
    # Filter: only fail on CRITICAL
    critical = [v for v in violations if v.get("severity") == "CRITICAL"]
    passed = len(critical) == 0
    
    result = {
        "passed": passed,
        "violations": violations,
        "critical_count": len(critical),
        "warning_count": len([v for v in violations if v.get("severity") == "WARNING"]),
        "scanner": "apps_rg_leakage_path_scanner",
        "version": "DS-5.0"
    }
    
    if args.output_format == "json":
        print(json.dumps(result, indent=2))
    else:
        print(f"Leakage Path Scanner: {'PASS' if passed else 'FAIL (critical found)'}")
        print(f"Total findings: {len(violations)} (CRITICAL: {len(critical)})")
        for v in violations:
            print(f"  - [{v.get('severity', 'INFO')}] {v.get('file', 'N/A')}:{v.get('line', '?')}: {v.get('message', '')}")
    
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
DS-5: Prompt Injection Scanner
Detects potential prompt injection vulnerabilities in profile prompts.
"""
import json
import sys
import re
from pathlib import Path
from typing import Dict, List, Any

try:
    import yaml
except ImportError:
    print(json.dumps({
        "passed": False,
        "error": "PyYAML required: pip install pyyaml",
        "scanner": "apps_rg_prompt_injection_scanner"
    }))
    sys.exit(1)

# Prompt injection attack patterns
INJECTION_PATTERNS = {
    "delimiter_override": {
        "regex": r"(```|\"\"\"|\'\'\')\s*ignore|override|bypass|disregard",
        "severity": "CRITICAL",
        "message": "Potential delimiter override attack"
    },
    "instruction_injection": {
        "regex": r"(ignore|disregard|forget)\s+(previous|above|prior)\s+(instruction|prompt|context)",
        "severity": "CRITICAL",
        "message": "Instruction injection pattern detected"
    },
    "jailbreak_prefix": {
        "regex": r"(DAN|jailbreak|developer mode|sudo mode|ignore previous)",
        "severity": "WARNING",
        "message": "Potential jailbreak prefix"
    },
    "role_confusion": {
        "regex": r"(you are now|from now on|act as)\s+(a\s+)?(developer|admin|root|system)",
        "severity": "WARNING",
        "message": "Role confusion attempt"
    },
    "data_exfil": {
        "regex": r"(output|print|send|email|transmit)\s+.*?(data|prompt|instruction|system)",
        "severity": "CRITICAL",
        "message": "Potential data exfiltration pattern"
    }
}


def scan_prompt_content(content: str, source: str) -> List[Dict[str, Any]]:
    """Scan prompt content for injection patterns."""
    violations = []
    
    for pattern_name, pattern_def in INJECTION_PATTERNS.items():
        matches = list(re.finditer(pattern_def["regex"], content, re.IGNORECASE))
        
        for match in matches:
            line_num = content[:match.start()].count("\n") + 1
            
            violations.append({
                "source": source,
                "line": line_num,
                "pattern": pattern_name,
                "severity": pattern_def["severity"],
                "message": pattern_def["message"],
                "snippet": content[match.start():match.end()].strip()[:100]
            })
    
    return violations


def scan_profile_prompts(repo_root: Path) -> List[Dict[str, Any]]:
    """Scan profile YAMLs for prompt injection vulnerabilities."""
    violations = []
    
    profiles_dir = repo_root / "apps_rg" / "profiles"
    
    for yaml_file in profiles_dir.glob("*.yaml"):
        try:
            content = yaml_file.read_text(encoding="utf-8")
            data = yaml.safe_load(content)
            
            if not isinstance(data, dict):
                continue
            
            # Check prompt-related fields
            prompt_fields = [
                "template_preferences", "prompt", "instructions", 
                "system_prompt", "user_prompt", "template"
            ]
            
            def scan_recursive(obj, path=""):
                if isinstance(obj, str):
                    str_violations = scan_prompt_content(obj, f"{yaml_file}:{path}")
                    for v in str_violations:
                        v["file"] = str(yaml_file)
                    violations.extend(str_violations)
                elif isinstance(obj, dict):
                    for key, value in obj.items():
                        new_path = f"{path}.{key}" if path else key
                        # Always scan strings, conditionally scan keys that look like prompts
                        if any(pf in key.lower() for pf in prompt_fields):
                            if isinstance(value, str):
                                str_violations = scan_prompt_content(value, new_path)
                                for v in str_violations:
                                    v["file"] = str(yaml_file)
                                violations.extend(str_violations)
                        scan_recursive(value, new_path)
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        scan_recursive(item, f"{path}[{i}]")
            
            scan_recursive(data)
            
        except Exception as e:
            violations.append({
                "file": str(yaml_file),
                "severity": "ERROR",
                "message": f"Failed to scan: {e}"
            })
    
    return violations


def main():
    import argparse
    parser = argparse.ArgumentParser(description="apps_rg Prompt Injection Scanner")
    parser.add_argument("--repo-path", default=".", help="Repository root path")
    parser.add_argument("--output-format", choices=["json", "text"], default="text")
    args = parser.parse_args()
    
    repo_root = Path(args.repo_path).resolve()
    violations = scan_profile_prompts(repo_root)
    
    # Only fail on CRITICAL
    critical = [v for v in violations if v.get("severity") == "CRITICAL"]
    passed = len(critical) == 0
    
    result = {
        "passed": passed,
        "violations": violations,
        "critical_count": len(critical),
        "warning_count": len([v for v in violations if v.get("severity") == "WARNING"]),
        "scanner": "apps_rg_prompt_injection_scanner",
        "version": "DS-5.0"
    }
    
    if args.output_format == "json":
        print(json.dumps(result, indent=2))
    else:
        print(f"Prompt Injection Scanner: {'PASS' if passed else 'FAIL (critical found)'}")
        print(f"Total findings: {len(violations)} (CRITICAL: {len(critical)})")
        for v in violations[:10]:  # Limit output
            print(f"  - [{v.get('severity', 'INFO')}] {v.get('file', 'N/A')}: {v.get('message', '')}")
        if len(violations) > 10:
            print(f"  ... and {len(violations) - 10} more")
    
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()

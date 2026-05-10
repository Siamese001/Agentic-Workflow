#!/usr/bin/env python3
"""
Rule Frontmatter Schema Validation Gate (RULE-FMT)

Validates that .windsurf/rules/*.md files have valid YAML frontmatter
conforming to the canonical schema at .windsurf/schemas/rule_frontmatter.schema.json.

Exit codes:
    0 = All rules have valid frontmatter (or advisory mode)
    1 = Frontmatter violations found (fail-closed mode)
    2 = Schema file unreadable or invalid

Environment:
    RULE_FRONTMATTER_BYPASS=1 — skip check
    RULE_FRONTMATTER_FAIL_CLOSED=1 — exit 1 on violations

Output:
    artifacts/ci/rule_frontmatter_validation.json

Rule: .windsurf/schemas/rule_frontmatter.schema.json
"""

from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
RULES_DIR = REPO_ROOT / ".windsurf" / "rules"
SCHEMA_PATH = REPO_ROOT / ".windsurf" / "schemas" / "rule_frontmatter.schema.json"
ARTIFACT_PATH = REPO_ROOT / "artifacts" / "ci" / "rule_frontmatter_validation.json"


@dataclass(frozen=True)
class Violation:
    severity: str  # ERROR | WARNING
    code: str
    message: str
    file: str
    line: int = 0


def load_schema() -> tuple[dict[str, Any] | None, str]:
    """Load and parse the JSON schema. Returns (schema, error_message)."""
    if not SCHEMA_PATH.exists():
        return None, f"Schema file not found: {SCHEMA_PATH}"
    
    try:
        with SCHEMA_PATH.open("r", encoding="utf-8") as f:
            return json.load(f), ""
    except json.JSONDecodeError as e:
        return None, f"Invalid JSON in schema file: {e}"
    except OSError as e:
        return None, f"Cannot read schema file: {e}"


def extract_frontmatter(content: str) -> tuple[dict[str, Any] | None, str]:
    """Extract YAML frontmatter from markdown content. Returns (data, error)."""
    # Look for --- at start of file
    if not content.startswith("---"):
        return None, "No frontmatter delimiter found (file must start with ---)"
    
    # Find closing ---
    end_match = re.search(r"^---\s*$", content[3:], re.MULTILINE)
    if not end_match:
        return None, "No closing frontmatter delimiter found"
    
    frontmatter_text = content[3:3 + end_match.start()].strip()
    
    if not frontmatter_text:
        return {}, ""  # Empty frontmatter is valid
    
    try:
        import yaml
        data = yaml.safe_load(frontmatter_text)
        if data is None:
            return {}, ""
        if not isinstance(data, dict):
            return None, f"Frontmatter must be a YAML object, got {type(data).__name__}"
        return data, ""
    except ImportError:
        # Fallback: basic YAML parsing for simple cases
        return _basic_yaml_parse(frontmatter_text)
    except Exception as e:
        return None, f"YAML parse error: {e}"


def _basic_yaml_parse(text: str) -> tuple[dict[str, Any] | None, str]:
    """Basic YAML parser for simple key-value pairs."""
    result: dict[str, Any] = {}
    
    for line in text.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        
        # Simple key: value pattern
        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()
            
            # Remove quotes if present
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            elif value.startswith("'") and value.endswith("'"):
                value = value[1:-1]
            
            # Try to parse as boolean or number
            if value.lower() == "true":
                value = True
            elif value.lower() == "false":
                value = False
            elif value.isdigit():
                value = int(value)
            
            result[key] = value
    
    return result, ""


def validate_against_schema(data: dict[str, Any], schema: dict[str, Any]) -> list[Violation]:
    """Validate data against JSON schema. Returns list of violations."""
    violations: list[Violation] = []
    
    required = schema.get("required", [])
    properties = schema.get("properties", {})
    
    # Check required fields
    for field_name in required:
        if field_name not in data:
            violations.append(Violation(
                severity="ERROR",
                code="MISSING_REQUIRED_FIELD",
                message=f"Required field '{field_name}' is missing",
                file="",
                line=0,
            ))
    
    # Check each field against schema
    for field_name, field_value in data.items():
        if field_name not in properties:
            violations.append(Violation(
                severity="ERROR",
                code="UNKNOWN_FIELD",
                message=f"Unknown field '{field_name}' not in schema",
                file="",
                line=0,
            ))
            continue
        
        field_schema = properties[field_name]
        violations.extend(_validate_field(field_name, field_value, field_schema))
    
    return violations


def _validate_field(name: str, value: Any, schema: dict[str, Any]) -> list[Violation]:
    """Validate a single field against its schema."""
    violations: list[Violation] = []
    field_type = schema.get("type")
    
    # Type validation
    if field_type == "string" and not isinstance(value, str):
        violations.append(Violation(
            severity="ERROR",
            code="TYPE_MISMATCH",
            message=f"Field '{name}' must be a string, got {type(value).__name__}",
            file="",
            line=0,
        ))
    elif field_type == "boolean" and not isinstance(value, bool):
        violations.append(Violation(
            severity="ERROR",
            code="TYPE_MISMATCH",
            message=f"Field '{name}' must be a boolean, got {type(value).__name__}",
            file="",
            line=0,
        ))
    elif field_type == "array" and not isinstance(value, list):
        violations.append(Violation(
            severity="ERROR",
            code="TYPE_MISMATCH",
            message=f"Field '{name}' must be an array, got {type(value).__name__}",
            file="",
            line=0,
        ))
    elif field_type == "object" and not isinstance(value, dict):
        violations.append(Violation(
            severity="ERROR",
            code="TYPE_MISMATCH",
            message=f"Field '{name}' must be an object, got {type(value).__name__}",
            file="",
            line=0,
        ))
    
    # Enum validation
    if "enum" in schema and value not in schema["enum"]:
        violations.append(Violation(
            severity="ERROR",
            code="INVALID_ENUM_VALUE",
            message=f"Field '{name}' has invalid value '{value}'. Allowed: {schema['enum']}",
            file="",
            line=0,
        ))
    
    # Pattern validation
    if "pattern" in schema and isinstance(value, str):
        if not re.match(schema["pattern"], value):
            violations.append(Violation(
                severity="ERROR",
                code="PATTERN_MISMATCH",
                message=f"Field '{name}' value '{value}' doesn't match pattern {schema['pattern']}",
                file="",
                line=0,
            ))
    
    return violations


def validate_rule_file(file_path: Path, schema: dict[str, Any]) -> list[Violation]:
    """Validate a single rule file."""
    violations: list[Violation] = []
    rel_path = f".windsurf/rules/{file_path.name}"
    
    try:
        content = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        return [Violation(
            severity="ERROR",
            code="FILE_READ_ERROR",
            message=f"Cannot read file: {e}",
            file=rel_path,
            line=0,
        )]
    
    # Skip files without frontmatter
    if not content.startswith("---"):
        violations.append(Violation(
            severity="WARNING",
            code="NO_FRONTMATTER",
            message="File lacks YAML frontmatter (does not start with ---)",
            file=rel_path,
            line=1,
        ))
        return violations
    
    # Extract frontmatter
    data, error = extract_frontmatter(content)
    if error:
        violations.append(Violation(
            severity="ERROR",
            code="FRONTMATTER_PARSE_ERROR",
            message=error,
            file=rel_path,
            line=1,
        ))
        return violations
    
    if data is None:
        return violations  # Empty frontmatter is valid
    
    # Validate against schema
    field_violations = validate_against_schema(data, schema)
    # Update file path in violations
    for v in field_violations:
        violations.append(Violation(
            severity=v.severity,
            code=v.code,
            message=v.message,
            file=rel_path,
            line=v.line,
        ))
    
    return violations


def evaluate() -> dict[str, Any]:
    """Run full validation. Returns report dict."""
    report: dict[str, Any] = {
        "checked_at": "",
        "schema_path": str(SCHEMA_PATH),
        "rules_dir": str(RULES_DIR),
        "valid": False,
        "files_checked": 0,
        "files_with_frontmatter": 0,
        "errors": [],
        "warnings": [],
    }
    
    # Load schema
    schema, error = load_schema()
    if schema is None:
        report["errors"].append({
            "code": "SCHEMA_LOAD_ERROR",
            "message": error,
            "file": str(SCHEMA_PATH),
        })
        return report
    
    # Find all rule files
    if not RULES_DIR.exists():
        report["errors"].append({
            "code": "RULES_DIR_NOT_FOUND",
            "message": f"Rules directory not found: {RULES_DIR}",
        })
        return report
    
    rule_files = list(RULES_DIR.glob("*.md"))
    report["files_checked"] = len(rule_files)
    
    all_violations: list[Violation] = []
    
    for rule_file in rule_files:
        violations = validate_rule_file(rule_file, schema)
        all_violations.extend(violations)
        
        # Count files with frontmatter
        if not any(v.code == "NO_FRONTMATTER" for v in violations):
            report["files_with_frontmatter"] += 1
    
    # Build report
    for v in all_violations:
        entry = {
            "severity": v.severity,
            "code": v.code,
            "message": v.message,
            "file": v.file,
            "line": v.line,
        }
        if v.severity == "ERROR":
            report["errors"].append(entry)
        else:
            report["warnings"].append(entry)
    
    report["valid"] = len(report["errors"]) == 0
    
    return report


def write_report(report: dict[str, Any]) -> None:
    """Write report to artifact path."""
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with ARTIFACT_PATH.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Rule Frontmatter Schema Validation")
    parser.add_argument("--fail-closed", action="store_true", help="Exit 1 on violations")
    parser.add_argument("--json", action="store_true", help="Output JSON to stdout")
    args = parser.parse_args(argv)

    # Bypass check
    if os.environ.get("RULE_FRONTMATTER_BYPASS") == "1":
        print("[check_rule_frontmatter_schema] BYPASS=1 — skipping", file=sys.stderr)
        return 0

    fail_closed = args.fail_closed or (os.environ.get("RULE_FRONTMATTER_FAIL_CLOSED") == "1")

    report = evaluate()
    write_report(report)

    error_count = len(report["errors"])
    warning_count = len(report["warnings"])

    if args.json:
        print(json.dumps(report, indent=2))
        return 0

    # Summary output
    print("=== Rule Frontmatter Schema Validation ===")
    print(f"Schema: {report['schema_path']}")
    print(f"Files checked: {report['files_checked']}")
    print(f"Files with frontmatter: {report['files_with_frontmatter']}")

    if report["errors"]:
        print(f"\n❌ ERRORS: {error_count}")
        for e in report["errors"]:
            print(f"  [{e['code']}] {e['file']}:{e['line']}")
            print(f"    {e['message']}")

    if report["warnings"]:
        print(f"\n⚠️  WARNINGS: {warning_count}")
        for w in report["warnings"]:
            print(f"  [{w['code']}] {w['file']}:{w['line']}")
            print(f"    {w['message']}")

    if not report["errors"] and not report["warnings"]:
        print("\n✅ All rule files have valid frontmatter")
    elif not report["errors"]:
        print("\n✅ Schema valid with warnings")

    if fail_closed and error_count > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

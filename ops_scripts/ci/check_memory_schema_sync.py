"""CI gate: Verify Memory MCP schema file matches Python constant.

Ensures SSOT discipline: canonical schema in .cursor/schemas/ must match
what sqlite_memory_store.py uses at runtime.

Gate ID: MEM-SYNC Memory MCP schema SSOT sync check
Location: ops_scripts/ci/check_memory_schema_sync.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


def _extract_embedded_schema(python_file: Path) -> str:
    """Extract the fallback embedded schema from sqlite_memory_store.py."""
    content = python_file.read_text(encoding="utf-8")
    
    # Find the return """...""" block in _load_schema function
    pattern = r'def _load_schema\(\)[^}]+return """(.*?)"""'
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        raise ValueError("Could not find embedded schema in _load_schema function")
    
    return match.group(1).strip()


def _normalize_sql(sql: str) -> str:
    """Normalize SQL for comparison (remove extra whitespace, lowercase)."""
    lines = []
    for line in sql.split("\n"):
        # Skip comments and empty lines
        line = line.strip()
        if not line or line.startswith("--"):
            continue
        lines.append(line.lower())
    # Join with single space and normalize multiple spaces
    normalized = " ".join(lines)
    while "  " in normalized:
        normalized = normalized.replace("  ", " ")
    return normalized.strip()


def _get_repo_root() -> Path:
    """Get repository root from CI gate location."""
    # This file is at: ops_scripts/ci/check_memory_schema_sync.py
    # Repo root is 3 levels up
    return Path(__file__).resolve().parents[2]


def check_memory_schema_sync() -> dict:
    """Check that Python embedded schema matches canonical schema file.
    
    Returns dict with:
        - status: "pass" | "fail"
        - schema_file: path to canonical schema
        - python_file: path to sqlite_memory_store.py
        - diff: description of any differences
    """
    repo_root = _get_repo_root()
    schema_file = repo_root / ".windsurf" / "schemas" / "knowledge_graph.schema.sql"
    python_file = repo_root / "tools" / "memory" / "sqlite_memory_store.py"
    
    if not schema_file.exists():
        return {
            "status": "fail",
            "schema_file": str(schema_file),
            "python_file": str(python_file),
            "diff": "Canonical schema file not found",
        }
    
    if not python_file.exists():
        return {
            "status": "fail",
            "schema_file": str(schema_file),
            "python_file": str(python_file),
            "diff": "Python file not found",
        }
    
    # Read canonical schema (without version table - that's added programmatically)
    canonical_schema = schema_file.read_text(encoding="utf-8")
    
    # Extract embedded schema from Python file
    try:
        embedded_schema = _extract_embedded_schema(python_file)
    except ValueError as e:
        return {
            "status": "fail",
            "schema_file": str(schema_file),
            "python_file": str(python_file),
            "diff": f"Failed to extract embedded schema: {e}",
        }
    
    # Compare core schema (excluding _schema_version table which is added programmatically)
    # The embedded schema is a fallback - compare without _schema_version in both
    canonical_normalized = _normalize_sql(canonical_schema)
    embedded_normalized = _normalize_sql(embedded_schema)
    
    # Remove _schema_version table and trailing content from both for comparison
    def _strip_version_table(sql: str) -> str:
        """Remove _schema_version table and INSERT from SQL."""
        # Remove INSERT first (comes after table definition)
        if "insert or ignore into _schema_version" in sql:
            sql = sql.split("insert or ignore into _schema_version")[0].strip()
        # Remove CREATE TABLE
        if "create table if not exists _schema_version" in sql:
            sql = sql.split("create table if not exists _schema_version")[0].strip()
        return sql
    
    canonical_core = _strip_version_table(canonical_normalized)
    embedded_core = _strip_version_table(embedded_normalized)
    
    if canonical_core == embedded_core:
        return {
            "status": "pass",
            "schema_file": str(schema_file),
            "python_file": str(python_file),
            "diff": "Schemas match",
        }
    
    # Find first difference
    for i, (c, e) in enumerate(zip(canonical_core, embedded_core)):
        if c != e:
            context_start = max(0, i - 50)
            context_end = min(len(canonical_core), i + 50)
            return {
                "status": "fail",
                "schema_file": str(schema_file),
                "python_file": str(python_file),
                "diff": f"Mismatch at position {i}: canonical has '...{canonical_core[context_start:context_end]}...' vs embedded '...{embedded_core[context_start:context_end]}...'",
            }
    
    # Length mismatch
    if len(canonical_core) != len(embedded_core):
        if len(canonical_core) > len(embedded_core):
            extra = f"Extra in canonical: ...{canonical_core[len(embedded_core):]}..."
        else:
            extra = f"Extra in embedded: ...{embedded_core[len(canonical_core):]}..."
        return {
            "status": "fail",
            "schema_file": str(schema_file),
            "python_file": str(python_file),
            "diff": f"Length mismatch: canonical {len(canonical_core)} vs embedded {len(embedded_core)}. {extra}",
        }
    
    # Should not reach here if schemas don't match
    return {
        "status": "fail",
        "schema_file": str(schema_file),
        "python_file": str(python_file),
        "diff": "Unknown mismatch - schemas appear different but no specific difference found",
    }


def main() -> int:
    """CLI entry point."""
    result = check_memory_schema_sync()
    
    print(f"[{__file__}] Memory MCP Schema SSOT Check")
    print(f"  Schema file: {result['schema_file']}")
    print(f"  Python file: {result['python_file']}")
    print(f"  Status: {result['status'].upper()}")
    
    if result["status"] != "pass":
        print(f"  Diff: {result['diff']}")
        print("\nResolution: Update either the schema file or the embedded fallback to match.")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

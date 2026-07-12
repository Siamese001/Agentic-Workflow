"""Fail CI when canonical ADG SQLite writer/schema authority forks."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "agentic_core/adg/artifact/sqlite_schema.py"
CANONICAL_WRITER = ROOT / "agentic_core/adg/artifact/ArtifactPaths.py"
LEGACY_ADAPTER = ROOT / "agentic_core/adg/artifact/multi_writer.py"


def validate_writer_authority() -> list[str]:
    """Return deterministic authority-contract errors."""
    errors: list[str] = []
    schema_text = SCHEMA.read_text(encoding="utf-8")
    canonical_text = CANONICAL_WRITER.read_text(encoding="utf-8")
    legacy_text = LEGACY_ADAPTER.read_text(encoding="utf-8")

    if schema_text.count("CREATE TABLE IF NOT EXISTS nodes") != 1:
        errors.append("sqlite_schema.py must define the canonical nodes DDL once")
    if "CREATE TABLE IF NOT EXISTS nodes" in canonical_text:
        errors.append("ArtifactPaths.py must import DDL, not define it")
    if "CREATE TABLE IF NOT EXISTS nodes" in legacy_text:
        errors.append("multi_writer.py must not define SQLite DDL")
    if "from agentic_core.adg.artifact.sqlite_schema import DDL, DDL_SHA256" not in canonical_text:
        errors.append("ArtifactPaths.py is not bound to canonical DDL provenance")
    if "from agentic_core.adg.artifact.sqlite_schema import DDL as _DDL" not in legacy_text:
        errors.append("multi_writer._DDL must remain a canonical compatibility alias")
    if "sqlite3.connect(" in legacy_text:
        errors.append("multi_writer.py must not open a second canonical writer connection")
    if "_canonical_write_sqlite" not in legacy_text:
        errors.append("multi_writer._write_sqlite must delegate to the canonical writer")
    if canonical_text.count("sqlite3.connect(") != 1:
        errors.append("ArtifactPaths.py must contain exactly one canonical SQLite connection")
    if '("ddl_sha256", DDL_SHA256)' not in canonical_text:
        errors.append("canonical metadata must persist the DDL digest")
    if '"writer_authority"' not in canonical_text:
        errors.append("canonical metadata must identify the writer authority")
    return errors


def main() -> int:
    errors = validate_writer_authority()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("ADG SQLite writer authority: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

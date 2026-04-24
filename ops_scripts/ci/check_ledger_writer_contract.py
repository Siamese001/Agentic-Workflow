"""check_ledger_writer_contract.py — CI gate for the intelligence-ledger rollout.

Validates:
    1. Every ledger in LEDGER_REGISTRY has its schema file on disk.
    2. Every ledger in LEDGER_REGISTRY has its consulting skill on disk.
    3. Every ledger has a DB under artifacts/ledgers/ with expected base tables
       (or can be created idempotently via apply_schema --check).
    4. No drift between the registered writer_hook path and actual existence on disk.

Exit codes:
    0 = all contracts pass
    1 = contract violations detected (details printed)
    2 = internal error (e.g., schema apply --check failed)

Usage:
    python ops_scripts/ci/check_ledger_writer_contract.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

# Allow running as a plain script: ensure repo root is importable
_REPO_ROOT_BOOTSTRAP = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT_BOOTSTRAP) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT_BOOTSTRAP))

from tools.ledgers.schema_registry import LEDGER_REGISTRY, REPO_ROOT

EXPECTED_TABLES = {"events", "event_scope", "events_fts", "schema_version"}


def _check_schema_file_exists(spec) -> str | None:
    if not spec.schema_path.exists():
        return f"missing schema file: {spec.schema_path.relative_to(REPO_ROOT)}"
    return None


def _check_consulting_skill_exists(spec) -> str | None:
    skill_path = REPO_ROOT / spec.consulting_skill
    if not skill_path.exists():
        return f"missing consulting skill: {spec.consulting_skill}"
    return None


def _check_writer_hook_exists(spec) -> str | None:
    hook_path = REPO_ROOT / spec.writer_hook
    if not hook_path.exists():
        return (
            f"registered writer_hook not found on disk: {spec.writer_hook} (create a stub or update registry)"
        )
    return None


def _check_db_schema(spec) -> str | None:
    if not spec.db_path.exists():
        # Acceptable on fresh clone — apply_schema will create it
        return None
    import sqlite3

    try:
        conn = sqlite3.connect(str(spec.db_path), timeout=5)
        try:
            tables = {
                r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
            }
        finally:
            conn.close()
    except sqlite3.Error as exc:
        return f"sqlite error: {exc}"
    missing = EXPECTED_TABLES - tables
    if missing:
        return f"db missing base tables: {sorted(missing)}"
    return None


def _check_apply_schema_dry_run() -> str | None:
    try:
        result = subprocess.run(
            [sys.executable, "-m", "tools.ledgers.apply_schema", "--check"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(REPO_ROOT),
            shell=False,
            check=False,
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        return f"apply_schema --check failed to execute: {exc}"
    if result.returncode == 0:
        return None
    return f"apply_schema --check exit={result.returncode}\n{result.stdout}\n{result.stderr}"


def main() -> int:
    violations: list[str] = []

    for spec in LEDGER_REGISTRY:
        for check in (
            _check_schema_file_exists,
            _check_consulting_skill_exists,
            _check_writer_hook_exists,
            _check_db_schema,
        ):
            err = check(spec)
            if err:
                violations.append(f"[{spec.name}] {err}")

    drift = _check_apply_schema_dry_run()
    if drift:
        violations.append(f"[apply_schema] {drift}")

    if violations:
        print(f"[check_ledger_writer_contract] {len(violations)} violation(s):")
        for v in violations:
            print(f"  - {v}")
        return 1

    print(f"[check_ledger_writer_contract] OK: all {len(LEDGER_REGISTRY)} ledgers conform.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python
"""CI gate — validate emitted ExitDecision artifacts against the SSOT schema.

Policy: fail-open on a clean repo (no artifacts → exit 0). When at least one
artifact exists under ``artifacts/eval_spine/`` (or an override path), every
``*.json`` file in the tree must validate against
``config/schemas/exit_decision.schema.json``.

Usage (from repo root):
    python ops_scripts/ci/check_exit_decision_schema.py
    python ops_scripts/ci/check_exit_decision_schema.py --artifacts path/to/dir

Exit codes:
    0 — OK (no artifacts OR all artifacts valid)
    1 — at least one artifact failed schema validation
    2 — schema file missing (configuration error)

Mechanics: delegates to
``agentic_core.L5_safety.eval_spine.exit_decision.validate_dict`` so that
the same validator used at runtime is used in CI.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ARTIFACTS = REPO_ROOT / "artifacts" / "eval_spine"
SCHEMA_PATH = REPO_ROOT / "config" / "schemas" / "exit_decision.schema.json"


def _emit(ok: bool, message: str) -> None:
    prefix = "OK   " if ok else "FAIL "
    print(f"{prefix}{message}")


def validate_artifacts(artifacts_dir: Path, schema_path: Path) -> int:
    """Return an exit code after validating every JSON under ``artifacts_dir``."""
    if not schema_path.exists():
        print(f"FAIL schema missing: {schema_path}", file=sys.stderr)
        return 2

    # Add repo root to sys.path so we can import agentic_core.* when run
    # directly.
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    from agentic_core.L5_safety.eval_spine.exit_decision import (  # noqa: WPS433
        validate_dict,
    )

    if not artifacts_dir.exists():
        _emit(True, f"no artifacts directory at {artifacts_dir}; skipping (fail-open)")
        return 0

    json_files = sorted(artifacts_dir.rglob("*.json"))
    if not json_files:
        _emit(True, f"no *.json under {artifacts_dir}; skipping (fail-open)")
        return 0

    failures = 0
    for path in json_files:
        try:
            with path.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            failures += 1
            _emit(False, f"{path}: read/parse error: {exc}")
            continue
        errors = validate_dict(payload, schema_path=schema_path)
        if errors:
            failures += 1
            _emit(False, f"{path}: {len(errors)} schema errors")
            for error in errors[:5]:
                print(f"        - {error}")
            if len(errors) > 5:
                print(f"        ... and {len(errors) - 5} more")
        else:
            _emit(True, f"{path}")

    if failures:
        print(f"\n{failures} of {len(json_files)} artifacts failed validation.")
        return 1
    print(f"\n{len(json_files)} ExitDecision artifacts validated.")
    return 0


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--artifacts",
        type=Path,
        default=DEFAULT_ARTIFACTS,
        help="Directory to scan for ExitDecision JSON artifacts.",
    )
    parser.add_argument(
        "--schema",
        type=Path,
        default=SCHEMA_PATH,
        help="Path to the ExitDecision JSON Schema.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    return validate_artifacts(args.artifacts, args.schema)


if __name__ == "__main__":
    raise SystemExit(main())

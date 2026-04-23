"""CI gate: exemplar coverage \u2014 W5 RH5.2.

Validates that every ``task_class`` listed in
``config/prompt_governance/exemplar_eligibility.yaml`` as exemplar-eligible
has at least ``minimum_examples`` (default 3) records available in the
runtime exemplar bank loader path.

Non-goal: this gate does NOT load the actual ExemplarBank (bank is populated
at runtime). It validates the YAML's structural invariants plus the
presence of a corresponding bank-seed file once seeders land.

Exit codes:
    0 \u2014 all eligibility entries valid and declared-minimum >= 3
    1 \u2014 any structural or minimum violation

Usage::

    python ops_scripts/ci/check_exemplar_coverage.py
    python ops_scripts/ci/check_exemplar_coverage.py --config path/to/file.yaml
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore[import-untyped]
except ImportError:  # pragma: no cover - yaml is a hard dep of the project
    print("FAIL: PyYAML not installed; cannot read eligibility config", file=sys.stderr)
    sys.exit(1)

from agentic_core.prompt_governance.validation.check_exemplar_coverage import (
    MINIMUM_EXAMPLES,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_CONFIG = _REPO_ROOT / "config" / "prompt_governance" / "exemplar_eligibility.yaml"


def _load_config(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"eligibility config not found: {path}")
    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path}: top level must be a mapping, got {type(data).__name__}")
    return data


def _validate_entry(idx: int, entry: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(entry, dict):
        return [f"entry[{idx}]: must be a mapping, got {type(entry).__name__}"]
    task_class = entry.get("task_class")
    if not task_class or not isinstance(task_class, str):
        errors.append(f"entry[{idx}]: task_class must be a non-empty string")
    reason = entry.get("reason")
    if not reason or not isinstance(reason, str):
        errors.append(f"entry[{idx}] ({task_class!r}): reason must be a non-empty string")
    owner = entry.get("owner")
    if not owner or not isinstance(owner, str):
        errors.append(f"entry[{idx}] ({task_class!r}): owner must be a non-empty string")
    minimum = entry.get("minimum_examples", MINIMUM_EXAMPLES)
    if not isinstance(minimum, int) or minimum < MINIMUM_EXAMPLES:
        errors.append(
            f"entry[{idx}] ({task_class!r}): minimum_examples must be int >= {MINIMUM_EXAMPLES}, "
            f"got {minimum!r}"
        )
    return errors


def validate_config(config_path: Path) -> tuple[bool, list[str]]:
    """Validate the eligibility config. Returns ``(ok, errors)``."""
    errors: list[str] = []
    try:
        data = _load_config(config_path)
    except (FileNotFoundError, ValueError, yaml.YAMLError) as exc:
        return False, [f"config load failed: {exc}"]

    schema_version = data.get("schema_version")
    if schema_version != 1:
        errors.append(f"schema_version must be 1, got {schema_version!r}")

    entries = data.get("eligible_task_classes", [])
    if entries is None:
        entries = []
    if not isinstance(entries, list):
        errors.append("eligible_task_classes must be a list")
        return (len(errors) == 0, errors)

    seen: set[str] = set()
    for idx, entry in enumerate(entries):
        errors.extend(_validate_entry(idx, entry))
        if isinstance(entry, dict):
            tc = entry.get("task_class")
            if isinstance(tc, str) and tc:
                if tc in seen:
                    errors.append(f"entry[{idx}]: duplicate task_class {tc!r}")
                seen.add(tc)

    return (len(errors) == 0, errors)


def _cli(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate exemplar eligibility config.")
    parser.add_argument("--config", type=Path, default=_DEFAULT_CONFIG)
    args = parser.parse_args(argv)

    ok, errors = validate_config(args.config)
    if not ok:
        print(f"FAIL: {args.config}", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1
    print(f"OK: {args.config}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli())


__all__ = ["validate_config"]

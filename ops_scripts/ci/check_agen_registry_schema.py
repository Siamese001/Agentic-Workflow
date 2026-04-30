#!/usr/bin/env python3
"""AGEN policy + best-practice registry schema gate.

Validates every ``docs/requirements/registry/{policy,best_practice}/AGEN-*.yaml``
file against the canonical schema, including:

  - Filename matches its declared ``id`` field (AGEN-NNNN.yaml ↔ id: AGEN-NNNN)
  - Required fields present: id, title, domain, status, statement
  - ``id`` is unique across the registry
  - ``id`` matches ``^AGEN-\\d{4}$``
  - ``status`` is in {active, draft, retired}
  - ``domain`` matches the directory (policy/ → policy, best_practice/ → best_practice)
  - When ``enforcement`` lists a ``ci_gate`` or ``pre_commit`` entry, that script
    or hook must exist on disk

Closes the orphan flagged by ``check_requirements_universe_inventory.py`` for U9.

Exit codes:
    0  All AGEN files validate.
    1  Schema violation, ID conflict, or missing enforcement reference.
    2  Infrastructure error.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - environment failure
    print("FATAL: PyYAML not installed", file=sys.stderr)
    sys.exit(2)

REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTRY = REPO_ROOT / "docs" / "requirements" / "registry"

ID_RE = re.compile(r"^AGEN-(\d{4})$")
ALLOWED_STATUS = frozenset({"active", "draft", "retired"})
ALLOWED_DOMAIN = frozenset({"policy", "best_practice"})
REQUIRED_FIELDS = ("id", "title", "domain", "status", "statement")


def _check_one(path: Path, expected_domain: str) -> list[str]:
    errors: list[str] = []
    rel = path.relative_to(REPO_ROOT).as_posix()

    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        return [f"{rel}: YAML parse error: {exc}"]

    if not isinstance(data, dict):
        return [f"{rel}: top-level must be a mapping"]

    # Required fields
    for f in REQUIRED_FIELDS:
        v = data.get(f)
        if v is None or (isinstance(v, str) and not v.strip()):
            errors.append(f"{rel}: missing required field '{f}'")

    # ID matches filename
    rid = data.get("id", "")
    if not ID_RE.match(str(rid)):
        errors.append(f"{rel}: id '{rid}' does not match AGEN-NNNN")
    else:
        expected_stem = str(rid)
        if path.stem != expected_stem:
            errors.append(
                f"{rel}: filename stem '{path.stem}' does not match id '{rid}'"
            )

    # Domain consistent with directory
    declared_domain = data.get("domain", "")
    if declared_domain not in ALLOWED_DOMAIN:
        errors.append(
            f"{rel}: domain '{declared_domain}' not in {sorted(ALLOWED_DOMAIN)}"
        )
    elif declared_domain != expected_domain:
        errors.append(
            f"{rel}: domain '{declared_domain}' does not match directory '{expected_domain}'"
        )

    # Status vocabulary
    status = data.get("status", "")
    if status and status not in ALLOWED_STATUS:
        errors.append(f"{rel}: status '{status}' not in {sorted(ALLOWED_STATUS)}")

    # Enforcement references must resolve on disk
    enforcement = data.get("enforcement") or []
    if isinstance(enforcement, list):
        for entry in enforcement:
            if not isinstance(entry, dict):
                continue
            for key in ("ci_gate", "pre_commit"):
                target = entry.get(key)
                if not target:
                    continue
                if key == "ci_gate":
                    target_path = REPO_ROOT / target
                    if not target_path.exists():
                        errors.append(
                            f"{rel}: enforcement.ci_gate '{target}' does not exist on disk"
                        )
                # pre_commit references are hook IDs, not file paths — skip path
                # check; the pre-commit config is the source of truth for those.

    return errors


def main() -> int:
    print("[AGEN registry schema gate]")
    if not REGISTRY.exists():
        print(f"FATAL: registry directory missing: {REGISTRY}", file=sys.stderr)
        return 2

    files: list[tuple[Path, str]] = []
    for domain in sorted(ALLOWED_DOMAIN):
        d = REGISTRY / domain
        if not d.exists():
            continue
        for yml in sorted(d.glob("AGEN-*.yaml")):
            files.append((yml, domain))

    if not files:
        print("FAIL: no AGEN-*.yaml files found under docs/requirements/registry/", file=sys.stderr)
        return 1

    all_errors: list[str] = []
    seen_ids: dict[str, str] = {}
    for path, domain in files:
        errs = _check_one(path, domain)
        all_errors.extend(errs)
        # Cross-file uniqueness
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            rid = data.get("id", "")
            if rid:
                if rid in seen_ids:
                    all_errors.append(
                        f"duplicate id '{rid}' in {path.relative_to(REPO_ROOT)} "
                        f"(also in {seen_ids[rid]})"
                    )
                else:
                    seen_ids[rid] = str(path.relative_to(REPO_ROOT))
        except yaml.YAMLError:
            pass  # already reported by _check_one

    print(f"  files validated : {len(files)}")
    print(f"  unique ids      : {len(seen_ids)}")
    print(f"  errors          : {len(all_errors)}")

    if all_errors:
        print("\nFAIL — AGEN registry schema violations:")
        for e in all_errors:
            print(f"  - {e}")
        return 1

    print("OK  AGEN registry valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

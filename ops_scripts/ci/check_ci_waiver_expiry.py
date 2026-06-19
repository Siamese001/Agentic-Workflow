#!/usr/bin/env python3
"""Audit expiry of CI waivers in `config/ci_waivers.yaml`."""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - CI installs PyYAML via python-setup.
    yaml = None

YAML_ERROR = getattr(yaml, "YAMLError", RuntimeError)

REPO_ROOT = Path(__file__).resolve().parents[2]
WAIVER_FILE = REPO_ROOT / "config" / "ci_waivers.yaml"
REQUIRED_FIELDS = ("workflow", "lane", "reason", "owner", "expires_on")


def _load_waivers() -> list[dict]:
    if yaml is None:
        raise RuntimeError("pyyaml is required to audit CI waivers")
    if not WAIVER_FILE.exists():
        return []
    data = yaml.safe_load(WAIVER_FILE.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise RuntimeError(f"{WAIVER_FILE} must contain a YAML mapping")
    waivers = data.get("waivers", [])
    if not isinstance(waivers, list):
        raise RuntimeError("config.ci_waivers.yaml waivers must be a list")
    return waivers


def main(argv: list[str] | None = None) -> int:
    _ = argv
    try:
        waivers = _load_waivers()
    except (OSError, RuntimeError, YAML_ERROR) as exc:
        print(f"CI waiver expiry audit failed: {exc}", file=sys.stderr)
        return 2

    today = datetime.now(timezone.utc).date()
    violations: list[str] = []
    for idx, waiver in enumerate(waivers):
        if not isinstance(waiver, dict):
            violations.append(f"waivers[{idx}] is not a mapping")
            continue
        missing = [field for field in REQUIRED_FIELDS if not waiver.get(field)]
        if missing:
            violations.append(f"{waiver.get('workflow', '?')}:{waiver.get('lane', '?')} missing {missing}")
            continue
        expires = str(waiver["expires_on"])
        try:
            exp_date = datetime.strptime(expires, "%Y-%m-%d").date()
        except ValueError:
            violations.append(
                f"{waiver['workflow']}:{waiver['lane']} expires_on={expires!r} is not YYYY-MM-DD"
            )
            continue
        if exp_date < today:
            violations.append(
                f"{waiver['workflow']}:{waiver['lane']} expired on {expires} "
                f"(owner={waiver.get('owner')})"
            )

    if violations:
        print("CI waiver expiry audit failed:")
        for line in violations:
            print(f"  - {line}")
        return 1

    print("CI waiver expiry audit passed: no expired waivers")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

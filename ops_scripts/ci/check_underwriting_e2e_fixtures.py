"""CI gate — apps_underwriting_ai E2E fixture validation.

D1.3 — E2E regression gate.
Plan: apps-underwriting-ai-deferred-scope-e8b2f4 D1.3.

Validates:
  1. All 4 demo fixture YAML files exist and parse cleanly.
  2. Each fixture declares the required keys for the E2E harness.
  3. demo_mode: true on every fixture.
  4. expected_x3_disposition is one of the 5 valid X3 classes.

Runs in < 2 seconds (no network, no LLM, no pytest invocation).

Exit codes:
  0 — all checks pass
  1 — one or more checks failed (printed to stdout)

Bypass: UNDERWRITING_E2E_FIXTURES_BYPASS=1
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_DIR = REPO_ROOT / "apps_underwriting_ai" / "fixtures"

_REQUIRED_FIXTURE_NAMES = [
    "demo_approve_packet.yaml",
    "demo_refer_packet.yaml",
    "demo_missing_evidence_packet.yaml",
    "demo_decline_packet.yaml",
]

_REQUIRED_KEYS = {
    "demo_packet_id",
    "demo_mode",
    "expected_x3_disposition",
    "demo_policy_hash",
    "blueprint_hash",
    "route_contract",
    "expected_verdict",
}

_VALID_X3 = {
    "X3A_APPROVE",
    "X3B_REFER",
    "X3C_DECLINE",
    "X3D_INSUFFICIENT",
    "X3E_SAFE_ABSTAIN",
}


def _load_yaml(path: Path) -> dict | None:
    try:
        import yaml  # noqa: PLC0415

        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else None
    except Exception as exc:  # noqa: BLE001
        # guardian: allow-broad-except -- CI gate must report parse errors, not crash
        print(f"  ERROR: failed to parse {path.name}: {exc}")
        return None


def run_checks() -> list[str]:
    errors: list[str] = []

    for fname in _REQUIRED_FIXTURE_NAMES:
        path = FIXTURE_DIR / fname
        if not path.exists():
            errors.append(f"MISSING_FIXTURE: {fname} not found at {path}")
            continue

        fixture = _load_yaml(path)
        if fixture is None:
            errors.append(f"PARSE_ERROR: {fname} failed to load as YAML mapping")
            continue

        missing_keys = _REQUIRED_KEYS - set(fixture.keys())
        if missing_keys:
            errors.append(
                f"MISSING_KEYS: {fname} missing {sorted(missing_keys)}"
            )

        if fixture.get("demo_mode") is not True:
            errors.append(f"DEMO_MODE_REQUIRED: {fname} must have demo_mode: true")

        x3 = fixture.get("expected_x3_disposition", "")
        if x3 not in _VALID_X3:
            errors.append(
                f"INVALID_X3: {fname} expected_x3_disposition={x3!r} "
                f"not in valid set {sorted(_VALID_X3)}"
            )

    return errors


def main() -> int:
    if os.environ.get("UNDERWRITING_E2E_FIXTURES_BYPASS") == "1":
        print("WARNING: UNDERWRITING_E2E_FIXTURES_BYPASS=1 — gate bypassed.")
        return 0

    print(f"[check_underwriting_e2e_fixtures] fixture_dir={FIXTURE_DIR}")
    errors = run_checks()

    if not errors:
        print(
            f"  OK: all {len(_REQUIRED_FIXTURE_NAMES)} fixture files valid."
        )
        return 0

    for err in errors:
        print(f"  {err}")
    print(f"\n  FAIL: {len(errors)} error(s) found.")
    return 1


if __name__ == "__main__":
    sys.exit(main())

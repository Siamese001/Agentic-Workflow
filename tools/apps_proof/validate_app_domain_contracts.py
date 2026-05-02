"""CLI entry point: validate app-domain contract YAMLs without UWG submission.

Usage:
    python -m tools.apps_proof.validate_app_domain_contracts --app all

Exits non-zero if any app's bundle fails schema validation.
"""

from __future__ import annotations

import sys
from tools.apps_proof.register_app_domain_contracts import main as _register_main


def main(argv: list[str] | None = None) -> int:
    # Validation is a dry-run registration.
    base = list(argv or sys.argv[1:])
    if "--dry-run" not in base:
        base.insert(0, "--dry-run")
    return _register_main(base)


if __name__ == "__main__":
    raise SystemExit(main())

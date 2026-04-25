"""W6.2b+c runner: apply prefix codemod for non-artifacts/adg literals."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

LOG = Path("artifacts/_w6_2bc_runner.log")
LOG.parent.mkdir(parents=True, exist_ok=True)


def run(literal: str, label: str) -> int:
    LOG.open("a", encoding="utf-8").write(f"\n=== {label} literal={literal} ===\n")
    sys.argv = ["ssot_prefix_path_migrator", "--apply", "--only-literal", literal]
    spec = importlib.util.spec_from_file_location(
        f"codemod_{label}",
        Path("tools/migration/ssot_prefix_path_migrator.py"),
    )
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    rc = mod.main()
    LOG.open("a", encoding="utf-8").write(f"{label} returned {rc}\n")
    return int(rc) if isinstance(rc, int) else 1


def main() -> int:
    LOG.write_text("w6.2bc runner start\n", encoding="utf-8")
    literals = [
        ("docs/reports", "W6.2b-docs-reports"),
        ("docs/architecture/adr", "W6.2c-adr"),
        (".windsurf/plans", "W6.2c-plans"),
        (".windsurf/scripts", "W6.2c-scripts"),
        ("artifacts/windsurf", "W6.2c-windsurf"),
    ]
    max_rc = 0
    for lit, label in literals:
        rc = run(lit, label)
        max_rc = max(max_rc, rc)
    LOG.open("a", encoding="utf-8").write(f"\nfinal max_rc={max_rc}\n")
    return max_rc


if __name__ == "__main__":
    sys.exit(main())

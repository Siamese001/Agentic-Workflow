#!/usr/bin/env python3
"""W2: Move RootCustomsAgent orphan body to archives; keep thin shim only."""
from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SRC = REPO / "agentic_core/L0_routing/reasoning/RootCustomsAgent.py"
ARCHIVE_DIR = REPO / "archives/agents/2026-05-25"
ARCHIVE = ARCHIVE_DIR / "agentic_core__L0_routing__reasoning__RootCustomsAgent_legacy_orphan_body.py"


def main() -> int:
    text = SRC.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    if len(lines) < 164:
        print(f"Already truncated ({len(lines)} lines)")
        return 0
    legacy = "".join(lines[163:])
    header = (
        '"""ARCHIVED orphan body removed from RootCustomsAgent.py '
        "(W2 agent-inventory-spine-taxonomy-b4e9f2).\n\n"
        "Accidentally concatenated after the thin delegating shim; re-defined "
        "RootCustomsAgent at import time. Canonical runtime: root_customs_util.\n"
        '"""\n\n'
    )
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    ARCHIVE.write_text(header + legacy, encoding="utf-8")
    thin = "".join(lines[:163])
    if not thin.endswith("\n"):
        thin += "\n"
    thin = thin.replace(
        "Archive-eligible date: 2026-07-23",
        "W2 archive (2026-05-25): legacy orphan body in archives/agents/2026-05-25/",
    )
    SRC.write_text(thin, encoding="utf-8")
    print(f"Wrote {ARCHIVE.relative_to(REPO)} ({len(legacy.splitlines())} lines)")
    print(f"Truncated {SRC.relative_to(REPO)} ({len(thin.splitlines())} lines)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

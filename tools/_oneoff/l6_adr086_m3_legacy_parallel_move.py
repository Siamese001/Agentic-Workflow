"""ADR-086 M3: move utils/evaluation implementations to shadow_eval/legacy_parallel/."""
from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SRC_DIR = REPO / "agentic_core/L6_observability/utils/evaluation"
DST_DIR = REPO / "agentic_core/L6_observability/shadow_eval/legacy_parallel"
SKIP = frozenset({"async_eval_packet.py", "governed_handoff.py"})

IMPORT_OLD = "agentic_core.L6_observability.utils.evaluation"
IMPORT_NEW = "agentic_core.L6_observability.shadow_eval.legacy_parallel"

SHIM_TEMPLATE = '''"""90-day compat shim (ADR-086 M3). Canonical: ``{canonical}``."""
from {canonical} import *  # noqa: F403
'''


def _rewrite_imports(text: str) -> str:
    return text.replace(IMPORT_OLD, IMPORT_NEW)


def main() -> None:
    DST_DIR.mkdir(parents=True, exist_ok=True)
    init = DST_DIR / "__init__.py"
    if not init.exists():
        init.write_text(
            '"""Legacy parallel B-surface (pre-M3 utils/evaluation). 90-day compat via utils/evaluation shims."""\n\n'
            '__l6_chapter__ = "06.x-legacy"\n',
            encoding="utf-8",
        )

    moved: list[str] = []
    for src in sorted(SRC_DIR.glob("*.py")):
        if src.name in SKIP:
            continue
        body = _rewrite_imports(src.read_text(encoding="utf-8"))
        dst = DST_DIR / src.name
        dst.write_text(body, encoding="utf-8")
        canonical = f"agentic_core.L6_observability.shadow_eval.legacy_parallel.{src.stem}"
        src.write_text(SHIM_TEMPLATE.format(canonical=canonical), encoding="utf-8")
        moved.append(src.name)

    readme = DST_DIR / "README.md"
    readme.write_text(
        "# legacy_parallel (ADR-086 M3)\n\n"
        "Implementations relocated from `utils/evaluation/`. "
        "Import via `shadow_eval.legacy_parallel.*` or 90-day shims at old paths.\n",
        encoding="utf-8",
    )
    print(f"M3 moved {len(moved)} modules -> {DST_DIR.relative_to(REPO)}")
    for name in moved:
        print(f"  {name}")


if __name__ == "__main__":
    main()

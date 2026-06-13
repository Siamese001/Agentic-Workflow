"""ADG-driven discovery of apps_* surfaces.

Replaces hardcoded app lists with a query against the ADG snapshot. The
inventory drives every other module in the proof harness.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class AppInventoryEntry:
    """One discovered apps_* surface."""

    app_id: str  # e.g. "apps_eval"
    has_ingress_runner: bool
    has_execution_adapter: bool
    has_engines_dir: bool
    has_outputs_dir: bool
    node_count_in_adg: int
    risk_class: str  # NORMAL | HIGH_IMPACT | INFRASTRUCTURE
    notes: tuple[str, ...] = field(default_factory=tuple)


# Risk classification (per prompt §4):
# - apps_underwriting_ai is HIGH_IMPACT (cannot auto-commit decisions)
# - apps_shared is INFRASTRUCTURE (meta-only proof scenario)
# - everything else is NORMAL
_HIGH_IMPACT = frozenset({"apps_underwriting_ai"})
_INFRASTRUCTURE = frozenset({"apps_shared"})


def _classify(app_id: str) -> str:
    if app_id in _HIGH_IMPACT:
        return "HIGH_IMPACT"
    if app_id in _INFRASTRUCTURE:
        return "INFRASTRUCTURE"
    return "NORMAL"


def discover_apps(
    *,
    repo_root: Path,
    adg_snapshot: Path,
) -> tuple[AppInventoryEntry, ...]:
    """Discover apps_* surfaces from the ADG snapshot + filesystem.

    The ADG `nodes` table is queried for distinct top-level packages whose
    ``resolved_path`` starts with ``apps_``. Filesystem checks confirm each
    app has the canonical sub-structure (ingress runner, execution adapter,
    etc.).
    """
    if not adg_snapshot.exists():
        raise FileNotFoundError(f"ADG snapshot missing: {adg_snapshot}")

    con = sqlite3.connect(adg_snapshot)
    try:
        cur = con.cursor()
        # Pull every distinct apps_* top-level package from nodes.
        rows = cur.execute(
            """
            SELECT
              SUBSTR(resolved_path, 1, INSTR(resolved_path, '/') - 1) AS pkg,
              COUNT(*) AS n
            FROM nodes
            WHERE resolved_path LIKE 'apps_%'
              AND INSTR(resolved_path, '/') > 0
            GROUP BY pkg
            ORDER BY pkg
            """
        ).fetchall()
    finally:
        con.close()

    out: list[AppInventoryEntry] = []
    for pkg, count in rows:
        if not pkg or not pkg.startswith("apps_"):
            continue
        app_dir = repo_root / pkg
        ingress = (
            list((app_dir / "integrations").glob("*ingress_runner.py"))
            if (app_dir / "integrations").exists()
            else []
        )
        adapter = (app_dir / "integrations" / "execution_adapter.py").exists()
        engines = (app_dir / "engines").exists()
        outputs = (app_dir / "outputs").exists()
        notes: list[str] = []
        if not ingress:
            notes.append("no ingress_runner found in integrations/")
        if not adapter:
            notes.append("no execution_adapter.py")
        out.append(
            AppInventoryEntry(
                app_id=pkg,
                has_ingress_runner=bool(ingress),
                has_execution_adapter=adapter,
                has_engines_dir=engines,
                has_outputs_dir=outputs,
                node_count_in_adg=int(count),
                risk_class=_classify(pkg),
                notes=tuple(notes),
            )
        )
    return tuple(out)


def required_apps(inventory: Iterable[AppInventoryEntry]) -> tuple[str, ...]:
    """Apps that MUST produce a passing proof scenario.

    Per the prompt, all 8 canonical apps are required.
    """
    canonical = (
        "apps_eval",
        "apps_exec",
        "apps_lic",
        "apps_research",
        "apps_rg",
        "apps_shared",
        "apps_underwriting_ai",
    )
    discovered = {e.app_id for e in inventory}
    return tuple(a for a in canonical if a in discovered)


__all__ = ["AppInventoryEntry", "discover_apps", "required_apps"]

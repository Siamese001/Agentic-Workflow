#!/usr/bin/env python3
"""Gate G-CALL-MULTIPLICITY — duplicate top-level call detector.

Walks the production source tree and flags ``(source_file, fully_qualified_call_target)``
pairs that appear more than ``THRESHOLD`` times at MODULE TOP LEVEL (not inside
function bodies). The classic offender is auto-instrumentation pollution where
a generator wave injects 80+ identical ``_emit_*("p1", "module_name", "tag")``
calls into module-load code, creating telemetry noise that's invisible to
existing gates.

Configurable via env:
    CALL_MULTIPLICITY_THRESHOLD=<int>  (default: 5)
    CALL_MULTIPLICITY_BYPASS=1         (skip gate entirely)

Tier: R (ratchet). On a fresh repo this MAY have a baseline; the gate is fail-
closed only when count > baseline. Baseline ratchet is stored at
``ops_scripts/ci/baselines/call_multiplicity_ratchet.json``.

Origin: RCA on 2026-04-28 ``full_agent_discovery`` / ``safety_kernel_seam``
auto-instrumentation pollution that escaped every existing gate. Pylint flags
re-imports as warnings but never gates them; no existing gate examines call-
edge multiplicity. See ``docs/reports/plans/`` for the full RCA.
"""

from __future__ import annotations

# W4 ADG consumer mode declaration (per .windsurf/rules/adg-canonical-invariants.md
# §6 + agentic_core/adg/artifact/consumer_mode.py).
# Counts top-level call duplication — sizing/inventory analysis, not a verdict.
__adg_consumer_mode__ = "inventory"

import ast
import json
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

PRODUCTION_PACKAGE_ROOTS = (
    "agentic_core",
    "apps_eval",
    "apps_exec",
    "apps_lic",
    "apps_research",
    "apps_rfp",
    "apps_rg",
    "apps_shared",
    "apps_underwriting_ai",
    "system_learning",
    "ops_scripts",
    "tools",
    "infrastructure",
    "scripts",
)

DEFAULT_THRESHOLD = 5

LOG_DIR = REPO_ROOT / "artifacts" / "windsurf"
LOG_FILE = LOG_DIR / "call_multiplicity_violations.jsonl"
BASELINE_DIR = REPO_ROOT / "ops_scripts" / "ci" / "baselines"
BASELINE_FILE = BASELINE_DIR / "call_multiplicity_ratchet.json"


@dataclass
class CallHotspot:
    source_file: str
    call_target: str
    occurrences: int
    first_line: int
    last_line: int


@dataclass
class GateOutcome:
    hotspots: list[CallHotspot] = field(default_factory=list)
    files_scanned: int = 0
    threshold: int = DEFAULT_THRESHOLD
    baseline: int | None = None
    bypassed: bool = False
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


def _attr_path(node: ast.expr) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = _attr_path(node.value)
        if base is None:
            return None
        return f"{base}.{node.attr}"
    return None


def _scan_file_top_level_calls(path: Path) -> dict[str, list[int]]:
    """Return {call_target_dotted_path: [linenos...]} for calls that appear at
    MODULE TOP LEVEL (i.e., as direct children of the Module body or inside
    ``if __name__ == "__main__":`` guards). Calls inside function/class bodies
    are NOT counted because those execute per-call, not at module load."""
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source)
    except (SyntaxError, OSError, ValueError):
        return {}

    calls: dict[str, list[int]] = {}

    def _harvest_from_stmt_list(stmts: list[ast.stmt]) -> None:
        for stmt in stmts:
            # progress_bar: bounded recursion over a single file's top-level
            # statement list. Per-file cost is constant; outer file iterator
            # in run_gate carries the multi-file progress bar.
            # Direct expression-statement top-level calls.
            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                target = _attr_path(stmt.value.func)
                if target:
                    calls.setdefault(target, []).append(stmt.value.lineno)
            # Recurse into top-level `if`/`try` blocks so `if __name__` etc are covered.
            if isinstance(stmt, (ast.If, ast.Try, ast.With)):
                bodies: list[list[ast.stmt]] = [stmt.body]
                if isinstance(stmt, ast.If):
                    bodies.append(stmt.orelse)
                if isinstance(stmt, ast.Try):
                    bodies.append(stmt.orelse)
                    bodies.append(stmt.finalbody)
                    for h in stmt.handlers:
                        bodies.append(h.body)
                for b in bodies:
                    _harvest_from_stmt_list(b)

    _harvest_from_stmt_list(tree.body)
    return calls


def _iter_python_files(repo_root: Path) -> Iterable[Path]:
    # progress_bar: this generator is consumed by run_gate which wraps it
    # with tqdm. The skip-set check below is constant-time per file.
    # Use the canonical exclusion SSOT — see check_hardcoded_exclusions.py.
    from agentic_core.L0_routing.config.path_constants import GLOBAL_EXCLUDED_DIRS

    skip_parts = set(GLOBAL_EXCLUDED_DIRS) | {"_archived_obsolete", "tools_graveyard"}
    for root_name in PRODUCTION_PACKAGE_ROOTS:
        root = repo_root / root_name
        if not root.is_dir():
            continue
        for path in root.rglob("*.py"):
            if any(skip in path.parts for skip in skip_parts):
                continue
            if any(p.startswith("archive") or "graveyard" in p for p in path.parts):
                continue
            yield path


def run_gate(repo_root: Path | None = None, threshold: int | None = None) -> GateOutcome:
    repo_root = repo_root or REPO_ROOT
    th = (
        threshold
        if threshold is not None
        else int(os.environ.get("CALL_MULTIPLICITY_THRESHOLD", DEFAULT_THRESHOLD))
    )
    outcome = GateOutcome(threshold=th)

    if os.environ.get("CALL_MULTIPLICITY_BYPASS", "").strip() == "1":
        outcome.bypassed = True
        return outcome

    from tqdm import tqdm  # noqa: PLC0415

    files = list(_iter_python_files(repo_root))
    outcome.files_scanned = len(files)

    for path in tqdm(files, desc="G-CALL-MULTIPLICITY", unit="file"):
        rel = str(path.relative_to(repo_root)).replace("\\", "/")
        per_file_calls = _scan_file_top_level_calls(path)
        for call_target, linenos in per_file_calls.items():
            # progress_bar: bounded — per-file dict iteration over distinct call targets.
            if len(linenos) > th:
                outcome.hotspots.append(
                    CallHotspot(
                        source_file=rel,
                        call_target=call_target,
                        occurrences=len(linenos),
                        first_line=min(linenos),
                        last_line=max(linenos),
                    )
                )

    # Sort by occurrence count desc for human readability.
    outcome.hotspots.sort(key=lambda h: (-h.occurrences, h.source_file))
    return outcome


def _load_baseline() -> int | None:
    if not BASELINE_FILE.exists():
        return None
    try:
        data = json.loads(BASELINE_FILE.read_text(encoding="utf-8"))
        return int(data.get("count", 0))
    except (json.JSONDecodeError, OSError, ValueError):
        return None


def _seed_baseline(count: int) -> None:
    BASELINE_DIR.mkdir(parents=True, exist_ok=True)
    BASELINE_FILE.write_text(
        json.dumps({"count": count, "seeded_at": datetime.now(timezone.utc).isoformat()}, indent=2),
        encoding="utf-8",
    )


def _emit_log(outcome: GateOutcome) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    record = {
        "gate": "G-CALL-MULTIPLICITY",
        "timestamp": outcome.timestamp,
        "threshold": outcome.threshold,
        "files_scanned": outcome.files_scanned,
        "hotspot_count": len(outcome.hotspots),
        "baseline": outcome.baseline,
        "bypassed": outcome.bypassed,
        "top_hotspots": [
            {
                "source_file": h.source_file,
                "call_target": h.call_target,
                "occurrences": h.occurrences,
                "first_line": h.first_line,
                "last_line": h.last_line,
            }
            for h in outcome.hotspots[:50]
        ],
    }
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


def main() -> int:
    if "--seed" in sys.argv:
        outcome = run_gate()
        _seed_baseline(len(outcome.hotspots))
        print(
            f"[G-CALL-MULTIPLICITY] baseline seeded at {len(outcome.hotspots)} "
            f"hotspots (threshold={outcome.threshold})"
        )
        return 0

    outcome = run_gate()
    outcome.baseline = _load_baseline()

    if outcome.bypassed:
        print("[G-CALL-MULTIPLICITY] BYPASSED via CALL_MULTIPLICITY_BYPASS=1")
        _emit_log(outcome)
        return 0

    current = len(outcome.hotspots)
    print(
        f"[G-CALL-MULTIPLICITY] scanned {outcome.files_scanned} files; "
        f"hotspots={current} (threshold={outcome.threshold}); "
        f"baseline={outcome.baseline if outcome.baseline is not None else 'unset (run with --seed)'}"
    )
    if outcome.hotspots:
        print("  Top hotspots (file → call → count):")
        for h in outcome.hotspots[:20]:
            print(
                f"    {h.source_file} → {h.call_target}  ×{h.occurrences} (lines {h.first_line}..{h.last_line})"
            )
        if len(outcome.hotspots) > 20:
            print(f"    ... ({len(outcome.hotspots) - 20} more)")
    _emit_log(outcome)

    if outcome.baseline is None:
        print("  baseline not set; gate is informational on first run")
        return 0
    if current > outcome.baseline:
        print(f"  FAIL: hotspots ({current}) > baseline ({outcome.baseline})")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

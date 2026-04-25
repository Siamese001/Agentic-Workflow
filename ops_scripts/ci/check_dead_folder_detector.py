#!/usr/bin/env python3
"""Gate D_dead_folder_detector — entire production subdirectories that are dead.

Rationale
    ``G_REACH_ARCHIVAL`` flags individual modules that are L0-unreachable.
    After the W1..W6 waves removed point-wise dead symbols / methods /
    modules, a coarser pattern emerged: whole subdirectories (e.g. old
    ``utils/``, retired interface packages, archived metric shims) where
    *every* non-__init__ module is orphaned. Archiving a dead folder in
    one move is far cheaper than N per-module archives and shrinks the
    ADG by the matching parent node + all children edges simultaneously.

How it works
    1. Ask G_REACH_ARCHIVAL for the set of archival orphans (modules that
       are L0-unreachable AND don't match any dynamic-dispatch anchor).
    2. Walk production-layer module nodes and group by parent directory.
    3. A directory is flagged when ALL of these hold:
         * total module count in dir >= MIN_FOLDER_SIZE (default 2)
         * every non-__init__ module in the dir is in the orphan set
         * no module in the dir matches a dynamic-dispatch anchor
    4. Emit one violation per dead folder, with the full orphan list in
       the violation detail so reviewers have archive evidence in-line.

Tier
    R (ratchet) with monotone auto-tighten + R→B auto-promotion via the
    W1 harness. Separate baseline from G_REACH_ARCHIVAL so directory-level
    reductions are tracked independently of per-file reductions.

SSOT for anchors: ``config/wiring_dynamic_dispatch_anchors.yaml``.
"""

from __future__ import annotations

import sqlite3
import sys
from collections import defaultdict
from pathlib import Path, PurePosixPath

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ops_scripts.ci._adg_wiring_gate_base import (  # noqa: E402
    Violation,
    WiringGate,
    cli_exit,
)
from ops_scripts.ci.check_graph_reach_archival import (  # noqa: E402
    find_archival_orphans,
    load_anchors,
    matches_anchor,
)


GATE_ID = "D_dead_folder_detector"
# Minimum production-module count inside a folder before it qualifies.
# Single-file folders often hold a CLI entry point or a standalone
# utility; flagging those duplicates G_REACH_ARCHIVAL with no benefit.
MIN_FOLDER_SIZE = 2
# Only consider these layers — matches check_graph_reach_archival.
_PRODUCTION_LAYERS = ("L1", "L2", "L3", "L4", "L5", "L_APP", "L_PG")
# Directory basenames we never flag as dead (they frequently hold dynamic
# dispatch targets the ADG doesn't see as imported).
_SKIP_DIR_BASENAMES = frozenset(
    {
        "tests",
        "test",
        "__pycache__",
        "migrations",
        "scripts",
        "hooks",
        "fixtures",
        "data",
    }
)


def _parent_dir(resolved_path: str) -> str:
    """Return the POSIX-normalized parent directory of a module path.

    Uses PurePosixPath so Windows back-slashes don't fragment grouping.
    """
    if not resolved_path:
        return ""
    return str(PurePosixPath(resolved_path.replace("\\", "/")).parent)


def _is_init_module(resolved_path: str) -> bool:
    if not resolved_path:
        return False
    return PurePosixPath(resolved_path.replace("\\", "/")).name == "__init__.py"


def _skip_directory(dir_path: str) -> bool:
    """Return True when the directory basename is in the skip list."""
    if not dir_path:
        return True
    base = PurePosixPath(dir_path).name
    return base in _SKIP_DIR_BASENAMES


def find_dead_folders(
    conn: sqlite3.Connection,
    anchor_patterns: list[str],
    min_folder_size: int = MIN_FOLDER_SIZE,
) -> list[tuple[str, list[str]]]:
    """Return [(folder_path, sorted orphan file list)] for each dead folder.

    A folder is "dead" when every non-__init__ production module inside it
    is an archival orphan AND the folder has at least ``min_folder_size``
    production modules AND no module inside matches a dynamic anchor.
    """
    orphan_records = find_archival_orphans(conn, anchor_patterns)
    orphan_paths = {rp for _, rp, _ in orphan_records if rp}

    # Group ALL production module resolved_paths by parent directory.
    by_dir: dict[str, list[str]] = defaultdict(list)
    layers_sql = ",".join(f"'{layer}'" for layer in _PRODUCTION_LAYERS)
    query = f"SELECT resolved_path FROM nodes WHERE entity_type='module' AND layer IN ({layers_sql})"
    for (resolved_path,) in conn.execute(query):
        if not resolved_path:
            continue
        by_dir[_parent_dir(resolved_path)].append(resolved_path)

    dead: list[tuple[str, list[str]]] = []
    for folder, modules in by_dir.items():
        if _skip_directory(folder):
            continue
        # Any module in this folder matching an anchor disqualifies the
        # whole folder — dynamic-dispatch entry points often live beside
        # helpers that look dead to the import graph.
        if any(matches_anchor(m, anchor_patterns) for m in modules):
            continue
        non_init = [m for m in modules if not _is_init_module(m)]
        if len(non_init) < min_folder_size:
            continue
        if not all(m in orphan_paths for m in non_init):
            continue
        dead.append((folder, sorted(non_init)))
    dead.sort(key=lambda t: t[0])
    return dead


class DeadFolderDetectorGate(WiringGate):
    gate_id = GATE_ID
    tier = "R"
    baseline_filename = "wiring_dead_folder_detector_ratchet.json"

    def run(self, conn: sqlite3.Connection) -> list[Violation]:
        anchors = load_anchors()
        dead = find_dead_folders(conn, anchors)
        violations: list[Violation] = []
        for folder, files in dead:
            preview = ", ".join(PurePosixPath(f).name for f in files[:5])
            if len(files) > 5:
                preview += f", ... (+{len(files) - 5} more)"
            violations.append(
                Violation(
                    gate_id=GATE_ID,
                    tier="R",
                    subject=folder,
                    rule="dead_folder",
                    detail=(
                        f"Production folder '{folder}' has {len(files)} "
                        "non-__init__ modules, all L0-unreachable and none "
                        f"matching a dynamic anchor. Files: {preview}. "
                        "Archive the whole folder in one move — shrinks ADG "
                        "by folder node + all import edges at once."
                    ),
                    extra={
                        "folder": folder,
                        "dead_file_count": len(files),
                        "dead_files": files,
                    },
                )
            )
        return violations


def main(argv: list[str] | None = None) -> int:  # noqa: ARG001
    result = DeadFolderDetectorGate().execute()
    return cli_exit(result)


if __name__ == "__main__":
    sys.exit(main())

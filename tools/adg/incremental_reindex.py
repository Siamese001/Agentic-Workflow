"""Incremental single-file ADG re-indexer (phase-1 of Wave W5).

Goal: when a single Python file changes on disk, patch its outgoing
``imports`` edges in a shadow copy of the current ADG snapshot — without
running the full pipeline. This gives Cascade (and runtime callers) a
"live" view of the graph for the file just edited, within seconds of
the edit.

Scope (phase-1 — intentionally narrow):
    - Updates ``nodes`` row for the file (insert or mtime-refresh).
    - Replaces all outgoing ``imports`` edges from this file's module node.
    - Targets only module-level nodes (``ADG::Module::<path>``). Does not
      rebuild symbol-level nodes, MVs, or any P-views. MVs/P-views stay
      on the full-snapshot cadence.
    - Safe: never mutates the canonical snapshot. Always writes to a
      shadow copy provided by the caller.

Non-goals (phase-2+ / deferred per the W5 DEFERRED_SCOPE marker):
    - Incremental MV refresh
    - Watcher daemon
    - Symbol-level edges (calls, flows_to, writes_to)
    - Redis hot-cache live projection

Usage::

    from tools.adg.incremental_reindex import IncrementalReindexer

    reindexer = IncrementalReindexer(
        source_snapshot=Path("artifacts/adg/adg_indexed_04242026_0721.sqlite"),
        shadow_snapshot=Path("artifacts/adg/shadow.sqlite"),
    )
    reindexer.initialize_shadow()
    delta = reindexer.reindex_file("tools/adg/runtime_query.py")
    print(delta.imports_added, delta.imports_removed)

    # Now use the shadow with the runtime query library:
    from tools.adg.runtime_query import RuntimeADGQuery
    q = RuntimeADGQuery(sqlite_path=reindexer.shadow_snapshot)
"""

from __future__ import annotations

import ast
import logging
import shutil
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)

ADG_MODULE_PREFIX = "ADG::Module::"


@dataclass
class ReindexDelta:
    """Summary of what changed for a single reindexed file."""

    file_path: str
    node_id: str | None = None
    created_node: bool = False
    imports_added: list[str] = field(default_factory=list)
    imports_removed: list[str] = field(default_factory=list)
    unresolved_imports: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "file_path": self.file_path,
            "node_id": self.node_id,
            "created_node": self.created_node,
            "imports_added": sorted(self.imports_added),
            "imports_removed": sorted(self.imports_removed),
            "unresolved_imports": sorted(self.unresolved_imports),
        }


class IncrementalReindexer:
    """Shadow-copy incremental reindexer (phase-1 scope).

    The reindexer never touches the source snapshot after
    ``initialize_shadow`` — all mutations land on the shadow copy. Callers
    can pass the shadow path to ``RuntimeADGQuery`` for live queries.
    """

    def __init__(
        self,
        source_snapshot: Path,
        shadow_snapshot: Path,
        *,
        repo_root: Path | None = None,
    ) -> None:
        if not source_snapshot.exists():
            raise FileNotFoundError(f"source snapshot missing: {source_snapshot}")
        self._source = source_snapshot
        self._shadow = shadow_snapshot
        self._repo_root = repo_root or Path(__file__).resolve().parents[2]

    @property
    def shadow_snapshot(self) -> Path:
        return self._shadow

    def initialize_shadow(self, *, overwrite: bool = True) -> None:
        """Copy the source snapshot to the shadow path."""
        if self._shadow.exists() and not overwrite:
            raise FileExistsError(f"shadow already exists: {self._shadow}")
        self._shadow.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(self._source, self._shadow)

    def reindex_file(self, file_path: str) -> ReindexDelta:
        """Patch the shadow snapshot with fresh imports for ``file_path``.

        ``file_path`` is repo-relative (forward-slash normalized). Returns a
        ``ReindexDelta`` summary. Never raises on unresolved imports — they
        land in ``unresolved_imports``.
        """
        norm = file_path.replace("\\", "/").lstrip("./")
        delta = ReindexDelta(file_path=norm)
        abs_path = self._repo_root / norm
        if not abs_path.exists() or abs_path.suffix != ".py":
            logger.debug("reindex_file: %s does not exist or is not .py", norm)
            return delta

        # Parse imports via AST — cheap and dependency-free.
        try:
            source = abs_path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(abs_path))
        except (OSError, SyntaxError, UnicodeDecodeError) as exc:
            logger.warning("reindex_file(%s) parse failed: %s", norm, exc)
            return delta

        import_modules = _extract_import_modules(tree)

        with sqlite3.connect(str(self._shadow), timeout=1.0) as conn:
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = OFF")

            # 1. Resolve or create the module node for this file.
            adg_name = ADG_MODULE_PREFIX + norm
            row = conn.execute(
                "SELECT id FROM nodes WHERE adg_name = ? OR resolved_path = ? LIMIT 1",
                (adg_name, norm),
            ).fetchone()
            if row is not None:
                node_id = str(row["id"])
            else:
                node_id = _mint_node_id(conn)
                layer = _infer_layer_for_path(norm)
                conn.execute(
                    "INSERT INTO nodes (id, adg_name, entity_type, layer, resolved_path) "
                    "VALUES (?, ?, 'module', ?, ?)",
                    (node_id, adg_name, layer, norm),
                )
                delta.created_node = True
            delta.node_id = node_id

            # 2. Capture current outgoing import edges to compute diff.
            existing_rows = conn.execute(
                "SELECT e.id AS edge_id, n.resolved_path AS tgt_path "
                "FROM edges e LEFT JOIN nodes n ON n.id = e.tgt_id "
                "WHERE e.src_id = ? AND e.relation_type = 'imports'",
                (node_id,),
            ).fetchall()
            existing_paths = {r["tgt_path"] for r in existing_rows if r["tgt_path"]}

            # 3. Resolve each AST-discovered import to an existing node.
            new_paths: set[str] = set()
            for mod in import_modules:
                tgt_id, tgt_path = _resolve_module_to_node(conn, mod)
                if tgt_id is None:
                    delta.unresolved_imports.append(mod)
                    continue
                if tgt_path:
                    new_paths.add(tgt_path)

            # 4. Compute add/remove sets.
            added = new_paths - existing_paths
            removed = existing_paths - new_paths
            delta.imports_added = sorted(added)
            delta.imports_removed = sorted(removed)

            # 5. Apply the delta.
            if removed:
                # Remove edges whose target path is in ``removed``.
                placeholders = ",".join("?" * len(removed))
                conn.execute(
                    f"DELETE FROM edges WHERE id IN ("
                    f"  SELECT e.id FROM edges e "
                    f"  LEFT JOIN nodes n ON n.id = e.tgt_id "
                    f"  WHERE e.src_id = ? AND e.relation_type = 'imports' "
                    f"    AND n.resolved_path IN ({placeholders})"
                    f")",
                    (node_id, *sorted(removed)),
                )
            for path in sorted(added):
                tgt_row = conn.execute(
                    "SELECT id FROM nodes WHERE resolved_path = ? LIMIT 1", (path,)
                ).fetchone()
                if tgt_row is None:
                    continue
                conn.execute(
                    "INSERT INTO edges (src_id, tgt_id, relation_type) VALUES (?, ?, 'imports')",
                    (node_id, str(tgt_row["id"])),
                )
            conn.commit()
        return delta


# ---------- AST helpers ----------


def _extract_import_modules(tree: ast.AST) -> list[str]:
    """Return a list of dotted module names imported by the file."""
    modules: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name:
                    modules.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.level == 0:
                modules.append(node.module)
    # Dedupe while preserving order.
    seen: set[str] = set()
    out: list[str] = []
    for m in modules:
        if m not in seen:
            seen.add(m)
            out.append(m)
    return out


def _resolve_module_to_node(conn: sqlite3.Connection, module_name: str) -> tuple[str | None, str | None]:
    """Given a dotted module name, find the best matching node in the DB.

    Returns ``(node_id, resolved_path)`` or ``(None, None)`` on miss.
    Resolution strategy:
        1. Exact adg_name match (``ADG::Module::<candidate_path>``)
        2. resolved_path match with ``<dotted>.py`` or ``<dotted>/__init__.py``
    """
    if not module_name:
        return (None, None)
    # Candidate file paths (repo-relative forward-slash).
    dotted = module_name.replace(".", "/")
    candidates = (
        f"{dotted}.py",
        f"{dotted}/__init__.py",
    )
    for cand in candidates:
        adg = ADG_MODULE_PREFIX + cand
        row = conn.execute(
            "SELECT id, resolved_path FROM nodes WHERE adg_name = ? OR resolved_path = ? LIMIT 1",
            (adg, cand),
        ).fetchone()
        if row is not None:
            return (str(row["id"]), row["resolved_path"])
    return (None, None)


def _mint_node_id(conn: sqlite3.Connection) -> str:
    """Generate a new unique node id by incrementing MAX(id)+1.

    Falls back to a prefixed UUID fragment if ids are non-numeric.
    """
    row = conn.execute("SELECT MAX(CAST(id AS INTEGER)) AS mx FROM nodes").fetchone()
    if row and row["mx"] is not None:
        return str(int(row["mx"]) + 1)
    # Non-numeric id space — use a deterministic prefix.
    import uuid

    return f"inc_{uuid.uuid4().hex[:12]}"


def _infer_layer_for_path(norm_path: str) -> str:
    """Map a repo-relative path to its canonical layer string."""
    prefix_to_layer = [
        ("agentic_core/L0_routing", "L0"),
        ("agentic_core/L1_cognition", "L1"),
        ("agentic_core/L2_execution", "L2"),
        ("agentic_core/L3_orchestration", "L3"),
        ("agentic_core/L4_state", "L4"),
        ("agentic_core/L5_safety", "L5"),
        ("agentic_core/L6_observability", "L6"),
        ("agentic_core/runtime", "L_RUNTIME"),
        ("agentic_core/", "L_AGENTIC_CORE"),
        ("apps_", "L_APPS"),
        ("tools/", "L_TOOLS"),
        ("tests/", "L_TESTS"),
        ("ops_scripts/", "L_OPS"),
        ("system_learning/", "L_SYSTEM_LEARNING"),
        ("infrastructure/", "L_INFRASTRUCTURE"),
    ]
    for prefix, layer in prefix_to_layer:
        if norm_path.startswith(prefix):
            return layer
    return "L_UNKNOWN"


__all__ = [
    "IncrementalReindexer",
    "ReindexDelta",
    "ADG_MODULE_PREFIX",
]

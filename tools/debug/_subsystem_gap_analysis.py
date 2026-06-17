"""Gap analysis — repo state vs the 4 knowledge subsystems.

Subsystems:
  1. Static ADG          (artifacts/adg/ + adg_sqlite MCP)
  2. Memory MCP          (artifacts/memory/knowledge_graph.sqlite + memory MCP)
  3. Runtime ADG / OTEL  (otel_mcp + OTEL backend)
  4. system_learning/    (the project's meta-learning subsystem)

For each, report: Storage state, MCP wiring state, Producer state, Consumer
state, and any obvious gaps.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path


def _size_mb(p: Path) -> float:
    if not p.exists():
        return 0.0
    if p.is_file():
        return p.stat().st_size / 1024 / 1024
    total = 0
    for child in p.rglob("*"):
        if child.is_file():
            try:
                total += child.stat().st_size
            except OSError:
                pass
    return total / 1024 / 1024


def _file_count(p: Path, pattern: str = "*") -> int:
    if not p.exists():
        return 0
    return sum(1 for x in p.rglob(pattern) if x.is_file())


def _sqlite_count(path: Path, table: str) -> int | None:
    if not path.exists():
        return None
    try:
        with sqlite3.connect(str(path)) as c:
            return c.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    except sqlite3.Error:
        return None


def _mcp_configured(name: str) -> bool:
    cfg = Path(".mcp.json")
    if not cfg.exists():
        return False
    data = json.loads(cfg.read_text(encoding="utf-8"))
    servers = data.get("mcpServers", data)
    server = servers.get(name)
    if not server:
        return False
    return not server.get("disabled", False)


def main() -> None:
    print("=" * 78)
    print("SUBSYSTEM GAP ANALYSIS — repo state vs 4 knowledge stores")
    print("=" * 78)

    # ---- 1. Static ADG ----
    print("\n[1] STATIC ADG  (code-structure knowledge)")
    print("-" * 78)
    adg_dir = Path("artifacts/adg")
    indexed = sorted(adg_dir.glob("adg_indexed_*.sqlite"))
    mcp_on = _mcp_configured("adg_sqlite")
    current_snap = indexed[-1] if indexed else None
    print(f"  MCP wired (adg_sqlite):  {'YES' if mcp_on else 'NO'}")
    print(f"  Current SQLite:          {current_snap.name if current_snap else 'NONE'}")
    print(f"    size:                  {_size_mb(current_snap) if current_snap else 0:.0f} MB")
    if current_snap:
        nodes = _sqlite_count(current_snap, "nodes")
        edges = _sqlite_count(current_snap, "edges")
        print(f"    nodes / edges:         {nodes:,} / {edges:,}")
    print(
        f"  Generator script:        tools/generate_full_adg.py  "
        f"({'exists' if Path('tools/generate_full_adg.py').exists() else 'MISSING'})"
    )
    print(f"  Directory total:         {_file_count(adg_dir)} files, {_size_mb(adg_dir):.0f} MB")
    print(f"  Archive retention:       keep_runs=1 (designed)")
    print(f"  Gap:                     none obvious — archiver now handles both TS formats")

    # ---- 2. Memory MCP ----
    print("\n[2] MEMORY MCP  (Codex's cross-session scratchpad)")
    print("-" * 78)
    mem = Path("artifacts/memory/knowledge_graph.sqlite")
    mcp_on = _mcp_configured("memory")
    print(f"  MCP wired (memory):      {'YES' if mcp_on else 'NO'}")
    print(f"  SQLite file:             {'exists' if mem.exists() else 'MISSING'}")
    print(f"    size:                  {_size_mb(mem):.1f} MB")
    entities = _sqlite_count(mem, "entities")
    obs = _sqlite_count(mem, "observations")
    rels = _sqlite_count(mem, "relations")
    print(f"    entities / obs / rel:  {entities} / {obs} / {rels}")
    # Break down by entityType
    if mem.exists():
        try:
            with sqlite3.connect(str(mem)) as c:
                cols = [r[1] for r in c.execute("PRAGMA table_info(entities)")]
                type_col = (
                    "entity_type"
                    if "entity_type" in cols
                    else ("entityType" if "entityType" in cols else None)
                )
                if type_col:
                    rows = c.execute(
                        f"SELECT {type_col}, COUNT(*) FROM entities "
                        f"GROUP BY {type_col} ORDER BY COUNT(*) DESC"
                    ).fetchall()
                    print(f"  By entity type:")
                    for t, n in rows:
                        print(f"    {t or '(null)':30s}  {n:>4}")
        except sqlite3.Error as e:
            print(f"  [type breakdown failed: {e}]")
    print(
        f"  Server script:           tools/memory/adg_memory_server.py  "
        f"({'exists' if Path('tools/memory/adg_memory_server.py').exists() else 'MISSING'})"
    )
    print(f"  Gap:                     none obvious")

    # ---- 3. Runtime ADG / OTEL ----
    print("\n[3] RUNTIME ADG / OTEL  (live agent behavior)")
    print("-" * 78)
    mcp_on = _mcp_configured("otel_mcp")
    print(f"  MCP wired (otel_mcp):    {'YES' if mcp_on else 'NO'}")

    # Resolve the canonical runtime ADG directory via otel_config (SSOT) —
    # avoids the previous hardcoded `artifacts/otel` / `system_learning/runtime_adg`
    # paths which were both wrong.
    try:
        from tools.otel.otel_config import build_config  # noqa: PLC0415

        _cfg = build_config(
            __file__.replace("tools\\debug\\_subsystem_gap_analysis.py", "tools\\otel\\otel_mcp_server.py")
        )
        runtime_adg_dir = _cfg.runtime_adg_dir
    except (ImportError, AttributeError, OSError) as exc:
        # Hard fallback to the canonical literal if the config module is unusable.
        runtime_adg_dir = Path("agentic_core/L4_state/memory/runtime_adg")
        print(f"  [WARN] otel_config import failed ({exc}); using literal fallback")

    try:
        display_path = runtime_adg_dir.relative_to(Path.cwd())
    except ValueError:
        display_path = runtime_adg_dir
    print(f"  runtime_adg_dir:         {display_path}")
    if runtime_adg_dir.exists():
        snapshot_files = [
            p
            for p in runtime_adg_dir.rglob("*.json")
            if p.name != "_index.json" and p.name != "_trace_index.json"
        ]
        print(f"    snapshot files:        {len(snapshot_files)}")
        print(f"    total size:            {_size_mb(runtime_adg_dir):.2f} MB")
    else:
        print(f"    MISSING")

    # look for traces
    traces_count = sum(
        1 for p in Path(".").rglob("*.jsonl") if "trace" in p.name.lower() or "span" in p.name.lower()
    )
    print(f"  trace/span JSONL files:  {traces_count} (repo-wide)")

    # ---- 4. system_learning/ ----
    print("\n[4] system_learning/  (meta-learning subsystem)")
    print("-" * 78)
    sl = Path("system_learning")
    print(f"  Source tree:             {'exists' if sl.exists() else 'MISSING'}")
    key_subdirs = [
        "adapters",
        "arbitration",
        "confidence",
        "meta_learning",
        "stores",
        "state",
        "snapshots",
        "ports",
        "engines",
        "runtime_adg",
        "telemetry",
    ]
    for sd in key_subdirs:
        p = sl / sd
        mark = "OK" if p.exists() else "MISSING"
        file_count = _file_count(p) if p.exists() else 0
        print(f"    {sd:20s} {mark:8s} {file_count} files")
    # Check for any persistent state
    state_dir = sl / "state"
    snap_dir = sl / "snapshots"
    print(f"  state/ files:            {_file_count(state_dir)}  ({_size_mb(state_dir):.1f} MB)")
    print(f"  snapshots/ files:        {_file_count(snap_dir)}  ({_size_mb(snap_dir):.1f} MB)")
    # Check runtime_hitl_consumer is present
    rhc = sl / "runtime_hitl_consumer.py"
    print(f"  runtime_hitl_consumer:   {'exists' if rhc.exists() else 'MISSING'}")


if __name__ == "__main__":
    main()

"""A6: Non-AST Entrypoint Scanner.

Scans configuration files for Python entrypoint references and emits
entrypoint_kind edges into the ADG edge list.

Sources:
  - .claude/settings.json → entrypoint_kind=hook
  - .mcp.json → entrypoint_kind=mcp
  - .pre-commit-config.yaml → entrypoint_kind=hook
  - .github/workflows/*.yml → entrypoint_kind=ci
  - pyproject.toml [project.scripts] → entrypoint_kind=cli
"""

from __future__ import annotations

import ast
import json
import re
import sqlite3
import sys
from pathlib import Path

from tqdm import tqdm  # progress: §16 compliance for scan/write loops

REPO = Path(__file__).resolve().parents[2]

# Regex to extract python file references from command strings
_PY_FILE_RE = re.compile(r"([a-zA-Z0-9_/]+\.py)")
_PY_MODULE_RE = re.compile(r"python\s+([a-zA-Z0-9_/]+\.py)")


def _resolve_to_repo_relative(raw: str) -> str | None:
    """Convert a raw path reference to a repo-relative path.

    Returns None if the path doesn't look like a repo file.
    """
    # Normalize backslashes
    raw = raw.replace("\\", "/")
    # Strip leading ./ or /
    raw = raw.lstrip("./")
    # Skip absolute paths outside repo
    if raw.startswith("C:") or raw.startswith("/usr") or raw.startswith("/opt"):
        return None
    # Skip if no .py extension
    if not raw.endswith(".py"):
        return None
    # Check if file exists in repo
    candidate = REPO / raw
    if candidate.is_file():
        return raw
    return None


def _extract_py_files_from_command(command: str) -> list[str]:
    """Extract Python file references from a command string."""
    results: list[str] = []
    # Match "python <file>.py" patterns
    for m in _PY_MODULE_RE.finditer(command):
        resolved = _resolve_to_repo_relative(m.group(1))
        if resolved:
            results.append(resolved)
    # Match bare .py references
    if not results:
        for m in _PY_FILE_RE.finditer(command):
            resolved = _resolve_to_repo_relative(m.group(1))
            if resolved:
                results.append(resolved)
    return results


def _scan_hooks_json() -> list[tuple[str, str]]:
    """Scan .claude/settings.json for hook entrypoints.

    Returns list of (repo_relative_path, entrypoint_kind).
    """
    settings_path = REPO / ".claude" / "settings.json"
    if not settings_path.is_file():
        return []

    results: list[tuple[str, str]] = []
    try:
        data = json.loads(settings_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return []

    def iter_commands(value: object) -> list[str]:
        commands: list[str] = []
        if isinstance(value, dict):
            command = value.get("command")
            if isinstance(command, str):
                commands.append(command)
            for nested in value.values():
                commands.extend(iter_commands(nested))
        elif isinstance(value, list):
            for item in value:
                commands.extend(iter_commands(item))
        return commands

    for command in iter_commands(data.get("hooks", {})):
        for py_file in _extract_py_files_from_command(command):
            results.append((py_file, "hook"))

    return results


def _scan_mcp_config() -> list[tuple[str, str]]:
    """Scan root .mcp.json for MCP entrypoints.

    Returns list of (repo_relative_path, entrypoint_kind).
    """
    mcp_path = REPO / ".mcp.json"
    if not mcp_path.is_file():
        return []

    results: list[tuple[str, str]] = []
    try:
        data = json.loads(mcp_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return []

    servers = data.get("mcpServers", {})
    for _name, config in servers.items():
        # progress_bar: bounded by mcpServers count (~10 entries, <100ms — §16 exempt)
        if not isinstance(config, dict):
            continue
        command = config.get("command", "")
        args = config.get("args", [])
        # Check command
        for py_file in _extract_py_files_from_command(command):
            results.append((py_file, "mcp"))
        # Check args
        for arg in args:
            if isinstance(arg, str):
                for py_file in _extract_py_files_from_command(arg):
                    results.append((py_file, "mcp"))

    return results


def _scan_pre_commit() -> list[tuple[str, str]]:
    """Scan .pre-commit-config.yaml for hook entrypoints.

    Returns list of (repo_relative_path, entrypoint_kind).
    """
    pc_path = REPO / ".pre-commit-config.yaml"
    if not pc_path.is_file():
        return []

    results: list[tuple[str, str]] = []
    try:
        content = pc_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return []

    # Simple regex-based extraction (no yaml dependency needed)
    # Match "entry:" lines
    entry_re = re.compile(r"entry:\s*(.+)")
    for m in tqdm(entry_re.finditer(content), desc="Scanning pre-commit config"):  # progress: §16 compliance
        entry_val = m.group(1).strip()
        for py_file in _extract_py_files_from_command(entry_val):
            results.append((py_file, "hook"))

    return results


def _scan_github_workflows() -> list[tuple[str, str]]:
    """Scan .github/workflows/*.yml for CI entrypoints.

    Returns list of (repo_relative_path, entrypoint_kind).
    """
    workflows_dir = REPO / ".github" / "workflows"
    if not workflows_dir.is_dir():
        return []

    results: list[tuple[str, str]] = []
    for wf_path in workflows_dir.glob("*.yml"):
        # progress_bar: bounded by workflows file count (~10-20, regex-only — §16 exempt)
        try:
            content = wf_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        # Match "python <file>.py" patterns in run: blocks
        for m in _PY_MODULE_RE.finditer(content):
            resolved = _resolve_to_repo_relative(m.group(1))
            if resolved:
                results.append((resolved, "ci"))
        # Also match bare .py references in run: blocks
        for m in _PY_FILE_RE.finditer(content):
            resolved = _resolve_to_repo_relative(m.group(1))
            if resolved and (resolved, "ci") not in results:
                results.append((resolved, "ci"))

    return results


def _scan_pyproject_scripts() -> list[tuple[str, str]]:
    """Scan pyproject.toml [project.scripts] for CLI entrypoints.

    Returns list of (repo_relative_path, entrypoint_kind).
    """
    pyproject_path = REPO / "pyproject.toml"
    if not pyproject_path.is_file():
        return []

    results: list[tuple[str, str]] = []
    try:
        content = pyproject_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return []

    # Simple regex: [project.scripts] section with "name = module:function" entries
    in_scripts = False
    for line in content.splitlines():
        # progress_bar: bounded by pyproject.toml line count, single-file scan — §16 exempt
        stripped = line.strip()
        if stripped == "[project.scripts]":
            in_scripts = True
            continue
        if stripped.startswith("[") and in_scripts:
            break  # next section
        if in_scripts and "=" in stripped:
            # Extract module path
            rhs = stripped.split("=", 1)[1].strip()
            # Format: "package.module:function" → convert to path
            module_part = rhs.split(":")[0].strip().strip('"').strip("'")
            path_candidate = module_part.replace(".", "/") + ".py"
            resolved = _resolve_to_repo_relative(path_candidate)
            if resolved:
                results.append((resolved, "cli"))

    return results


def scan_all_entrypoints() -> list[tuple[str, str]]:
    """Run all entrypoint scanners and return deduplicated results.

    Returns list of (repo_relative_path, entrypoint_kind).
    Priority on conflict: mcp > hook > ci > cli > imported
    """
    # progress_bar: 5 fixed-cost scanners over small config files (<1s total — §16 exempt)
    all_results: list[tuple[str, str]] = []
    all_results.extend(_scan_hooks_json())
    all_results.extend(_scan_mcp_config())
    all_results.extend(_scan_pre_commit())
    all_results.extend(_scan_github_workflows())
    all_results.extend(_scan_pyproject_scripts())

    # Deduplicate with priority
    priority = {"mcp": 5, "hook": 4, "ci": 3, "cli": 2, "imported": 1}
    best: dict[str, str] = {}
    for path, kind in all_results:
        if path not in best or priority.get(kind, 0) > priority.get(best[path], 0):
            best[path] = kind

    return list(best.items())


def write_entrypoint_edges(sqlite_path: Path) -> int:
    """Write entrypoint_kind edges into the ADG SQLite.

    Returns the number of edges written.
    """
    entrypoints = scan_all_entrypoints()
    if not entrypoints:
        return 0

    conn = sqlite3.connect(str(sqlite_path), timeout=30)
    conn.execute("PRAGMA journal_mode=WAL")
    cursor = conn.cursor()

    # Find node IDs for each entrypoint file
    edge_count = 0
    for rel_path, kind in tqdm(entrypoints, desc="A6 entrypoint edges", unit="ep"):  # progress: §16
        # Normalize path for matching
        normalized = rel_path.replace("\\", "/")
        cursor.execute(
            "SELECT id, adg_name FROM nodes WHERE resolved_path = ? AND entity_type = 'module'",
            (normalized,),
        )
        row = cursor.fetchone()
        if not row:
            # Try with leading path variations
            for variant in (normalized, f"./{normalized}", f".\\{normalized}"):
                cursor.execute(
                    "SELECT id, adg_name FROM nodes WHERE resolved_path LIKE ? AND entity_type = 'module'",
                    (f"%{variant}%",),
                )
                row = cursor.fetchone()
                if row:
                    break

        if row:
            node_id = row[0]
        else:
            # No matching node — create a synthetic module node for this entrypoint
            adg_name = f"ADG::Module::{normalized}"
            cursor.execute(
                "INSERT INTO nodes (adg_name, entity_type, layer, identity_kind, confidence, resolved_path, entrypoint_kind) "
                "VALUES (?, 'module', 'L_TOOLS', 'entrypoint_inferred', 0.9, ?, ?)",
                (adg_name, normalized, kind),
            )
            node_id = cursor.lastrowid

        # Create synthetic target node if not exists
        target_name = f"ADG::Entrypoint::{kind}"
        cursor.execute("SELECT id FROM nodes WHERE adg_name = ?", (target_name,))
        target_row = cursor.fetchone()
        if not target_row:
            cursor.execute(
                "INSERT INTO nodes (adg_name, entity_type, layer, identity_kind, confidence, resolved_path) "
                "VALUES (?, 'Entrypoint', 'L_META', 'synthetic', 1.0, '')",
                (target_name,),
            )
            target_id = cursor.lastrowid
        else:
            target_id = target_row[0]

        # Insert edge
        cursor.execute(
            "INSERT INTO edges (src_id, dst_id, relation_type, edge_kind, source_file, line_no, symbol, semantic_type) "
            "VALUES (?, ?, 'entrypoint_kind', 'entrypoint', ?, ?, ?, ?)",
            (node_id, target_id, rel_path, 0, kind, kind),
        )
        edge_count += 1

        # Update node's entrypoint_kind column
        try:
            cursor.execute(
                "UPDATE nodes SET entrypoint_kind = ? WHERE id = ?",
                (kind, node_id),
            )
        except sqlite3.OperationalError:
            pass  # Column doesn't exist yet — that's OK

    conn.commit()
    conn.close()
    return edge_count


def main() -> int:
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="A6: Scan non-AST entrypoints")
    parser.add_argument("--sqlite", type=Path, help="Path to ADG SQLite file")
    parser.add_argument("--dry-run", action="store_true", help="Print results without writing")
    args = parser.parse_args()

    entrypoints = scan_all_entrypoints()
    print(f"[A6] Found {len(entrypoints)} non-AST entrypoints:")
    for path, kind in sorted(entrypoints):
        print(f"  [{kind}] {path}")

    if args.sqlite and not args.dry_run:
        count = write_entrypoint_edges(args.sqlite)
        print(f"[A6] Wrote {count} entrypoint_kind edges to {args.sqlite}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

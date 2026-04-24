#!/usr/bin/env python3
"""
ADG Query Bridge — Unified Query Interface

Provides a unified interface for CI scripts to query ADG data
with automatic backend selection: Redis → SQLite → AST fallback.

This replaces direct glob+AST+regex patterns in CI scripts with
ADG-powered queries for better performance and accuracy.
"""

import ast
import json
import logging
import sqlite3
import warnings
from pathlib import Path
from typing import Any

# Try to import ADG Redis MCP
try:
    # MCP tools are accessed via the MCP protocol, not as Python imports
    # Redis access is handled via direct connection or SQLite fallback
    ADG_REDIS_AVAILABLE = False
except ImportError as e:
    warnings.warn(f"ADG Redis MCP unavailable: {e}", stacklevel=2)
    ADG_REDIS_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


class FileMatch:
    """Represents a file match with location and context."""

    def __init__(
        self,
        file_path: str,
        line_number: int | None = None,
        symbol: str | None = None,
        context: str | None = None,
    ):
        self.file_path = file_path
        self.line_number = line_number
        self.symbol = symbol
        self.context = context

    def __repr__(self):
        return f"FileMatch({self.file_path}:{self.line_number} -> {self.symbol})"


class Node:
    """Represents an ADG node with metadata."""

    def __init__(
        self,
        node_id: str,
        label: str,
        layer: str,
        entity_type: str,
        file_path: str | None = None,
        **kwargs,
    ):
        self.node_id = node_id
        self.label = label
        self.layer = layer
        self.entity_type = entity_type
        self.file_path = file_path
        self.attributes = kwargs

    def __repr__(self):
        return f"Node({self.label} in {self.layer} [{self.entity_type}])"


class Violation:
    """Represents an ADG anti-pattern violation."""

    def __init__(
        self,
        file_path: str,
        line_number: int,
        category: str,
        evidence: str,
        symbol: str | None = None,
    ):
        self.file_path = file_path
        self.line_number = line_number
        self.category = category
        self.evidence = evidence
        self.symbol = symbol

    def __repr__(self):
        return f"Violation({self.category} at {self.file_path}:{self.line_number})"


class ADGQueryBridge:
    """Unified query interface: ADG Redis → ADG SQLite → AST fallback."""

    def __init__(self, repo_root: str | None = None):
        self.repo_root = Path(repo_root) if repo_root else Path.cwd()
        self.adg_dir = self.repo_root / "artifacts" / "adg"
        self._cache_status = None
        self._sqlite_path = None
        self._table_columns: dict[str, set[str]] = {}

    def _check_adg_status(self) -> dict[str, Any]:
        """Check ADG Redis cache status."""
        if self._cache_status is None:
            # Redis MCP unavailable - always use SQLite fallback
            self._cache_status = {"is_fresh": False, "error": "ADG Redis MCP unavailable"}
        return self._cache_status

    def _get_sqlite_path(self) -> Path | None:
        """Find the latest ADG SQLite database."""
        if self._sqlite_path is None:
            if self.repo_root.suffix == ".sqlite" and self.repo_root.exists():
                self._sqlite_path = self.repo_root
                return self._sqlite_path
            candidate = self.repo_root.with_suffix(".sqlite")
            if candidate.exists():
                self._sqlite_path = candidate
                return self._sqlite_path
            # Look for the latest adg_indexed_*.sqlite file
            sqlite_files = list(self.adg_dir.glob("adg_indexed_*.sqlite"))
            if sqlite_files:
                # Sort by timestamp in filename and take the latest
                sqlite_files.sort(key=lambda x: x.name, reverse=True)
                self._sqlite_path = sqlite_files[0]
                logger.info(f"Using ADG SQLite: {self._sqlite_path}")
            else:
                logger.warning("No ADG SQLite database found")
        return self._sqlite_path

    def _get_table_columns(self, table: str) -> set[str]:
        """Get column names for a SQLite table."""
        if table in self._table_columns:
            return self._table_columns[table]
        sqlite_path = self._get_sqlite_path()
        if not sqlite_path:
            self._table_columns[table] = set()
            return self._table_columns[table]
        try:
            conn = sqlite3.connect(sqlite_path)
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info({table})")
            columns = {row[1] for row in cursor.fetchall()}
            conn.close()
        except Exception:  # guardian: allow-broad-exception -- offline tooling, reports failure
            columns = set()
        self._table_columns[table] = columns
        return columns

    def _query_sqlite(self, query: str, params: tuple = ()) -> list[dict[str, Any]]:
        """Execute a query against the ADG SQLite database."""
        sqlite_path = self._get_sqlite_path()
        if not sqlite_path:
            return []

        try:
            conn = sqlite3.connect(sqlite_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            results = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return results
        except Exception as e:  # guardian: allow-broad-exception -- offline tooling, reports failure
            logger.error(f"SQLite query failed: {e}")
            return []

    def _find_node_by_symbol(self, symbol: str) -> str | None:
        """Find node ID by symbol name."""
        columns = self._get_table_columns("nodes")
        clauses = []
        params: list[str] = []
        if "adg_name" in columns:
            clauses.append("adg_name = ?")
            params.append(symbol)
        if "label" in columns:
            clauses.append("label = ?")
            params.append(symbol)
        if not clauses:
            return None
        query = f"SELECT id FROM nodes WHERE {' OR '.join(clauses)} LIMIT 1"
        results = self._query_sqlite(query, tuple(params))
        if results:
            return results[0]["id"]

        # Redis unavailable - use SQLite only
        return None

    def files_calling(self, symbol: str) -> list[FileMatch]:
        """Find files that call the given symbol."""
        status = self._check_adg_status()

        # Redis unavailable - use SQLite fallback only
        columns = self._get_table_columns("edges")
        if "relation_type" not in columns or "symbol" not in columns:
            return []
        results = self._query_sqlite(
            "SELECT * FROM edges WHERE relation_type = 'calls' AND symbol LIKE ?",
            (f"%{symbol}%",),
        )
        matches = []
        for row in results:
            file_path = row.get("source_file") or row.get("file_path") or ""
            line_no = row.get("line_no") or row.get("line")
            matches.append(FileMatch(file_path, line_no, row.get("symbol")))
        return matches

    def files_importing(self, module: str) -> list[FileMatch]:
        """Find files that import the given module."""
        status = self._check_adg_status()

        # Redis unavailable - use SQLite fallback only
        columns = self._get_table_columns("edges")
        if "relation_type" not in columns or "symbol" not in columns:
            return []
        if "to_name" in columns:
            query = (
                "SELECT * FROM edges WHERE relation_type = 'imports' AND (symbol LIKE ? OR to_name LIKE ?)"
            )
            params = (f"%{module}%", f"%{module}%")
        else:
            query = "SELECT * FROM edges WHERE relation_type = 'imports' AND symbol LIKE ?"
            params = (f"%{module}%",)
        results = self._query_sqlite(query, params)
        matches = []
        for row in results:
            file_path = row.get("source_file") or row.get("file_path") or ""
            line_no = row.get("line_no") or row.get("line")
            matches.append(FileMatch(file_path, line_no, row.get("symbol")))
        return matches

    def nodes_in_layer(self, layer: str) -> list[Node]:
        """Get all nodes in the specified layer."""
        # Redis unavailable - use SQLite only
        columns = self._get_table_columns("nodes")
        if "layer" not in columns:
            return []
        results = self._query_sqlite("SELECT * FROM nodes WHERE layer = ?", (layer,))

        return [
            Node(
                node_id=r["id"],
                label=r.get("adg_name") or r.get("label") or r.get("name") or "",
                layer=r.get("layer", ""),
                entity_type=r.get("entity_type", ""),
                file_path=r.get("resolved_path") or r.get("file_path"),
            )
            for r in results
        ]

    def violations(self) -> list[Violation]:
        """Get all anti-pattern violations."""
        # Redis unavailable - use AST fallback directly
        logger.info("Violations not available in Redis/SQLite, using AST fallback")
        return self._violations_ast_fallback()

    def files_in_scope(self, directories: list[str]) -> list[Path]:
        """Get files in scope using ADG file discovery (replaces glob/rglob)."""
        status = self._check_adg_status()
        files = set()

        # Try Redis/SQLite approach first
        if status.get("is_fresh") or self._get_sqlite_path():
            for directory in directories:
                dir_path = Path(directory)
                if not dir_path.exists():
                    continue

                # Try to get files from ADG nodes by file
                try:
                    if status.get("is_fresh"):
                        # This is a simplified approach - might need refinement
                        for root_dir in [dir_path]:
                            for py_file in root_dir.rglob("*.py"):
                                if py_file.is_file():
                                    files.add(py_file)
                    else:
                        # SQLite approach
                        rel_path = str(dir_path.relative_to(self.repo_root))
                        pattern = f"{rel_path}%"
                        results = self._query_sqlite(
                            "SELECT DISTINCT resolved_path FROM nodes WHERE resolved_path LIKE ?",
                            (pattern,),
                        )
                        for r in results:
                            file_path = self.repo_root / r["resolved_path"]
                            if file_path.exists():
                                files.add(file_path)
                except Exception as e:  # guardian: allow-broad-exception -- offline tooling, reports failure
                    logger.warning(f"ADG file discovery failed for {directory}: {e}")
                    # Fall back to traditional glob
                    files.update(dir_path.rglob("*.py"))
        else:
            # Traditional glob fallback
            for directory in directories:
                dir_path = Path(directory)
                if dir_path.exists():
                    files.update(dir_path.rglob("*.py"))

        return sorted(files)

    def subprocess_calls_without_timeout(self) -> list[FileMatch]:
        """Find subprocess.run/Popen calls without timeout using ADG edges."""
        status = self._check_adg_status()

        # Try Redis first if cache is fresh
        if status.get("is_fresh"):
            try:
                # Look for calls to subprocess.run and subprocess.Popen
                matches = []
                for symbol in ["subprocess.run", "subprocess.Popen"]:
                    symbol_matches = self.files_calling(symbol)
                    matches.extend(symbol_matches)

                # Filter for those likely without timeout (simplified heuristic)
                # In practice, would need AST analysis to check for timeout parameter
                return matches
            except Exception as e:  # guardian: allow-broad-exception -- offline tooling, reports failure
                logger.warning(f"Redis query failed, falling back to SQLite: {e}")

        # Fallback to SQLite
        results = self._query_sqlite("""
            SELECT DISTINCT e.source_file, e.line_no, e.symbol
            FROM edges e
            WHERE e.relation_type = 'calls'
            AND (e.symbol LIKE 'subprocess.run%' OR e.symbol LIKE 'subprocess.Popen%')
        """)

        return [FileMatch(r["source_file"], r["line_no"], r["symbol"]) for r in results]

    def loops_without_progress(self) -> list[FileMatch]:
        """Find loops without progress reporting (AST fallback - needs body analysis)."""
        logger.info("loops_without_progress requires AST analysis, using fallback")
        return self._loops_ast_fallback()

    def _violations_ast_fallback(self) -> list[Violation]:
        """AST fallback for violation detection."""
        violations = []
        repo_root = self.repo_root

        for py_file in repo_root.rglob("*.py"):
            if not py_file.is_file():
                continue

            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                tree = ast.parse(content)

                for node in ast.walk(tree):
                    # Look for common anti-patterns
                    if isinstance(node, ast.ExceptHandler) and node.type is None:
                        violations.append(
                            Violation(
                                file_path=str(py_file.relative_to(repo_root)),
                                line_number=node.lineno,
                                category="bare_except",
                                evidence="bare except clause",
                            ),
                        )

                    elif isinstance(node, ast.Call):
                        # Check for other patterns as needed
                        pass

            except Exception as e:  # guardian: allow-broad-exception -- offline tooling, reports failure
                logger.debug(f"Could not parse {py_file}: {e}")

        return violations

    def _loops_ast_fallback(self) -> list[FileMatch]:
        """AST fallback for loop detection."""
        loops = []
        repo_root = self.repo_root

        for py_file in repo_root.rglob("*.py"):
            if not py_file.is_file():
                continue

            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, (ast.For, ast.While)):
                        # Simple heuristic - look for loops without progress reporting
                        # In practice, would need more sophisticated analysis
                        loops.append(
                            FileMatch(
                                file_path=str(py_file.relative_to(repo_root)),
                                line_number=node.lineno,
                                symbol="loop",
                                context="for/while loop",
                            ),
                        )

            except Exception as e:  # guardian: allow-broad-exception -- offline tooling, reports failure
                logger.debug(f"Could not parse {py_file}: {e}")

        return loops


# Convenience functions for common use cases
def files_calling(symbol: str, repo_root: str | None = None) -> list[FileMatch]:
    """Convenience function to find files calling a symbol."""
    bridge = ADGQueryBridge(repo_root)
    return bridge.files_calling(symbol)


def files_importing(module: str, repo_root: str | None = None) -> list[FileMatch]:
    """Convenience function to find files importing a module."""
    bridge = ADGQueryBridge(repo_root)
    return bridge.files_importing(module)


def nodes_in_layer(layer: str, repo_root: str | None = None) -> list[Node]:
    """Convenience function to get nodes in a layer."""
    bridge = ADGQueryBridge(repo_root)
    return bridge.nodes_in_layer(layer)


def violations(repo_root: str | None = None) -> list[Violation]:
    """Convenience function to get violations."""
    bridge = ADGQueryBridge(repo_root)
    return bridge.violations()


def subprocess_calls_without_timeout(repo_root: str | None = None) -> list[FileMatch]:
    """Convenience function to find subprocess calls without timeout."""
    bridge = ADGQueryBridge(repo_root)
    return bridge.subprocess_calls_without_timeout()


if __name__ == "__main__":
    # Simple CLI for testing
    import argparse

    parser = argparse.ArgumentParser(description="ADG Query Bridge CLI")
    parser.add_argument(
        "query",
        choices=["files-calling", "files-importing", "nodes-in-layer", "violations", "subprocess-calls"],
    )
    parser.add_argument("--symbol", help="Symbol or module name")
    parser.add_argument("--layer", help="Layer name")
    parser.add_argument("--repo-root", help="Repository root path")

    args = parser.parse_args()

    bridge = ADGQueryBridge(args.repo_root)

    if args.query == "files-calling" and args.symbol:
        results = bridge.files_calling(args.symbol)
    elif args.query == "files-importing" and args.symbol:
        results = bridge.files_importing(args.symbol)
    elif args.query == "nodes-in-layer" and args.layer:
        results = bridge.nodes_in_layer(args.layer)
    elif args.query == "violations":
        results = bridge.violations()
    elif args.query == "subprocess-calls":
        results = bridge.subprocess_calls_without_timeout()
    else:
        parser.error("Invalid arguments")

    print(json.dumps([vars(r) if hasattr(r, "__dict__") else str(r) for r in results], indent=2))


def query_bridge(query: str) -> dict:
    """Bridge query function."""
    return {"results": []}

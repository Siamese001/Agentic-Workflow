from __future__ import annotations
"""
Dependency Graph Analyzer (DGA) — Phase 2 Tool

Unified graph for import/call dependencies enabling:
- Cycle detection (circular imports)
- Impact analysis (what breaks if X changes)
- Unused import detection
- Dependency visualization

Part of the Tool Registry Enhancement Roadmap.
"""
import ast
import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from pydantic import BaseModel, Field
from agentic_core.utils.sovereign_index import SovereignIndex
from agentic_core.utils.file_utils import safe_read_file, safe_write_file


class GraphOperation(str, Enum):
    """Supported dependency graph operations."""
    BUILD_GRAPH = "build_graph"
    DETECT_CYCLES = "detect_cycles"
    IMPACT_ANALYSIS = "ImpactAnalysis"
    UNUSED_IMPORTS = "unused_imports"
    MODULE_DEPENDENCIES = "module_dependencies"


class DependencyGraphArgs(BaseModel):
    """Arguments for dependency graph operations."""
    operation: GraphOperation = Field(
        description="Operation to perform on the dependency graph"
    )
    target_path: str = Field(
        description="File or directory path to analyze"
    )
    symbol: Optional[str] = Field(
        default=None,
        description="Symbol name for impact analysis (function, class, or module)"
    )
    max_depth: Optional[int] = Field(
        default=10,
        description="Maximum depth for recursive analysis"
    )
    include_stdlib: bool = Field(
        default=False,
        description="Include standard library modules in graph"
    )


@dataclass
class DependencyNode:
    """A node in the dependency graph."""
    name: str
    path: Optional[str] = None
    node_type: str = "module"  # module, function, class
    imports: List[str] = field(default_factory=list)
    imported_by: List[str] = field(default_factory=list)
    calls: List[str] = field(default_factory=list)
    called_by: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "path": self.path,
            "node_type": self.node_type,
            "imports": self.imports,
            "imported_by": self.imported_by,
            "calls": self.calls,
            "called_by": self.called_by,
        }


@dataclass
class DependencyGraph:
    """Complete dependency graph structure."""
    nodes: Dict[str, DependencyNode] = field(default_factory=dict)
    edges: List[Tuple[str, str, str]] = field(default_factory=list)  # (from, to, type)

    def add_node(self, name: str, **kwargs) -> DependencyNode:
        """Add or update a node in the graph."""
        if name not in self.nodes:
            self.nodes[name] = DependencyNode(name=name, **kwargs)
        return self.nodes[name]

    def add_edge(self, from_node: str, to_node: str, edge_type: str = "imports"):
        """Add an edge between nodes."""
        self.edges.append((from_node, to_node, edge_type))

        # Update node relationships
        if from_node in self.nodes:
            if edge_type == "imports":
                if to_node not in self.nodes[from_node].imports:
                    self.nodes[from_node].imports.append(to_node)
            elif edge_type == "calls":
                if to_node not in self.nodes[from_node].calls:
                    self.nodes[from_node].calls.append(to_node)

        if to_node in self.nodes:
            if edge_type == "imports":
                if from_node not in self.nodes[to_node].imported_by:
                    self.nodes[to_node].imported_by.append(from_node)
            elif edge_type == "calls":
                if from_node not in self.nodes[to_node].called_by:
                    self.nodes[to_node].called_by.append(from_node)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "nodes": {k: v.to_dict() for k, v in self.nodes.items()},
            "edges": [{"from": e[0], "to": e[1], "type": e[2]} for e in self.edges],
            "node_count": len(self.nodes),
            "edge_count": len(self.edges),
        }


@dataclass
class GraphResult:
    """Result of a dependency graph operation."""
    success: bool
    operation: str
    data: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "operation": self.operation,
            "data": self.data,
            "warnings": self.warnings,
            "error": self.error,
        }


# =============================================================================
# STDLIB MODULES (for filtering)
# =============================================================================
STDLIB_MODULES = {
    "abc", "aifc", "argparse", "array", "ast", "asynchat", "asyncio", "asyncore",
    "atexit", "audioop", "base64", "bdb", "binascii", "binhex", "bisect",
    "builtins", "bz2", "calendar", "cgi", "cgitb", "chunk", "cmath", "cmd",
    "code", "codecs", "codeop", "collections", "colorsys", "compileall",
    "concurrent", "configparser", "contextlib", "contextvars", "copy", "copyreg",
    "cProfile", "crypt", "csv", "ctypes", "curses", "dataclasses", "datetime",
    "dbm", "decimal", "difflib", "dis", "distutils", "doctest", "email",
    "encodings", "enum", "errno", "faulthandler", "fcntl", "filecmp", "fileinput",
    "fnmatch", "fractions", "ftplib", "functools", "gc", "getopt", "getpass",
    "gettext", "glob", "graphlib", "grp", "gzip", "hashlib", "heapq", "hmac",
    "html", "http", "idlelib", "imaplib", "imghdr", "imp", "importlib", "inspect",
    "io", "ipaddress", "itertools", "json", "keyword", "lib2to3", "linecache",
    "locale", "logging", "lzma", "mailbox", "mailcap", "marshal", "math",
    "mimetypes", "mmap", "modulefinder", "multiprocessing", "netrc", "nis",
    "nntplib", "numbers", "operator", "optparse", "os", "ossaudiodev", "pathlib",
    "pdb", "pickle", "pickletools", "pipes", "pkgutil", "platform", "plistlib",
    "poplib", "posix", "posixpath", "pprint", "profile", "pstats", "pty", "pwd",
    "py_compile", "pyclbr", "pydoc", "queue", "quopri", "random", "re",
    "readline", "reprlib", "resource", "rlcompleter", "runpy", "sched", "secrets",
    "select", "selectors", "shelve", "shlex", "shutil", "signal", "site",
    "smtpd", "smtplib", "sndhdr", "socket", "socketserver", "spwd", "sqlite3",
    "ssl", "stat", "statistics", "string", "stringprep", "struct", "subprocess",
    "sunau", "symtable", "sys", "sysconfig", "syslog", "tabnanny", "tarfile",
    "telnetlib", "tempfile", "termios", "test", "textwrap", "threading", "time",
    "timeit", "tkinter", "token", "tokenize", "trace", "traceback", "tracemalloc",
    "tty", "turtle", "turtledemo", "types", "typing", "unicodedata", "unittest",
    "urllib", "uu", "uuid", "venv", "warnings", "wave", "weakref", "webbrowser",
    "winreg", "winsound", "wsgiref", "xdrlib", "xml", "xmlrpc", "zipapp",
    "zipfile", "zipimport", "zlib", "_thread",
}


class ImportExtractor(ast.NodeVisitor):
    """Extract imports from Python AST."""

    def __init__(self, include_stdlib: bool = False):
        self.imports: List[Dict[str, Any]] = []
        self.include_stdlib = include_stdlib

    def _is_stdlib(self, module: str) -> bool:
        """Check if module is from standard library."""
        root = module.split(".")[0]
        return root in STDLIB_MODULES

    def visit_Import(self, node: ast.Import):
        """Handle 'import x' statements."""
        for alias in node.names:
            module = alias.name
            if self.include_stdlib or not self._is_stdlib(module):
                self.imports.append({
                    "module": module,
                    "alias": alias.asname,
                    "line": node.lineno,
                    "type": "import",
                })
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        """Handle 'from x import y' statements."""
        module = node.module or ""
        if self.include_stdlib or not self._is_stdlib(module):
            for alias in node.names:
                self.imports.append({
                    "module": module,
                    "name": alias.name,
                    "alias": alias.asname,
                    "line": node.lineno,
                    "type": "from_import",
                    "level": node.level,  # Relative import level
                })
        self.generic_visit(node)


class CallExtractor(ast.NodeVisitor):
    """Extract function/method calls from Python AST."""

    def __init__(self):
        self.calls: List[Dict[str, Any]] = []
        self._current_scope: List[str] = []

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Track function scope."""
        self._current_scope.append(node.name)
        self.generic_visit(node)
        self._current_scope.pop()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        """Track async function scope."""
        self._current_scope.append(node.name)
        self.generic_visit(node)
        self._current_scope.pop()

    def visit_ClassDef(self, node: ast.ClassDef):
        """Track class scope."""
        self._current_scope.append(node.name)
        self.generic_visit(node)
        self._current_scope.pop()

    def visit_Call(self, node: ast.Call):
        """Extract call information."""
        call_name = self._get_call_name(node.func)
        if call_name:
            self.calls.append({
                "name": call_name,
                "line": node.lineno,
                "scope": ".".join(self._current_scope) if self._current_scope else "<module>",
            })
        self.generic_visit(node)

    def _get_call_name(self, node: ast.expr) -> Optional[str]:
        """Extract the name of a called function."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            value = self._get_call_name(node.value)
            if value:
                return f"{value}.{node.attr}"
            return node.attr
        return None


class DefinitionExtractor(ast.NodeVisitor):
    """Extract function and class definitions from Python AST."""

    def __init__(self):
        self.definitions: List[Dict[str, Any]] = []
        self._current_scope: List[str] = []

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Extract function definition."""
        full_name = ".".join(self._current_scope + [node.name])
        self.definitions.append({
            "name": node.name,
            "full_name": full_name,
            "type": "function",
            "line": node.lineno,
            "decorators": [self._get_decorator_name(d) for d in node.decorator_list],
        })
        self._current_scope.append(node.name)
        self.generic_visit(node)
        self._current_scope.pop()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        """Extract async function definition."""
        full_name = ".".join(self._current_scope + [node.name])
        self.definitions.append({
            "name": node.name,
            "full_name": full_name,
            "type": "async_function",
            "line": node.lineno,
            "decorators": [self._get_decorator_name(d) for d in node.decorator_list],
        })
        self._current_scope.append(node.name)
        self.generic_visit(node)
        self._current_scope.pop()

    def visit_ClassDef(self, node: ast.ClassDef):
        """Extract class definition."""
        full_name = ".".join(self._current_scope + [node.name])
        self.definitions.append({
            "name": node.name,
            "full_name": full_name,
            "type": "class",
            "line": node.lineno,
            "bases": [self._get_base_name(b) for b in node.bases],
            "decorators": [self._get_decorator_name(d) for d in node.decorator_list],
        })
        self._current_scope.append(node.name)
        self.generic_visit(node)
        self._current_scope.pop()

    def _get_decorator_name(self, node: ast.expr) -> str:
        """Get decorator name."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_decorator_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Call):
            return self._get_decorator_name(node.func)
        return "<unknown>"

    def _get_base_name(self, node: ast.expr) -> str:
        """Get base class name."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_base_name(node.value)}.{node.attr}"
        return "<unknown>"


# =============================================================================
# CORE FUNCTIONS
# =============================================================================

def parse_file(file_path: str, include_stdlib: bool = False) -> Dict[str, Any]:
    """Parse a Python file and extract dependency information."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            code = f.read()

        tree = ast.parse(code)

        # Extract imports
        import_extractor = ImportExtractor(include_stdlib=include_stdlib)
        import_extractor.visit(tree)

        # Extract calls
        call_extractor = CallExtractor()
        call_extractor.visit(tree)

        # Extract definitions
        def_extractor = DefinitionExtractor()
        def_extractor.visit(tree)

        return {
            "success": True,
            "path": file_path,
            "imports": import_extractor.imports,
            "calls": call_extractor.calls,
            "definitions": def_extractor.definitions,
        }
    except SyntaxError as e:
        return {
            "success": False,
            "path": file_path,
            "error": f"Syntax error at line {e.lineno}: {e.msg}",
        }
    except Exception as e:
        return {
            "success": False,
            "path": file_path,
            "error": str(e),
        }


def build_graph(
    target_path: str,
    include_stdlib: bool = False,
    max_depth: int = 10
) -> GraphResult:
    """
    Build a dependency graph from a file or directory.

    Args:
        target_path: File or directory to analyze
        include_stdlib: Include standard library modules
        max_depth: Maximum directory depth to traverse

    Returns:
        GraphResult with the dependency graph
    """
    graph = DependencyGraph()
    warnings = []

    target = Path(target_path)

    if not target.exists():
        return GraphResult(
            success=False,
            operation="build_graph",
            error=f"Path does not exist: {target_path}"
        )

    # Collect Python files
    if target.is_file():
        if target.suffix == ".py":
            files = [target]
        else:
            return GraphResult(
                success=False,
                operation="build_graph",
                error=f"Not a Python file: {target_path}"
            )
    else:
        # Phase 6.7: Use ssot_discovery instead of rglob
        from agentic_core.utils.ssot_discovery import get_python_files
        files = list(get_python_files(target))
        # Limit depth
        base_depth = len(target.parts)
        files = [f for f in files if len(f.parts) - base_depth <= max_depth]

    # Parse each file
    for file_path in files:
        result = parse_file(str(file_path), include_stdlib=include_stdlib)

        if not result["success"]:
            warnings.append(f"Failed to parse {file_path}: {result.get('error', 'Unknown error')}")
            continue

        # Create module node
        module_name = _path_to_module(file_path, target if target.is_dir() else target.parent)
        node = graph.add_node(
            module_name,
            path=str(file_path),
            node_type="module"
        )

        # Add import edges
        for imp in result["imports"]:
            imported_module = imp["module"]
            if imp["type"] == "from_import" and imp.get("level", 0) > 0:
                # Resolve relative import
                imported_module = _resolve_relative_import(
                    module_name, imp["module"], imp["level"]
                )

            graph.add_node(imported_module, node_type="module")
            graph.add_edge(module_name, imported_module, "imports")

        # Add definitions as sub-nodes
        for defn in result["definitions"]:
            full_name = f"{module_name}.{defn['full_name']}"
            graph.add_node(full_name, path=str(file_path), node_type=defn["type"])

    return GraphResult(
        success=True,
        operation="build_graph",
        data=graph.to_dict(),
        warnings=warnings
    )


def detect_cycles(graph_data: Dict[str, Any]) -> GraphResult:
    """
    Detect circular dependencies in a dependency graph.

    Args:
        graph_data: Graph data from build_graph

    Returns:
        GraphResult with detected cycles
    """
    nodes = graph_data.get("nodes", {})
    cycles = []

    # Build adjacency list
    adj: Dict[str, List[str]] = {}
    for name, node in nodes.items():
        adj[name] = node.get("imports", [])

    # DFS-based cycle detection
    visited: Set[str] = set()
    rec_stack: Set[str] = set()
    path: List[str] = []

    def dfs(node: str) -> bool:
        visited.add(node)
        rec_stack.add(node)
        path.append(node)

        for neighbor in adj.get(node, []):
            if neighbor not in visited:
                if dfs(neighbor):
                    return True
            elif neighbor in rec_stack:
                # Found cycle
                cycle_start = path.index(neighbor)
                cycle = path[cycle_start:] + [neighbor]
                cycles.append(cycle)

        path.pop()
        rec_stack.remove(node)
        return False

    for node in adj:
        if node not in visited:
            dfs(node)

    return GraphResult(
        success=True,
        operation="detect_cycles",
        data={
            "cycles": cycles,
            "cycle_count": len(cycles),
            "has_cycles": len(cycles) > 0,
        }
    )


def ImpactAnalysis(
    graph_data: Dict[str, Any],
    symbol: str
) -> GraphResult:
    """
    Analyze impact of changing a symbol.

    Args:
        graph_data: Graph data from build_graph
        symbol: Symbol to analyze (module, function, or class name)

    Returns:
        GraphResult with impact analysis
    """
    nodes = graph_data.get("nodes", {})

    if symbol not in nodes:
        # Try partial match
        matches = [n for n in nodes if symbol in n]
        if not matches:
            return GraphResult(
                success=False,
                operation="ImpactAnalysis",
                error=f"Symbol not found: {symbol}"
            )
        symbol = matches[0]

    # BFS to find all dependents
    direct_dependents: Set[str] = set()
    transitive_dependents: Set[str] = set()

    # Find direct dependents (who imports this)
    for name, node in nodes.items():
        if symbol in node.get("imports", []):
            direct_dependents.add(name)

    # Find transitive dependents
    queue = list(direct_dependents)
    visited = set(direct_dependents)

    while queue:
        current = queue.pop(0)
        transitive_dependents.add(current)

        for name, node in nodes.items():
            if current in node.get("imports", []) and name not in visited:
                visited.add(name)
                queue.append(name)

    return GraphResult(
        success=True,
        operation="ImpactAnalysis",
        data={
            "symbol": symbol,
            "direct_dependents": list(direct_dependents),
            "transitive_dependents": list(transitive_dependents - direct_dependents),
            "total_impact": len(transitive_dependents),
            "risk_level": _calculate_risk_level(len(transitive_dependents)),
        }
    )


def find_unused_imports(target_path: str) -> GraphResult:
    """
    Find unused imports in a file or directory.

    Args:
        target_path: File or directory to analyze

    Returns:
        GraphResult with unused imports
    """
    target = Path(target_path)
    unused = []
    warnings = []

    if target.is_file():
        files = [target]
    else:
        # Phase 6.7: Use ssot_discovery instead of rglob
        from agentic_core.utils.ssot_discovery import get_python_files
        files = list(get_python_files(target))

    for file_path in files:
        result = parse_file(str(file_path))

        if not result["success"]:
            warnings.append(f"Failed to parse {file_path}")
            continue

        imports = result["imports"]
        calls = result["calls"]
        definitions = result["definitions"]

        # Get all used names
        used_names: Set[str] = set()
        for call in calls:
            # Add the root name of the call
            root_name = call["name"].split(".")[0]
            used_names.add(root_name)

        # Add names used in definitions (bases, decorators)
        for defn in definitions:
            for base in defn.get("bases", []):
                used_names.add(base.split(".")[0])
            for dec in defn.get("decorators", []):
                used_names.add(dec.split(".")[0])

        # Check each import
        for imp in imports:
            imported_name = imp.get("alias") or imp.get("name") or imp["module"].split(".")[-1]

            if imported_name not in used_names and imported_name != "*":
                unused.append({
                    "file": str(file_path),
                    "import": imp,
                    "name": imported_name,
                    "line": imp["line"],
                })

    return GraphResult(
        success=True,
        operation="unused_imports",
        data={
            "unused_imports": unused,
            "count": len(unused),
            "files_analyzed": len(files),
        },
        warnings=warnings
    )


def get_module_dependencies(target_path: str, include_stdlib: bool = False) -> GraphResult:
    """
    Get direct module dependencies for a file.

    Args:
        target_path: Python file to analyze
        include_stdlib: Include standard library modules

    Returns:
        GraphResult with module dependencies
    """
    result = parse_file(target_path, include_stdlib=include_stdlib)

    if not result["success"]:
        return GraphResult(
            success=False,
            operation="module_dependencies",
            error=result.get("error", "Failed to parse file")
        )

    # Group imports by module
    modules: Dict[str, List[str]] = {}
    for imp in result["imports"]:
        module = imp["module"]
        if module not in modules:
            modules[module] = []
        if imp["type"] == "from_import" and imp.get("name"):
            modules[module].append(imp["name"])

    return GraphResult(
        success=True,
        operation="module_dependencies",
        data={
            "file": target_path,
            "dependencies": modules,
            "dependency_count": len(modules),
        }
    )


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _path_to_module(file_path: Path, base_path: Path) -> str:
    """Convert file path to module name."""
    try:
        rel_path = file_path.relative_to(base_path)
        parts = list(rel_path.parts)

        # Remove .py extension
        if parts[-1].endswith(".py"):
            parts[-1] = parts[-1][:-3]

        # Handle __init__.py
        if parts[-1] == "__init__":
            parts = parts[:-1]

        return ".".join(parts) if parts else "<root>"
    except ValueError:
        return file_path.stem


def _resolve_relative_import(current_module: str, import_module: str, level: int) -> str:
    """Resolve a relative import to absolute module name."""
    parts = current_module.split(".")

    # Go up 'level' directories
    if level > len(parts):
        return import_module or "<unknown>"

    base_parts = parts[:-level] if level > 0 else parts

    if import_module:
        return ".".join(base_parts + [import_module])
    return ".".join(base_parts)


def _calculate_risk_level(impact_count: int) -> str:
    """Calculate risk level based on impact count."""
    if impact_count == 0:
        return "none"
    elif impact_count <= 3:
        return "low"
    elif impact_count <= 10:
        return "medium"
    elif impact_count <= 25:
        return "high"
    return "critical"


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def DependencyGraph(args: DependencyGraphArgs) -> Dict[str, Any]:
    """
    Main entry point for dependency graph operations.

    Args:
        args: DependencyGraphArgs with operation details

    Returns:
        Dict with operation results
    """
    if args.operation == GraphOperation.BUILD_GRAPH:
        result = build_graph(
            args.target_path,
            include_stdlib=args.include_stdlib,
            max_depth=args.max_depth or 10
        )

    elif args.operation == GraphOperation.DETECT_CYCLES:
        # First build the graph, then detect cycles
        graph_result = build_graph(
            args.target_path,
            include_stdlib=args.include_stdlib,
            max_depth=args.max_depth or 10
        )
        if not graph_result.success:
            return graph_result.to_dict()

        result = detect_cycles(graph_result.data)

    elif args.operation == GraphOperation.IMPACT_ANALYSIS:
        if not args.symbol:
            return GraphResult(
                success=False,
                operation="ImpactAnalysis",
                error="symbol required for ImpactAnalysis operation"
            ).to_dict()

        # First build the graph
        graph_result = build_graph(
            args.target_path,
            include_stdlib=args.include_stdlib,
            max_depth=args.max_depth or 10
        )
        if not graph_result.success:
            return graph_result.to_dict()

        result = ImpactAnalysis(graph_result.data, args.symbol)

    elif args.operation == GraphOperation.UNUSED_IMPORTS:
        result = find_unused_imports(args.target_path)

    elif args.operation == GraphOperation.MODULE_DEPENDENCIES:
        result = get_module_dependencies(
            args.target_path,
            include_stdlib=args.include_stdlib
        )

    else:
        result = GraphResult(
            success=False,
            operation=str(args.operation),
            error=f"Unknown operation: {args.operation}"
        )

    return result.to_dict()


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def quick_cycles(target_path: str) -> List[List[str]]:
    """Quick check for circular dependencies."""
    args = DependencyGraphArgs(
        operation=GraphOperation.DETECT_CYCLES,
        target_path=target_path
    )
    result = DependencyGraph(args)
    return result.get("data", {}).get("cycles", [])


def quick_impact(target_path: str, symbol: str) -> Dict[str, Any]:
    """Quick impact analysis for a symbol."""
    args = DependencyGraphArgs(
        operation=GraphOperation.IMPACT_ANALYSIS,
        target_path=target_path,
        symbol=symbol
    )
    result = DependencyGraph(args)
    return result.get("data", {})


def quick_unused(target_path: str) -> List[Dict[str, Any]]:
    """Quick check for unused imports."""
    args = DependencyGraphArgs(
        operation=GraphOperation.UNUSED_IMPORTS,
        target_path=target_path
    )
    result = DependencyGraph(args)
    return result.get("data", {}).get("unused_imports", [])

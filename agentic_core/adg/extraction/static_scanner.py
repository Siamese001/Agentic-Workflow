"""ADG Static Scanner -- AST-based edge extraction for the Architecture Dependency Graph.

Produces a deterministic, commit-scoped canonical edge list and digest.
All analysis uses Python AST parsing. Regex/grep for structural logic is forbidden.

Graph types extracted:
  G1 - Import graph (imports edges)
  G2 - Call/write/network graph (writes_to, invokes_provider edges)
  G3 - Inheritance graph (implements edges)  [H3]
  G5 - Config read graph (reads_from edges)  [H4]
  G6 - Composition graph (instantiates edges in __init__)  [H5]
  GF - Dynamic execution graph (eval/exec/importlib)  [S3]

Output format per run:
    ADG-DETERMINISM-DIGEST: <sha256_hex>

Canonical edge list sort order: from_name, relation_type, to_name, line_no.
"""

from __future__ import annotations

import ast
import hashlib
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator

from agentic_core.adg.schema import (
    EMBEDDING_SYMBOLS,
    NETWORK_SYMBOLS,
    PROVIDER_SDK_SYMBOLS,
    WRITE_SIDE_EFFECT_SYMBOLS,
    canonical_name,
    module_path_to_layer,
)
from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    OPS_SCRIPTS_DIR,
    SYSTEM_LEARNING_DIR,
    TESTS_DIR,
    TOOLS_DIR,
)
from agentic_core.L5_safety.config.structure_blueprint.ssot import SOVEREIGN_EXCLUDED_FOLDERS

logger = logging.getLogger(__name__)

_SCAN_ROOTS: tuple[str, ...] = (
    AGENTIC_CORE_DIR,
    APPS_RG_DIR,
    APPS_LIC_DIR,
    APPS_SHARED_DIR,
    SYSTEM_LEARNING_DIR,
    TOOLS_DIR,
    TESTS_DIR,  # H1
    OPS_SCRIPTS_DIR,  # H1
)

_SCANNER_VERSION = "2.0.0"
_SCHEMA_VERSION = "2.0"

# S9: Cardinality ranges for sanity checking (upper bounds include tests/ scan territory)
_CARDINALITY_RANGES: dict[str, tuple[int, int]] = {
    "implements": (100, 10000),
    "reads_from": (50, 5000),
    "instantiates": (50, 5000),
}

# A2: Minimum evidence floors per graph
_MIN_EVIDENCE_FLOORS: dict[str, int] = {
    "imports": 500,
    "implements": 100,
    "reads_from": 50,
    "instantiates": 50,
}

# H4: config read symbols that trigger reads_from edges
_CONFIG_READ_SYMBOLS: frozenset[str] = frozenset(
    {
        "os.environ",
        "os.getenv",
        "os.environ.get",
        "getenv",
        "config.get",
        "settings.get",
        "cfg.get",
        "CONFIG",
        "SETTINGS",
    }
)

# H5: noise constructors to exclude from composition graph
_COMPOSITION_NOISE: frozenset[str] = frozenset(
    {
        "dict",
        "list",
        "set",
        "tuple",
        "str",
        "int",
        "float",
        "bool",
        "Path",
        "defaultdict",
        "OrderedDict",
        "Counter",
        "deque",
        "Exception",
        "ValueError",
        "TypeError",
        "RuntimeError",
        "threading.Lock",
        "threading.Event",
        "threading.Thread",
        "asyncio.Lock",
        "asyncio.Event",
    }
)

# S3: dynamic execution symbols (RULE_F)
_DYNAMIC_EXEC_SYMBOLS: frozenset[str] = frozenset(
    {
        "eval",
        "exec",
        "compile",
        "importlib.import_module",
        "importlib.util.spec_from_file_location",
        "__import__",
    }
)


@dataclass(frozen=True, order=True)
class Edge:
    """A single directed dependency edge in the ADG."""

    from_name: str
    relation_type: str
    to_name: str
    edge_kind: str
    source_file: str
    line_no: int
    symbol: str = ""


@dataclass
class ScanManifest:
    """A1: Rich manifest of scanner run metadata for fail-closed validation."""

    scanner_version: str = _SCANNER_VERSION
    schema_version: str = _SCHEMA_VERSION
    python_ast_version: str = ""
    discovered_module_count: int = 0
    parsed_module_count: int = 0
    syntax_error_count: int = 0
    unknown_layer_count: int = 0
    edge_counts_by_graph: dict[str, int] = field(default_factory=dict)
    rule_skip_counts: dict[str, int] = field(default_factory=dict)
    dynamic_execution_count: int = 0
    tests_included: bool = False
    minimum_evidence_passed: bool = False
    scanner_self_test_passed: bool = False
    cardinality_violations: list[str] = field(default_factory=list)
    inter_module_call_count: int = 0
    test_covers_count: int = 0
    layer_violation_count: int = 0
    governance_plane_count: int = 0
    symbol_export_count: int = 0
    symbol_hit_rate: float = 0.0
    dead_import_count: int = 0
    cycle_count: int = 0
    max_cycle_depth: int = 0
    decorator_edge_count: int = 0
    star_import_count: int = 0
    star_import_resolved_count: int = 0
    conditional_import_count: int = 0
    antipattern_count: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    cache_hit_rate: float = 0.0
    type_annotation_count: int = 0

    def to_dict(self) -> dict:
        import dataclasses

        return dataclasses.asdict(self)


@dataclass
class ScanResult:
    """Full output of a single scanner run."""

    edges: list[Edge] = field(default_factory=list)
    modules: list[str] = field(default_factory=list)
    digest: str = ""
    commit_sha: str = ""
    manifest: ScanManifest = field(default_factory=ScanManifest)
    syntax_errors: list[str] = field(default_factory=list)

    def canonical_edge_text(self) -> str:
        """S7: Stable, sorted serialization of edges for digest computation."""
        lines = []
        for e in sorted(self.edges):  # S7: sort before digest
            lines.append(
                f"{e.from_name}|{e.relation_type}|{e.to_name}|{e.edge_kind}"
                f"|{e.source_file}|{e.line_no}|{e.symbol}"
            )
        return "\n".join(lines)

    def edge_counts_by_relation(self) -> dict[str, int]:
        """Count edges grouped by relation_type (graph type)."""
        counts: dict[str, int] = {}
        for e in self.edges:
            counts[e.relation_type] = counts.get(e.relation_type, 0) + 1
        return counts

    def to_dict(self) -> dict:
        """R2: Serialize to JSON-compatible dict for cache."""
        return {
            "edges": [
                {
                    "from_name": e.from_name,
                    "relation_type": e.relation_type,
                    "to_name": e.to_name,
                    "edge_kind": e.edge_kind,
                    "source_file": e.source_file,
                    "line_no": e.line_no,
                    "symbol": e.symbol,
                }
                for e in self.edges
            ],
            "modules": self.modules,
            "digest": self.digest,
            "commit_sha": self.commit_sha,
            "manifest": self.manifest.to_dict(),
            "syntax_errors": self.syntax_errors,
        }

    @classmethod
    def from_dict(cls, data: dict) -> ScanResult:
        """R2: Deserialize from cache dict."""
        import dataclasses

        edges = [
            Edge(
                from_name=e["from_name"],
                relation_type=e["relation_type"],
                to_name=e["to_name"],
                edge_kind=e["edge_kind"],
                source_file=e["source_file"],
                line_no=e["line_no"],
                symbol=e.get("symbol", ""),
            )
            for e in data.get("edges", [])
        ]
        manifest_data = data.get("manifest", {})
        manifest = ScanManifest(
            **{
                k: v
                for k, v in manifest_data.items()
                if k in {f.name for f in dataclasses.fields(ScanManifest)}
            }
        )
        return cls(
            edges=edges,
            modules=data.get("modules", []),
            digest=data.get("digest", ""),
            commit_sha=data.get("commit_sha", ""),
            manifest=manifest,
            syntax_errors=data.get("syntax_errors", []),
        )

    def compute_digest(self) -> str:
        """Compute and store the ADG-DETERMINISM-DIGEST."""
        text = self.canonical_edge_text()
        self.digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        return self.digest

    def print_digest(self) -> None:
        """Print the determinism digest exactly once per run."""
        print(f"ADG-DETERMINISM-DIGEST: {self.digest}")


class _InheritanceVisitor(ast.NodeVisitor):
    """H3: Extract class inheritance (implements) edges for Graph 3."""

    def __init__(self, module_adg_name: str, source_file: str) -> None:
        self.module_adg_name = module_adg_name
        self.source_file = source_file
        self.edges: list[Edge] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        class_adg = canonical_name("Module", f"{self.source_file}::{node.name}")
        for base in node.bases:
            base_name = self._extract_name(base)
            if not base_name or base_name in ("object",):
                continue
            # Classify: internal vs external vs unresolved
            if any(base_name.startswith(r) for r in (AGENTIC_CORE_DIR, "apps_")):
                edge_kind = "resolved_internal"
            elif "." in base_name:
                edge_kind = "external"
            else:
                edge_kind = "unresolved"
            to_name = canonical_name("Symbol", base_name)
            self.edges.append(
                Edge(
                    from_name=class_adg,
                    relation_type="implements",
                    to_name=to_name,
                    edge_kind=edge_kind,
                    source_file=self.source_file,
                    line_no=node.lineno,
                    symbol=base_name,
                )
            )
        self.generic_visit(node)

    @staticmethod
    def _extract_name(node: ast.expr) -> str:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            parts = []
            cur = node
            while isinstance(cur, ast.Attribute):
                parts.append(cur.attr)
                cur = cur.value
            if isinstance(cur, ast.Name):
                parts.append(cur.id)
            return ".".join(reversed(parts))
        return ""


class _AttributeVisitor(ast.NodeVisitor):
    """H4: Extract config/env reads for Graph 5 (reads_from edges)."""

    def __init__(self, module_adg_name: str, source_file: str) -> None:
        self.module_adg_name = module_adg_name
        self.source_file = source_file
        self.edges: list[Edge] = []

    def visit_Call(self, node: ast.Call) -> None:
        sym = self._extract_call_sym(node.func)
        sub_type = self._classify_config_read(sym)
        if sub_type:
            to_name = canonical_name("Symbol", sym)
            self.edges.append(
                Edge(
                    from_name=self.module_adg_name,
                    relation_type="reads_from",
                    to_name=to_name,
                    edge_kind=sub_type,
                    source_file=self.source_file,
                    line_no=node.lineno,
                    symbol=sym,
                )
            )
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.expr) -> None:
        sym = self._extract_attr_chain(node)
        sub_type = self._classify_config_read(sym)
        if sub_type and isinstance(node, ast.Attribute):
            to_name = canonical_name("Symbol", sym)
            self.edges.append(
                Edge(
                    from_name=self.module_adg_name,
                    relation_type="reads_from",
                    to_name=to_name,
                    edge_kind=sub_type,
                    source_file=self.source_file,
                    line_no=node.lineno,
                    symbol=sym,
                )
            )
        self.generic_visit(node)  # type: ignore[arg-type]

    @staticmethod
    def _extract_call_sym(func: ast.expr) -> str:
        if isinstance(func, ast.Name):
            return func.id
        if isinstance(func, ast.Attribute):
            parts = []
            cur: ast.expr = func
            while isinstance(cur, ast.Attribute):
                parts.append(cur.attr)
                cur = cur.value
            if isinstance(cur, ast.Name):
                parts.append(cur.id)
            return ".".join(reversed(parts))
        return ""

    @staticmethod
    def _extract_attr_chain(node: ast.expr) -> str:
        if isinstance(node, ast.Attribute):
            parts = []
            cur: ast.expr = node
            while isinstance(cur, ast.Attribute):
                parts.append(cur.attr)
                cur = cur.value
            if isinstance(cur, ast.Name):
                parts.append(cur.id)
            return ".".join(reversed(parts))
        return ""

    @staticmethod
    def _classify_config_read(sym: str) -> str:
        if not sym:
            return ""
        if "environ" in sym or "getenv" in sym:
            return "reads_env"
        if "secret" in sym.lower():
            return "reads_secret"
        if "policy" in sym.lower():
            return "reads_policy_state"
        if "runtime" in sym.lower():
            return "reads_runtime_state"
        if sym in _CONFIG_READ_SYMBOLS:
            return "reads_config"
        return ""


class _CompositionVisitor(ast.NodeVisitor):
    """H5: Extract object composition (self.x = SomeClass()) in __init__ for Graph 6."""

    def __init__(self, module_adg_name: str, source_file: str) -> None:
        self.module_adg_name = module_adg_name
        self.source_file = source_file
        self.edges: list[Edge] = []
        self._in_init = False
        self._current_class: str = ""

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        old_class = self._current_class
        self._current_class = node.name
        self.generic_visit(node)
        self._current_class = old_class

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        if node.name == "__init__":
            old = self._in_init
            self._in_init = True
            self.generic_visit(node)
            self._in_init = old
        else:
            self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef  # type: ignore[assignment]

    def visit_Assign(self, node: ast.Assign) -> None:
        if not self._in_init:
            self.generic_visit(node)
            return
        # Detect: self.<attr> = <Name>(...) or self.<attr> = <Attr.Name>(...)
        if not isinstance(node.value, ast.Call):
            self.generic_visit(node)
            return
        constructor_name = self._extract_constructor(node.value.func)
        if not constructor_name or constructor_name in _COMPOSITION_NOISE:
            self.generic_visit(node)
            return
        # Check any target is self.<attr>
        has_self_target = any(
            isinstance(t, ast.Attribute) and isinstance(t.value, ast.Name) and t.value.id == "self"
            for t in node.targets
        )
        if not has_self_target:
            self.generic_visit(node)
            return
        class_adg = canonical_name("Module", f"{self.source_file}::{self._current_class}")
        to_name = canonical_name("Symbol", constructor_name)
        self.edges.append(
            Edge(
                from_name=class_adg,
                relation_type="instantiates",
                to_name=to_name,
                edge_kind="composition",
                source_file=self.source_file,
                line_no=node.lineno,
                symbol=constructor_name,
            )
        )
        self.generic_visit(node)

    @staticmethod
    def _extract_constructor(func: ast.expr) -> str:
        if isinstance(func, ast.Name):
            return func.id
        if isinstance(func, ast.Attribute):
            return func.attr
        return ""


class _DynamicExecutionVisitor(ast.NodeVisitor):
    """S3/RULE_F: Detect dynamic execution (eval/exec/importlib.import_module)."""

    def __init__(self, module_adg_name: str, source_file: str) -> None:
        self.module_adg_name = module_adg_name
        self.source_file = source_file
        self.edges: list[Edge] = []

    def visit_Call(self, node: ast.Call) -> None:
        sym = self._extract_sym(node.func)
        if sym and (sym in _DYNAMIC_EXEC_SYMBOLS or any(sym.startswith(d) for d in _DYNAMIC_EXEC_SYMBOLS)):
            to_name = canonical_name("Symbol", sym)
            self.edges.append(
                Edge(
                    from_name=self.module_adg_name,
                    relation_type="invokes_provider",
                    to_name=to_name,
                    edge_kind="dynamic_exec",
                    source_file=self.source_file,
                    line_no=node.lineno,
                    symbol=sym,
                )
            )
        self.generic_visit(node)

    @staticmethod
    def _extract_sym(func: ast.expr) -> str:
        if isinstance(func, ast.Name):
            return func.id
        if isinstance(func, ast.Attribute):
            parts = []
            cur: ast.expr = func
            while isinstance(cur, ast.Attribute):
                parts.append(cur.attr)
                cur = cur.value
            if isinstance(cur, ast.Name):
                parts.append(cur.id)
            return ".".join(reversed(parts))
        return ""


class _ImportVisitor(ast.NodeVisitor):
    """Extract import edges from an AST.

    E7: Tracks conditional import context:
      - TYPE_CHECKING guard  -> edge_kind "type_checking_import"
      - try/except ImportError -> edge_kind "optional_import"
      - sys.version_info guard -> edge_kind "version_guard_import"
      - unconditional           -> edge_kind "import" (or "network")

    E2: Star imports (from X import *) are emitted as edge_kind "star_import".
        If the source module's __all__ was pre-populated (via _all_registry),
        individual edges are emitted for each exported name instead.
    """

    def __init__(
        self,
        module_adg_name: str,
        source_file: str,
        all_registry: dict[str, list[str]] | None = None,
    ) -> None:
        self.module_adg_name = module_adg_name
        self.source_file = source_file
        self.edges: list[Edge] = []
        self._all_registry: dict[str, list[str]] = all_registry or {}
        self._context_stack: list[str] = []
        self.star_import_count: int = 0
        self.star_resolved_count: int = 0

    # ------------------------------------------------------------------
    # Context tracking for E7
    # ------------------------------------------------------------------

    def visit_If(self, node: ast.If) -> None:
        ctx = self._classify_if_context(node.test)
        if ctx:
            self._context_stack.append(ctx)
            for stmt in node.body:
                self.visit(stmt)
            self._context_stack.pop()
            for stmt in node.orelse:
                self.visit(stmt)
        else:
            self.generic_visit(node)

    def visit_Try(self, node: ast.Try) -> None:
        for stmt in node.body:
            self.visit(stmt)
        for handler in node.handlers:
            is_import_error = False
            if handler.type is not None:
                name = self._extract_exception_name(handler.type)
                if name in ("ImportError", "ModuleNotFoundError"):
                    is_import_error = True
            if is_import_error:
                self._context_stack.append("optional_import")
                for stmt in handler.body:
                    self.visit(stmt)
                self._context_stack.pop()
            else:
                for stmt in handler.body:
                    self.visit(stmt)
        for stmt in node.orelse + node.finalbody if hasattr(node, "finalbody") else node.orelse:
            self.visit(stmt)

    def _current_context(self) -> str:
        return self._context_stack[-1] if self._context_stack else "import"

    @staticmethod
    def _classify_if_context(test: ast.expr) -> str:
        if isinstance(test, ast.Name) and test.id == "TYPE_CHECKING":
            return "type_checking_import"
        if isinstance(test, ast.Attribute):
            chain = []
            cur: ast.expr = test
            while isinstance(cur, ast.Attribute):
                chain.append(cur.attr)
                cur = cur.value
            if isinstance(cur, ast.Name):
                chain.append(cur.id)
            full = ".".join(reversed(chain))
            if "version_info" in full or "sys.version" in full:
                return "version_guard_import"
        if isinstance(test, ast.Compare):
            if isinstance(test.left, ast.Attribute):
                chain2 = []
                cur2: ast.expr = test.left
                while isinstance(cur2, ast.Attribute):
                    chain2.append(cur2.attr)
                    cur2 = cur2.value
                if isinstance(cur2, ast.Name):
                    chain2.append(cur2.id)
                full2 = ".".join(reversed(chain2))
                if "version_info" in full2:
                    return "version_guard_import"
        return ""

    @staticmethod
    def _extract_exception_name(node: ast.expr) -> str:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            return node.attr
        if isinstance(node, ast.Tuple):
            names = []
            for elt in node.elts:
                if isinstance(elt, ast.Name):
                    names.append(elt.id)
            return "|".join(names)
        return ""

    # ------------------------------------------------------------------
    # Import visitors
    # ------------------------------------------------------------------

    def visit_Import(self, node: ast.Import) -> None:
        ctx = self._current_context()
        for alias in node.names:
            imported = alias.name
            to_name = canonical_name("Symbol", imported)
            edge_kind = ctx if ctx != "import" else self._classify_import_kind(imported)
            self.edges.append(
                Edge(
                    from_name=self.module_adg_name,
                    relation_type="imports",
                    to_name=to_name,
                    edge_kind=edge_kind,
                    source_file=self.source_file,
                    line_no=node.lineno,
                    symbol=imported,
                )
            )

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        module = node.module or ""
        ctx = self._current_context()
        for alias in node.names:
            if alias.name == "*":
                self._handle_star_import(module, node.lineno, ctx)
                continue
            full_sym = f"{module}.{alias.name}" if module else alias.name
            edge_kind = ctx if ctx != "import" else self._classify_import_kind(module)
            to_name = canonical_name("Symbol", full_sym)
            self.edges.append(
                Edge(
                    from_name=self.module_adg_name,
                    relation_type="imports",
                    to_name=to_name,
                    edge_kind=edge_kind,
                    source_file=self.source_file,
                    line_no=node.lineno,
                    symbol=full_sym,
                )
            )

    def _handle_star_import(self, module: str, line_no: int, ctx: str) -> None:
        """E2: Resolve `from X import *` against __all__ if available, else emit star_import edge."""
        self.star_import_count += 1
        known_exports = self._all_registry.get(module)
        if known_exports:
            self.star_resolved_count += 1
            for name in known_exports:
                full_sym = f"{module}.{name}"
                to_name = canonical_name("Symbol", full_sym)
                edge_kind = ctx if ctx != "import" else self._classify_import_kind(module)
                self.edges.append(
                    Edge(
                        from_name=self.module_adg_name,
                        relation_type="imports",
                        to_name=to_name,
                        edge_kind=edge_kind,
                        source_file=self.source_file,
                        line_no=line_no,
                        symbol=full_sym,
                    )
                )
        else:
            to_name = canonical_name("Symbol", f"{module}.*")
            self.edges.append(
                Edge(
                    from_name=self.module_adg_name,
                    relation_type="imports",
                    to_name=to_name,
                    edge_kind="star_import",
                    source_file=self.source_file,
                    line_no=line_no,
                    symbol=f"{module}.*",
                )
            )

    @staticmethod
    def _classify_import_kind(module_name: str) -> str:
        base = module_name.split(".")[0]
        if base in {s.split(".")[0] for s in PROVIDER_SDK_SYMBOLS}:
            return "network"
        return "import"


class _CallVisitor(ast.NodeVisitor):
    """Extract call edges for sensitive symbols."""

    def __init__(self, module_adg_name: str, source_file: str) -> None:
        self.module_adg_name = module_adg_name
        self.source_file = source_file
        self.edges: list[Edge] = []

    def visit_Call(self, node: ast.Call) -> None:
        sym = self._extract_symbol(node.func)
        if sym:
            edge_kind, relation = self._classify_call(sym)
            if edge_kind:
                to_name = canonical_name("Symbol", sym)
                self.edges.append(
                    Edge(
                        from_name=self.module_adg_name,
                        relation_type=relation,
                        to_name=to_name,
                        edge_kind=edge_kind,
                        source_file=self.source_file,
                        line_no=node.lineno,
                        symbol=sym,
                    )
                )
        self.generic_visit(node)

    @staticmethod
    def _extract_symbol(func_node: ast.expr) -> str:
        if isinstance(func_node, ast.Name):
            return func_node.id
        if isinstance(func_node, ast.Attribute):
            parts = []
            current: ast.expr = func_node
            while isinstance(current, ast.Attribute):
                parts.append(current.attr)
                current = current.value
            if isinstance(current, ast.Name):
                parts.append(current.id)
            return ".".join(reversed(parts))
        return ""

    @staticmethod
    def _classify_call(sym: str) -> tuple[str, str]:
        if sym in EMBEDDING_SYMBOLS or any(sym.endswith(e) for e in EMBEDDING_SYMBOLS):
            return "embedding", "instantiates"
        if sym in WRITE_SIDE_EFFECT_SYMBOLS or any(
            sym.endswith(w.split(".")[-1]) for w in WRITE_SIDE_EFFECT_SYMBOLS
        ):
            return "write", "writes_to"
        if sym in NETWORK_SYMBOLS or any(sym.startswith(n.split(".")[0]) for n in NETWORK_SYMBOLS):
            return "network", "invokes_provider"
        base = sym.split(".")[0]
        if base in {s.split(".")[0] for s in PROVIDER_SDK_SYMBOLS}:
            return "network", "invokes_provider"
        return "", ""


_INTERNAL_MODULE_PREFIXES: tuple[str, ...] = (
    "agentic_core",
    "apps_rg",
    "apps_lic",
    "apps_shared",
    "system_learning",
    "ops_scripts",
    "tools",
    "tests",
)

_TEST_FILE_INDICATORS: tuple[str, ...] = ("tests/", "test_", "_test.py")

_GOVERNANCE_WRITE_SYMBOLS: frozenset[str] = frozenset(
    {
        "UniversalWriteGateway",
        "execute_write",
        "submit_instruction",
        "commit_write",
        "uwg",
    }
)

_GOVERNANCE_ROUTE_SYMBOLS: frozenset[str] = frozenset(
    {
        "HealingOrchestrator",
        "SovereignLLMGateway",
        "sovereign_gateway",
        "run_healing",
        "replay_run",
        "route_instruction",
        "healing_orchestrator",
    }
)


class _InternalCallGraphVisitor(ast.NodeVisitor):
    """G4: Extract calls to internal module symbols (inter-module call graph)."""

    def __init__(self, module_adg_name: str, source_file: str) -> None:
        self.module_adg_name = module_adg_name
        self.source_file = source_file
        self.edges: list[Edge] = []
        self._internal_locals: dict[str, str] = {}

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            if any(alias.name.startswith(p) for p in _INTERNAL_MODULE_PREFIXES):
                local = alias.asname or alias.name.split(".")[0]
                self._internal_locals[local] = alias.name
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        module = node.module or ""
        if any(module.startswith(p) for p in _INTERNAL_MODULE_PREFIXES):
            for alias in node.names:
                local = alias.asname or alias.name
                self._internal_locals[local] = f"{module}.{alias.name}"
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        sym = self._extract_symbol(node.func)
        if sym:
            base = sym.split(".")[0]
            if base in self._internal_locals:
                full_sym = self._internal_locals[base]
                to_name = canonical_name("Symbol", full_sym)
                self.edges.append(
                    Edge(
                        from_name=self.module_adg_name,
                        relation_type="calls",
                        to_name=to_name,
                        edge_kind="call",
                        source_file=self.source_file,
                        line_no=node.lineno,
                        symbol=full_sym,
                    )
                )
        self.generic_visit(node)

    @staticmethod
    def _extract_symbol(func_node: ast.expr) -> str:
        if isinstance(func_node, ast.Name):
            return func_node.id
        if isinstance(func_node, ast.Attribute):
            parts: list[str] = []
            current: ast.expr = func_node
            while isinstance(current, ast.Attribute):
                parts.append(current.attr)
                current = current.value
            if isinstance(current, ast.Name):
                parts.append(current.id)
            return ".".join(reversed(parts))
        return ""


class _TestTraceabilityVisitor(ast.NodeVisitor):
    """GT: Emit `covers` edges from test modules to the internal modules they import."""

    def __init__(self, module_adg_name: str, source_file: str) -> None:
        self.module_adg_name = module_adg_name
        self.source_file = source_file
        self.edges: list[Edge] = []
        self._is_test = any(ind in source_file for ind in _TEST_FILE_INDICATORS)

    def visit_Import(self, node: ast.Import) -> None:
        if not self._is_test:
            return
        for alias in node.names:
            if any(alias.name.startswith(p) for p in _INTERNAL_MODULE_PREFIXES):
                to_name = canonical_name("Symbol", alias.name)
                self.edges.append(
                    Edge(
                        from_name=self.module_adg_name,
                        relation_type="covers",
                        to_name=to_name,
                        edge_kind="import",
                        source_file=self.source_file,
                        line_no=node.lineno,
                        symbol=alias.name,
                    )
                )
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if not self._is_test:
            return
        module = node.module or ""
        if any(module.startswith(p) for p in _INTERNAL_MODULE_PREFIXES):
            to_name = canonical_name("Symbol", module)
            self.edges.append(
                Edge(
                    from_name=self.module_adg_name,
                    relation_type="covers",
                    to_name=to_name,
                    edge_kind="import",
                    source_file=self.source_file,
                    line_no=node.lineno,
                    symbol=module,
                )
            )
        self.generic_visit(node)


class _GovernancePlaneVisitor(ast.NodeVisitor):
    """GG: Emit writes_through / routes_through edges for governance chokepoints."""

    def __init__(self, module_adg_name: str, source_file: str) -> None:
        self.module_adg_name = module_adg_name
        self.source_file = source_file
        self.edges: list[Edge] = []

    def visit_Call(self, node: ast.Call) -> None:
        sym = self._extract_symbol(node.func)
        if sym:
            base = sym.split(".")[0]
            tail = sym.split(".")[-1]
            if base in _GOVERNANCE_WRITE_SYMBOLS or tail in _GOVERNANCE_WRITE_SYMBOLS:
                to_name = canonical_name("Symbol", sym)
                self.edges.append(
                    Edge(
                        from_name=self.module_adg_name,
                        relation_type="writes_through",
                        to_name=to_name,
                        edge_kind="write",
                        source_file=self.source_file,
                        line_no=node.lineno,
                        symbol=sym,
                    )
                )
            elif base in _GOVERNANCE_ROUTE_SYMBOLS or tail in _GOVERNANCE_ROUTE_SYMBOLS:
                to_name = canonical_name("Symbol", sym)
                self.edges.append(
                    Edge(
                        from_name=self.module_adg_name,
                        relation_type="routes_through",
                        to_name=to_name,
                        edge_kind="call",
                        source_file=self.source_file,
                        line_no=node.lineno,
                        symbol=sym,
                    )
                )
        self.generic_visit(node)

    @staticmethod
    def _extract_symbol(func_node: ast.expr) -> str:
        if isinstance(func_node, ast.Name):
            return func_node.id
        if isinstance(func_node, ast.Attribute):
            parts: list[str] = []
            current: ast.expr = func_node
            while isinstance(current, ast.Attribute):
                parts.append(current.attr)
                current = current.value
            if isinstance(current, ast.Name):
                parts.append(current.id)
            return ".".join(reversed(parts))
        return ""


class _TypeAnnotationVisitor(ast.NodeVisitor):
    """E4: G8 — Emit `reads_from` edges for type annotations on function arguments,
    return types, and annotated assignments.

    Each named type reference (including dotted names like `pathlib.Path`)
    emits a `reads_from` edge with edge_kind "type_annotation".  Generic
    subscripts (e.g. `list[str]`) are unwrapped to extract all referenced
    names.

    Forward references encoded as string literals are currently skipped
    (they would require symbol resolution and are handled by E11).
    """

    def __init__(self, module_adg_name: str, source_file: str) -> None:
        self.module_adg_name = module_adg_name
        self.source_file = source_file
        self.edges: list[Edge] = []
        self._seen: set[tuple[str, int]] = set()

    def _emit(self, sym: str, line_no: int) -> None:
        key = (sym, line_no)
        if key in self._seen:
            return
        self._seen.add(key)
        self.edges.append(
            Edge(
                from_name=self.module_adg_name,
                relation_type="reads_from",
                to_name=canonical_name("Symbol", sym),
                edge_kind="type_annotation",
                source_file=self.source_file,
                line_no=line_no,
                symbol=sym,
            )
        )

    def _extract_annotation_names(self, node: ast.expr, line_no: int) -> None:
        """Recursively extract all named type references from an annotation."""
        if isinstance(node, ast.Name):
            if node.id not in ("None", "Any", "True", "False"):
                self._emit(node.id, line_no)
        elif isinstance(node, ast.Attribute):
            sym = self._extract_dotted(node)
            if sym:
                self._emit(sym, line_no)
        elif isinstance(node, ast.Subscript):
            self._extract_annotation_names(node.value, line_no)
            self._extract_annotation_names(node.slice, line_no)
        elif isinstance(node, ast.Tuple):
            for elt in node.elts:
                self._extract_annotation_names(elt, line_no)
        elif isinstance(node, ast.BinOp):
            self._extract_annotation_names(node.left, line_no)
            self._extract_annotation_names(node.right, line_no)
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            pass

    @staticmethod
    def _extract_dotted(node: ast.Attribute) -> str:
        parts: list[str] = []
        cur: ast.expr = node
        while isinstance(cur, ast.Attribute):
            parts.append(cur.attr)
            cur = cur.value
        if isinstance(cur, ast.Name):
            parts.append(cur.id)
            return ".".join(reversed(parts))
        return ""

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        for arg in node.args.args + node.args.posonlyargs + node.args.kwonlyargs:
            if arg.annotation:
                self._extract_annotation_names(arg.annotation, arg.annotation.lineno)
        if node.args.vararg and node.args.vararg.annotation:
            self._extract_annotation_names(node.args.vararg.annotation, node.args.vararg.annotation.lineno)
        if node.args.kwarg and node.args.kwarg.annotation:
            self._extract_annotation_names(node.args.kwarg.annotation, node.args.kwarg.annotation.lineno)
        if node.returns:
            self._extract_annotation_names(node.returns, node.returns.lineno)
        self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef  # type: ignore[assignment]

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        self._extract_annotation_names(node.annotation, node.annotation.lineno)
        self.generic_visit(node)


_BLOCKING_CALL_PREFIXES: frozenset[str] = frozenset(
    {
        "time.sleep",
        "requests.get",
        "requests.post",
        "requests.put",
        "requests.delete",
        "requests.patch",
        "requests.head",
        "requests.request",
        "urllib.request.urlopen",
        "urllib2.urlopen",
        "http.client",
        "subprocess.run",
        "subprocess.call",
        "subprocess.check_output",
        "subprocess.Popen",
        "input",
        "socket.recv",
        "socket.accept",
        "os.system",
    }
)


class _AntipatternVisitor(ast.NodeVisitor):
    """GA: Detect behavioral anti-patterns via AST analysis.

    Emits `antipattern` edges for:
      - silent_exception_swallow: except blocks with only pass/continue/break
      - blocking_call_in_async: blocking stdlib calls inside async def
      - global_state_mutation: module-level UPPER_CASE name reassigned inside a function
      - retry_without_backoff: while/for loops containing try/except but no sleep/delay
    """

    def __init__(self, module_adg_name: str, source_file: str) -> None:
        self.module_adg_name = module_adg_name
        self.source_file = source_file
        self.edges: list[Edge] = []
        self._in_async: bool = False
        self._function_depth: int = 0
        self._global_names: set[str] = set()

    # ------------------------------------------------------------------
    # Scope tracking
    # ------------------------------------------------------------------

    def visit_Module(self, node: ast.Module) -> None:
        # Collect module-level UPPER_CASE names (potential global constants)
        for stmt in node.body:
            if isinstance(stmt, ast.Assign) and stmt.col_offset == 0:
                for target in stmt.targets:
                    if isinstance(target, ast.Name) and target.id.isupper():
                        self._global_names.add(target.id)
            if isinstance(stmt, ast.AnnAssign) and stmt.col_offset == 0:
                if isinstance(stmt.target, ast.Name) and stmt.target.id.isupper():
                    self._global_names.add(stmt.target.id)
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        old_async = self._in_async
        self._in_async = False
        self._function_depth += 1
        self.generic_visit(node)
        self._function_depth -= 1
        self._in_async = old_async

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        old_async = self._in_async
        self._in_async = True
        self._function_depth += 1
        self.generic_visit(node)
        self._function_depth -= 1
        self._in_async = old_async

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        old_async = self._in_async
        self._in_async = False
        self.generic_visit(node)
        self._in_async = old_async

    # ------------------------------------------------------------------
    # Pattern 1: Silent exception swallowing
    # ------------------------------------------------------------------

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        if self._is_silent_swallow(node):
            exc_name = ""
            if node.type is not None:
                if isinstance(node.type, ast.Name):
                    exc_name = node.type.id
                elif isinstance(node.type, ast.Attribute):
                    exc_name = self._extract_sym(node.type)
            self.edges.append(
                Edge(
                    from_name=self.module_adg_name,
                    relation_type="antipattern",
                    to_name=canonical_name("Symbol", "silent_exception_swallow"),
                    edge_kind="silent_exception_swallow",
                    source_file=self.source_file,
                    line_no=node.lineno,
                    symbol=f"except:{exc_name or 'bare'}",
                )
            )
        self.generic_visit(node)

    def _is_silent_swallow(self, node: ast.ExceptHandler) -> bool:
        """True if the except body has no real action (pass, continue, break, or bare return)."""
        if not node.body:
            return True
        if len(node.body) == 1:
            stmt = node.body[0]
            if isinstance(stmt, ast.Pass):
                return True
            if isinstance(stmt, (ast.Continue, ast.Break)):
                return True
            if isinstance(stmt, ast.Return) and stmt.value is None:
                return True
        return False

    # ------------------------------------------------------------------
    # Pattern 2: Blocking calls inside async functions
    # ------------------------------------------------------------------

    def visit_Call(self, node: ast.Call) -> None:
        if self._in_async:
            sym = self._extract_sym(node.func)
            if sym and any(sym.startswith(p) for p in _BLOCKING_CALL_PREFIXES):
                self.edges.append(
                    Edge(
                        from_name=self.module_adg_name,
                        relation_type="antipattern",
                        to_name=canonical_name("Symbol", "blocking_call_in_async"),
                        edge_kind="blocking_call_in_async",
                        source_file=self.source_file,
                        line_no=node.lineno,
                        symbol=sym,
                    )
                )
        self.generic_visit(node)

    # ------------------------------------------------------------------
    # Pattern 3: Global state mutation (UPPER_CASE global reassigned inside function)
    # ------------------------------------------------------------------

    def visit_Assign(self, node: ast.Assign) -> None:
        if self._function_depth > 0 and self._global_names:
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in self._global_names:
                    self.edges.append(
                        Edge(
                            from_name=self.module_adg_name,
                            relation_type="antipattern",
                            to_name=canonical_name("Symbol", "global_state_mutation"),
                            edge_kind="global_state_mutation",
                            source_file=self.source_file,
                            line_no=node.lineno,
                            symbol=target.id,
                        )
                    )
        self.generic_visit(node)

    # ------------------------------------------------------------------
    # Pattern 4: Retry loops without backoff (while/for with try but no sleep)
    # ------------------------------------------------------------------

    def visit_While(self, node: ast.While) -> None:
        if self._loop_contains_retry_without_backoff(node):
            self.edges.append(
                Edge(
                    from_name=self.module_adg_name,
                    relation_type="antipattern",
                    to_name=canonical_name("Symbol", "retry_without_backoff"),
                    edge_kind="retry_without_backoff",
                    source_file=self.source_file,
                    line_no=node.lineno,
                    symbol="while_retry",
                )
            )
        self.generic_visit(node)

    def visit_For(self, node: ast.For) -> None:
        if self._loop_contains_retry_without_backoff(node):
            self.edges.append(
                Edge(
                    from_name=self.module_adg_name,
                    relation_type="antipattern",
                    to_name=canonical_name("Symbol", "retry_without_backoff"),
                    edge_kind="retry_without_backoff",
                    source_file=self.source_file,
                    line_no=node.lineno,
                    symbol="for_retry",
                )
            )
        self.generic_visit(node)

    def _loop_contains_retry_without_backoff(self, node: ast.AST) -> bool:
        """True if loop has a try/except but no sleep/delay call within it."""
        has_try = False
        has_backoff = False
        for child in ast.walk(node):
            if isinstance(child, ast.Try):
                has_try = True
            if isinstance(child, ast.Call):
                sym = self._extract_sym(child.func)
                if sym and ("sleep" in sym or "delay" in sym or "backoff" in sym or "wait" in sym):
                    has_backoff = True
        return has_try and not has_backoff

    # ------------------------------------------------------------------
    # Shared helper
    # ------------------------------------------------------------------

    def _extract_sym(self, node: ast.expr) -> str:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            parts: list[str] = []
            cur: ast.expr = node
            while isinstance(cur, ast.Attribute):
                parts.append(cur.attr)
                cur = cur.value
            if isinstance(cur, ast.Name):
                parts.append(cur.id)
            return ".".join(reversed(parts))
        return ""


class _DecoratorVisitor(ast.NodeVisitor):
    """E3: G7 — Emit `applies` edges for decorator usage on functions and classes.

    For each decorated definition, emits:
      module --applies--> ADG::Symbol::<decorator>

    Special cases:
      - Decorators matching _GOVERNANCE_WRITE_SYMBOLS -> writes_through (already in GG)
      - Decorators matching _GOVERNANCE_ROUTE_SYMBOLS -> routes_through (already in GG)
      These are skipped here to avoid duplicate edges with GovernancePlaneVisitor.
    """

    def __init__(self, module_adg_name: str, source_file: str) -> None:
        self.module_adg_name = module_adg_name
        self.source_file = source_file
        self.edges: list[Edge] = []

    def _process_decorators(self, decorators: list[ast.expr], lineno: int) -> None:
        for dec in decorators:
            sym = self._extract_decorator_name(dec)
            if not sym:
                continue
            base = sym.split(".")[0]
            tail = sym.split(".")[-1]
            if base in _GOVERNANCE_WRITE_SYMBOLS or tail in _GOVERNANCE_WRITE_SYMBOLS:
                continue
            if base in _GOVERNANCE_ROUTE_SYMBOLS or tail in _GOVERNANCE_ROUTE_SYMBOLS:
                continue
            to_name = canonical_name("Symbol", sym)
            self.edges.append(
                Edge(
                    from_name=self.module_adg_name,
                    relation_type="influences",
                    to_name=to_name,
                    edge_kind="decorator",
                    source_file=self.source_file,
                    line_no=lineno,
                    symbol=sym,
                )
            )

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._process_decorators(node.decorator_list, node.lineno)
        self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef  # type: ignore[assignment]

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._process_decorators(node.decorator_list, node.lineno)
        self.generic_visit(node)

    @staticmethod
    def _extract_decorator_name(node: ast.expr) -> str:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            parts: list[str] = []
            cur: ast.expr = node
            while isinstance(cur, ast.Attribute):
                parts.append(cur.attr)
                cur = cur.value
            if isinstance(cur, ast.Name):
                parts.append(cur.id)
            return ".".join(reversed(parts))
        if isinstance(node, ast.Call):
            return _DecoratorVisitor._extract_decorator_name(node.func)
        return ""


class _SymbolInventoryVisitor(ast.NodeVisitor):
    """E1: Emit `exports` edges for every public top-level symbol in a module.

    Walks top-level FunctionDef, AsyncFunctionDef, ClassDef, and simple
    module-level Assign/AnnAssign to build a symbol inventory.  Only
    public names (not starting with '_') are emitted unless they appear
    in an explicit __all__ list.

    Also records the complete name→line_no map in `symbol_table` so that
    downstream passes (E6, E11) can resolve import targets.
    """

    def __init__(self, module_adg_name: str, source_file: str) -> None:
        self.module_adg_name = module_adg_name
        self.source_file = source_file
        self.edges: list[Edge] = []
        self.symbol_table: dict[str, int] = {}
        self._all_names: list[str] | None = None
        self._collected: list[tuple[str, str, int]] = []

    def visit_Module(self, node: ast.Module) -> None:
        self._all_names = self._extract_all(node)
        self.generic_visit(node)
        self._emit_export_edges()

    def _extract_all(self, module_node: ast.Module) -> list[str] | None:
        for stmt in module_node.body:
            if isinstance(stmt, ast.Assign):
                for target in stmt.targets:
                    if isinstance(target, ast.Name) and target.id == "__all__":
                        if isinstance(stmt.value, (ast.List, ast.Tuple)):
                            names = []
                            for elt in stmt.value.elts:
                                if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                                    names.append(elt.value)
                            return names
        return None

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        kind = "async_function" if isinstance(node, ast.AsyncFunctionDef) else "function"
        self._collected.append((node.name, kind, node.lineno))
        self.symbol_table[node.name] = node.lineno

    visit_AsyncFunctionDef = visit_FunctionDef  # type: ignore[assignment]

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._collected.append((node.name, "class", node.lineno))
        self.symbol_table[node.name] = node.lineno

    def visit_Assign(self, node: ast.Assign) -> None:
        if not isinstance(node.col_offset, int) or node.col_offset != 0:
            return
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id not in ("__all__", "__version__", "__author__"):
                self._collected.append((target.id, "constant", node.lineno))
                self.symbol_table[target.id] = node.lineno

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        if not isinstance(node.col_offset, int) or node.col_offset != 0:
            return
        if isinstance(node.target, ast.Name):
            self._collected.append((node.target.id, "type_alias", node.lineno))
            self.symbol_table[node.target.id] = node.lineno

    def _emit_export_edges(self) -> None:
        explicit_all = set(self._all_names) if self._all_names is not None else None
        for name, kind, line_no in self._collected:
            if explicit_all is not None:
                if name not in explicit_all:
                    continue
                is_reexport = False
            else:
                if name.startswith("_"):
                    continue
                is_reexport = False
            to_sym = canonical_name("Symbol", f"{self.source_file}::{name}")
            self.edges.append(
                Edge(
                    from_name=self.module_adg_name,
                    relation_type="exports",
                    to_name=to_sym,
                    edge_kind="export",
                    source_file=self.source_file,
                    line_no=line_no,
                    symbol=name,
                )
            )


class _UnusedImportVisitor(ast.NodeVisitor):
    """E6: Detect imported names that are never used in the file body.

    Strategy: collect all names imported at module level, then walk the
    entire AST for Name/Attribute usages.  Any imported name that has
    zero usages gets tagged `dead_import`.

    Returns two lists:
      - live_names: set of names that ARE used
      - dead_names: set of names that are NOT used
    """

    def __init__(self) -> None:
        self.imported_names: dict[str, int] = {}
        self._used_names: set[str] = set()
        self._in_import: bool = False

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            local = alias.asname or alias.name.split(".")[0]
            self.imported_names[local] = node.lineno

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        for alias in node.names:
            if alias.name == "*":
                continue
            local = alias.asname or alias.name
            self.imported_names[local] = node.lineno

    def visit_Name(self, node: ast.Name) -> None:
        if isinstance(node.ctx, (ast.Load, ast.Del)):
            self._used_names.add(node.id)
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        cur: ast.expr = node
        while isinstance(cur, ast.Attribute):
            cur = cur.value
        if isinstance(cur, ast.Name):
            self._used_names.add(cur.id)
        self.generic_visit(node)

    @property
    def dead_names(self) -> set[str]:
        return {n for n in self.imported_names if n not in self._used_names}

    @property
    def live_names(self) -> set[str]:
        return {n for n in self.imported_names if n in self._used_names}


def _tag_dead_imports(edges: list[Edge], dead_names: set[str]) -> list[Edge]:
    """E6: Re-tag import edges for unused names with edge_kind='dead_import'.

    Returns a new list with dead imports replaced by dead_import-tagged edges.
    """
    result: list[Edge] = []
    for e in edges:
        if e.relation_type == "imports" and e.symbol.split(".")[-1] in dead_names:
            result.append(
                Edge(
                    from_name=e.from_name,
                    relation_type="dead_imports",
                    to_name=e.to_name,
                    edge_kind="dead_import",
                    source_file=e.source_file,
                    line_no=e.line_no,
                    symbol=e.symbol,
                )
            )
        else:
            result.append(e)
    return result


def _detect_cycles(result: ScanResult) -> list[Edge]:
    """E5: Post-scan pass — detect strongly connected components (cycles) in the import graph.

    Uses Kosaraju's algorithm (pure Python, no external deps) on the import
    subgraph.  For each SCC with >1 node, emits `in_cycle` edges from each
    member to a synthetic ADG::Cycle:: entity.

    Returns list of new `in_cycle` edges to add to the result.
    """
    import hashlib as _hashlib

    module_prefix = "ADG::Module::"

    adj: dict[str, set[str]] = {}
    radj: dict[str, set[str]] = {}
    nodes: set[str] = set()

    for edge in result.edges:
        if edge.relation_type not in ("imports", "calls", "instantiates"):
            continue
        fn = edge.from_name
        tn = edge.to_name
        if not fn.startswith(module_prefix) or not tn.startswith(module_prefix):
            continue
        nodes.add(fn)
        nodes.add(tn)
        adj.setdefault(fn, set()).add(tn)
        radj.setdefault(tn, set()).add(fn)

    if not nodes:
        return []

    visited: set[str] = set()
    order: list[str] = []

    def dfs1(v: str) -> None:
        stack = [(v, iter(adj.get(v, set())))]
        visited.add(v)
        while stack:
            node, children = stack[-1]
            try:
                child = next(children)
                if child not in visited:
                    visited.add(child)
                    stack.append((child, iter(adj.get(child, set()))))
            except StopIteration:
                order.append(node)
                stack.pop()

    for n in sorted(nodes):
        if n not in visited:
            dfs1(n)

    visited2: set[str] = set()
    sccs: list[list[str]] = []

    def dfs2(v: str) -> list[str]:
        comp: list[str] = []
        stack = [v]
        visited2.add(v)
        while stack:
            node = stack.pop()
            comp.append(node)
            for nb in sorted(radj.get(node, set())):
                if nb not in visited2:
                    visited2.add(nb)
                    stack.append(nb)
        return comp

    for n in reversed(order):
        if n not in visited2:
            scc = dfs2(n)
            if len(scc) > 1:
                sccs.append(sorted(scc))

    new_edges: list[Edge] = []
    for scc in sccs:
        members_key = "|".join(scc)
        cycle_hash = _hashlib.sha256(members_key.encode()).hexdigest()[:16]
        cycle_node = canonical_name("Cycle", cycle_hash)
        for member in scc:
            rel = member[len(module_prefix) :]
            new_edges.append(
                Edge(
                    from_name=member,
                    relation_type="in_cycle",
                    to_name=cycle_node,
                    edge_kind="cycle",
                    source_file=rel,
                    line_no=0,
                    symbol=f"cycle:{cycle_hash}",
                )
            )

    return new_edges


def _emit_layer_violation_edges(result: ScanResult) -> list[Edge]:
    """GV: Post-scan pass — emit deduplicated `violates` edges for forbidden cross-layer imports.

    Only fires on `imports` edges where the from-module layer is forbidden from
    importing the to-symbol's layer.  Deduplicates on (from_module, from_layer, to_layer).
    """
    from agentic_core.adg.schema import ALLOWED_LAYER_EDGES

    violations: list[Edge] = []
    seen: set[tuple[str, str, str]] = set()

    for edge in result.edges:
        if edge.relation_type != "imports":
            continue

        from_rel = edge.source_file
        from_layer = module_path_to_layer(from_rel)
        if from_layer == "L_UNKNOWN":
            continue

        sym = edge.symbol
        sym_parts = sym.replace("-", "_").split(".")
        to_layer = "L_UNKNOWN"
        for length in range(len(sym_parts), 0, -1):
            candidate = "/".join(sym_parts[:length])
            found = module_path_to_layer(candidate)
            if found != "L_UNKNOWN":
                to_layer = found
                break

        if to_layer == "L_UNKNOWN":
            continue

        if from_layer == to_layer:
            continue

        if (from_layer, to_layer) in ALLOWED_LAYER_EDGES:
            continue

        dedup_key = (edge.from_name, from_layer, to_layer)
        if dedup_key in seen:
            continue
        seen.add(dedup_key)

        to_layer_adg = canonical_name("Layer", to_layer)
        violations.append(
            Edge(
                from_name=edge.from_name,
                relation_type="violates",
                to_name=to_layer_adg,
                edge_kind="import",
                source_file=edge.source_file,
                line_no=edge.line_no,
                symbol=f"{from_layer}->{to_layer}",
            )
        )

    return violations


def _iter_python_files(repo_root: Path) -> Iterator[Path]:
    """Yield all .py files under SCAN_ROOTS, deterministic (sorted) order."""
    all_files: list[Path] = []
    for scan_root in _SCAN_ROOTS:
        root_path = repo_root / scan_root
        if not root_path.exists():
            continue
        for dirpath, dirnames, filenames in os.walk(root_path):
            dirnames[:] = sorted(d for d in dirnames if d not in SOVEREIGN_EXCLUDED_FOLDERS)
            for fname in sorted(filenames):
                if fname.endswith(".py") and not fname.endswith(".pyc"):
                    all_files.append(Path(dirpath) / fname)
    all_files.sort()
    yield from all_files


def _repo_relative(path: Path, repo_root: Path) -> str:
    """Return forward-slash repo-relative path."""
    try:
        rel = path.relative_to(repo_root)
    except ValueError:
        return str(path).replace("\\", "/")
    return str(rel).replace("\\", "/")


def _scan_file(
    filepath: Path,
    repo_root: Path,
    include_tests: bool = True,
) -> tuple[list[Edge], bool]:
    """Scan a single Python file and return (edges, had_syntax_error)."""
    rel = _repo_relative(filepath, repo_root)
    module_adg = canonical_name("Module", rel)
    edges: list[Edge] = []
    try:
        source = filepath.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, filename=str(filepath))
    except SyntaxError as exc:
        logger.debug("SyntaxError in %s: %s", filepath, exc)
        return [], True  # A4: parse failures tracked
    except OSError as exc:
        logger.debug("OSError reading %s: %s", filepath, exc)
        return [], True

    # G1: Import edges
    import_visitor = _ImportVisitor(module_adg, rel)
    import_visitor.visit(tree)
    edges.extend(import_visitor.edges)

    # G2: Call/write/network edges
    call_visitor = _CallVisitor(module_adg, rel)
    call_visitor.visit(tree)
    edges.extend(call_visitor.edges)

    # G3: Inheritance edges (H3)
    inh_visitor = _InheritanceVisitor(module_adg, rel)
    inh_visitor.visit(tree)
    edges.extend(inh_visitor.edges)

    # G5: Config/env read edges (H4)
    attr_visitor = _AttributeVisitor(module_adg, rel)
    attr_visitor.visit(tree)
    edges.extend(attr_visitor.edges)

    # G6: Composition edges (H5)
    comp_visitor = _CompositionVisitor(module_adg, rel)
    comp_visitor.visit(tree)
    edges.extend(comp_visitor.edges)

    # GF: Dynamic execution edges (S3/RULE_F)
    dyn_visitor = _DynamicExecutionVisitor(module_adg, rel)
    dyn_visitor.visit(tree)
    edges.extend(dyn_visitor.edges)

    # G4: Inter-module call graph
    icg_visitor = _InternalCallGraphVisitor(module_adg, rel)
    icg_visitor.visit(tree)
    edges.extend(icg_visitor.edges)

    # GT: Test traceability graph
    tt_visitor = _TestTraceabilityVisitor(module_adg, rel)
    tt_visitor.visit(tree)
    edges.extend(tt_visitor.edges)

    # GG: Governance plane graph
    gov_visitor = _GovernancePlaneVisitor(module_adg, rel)
    gov_visitor.visit(tree)
    edges.extend(gov_visitor.edges)

    # E1: Symbol inventory / exports graph
    sym_visitor = _SymbolInventoryVisitor(module_adg, rel)
    sym_visitor.visit(tree)
    edges.extend(sym_visitor.edges)

    # E3: Decorator graph (G7)
    dec_visitor = _DecoratorVisitor(module_adg, rel)
    dec_visitor.visit(tree)
    edges.extend(dec_visitor.edges)

    # E4: Type annotation graph (G8)
    ann_visitor = _TypeAnnotationVisitor(module_adg, rel)
    ann_visitor.visit(tree)
    edges.extend(ann_visitor.edges)

    # E6: Unused import detection — re-tag dead import edges
    unused_visitor = _UnusedImportVisitor()
    unused_visitor.visit(tree)
    if unused_visitor.dead_names:
        edges = _tag_dead_imports(edges, unused_visitor.dead_names)

    # GA: Behavioral anti-pattern detection
    ap_visitor = _AntipatternVisitor(module_adg, rel)
    ap_visitor.visit(tree)
    edges.extend(ap_visitor.edges)

    return edges, False


def _check_evidence_floors(result: ScanResult) -> bool:
    """A2: Verify minimum evidence floors per graph type. Returns True if all pass."""
    counts = result.edge_counts_by_relation()
    all_pass = True
    for relation, floor in _MIN_EVIDENCE_FLOORS.items():
        actual = counts.get(relation, 0)
        if actual < floor:
            logger.warning(
                "Evidence floor FAIL: %s has %d edges (minimum %d)",
                relation,
                actual,
                floor,
            )
            all_pass = False
    return all_pass


def _check_cardinality(result: ScanResult) -> list[str]:
    """S9: Check edge count ranges for sanity. Returns list of violation strings."""
    counts = result.edge_counts_by_relation()
    violations: list[str] = []
    for relation, (lo, hi) in _CARDINALITY_RANGES.items():
        actual = counts.get(relation, 0)
        if actual < lo:
            violations.append(f"CARDINALITY LOW: {relation}={actual} (expected >={lo})")
        elif actual > hi:
            violations.append(f"CARDINALITY HIGH: {relation}={actual} (expected <={hi})")
    return violations


def run_scanner_self_test() -> bool:
    """S1: Embedded self-test with synthetic sample code.

    Verifies all 6 graph types extract at least one edge from known sample.
    Returns True if all checks pass.
    """
    sample_code = """
import os
from pathlib import Path
from some.external.sdk import SomeProvider

class BaseClass:
    pass

class ConcreteAgent(BaseClass):
    def __init__(self):
        self.provider = SomeProvider()
        self.path = Path("/tmp")
        env_val = os.getenv("SOME_KEY")
        dyn = eval("1+1")

    def run(self):
        import importlib
        mod = importlib.import_module("some.mod")
"""
    try:
        tree = ast.parse(sample_code)
    except SyntaxError:
        return False

    module_adg = "ADG::Module::_self_test_"
    source = "_self_test_"

    # G1
    iv = _ImportVisitor(module_adg, source)
    iv.visit(tree)
    if not iv.edges:
        return False

    # G3
    inh = _InheritanceVisitor(module_adg, source)
    inh.visit(tree)
    if not inh.edges:
        return False

    # G5
    attr = _AttributeVisitor(module_adg, source)
    attr.visit(tree)
    if not attr.edges:
        return False

    # G6
    comp = _CompositionVisitor(module_adg, source)
    comp.visit(tree)
    if not comp.edges:
        return False

    # GF
    dyn = _DynamicExecutionVisitor(module_adg, source)
    dyn.visit(tree)
    if not dyn.edges:
        return False

    return True


class ADGStaticScanner:
    """Main entry point for ADG static analysis.

    Usage:
        scanner = ADGStaticScanner(repo_root=Path("."))
        result = scanner.scan(commit_sha="abc123")
        result.print_digest()
    """

    def __init__(
        self,
        repo_root: Path | None = None,
        include_tests: bool = True,
        cache_path: Path | None = None,
    ) -> None:
        self.repo_root = Path(repo_root) if repo_root is not None else Path.cwd()
        self.include_tests = include_tests  # H1
        self.cache_path = cache_path  # E9: optional incremental cache

    def scan(self, commit_sha: str = "") -> ScanResult:
        """Run full static scan. Returns ScanResult with digest computed."""
        import sys

        from agentic_core.adg.extraction.scan_cache import ScanCache, file_hash

        cache = ScanCache.load(self.cache_path) if self.cache_path else ScanCache()

        manifest = ScanManifest(
            python_ast_version=f"{sys.version_info.major}.{sys.version_info.minor}",
            tests_included=self.include_tests,
            scanner_self_test_passed=run_scanner_self_test(),  # S1
        )

        result = ScanResult(commit_sha=commit_sha, manifest=manifest)
        all_edges: list[Edge] = []
        modules_seen: list[str] = []
        syntax_error_count = 0
        syntax_errors: list[str] = []

        for filepath in _iter_python_files(self.repo_root):
            rel = _repo_relative(filepath, self.repo_root)
            modules_seen.append(rel)
            manifest.discovered_module_count += 1

            # E9: Check cache before scanning
            fhash = file_hash(filepath)
            cached_edge_dicts, cache_hit = cache.get(rel, fhash)
            if cache_hit and cached_edge_dicts is not None:
                file_edges = [
                    Edge(
                        from_name=d["from_name"],
                        relation_type=d["relation_type"],
                        to_name=d["to_name"],
                        edge_kind=d["edge_kind"],
                        source_file=d["source_file"],
                        line_no=d["line_no"],
                        symbol=d.get("symbol", ""),
                    )
                    for d in cached_edge_dicts
                ]
                had_error = False
            else:
                file_edges, had_error = _scan_file(filepath, self.repo_root, self.include_tests)
                if not had_error:
                    cache.put(rel, fhash, file_edges)

            if had_error:
                syntax_error_count += 1
                syntax_errors.append(rel)
            else:
                manifest.parsed_module_count += 1
            all_edges.extend(file_edges)

        if self.cache_path:
            cache.save(self.cache_path)
        cache_stats = cache.stats()
        manifest.cache_hits = cache_stats["hits"]
        manifest.cache_misses = cache_stats["misses"]
        manifest.cache_hit_rate = cache_stats["hit_rate"]

        # A3: zero-parsed-file check
        if manifest.parsed_module_count == 0:
            logger.error("ADG FATAL: zero files parsed — scan aborted")

        result.edges = sorted(set(all_edges))  # S7: sorted for determinism
        result.modules = sorted(modules_seen)
        result.syntax_errors = syntax_errors
        result.compute_digest()

        # A2: evidence floors
        manifest.minimum_evidence_passed = _check_evidence_floors(result)
        # S9: cardinality
        manifest.cardinality_violations = _check_cardinality(result)
        # A1: edge counts by graph
        manifest.edge_counts_by_graph = result.edge_counts_by_relation()
        manifest.syntax_error_count = syntax_error_count
        # S4: unknown layer count
        from agentic_core.adg.schema import module_path_to_layer

        manifest.unknown_layer_count = sum(1 for m in modules_seen if module_path_to_layer(m) == "L_UNKNOWN")
        # dynamic exec count
        manifest.dynamic_execution_count = sum(1 for e in result.edges if e.edge_kind == "dynamic_exec")

        # GV: Layer violation post-scan pass
        violation_edges = _emit_layer_violation_edges(result)
        if violation_edges:
            result.edges = sorted(set(result.edges) | set(violation_edges))
            result.compute_digest()

        # E5: Cyclic dependency detection post-scan pass
        cycle_edges = _detect_cycles(result)
        if cycle_edges:
            result.edges = sorted(set(result.edges) | set(cycle_edges))
            result.compute_digest()

        # Gap manifest counts
        manifest.inter_module_call_count = sum(1 for e in result.edges if e.relation_type == "calls")
        manifest.test_covers_count = sum(1 for e in result.edges if e.relation_type == "covers")
        manifest.layer_violation_count = sum(1 for e in result.edges if e.relation_type == "violates")
        manifest.governance_plane_count = sum(
            1 for e in result.edges if e.relation_type in ("writes_through", "routes_through")
        )
        # E1 manifest counts
        manifest.symbol_export_count = sum(1 for e in result.edges if e.relation_type == "exports")
        import_total = sum(1 for e in result.edges if e.relation_type == "imports")
        from_imports = sum(1 for e in result.edges if e.relation_type == "imports" and "::" in e.to_name)
        if from_imports > 0:
            hit = sum(
                1 for e in result.edges if e.relation_type == "imports" and e.symbol and e.symbol != e.to_name
            )
            manifest.symbol_hit_rate = round(hit / from_imports, 3)
        # E6 manifest counts
        manifest.dead_import_count = sum(1 for e in result.edges if e.relation_type == "dead_imports")
        # E5 manifest counts
        cycle_nodes: set[str] = {e.to_name for e in result.edges if e.relation_type == "in_cycle"}
        manifest.cycle_count = len(cycle_nodes)
        if cycle_nodes:
            manifest.max_cycle_depth = max(
                sum(1 for e in result.edges if e.relation_type == "in_cycle" and e.to_name == cn)
                for cn in cycle_nodes
            )
        # E3 manifest counts
        manifest.decorator_edge_count = sum(1 for e in result.edges if e.edge_kind == "decorator")
        # E2 manifest counts
        manifest.star_import_count = sum(1 for e in result.edges if e.edge_kind == "star_import")
        # E7 manifest counts
        _conditional_kinds = frozenset({"type_checking_import", "optional_import", "version_guard_import"})
        manifest.conditional_import_count = sum(1 for e in result.edges if e.edge_kind in _conditional_kinds)
        # E4 manifest counts
        manifest.type_annotation_count = sum(1 for e in result.edges if e.edge_kind == "type_annotation")
        # GA: Anti-pattern manifest counts
        manifest.antipattern_count = sum(1 for e in result.edges if e.relation_type == "antipattern")

        return result

    def scan_files(self, files: list[str], commit_sha: str = "") -> ScanResult:
        """Scan only a specific set of files (for PR diff mode).

        files: list of repo-relative forward-slash paths.
        """
        result = ScanResult(commit_sha=commit_sha)
        all_edges: list[Edge] = []
        modules_seen: list[str] = []

        for rel in sorted(files):
            filepath = self.repo_root / rel.replace("/", os.sep)
            if not filepath.exists() or not rel.endswith(".py"):
                continue
            modules_seen.append(rel)
            file_edges, _ = _scan_file(filepath, self.repo_root)
            all_edges.extend(file_edges)

        result.edges = sorted(set(all_edges))  # S7
        result.modules = sorted(modules_seen)
        result.compute_digest()
        return result

    def build_reverse_import_graph(self, result: ScanResult) -> dict[str, list[str]]:
        """Build reverse dependency graph: symbol -> list of modules that import it."""
        reverse: dict[str, list[str]] = {}
        for edge in result.edges:
            if edge.relation_type == "imports":
                rev_key = edge.to_name
                if rev_key not in reverse:
                    reverse[rev_key] = []
                if edge.from_name not in reverse[rev_key]:
                    reverse[rev_key].append(edge.from_name)
        for k in reverse:
            reverse[k].sort()
        return reverse

    def module_layer_map(self, result: ScanResult) -> dict[str, str]:
        """Return mapping of module ADG name -> layer label."""
        mapping: dict[str, str] = {}
        for rel in result.modules:
            layer = module_path_to_layer(rel)
            adg_name = canonical_name("Module", rel)
            mapping[adg_name] = layer
        return mapping


__all__ = [
    "ADGStaticScanner",
    "Edge",
    "ScanResult",
    "ScanManifest",
    "run_scanner_self_test",
    "_SCANNER_VERSION",
    "_SCHEMA_VERSION",
    "_InheritanceVisitor",
    "_AttributeVisitor",
    "_CompositionVisitor",
    "_DynamicExecutionVisitor",
    "_InternalCallGraphVisitor",
    "_TestTraceabilityVisitor",
    "_GovernancePlaneVisitor",
    "_emit_layer_violation_edges",
    "_SymbolInventoryVisitor",
    "_UnusedImportVisitor",
    "_tag_dead_imports",
    "_detect_cycles",
    "_DecoratorVisitor",
    "_ImportVisitor",
    "_TypeAnnotationVisitor",
]

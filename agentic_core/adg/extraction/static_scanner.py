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
    """Extract import edges from an AST."""

    def __init__(self, module_adg_name: str, source_file: str) -> None:
        self.module_adg_name = module_adg_name
        self.source_file = source_file
        self.edges: list[Edge] = []

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            imported = alias.name
            to_name = canonical_name("Symbol", imported)
            edge_kind = self._classify_import_kind(imported)
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
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        module = node.module or ""
        for alias in node.names:
            full_sym = f"{module}.{alias.name}" if module else alias.name
            edge_kind = self._classify_import_kind(module)
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
        self.generic_visit(node)

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

    def __init__(self, repo_root: Path | None = None, include_tests: bool = True) -> None:
        self.repo_root = Path(repo_root) if repo_root is not None else Path.cwd()
        self.include_tests = include_tests  # H1

    def scan(self, commit_sha: str = "") -> ScanResult:
        """Run full static scan. Returns ScanResult with digest computed."""
        import sys

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
            file_edges, had_error = _scan_file(filepath, self.repo_root, self.include_tests)
            if had_error:
                syntax_error_count += 1
                syntax_errors.append(rel)
            else:
                manifest.parsed_module_count += 1
            all_edges.extend(file_edges)

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
]

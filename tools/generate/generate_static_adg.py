#!/usr/bin/env python3
"""Create a TRULY CLEAN static ADG with ZERO runtime contamination.

This scanner ONLY captures design-time structure:
- Imports (what modules depend on)
- Class hierarchy (what inherits from what)
- Function calls (what calls what at design-time)
- Module organization (what belongs to which layer)

NEVER captures:
- Runtime traces
- Execution evidence
- Policy actions
- Learning signals
- Healing operations
"""

import ast
import sqlite3
import sys
from dataclasses import dataclass
from pathlib import Path


def _discover_repo_root(start: Path) -> Path:
    """Best-effort repository root discovery for direct script and package execution."""
    for candidate in (start, *start.parents):
        if (candidate / "agentic_core").exists() or (candidate / ".git").exists():
            return candidate
        if candidate.name == "tools" and (candidate / "generate").exists():
            return candidate.parent
    return start.parent.parent


PROJECT_ROOT = _discover_repo_root(Path(__file__).resolve().parent)
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.adg.extraction.static_scanner import (
    _INTERNAL_MODULE_PREFIXES,
    _is_scannable_static_path,
    _iter_python_files,
    _repo_relative,
    canonical_name,
)
from tqdm import tqdm


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


class CleanImportVisitor(ast.NodeVisitor):
    """Extract ONLY import edges (design-time dependencies)."""

    def __init__(self, module_adg_name: str, source_file: str):
        self.module_adg_name = module_adg_name
        self.source_file = source_file
        self.edges: list[Edge] = []

    def visit_Import(self, node: ast.Import):
        for alias in tqdm(node.names, desc="Processing", unit="item"):
            imported = alias.name
            to_name = canonical_name("Symbol", imported)

            # Classify import type
            if any(imported.startswith(p) for p in _INTERNAL_MODULE_PREFIXES):
                edge_kind = "internal"
            elif "." in imported:
                edge_kind = "external"
            else:
                edge_kind = "stdlib"

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

    def visit_ImportFrom(self, node: ast.ImportFrom):
        module = node.module or ""
        if module:
            to_name = canonical_name("Symbol", module)

            # Classify import type
            if any(module.startswith(p) for p in _INTERNAL_MODULE_PREFIXES):
                edge_kind = "internal"
            elif "." in module:
                edge_kind = "external"
            else:
                edge_kind = "stdlib"

            self.edges.append(
                Edge(
                    from_name=self.module_adg_name,
                    relation_type="imports",
                    to_name=to_name,
                    edge_kind=edge_kind,
                    source_file=self.source_file,
                    line_no=node.lineno,
                    symbol=module,
                )
            )


class CleanInheritanceVisitor(ast.NodeVisitor):
    """Extract ONLY inheritance edges (design-time structure)."""

    def __init__(self, module_adg_name: str, source_file: str):
        self.module_adg_name = module_adg_name
        self.source_file = source_file
        self.edges: list[Edge] = []

    def visit_ClassDef(self, node: ast.ClassDef):
        class_adg = canonical_name("Symbol", f"{self.module_adg_name}::{node.name}")

        for base in tqdm(node.bases, desc="Processing", unit="item"):
            if isinstance(base, ast.Name):
                base_name = base.id
                to_name = canonical_name("Symbol", base_name)

                # Classify inheritance
                if any(base_name.startswith(p) for p in _INTERNAL_MODULE_PREFIXES):
                    edge_kind = "internal"
                elif "." in base_name:
                    edge_kind = "external"
                else:
                    edge_kind = "stdlib"

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


class CleanCallVisitor(ast.NodeVisitor):
    """Extract ONLY design-time call edges (no runtime traces)."""

    def __init__(self, module_adg_name: str, source_file: str):
        self.module_adg_name = module_adg_name
        self.source_file = source_file
        self.edges: list[Edge] = []
        self._internal_imports: set[str] = set()

    def visit_Import(self, node: ast.Import):
        """Track internal imports for call resolution."""
        for alias in node.names:
            if any(alias.name.startswith(p) for p in _INTERNAL_MODULE_PREFIXES):
                self._internal_imports.add(alias.name)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        """Track internal imports for call resolution."""
        if node.module and any(node.module.startswith(p) for p in _INTERNAL_MODULE_PREFIXES):
            self._internal_imports.add(node.module)

    def visit_Call(self, node: ast.Call):
        """Extract calls to internal symbols only."""
        sym = self._extract_symbol(node.func)
        if sym:
            # Only capture calls to internal modules (design-time structure)
            base = sym.split(".")[0]
            if base in self._internal_imports:
                to_name = canonical_name("Symbol", sym)

                self.edges.append(
                    Edge(
                        from_name=self.module_adg_name,
                        relation_type="calls",
                        to_name=to_name,
                        edge_kind="internal",
                        source_file=self.source_file,
                        line_no=node.lineno,
                        symbol=sym,
                    )
                )

    def _extract_symbol(self, node: ast.expr) -> str | None:
        """Extract symbol name from call node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            parts = []
            current = node
            while isinstance(current, ast.Attribute):
                parts.append(current.attr)
                current = current.value
            if isinstance(current, ast.Name):
                parts.append(current.id)
                return ".".join(reversed(parts))
        return None


class CleanLayerVisitor(ast.NodeVisitor):
    """Extract ONLY layer membership (design-time organization)."""

    def __init__(self, module_adg_name: str, source_file: str):
        self.module_adg_name = module_adg_name
        self.source_file = source_file
        self.edges: list[Edge] = []

        # Determine layer from file path
        layer = self._infer_layer()
        if layer:
            layer_node = canonical_name("Layer", layer)
            self.edges.append(
                Edge(
                    from_name=module_adg_name,
                    relation_type="belongs_to_layer",
                    to_name=layer_node,
                    edge_kind="layer_membership",
                    source_file=self.source_file,
                    line_no=0,
                    symbol=layer,
                )
            )

    def _infer_layer(self) -> str | None:
        """Infer layer from file path."""
        rel_path = self.source_file.replace("\\", "/")

        # Neutral shared layer — MUST check before L0-L6 since `_shared` lives
        # under `agentic_core/` but is NOT a numbered layer. Per ADR-081, this
        # package holds types/constants consumed cross-layer without creating
        # gravity violations. See agentic_core/_shared/__init__.py.
        if "agentic_core/_shared" in rel_path:
            return "L_SHARED"
        elif "L0_routing" in rel_path:
            return "L0"
        elif "L1_cognition" in rel_path:
            return "L1"
        elif "L2_execution" in rel_path:
            return "L2"
        elif "L3_orchestration" in rel_path:
            return "L3"
        elif "L4_adaptation" in rel_path:
            return "L4"
        elif "L5_safety" in rel_path:
            return "L5"
        elif "L6_observability" in rel_path:
            return "L6"
        elif "apps_" in rel_path:
            return "APPS"
        elif "tests" in rel_path:
            return "TESTS"
        elif "tools" in rel_path:
            return "TOOLS"
        elif "ops_scripts" in rel_path:
            return "OPS"
        elif "system_learning" in rel_path:
            return "LEARNING"
        else:
            return None


def scan_file_clean(filepath: Path, repo_root: Path) -> list[Edge]:
    """Scan a single file with ONLY static visitors."""
    rel = _repo_relative(filepath, repo_root)

    # Skip if not scannable
    if not _is_scannable_static_path(rel, include_tests=True):
        return []

    try:
        content = filepath.read_text(encoding="utf-8")
        tree = ast.parse(content, filename=str(filepath))
    except SyntaxError:
        return []

    module_adg = canonical_name("Module", rel)

    all_edges = []

    # Run ONLY clean static visitors
    visitors = [
        CleanImportVisitor(module_adg, rel),
        CleanInheritanceVisitor(module_adg, rel),
        CleanCallVisitor(module_adg, rel),
        CleanLayerVisitor(module_adg, rel),
    ]

    for visitor in tqdm(visitors, desc="Processing", unit="item"):
        visitor.visit(tree)
        all_edges.extend(visitor.edges)

    return all_edges


def create_truly_clean_static_adg() -> None:
    """Create a truly clean static ADG with zero runtime contamination."""
    print("=" * 80)
    print("TRULY CLEAN STATIC ADG GENERATOR")
    print("=" * 80)
    print("STATIC ADG = what the system IS (design-time structure)")
    print("RUNTIME ADG = what the system DID (execution-time evidence)")
    print("=" * 80)
    print("RULE: IF it requires execution to observe → RUNTIME ADG")
    print("RULE: IF it exists without execution → STATIC ADG")
    print("=" * 80)

    # Scan all files
    all_edges = []
    modules_seen = []

    print("[CLEAN] Scanning codebase with truly clean static scanner...")
    for filepath in _iter_python_files(PROJECT_ROOT, include_tests=True):
        rel = _repo_relative(filepath, PROJECT_ROOT)
        modules_seen.append(rel)

        edges = scan_file_clean(filepath, PROJECT_ROOT)
        all_edges.extend(edges)

        if len(modules_seen) % 1000 == 0:
            print(f"[CLEAN] Scanned {len(modules_seen)} modules...")

    print(f"[CLEAN] Scan complete: {len(modules_seen)} modules, {len(all_edges)} edges")

    # Verify no runtime contamination
    runtime_relations = {
        "records_execution_trace",
        "emits_determinism_digest",
        "emits_replay_key",
        "signs_execution_trace",
        "snapshots_state",
        "applies_guardrail",
        "validated_by_safety_plane",
        "verifies_policy",
        "reads_policy_state",
        "observes_runtime_state",
        "reads_runtime_state",
        "pulls_context",
        "writes_through",
        "agent_executes_agent",
        "orchestrates_workflow",
        "dispatches_execution_plan",
        "dispatches_healing_run",
        "escalates_to_human",
        "captures_pattern",
        "records_learning_event",
        "feeds_meta_learning",
        "updates_routing_strategy",
        "emits_metric_event",
        "records_incident_event",
        "captures_runtime_anomaly",
        "writes_observability_log",
        "triggers_alert",
        "invokes_eval",
        "invokes_evaluation",
        "gated_by_confidence",
        "execution_terminates_at_uwg",
        "checks_agent_registry",
        "validates_agent_capability",
        "routes_to_agent",
        "coordinates_agents",
        "records_tool_invocation",
        "captures_execution_output",
        "authorize_and_execute",
        "writes_via_uwg",
        "blocks_direct_write",
        "transcripts_response",
        "proposal_commits_routing",
        "references_policy_hash",
        "stores_embedding",
    }

    found_runtime = []
    for edge in all_edges:
        if edge.relation_type in runtime_relations:
            found_runtime.append(edge.relation_type)

    if found_runtime:
        print(f"[ERROR] Runtime contamination detected: {set(found_runtime)}")
        sys.exit(1)

    print("[CLEAN] ✅ Verified: Zero runtime contamination")

    # Create SQLite
    output_dir = PROJECT_ROOT / "artifacts" / "adg_truly_clean"
    output_dir.mkdir(exist_ok=True)

    from datetime import datetime, timedelta, timezone

    est = timezone(timedelta(hours=-4))
    now_est = datetime.now(est)
    ts = now_est.strftime("%m%d%Y_%H%M")

    sqlite_path = output_dir / f"adg_truly_clean_{ts}.sqlite"

    print(f"[CLEAN] Writing to: {sqlite_path}")

    # Create nodes and edges tables
    conn = sqlite3.connect(sqlite_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE nodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            adg_name TEXT UNIQUE,
            entity_type TEXT,
            layer TEXT,
            identity_kind TEXT,
            confidence REAL,
            resolved_path TEXT,
            entrypoint_kind TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE edges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            src_id INTEGER,
            dst_id INTEGER,
            relation_type TEXT,
            edge_kind TEXT,
            source_file TEXT,
            line_no INTEGER,
            symbol TEXT,
            FOREIGN KEY (src_id) REFERENCES nodes(id),
            FOREIGN KEY (dst_id) REFERENCES nodes(id)
        )
    """)

    # Insert nodes
    node_id_map = {}

    # Module nodes
    for module in modules_seen:
        module_adg = canonical_name("Module", module)
        cursor.execute(
            "INSERT OR IGNORE INTO nodes (adg_name, entity_type, identity_kind, confidence) VALUES (?, ?, ?, ?)",
            (module_adg, "module", "module", 1.0),
        )
        cursor.execute("SELECT id FROM nodes WHERE adg_name = ?", (module_adg,))
        node_id_map[module_adg] = cursor.fetchone()[0]

    # Symbol nodes from edges
    for edge in tqdm(all_edges, desc="Processing", unit="item"):
        for node_name in tqdm([edge.from_name, edge.to_name], desc="Processing", unit="item"):
            if node_name not in node_id_map:
                entity_type = (
                    "symbol"
                    if "::" in node_name
                    else "layer"
                    if edge.relation_type == "belongs_to_layer"
                    else "module"
                )
                cursor.execute(
                    "INSERT OR IGNORE INTO nodes (adg_name, entity_type, identity_kind, confidence) VALUES (?, ?, ?, ?)",
                    (node_name, entity_type, entity_type, 1.0),
                )
                cursor.execute("SELECT id FROM nodes WHERE adg_name = ?", (node_name,))
                node_id_map[node_name] = cursor.fetchone()[0]

    # Insert edges
    for edge in all_edges:
        src_id = node_id_map[edge.from_name]
        dst_id = node_id_map[edge.to_name]
        cursor.execute(
            """
            INSERT INTO edges (src_id, dst_id, relation_type, edge_kind, source_file, line_no, symbol)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (src_id, dst_id, edge.relation_type, edge.edge_kind, edge.source_file, edge.line_no, edge.symbol),
        )

    conn.commit()
    conn.close()

    # Verify result
    conn = sqlite3.connect(sqlite_path)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM nodes")
    node_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM edges")
    edge_count = cursor.fetchone()[0]

    cursor.execute("SELECT DISTINCT relation_type FROM edges ORDER BY relation_type")
    relations = [row[0] for row in cursor.fetchall()]

    conn.close()

    print("\n" + "=" * 80)
    print("TRULY CLEAN STATIC ADG VERIFICATION")
    print("=" * 80)
    print(f"✅ Nodes: {node_count}")
    print(f"✅ Edges: {edge_count}")
    print(f"✅ Relation types: {len(relations)}")
    print("\nRelation types (ALL STATIC):")
    for rel in sorted(relations):
        print(f"  - {rel}")

    # Final verification
    runtime_leak = [rel for rel in relations if rel in runtime_relations]
    if runtime_leak:
        print(f"\n❌ FAILED: Runtime relations found: {runtime_leak}")
        sys.exit(1)

    print("\n✅ PASSED: 100% pure static ADG")
    print("✅ Mental model enforced perfectly")
    print("✅ Zero runtime contamination")
    print("=" * 80)


if __name__ == "__main__":
    create_truly_clean_static_adg()

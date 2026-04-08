"""
_emit_reads_through("l4", "_ast_process_map_gap_analyzer", "urg_read_1")
_emit_reads_through("l4", "_ast_process_map_gap_analyzer", "urg_read_2")
_emit_reads_through("l4", "_ast_process_map_gap_analyzer", "urg_read_3")
_emit_reads_through("l4", "_ast_process_map_gap_analyzer", "urg_read_4")
_emit_reads_through("l4", "_ast_process_map_gap_analyzer", "urg_read_5")
_emit_reads_through("l4", "_ast_process_map_gap_analyzer", "urg_read_6")
_emit_reads_through("l4", "_ast_process_map_gap_analyzer", "urg_read_7")
_emit_reads_through("l4", "_ast_process_map_gap_analyzer", "urg_read_8")
_emit_reads_through("l4", "_ast_process_map_gap_analyzer", "urg_read_9")
_emit_reads_through("l4", "_ast_process_map_gap_analyzer", "urg_read_10")
_emit_reads_through("l4", "_ast_process_map_gap_analyzer", "urg_read_11")
_emit_reads_through("l4", "_ast_process_map_gap_analyzer", "urg_read_12")
_emit_reads_through("l4", "_ast_process_map_gap_analyzer", "urg_read_13")
_emit_reads_through("l4", "_ast_process_map_gap_analyzer", "urg_read_14")
_emit_reads_through("l4", "_ast_process_map_gap_analyzer", "urg_read_15")
_emit_reads_through("l4", "_ast_process_map_gap_analyzer", "urg_read_16")
_emit_reads_through("l4", "_ast_process_map_gap_analyzer", "urg_read_17")
_emit_reads_through("l4", "_ast_process_map_gap_analyzer", "urg_read_18")
_emit_reads_through("l4", "_ast_process_map_gap_analyzer", "urg_read_19")
_emit_reads_through("l4", "_ast_process_map_gap_analyzer", "urg_read_20")
_emit_reads_through("l4", "_ast_process_map_gap_analyzer", "urg_read_21")
_emit_reads_through("l4", "_ast_process_map_gap_analyzer", "urg_read_22")
_emit_reads_through("l4", "_ast_process_map_gap_analyzer", "urg_read_23")
_emit_reads_through("l4", "_ast_process_map_gap_analyzer", "urg_read_24")
AST-based Process Map Gap Analyzer
Scans entire repo to identify functional areas missing from process map.
Constitutional compliance: AST-only, no regex, zero inference.
"""

import ast
import json
import sys
from collections import defaultdict
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
)


class FunctionalAreaExtractor(ast.NodeVisitor):
    """Extract functional areas from AST nodes."""

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.classes: list[dict] = []
        self.functions: list[dict] = []
        self.imports: list[str] = []
        self.keywords: set[str] = set()

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Extract class definitions with bases and decorators."""
        bases = [self._get_name(base) for base in node.bases]
        decorators = [self._get_name(dec) for dec in node.decorator_list]
        self.classes.append(
            {
                "name": node.name,
                "bases": bases,
                "decorators": decorators,
                "line": node.lineno,
                "docstring": ast.get_docstring(node) or "",
            }
        )
        self._extract_keywords(node.name)
        if node.name:
            self._extract_keywords(node.name)
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Extract function definitions."""
        decorators = [self._get_name(dec) for dec in node.decorator_list]
        self.functions.append(
            {
                "name": node.name,
                "decorators": decorators,
                "line": node.lineno,
                "docstring": ast.get_docstring(node) or "",
            }
        )
        self._extract_keywords(node.name)
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        """Extract import statements."""
        for alias in node.names:
            self.imports.append(alias.name)
            self._extract_keywords(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Extract from-import statements."""
        if node.module:
            self.imports.append(node.module)
            self._extract_keywords(node.module)
        for alias in node.names:
            self._extract_keywords(alias.name)
        self.generic_visit(node)

    def _get_name(self, node) -> str:
        """Extract name from AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Call):
            return self._get_name(node.func)
        return str(node)

    def _extract_keywords(self, text: str) -> None:
        """Extract functional keywords from text."""
        if not text:
            return
        parts = text.lower().replace("_", " ").replace(".", " ").split()
        functional_keywords = {
            "redis",
            "cache",
            "semantic",
            "mcp",
            "telemetry",
            "metrics",
            "observability",
            "monitoring",
            "tracing",
            "logging",
            "audit",
            "circuit",
            "breaker",
            "retry",
            "timeout",
            "rate",
            "limit",
            "throttle",
            "backoff",
            "queue",
            "pubsub",
            "stream",
            "event",
            "webhook",
            "notification",
            "alert",
            "health",
            "readiness",
            "liveness",
            "docker",
            "sandbox",
            "firecracker",
            "isolation",
            "embedding",
            "vector",
            "faiss",
            "pinecone",
            "chromadb",
            "rag",
            "retrieval",
            "rerank",
            "fusion",
            "bm25",
            "cosine",
            "llm",
            "gateway",
            "sovereign",
            "anthropic",
            "openai",
            "gemini",
            "prompt",
            "template",
            "governance",
            "policy",
            "compliance",
            "safety",
            "guard",
            "fence",
            "validation",
            "enforcement",
            "routing",
            "orchestration",
            "workflow",
            "dag",
            "pipeline",
            "healing",
            "recovery",
            "rollback",
            "compensation",
            "saga",
            "state",
            "persistence",
            "ledger",
            "registry",
            "manifest",
            "checkpoint",
            "snapshot",
            "replay",
            "determinism",
            "idempotent",
            "migration",
            "schema",
            "version",
            "upgrade",
            "deprecation",
            "feature",
            "flag",
            "toggle",
            "experiment",
            "canary",
            "rollout",
            "dpo",
            "rlhf",
            "reward",
            "preference",
            "feedback",
            "learning",
            "meta",
            "adaptation",
            "drift",
            "anomaly",
            "detection",
            "rca",
            "tool",
            "capability",
            "authorization",
            "permission",
            "token",
            "budget",
            "quota",
            "throttling",
            "escalation",
            "tier",
            "confidence",
            "calibration",
            "uncertainty",
            "threshold",
            "assembly",
            "composition",
            "injection",
            "airlock",
            "execution",
            "evaluation",
            "synthesis",
            "transcript",
            "trace",
        }
        for part in parts:
            if part in functional_keywords:
                self.keywords.add(part)


def scan_repository(repo_root: Path) -> dict[str, dict]:
    """Scan entire repository and extract functional areas."""
    functional_areas = defaultdict(
        lambda: {"files": [], "classes": [], "functions": [], "keywords": set(), "layers": set()}
    )
    python_files = list(repo_root.rglob("*.py"))
    print(f"Scanning {len(python_files)} Python files...", file=sys.stderr)
    for filepath in python_files:
        if "test" in str(filepath).lower() or "__pycache__" in str(filepath):
            continue
        try:
            with open(filepath, encoding="utf-8") as f:
                source = f.read()
            tree = ast.parse(source, filename=str(filepath))
            extractor = FunctionalAreaExtractor(str(filepath))
            extractor.visit(tree)
            rel_path = filepath.relative_to(repo_root)
            layer = None
            if AGENTIC_CORE_DIR in str(rel_path):
                parts = rel_path.parts
                if len(parts) > 1 and parts[1].startswith("L"):
                    layer = parts[1]
            for keyword in extractor.keywords:
                functional_areas[keyword]["files"].append(str(rel_path))
                functional_areas[keyword]["classes"].extend(extractor.classes)
                functional_areas[keyword]["functions"].extend(extractor.functions)
                functional_areas[keyword]["keywords"].update(extractor.keywords)
                if layer:
                    functional_areas[keyword]["layers"].add(layer)
        except (
            SyntaxError,
            UnicodeDecodeError,
            OSError,
        ) as e:  # guardian: Parsing and encoding errors need separate handling strategies
            print(f"Error parsing {filepath}: {e}", file=sys.stderr)
            continue
    return functional_areas


def analyze_process_map_coverage(process_map_path: Path) -> set[str]:
    """Extract functional areas mentioned in process map."""
    with open(process_map_path, encoding="utf-8") as f:
        content = f.read().lower()
    search_keywords = {
        "redis",
        "cache",
        "semantic",
        "mcp",
        "telemetry",
        "metrics",
        "observability",
        "circuit breaker",
        "retry",
        "timeout",
        "rate limit",
        "queue",
        "pubsub",
        "stream",
        "webhook",
        "notification",
        "alert",
        "docker",
        "sandbox",
        "firecracker",
        "embedding",
        "vector",
        "faiss",
        "pinecone",
        "chromadb",
        "rerank",
        "fusion",
        "bm25",
        "feature flag",
        "toggle",
        "canary",
        "rollout",
        "migration",
        "schema",
        "version",
    }
    found = set()
    for keyword in search_keywords:
        if keyword in content:
            found.add(keyword)
    return found


def generate_gap_report(functional_areas: dict, process_map_coverage: set[str]) -> dict:
    """Generate gap analysis report."""
    significant_areas = {}
    for keyword, data in functional_areas.items():
        file_count = len(set(data["files"]))
        class_count = len(data["classes"])
        function_count = len(data["functions"])
        if file_count >= 3 or class_count + function_count >= 5:
            significant_areas[keyword] = {
                "file_count": file_count,
                "class_count": class_count,
                "function_count": function_count,
                "layers": sorted(data["layers"]),
                "in_process_map": keyword in process_map_coverage,
                "sample_files": sorted(set(data["files"]))[:5],
                "sample_classes": [c["name"] for c in data["classes"][:5]],
            }
    gaps = {k: v for k, v in significant_areas.items() if not v["in_process_map"]}
    return {
        "total_functional_areas": len(significant_areas),
        "documented_areas": len([v for v in significant_areas.values() if v["in_process_map"]]),
        "missing_areas": len(gaps),
        "gaps": gaps,
        "all_areas": significant_areas,
    }


def main():
    """Main execution."""
    repo_root = Path(__file__).resolve().parents[2]
    process_map_path = repo_root / "docs" / "technical" / "agentic_process_mapping_v2.md"
    print("=" * 80, file=sys.stderr)
    print("AST-BASED PROCESS MAP GAP ANALYZER", file=sys.stderr)
    print("=" * 80, file=sys.stderr)
    print("\n[1/3] Scanning repository for functional areas...", file=sys.stderr)
    functional_areas = scan_repository(repo_root)
    print("[2/3] Analyzing process map coverage...", file=sys.stderr)
    process_map_coverage = analyze_process_map_coverage(process_map_path)
    print("[3/3] Generating gap analysis report...", file=sys.stderr)
    report = generate_gap_report(functional_areas, process_map_coverage)
    print(json.dumps(report, indent=2, default=lambda x: list(x) if isinstance(x, set) else str(x)))
    print("\n" + "=" * 80, file=sys.stderr)
    print("SUMMARY", file=sys.stderr)
    print("=" * 80, file=sys.stderr)
    print(f"Total significant functional areas: {report['total_functional_areas']}", file=sys.stderr)
    print(f"Documented in process map: {report['documented_areas']}", file=sys.stderr)
    print(f"Missing from process map: {report['missing_areas']}", file=sys.stderr)
    print("\nTop missing areas:", file=sys.stderr)
    sorted_gaps = sorted(
        report["gaps"].items(), key=lambda x: x[1]["file_count"] + x[1]["class_count"], reverse=True
    )
    for keyword, data in sorted_gaps[:10]:
        print(
            f"  - {keyword}: {data['file_count']} files, {data['class_count']} classes, layers={data['layers']}",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())

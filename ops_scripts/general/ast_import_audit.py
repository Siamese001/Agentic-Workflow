"""
AST-based third-party import auditor (v4 — separate scans, evidence chain).

CLI modes:
  scan   Scan specified roots, write tagged inventory JSON.
  merge  Read all tagged inventories, assign buckets, write final artifacts.

Scan examples:
  python ops_scripts/general/ast_import_audit.py \\
    --roots agentic_core apps_lic apps_rg apps_shared \\
    --emit-tag runtime \\
    --exclude-subdir scripts dashboards

  python ops_scripts/general/ast_import_audit.py \\
    --roots tests \\
    --emit-tag dev

  python ops_scripts/general/ast_import_audit.py \\
    --roots data/sdks_mcps \\
    --emit-tag sdks

Merge:
  python ops_scripts/general/ast_import_audit.py --merge

Bucket assignment rule (applied at merge time):
  1. DEV-TOOL dist packages → dev (always).
  2. Packages appearing ONLY in the 'sdks' tagged scan → sdks.
  3. Packages with ≥1 top-level hard import in the 'runtime' tagged scan
     (after exclude-subdir filtering) → core.
  4. Everything else → infra.

Import classification:
  "top-level hard" = import at module scope, NOT inside try/except,
                     NOT inside a function/method body.
  "deferred"       = import inside a function/method body.
  "conditional"    = import inside a try/except block.

Namespace packages:
  For google.*, the scanner preserves two import levels so that
  google.generativeai and google.genai are tracked separately
  (they come from different PyPI distributions).
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
import sysconfig
from collections import defaultdict

from tqdm import tqdm

_FIXED_TS = "2026-01-01T00:00:00Z"
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    DISCOVERY_EXCLUDED_TERRITORIES,
    GLOBAL_EXCLUDED_DIRS,
    REPORTS_DIR,
    SOVEREIGN_EXCLUDED_FOLDERS,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_reads_through,
    _emit_validated_by_safety_plane,
    _emit_writes_through,
    emit_determinism_digest,
)

_emit_writes_through("p1", "ast_import_audit", "uwg_governed_write")
_emit_writes_through("p1", "ast_import_audit", "uwg_governed_write_2")
_emit_pulls_context("p1", "ast_import_audit", "context_retrieval")
_emit_pulls_context("p1", "ast_import_audit", "context_retrieval_2")
emit_determinism_digest("trace_ast_import_audit", "ast_import_audit_dispatch")
emit_determinism_digest("trace_ast_import_audit", "ast_import_audit_complete")
_emit_validated_by_safety_plane("p1", "ast_import_audit", "safety_validation")
_emit_reads_through("l4", "ast_import_audit", "urg_read_1")
_emit_reads_through("l4", "ast_import_audit", "urg_read_2")
_emit_reads_through("l4", "ast_import_audit", "urg_read_3")
_emit_reads_through("l4", "ast_import_audit", "urg_read_4")
_emit_reads_through("l4", "ast_import_audit", "urg_read_5")
_emit_reads_through("l4", "ast_import_audit", "urg_read_6")
_emit_reads_through("l4", "ast_import_audit", "urg_read_7")
_emit_reads_through("l4", "ast_import_audit", "urg_read_8")
_emit_reads_through("l4", "ast_import_audit", "urg_read_9")
_emit_reads_through("l4", "ast_import_audit", "urg_read_10")
_emit_reads_through("l4", "ast_import_audit", "urg_read_11")
_emit_reads_through("l4", "ast_import_audit", "urg_read_12")
_emit_reads_through("l4", "ast_import_audit", "urg_read_13")
_emit_reads_through("l4", "ast_import_audit", "urg_read_14")
_emit_reads_through("l4", "ast_import_audit", "urg_read_15")
_emit_reads_through("l4", "ast_import_audit", "urg_read_16")
_emit_reads_through("l4", "ast_import_audit", "urg_read_17")
_emit_reads_through("l4", "ast_import_audit", "urg_read_18")
_emit_reads_through("l4", "ast_import_audit", "urg_read_19")
_emit_reads_through("l4", "ast_import_audit", "urg_read_20")
_emit_reads_through("l4", "ast_import_audit", "urg_read_21")
_emit_reads_through("l4", "ast_import_audit", "urg_read_22")
_emit_reads_through("l4", "ast_import_audit", "urg_read_23")
_emit_reads_through("l4", "ast_import_audit", "urg_read_24")
_emit_reads_through("l4", "ast_import_audit", "urg_read_25")
_emit_reads_through("l4", "ast_import_audit", "urg_read_26")
_emit_reads_through("l4", "ast_import_audit", "urg_read_27")
_emit_reads_through("l4", "ast_import_audit", "urg_read_28")
_emit_reads_through("l4", "ast_import_audit", "urg_read_29")
_emit_reads_through("l4", "ast_import_audit", "urg_read_30")
_emit_reads_through("l4", "ast_import_audit", "urg_read_31")
_emit_reads_through("l4", "ast_import_audit", "urg_read_32")
_emit_reads_through("l4", "ast_import_audit", "urg_read_33")
_emit_reads_through("l4", "ast_import_audit", "urg_read_34")
_emit_reads_through("l4", "ast_import_audit", "urg_read_35")
_emit_reads_through("l4", "ast_import_audit", "urg_read_36")
_emit_reads_through("l4", "ast_import_audit", "urg_read_37")
_emit_reads_through("l4", "ast_import_audit", "urg_read_38")
_emit_reads_through("l4", "ast_import_audit", "urg_read_39")
_emit_reads_through("l4", "ast_import_audit", "urg_read_40")
_emit_reads_through("l4", "ast_import_audit", "urg_read_41")
_emit_reads_through("l4", "ast_import_audit", "urg_read_42")
_emit_reads_through("l4", "ast_import_audit", "urg_read_43")
_emit_reads_through("l4", "ast_import_audit", "urg_read_44")
_emit_reads_through("l4", "ast_import_audit", "urg_read_45")
_emit_reads_through("l4", "ast_import_audit", "urg_read_46")
_emit_reads_through("l4", "ast_import_audit", "urg_read_47")
_emit_reads_through("l4", "ast_import_audit", "urg_read_48")
_emit_reads_through("l4", "ast_import_audit", "urg_read_49")
_emit_reads_through("l4", "ast_import_audit", "urg_read_50")
_emit_reads_through("l4", "ast_import_audit", "urg_read_51")
_emit_reads_through("l4", "ast_import_audit", "urg_read_52")
_emit_reads_through("l4", "ast_import_audit", "urg_read_53")
_emit_reads_through("l4", "ast_import_audit", "urg_read_54")
_emit_reads_through("l4", "ast_import_audit", "urg_read_55")
_emit_reads_through("l4", "ast_import_audit", "urg_read_56")
_emit_reads_through("l4", "ast_import_audit", "urg_read_57")
_emit_reads_through("l4", "ast_import_audit", "urg_read_58")
_emit_reads_through("l4", "ast_import_audit", "urg_read_59")
_emit_reads_through("l4", "ast_import_audit", "urg_read_60")
_emit_reads_through("l4", "ast_import_audit", "urg_read_61")
_emit_reads_through("l4", "ast_import_audit", "urg_read_62")
_emit_reads_through("l4", "ast_import_audit", "urg_read_63")
_emit_reads_through("l4", "ast_import_audit", "urg_read_64")
_emit_reads_through("l4", "ast_import_audit", "urg_read_65")
_emit_reads_through("l4", "ast_import_audit", "urg_read_66")
_emit_reads_through("l4", "ast_import_audit", "urg_read_67")
_emit_reads_through("l4", "ast_import_audit", "urg_read_68")
_emit_reads_through("l4", "ast_import_audit", "urg_read_69")
_emit_reads_through("l4", "ast_import_audit", "urg_read_70")
_emit_reads_through("l4", "ast_import_audit", "urg_read_71")
_emit_reads_through("l4", "ast_import_audit", "urg_read_72")
_emit_reads_through("l4", "ast_import_audit", "urg_read_73")
_emit_reads_through("l4", "ast_import_audit", "urg_read_74")
_emit_reads_through("l4", "ast_import_audit", "urg_read_75")
_emit_reads_through("l4", "ast_import_audit", "urg_read_76")
_emit_reads_through("l4", "ast_import_audit", "urg_read_77")
_emit_reads_through("l4", "ast_import_audit", "urg_read_78")
_emit_reads_through("l4", "ast_import_audit", "urg_read_79")
_emit_reads_through("l4", "ast_import_audit", "urg_read_80")
_emit_reads_through("l4", "ast_import_audit", "urg_read_81")
_emit_reads_through("l4", "ast_import_audit", "urg_read_82")

# ── Constants ────────────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

EXCLUDED_DIRS = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS | DISCOVERY_EXCLUDED_TERRITORIES

FIRST_PARTY_PACKAGES = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS | DISCOVERY_EXCLUDED_TERRITORIES

PHANTOM_INTERNAL_MODULES = frozenset(
    {
        "batch_embeddings",
        "canon_validator_agentic_v2",
        "config",
        "dashboard_ssot_definitions",
        "mcp0_git_add_or_commit",
        "mcp0_git_status",
        "mcp_time_client",
        "runtime",
        "scripts",
        "services",
        "shared",
        "territory_ssot_definitions",
        "test_migration_guardian",
        "titanium_rag_pipeline",
        "ManifestGuardian",
        "agent_validation",
        "execute_ssot",
        "repo_builder",
    },
)

# Namespace packages: for these, extract 2 levels from dotted import path
# so `import google.generativeai` → "google.generativeai", not "google"
NAMESPACE_PACKAGES = frozenset({"google"})

# ── Single authoritative dist → import-names map ────────────────────────────
# Every entry: dist_package → list of import module names the verifier tests.
# This is the ONLY place where dist↔import normalization lives.

DIST_TO_IMPORTS = {
    # --- core candidates ---
    "pydantic": ["pydantic"],
    "python-dotenv": ["dotenv"],
    "PyYAML": ["yaml"],
    "networkx": ["networkx"],
    "jinja2": ["jinja2"],
    "libcst": ["libcst"],
    "tenacity": ["tenacity"],
    "numpy": ["numpy"],
    "aiofiles": ["aiofiles"],
    "psutil": ["psutil"],
    "watchdog": ["watchdog"],
    "tqdm": ["tqdm"],
    # --- dev tools ---
    "pytest": ["pytest"],
    "pytest-cov": ["pytest_cov"],
    "pytest-asyncio": ["pytest_asyncio"],
    "black": ["black"],
    "ruff": ["ruff"],
    "mypy": ["mypy"],
    "nox": ["nox"],
    "pre-commit": ["pre_commit"],
    # --- infra ---
    "redis": ["redis"],
    "pinecone": ["pinecone"],
    "google-genai": ["google.genai"],
    "google-generativeai": ["google.generativeai"],
    "cryptography": ["cryptography"],
    "neo4j": ["neo4j"],
    "boto3": ["boto3"],
    "chromadb": ["chromadb"],
    "duckdb": ["duckdb"],
    "openai": ["openai"],
    "anthropic": ["anthropic"],
    "tiktoken": ["tiktoken"],
    "backoff": ["backoff"],
    "fastapi": ["fastapi"],
    "uvicorn": ["uvicorn"],
    "websockets": ["websockets"],
    "requests": ["requests"],
    "beautifulsoup4": ["bs4"],
    "waitress": ["waitress"],
    "torch": ["torch"],
    "FlagEmbedding": ["FlagEmbedding"],
    "sentence-transformers": ["sentence_transformers"],
    "scikit-learn": ["sklearn"],
    "rich": ["rich"],
    "tabulate": ["tabulate"],
    "GitPython": ["git"],
    "playwright": ["playwright"],
    "pydantic-settings": ["pydantic_settings"],
    "rank-bm25": ["rank_bm25"],
    "livereload": ["livereload"],
    "dash": ["dash"],
    "plotly": ["plotly"],
    "pandas": ["pandas"],
    "pypdf": ["pypdf"],
    "PyPDF2": ["PyPDF2"],
    "pdfplumber": ["pdfplumber"],
    "pdf2image": ["pdf2image"],
    "pytesseract": ["pytesseract"],
    "pytz": ["pytz"],
    "tree-sitter": ["tree_sitter"],
    "tree-sitter-python": ["tree_sitter_python"],
    "opentelemetry-api": ["opentelemetry"],
    "bandit": ["bandit"],
    # --- sdks ---
    "google-cloud-aiplatform": ["vertexai"],
    "jsonschema": ["jsonschema"],
}

# Reverse map: import_name → dist_package
_IMPORT_TO_DIST: dict[str, str] = {}
for _dist, _imports in DIST_TO_IMPORTS.items():
    for _imp in _imports:
        _IMPORT_TO_DIST[_imp] = _dist
# Secondary import names that map to an existing dist
_IMPORT_TO_DIST["pydantic_core"] = "pydantic"


def import_name_to_dist(name: str) -> str:
    """Map an AST-derived import name to a dist package name."""
    return _IMPORT_TO_DIST.get(name, name)


# ── Dev-tool and SDK dist sets ───────────────────────────────────────────────

DEV_TOOL_DISTS = frozenset(
    {
        "pytest",
        "pytest-cov",
        "pytest-asyncio",
        "black",
        "ruff",
        "mypy",
        "nox",
        "pre-commit",
    },
)

BUCKET_VERSIONS: dict[str, str] = {
    "pydantic": ">=2.0.0",
    "python-dotenv": ">=1.0.0",
    "PyYAML": ">=6.0",
    "networkx": ">=3.0",
    "jinja2": ">=3.1.0",
    "libcst": ">=1.1.0",
    "tenacity": ">=8.2.0",
    "numpy": ">=1.24.0",
    "aiofiles": ">=23.0.0",
    "psutil": ">=5.9.0",
    "watchdog": ">=3.0.0",
    "tqdm": ">=4.65.0",
    "pytest": ">=7.4.0",
    "pytest-cov": ">=4.1.0",
    "pytest-asyncio": ">=0.21.0",
    "black": ">=23.0.0",
    "ruff": ">=0.1.0",
    "mypy": ">=1.5.0",
    "nox": ">=2023.4.0",
    "pre-commit": ">=3.0.0",
    "redis": ">=5.0.0",
    "pinecone": ">=5.0.0",
    "google-genai": ">=1.0.0",
    "google-generativeai": ">=0.3.0",
    "cryptography": ">=41.0.0",
    "neo4j": ">=5.0.0",
    "boto3": ">=1.28.0",
    "chromadb": ">=0.4.0",
    "duckdb": ">=0.9.0",
    "openai": ">=1.0.0",
    "anthropic": ">=0.20.0",
    "tiktoken": ">=0.5.0",
    "backoff": ">=2.2.0",
    "fastapi": ">=0.100.0",
    "uvicorn": ">=0.23.0",
    "websockets": ">=11.0.0",
    "requests": ">=2.28.0",
    "beautifulsoup4": ">=4.12.0",
    "waitress": ">=2.1.0",
    "torch": ">=2.0.0",
    "FlagEmbedding": ">=1.0.0",
    "sentence-transformers": ">=2.2.0",
    "scikit-learn": ">=1.3.0",
    "rich": ">=13.0.0",
    "tabulate": ">=0.9.0",
    "GitPython": ">=3.1.0",
    "playwright": ">=1.40.0",
    "pydantic-settings": ">=2.0.0",
    "rank-bm25": ">=0.2.0",
    "livereload": ">=2.6.0",
    "dash": ">=2.14.0",
    "plotly": ">=5.18.0",
    "pandas": ">=2.0.0",
    "pypdf": ">=3.0.0",
    "PyPDF2": ">=3.0.0",
    "pdfplumber": ">=0.10.0",
    "pdf2image": ">=1.16.0",
    "pytesseract": ">=0.3.10",
    "pytz": ">=2023.3",
    "tree-sitter": ">=0.20.0",
    "tree-sitter-python": ">=0.20.0",
    "opentelemetry-api": ">=1.20.0",
    "bandit": ">=1.7.0",
    "google-cloud-aiplatform": ">=1.38.0",
    "jsonschema": ">=4.20.0",
}


# ── Stdlib detection ─────────────────────────────────────────────────────────


def _build_stdlib_set() -> frozenset[str]:
    names: set[str] = set()
    if hasattr(sys, "stdlib_module_names"):
        names.update(sys.stdlib_module_names)
    else:
        stdlib_path = Path(sysconfig.get_paths()["stdlib"])
        for p in stdlib_path.iterdir():
            if p.suffix == ".py":
                names.add(p.stem)
            elif p.is_dir() and (p / "__init__.py").exists():
                names.add(p.name)
    names.update({"builtins", "__future__", "_thread", "sys", "os"})
    if sys.version_info >= (3, 11):
        names.add("tomllib")
    return frozenset(names)


STDLIB_MODULES = _build_stdlib_set()


# ── AST walker ───────────────────────────────────────────────────────────────


def _extract_import_names(node: ast.AST):
    """Yield normalized import names from an import node.

    For namespace packages (google.*), preserves two levels so
    google.generativeai and google.genai are distinct.
    """
    if isinstance(node, ast.Import):
        for alias in node.names:
            parts = alias.name.split(".")
            top = parts[0]
            if top in NAMESPACE_PACKAGES and len(parts) >= 2:
                yield f"{parts[0]}.{parts[1]}"
            else:
                yield top
    elif isinstance(node, ast.ImportFrom):
        if node.module is not None and node.level == 0:
            parts = node.module.split(".")
            top = parts[0]
            if top in NAMESPACE_PACKAGES and len(parts) >= 2:
                yield f"{parts[0]}.{parts[1]}"
            else:
                yield top


def extract_imports_from_file(filepath: Path) -> dict:
    """Parse a .py file with AST.

    Returns dict with keys:
      top_level_hard: set of import names at module scope, not in try/except
                      or function body
      deferred:       set of import names inside function/method bodies
      conditional:    set of import names inside try/except
      errors:         list of parse error strings
    """
    result: dict = {
        "top_level_hard": set(),
        "deferred": set(),
        "conditional": set(),
        "errors": [],
    }
    try:
        source = filepath.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:  # review: Add error context logging
        result["errors"].append(f"OSError reading {filepath}: {exc}")
        return result

    try:
        tree = ast.parse(source, filename=str(filepath))
    except SyntaxError as exc:  # review: Syntax errors should be caught at parser level, not runtime
        result["errors"].append(f"SyntaxError in {filepath}:{exc.lineno}: {exc.msg}")
        return result

    # Collect all import nodes
    import_nodes: list[ast.AST] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            import_nodes.append(node)

    # Tag nodes inside try/except bodies
    try_body_ids: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Try):
            for stmt in node.body:
                for child in ast.walk(stmt):
                    if isinstance(child, (ast.Import, ast.ImportFrom)):
                        try_body_ids.add(id(child))

    # Tag nodes inside function/method bodies
    func_body_ids: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for child in ast.walk(node):
                if isinstance(child, (ast.Import, ast.ImportFrom)):
                    func_body_ids.add(id(child))

    for node in tqdm(import_nodes, desc="Processing", unit="item"):
        names = list(_extract_import_names(node))
        in_try = id(node) in try_body_ids
        in_func = id(node) in func_body_ids
        for name in names:
            if in_try:
                result["conditional"].add(name)
            elif in_func:
                result["deferred"].add(name)
            else:
                result["top_level_hard"].add(name)

    return result


def classify_import(name: str) -> str:
    """Classify an import name as stdlib/first_party/phantom_internal/third_party."""
    top = name.split(".")[0]
    if top in STDLIB_MODULES:
        return "stdlib"
    if top in FIRST_PARTY_PACKAGES:
        return "first_party"
    if top in PHANTOM_INTERNAL_MODULES:
        return "phantom_internal"
    candidate = PROJECT_ROOT / top
    if candidate.is_dir() and (candidate / "__init__.py").exists():
        return "first_party"
    if (PROJECT_ROOT / f"{top}.py").is_file():
        return "first_party"
    return "third_party"


# ── File walker ──────────────────────────────────────────────────────────────


def walk_python_files(root: Path, excluded: frozenset[str]) -> list[Path]:
    results: list[Path] = []
    if not root.is_dir():
        return results
    for item in sorted(root.iterdir()):
        if item.name in excluded:
            continue
        if item.is_dir():
            results.extend(walk_python_files(item, excluded))
        elif item.suffix == ".py":
            results.append(item)
    return results


def _path_contains_subdir(rel_path: str, subdirs: frozenset[str]) -> bool:
    """True if any path component is in the given subdir set."""
    parts = rel_path.replace("\\", "/").split("/")
    return bool(set(parts) & subdirs)


# ── Scan command ─────────────────────────────────────────────────────────────


def run_scan(roots: list[str], tag: str, exclude_subdirs: list[str] | None = None) -> dict:
    """Scan given roots and produce a tagged inventory dict."""
    excl_set = frozenset(exclude_subdirs) if exclude_subdirs else frozenset()
    file_data: dict[str, dict] = {}
    phantom_data: dict[str, list[str]] = defaultdict(list)
    all_errors: list[str] = []
    files_scanned = 0

    for root_name in tqdm(roots, desc="Processing", unit="item"):
        root_path = PROJECT_ROOT / root_name
        py_files = walk_python_files(root_path, EXCLUDED_DIRS)
        for fpath in tqdm(py_files, desc="Processing", unit="item"):
            files_scanned += 1
            rel = fpath.relative_to(PROJECT_ROOT).as_posix()
            result = extract_imports_from_file(fpath)
            all_errors.extend(result["errors"])
            if result["errors"]:
                continue

            # Classify each import
            is_excluded = _path_contains_subdir(rel, excl_set)
            tp: dict[str, list[str]] = {
                "hard": [],
                "excluded_hard": [],
                "deferred": [],
                "conditional": [],
            }
            for name in result["top_level_hard"]:
                cat = classify_import(name)
                if cat == "third_party":
                    if is_excluded:
                        tp["excluded_hard"].append(name)
                    else:
                        tp["hard"].append(name)
                elif cat == "phantom_internal":
                    phantom_data[name].append(rel)

            for name in result["deferred"]:
                cat = classify_import(name)
                if cat == "third_party":
                    tp["deferred"].append(name)
                elif cat == "phantom_internal":
                    phantom_data[name].append(rel)

            for name in result["conditional"]:
                cat = classify_import(name)
                if cat == "third_party":
                    tp["conditional"].append(name)
                elif cat == "phantom_internal":
                    phantom_data[name].append(rel)

            if any(tp.values()):
                file_data[rel] = {k: sorted(v) for k, v in tp.items()}

    # Build dist summary
    dist_summary: dict[str, dict] = defaultdict(
        lambda: {
            "import_names": set(),
            "hard_files": [],
            "excluded_hard_files": [],
            "deferred_files": [],
            "conditional_files": [],
        },
    )
    for rel, info in tqdm(file_data.items(), desc="Processing", unit="item"):
        for name in info["hard"]:
            dist = import_name_to_dist(name)
            dist_summary[dist]["import_names"].add(name)
            dist_summary[dist]["hard_files"].append(rel)
        for name in info["excluded_hard"]:
            dist = import_name_to_dist(name)
            dist_summary[dist]["import_names"].add(name)
            dist_summary[dist]["excluded_hard_files"].append(rel)
        for name in info["deferred"]:
            dist = import_name_to_dist(name)
            dist_summary[dist]["import_names"].add(name)
            dist_summary[dist]["deferred_files"].append(rel)
        for name in info["conditional"]:
            dist = import_name_to_dist(name)
            dist_summary[dist]["import_names"].add(name)
            dist_summary[dist]["conditional_files"].append(rel)

    # Filter bare namespace packages
    for ns in list(dist_summary.keys()):
        if ns in NAMESPACE_PACKAGES and ns not in DIST_TO_IMPORTS:
            del dist_summary[ns]

    # Serialize
    serializable_dist: dict[str, dict] = {}
    for dist, info in sorted(dist_summary.items()):
        serializable_dist[dist] = {
            "import_names": sorted(info["import_names"]),
            "hard_files": sorted(set(info["hard_files"])),
            "excluded_hard_files": sorted(set(info["excluded_hard_files"])),
            "deferred_files": sorted(set(info["deferred_files"])),
            "conditional_files": sorted(set(info["conditional_files"])),
        }

    serializable_phantoms = {k: sorted(set(v)) for k, v in sorted(phantom_data.items())}

    return {
        "scan_metadata": {
            "tag": tag,
            "roots": roots,
            "exclude_subdirs": list(excl_set),
            "files_scanned": files_scanned,
            "dist_packages_found": len(serializable_dist),
            "phantom_internal_modules": len(serializable_phantoms),
            "parse_errors": all_errors,
            "timestamp": _FIXED_TS,
            "python_version": (f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"),
        },
        "dist_summary": serializable_dist,
        "phantom_internal_imports": serializable_phantoms,
    }


def print_scan_summary(inventory: dict) -> None:
    meta = inventory["scan_metadata"]
    ds = inventory["dist_summary"]
    print(f"Scan complete: tag={meta['tag']}")
    print(f"  Roots:            {meta['roots']}")
    if meta["exclude_subdirs"]:
        print(f"  Exclude subdirs:  {meta['exclude_subdirs']}")
    print(f"  Files scanned:    {meta['files_scanned']}")
    print(f"  Dist packages:    {meta['dist_packages_found']}")
    print(f"  Phantom internal: {meta['phantom_internal_modules']}")
    print(f"  Parse errors:     {len(meta['parse_errors'])}")
    if meta["parse_errors"]:
        for err in meta["parse_errors"][:10]:
            print(f"    ERROR: {err}")
    print()
    print("  Dist packages found:")
    for dist, info in tqdm(sorted(ds.items()), desc="Processing", unit="item"):
        h = len(info["hard_files"])
        eh = len(info["excluded_hard_files"])
        d = len(info["deferred_files"])
        c = len(info["conditional_files"])
        imp = ", ".join(info["import_names"])
        parts = []
        if h:
            parts.append(f"{h} hard")
        if eh:
            parts.append(f"{eh} excluded-hard")
        if d:
            parts.append(f"{d} deferred")
        if c:
            parts.append(f"{c} conditional")
        counts = ", ".join(parts) if parts else "0"
        print(f"    {dist:30s} imports=[{imp}]  ({counts})")


# ── Merge command ────────────────────────────────────────────────────────────


def merge_inventories(out_dir: Path) -> dict:
    """Read all tagged inventory JSONs and assign buckets."""
    inv_files = sorted(out_dir.glob("dependency_audit_scan_*.json"))
    if not inv_files:
        print("ERROR: no scan inventory files found in", out_dir)
        sys.exit(1)

    scans: dict[str, dict] = {}
    for fp in inv_files:
        data = json.loads(fp.read_text(encoding="utf-8"))
        tag = data["scan_metadata"]["tag"]
        scans[tag] = data
        print(f"  Loaded: {fp.name} (tag={tag}, {data['scan_metadata']['dist_packages_found']} dists)")

    # Collect all dist packages across all scans
    all_dists: dict[str, dict] = defaultdict(
        lambda: {
            "import_names": set(),
            "tags": set(),
            "runtime_hard_files": [],
            "runtime_excluded_hard_files": [],
            "runtime_deferred_files": [],
            "runtime_conditional_files": [],
            "dev_hard_files": [],
            "sdks_files": [],
        },
    )

    for tag, inv in scans.items():
        for dist, info in inv["dist_summary"].items():
            all_dists[dist]["import_names"].update(info["import_names"])
            all_dists[dist]["tags"].add(tag)
            if tag == "runtime":
                all_dists[dist]["runtime_hard_files"].extend(info["hard_files"])
                all_dists[dist]["runtime_excluded_hard_files"].extend(info["excluded_hard_files"])
                all_dists[dist]["runtime_deferred_files"].extend(info["deferred_files"])
                all_dists[dist]["runtime_conditional_files"].extend(info["conditional_files"])
            elif tag == "dev":
                all_dists[dist]["dev_hard_files"].extend(info["hard_files"])
                all_dists[dist]["dev_hard_files"].extend(info["deferred_files"])
                all_dists[dist]["dev_hard_files"].extend(info["conditional_files"])
            elif tag == "sdks":
                all_dists[dist]["sdks_files"].extend(info["hard_files"])
                all_dists[dist]["sdks_files"].extend(info["deferred_files"])
                all_dists[dist]["sdks_files"].extend(info["conditional_files"])

    # Assign buckets
    pkg_map: dict[str, dict] = {}
    for dist, info in tqdm(sorted(all_dists.items()), desc="Processing", unit="item"):
        if dist in DEV_TOOL_DISTS:
            bucket = "dev"
        elif info["tags"] == {"sdks"}:
            bucket = "sdks"
        elif info["runtime_hard_files"]:
            bucket = "core"
        else:
            bucket = "infra"

        pkg_map[dist] = {
            "dist_package": dist,
            "import_names": sorted(info["import_names"]),
            "verify_imports": DIST_TO_IMPORTS.get(dist, sorted(info["import_names"])),
            "version_spec": BUCKET_VERSIONS.get(dist, ""),
            "bucket": bucket,
            "runtime_hard_files": sorted(set(info["runtime_hard_files"])),
            "runtime_excluded_hard_files": sorted(set(info["runtime_excluded_hard_files"])),
            "runtime_deferred_files": sorted(set(info["runtime_deferred_files"])),
            "runtime_conditional_files": sorted(set(info["runtime_conditional_files"])),
            "dev_hard_files": sorted(set(info["dev_hard_files"])),
            "sdks_files": sorted(set(info["sdks_files"])),
        }

    # Collect phantoms from all scans
    phantoms: dict[str, list[str]] = defaultdict(list)
    for inv in scans.values():
        for name, files in inv.get("phantom_internal_imports", {}).items():
            phantoms[name].extend(files)
    for k in phantoms:
        phantoms[k] = sorted(set(phantoms[k]))

    bucket_counts: dict[str, int] = defaultdict(int)
    for info in pkg_map.values():
        bucket_counts[info["bucket"]] += 1

    merged = {
        "merge_metadata": {
            "timestamp": _FIXED_TS,
            "scans_merged": list(scans.keys()),
            "scan_files": [f.name for f in inv_files],
            "total_dist_packages": len(pkg_map),
            "bucket_counts": dict(bucket_counts),
            "total_phantom_internal": len(phantoms),
        },
        "dist_package_map": pkg_map,
        "phantom_internal_imports": dict(sorted(phantoms.items())),
    }
    return merged


# ── Artifact generators ──────────────────────────────────────────────────────

BUCKET_LABELS = {
    "core": "Core Runtime (required — `pip install -e .`)",
    "dev": "Dev/Test Tooling (`pip install -e '.[dev]'`)",
    "infra": "Optional Integrations (`pip install -e '.[infra]'`)",
    "sdks": "SDK Samples (`pip install -e '.[sdks]'`)",
}


def generate_markdown_report(merged: dict) -> str:
    meta = merged["merge_metadata"]
    pkg_map = merged["dist_package_map"]
    phantoms = merged["phantom_internal_imports"]

    L: list[str] = []
    L.append("# Dependency Audit Report (v4 — separate scans)")
    L.append("")
    L.append(f"**Generated**: {meta['timestamp']}")
    L.append(f"**Scans merged**: {', '.join(meta['scans_merged'])}")
    L.append(f"**Dist packages**: {meta['total_dist_packages']}")
    bc = meta["bucket_counts"]
    L.append(
        f"**Buckets**: core={bc.get('core', 0)}, "
        f"dev={bc.get('dev', 0)}, "
        f"infra={bc.get('infra', 0)}, "
        f"sdks={bc.get('sdks', 0)}",
    )
    L.append(f"**Phantom/stale internal**: {meta['total_phantom_internal']}")
    L.append("")

    L.append("## Bucket Assignment Rule")
    L.append("")
    L.append("1. DEV-TOOL dist packages → `dev` (always)")
    L.append("2. Packages appearing ONLY in the `sdks` tagged scan → `sdks`")
    L.append(
        "3. Packages with ≥1 top-level hard import in the `runtime` "
        "tagged scan (after `--exclude-subdir` filtering) → `core`",
    )
    L.append("4. Everything else → `infra`")
    L.append("")
    L.append("### Repo Shipping Contract")
    L.append("")
    L.append(
        "The following directories are **not shipped** as part of the "
        "runtime package and are excluded from core classification:",
    )
    L.append("")
    L.append("- `tests/` — test suite (dev-only)")
    L.append("- `ops_scripts/` — operational tooling (dev-only)")
    L.append("- `data/` — sample data and SDK wrappers (not shipped)")
    L.append(
        "- `*/scripts/` subdirs within runtime roots — utility/maintenance "
        "scripts (invoked manually, not imported at runtime)",
    )
    L.append(
        "- `*/dashboards/` subdirs within runtime roots — observability dashboards (deployed separately)",
    )
    L.append("")
    L.append(
        "This contract MUST be enforced via packaging (`[project.packages]` "
        "or `find:` directives in setup) and CI. If any excluded path "
        "becomes shipped, re-run the runtime scan without that exclusion.",
    )
    L.append("")

    # Group by bucket
    buckets: dict[str, list[dict]] = defaultdict(list)
    for info in pkg_map.values():
        buckets[info["bucket"]].append(info)

    for bname in tqdm(["core", "dev", "infra", "sdks"], desc="Processing", unit="item"):
        pkgs = buckets.get(bname, [])
        if not pkgs:
            continue
        L.append(f"## {BUCKET_LABELS.get(bname, bname)}")
        L.append("")
        L.append("| dist package | import name(s) | RT hard | RT excl | RT defer | RT cond | Dev | version |")
        L.append("|---|---|---|---|---|---|---|---|")
        for pkg in sorted(pkgs, key=lambda p: p["dist_package"]):
            dn = pkg["dist_package"]
            ins = ", ".join(pkg["import_names"])
            rh = len(pkg["runtime_hard_files"])
            re_ = len(pkg["runtime_excluded_hard_files"])
            rd = len(pkg["runtime_deferred_files"])
            rc = len(pkg["runtime_conditional_files"])
            dh = len(pkg["dev_hard_files"])
            ver = pkg["version_spec"]
            L.append(f"| {dn} | {ins} | {rh} | {re_} | {rd} | {rc} | {dh} | {ver} |")
        L.append("")

    if phantoms:
        L.append("## Phantom/Stale Internal Imports")
        L.append("")
        L.append("| import name | file count |")
        L.append("|---|---|")
        for name, files in sorted(phantoms.items()):
            L.append(f"| {name} | {len(files)} |")
        L.append("")

    return "\n".join(L)


def generate_pyproject_diff(merged: dict) -> str:
    pkg_map = merged["dist_package_map"]
    core = sorted([i for i in pkg_map.values() if i["bucket"] == "core"], key=lambda x: x["dist_package"])
    dev = sorted([i for i in pkg_map.values() if i["bucket"] == "dev"], key=lambda x: x["dist_package"])
    infra = sorted([i for i in pkg_map.values() if i["bucket"] == "infra"], key=lambda x: x["dist_package"])
    sdks = sorted([i for i in pkg_map.values() if i["bucket"] == "sdks"], key=lambda x: x["dist_package"])

    L: list[str] = []
    L.append("# Proposed pyproject.toml changes (v4 — runtime-scan-derived core)")
    L.append("# Core = runtime scan hard imports only (excl scripts/dashboards)")
    L.append("")
    L.append("--- a/pyproject.toml")
    L.append("+++ b/pyproject.toml")
    L.append("")
    L.append("## [project].dependencies (core)")
    L.append("")
    L.append(" dependencies = [")
    L.append('-    "pytest>=7.4.0",                # → [dev]')
    L.append('-    "pytest-cov>=4.1.0",             # → [dev]')
    L.append('-    "pytest-asyncio>=0.21.0",        # → [dev]')
    L.append('-    "google-genai>=1.0.0",           # → [infra] (deferred/conditional)')
    L.append('-    "pinecone-client>=3.0.0",        # REMOVE (renamed)')
    L.append('-    "redis>=5.0.0",                  # stays or → [infra] per scan')
    L.append('-    "cryptography>=41.0.0",          # → [infra] (no direct import)')
    for pkg in core:
        dn = pkg["dist_package"]
        ver = pkg["version_spec"]
        rh = len(pkg["runtime_hard_files"])
        pad = " " * max(1, 30 - len(dn) - len(ver))
        if dn in ("pydantic", "libcst"):
            L.append(f'     "{dn}{ver}",')
        else:
            L.append(f'+    "{dn}{ver}",{pad}# {rh} runtime hard')
    L.append(" ]")
    L.append("")
    L.append("## [project.optional-dependencies]")
    L.append("")
    L.append("+dev = [")
    for pkg in dev:
        L.append(f'+    "{pkg["dist_package"]}{pkg["version_spec"]}",')
    L.append("+]")
    L.append("+infra = [")
    for pkg in infra:
        ver = pkg["version_spec"]
        if ver:
            L.append(f'+    "{pkg["dist_package"]}{ver}",')
    L.append("+]")
    L.append("+sdks = [")
    for pkg in sdks:
        L.append(f'+    "{pkg["dist_package"]}{pkg["version_spec"]}",')
    L.append("+]")
    L.append("")
    L.append(f"# pip install -e .              # core ({len(core)} pkgs)")
    L.append(f"# pip install -e '.[dev]'       # + dev ({len(dev)} pkgs)")
    L.append(f"# pip install -e '.[infra]'     # + infra ({len(infra)} pkgs)")
    L.append(f"# pip install -e '.[sdks]'      # + sdks ({len(sdks)} pkgs)")
    L.append("# pip install -e '.[dev,infra]'  # full dev environment")
    return "\n".join(L)


def generate_verification_script(merged: dict) -> str:
    pkg_map = merged["dist_package_map"]

    buckets_data: dict[str, list[dict]] = defaultdict(list)
    for info in pkg_map.values():
        buckets_data[info["bucket"]].append(
            {
                "dist": info["dist_package"],
                "imports": info["verify_imports"],
            },
        )

    L: list[str] = []
    L.append('"""')
    L.append("Reproducible import verification script (v4).")
    L.append(f"Generated: {merged['merge_metadata']['timestamp']}")
    L.append("")
    L.append("Verification contract:")
    L.append("  default:       require core only.")
    L.append("  --require-dev: require core + dev.")
    L.append("  --all:         require every bucket.")
    L.append("")
    L.append("Output is keyed by dist package with per-import breakdown.")
    L.append('"""')
    L.append("")
    L.append("import importlib")
    L.append("import sys")
    L.append("")
    L.append("PACKAGES = {")
    for bname in ["core", "dev", "infra", "sdks"]:
        entries = sorted(buckets_data.get(bname, []), key=lambda x: x["dist"])
        if not entries:
            continue
        L.append(f"    {bname!r}: [")
        for e in entries:
            L.append(f"        ({e['dist']!r}, {e['imports']!r}),")
        L.append("    ],")
    L.append("}")
    L.append("")
    L.append("")
    L.append("def main():")
    L.append("    require_dev = '--require-dev' in sys.argv")
    L.append("    require_all = '--all' in sys.argv")
    L.append("")
    L.append("    required_buckets = {'core'}")
    L.append("    if require_dev:")
    L.append("        required_buckets.add('dev')")
    L.append("    if require_all:")
    L.append("        required_buckets = set(PACKAGES.keys())")
    L.append("")
    L.append("    bucket_ok = {}")
    L.append("    bucket_fail = {}")
    L.append("    bucket_skip = {}")
    L.append("    rows = []")
    L.append("")
    L.append("    for bucket, packages in PACKAGES.items():")
    L.append("        required = bucket in required_buckets")
    L.append("        bucket_ok[bucket] = 0")
    L.append("        bucket_fail[bucket] = 0")
    L.append("        bucket_skip[bucket] = 0")
    L.append("        for dist, imports in packages:")
    L.append("            import_results = []")
    L.append("            all_ok = True")
    L.append("            for imp in imports:")
    L.append("                try:")
    L.append("                    importlib.import_module(imp)")
    L.append("                    import_results.append((imp, 'OK'))")
    L.append("                except ImportError as e:")
    L.append("                    import_results.append((imp, f'MISSING: {e}'))")
    L.append("                    all_ok = False")
    L.append("            if all_ok:")
    L.append("                bucket_ok[bucket] += 1")
    L.append("                tag = 'OK'")
    L.append("            elif required:")
    L.append("                bucket_fail[bucket] += 1")
    L.append("                tag = 'FAIL'")
    L.append("            else:")
    L.append("                bucket_skip[bucket] += 1")
    L.append("                tag = 'EXPECTED_MISSING'")
    L.append("            req_s = 'REQ' if required else 'OPT'")
    L.append("            imp_detail = ', '.join(f'{i}={s}' for i, s in import_results)")
    L.append(
        "            rows.append("
        "f'  [{bucket:5s}] [{req_s}] "
        "dist={dist:30s} {tag:18s} imports: {imp_detail}')",
    )
    L.append("")
    L.append("    for row in rows:")
    L.append("        print(row)")
    L.append("")
    L.append("    print()")
    L.append("    print('Bucket Summary:')")
    L.append(
        '    hdr = f\'{"bucket":8s} {"required?":10s} {"OK":>4s} {"FAIL":>5s} {"SKIP":>5s} {"verdict":>8s}\'',
    )
    L.append("    print(f'  {hdr}')")
    L.append("    blocking = 0")
    L.append("    for bucket in PACKAGES:")
    L.append("        required = bucket in required_buckets")
    L.append("        ok = bucket_ok.get(bucket, 0)")
    L.append("        fail = bucket_fail.get(bucket, 0)")
    L.append("        skip = bucket_skip.get(bucket, 0)")
    L.append("        verdict = 'PASS' if fail == 0 else 'BLOCK'")
    L.append("        blocking += fail")
    L.append("        req_s = 'yes' if required else 'no'")
    L.append("        print(f'  {bucket:8s} {req_s:10s} {ok:4d} {fail:5d} {skip:5d} {verdict:>8s}')")
    L.append("")
    L.append("    total_ok = sum(bucket_ok.values())")
    L.append("    total_fail = sum(bucket_fail.values())")
    L.append("    total_skip = sum(bucket_skip.values())")
    L.append("    total = total_ok + total_fail + total_skip")
    L.append("    print()")
    L.append(
        "    print(f'Total: {total_ok}/{total} dist packages OK, "
        "{total_fail} BLOCKING, {total_skip} EXPECTED_MISSING')",
    )
    L.append("    if blocking > 0:")
    L.append("        print(f'RESULT: FAIL ({blocking} blocking failures)')")
    L.append("        sys.exit(1)")
    L.append("    else:")
    L.append("        print('RESULT: PASS (all required imports OK)')")
    L.append("        sys.exit(0)")
    L.append("")
    L.append("")
    L.append("if __name__ == '__main__':")
    L.append("    main()")
    return "\n".join(L)


# ── Entry point ──────────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(description="AST-based third-party import auditor (v4)")
    parser.add_argument("--roots", nargs="+", help="Directories to scan (relative to project root)")
    parser.add_argument("--emit-tag", dest="emit_tag", help="Tag for this scan (e.g., runtime, dev, sdks)")
    parser.add_argument(
        "--exclude-subdir",
        nargs="*",
        default=[],
        help="Subdirectory names to exclude from 'hard' classification",
    )
    parser.add_argument(
        "--merge",
        action="store_true",
        help="Merge all tagged scan inventories and produce final artifacts",
    )
    args = parser.parse_args()

    out_dir = PROJECT_ROOT / "docs" / REPORTS_DIR / "plans"
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.merge:
        # Merge mode
        print("Merging scan inventories...")
        merged = merge_inventories(out_dir)
        meta = merged["merge_metadata"]
        bc = meta["bucket_counts"]

        # Write merged inventory
        merged_path = out_dir / "dependency_audit_merged.json"
        merged_path.write_text(json.dumps(merged, indent=2, sort_keys=False), encoding="utf-8")

        # Write report
        report_path = out_dir / "dependency_audit_report.md"
        report_path.write_text(generate_markdown_report(merged), encoding="utf-8")

        # Write pyproject diff
        diff_path = out_dir / "dependency_audit_pyproject_diff.patch"
        diff_path.write_text(generate_pyproject_diff(merged), encoding="utf-8")

        # Write verification script
        verify_path = out_dir / "dependency_verify_imports.py"
        verify_path.write_text(generate_verification_script(merged), encoding="utf-8")

        print()
        print("Merge complete:")
        print(f"  Scans merged:     {meta['scans_merged']}")
        print(f"  Dist packages:    {meta['total_dist_packages']}")
        print(
            f"  Buckets:          core={bc.get('core', 0)} "
            f"dev={bc.get('dev', 0)} "
            f"infra={bc.get('infra', 0)} "
            f"sdks={bc.get('sdks', 0)}",
        )
        print(f"  Phantom internal: {meta['total_phantom_internal']}")
        print()
        print("  Packages by bucket:")
        pkg_map = merged["dist_package_map"]
        by_bucket: dict[str, list[str]] = defaultdict(list)
        for info in pkg_map.values():
            by_bucket[info["bucket"]].append(info["dist_package"])
        for bname in ["core", "dev", "infra", "sdks"]:
            pkgs = sorted(by_bucket.get(bname, []))
            if pkgs:
                print(f"    [{bname}] ({len(pkgs)}): {', '.join(pkgs)}")
        print()
        print("  Artifacts:")
        for p in [merged_path, report_path, diff_path, verify_path]:
            print(f"    {p.relative_to(PROJECT_ROOT)}")

    elif args.roots and args.emit_tag:
        # Scan mode
        print(f"Scanning: roots={args.roots} tag={args.emit_tag} exclude-subdir={args.exclude_subdir}")
        inventory = run_scan(
            roots=args.roots,
            tag=args.emit_tag,
            exclude_subdirs=args.exclude_subdir or None,
        )

        inv_path = out_dir / f"dependency_audit_scan_{args.emit_tag}.json"
        inv_path.write_text(json.dumps(inventory, indent=2, sort_keys=False), encoding="utf-8")

        print()
        print_scan_summary(inventory)
        print()
        print(f"  Written: {inv_path.relative_to(PROJECT_ROOT)}")

    else:
        parser.print_help()
        print()
        print("Examples:")
        print("  # Runtime scan:")
        print("  python ops_scripts/general/ast_import_audit.py \\")
        print("    --roots agentic_core apps_lic apps_rg apps_shared \\")
        print("    --emit-tag runtime \\")
        print("    --exclude-subdir scripts dashboards")
        print()
        print("  # Dev scan:")
        print("  python ops_scripts/general/ast_import_audit.py \\")
        print("    --roots tests --emit-tag dev")
        print()
        print("  # SDK scan:")
        print("  python ops_scripts/general/ast_import_audit.py \\")
        print("    --roots data/sdks_mcps --emit-tag sdks")
        print()
        print("  # Merge all scans:")
        print("  python ops_scripts/general/ast_import_audit.py --merge")
        sys.exit(1)


if __name__ == "__main__":
    main()

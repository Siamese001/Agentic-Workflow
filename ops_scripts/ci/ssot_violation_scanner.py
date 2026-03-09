"""
SSOT Violation Scanner  [UTF-8 output]
======================

Scans all SOVEREIGN_TERRITORIES (10 folders) for Python files that contain
hardcoded string literals or import paths that violate SSOT as defined by:

  - agentic_core/L0_routing/config/path_constants.py
  - agentic_core/L5_safety/config/structure_blueprint/ssot.py
  - agentic_core/L5_safety/config/structure_blueprint_config.py

Violation categories:
  REPLACE        - hardcoded path string, clear path construction context → swap for SSOT constant
  WRONG_IMPORT   - imports from structure_blueprint_config directly instead of canonical path
  SKIP_COMMENT   - in a docstring or comment only
  SKIP_TEST_DATA - intentional test fixture / assertion string
  SKIP_DYNAMIC   - runtime-computed or ambiguous context, needs manual review

Output: artifacts/ssot_violation_scan.json

Usage:
    python ops_scripts/ci/ssot_violation_scanner.py
    python ops_scripts/ci/ssot_violation_scanner.py --summary
    python ops_scripts/ci/ssot_violation_scanner.py --category REPLACE
"""

from __future__ import annotations

import ast
import io
import json
import sys
from pathlib import Path

# Ensure UTF-8 output on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ---------------------------------------------------------------------------
# COMPREHENSIVE SSOT TARGETS
# Sources:
#   agentic_core/L0_routing/config/path_constants.py
#   agentic_core/L5_safety/config/structure_blueprint/ssot.py
#
# Format: "hardcoded_string" -> ("CONSTANT_NAME", "canonical_import_module")
# ---------------------------------------------------------------------------

# (value, constant_name, canonical_module, category_tag)
SSOT_TARGETS: list[tuple[str, str, str, str]] = [
    # ---- Root directories --------------------------------------------------
    ("archives", "ARCHIVES_DIR", "agentic_core.L0_routing.config.path_constants", "root_dir"),
    ("agentic_core", "AGENTIC_CORE_DIR", "agentic_core.L0_routing.config.path_constants", "root_dir"),
    ("apps_lic", "APPS_LIC_DIR", "agentic_core.L0_routing.config.path_constants", "root_dir"),
    ("apps_rg", "APPS_RG_DIR", "agentic_core.L0_routing.config.path_constants", "root_dir"),
    ("apps_shared", "APPS_SHARED_DIR", "agentic_core.L0_routing.config.path_constants", "root_dir"),
    ("ops_scripts", "OPS_SCRIPTS_DIR", "agentic_core.L0_routing.config.path_constants", "root_dir"),
    ("tests", "TESTS_DIR", "agentic_core.L0_routing.config.path_constants", "root_dir"),
    ("system_learning", "SYSTEM_LEARNING_DIR", "agentic_core.L0_routing.config.path_constants", "root_dir"),
    ("tools", "TOOLS_DIR", "agentic_core.L0_routing.config.path_constants", "root_dir"),
    ("reports", "REPORTS_DIR", "agentic_core.L5_safety.config.structure_blueprint.ssot", "root_dir"),
    ("data", "DATA_DIR", "agentic_core.L5_safety.config.structure_blueprint.ssot", "root_dir"),
    ("docs", "DOCS_DIR", "agentic_core.L5_safety.config.structure_blueprint.ssot", "root_dir"),
    # ---- Layer root bare names (single component) --------------------------
    ("L0_routing", "LAYER_ROOTS", "agentic_core.L5_safety.config.structure_blueprint.ssot", "layer_root"),
    ("L1_cognition", "LAYER_ROOTS", "agentic_core.L5_safety.config.structure_blueprint.ssot", "layer_root"),
    ("L2_execution", "LAYER_ROOTS", "agentic_core.L5_safety.config.structure_blueprint.ssot", "layer_root"),
    (
        "L3_orchestration",
        "LAYER_ROOTS",
        "agentic_core.L5_safety.config.structure_blueprint.ssot",
        "layer_root",
    ),
    ("L4_state", "LAYER_ROOTS", "agentic_core.L5_safety.config.structure_blueprint.ssot", "layer_root"),
    ("L5_safety", "LAYER_ROOTS", "agentic_core.L5_safety.config.structure_blueprint.ssot", "layer_root"),
    (
        "L6_observability",
        "LAYER_ROOTS",
        "agentic_core.L5_safety.config.structure_blueprint.ssot",
        "layer_root",
    ),
    # ---- Layer compound paths ----------------------------------------------
    (
        "agentic_core/L0_routing",
        "L0_ROUTING_DIR",
        "agentic_core.L0_routing.config.path_constants",
        "layer_path",
    ),
    (
        "agentic_core/L1_cognition",
        "L1_COGNITION_DIR",
        "agentic_core.L0_routing.config.path_constants",
        "layer_path",
    ),
    (
        "agentic_core/L2_execution",
        "L2_EXECUTION_DIR",
        "agentic_core.L0_routing.config.path_constants",
        "layer_path",
    ),
    (
        "agentic_core/L3_orchestration",
        "L3_ORCHESTRATION_DIR",
        "agentic_core.L0_routing.config.path_constants",
        "layer_path",
    ),
    ("agentic_core/L4_state", "L4_STATE_DIR", "agentic_core.L0_routing.config.path_constants", "layer_path"),
    (
        "agentic_core/L5_safety",
        "L5_SAFETY_DIR",
        "agentic_core.L0_routing.config.path_constants",
        "layer_path",
    ),
    (
        "agentic_core/L6_observability",
        "L6_OBSERVABILITY_DIR",
        "agentic_core.L0_routing.config.path_constants",
        "layer_path",
    ),
    # ---- Deep compound paths -----------------------------------------------
    (
        "agentic_core/L6_observability/dashboards",
        "DASHBOARD_DIR",
        "agentic_core.L5_safety.config.structure_blueprint.ssot",
        "compound_path",
    ),
    (
        "agentic_core/config/core",
        "BLUEPRINT_SOVEREIGN_DIR",
        "agentic_core.L5_safety.config.structure_blueprint.ssot",
        "compound_path",
    ),
    (
        "agentic_core/runtime/types",
        "SCHEMAS_DIR",
        "agentic_core.L5_safety.config.structure_blueprint.ssot",
        "compound_path",
    ),
    (
        "agentic_core/prompt_governance",
        "PROMPT_GOVERNANCE_DIR",
        "agentic_core.L5_safety.config.structure_blueprint.ssot",
        "compound_path",
    ),
    (
        "agentic_core/utils",
        "UTILS_DIR",
        "agentic_core.L5_safety.config.structure_blueprint.ssot",
        "compound_path",
    ),
    (
        "agentic_core/runtime",
        "RUNTIME_DIR",
        "agentic_core.L5_safety.config.structure_blueprint.ssot",
        "compound_path",
    ),
    (
        "docs/reports/plans",
        "DOCS_REPORTS_PLANS",
        "agentic_core.L5_safety.config.structure_blueprint.ssot",
        "compound_path",
    ),
    (
        "reports/coverage_html",
        "COVERAGE_HTML_DIR",
        "agentic_core.L5_safety.config.structure_blueprint.ssot",
        "compound_path",
    ),
    # ---- Test mirror paths -------------------------------------------------
    ("tests/unit", "TESTS_UNIT_DIR", "agentic_core.L5_safety.config.structure_blueprint.ssot", "test_path"),
    (
        "tests/integration",
        "TESTS_INTEGRATION_DIR",
        "agentic_core.L5_safety.config.structure_blueprint.ssot",
        "test_path",
    ),
    ("tests/e2e", "TESTS_E2E_DIR", "agentic_core.L5_safety.config.structure_blueprint.ssot", "test_path"),
    (
        "tests/unit_min_deps",
        "TESTS_AUTOGEN_DIR",
        "agentic_core.L5_safety.config.structure_blueprint.ssot",
        "test_path",
    ),
    (
        "tests/unit/agentic_core",
        "TEST_CANONICAL_LOCATION_MAP",
        "agentic_core.L5_safety.config.structure_blueprint.ssot",
        "test_path",
    ),
    (
        "tests/unit/apps_lic",
        "TEST_CANONICAL_LOCATION_MAP",
        "agentic_core.L5_safety.config.structure_blueprint.ssot",
        "test_path",
    ),
    (
        "tests/unit/apps_rg",
        "TEST_CANONICAL_LOCATION_MAP",
        "agentic_core.L5_safety.config.structure_blueprint.ssot",
        "test_path",
    ),
    (
        "tests/unit/apps_shared",
        "TEST_CANONICAL_LOCATION_MAP",
        "agentic_core.L5_safety.config.structure_blueprint.ssot",
        "test_path",
    ),
    (
        "tests/unit/system_learning",
        "TEST_CANONICAL_LOCATION_MAP",
        "agentic_core.L5_safety.config.structure_blueprint.ssot",
        "test_path",
    ),
    # ---- Canonical JSON/state filenames ------------------------------------
    ("runtime_state.json", "RUNTIME_STATE_JSON", "agentic_core.L0_routing.config.path_constants", "filename"),
    (
        "agent_discovery_full.json",
        "AGENT_DISCOVERY_JSON",
        "agentic_core.L5_safety.config.structure_blueprint.ssot",
        "filename",
    ),
    (
        "agent_discovery_full.manifest.json",
        "AGENT_DISCOVERY_MANIFEST_JSON",
        "agentic_core.L5_safety.config.structure_blueprint.ssot",
        "filename",
    ),
]

# Build lookup dict: value -> (constant, module, category)
_TARGET_MAP: dict[str, tuple[str, str, str]] = {v: (c, m, t) for v, c, m, t in SSOT_TARGETS}

# ---- Wrong-import patterns ------------------------------------------------
# Files that import from the old shim path instead of the canonical package
WRONG_IMPORT_PATTERNS: list[tuple[str, str]] = [
    # (bad_module, good_module)
    ("structure_blueprint_config", "agentic_core.L5_safety.config.structure_blueprint"),
    (
        "agentic_core.L5_safety.config.structure_blueprint_config",
        "agentic_core.L5_safety.config.structure_blueprint",
    ),
]

# ---- Scan scope -----------------------------------------------------------
SCAN_ROOTS: list[str] = [
    "agentic_core",
    "apps_lic",
    "apps_rg",
    "apps_shared",
    "ops_scripts",
    "tests",
    "tools",
    "system_learning",
    "data",
    "docs",
]

# Files that ARE the SSOT definition sites — skip REPLACE classification for their own assignments
SSot_DEFINITION_FILES: frozenset[str] = frozenset(
    {
        "agentic_core/L0_routing/config/path_constants.py",
        "agentic_core/L5_safety/config/structure_blueprint/ssot.py",
        "agentic_core/L5_safety/config/structure_blueprint/_constants.py",
        "agentic_core/L5_safety/config/structure_blueprint/_verify.py",
    }
)

EXCLUDE_DIRS: frozenset[str] = frozenset(
    {
        "archives",
        "artifacts",
        "logs",
        ".git",
        ".github",
        "__pycache__",
        ".venv",
        "venv",
        ".backup",
        ".gravity_state",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "node_modules",
    }
)

# Parent AST node types that indicate a path-construction context
PATH_PARENT_TYPES: frozenset[str] = frozenset(
    {
        "BinOp",  # Path("x") / "sub"
        "Call",  # Path("x"), os.path.join("x", ...)
        "Attribute",  # root / "x" / ...
        "Assign",  # X = root / "x"
        "AugAssign",
        "AnnAssign",
        "Return",
        "keyword",  # kwarg value
        "JoinedStr",  # f-string
        "List",  # list literal containing path string
        "Tuple",  # tuple containing path string
    }
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_project_root() -> Path:
    current = Path(__file__).resolve()
    for parent in [current, *current.parents]:
        if (parent / "pyproject.toml").exists() or (parent / ".git").exists():
            return parent
    return Path.cwd()


def _is_already_using_constant(line_text: str) -> bool:
    """Return True if the line already references an SSOT constant."""
    ssot_suffixes = ("_DIR", "_ROOT", "_ROOTS", "_MAP", "_JSON", "_PLANS", "_BASE")
    return any(s in line_text for s in ssot_suffixes)


def _is_dict_key_or_comparison(value: str, line_text: str) -> bool:
    """Return True for dict-key lookups, startswith/endswith — not path constructions."""
    checks = (
        f'.get("{value}"',
        f".get('{value}'",
        f'["{value}"]',
        f"['{value}']",
        f'.startswith("{value}"',
        f".startswith('{value}'",
        f'.endswith("{value}"',
        f".endswith('{value}'",
        f'.index("{value}"',
        f".index('{value}'",
        f'.split("{value}"',
        f".split('{value}'",
        f'== "{value}"',
        f"== '{value}'",
        f'!= "{value}"',
        f"!= '{value}'",
        f'in "{value}"',
        f"in '{value}'",
    )
    return any(p in line_text for p in checks)


def _classify_string_hit(
    node: ast.Constant,
    tree: ast.Module,
    source_lines: list[str],
    file_path: Path,
) -> str:
    value: str = node.value
    line_idx = node.lineno - 1
    line_text = source_lines[line_idx] if line_idx < len(source_lines) else ""

    # 1. Pure comment line
    if line_text.lstrip().startswith("#"):
        return "SKIP_COMMENT"

    # 2. Inside a docstring (Expr wrapping a Constant)
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            if child is node:
                if isinstance(parent, ast.Expr) and isinstance(parent.value, ast.Constant):
                    return "SKIP_COMMENT"

    # 3. Already uses SSOT constant on same line
    if _is_already_using_constant(line_text):
        return "SKIP_COMMENT"

    # 4. Dict-key / comparison context
    if _is_dict_key_or_comparison(value, line_text):
        return "SKIP_DYNAMIC"

    # 5. Test-data signals in test files
    test_data_signals = (
        "test_",
        "_test",
        "assert",
        "expected",
        "fixture",
        "parametrize",
        "EXPECTED",
        "pytest.param",
    )
    is_test_file = any(s in str(file_path) for s in ("test_", "_test", "tests/", "tests\\"))
    if is_test_file:
        if any(sig in line_text for sig in test_data_signals):
            return "SKIP_TEST_DATA"
        if "assert" in line_text or "expected" in line_text.lower():
            return "SKIP_TEST_DATA"

    # 6. Parent node type → path construction
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            if child is node:
                ptype = type(parent).__name__
                if ptype in PATH_PARENT_TYPES:
                    return "REPLACE"
                if ptype in ("Compare", "If", "Assert"):
                    return "SKIP_DYNAMIC"

    return "SKIP_DYNAMIC"


# ---------------------------------------------------------------------------
# Import violation scanner
# ---------------------------------------------------------------------------


def _scan_imports(tree: ast.Module, file_path: Path, project_root: Path) -> list[dict]:
    """Detect WRONG_IMPORT violations in import statements."""
    hits = []
    rel = str(file_path.relative_to(project_root))

    for node in ast.walk(tree):
        # from X import Y  or  import X
        if isinstance(node, (ast.ImportFrom, ast.Import)):
            if isinstance(node, ast.ImportFrom):
                module = node.module or ""
            else:
                # import X — check names
                for alias in node.names:
                    module = alias.name
                    for bad, good in WRONG_IMPORT_PATTERNS:
                        if bad in module:
                            hits.append(
                                {
                                    "file": rel,
                                    "line": node.lineno,
                                    "col": 0,
                                    "value": module,
                                    "ssot_constant": good,
                                    "classification": "WRONG_IMPORT",
                                    "category": "wrong_import",
                                    "context": f"import {module}",
                                    "canonical_module": good,
                                }
                            )
                continue

            for bad, good in WRONG_IMPORT_PATTERNS:
                if bad in module:
                    # Skip the shim file itself — it's the definition
                    if "structure_blueprint_config" in rel:
                        continue
                    hits.append(
                        {
                            "file": rel,
                            "line": node.lineno,
                            "col": 0,
                            "value": module,
                            "ssot_constant": good,
                            "classification": "WRONG_IMPORT",
                            "category": "wrong_import",
                            "context": f"from {module} import ...",
                            "canonical_module": good,
                        }
                    )

    return hits


# ---------------------------------------------------------------------------
# File scanner
# ---------------------------------------------------------------------------


def scan_file(file_path: Path, project_root: Path) -> list[dict]:
    hits = []
    try:
        source = file_path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, filename=str(file_path))
    except (SyntaxError, Exception):
        return []

    source_lines = source.splitlines()
    rel = str(file_path.relative_to(project_root)).replace("\\", "/")

    # Skip REPLACE classification for SSOT definition files themselves
    is_definition_site = rel in SSot_DEFINITION_FILES

    # String-literal hits
    for node in ast.walk(tree):
        if not isinstance(node, ast.Constant) or not isinstance(node.value, str):
            continue

        value = node.value
        entry = _TARGET_MAP.get(value)
        if entry is None:
            continue

        constant, canonical_module, category = entry
        if is_definition_site:
            classification = "SKIP_DYNAMIC"  # definition site — value is canonical here
        else:
            classification = _classify_string_hit(node, tree, source_lines, file_path)
        line_idx = node.lineno - 1
        context = source_lines[line_idx].strip() if line_idx < len(source_lines) else ""

        hits.append(
            {
                "file": rel,
                "line": node.lineno,
                "col": node.col_offset,
                "value": value,
                "ssot_constant": constant,
                "classification": classification,
                "category": category,
                "context": context,
                "canonical_module": canonical_module,
            }
        )

    # Import violations
    hits.extend(_scan_imports(tree, file_path, project_root))

    return hits


# ---------------------------------------------------------------------------
# Directory walker
# ---------------------------------------------------------------------------


def scan_all(project_root: Path) -> list[dict]:
    all_hits: list[dict] = []
    files_scanned = 0
    files_skipped = 0

    for root_name in SCAN_ROOTS:
        root_path = project_root / root_name
        if not root_path.exists():
            continue

        for py_file in root_path.rglob("*.py"):
            if any(part in EXCLUDE_DIRS for part in py_file.parts):
                files_skipped += 1
                continue
            files_scanned += 1
            all_hits.extend(scan_file(py_file, project_root))

    print(f"[scanner] Scanned {files_scanned} files, skipped {files_skipped}")
    return all_hits


# ---------------------------------------------------------------------------
# Report builder
# ---------------------------------------------------------------------------


def build_report(hits: list[dict]) -> dict:
    classifications = ["REPLACE", "WRONG_IMPORT", "SKIP_COMMENT", "SKIP_TEST_DATA", "SKIP_DYNAMIC"]
    by_cls: dict[str, list[dict]] = {c: [] for c in classifications}
    by_constant: dict[str, list[dict]] = {}
    by_category: dict[str, list[dict]] = {}
    by_file: dict[str, list[dict]] = {}

    for h in hits:
        cls = h["classification"]
        by_cls.setdefault(cls, []).append(h)
        by_constant.setdefault(h["ssot_constant"], []).append(h)
        by_category.setdefault(h["category"], []).append(h)
        by_file.setdefault(h["file"], []).append(h)

    # Files with most violations (actionable only)
    actionable = by_cls["REPLACE"] + by_cls["WRONG_IMPORT"]
    file_counts: dict[str, int] = {}
    for h in actionable:
        file_counts[h["file"]] = file_counts.get(h["file"], 0) + 1
    top_files = sorted(file_counts.items(), key=lambda x: -x[1])[:30]

    summary = {
        "total_hits": len(hits),
        "replace_count": len(by_cls["REPLACE"]),
        "wrong_import_count": len(by_cls.get("WRONG_IMPORT", [])),
        "skip_comment_count": len(by_cls["SKIP_COMMENT"]),
        "skip_test_data_count": len(by_cls["SKIP_TEST_DATA"]),
        "skip_dynamic_count": len(by_cls["SKIP_DYNAMIC"]),
        "actionable_total": len(actionable),
        "by_constant": {k: len(v) for k, v in sorted(by_constant.items(), key=lambda x: -len(x[1]))},
        "by_category": {k: len(v) for k, v in sorted(by_category.items(), key=lambda x: -len(x[1]))},
        "top_offending_files": [{"file": f, "count": c} for f, c in top_files],
    }

    return {
        "summary": summary,
        "hits_by_classification": by_cls,
        "hits_by_constant": dict(by_constant.items()),
        "hits_by_category": by_category,
        "all_hits": hits,
    }


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> int:
    summary_only = "--summary" in sys.argv
    filter_cat = None
    if "--category" in sys.argv:
        idx = sys.argv.index("--category")
        if idx + 1 < len(sys.argv):
            filter_cat = sys.argv[idx + 1].upper()

    project_root = _get_project_root()
    print(f"[scanner] Project root: {project_root}")
    print(
        f"[scanner] Targets: {len(SSOT_TARGETS)} string constants + {len(WRONG_IMPORT_PATTERNS)} import patterns"
    )
    print(f"[scanner] Scanning {len(SCAN_ROOTS)} SOVEREIGN_TERRITORIES...")

    hits = scan_all(project_root)
    report = build_report(hits)

    output_path = project_root / "artifacts" / "ssot_violation_scan.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"\n[scanner] Report written to: {output_path.relative_to(project_root)}")

    s = report["summary"]
    w = 62
    print(f"\n{'=' * w}")
    print("SSOT VIOLATION SCAN — SUMMARY")
    print(f"{'=' * w}")
    print(f"  Total hits          : {s['total_hits']}")
    print(f"  REPLACE             : {s['replace_count']}  ← path construction, swap to constant")
    print(f"  WRONG_IMPORT        : {s['wrong_import_count']}  ← bad import path, use canonical")
    print(f"  SKIP_DYNAMIC        : {s['skip_dynamic_count']}  ← manual review")
    print(f"  SKIP_COMMENT        : {s['skip_comment_count']}")
    print(f"  SKIP_TEST_DATA      : {s['skip_test_data_count']}")
    print(f"  ── Actionable total : {s['actionable_total']}")

    print("\n  By category:")
    for cat, cnt in sorted(s["by_category"].items(), key=lambda x: -x[1]):
        print(f"    {cat:<25} {cnt}")

    print("\n  By constant (top 20):")
    for const, cnt in list(s["by_constant"].items())[:20]:
        print(f"    {const:<35} {cnt}")

    print("\n  Top offending files:")
    for entry in s["top_offending_files"][:20]:
        print(f"    [{entry['count']:>3}]  {entry['file']}")

    if summary_only:
        return 0

    # Detailed output filtered by --category
    show_cats = [filter_cat] if filter_cat else ["REPLACE", "WRONG_IMPORT"]
    for cat in show_cats:
        cat_hits = report["hits_by_classification"].get(cat, [])
        if not cat_hits:
            continue
        print(f"\n{'=' * w}")
        print(f"{cat} HITS ({len(cat_hits)} total)")
        print(f"{'=' * w}")
        for h in cat_hits:
            print(f"  {h['file']}:{h['line']}  [{h['ssot_constant']}]  <{h['category']}>")
            print(f"    {h['context']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

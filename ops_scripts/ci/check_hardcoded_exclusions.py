#!/usr/bin/env python3
"""R3 gate: detect hardcoded exclusion sets outside the allowlist (ratchet).

Problem: agents, enforcers, and scripts sometimes inline literal sets like
    exclude_dirs = {".git", "__pycache__", "archives", "node_modules", "venv"}
instead of importing from the canonical SSOT modules:
    - agentic_core.L0_routing.config.path_constants
      (GLOBAL_EXCLUDED_DIRS, SOVEREIGN_EXCLUDED_FOLDERS, DISCOVERY_EXCLUDED_TERRITORIES)
    - agentic_core.L5_safety.config.exclusion_loader
      (EXCLUDED_DIRS, get_excluded_directories)

These shadow SSOTs drift silently — a new entry added to the canonical
Python frozenset never reaches the hardcoded literal. This gate fails when it
finds a literal Python set/frozenset whose contents overlap heavily with the
canonical exclusion vocabulary.

Heuristic (conservative, low-false-positive):
    A Python set/frozenset literal is flagged when it contains >= MIN_HITS
    distinct tokens from CANONICAL_EXCLUSION_TOKENS, unless the containing
    file is in ALLOWLIST.

Ratchet mode (default): reads a frozen baseline of known violations from
artifacts/ci_baselines/hardcoded_exclusions_baseline.json and fails only on
net-new offenders. This lets us land the gate without blocking the tree on
the 37 pre-existing shadow sets — they become a tracked tech-debt burndown.

Exit 0 on clean (or baseline-match), 1 on net-new violations.

Usage:
    python ops_scripts/ci/check_hardcoded_exclusions.py
    python ops_scripts/ci/check_hardcoded_exclusions.py --path some/file.py
    python ops_scripts/ci/check_hardcoded_exclusions.py --refresh-baseline
    python ops_scripts/ci/check_hardcoded_exclusions.py --strict   # ignore baseline
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path
from typing import Iterable
from agentic_core.L0_routing.config.path_constants import WINDSURF_SCRIPTS_DIR

REPO_ROOT = Path(__file__).resolve().parents[2]
BASELINE_PATH = REPO_ROOT / "ops_scripts" / "ci" / "baselines" / "hardcoded_exclusions_baseline.json"

# Canonical exclusion tokens: any literal set containing >= MIN_HITS of these
# is treated as a shadow SSOT unless allowlisted.
CANONICAL_EXCLUSION_TOKENS: frozenset[str] = frozenset(
    {
        "__pycache__",
        ".git",
        ".github",
        ".venv",
        ".windsurf",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        "node_modules",
        "venv",
        "build",
        "dist",
        "htmlcov",
        ".tox",
        ".nox",
        "eggs",
        "artifacts",
        ".sovereign_healing_backup",
        ".healing_backups",
        "archives",
        "archive",
        "runtime_shared",
        "legacy_code",
        "legacy_engines",
        "stubs",
        "examples",
    },
)

MIN_HITS = 3  # Flag literal sets with 3+ canonical tokens

# Files where hardcoded sets are legitimate (source of truth, fallbacks,
# test fixtures that deliberately assert specific content).
ALLOWLIST_PATHS: frozenset[str] = frozenset(
    {
        # Canonical SSOTs
        "agentic_core/L0_routing/config/path_constants.py",
        "agentic_core/L5_safety/config/exclusion_loader.py",
        "agentic_core/L5_safety/config/structure_blueprint/ssot.py",
        # This gate itself (it references the tokens)
        "ops_scripts/ci/check_hardcoded_exclusions.py",
        # Generator (deliberately categorizes literal names)
        "tools/generate/generate_gitignore.py",
        # Test fixtures deliberately assert specific sets
        "tests/unit/tools/generate/test_generate_gitignore.py",
        "tests/unit/agentic_core/L5_safety/config/structure_blueprint/test_ssot_yaml_loading.py",
        # Hygiene healer — cleanup/delete ACTION targets (Write Surface domain literals),
        # semantically distinct from walk-exclusion sets. Sets ALWAYS_DELETE, DELETE_IF_OLD,
        # and temp/backup cleanup sets represent "what to mutate on disk", not "what to
        # exclude from scanning". Extracted tooling subset (L544) uses SSOT TOOLING_EXCLUDED_DIRS.
        "agentic_core/L5_safety/reasoning/root_hygiene_healer.py",
        # Sovereign index — DEFAULT_EXCLUDED_DIRS already imports GLOBAL_EXCLUDED_DIRS as
        # primary; the inline literal is a deliberate ImportError fallback (see line 190-204).
        "agentic_core/runtime/utils/sovereign_index_util.py",
        # W1-P1: DDDAlignmentAgent — uses SSOT GLOBAL_EXCLUDED_DIRS
        "agentic_core/L5_safety/reasoning/DDDAlignmentAgent.py",
        # W1-P1: PascalSovereigntyAgent — uses SSOT GLOBAL_EXCLUDED_DIRS + DISCOVERY_EXCLUDED_TERRITORIES
        # plus domain-specific ".env" for sovereignty checks (credential scanning domain)
        "agentic_core/L5_safety/reasoning/PascalSovereigntyAgent.py",
        # W1-P1: credential_scanner_util — uses SSOT GLOBAL_EXCLUDED_DIRS plus domain-specific
        # exclusions for credential scanning (.sovereign_healing_backup, healing_backups, coverage_html)
        "agentic_core/L5_safety/utils/credential_scanner_util.py",
        # W2-P1: constants_config — ImportError fallback when SSOT module cannot be loaded
        # (legitimate fallback pattern; cannot import SSOT in except block)
        "agentic_core/config/constants_config.py",
        # W2-P1: non_conforming_agent_finder_config — ImportError fallback when SSOT loading fails
        # (legitimate fallback pattern; cannot import SSOT in except block)
        "agentic_core/config/non_conforming_agent_finder_config.py",
        # W6-P1: apps_shared shim — test/compat shim DEFINING a fake path_constants module
        # for isolated test environments. The literal set IS the SSOT definition inside the
        # shim, not a replacement for it. Cannot import real SSOT here by design.
        "apps_shared/_compat/agentic_core_shim.py",
        # W6-P1: validate_structure — VALID_TERRITORIES is a territory allowlist (what
        # top-level dirs are valid), not an exclusion set. Semantically orthogonal to
        # GLOBAL_EXCLUDED_DIRS; must remain a deliberate literal.
        "ops_scripts/general/validate_structure.py",
    },
)

ALLOWLIST_PATH_PREFIXES: tuple[str, ...] = (
    # Archives / legacy — not production code
    "archives/",
    "tools/archive/",
    ".sovereign_healing_backup/",
    ".healing_backups/",
    # .venv and other scanner-excluded dirs
    ".venv/",
    # Generated / vendored
    "node_modules/",
    # W4-P1: RAG ingestion scripts — all 7 scripts share the same domain-specific
    # exclusion pattern (archives, artifacts, .windsurf, vector_store, data) which
    # is tied to ChromaDB ingestion topology, NOT generic file discovery. These
    # literal sets are semantically the RAG ingestion scope, not a hardcoded
    # replacement for GLOBAL_EXCLUDED_DIRS. Several scripts are retired (Wave B2).
    "tools/generate/ingestion/",
)

DEFAULT_SCAN_ROOTS: tuple[str, ...] = (
    "agentic_core",
    "apps_",  # Prefix match via glob
    "ops_scripts",
    "tools",
    WINDSURF_SCRIPTS_DIR,
)


def _is_allowlisted(rel_path: str) -> bool:
    rel_posix = rel_path.replace("\\", "/")
    if rel_posix in ALLOWLIST_PATHS:
        return True
    for prefix in ALLOWLIST_PATH_PREFIXES:
        if rel_posix.startswith(prefix):
            return True
    return False


def _extract_literal_set_strs(node: ast.AST) -> list[str]:
    """Return the list of string literal values in a set/frozenset literal node.

    Recognises:
        {"a", "b", "c"}                            -> ast.Set
        frozenset({"a", "b", "c"})                 -> ast.Call to frozenset()
        frozenset(("a", "b", "c"))                 -> ast.Call to frozenset()
        frozenset(["a", "b", "c"])                 -> ast.Call to frozenset()
    """
    values: list[str] = []

    def _collect(elts: Iterable[ast.expr]) -> None:
        for elt in elts:
            if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                values.append(elt.value)

    if isinstance(node, ast.Set):
        _collect(node.elts)
    elif isinstance(node, ast.Call):
        func = node.func
        is_frozenset = (isinstance(func, ast.Name) and func.id == "frozenset") or (
            isinstance(func, ast.Attribute) and func.attr == "frozenset"
        )
        if not is_frozenset or not node.args:
            return values
        arg = node.args[0]
        if isinstance(arg, (ast.Set, ast.List, ast.Tuple)):
            _collect(arg.elts)

    return values


def _scan_file(path: Path) -> list[tuple[int, list[str]]]:
    """Return list of (lineno, matched_tokens) for each offending set literal."""
    try:
        source = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError:
        return []
    violations: list[tuple[int, list[str]]] = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Set, ast.Call)):
            continue
        strs = _extract_literal_set_strs(node)
        if not strs:
            continue
        hits = sorted(set(strs) & CANONICAL_EXCLUSION_TOKENS)
        if len(hits) >= MIN_HITS:
            violations.append((getattr(node, "lineno", 0), hits))
    return violations


def _iter_python_files(roots: Iterable[str]) -> Iterable[Path]:
    for root in roots:
        # Support both exact dirs and apps_* glob
        if root.endswith("_"):
            # Wildcard match for apps_*, etc.
            for entry in REPO_ROOT.iterdir():
                if entry.is_dir() and entry.name.startswith(root):
                    yield from entry.rglob("*.py")
        else:
            root_path = REPO_ROOT / root
            if root_path.is_dir():
                yield from root_path.rglob("*.py")


def _load_baseline() -> set[str]:
    """Return frozen baseline keys as 'relpath:lineno' strings.

    Missing or malformed baseline -> empty set (strict mode).
    """
    if not BASELINE_PATH.exists():
        return set()
    try:
        data = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return set()
    entries = data.get("violations", []) if isinstance(data, dict) else []
    return {f"{e['path']}:{e['lineno']}" for e in entries if "path" in e and "lineno" in e}


def _write_baseline(violations: list[tuple[str, int, list[str]]]) -> None:
    BASELINE_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "description": (
            "Known hardcoded exclusion-set violations as of baseline freeze. "
            "These are tech debt; see R3 in "
            "docs/reports/exclusion-ssot-consolidated-review-2026-04-19.md. "
            "The gate blocks only NEW entries. Shrinking this baseline over time "
            "is the burndown goal."
        ),
        "count": len(violations),
        "violations": [
            {"path": rel, "lineno": lineno, "canonical_tokens": hits}
            for rel, lineno, hits in sorted(violations)
        ],
    }
    BASELINE_PATH.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    print(f"[hardcoded_exclusions] Baseline written: {BASELINE_PATH}", flush=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Detect hardcoded exclusion sets.")
    parser.add_argument(
        "--path",
        action="append",
        default=[],
        help="Specific file(s) to scan (repeatable). Defaults to repo-wide scan.",
    )
    parser.add_argument(
        "--show-tokens",
        action="store_true",
        help="Print the matched tokens for each violation.",
    )
    parser.add_argument(
        "--refresh-baseline",
        action="store_true",
        help="Overwrite the baseline with current violations and exit 0.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Ignore baseline and fail on ANY violation (for tracking burndown).",
    )
    args = parser.parse_args()

    if args.path:
        files: list[Path] = []
        for p in args.path:
            candidate = Path(p)
            if not candidate.is_absolute():
                candidate = REPO_ROOT / p
            if candidate.exists() and candidate.suffix == ".py":
                files.append(candidate)
    else:
        files = list(_iter_python_files(DEFAULT_SCAN_ROOTS))

    offending: list[tuple[str, int, list[str]]] = []
    for f in files:
        try:
            rel = f.relative_to(REPO_ROOT).as_posix()
        except ValueError:
            continue
        if _is_allowlisted(rel):
            continue
        for lineno, hits in _scan_file(f):
            offending.append((rel, lineno, hits))

    if args.refresh_baseline:
        _write_baseline(offending)
        print(
            f"[hardcoded_exclusions] Baseline refreshed with {len(offending)} violation(s).",
            flush=True,
        )
        return 0

    baseline = set() if args.strict else _load_baseline()
    net_new = [(rel, ln, hits) for rel, ln, hits in offending if f"{rel}:{ln}" not in baseline]
    retired = baseline - {f"{rel}:{ln}" for rel, ln, _ in offending}

    if net_new:
        print(
            f"[hardcoded_exclusions] FAIL: {len(net_new)} NEW shadow exclusion set(s) "
            f"(baseline size: {len(baseline)}).",
            flush=True,
        )
        for rel, lineno, hits in net_new:
            if args.show_tokens:
                print(f"  {rel}:{lineno}   tokens={hits}", flush=True)
            else:
                print(f"  {rel}:{lineno}   ({len(hits)} canonical tokens)", flush=True)
        print(
            "\n  Fix: import from agentic_core.L0_routing.config.path_constants "
            "(GLOBAL_EXCLUDED_DIRS / SOVEREIGN_EXCLUDED_FOLDERS / "
            "DISCOVERY_EXCLUDED_TERRITORIES) or "
            "agentic_core.L5_safety.config.exclusion_loader.get_excluded_directories().",
            flush=True,
        )
        print(
            "  If the literal is legitimate (test fixture, deliberate fallback), "
            "add the file path to ALLOWLIST_PATHS in "
            "ops_scripts/ci/check_hardcoded_exclusions.py.",
            flush=True,
        )
        return 1

    if retired:
        print(
            f"[hardcoded_exclusions] NOTE: {len(retired)} baseline entries retired "
            "(fixed). Run --refresh-baseline to shrink the tracked debt.",
            flush=True,
        )
        for entry in sorted(retired):
            print(f"  - {entry}", flush=True)

    if args.strict and offending:
        print(
            f"[hardcoded_exclusions] STRICT FAIL: {len(offending)} total violation(s).",
            flush=True,
        )
        return 1

    print(
        f"[hardcoded_exclusions] OK: scanned {len(files)} file(s); "
        f"{len(offending)} known, 0 net-new (baseline size: {len(baseline)}).",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

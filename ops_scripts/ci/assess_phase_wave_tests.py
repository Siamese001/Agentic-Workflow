"""
Guardian assessment script: phase/wave named test files.

Produces a structured report covering three questions per file:
  1. Does this file test CURRENT functionality (live imports, real logic)?
  2. Is there STRUCTURAL DUPLICATE logic in other tests/ files? (AST-based)
  3. VERDICT: DELETE | RENAME | KEEP-AS-IS | NEEDS-REVIEW

Duplicate detection method (AST-only, no execution, no imports):
  - For every test function in a phase/wave file, build a canonical structural
    fingerprint by walking the function's AST and emitting a normalised token
    sequence:  node type + operator type (where relevant).  All names, string
    literals, numeric literals and docstrings are replaced with typed
    placeholders (NAME, STR, NUM) so that two functions with identical logic
    but different variable names / assertion messages are still detected as
    duplicates.
  - The token sequence is SHA-256 hashed.
  - An index of {fingerprint -> [(file, func_name), ...]} is built across ALL
    non-phase/wave test files in tests/.
  - Phase/wave test functions whose fingerprint appears in the index are
    reported as STRUCTURAL_DUPLICATE with exact provenance.

Additionally, name-normalised matching is performed: phase/wave tokens are
stripped from test function names and the remainder is matched against the
corpus — catching cases where logic was slightly rewritten but covers the
same invariant.

Run with:
    python ops_scripts/ci/assess_phase_wave_tests.py

Exit codes:
    0  — all files have a clear verdict recorded
    1  — at least one file is NEEDS-REVIEW (requires manual action before
         delete/rename can proceed)

The script uses AST-only analysis — no test execution, no imports.
"""

from __future__ import annotations

import ast
import hashlib
import json
import sys
import textwrap
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from agentic_core.L0_routing.config.path_constants import TESTS_DIR, get_validated_project_root

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

# ---------------------------------------------------------------------------
# Repo layout
# ---------------------------------------------------------------------------
REPO_ROOT = get_validated_project_root()
TESTS_ROOT = REPO_ROOT / TESTS_DIR

# ---------------------------------------------------------------------------
# Phase/wave token detection
# ---------------------------------------------------------------------------

_PHASE_WAVE_TOKENS = ("phase", "wave")


def _is_phase_wave_file(path: Path) -> bool:
    name_lower = path.stem.lower()
    return any(tok in name_lower for tok in _PHASE_WAVE_TOKENS)


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------


def _find_phase_wave_files() -> list[Path]:
    found = []
    for p in TESTS_ROOT.rglob("*.py"):
        if "__pycache__" in p.parts:
            continue
        if _is_phase_wave_file(p):
            found.append(p)
    return sorted(found)


def _find_corpus_files(exclude: set[Path]) -> list[Path]:
    """All non-phase/wave .py test files outside _quarantine (active corpus)."""
    found = []
    for p in TESTS_ROOT.rglob("*.py"):
        if "__pycache__" in p.parts:
            continue
        if "_quarantine" in p.parts:
            continue
        if p in exclude:
            continue
        if _is_phase_wave_file(p):
            continue
        found.append(p)
    return sorted(found)


# ---------------------------------------------------------------------------
# AST helpers — parsing and basic extraction
# ---------------------------------------------------------------------------


def _parse_safe(path: Path) -> ast.Module | None:
    try:
        return ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        return None


def _extract_imports(tree: ast.Module) -> list[str]:
    modules: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                modules.append(node.module)
    return modules


def _extract_test_names(tree: ast.Module) -> list[str]:
    names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name.startswith("test_"):
                names.append(node.name)
    return names


def _extract_docstring(tree: ast.Module) -> str:
    try:
        return ast.get_docstring(tree) or ""
    except (AttributeError, TypeError):
        return ""


def _quarantine_headers(path: Path) -> dict[str, str]:
    headers: dict[str, str] = {}
    try:
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines()[:10]:
            line = line.strip()
            if line.startswith("# DELETE AFTER:"):
                headers["delete_after"] = line[len("# DELETE AFTER:") :].strip()
            elif line.startswith("# Superseded by:"):
                headers["superseded_by"] = line[len("# Superseded by:") :].strip()
            elif line.startswith("# QUARANTINE:"):
                headers["quarantine_reason"] = line[len("# QUARANTINE:") :].strip()
    except OSError:
        pass
    return headers


def _resolve_superseding_path(superseded_by_str: str) -> Path | None:
    part = superseded_by_str.split("(")[0].strip()
    candidate = REPO_ROOT / part
    if candidate.exists():
        return candidate
    for prefix in ("tests/", "tests\\"):
        if part.startswith(prefix):
            candidate = TESTS_ROOT / part[len(prefix) :]
            if candidate.exists():
                return candidate
    return None


def _check_imports_resolvable(imports: list[str]) -> tuple[list[str], list[str]]:
    _KNOWN_STDLIB_OR_THIRD_PARTY = {
        "ast",
        "os",
        "sys",
        "pathlib",
        "hashlib",
        "json",
        "re",
        "textwrap",
        "unittest",
        "dataclasses",
        "collections",
        "typing",
        "functools",
        "importlib",
        "tempfile",
        "pytest",
        "unittest.mock",
        "contextlib",
        "itertools",
        "copy",
        "abc",
        "io",
        "time",
        "datetime",
        "math",
        "random",
        "string",
        "struct",
        "threading",
        "subprocess",
    }
    found, missing = [], []
    for mod in imports:
        parts = mod.split(".")
        top = parts[0]
        if top in _KNOWN_STDLIB_OR_THIRD_PARTY:
            found.append(mod)
            continue
        as_dir = REPO_ROOT / Path(*parts)
        as_file = (
            REPO_ROOT / Path(*parts[:-1]) / f"{parts[-1]}.py"
            if len(parts) > 1
            else REPO_ROOT / f"{parts[0]}.py"
        )
        as_init = as_dir / "__init__.py"
        if as_dir.exists() or as_file.exists() or as_init.exists():
            found.append(mod)
        else:
            missing.append(mod)
    return found, missing


# ---------------------------------------------------------------------------
# AST structural fingerprinting
# ---------------------------------------------------------------------------
# Strategy: walk every node in the function body and emit a normalised token.
# Names → "NAME", string constants → "STR", numeric constants → "NUM",
# boolean/None constants → their repr, operators → op class name,
# AST node types → node class name.  Docstring-only Expr nodes at the top of
# the function are skipped (they are documentation, not logic).
# The token list is joined and SHA-256 hashed.


class _FingerprintVisitor(ast.NodeVisitor):
    """Emit a stable, normalised token sequence for an AST subtree."""

    def __init__(self) -> None:
        self.tokens: list[str] = []

    # ── leaf nodes ──────────────────────────────────────────────────────────

    def visit_Name(self, node: ast.Name) -> None:
        self.tokens.append("NAME")

    def visit_Attribute(self, node: ast.Attribute) -> None:
        self.tokens.append("ATTR")
        self.generic_visit(node)

    def visit_Constant(self, node: ast.Constant) -> None:
        if isinstance(node.value, bool) or node.value is None:
            self.tokens.append(repr(node.value))
        elif isinstance(node.value, str):
            self.tokens.append("STR")
        elif isinstance(node.value, (int, float, complex)):
            self.tokens.append("NUM")
        else:
            self.tokens.append("CONST")

    # ── structural nodes — emit type + recurse ───────────────────────────────

    def visit_Call(self, node: ast.Call) -> None:
        self.tokens.append("Call")
        self.tokens.append(f"nargs={len(node.args)}")
        self.tokens.append(f"nkw={len(node.keywords)}")
        self.generic_visit(node)

    def visit_Assert(self, node: ast.Assert) -> None:
        self.tokens.append("Assert")
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        self.tokens.append("Assign")
        self.generic_visit(node)

    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        self.tokens.append("AugAssign")
        self.tokens.append(type(node.op).__name__)
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        self.tokens.append("AnnAssign")
        self.generic_visit(node)

    def visit_Return(self, node: ast.Return) -> None:
        self.tokens.append("Return")
        self.generic_visit(node)

    def visit_Raise(self, node: ast.Raise) -> None:
        self.tokens.append("Raise")
        self.generic_visit(node)

    def visit_If(self, node: ast.If) -> None:
        self.tokens.append("If")
        self.tokens.append(f"nbody={len(node.body)}")
        self.tokens.append(f"norelse={len(node.orelse)}")
        self.generic_visit(node)

    def visit_For(self, node: ast.For) -> None:
        self.tokens.append("For")
        self.generic_visit(node)

    def visit_While(self, node: ast.While) -> None:
        self.tokens.append("While")
        self.generic_visit(node)

    def visit_With(self, node: ast.With) -> None:
        self.tokens.append("With")
        self.tokens.append(f"nitems={len(node.items)}")
        self.generic_visit(node)

    def visit_Try(self, node: ast.Try) -> None:
        self.tokens.append("Try")
        self.tokens.append(f"nhandlers={len(node.handlers)}")
        self.generic_visit(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        self.tokens.append("ExceptHandler")
        self.generic_visit(node)

    def visit_BoolOp(self, node: ast.BoolOp) -> None:
        self.tokens.append(f"BoolOp:{type(node.op).__name__}")
        self.generic_visit(node)

    def visit_BinOp(self, node: ast.BinOp) -> None:
        self.tokens.append(f"BinOp:{type(node.op).__name__}")
        self.generic_visit(node)

    def visit_UnaryOp(self, node: ast.UnaryOp) -> None:
        self.tokens.append(f"UnaryOp:{type(node.op).__name__}")
        self.generic_visit(node)

    def visit_Compare(self, node: ast.Compare) -> None:
        ops = ":".join(type(op).__name__ for op in node.ops)
        self.tokens.append(f"Compare:{ops}")
        self.generic_visit(node)

    def visit_ListComp(self, node: ast.ListComp) -> None:
        self.tokens.append("ListComp")
        self.generic_visit(node)

    def visit_DictComp(self, node: ast.DictComp) -> None:
        self.tokens.append("DictComp")
        self.generic_visit(node)

    def visit_SetComp(self, node: ast.SetComp) -> None:
        self.tokens.append("SetComp")
        self.generic_visit(node)

    def visit_GeneratorExp(self, node: ast.GeneratorExp) -> None:
        self.tokens.append("GeneratorExp")
        self.generic_visit(node)

    def visit_Lambda(self, node: ast.Lambda) -> None:
        self.tokens.append("Lambda")
        self.generic_visit(node)

    def visit_Subscript(self, node: ast.Subscript) -> None:
        self.tokens.append("Subscript")
        self.generic_visit(node)

    def visit_Dict(self, node: ast.Dict) -> None:
        self.tokens.append(f"Dict:n={len(node.keys)}")
        self.generic_visit(node)

    def visit_List(self, node: ast.List) -> None:
        self.tokens.append(f"List:n={len(node.elts)}")
        self.generic_visit(node)

    def visit_Tuple(self, node: ast.Tuple) -> None:
        self.tokens.append(f"Tuple:n={len(node.elts)}")
        self.generic_visit(node)

    def visit_Set(self, node: ast.Set) -> None:
        self.tokens.append(f"Set:n={len(node.elts)}")
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        # Local imports inside functions
        self.tokens.append(f"Import:n={len(node.names)}")

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        self.tokens.append(f"ImportFrom:n={len(node.names)}")

    def visit_Global(self, node: ast.Global) -> None:
        self.tokens.append("Global")

    def visit_Nonlocal(self, node: ast.Nonlocal) -> None:
        self.tokens.append("Nonlocal")

    def visit_Delete(self, node: ast.Delete) -> None:
        self.tokens.append("Delete")
        self.generic_visit(node)

    def visit_Expr(self, node: ast.Expr) -> None:
        self.tokens.append("Expr")
        self.generic_visit(node)

    def visit_Pass(self, node: ast.Pass) -> None:
        self.tokens.append("Pass")

    def visit_Break(self, node: ast.Break) -> None:
        self.tokens.append("Break")

    def visit_Continue(self, node: ast.Continue) -> None:
        self.tokens.append("Continue")

    def visit_Yield(self, node: ast.Yield) -> None:
        self.tokens.append("Yield")
        self.generic_visit(node)

    def visit_YieldFrom(self, node: ast.YieldFrom) -> None:
        self.tokens.append("YieldFrom")
        self.generic_visit(node)

    def visit_Await(self, node: ast.Await) -> None:
        self.tokens.append("Await")
        self.generic_visit(node)

    def visit_JoinedStr(self, node: ast.JoinedStr) -> None:
        # f-string
        self.tokens.append("FStr")
        self.generic_visit(node)

    def visit_IfExp(self, node: ast.IfExp) -> None:
        self.tokens.append("IfExp")
        self.generic_visit(node)

    def visit_Starred(self, node: ast.Starred) -> None:
        self.tokens.append("Starred")
        self.generic_visit(node)

    def visit_FormattedValue(self, node: ast.FormattedValue) -> None:
        self.tokens.append("FormattedValue")
        self.generic_visit(node)


def _function_body_nodes(
    func: ast.FunctionDef | ast.AsyncFunctionDef,
) -> list[ast.stmt]:
    """Return body statements, skipping a leading docstring-only Expr node."""
    body = func.body
    if (
        body
        and isinstance(body[0], ast.Expr)
        and isinstance(body[0].value, ast.Constant)
        and isinstance(body[0].value.value, str)
    ):
        return body[1:]
    return body


def _structural_fingerprint(
    func: ast.FunctionDef | ast.AsyncFunctionDef,
) -> str:
    """
    Return a SHA-256 hex digest representing the structural skeleton of the
    function body.  All names and literal values are normalised so that two
    functions with identical logic but different identifiers/messages still
    produce the same fingerprint.

    Additionally encode:
      - number of arguments (arity)
      - async vs sync
      - number of body statements (rough complexity signal)
    """
    visitor = _FingerprintVisitor()
    stmts = _function_body_nodes(func)
    for stmt in stmts:
        visitor.visit(stmt)

    is_async = isinstance(func, ast.AsyncFunctionDef)
    arity = len(func.args.args) + len(func.args.posonlyargs) + len(func.args.kwonlyargs)
    prefix = f"async={is_async}:arity={arity}:nstmt={len(stmts)}:"
    token_str = prefix + "|".join(visitor.tokens)
    return hashlib.sha256(token_str.encode()).hexdigest()


# ---------------------------------------------------------------------------
# Corpus index: fingerprint → [(rel_path, func_name), ...]
# Also builds name-normalised index: normalised_name → [(rel_path, func_name)]
# ---------------------------------------------------------------------------


@dataclass
class CorpusEntry:
    rel_path: str
    func_name: str


def _strip_phase_wave_tokens(name: str) -> str:
    """
    Strip phase/wave migration tokens from a test function name to get the
    semantic core.  Examples:
      test_phase10_embedding_activation  → embedding_activation
      test_wave2_upward_import_detected  → upward_import_detected
      test_w10_replay_determinism        → replay_determinism
    """
    stem = name[len("test_") :] if name.startswith("test_") else name
    # Remove numeric-prefixed tokens like phase10_, wave2_, w10_, p2_
    import re as _re

    stem = _re.sub(r"^(phase|wave|w|p)\d+[_.]", "", stem, flags=_re.IGNORECASE)
    # Also strip plain phase/wave prefix without number
    stem = _re.sub(r"^(phase|wave)[_.]", "", stem, flags=_re.IGNORECASE)
    return stem.lower().strip("_")


@dataclass
class CorpusIndex:
    # fingerprint (SHA-256 hex) → list of entries in the NON-phase/wave corpus
    by_fingerprint: dict[str, list[CorpusEntry]] = field(default_factory=dict)
    # normalised name → list of entries
    by_normalised_name: dict[str, list[CorpusEntry]] = field(default_factory=dict)
    # statistics
    files_indexed: int = 0
    functions_indexed: int = 0
    parse_failures: list[str] = field(default_factory=list)


def _collect_func_nodes(
    tree: ast.Module,
) -> list[ast.FunctionDef | ast.AsyncFunctionDef]:
    """Collect all FunctionDef/AsyncFunctionDef nodes that start with test_."""
    result = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name.startswith("test_"):
                result.append(node)
    return result


def _build_corpus_index(corpus_files: list[Path]) -> CorpusIndex:
    idx = CorpusIndex()
    for p in corpus_files:
        tree = _parse_safe(p)
        if tree is None:
            idx.parse_failures.append(str(p.relative_to(REPO_ROOT)).replace("\\", "/"))
            continue
        idx.files_indexed += 1
        rel = str(p.relative_to(REPO_ROOT)).replace("\\", "/")
        funcs = _collect_func_nodes(tree)
        for fn in funcs:
            idx.functions_indexed += 1
            entry = CorpusEntry(rel_path=rel, func_name=fn.name)
            # structural fingerprint
            fp = _structural_fingerprint(fn)
            idx.by_fingerprint.setdefault(fp, []).append(entry)
            # normalised name
            norm = _strip_phase_wave_tokens(fn.name)
            if norm:
                idx.by_normalised_name.setdefault(norm, []).append(entry)
    return idx


# ---------------------------------------------------------------------------
# Per-function duplicate result
# ---------------------------------------------------------------------------


@dataclass
class FuncDuplicateResult:
    func_name: str
    fingerprint: str
    structural_matches: list[CorpusEntry] = field(default_factory=list)
    name_matches: list[CorpusEntry] = field(default_factory=list)

    @property
    def has_structural_duplicate(self) -> bool:
        return bool(self.structural_matches)

    @property
    def has_name_duplicate(self) -> bool:
        return bool(self.name_matches)

    @property
    def is_duplicate(self) -> bool:
        return self.has_structural_duplicate or self.has_name_duplicate


def _check_duplicates(path: Path, tree: ast.Module, idx: CorpusIndex) -> list[FuncDuplicateResult]:
    results = []
    for fn in _collect_func_nodes(tree):
        fp = _structural_fingerprint(fn)
        norm = _strip_phase_wave_tokens(fn.name)
        rel_self = str(path.relative_to(REPO_ROOT)).replace("\\", "/")

        struct_matches = [e for e in idx.by_fingerprint.get(fp, []) if e.rel_path != rel_self]
        name_matches = (
            [e for e in idx.by_normalised_name.get(norm, []) if e.rel_path != rel_self] if norm else []
        )

        # Deduplicate name matches already captured by structural match
        struct_match_keys = {(e.rel_path, e.func_name) for e in struct_matches}
        name_matches_deduped = [e for e in name_matches if (e.rel_path, e.func_name) not in struct_match_keys]

        results.append(
            FuncDuplicateResult(
                func_name=fn.name,
                fingerprint=fp,
                structural_matches=struct_matches,
                name_matches=name_matches_deduped,
            )
        )
    return results


# ---------------------------------------------------------------------------
# Per-file verdict dataclass
# ---------------------------------------------------------------------------

Verdict = Literal["DELETE", "RENAME", "KEEP-AS-IS", "NEEDS-REVIEW"]


@dataclass
class FileVerdict:
    path: Path
    rel_path: str
    quarantine_reason: str = ""
    delete_after: str = ""
    superseded_by: str = ""
    superseding_exists: bool = False
    superseding_path: str = ""
    test_names: list[str] = field(default_factory=list)
    imports: list[str] = field(default_factory=list)
    missing_imports: list[str] = field(default_factory=list)
    docstring_snippet: str = ""
    func_duplicate_results: list[FuncDuplicateResult] = field(default_factory=list)
    duplicate_logic_notes: str = ""
    functionality_assessment: str = ""
    verdict: Verdict = "NEEDS-REVIEW"
    suggested_name: str = ""
    rationale: str = ""
    parse_ok: bool = True

    @property
    def total_funcs(self) -> int:
        return len(self.func_duplicate_results)

    @property
    def structural_dup_count(self) -> int:
        return sum(1 for r in self.func_duplicate_results if r.has_structural_duplicate)

    @property
    def name_dup_count(self) -> int:
        return sum(1 for r in self.func_duplicate_results if r.has_name_duplicate)

    @property
    def unique_func_count(self) -> int:
        return sum(1 for r in self.func_duplicate_results if not r.is_duplicate)


def _assess_file(path: Path, idx: CorpusIndex) -> FileVerdict:
    rel = str(path.relative_to(REPO_ROOT)).replace("\\", "/")
    v = FileVerdict(path=path, rel_path=rel)

    tree = _parse_safe(path)
    if tree is None:
        v.parse_ok = False
        v.verdict = "NEEDS-REVIEW"
        v.rationale = "SyntaxError — cannot parse"
        return v

    v.docstring_snippet = _extract_docstring(tree)[:200].replace("\n", " ")
    v.test_names = _extract_test_names(tree)
    v.imports = _extract_imports(tree)
    _, v.missing_imports = _check_imports_resolvable(v.imports)

    headers = _quarantine_headers(path)
    v.quarantine_reason = headers.get("quarantine_reason", "")
    v.delete_after = headers.get("delete_after", "")
    v.superseded_by = headers.get("superseded_by", "")

    if v.superseded_by:
        sup_path = _resolve_superseding_path(v.superseded_by)
        v.superseding_exists = sup_path is not None and sup_path.exists()
        if sup_path and v.superseding_exists:
            v.superseding_path = str(sup_path.relative_to(REPO_ROOT)).replace("\\", "/")

    # AST duplicate check (only for parseable files)
    v.func_duplicate_results = _check_duplicates(path, tree, idx)

    return v


# ---------------------------------------------------------------------------
# Verdict rules
# ---------------------------------------------------------------------------

# Convention: file names in tests/ use functional descriptions, not phase/wave
# labels.  e.g. test_routing_hash_invariants.py, not test_phase13_...
#
# Rule set:
#   A) File is in _quarantine/ AND has a QUARANTINE header AND superseding EXISTS
#      → DELETE (isolated, superseded, tracked in QUARANTINE_MANIFEST.json)
#   B) File is in _quarantine/ AND has QUARANTINE header BUT superseder MISSING
#      → NEEDS-REVIEW (cannot delete until superseder is created)
#   C) File is in _quarantine/ AND is a _1 mechanical duplicate
#      → DELETE
#   D) File is in _quarantine/ WITHOUT a quarantine header
#      → NEEDS-REVIEW (unexpected — manual inspection)
#   E) Active file: ALL test functions are structural duplicates of corpus files
#      → DELETE (100% coverage redundancy confirmed by AST)
#   F) Active file: SOME test functions are structural duplicates
#      → RENAME + note which functions are duplicated
#   G) Active file: in rename map, no structural duplicates detected
#      → RENAME (naming only — logic is unique)
#   H) Active file: in eval rename map
#      → RENAME (evaluation pipeline stages, not migration)
#   I) Active file: has missing imports
#      → NEEDS-REVIEW (broken test)
#   J) Active file: none of the above
#      → KEEP-AS-IS with note

_RENAME_MAP: dict[str, tuple[str, str]] = {
    "test_wave1_phase1_2_sovereignty": (
        "test_provider_import_sovereignty",
        "Tests direct-provider-import detection and upward-import guard in "
        "ASTAnalyzer — purely functional, no phase dependency.",
    ),
    "test_wave1_phase1_3_governance": (
        "test_governance_stamp_wiring",
        "Tests governance/elevator-shaft hint detection and gap generation — purely functional.",
    ),
    "test_wave1_phase1_parse_failures_and_ssot_paths": (
        "test_ssot_parse_failures_and_component_paths",
        "Tests parse-failure remediation + SSOT component path correctness — purely functional invariant.",
    ),
    "test_wave2_phase2_1_advanced_governance": (
        "test_layer_connection_integrity",
        "Tests analyze_layer_connection_integrity branches (upward import, "
        "gateway bypass, mutation risk, PathD) — purely functional.",
    ),
    "test_wave2_phase2_2_embedding_sovereignty": (
        "test_rag_embedding_sovereignty",
        "Tests analyze_rag_embedding_sovereignty allowed/disallowed placements — purely functional.",
    ),
    "test_wave2_phase2_3_prompt_taxonomy": (
        "test_prompt_taxonomy_coverage",
        "Tests analyze_prompt_taxonomy_coverage slot/manifest/validator branches — purely functional.",
    ),
    "test_wave3_phase3_1_cache_wirings": (
        "test_cache_wiring_gap_detection",
        "Tests L0/L1 cache-import gap detection in SemanticGapAnalyzer — purely functional.",
    ),
    "test_wave3_phase3_2_boundary_hardening": (
        "test_layer_boundary_gap_detection",
        "Tests L2-L6 boundary gap detection (validator/orchestrator/blob/"
        "safety/telemetry) — purely functional.",
    ),
    "test_wave3_phase3_3_finalization": (
        "test_semantic_gap_analyzer_run_and_report",
        "Tests run_analysis() + generate_report() output contract — purely functional.",
    ),
    "test_wave1_cda_sync_wrapper": (
        "test_cognitive_disposition_agent_sync_api",
        "Tests CognitiveDispositionAgent exposes sync analyze_violation() — "
        "pure structural contract, not wave-specific.",
    ),
    "test_wave2_gravity_exclusion": (
        "test_gravity_leak_repair_exclusion_paths",
        "Tests GravityLeakRepairAgent excluded_paths field in StructureConfig — pure structural contract.",
    ),
    "test_wave4_v15_agent_id": (
        "test_v15_gateway_execute_agent_id_required",
        "Tests all V15ExecutionGateway.execute() call sites supply agent_id — "
        "pure call-site invariant, not wave-specific.",
    ),
    "test_wave5_longpaths_guard": (
        "test_longpaths_bypass_guard",
        "Tests AGENTIC_BYPASS_LONGPATHS_CHECK guard in execute_ssot.py — pure structural invariant.",
    ),
    "test_wave6_hitl_gates": (
        "test_hitl_gate_wiring",
        "Tests HITL gate wiring at all required trigger points — "
        "pure structural contract, not wave-specific.",
    ),
    "test_healers_wave6": (
        "test_healer_contracts",
        "Tests healer dry-run/apply modes and registry — pure contract test, wave label is cosmetic.",
    ),
    "test_v15_p2_wave2_1_inventory": (
        "test_runtime_entrypoint_inventory_schema",
        "Tests v15_phase2_wave2_1_runtime_entrypoints.json schema and content — "
        "rename to reflect the JSON artifact it validates.",
    ),
    "test_wave0c_meta_learning_intake_wiring": (
        "test_meta_learning_intake_wiring",
        "Tests _fire_meta_learning_intake wiring in execute_ssot.py — purely functional invariant.",
    ),
    "test_req253_254_cross_wave_linkage": (
        "test_cross_wave_audit_hash_linkage",
        "Tests REQ-253/254 WaveAuditSummary prev_wave_hash linkage — "
        "'wave' is a domain concept (audit chain), not a migration phase; "
        "rename removes ambiguity.",
    ),
}

_EVAL_RENAME_MAP: dict[str, tuple[str, str]] = {
    "test_phase1_metrics": (
        "test_evaluation_metrics",
        "Tests PrecisionAtK, RecallAtK, MRR, NDCG, Groundedness, AnswerCorrectness — "
        "evaluation framework metrics, phase number is pipeline stage label.",
    ),
    "test_phase1_runners": (
        "test_evaluation_runners",
        "Tests evaluation pipeline runners — evaluation framework, not migration.",
    ),
    "test_phase1_schemas": (
        "test_evaluation_schemas",
        "Tests evaluation schema contracts — evaluation framework.",
    ),
    "test_phase2_retrieval": (
        "test_evaluation_retrieval",
        "Tests retrieval evaluation pipeline — evaluation framework.",
    ),
    "test_phase3_chunking": (
        "test_evaluation_chunking",
        "Tests chunking evaluation pipeline — evaluation framework.",
    ),
    "test_phase4_monitoring": (
        "test_evaluation_monitoring",
        "Tests monitoring evaluation pipeline — evaluation framework.",
    ),
    "test_phase5_feedback": (
        "test_evaluation_feedback",
        "Tests feedback evaluation pipeline — evaluation framework.",
    ),
    "test_phase6_completeness_retrieval": (
        "test_evaluation_completeness_retrieval",
        "Tests completeness+retrieval evaluation — evaluation framework.",
    ),
}

_DUPLICATE_SUFFIX_PATTERN = "_1"


def _format_dup_results(results: list[FuncDuplicateResult], max_per_func: int = 2) -> str:
    """Compact one-line summary of duplicate findings."""
    parts = []
    for r in results:
        if r.has_structural_duplicate:
            matches = r.structural_matches[:max_per_func]
            refs = "; ".join(f"{e.func_name}@{e.rel_path}" for e in matches)
            parts.append(f"STRUCTURAL: {r.func_name} → {refs}")
        elif r.has_name_duplicate:
            matches = r.name_matches[:max_per_func]
            refs = "; ".join(f"{e.func_name}@{e.rel_path}" for e in matches)
            parts.append(f"NAME-MATCH: {r.func_name} → {refs}")
    return " | ".join(parts) if parts else ""


def _apply_verdicts(verdicts: list[FileVerdict]) -> None:
    for v in verdicts:
        in_quarantine = "_quarantine" in v.rel_path

        # ── Quarantine files ─────────────────────────────────────────────────
        if in_quarantine:
            v.functionality_assessment = "QUARANTINED — not in active test suite"
            if v.quarantine_reason:
                if v.superseded_by and v.superseding_exists:
                    v.verdict = "DELETE"
                    v.rationale = (
                        f"In _quarantine, QUARANTINE header present, superseded by "
                        f"{v.superseding_path} which EXISTS. Safe to remove — "
                        f"tracked in QUARANTINE_MANIFEST.json."
                    )
                    v.duplicate_logic_notes = f"Superseding file covers invariants: {v.superseded_by}"
                elif v.superseded_by and not v.superseding_exists:
                    v.verdict = "NEEDS-REVIEW"
                    v.rationale = (
                        f"QUARANTINE header says superseded by '{v.superseded_by}' "
                        f"but that file does NOT exist. Cannot delete until the "
                        f"superseding test is created."
                    )
                else:
                    v.verdict = "DELETE"
                    v.rationale = (
                        "In _quarantine with QUARANTINE header. assertion_rot category — "
                        "tests OpenAI/provider-specific code no longer in the system."
                    )
            else:
                if v.path.stem.endswith(_DUPLICATE_SUFFIX_PATTERN):
                    base_stem = v.path.stem[: -len(_DUPLICATE_SUFFIX_PATTERN)]
                    base_path = v.path.parent / f"{base_stem}.py"
                    if base_path.exists():
                        v.verdict = "DELETE"
                        v.duplicate_logic_notes = (
                            f"Mechanical _1 duplicate of {base_path.relative_to(REPO_ROOT)}"
                        )
                        v.rationale = (
                            f"Mechanically generated _1 duplicate of {base_stem}.py "
                            f"— identical content, safe to delete."
                        )
                    else:
                        v.verdict = "NEEDS-REVIEW"
                        v.rationale = "No base file found for _1 suffix duplicate."
                else:
                    v.verdict = "NEEDS-REVIEW"
                    v.rationale = "In _quarantine but no QUARANTINE header found — unexpected."
            continue

        # ── Active (non-quarantine) files ────────────────────────────────────
        stem = v.path.stem
        dup_summary = _format_dup_results([r for r in v.func_duplicate_results if r.is_duplicate])

        # Rule E: 100% structural duplicate coverage → DELETE
        if v.total_funcs > 0 and v.structural_dup_count == v.total_funcs and v.unique_func_count == 0:
            v.verdict = "DELETE"
            v.functionality_assessment = (
                f"ALL {v.total_funcs} test functions are structural duplicates "
                f"of functions in the active corpus."
            )
            v.duplicate_logic_notes = dup_summary
            v.rationale = (
                "100% structural duplicate coverage confirmed by AST fingerprint "
                "comparison. No unique logic remains in this file."
            )
            continue

        # Rule F: partial structural duplicates detected
        if v.structural_dup_count > 0:
            struct_pct = int(100 * v.structural_dup_count / max(v.total_funcs, 1))
            if stem in _RENAME_MAP:
                suggested, base_rationale = _RENAME_MAP[stem]
                v.suggested_name = f"{suggested}.py"
                v.verdict = "RENAME"
                v.rationale = (
                    f"{base_rationale}  "
                    f"NOTE: {v.structural_dup_count}/{v.total_funcs} functions "
                    f"({struct_pct}%) have structural duplicates in the corpus — "
                    f"merge unique tests into the renamed file, remove duplicates."
                )
            elif stem in _EVAL_RENAME_MAP:
                suggested, base_rationale = _EVAL_RENAME_MAP[stem]
                v.suggested_name = f"{suggested}.py"
                v.verdict = "RENAME"
                v.rationale = (
                    f"{base_rationale}  "
                    f"NOTE: {v.structural_dup_count}/{v.total_funcs} functions "
                    f"({struct_pct}%) are structural duplicates."
                )
            else:
                v.verdict = "NEEDS-REVIEW"
                v.rationale = (
                    f"{v.structural_dup_count}/{v.total_funcs} functions ({struct_pct}%) "
                    f"are structural duplicates of corpus functions. "
                    f"Merge unique tests, delete duplicates."
                )
            v.functionality_assessment = (
                f"{v.unique_func_count}/{v.total_funcs} unique functions; "
                f"{v.structural_dup_count} structural dup(s); "
                f"{v.name_dup_count} name-only match(es)."
            )
            v.duplicate_logic_notes = dup_summary
            existing = v.path.parent / f"{v.suggested_name}" if v.suggested_name else None
            if existing and existing.exists():
                v.verdict = "NEEDS-REVIEW"
                v.rationale += f" WARNING: {v.suggested_name} already exists — manual merge required."
            continue

        # Rule G: in rename map, no structural duplicates
        if stem in _RENAME_MAP:
            suggested, rationale = _RENAME_MAP[stem]
            v.suggested_name = f"{suggested}.py"
            v.verdict = "RENAME"
            v.rationale = rationale
            v.functionality_assessment = (
                f"Tests CURRENT functionality. {v.total_funcs} functions, 0 structural duplicates detected."
            )
            if v.name_dup_count:
                v.duplicate_logic_notes = (
                    f"{v.name_dup_count} name-match(es) found (different body): "
                    + _format_dup_results([r for r in v.func_duplicate_results if r.has_name_duplicate])
                )
            existing = v.path.parent / f"{suggested}.py"
            if existing.exists():
                v.verdict = "NEEDS-REVIEW"
                v.rationale += f" NOTE: {suggested}.py already exists — manual merge required."
            continue

        # Rule H: in eval rename map
        if stem in _EVAL_RENAME_MAP:
            suggested, rationale = _EVAL_RENAME_MAP[stem]
            v.suggested_name = f"{suggested}.py"
            v.verdict = "RENAME"
            v.rationale = rationale
            v.functionality_assessment = (
                f"Tests CURRENT evaluation framework (agentic_core.evaluation.*). "
                f"{v.total_funcs} functions, 0 structural duplicates."
            )
            existing = v.path.parent / f"{suggested}.py"
            if existing.exists():
                v.verdict = "NEEDS-REVIEW"
                v.rationale += f" NOTE: {suggested}.py already exists — manual merge required."
            continue

        # Rule I: missing imports
        if v.missing_imports:
            v.verdict = "NEEDS-REVIEW"
            v.functionality_assessment = f"Has {len(v.missing_imports)} unresolvable import(s): " + ", ".join(
                v.missing_imports[:5]
            )
            v.rationale = "Cannot assess fully without resolving missing imports."
            continue

        # Rule J: everything else
        v.verdict = "KEEP-AS-IS"
        v.functionality_assessment = (
            f"References live modules. {v.total_funcs} functions, {v.structural_dup_count} structural dup(s)."
        )
        v.rationale = (
            "Not in rename map — review manually to determine if phase/wave label "
            "is a domain concept (e.g. audit chain) or migration artifact."
        )


# ---------------------------------------------------------------------------
# Report rendering
# ---------------------------------------------------------------------------

_VERDICT_ORDER = {"DELETE": 0, "RENAME": 1, "KEEP-AS-IS": 2, "NEEDS-REVIEW": 3}
_VERDICT_SYMBOL = {
    "DELETE": "DELETE",
    "RENAME": "RENAME",
    "KEEP-AS-IS": "KEEP-AS-IS",
    "NEEDS-REVIEW": "NEEDS-REVIEW",
}


def _print_report(verdicts: list[FileVerdict], idx: CorpusIndex) -> None:
    verdicts_sorted = sorted(verdicts, key=lambda v: (_VERDICT_ORDER[v.verdict], v.rel_path))
    counts = {k: sum(1 for v in verdicts if v.verdict == k) for k in _VERDICT_ORDER}

    W = 100
    print("=" * W)
    print("PHASE/WAVE TEST FILE ASSESSMENT — AST STRUCTURAL DUPLICATE REPORT")
    print("=" * W)
    print(
        f"Phase/wave files: {len(verdicts)}  |  "
        f"Corpus files indexed: {idx.files_indexed}  |  "
        f"Corpus functions indexed: {idx.functions_indexed}  |  "
        f"Corpus parse failures: {len(idx.parse_failures)}"
    )
    for verdict, count in counts.items():
        print(f"  {_VERDICT_SYMBOL[verdict]}: {count}")
    print()

    for verdict_key in ("DELETE", "RENAME", "KEEP-AS-IS", "NEEDS-REVIEW"):
        group = [v for v in verdicts_sorted if v.verdict == verdict_key]
        if not group:
            continue
        print(f"{'─' * W}")
        print(f"  {_VERDICT_SYMBOL[verdict_key]}  ({len(group)} files)")
        print(f"{'─' * W}")
        for v in group:
            print(f"\n  FILE : {v.rel_path}")
            if v.quarantine_reason:
                print(f"  QUAR : {v.quarantine_reason}")
            if v.superseded_by:
                exists_str = "(EXISTS)" if v.superseding_exists else "(MISSING)"
                print(f"  SUP  : {v.superseded_by} {exists_str}")
            if v.suggested_name:
                parent_rel = str(v.path.parent.relative_to(REPO_ROOT)).replace("\\", "/")
                print(f"  NEW  : {parent_rel}/{v.suggested_name}")
            print(f"  FUNC : {v.functionality_assessment}")
            # Per-function duplicate breakdown (non-quarantine only)
            if "_quarantine" not in v.rel_path and v.func_duplicate_results:
                dup_funcs = [r for r in v.func_duplicate_results if r.is_duplicate]
                unique_funcs = [r for r in v.func_duplicate_results if not r.is_duplicate]
                if dup_funcs:
                    print(f"  DUPS : {len(dup_funcs)} duplicate function(s):")
                    for r in dup_funcs[:8]:
                        kind = "STRUCT" if r.has_structural_duplicate else "NAME"
                        matches = r.structural_matches or r.name_matches
                        match_str = "; ".join(f"{e.func_name} @ {e.rel_path}" for e in matches[:2])
                        print(f"         [{kind}] {r.func_name}")
                        print(f"                  → {match_str}")
                    if len(dup_funcs) > 8:
                        print(f"         ... (+{len(dup_funcs) - 8} more)")
                if unique_funcs:
                    names = ", ".join(r.func_name for r in unique_funcs[:6])
                    if len(unique_funcs) > 6:
                        names += f" (+{len(unique_funcs) - 6} more)"
                    print(f"  UNIQ : {names}")
            print(f"  WHY  : {textwrap.fill(v.rationale, width=W - 9, subsequent_indent=' ' * 9)}")
        print()

    # Sprawl summary
    print("=" * W)
    print("SPRAWL SUMMARY")
    print("=" * W)
    active = [v for v in verdicts if "_quarantine" not in v.rel_path]
    total_funcs = sum(v.total_funcs for v in active)
    total_struct_dups = sum(v.structural_dup_count for v in active)
    total_unique = sum(v.unique_func_count for v in active)
    print(f"  Active phase/wave files  : {len(active)}")
    print(f"  Total test functions     : {total_funcs}")
    print(f"  Structural duplicates    : {total_struct_dups}")
    print(f"  Unique functions         : {total_unique}")
    if total_funcs:
        dup_pct = int(100 * total_struct_dups / total_funcs)
        unique_pct = 100 - dup_pct
        print(f"  Duplication rate         : {dup_pct}%  (unique signal: {unique_pct}%)")
    print()


def _emit_json(verdicts: list[FileVerdict], idx: CorpusIndex, output_path: Path) -> None:
    data = {
        "corpus_stats": {
            "files_indexed": idx.files_indexed,
            "functions_indexed": idx.functions_indexed,
            "parse_failures": idx.parse_failures,
        },
        "verdicts": [],
    }
    for v in verdicts:
        dup_details = [
            {
                "func_name": r.func_name,
                "fingerprint": r.fingerprint[:16] + "...",
                "structural_matches": [
                    {"rel_path": e.rel_path, "func_name": e.func_name} for e in r.structural_matches[:5]
                ],
                "name_matches": [
                    {"rel_path": e.rel_path, "func_name": e.func_name} for e in r.name_matches[:5]
                ],
            }
            for r in v.func_duplicate_results
            if r.is_duplicate
        ]
        data["verdicts"].append(
            {
                "path": v.rel_path,
                "verdict": v.verdict,
                "suggested_name": v.suggested_name,
                "quarantine_reason": v.quarantine_reason,
                "superseded_by": v.superseded_by,
                "superseding_exists": v.superseding_exists,
                "superseding_path": v.superseding_path,
                "total_funcs": v.total_funcs,
                "structural_dup_count": v.structural_dup_count,
                "name_dup_count": v.name_dup_count,
                "unique_func_count": v.unique_func_count,
                "missing_imports": v.missing_imports,
                "functionality_assessment": v.functionality_assessment,
                "duplicate_logic_notes": v.duplicate_logic_notes,
                "rationale": v.rationale,
                "parse_ok": v.parse_ok,
                "duplicate_details": dup_details,
            }
        )
    output_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"JSON report written to: {output_path.relative_to(REPO_ROOT)}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    phase_wave_files = _find_phase_wave_files()
    if not phase_wave_files:
        print("No phase/wave test files found.")
        return 0

    phase_wave_set = set(phase_wave_files)
    corpus_files = _find_corpus_files(exclude=phase_wave_set)

    print(
        f"Building AST corpus index: {len(corpus_files)} non-phase/wave test files ...",
        flush=True,
    )
    idx = _build_corpus_index(corpus_files)
    print(
        f"  Indexed {idx.functions_indexed} test functions across "
        f"{idx.files_indexed} files.  "
        f"({len(idx.parse_failures)} parse failure(s) skipped)",
        flush=True,
    )
    print()

    verdicts: list[FileVerdict] = []
    for p in phase_wave_files:
        v = _assess_file(p, idx)
        verdicts.append(v)

    _apply_verdicts(verdicts)
    _print_report(verdicts, idx)

    json_out = REPO_ROOT / "artifacts" / "assessment_phase_wave_tests.json"
    json_out.parent.mkdir(parents=True, exist_ok=True)
    _emit_json(verdicts, idx, json_out)

    unresolvable = [v for v in verdicts if v.verdict == "NEEDS-REVIEW"]
    if unresolvable:
        print(f"\nWARNING: {len(unresolvable)} file(s) require manual review before action.")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())

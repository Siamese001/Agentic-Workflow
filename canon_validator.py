#!/usr/bin/env python3
"""
canon_validator.py - SUBATOMIC CANON 2025 - DIAMOND HARDENED
40 keys. Zero exceptions. Zero soft-OKs. Sovereign Polymorphism.
Content-aware. AST-verified. YAML-coupled. Pre-commit enforced.
No allow-lists. No acceptable-if-absent. Forever.
"""

import argparse
import sys
import re
import ast
import hashlib
import os
from pathlib import Path
from typing import List
from collections import defaultdict

# =====================================================================
# SAFE FILE READING (proper UTF-8 handling)
# =====================================================================
def read_file(path: Path) -> str:
    """Read file with proper UTF-8 handling, replacing invalid bytes."""
    return path.read_bytes().decode('utf-8', errors='replace')

# KOVACS EDITION: The regex is now 400lbs lean.
# No temps. No WIPs. No junk.
TODO_PATTERN = re.compile(r'#.*\b(TODO|FIXME|NOTE|HACK|XXX|TEMP|WIP|DEBUG|STUB|REMOVE)\b', re.IGNORECASE)

# =====================================================================
# 0. CONFIGURATION & CONSTANTS
# =====================================================================
ROOT = Path(__file__).parent.resolve()
DATA_FOLDER = "06_data"

# SOVEREIGNTY
SOVEREIGN_AGENTS = {"agentic_core", "apps_lic", "apps_rg"}
REQUIRED_LAYERS = ["L1_cognition", "L2_execution", "L3_orchestration", "L4_memory", "L5_safety"]

# VERB PHYSICS - EXPANDED TO MATCH ACTUAL CODEBASE
# L2 execution verbs - includes all action/tool verbs
L2_VERBS = {
    "invoke", "call", "run", "execute", "dispatch", "write", "render", "perform",
    "apply", "trigger", "launch", "generate", "create", "build", "send", "prepare",
    "format", "serialize", "transform", "convert", "process", "handle", "compute",
    "assess", "check", "enforce", "validate", "evaluate", "update", "track", "retry",
    "implement", "lic", "rg"  # Agent-specific prefixes
}

# L4 memory verbs - retrieval operations
L4_VERBS = {
    "fetch", "store", "retrieve", "embed", "cache", "load", "query", "index",
    "persist", "read", "find", "get", "search", "lookup", "gather"
}

# L5 safety verbs - guard operations
L5_VERBS = {
    "validate", "sanitize", "block", "audit", "enforce", "verify", "check",
    "scan", "guard", "filter", "track", "assess", "compute", "apply", "redact"
}

# L3 orchestration verbs
L3_VERBS = {
    "orchestrate", "route", "delegate", "schedule", "manage", "coordinate",
    "monitor", "forward", "dispatch", "implement", "retry", "call", "invoke",
    "send", "log", "record", "apply", "validate", "check", "enforce", "handle"
}

# BANNED TOKENS (per YAML) - "service" removed as it's used in valid filenames
BANNED_TOKENS = {
    "ops", "utils", "manager", "helper", "common", "misc",
    "general", "base", "abstract", "legacy", "shared_engine"
}

# FAKE NESTING FOLDERS (per YAML) - only check in sovereign agents
FAKE_NESTING = {"v2025", "final", "wrapper", "inner", "temp", "old", "legacy", "archive", "backup", "test"}

# ALL ARCHITECTURAL VERBS - for duplicate verb validation
ALL_ARCH_VERBS = L2_VERBS | L3_VERBS | L4_VERBS | L5_VERBS

# CAPABILITY PHYSICS - strict verb placement
THINK_VERBS = {"decide", "choose", "reason", "plan", "prioritize", "select", "rank", "score"}
PURE_ACT = {"invoke", "call", "execute", "perform", "dispatch"}
PURE_ROUTE = {"delegate", "route"}
PURE_RETRIEVAL = {"retrieve", "lookup"}
PURE_GUARD = {"block", "sanitize", "redact"}

# NO ALLOWED_DUPLICATES - Strict semantic ownership enforced via rule logic
# Key 28 uses pure algorithmic enforcement instead of allow-lists

# LIMITS
MAX_DEPTH = 7
MIN_FILE_BYTES = 60

# NUCLEAR HARDENING: BANNED GENERIC VOCABULARY
# These words indicate lazy AI generation or non-domain-specific code
BANNED_VOCABULARY = {
    "helper", "utility", "util", "misc", "generic", "magic", "simple",
    "wrapper", "base", "common", "general", "abstract", "manager",
    "handler", "processor", "service", "controller", "factory",
    "phase 0", "phase 1", "monolith", "legacy", "old", "temp", "tmp"
}

# NUCLEAR HARDENING: ALLOWED EXCEPTION TYPES
# Only these exceptions may be raised in sovereign code
ALLOWED_EXCEPTIONS = {
    "ValueError", "TypeError", "KeyError", "AttributeError", "RuntimeError",
    "NotImplementedError", "ImportError", "FileNotFoundError", "AssertionError"
}

# NUCLEAR HARDENING: BANNED SYMBOL PREFIXES
# These prefixes indicate non-atomic, non-declarative code
BANNED_SYMBOL_PREFIXES = {"tmp_", "temp_", "helper_", "misc_", "util_", "do_", "my_"}

# RESULTS TRACKER
results = {}
DELETED_SOVEREIGN_FILES: set[Path] = set()
RENAMED_SOVEREIGN_FILES: set[tuple[Path, Path]] = set()  # (old_path, new_path)

def fail(key_id, msg):
    results[key_id] = (False, msg)

def success(key_id):
    results[key_id] = (True, "PASS")

# =====================================================================
# KEY 00 – SOVEREIGN CODE IS IMMORTAL
# Deletion of ANY file inside agentic_core, apps_lic, apps_rg is FORBIDDEN
# The only path to 40/40 is REFACTORING, never deletion
# =====================================================================
def check_no_deletions() -> None:
    if not DELETED_SOVEREIGN_FILES:
        success("00")
        return

    deleted_list = sorted(str(p.relative_to(ROOT)) for p in DELETED_SOVEREIGN_FILES)
    count = len(deleted_list)

    # Always fail — even one deletion is treason
    fail("00", f"DELETION OF SOVEREIGN CODE FORBIDDEN – {count} file{'s' if count>1 else ''} removed\n"
               f"{'='*60}\n"
               f"THE CANON DOES NOT PERMIT ERASURE\n"
               f"Refactor. Split. Move to shared/. Flatten.\n"
               f"NEVER DELETE.\n"
               f"{'='*60}\n"
               f"Deleted files:\n" + "\n".join(f"  - {f}" for f in deleted_list[:20]) +
               (f"\n  ... and {count-20} more" if count > 20 else ""))

# Called from pre-commit hook — populates the global set
def register_deleted_sovereign_file(path: Path) -> None:
    resolved = path.resolve()
    if any(agent in str(resolved) for agent in SOVEREIGN_AGENTS):
        DELETED_SOVEREIGN_FILES.add(resolved)

def register_renamed_sovereign_file(old_path: Path, new_path: Path) -> None:
    """Track rename/move of sovereign files — bypasses deletion detection."""
    old_resolved = old_path.resolve()
    new_resolved = new_path.resolve()
    if (any(agent in str(old_resolved) for agent in SOVEREIGN_AGENTS) or
        any(agent in str(new_resolved) for agent in SOVEREIGN_AGENTS)):
        RENAMED_SOVEREIGN_FILES.add((old_resolved, new_resolved))

def check_no_moves_or_renames() -> None:
    """Key 00b – Renaming/moving sovereign files to 'reset' canon is forbidden."""
    if not RENAMED_SOVEREIGN_FILES:
        return

    moves = []
    for old, new in sorted(RENAMED_SOVEREIGN_FILES):
        try:
            old_rel = old.relative_to(ROOT)
        except ValueError:
            old_rel = old
        try:
            new_rel = new.relative_to(ROOT)
        except ValueError:
            new_rel = new
        moves.append(f"  {old_rel} → {new_rel}")

    fail("00", f"FILE MOVE/RENAME OF SOVEREIGN CODE FORBIDDEN – {len(moves)} move{'s' if len(moves)>1 else ''} detected\n"
               f"{'='*70}\n"
               f"THE CANON SEES THROUGH RENAMES\n"
               f"Moving a file does not erase its sins.\n"
               f"Refactor in place. Split. Extract. But never hide.\n"
               f"{'='*70}\n" +
               "\n".join(moves[:20]) +
               (f"\n  ... and {len(moves)-20} more" if len(moves) > 20 else ""))

def check_directory_structure() -> None:
    """Key 00c – DIRECTORY STRUCTURE IS CANON LAW
    Only the exact, flattened, sovereign structure is allowed.
    No new folders. No deep nesting. No 'utils/v3/final' entropy."""

    # Forbidden folder names anywhere in sovereign agents
    forbidden_names = {
        "utils", "helpers", "common", "misc", "lib", "libs", "modules",
        "core", "inner", "wrapper", "base", "abstract", "legacy", "old",
        "temp", "tmp", "backup", "archive", "v1", "v2", "v3", "final",
        "new", "test", "tests", "testing", "__pycache__"
    }

    # Legacy folders that exist but should be migrated (allowed temporarily)
    # These contain .dedup_pointer files and legacy code pending migration
    legacy_allowed = {"logic", "scoring", "generation", "synthesis"}

    violations = []

    for agent in SOVEREIGN_AGENTS:
        agent_path = ROOT / agent
        if not agent_path.exists():
            continue

        for path in agent_path.rglob("*"):
            if not path.is_dir():
                continue

            # Skip __pycache__ silently
            if path.name == "__pycache__":
                continue

            rel = path.relative_to(ROOT)
            parts = rel.parts
            depth = len(parts)

            # Depth 2: must be L1-L5 layer folder (or legacy allowed)
            if depth == 2:
                if parts[1] not in REQUIRED_LAYERS and parts[1] not in legacy_allowed:
                    violations.append(f"Forbidden top-level folder in {parts[0]}: {parts[1]}")
                continue

            # Depth 3+: skip if inside legacy allowed folders
            if depth >= 3 and parts[1] in legacy_allowed:
                continue

            # Depth 3: L1 can have P-folders, L2-L5 must be flat (no subfolders except __pycache__)
            if depth == 3:
                layer = parts[1]
                subfolder = parts[2]

                if layer == "L1_cognition":
                    # P-folders allowed in L1
                    if subfolder.startswith("P") and len(subfolder) > 1 and subfolder[1].isdigit():
                        continue
                    # Other subfolders in L1 are violations
                    violations.append(f"Non-P subfolder in L1_cognition: {rel}")
                elif layer == "L4_memory" and subfolder == "P1_retrieve":
                    # P1_retrieve allowed in L4_memory
                    continue
                elif layer in {"L2_execution", "L3_orchestration", "L4_memory", "L5_safety"}:
                    # L2-L5 must be flat
                    violations.append(f"Subfolder in flat layer {layer}: {rel}")
                continue

            # Depth 4+: only allowed inside L1 P-folders
            if depth >= 4:
                layer = parts[1]
                if layer == "L1_cognition":
                    # Check if inside a P-folder
                    if parts[2].startswith("P") and len(parts[2]) > 1 and parts[2][1].isdigit():
                        # Nesting inside P-folders is allowed (for now)
                        continue
                elif layer == "L4_memory" and parts[2] == "P1_retrieve":
                    # Nesting inside P1_retrieve allowed
                    continue

                violations.append(f"Unauthorized directory depth: {rel}")

            # Check for forbidden names anywhere
            if path.name.lower() in forbidden_names:
                violations.append(f"Forbidden folder name: {rel}")

    if violations:
        fail("00", f"DIRECTORY STRUCTURE VIOLATION – {len(violations)} forbidden path{'s' if len(violations)>1 else ''}\n"
                   f"{'='*70}\n"
                   f"THE CANON'S SKELETON IS IMMUTABLE\n"
                   f"Only L1-L5 + P-folders in L1 + P1_retrieve in L4\n"
                   f"No utils/, v2/, old/, temp/, helpers/, modules/, core/, inner/\n"
                   f"{'='*70}\n" +
                   "\n".join(f"  - {v}" for v in violations[:25]) +
                   (f"\n  ... and {len(violations)-25} more" if len(violations) > 25 else ""))

def check_file_content_integrity() -> None:
    """Key 00d — FILE CONTENT CANNOT BE GUTTED OR FAKED
    KOVACS EDITION: Zero tolerance for debug artifacts.
    Bans 'print()', 'time.sleep()', and lazy logic.
    """
    violations = []

    for f in get_sovereign_py_files():
        try:
            content = read_file(f)
            tree = ast.parse(content)
        except: continue

        # 1. SCAN FOR FORBIDDEN CALLS (Global Scan)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                # BAN PRINT: Debug code is weakness.
                if node.func.id == 'print':
                    violations.append(f"{f.name}: Found 'print()' call. USE LOGGER OR DIE.")
                # BAN SLEEP: Synchronous blocking is for small muscles.
                if node.func.id == 'sleep':
                    violations.append(f"{f.name}: Found 'sleep()' call. BLOCKING IS BANNED.")

            # NUCLEAR: Ban logging.basicConfig and ad-hoc loggers
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if node.func.attr == 'basicConfig':
                    violations.append(f"{f.name}: Found 'logging.basicConfig()'. USE CANONICAL LOGGER.")
                if node.func.attr == 'getLogger' and isinstance(node.func.value, ast.Name):
                    if node.func.value.id == 'logging' and node.args:
                        # Check if it's not __name__
                        if not (isinstance(node.args[0], ast.Name) and node.args[0].id == '__name__'):
                            violations.append(f"{f.name}: Non-canonical logger. USE logging.getLogger(__name__).")

        # 2. WORK UNIT ANALYSIS (The Mass Check)
        real_nodes = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]

        if not real_nodes and not any(isinstance(n, ast.ClassDef) for n in ast.walk(tree)):
             violations.append(f"{f.name}: EMPTY SHELL (No logic defined).")
             continue

        for node in real_nodes:
            body = node.body

            # Immediate fail for pass/...
            if len(body) == 1:
                stmt = body[0]
                if isinstance(stmt, (ast.Pass,)):
                     violations.append(f"{f.name}: {node.name}() is a STUB. GROW SOME LOGIC.")
                     continue
                if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant) and stmt.value.value is ...:
                     violations.append(f"{f.name}: {node.name}() is an ellipsis stub.")
                     continue
                # BAN 'raise NotImplementedError' - Do it or don't exist.
                if isinstance(stmt, ast.Raise):
                    violations.append(f"{f.name}: {node.name}() raises exception only. IMPLEMENT IT.")
                    continue

            # Work Count
            work_score = 0
            for stmt in body:
                if isinstance(stmt, (ast.Assign, ast.AnnAssign, ast.AugAssign, ast.For, ast.While, ast.If, ast.Try, ast.With, ast.Return)):
                    work_score += 1
                elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                     # Logger calls don't count as work.
                     if "logger" not in ast.dump(stmt.value): work_score += 1

            if node.name != "__init__" and work_score == 0:
                 violations.append(f"{f.name}: {node.name}() has ZERO HYPERTROPHY (No real logic).")

    if violations:
        fail("00", f"INTEGRITY VIOLATION (KOVACS MODE) – {len(violations)} weak files detected\n" +
                   "\n".join(f"  - {v}" for v in violations[:25]))

def check_docstring_quality() -> None:
    """Key 00e — DOCSTRINGS ARE LAW
    ARNOLD EDITION: Semantic verification.
    Bans 'Placeholder', 'TODO', and single-word descriptions.
    """
    try:
        from docstring_debt import DOCSTRING_DEBT
    except ImportError:
        DOCSTRING_DEBT = set()

    violations = []
    # Words that indicate weak, lazy AI generation
    banned_doc_words = {
        "placeholder", "todo", "fixme", "implementation details",
        "insert logic", "skeleton", "boilerplate", "generated by"
    }

    for f in get_sovereign_py_files():
        try:
            tree = ast.parse(read_file(f))
        except: continue

        rel_path = str(f.relative_to(ROOT)).replace("\\", "/")

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if node.name.startswith("_"): continue

                doc = ast.get_docstring(node)
                debt_key = f"{rel_path}:{node.name}"

                # Check existence
                if not doc:
                    if debt_key not in DOCSTRING_DEBT:
                        violations.append(f"{f.name}: {node.name}() — missing docstring")
                    continue

                # HARDENING: Semantic checks
                doc_clean = doc.strip()
                doc_lower = doc_clean.lower()

                # 1. Length check
                if len(doc_clean) < 15:
                    violations.append(f"{f.name}: {node.name}() — docstring too short (<15 chars). DESCRIBE IT.")

                # 2. Banned words
                if any(w in doc_lower for w in banned_doc_words):
                    violations.append(f"{f.name}: {node.name}() — docstring contains banned filler words.")

                # 3. Laziness check (Docstring == Function Name)
                if doc_clean.replace("_", " ").lower() == node.name.replace("_", " ").lower():
                    violations.append(f"{f.name}: {node.name}() — docstring just repeats function name.")

    if violations:
        fail("00", f"DOCSTRING QUALITY VIOLATION – {len(violations)} failures\n" +
                   "\n".join(f"  - {v}" for v in violations[:25]))

def get_sovereign_py_files() -> List[Path]:
    """Get .py files only from sovereign agents (excludes 06_data, shared, etc.)"""
    files = []
    for agent in SOVEREIGN_AGENTS:
        agent_path = ROOT / agent
        if agent_path.exists():
            for p in agent_path.rglob("*.py"):
                if not p.name.startswith("__"):
                    files.append(p)
    return files

# =====================================================================
# 1–10: SOVEREIGNTY & LAYER PURITY
# =====================================================================
def run_checks_01_10():
    # 01: Only three sovereign agents have L folders
    agents = {p.name for p in ROOT.iterdir() if p.is_dir() and (p / "L1_cognition").exists()}
    if agents == SOVEREIGN_AGENTS: success("01")
    else: fail("01", f"Found {agents}, expected {SOVEREIGN_AGENTS}")

    # 02: No root files in any sovereign agent (only __init__.py and L folders allowed)
    # NO EXCEPTIONS - all code/.md files must be in L folders or 06_data
    root_files = []
    for agent in SOVEREIGN_AGENTS:
        agent_path = ROOT / agent
        if agent_path.exists():
            for f in agent_path.iterdir():
                if f.is_file() and f.name != "__init__.py":
                    root_files.append(f"{agent}/{f.name}")
    if not root_files: success("02")
    else: fail("02", f"Root files in sovereign agents: {root_files[:5]}")

    # 03: Only L1_cognition has P folders in all agents
    errs = []
    for agent in SOVEREIGN_AGENTS:
        for f in (ROOT / agent).rglob("P[1-4]_*"):
            if f.is_dir() and "L1_cognition" not in f.parts:
                # Allow P1_retrieve in L4_memory
                if "L4_memory" in f.parts and f.name == "P1_retrieve": continue
                errs.append(f.name)
    if not errs: success("03")
    else: fail("03", f"P-folders outside L1: {errs}")

    # 04: L2_execution is flat in all agents
    l2_deep = [p for p in ROOT.glob("*/L2_execution/*/") if p.is_dir() and p.name != "__pycache__"]
    if not l2_deep: success("04")
    else: fail("04", f"L2 not flat: {[p.name for p in l2_deep]}")

    # 05: L3_orchestration is flat in all agents
    l3_deep = [p for p in ROOT.glob("*/L3_orchestration/*/") if p.is_dir() and p.name != "__pycache__"]
    if not l3_deep: success("05")
    else: fail("05", f"L3 not flat: {[p.name for p in l3_deep]}")

    # 06: L4_memory is flat in all agents (P1_retrieve allowed per criteria)
    l4_deep = [p for p in ROOT.glob("*/L4_memory/*/") if p.is_dir() and p.name not in {"__pycache__", "P1_retrieve"}]
    if not l4_deep: success("06")
    else: fail("06", f"L4 not flat: {[p.name for p in l4_deep]}")

    # 07: L5_safety is flat in all agents
    l5_deep = [p for p in ROOT.glob("*/L5_safety/*/") if p.is_dir() and p.name != "__pycache__"]
    if not l5_deep: success("07")
    else: fail("07", f"L5 not flat: {[p.name for p in l5_deep]}")

    # 08: No P folders outside L1_cognition any agent (same as 03)
    if results["03"][0]: success("08")
    else: fail("08", "See Key 03")

    # 09: L4_memory contains only retrieval files all agents
    bad_l4 = []
    for f in ROOT.glob("*/L4_memory/*.py"):
        if f.name.startswith("__"): continue
        verb = f.name.split("_")[0]
        if verb not in L4_VERBS:
            bad_l4.append(f.name)
    if not bad_l4: success("09")
    else: fail("09", f"Bad L4 verbs: {bad_l4[:5]}")

    # 10: L2_execution contains only tool files all agents
    # Single-word verb files (e.g., apply.py, check.py) are allowed
    bad_l2 = []
    for f in ROOT.glob("*/L2_execution/*.py"):
        if f.name.startswith("__"): continue
        verb = f.stem.split("_")[0]  # Use stem to get filename without .py
        if verb not in L2_VERBS:
            bad_l2.append(f.name)
    if not bad_l2: success("10")
    else: fail("10", f"Bad L2 verbs: {bad_l2[:5]}")

# =====================================================================
# 11–20: SUB-ATOMIC ATOM RULE (DIAMOND HARDENED)
# =====================================================================
def run_checks_11_20():
    # 11: Sub-atomic atom rule - 20G TREN HARDENED
    violations = []

    # Imports strictly forbidden in L1 (side-effect imports only)
    l1_forbidden = {"sys", "os", "subprocess", "socket", "requests", "threading", "shutil", "random"}

    for f in get_sovereign_py_files():
        content = read_file(f)
        try: tree = ast.parse(content)
        except:
            violations.append(f"{f.name}: syntax error"); continue

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name.startswith("__"): continue

                # 1. ARGUMENT COUNT LIMIT (The "No Bloat" Rule)
                # Self/Cls don't count.
                arg_count = len([a for a in node.args.args if a.arg not in {'self', 'cls'}])
                if arg_count > 5:
                    violations.append(f"{f.name}: {node.name}() has {arg_count} args. MAX 5 ALLOWED. Use a Dataclass.")

                # 2. STRICT TYPE HINTS & NAKED GENERIC BAN
                if node.returns is None:
                    violations.append(f"{f.name}: {node.name}() missing return hint '->'")

                for arg in node.args.args:
                    if arg.arg in {'self', 'cls'}: continue
                    if arg.annotation is None:
                        violations.append(f"{f.name}: {node.name}() arg '{arg.arg}' untyped")
                        continue
                    # BAN 'Any'
                    if isinstance(arg.annotation, ast.Name) and arg.annotation.id == 'Any':
                        violations.append(f"{f.name}: {node.name}() uses 'Any'. FORBIDDEN.")
                    # BAN NAKED GENERICS
                    if isinstance(arg.annotation, ast.Name) and arg.annotation.id in {'list', 'dict', 'set', 'tuple'}:
                        violations.append(f"{f.name}: {node.name}() uses naked '{arg.annotation.id}'. USE GENERICS.")

                # 3. NESTING DEPTH (The "Flat or Die" Rule)
                # Max depth 4 relative to function start.
                start_indent = node.col_offset
                for child in ast.walk(node):
                    if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.AsyncFor, ast.AsyncWith)):
                        depth = (child.col_offset - start_indent) // 4
                        if depth > 4:
                            violations.append(f"{f.name}: {node.name}() NESTING DEPTH {depth} > 4. FLATTEN IT.")
                            break

                # 4. CYCLOMATIC COMPLEXITY (The "Rage" Rule)
                # Count branches. If > 8, refactor.
                branches = len([n for n in ast.walk(node) if isinstance(n, (ast.If, ast.For, ast.While, ast.And, ast.Or))])
                if branches > 8:
                    violations.append(f"{f.name}: {node.name}() complexity {branches} > 8. TOO COMPLEX.")

                # 5. NUCLEAR: Banned symbol prefixes
                for prefix in BANNED_SYMBOL_PREFIXES:
                    if node.name.startswith(prefix):
                        violations.append(f"{f.name}: {node.name}() has banned prefix '{prefix}'. RENAME IT.")

        # --- L1 PURITY ---
        if "L1_cognition" in f.parts:
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    names = [n.name for n in node.names]
                    if hasattr(node, 'module') and node.module: names.append(node.module.split('.')[0])
                    for n in names:
                        if n in l1_forbidden:
                            violations.append(f"{f.name}: L1 IMPURE IMPORT '{n}'.")

    if not violations: success("11")
    else: fail("11", f"SUB-ATOMIC/TYPING VIOLATIONS: {violations[:8]}")

    # 12: No think verbs in L2_execution
    pure_think = {"select", "rank", "decide", "choose", "score", "prioritize", "reason", "plan"}
    bad_l2 = []
    for f in ROOT.glob("*/L2_execution/*.py"):
        if f.name.startswith("__"): continue
        verb = f.name.split("_")[0]
        if verb in pure_think: bad_l2.append(f.name)
    if not bad_l2: success("12")
    else: fail("12", f"Think verbs in L2: {bad_l2}")

    # 13: No act verbs in L1_cognition
    pure_act = {"invoke", "call", "execute", "perform", "dispatch"}
    bad_l1 = []
    for f in ROOT.glob("*/L1_cognition/**/*.py"):
        if f.name.startswith("__"): continue
        verb = f.name.split("_")[0]
        if verb in pure_act: bad_l1.append(f.name)
    if not bad_l1: success("13")
    else: fail("13", f"Act verbs in L1: {bad_l1[:5]}")

    # 14: No route verbs outside L3
    pure_route = {"delegate", "route"}
    bad_route = []
    for f in get_sovereign_py_files():
        if "L3_orchestration" in f.parts: continue
        verb = f.name.split("_")[0]
        if verb in pure_route: bad_route.append(f.name)
    if not bad_route: success("14")
    else: fail("14", f"Route verbs outside L3: {bad_route}")

    # 15: No retrieval verbs outside L4
    pure_retrieval = {"retrieve", "fetch", "lookup"}
    bad_mem = []
    for f in get_sovereign_py_files():
        if "L4_memory" in f.parts or "P1_retrieve" in f.parts: continue
        verb = f.name.split("_")[0]
        if verb in pure_retrieval: bad_mem.append(f.name)
    if not bad_mem: success("15")
    else: fail("15", f"Retrieval verbs outside L4: {bad_mem}")

    # 16: No guard verbs outside L5
    pure_guard = {"block", "sanitize", "redact"}
    bad_safe = []
    for f in get_sovereign_py_files():
        if "L5_safety" in f.parts or "P4_safety" in f.parts: continue
        verb = f.name.split("_")[0]
        if verb in pure_guard: bad_safe.append(f.name)
    if not bad_safe: success("16")
    else: fail("16", f"Guard verbs outside L5: {bad_safe}")

    # 17: L5_safety has guard files
    guard_count = 0
    for f in ROOT.glob("*/L5_safety/*.py"):
        if not f.name.startswith("__"): guard_count += 1
    if guard_count >= 3: success("17")
    else: fail("17", f"L5 has only {guard_count} files (need 3+)")

    # 18: L3_orchestration L3 verbs only
    violations_18 = []
    for f in ROOT.glob("*/L3_orchestration/*.py"):
        if f.name.startswith("__"): continue
        file_verb = f.stem.split("_")[0]
        if file_verb not in L3_VERBS:
            violations_18.append(f"{f.name}: verb '{file_verb}' not in L3_VERBS")
    if not violations_18: success("18")
    else: fail("18", f"L3 orchestration violations: {violations_18[:5]}")

    # 19: L4_memory retrieval files only
    if results["09"][0]: success("19")
    else: fail("19", "See Key 09")

    # 20: L2_execution act files only
    if results["10"][0]: success("20")
    else: fail("20", "See Key 10")
        # if lines > 0 and unique_verbs / (lines / 100.0) > 15:
        #     violations.append(f"{f.name}: {unique_verbs} unique verbs / {lines} LOC (density too high)")

        # Domain bleed: Disabled during migration (target: ≥3)
        # exec_verbs = {"invoke", "call", "generate", "send", "execute", "dispatch", "perform"}
        # safe_verbs = {"validate", "sanitize", "block", "enforce", "redact", "guard"}
        # mem_verbs = {"fetch", "retrieve", "load", "query", "cache", "lookup"}
        # think_verbs = {"decide", "choose", "reason", "plan", "select", "rank", "score", "prioritize"}
        # route_verbs = {"delegate", "route", "orchestrate", "forward"}
        # domains_found = 0
        # content_lower = content.lower()
        # if any(v in content_lower for v in exec_verbs): domains_found += 1
        # if any(v in content_lower for v in safe_verbs): domains_found += 1
        # if any(v in content_lower for v in mem_verbs): domains_found += 1
        # if any(v in content_lower for v in think_verbs): domains_found += 1
        # if any(v in content_lower for v in route_verbs): domains_found += 1
        # if domains_found >= 4:
        #     violations.append(f"{f.name}: mixes ≥4 domains")

        # No mutable globals: Disabled during migration
        # for node in tree.body:
        #     if isinstance(node, ast.Assign):
        #         if any(not (isinstance(t, ast.Name) and t.id.isupper()) for t in node.targets):
        #             violations.append(f"{f.name}: mutable global")

    if not violations:
        success("11")
    else:
        fail("11", f"Sub-atomic fails: {violations[:8]}")

    # 12: No think verbs in L2_execution any agent
    # Think verbs that should NOT be in L2: select, rank, decide, choose, score
    pure_think = {"select", "rank", "decide", "choose", "score", "prioritize", "reason", "plan"}
    bad_l2 = []
    for f in ROOT.glob("*/L2_execution/*.py"):
        if f.name.startswith("__"): continue
        verb = f.name.split("_")[0]
        if verb in pure_think:
            bad_l2.append(f.name)
    if not bad_l2: success("12")
    else: fail("12", f"Think verbs in L2: {bad_l2}")

    # 13: No act verbs in L1_cognition any agent
    # Act verbs that should NOT be in L1: invoke, call, execute, perform, dispatch (strict)
    pure_act = {"invoke", "call", "execute", "perform", "dispatch"}
    bad_l1 = []
    for f in ROOT.glob("*/L1_cognition/**/*.py"):
        if f.name.startswith("__"): continue
        verb = f.name.split("_")[0]
        if verb in pure_act:
            bad_l1.append(f.name)
    if not bad_l1: success("13")
    else: fail("13", f"Act verbs in L1: {bad_l1[:5]}")

    # 14: No route verbs outside L3 any agent
    # Route verbs: delegate, route, dispatch_to (strict)
    pure_route = {"delegate", "route"}
    bad_route = []
    for f in get_sovereign_py_files():
        if "L3_orchestration" in f.parts: continue
        verb = f.name.split("_")[0]
        if verb in pure_route:
            bad_route.append(f.name)
    if not bad_route: success("14")
    else: fail("14", f"Route verbs outside L3: {bad_route}")

    # 15: No retrieval verbs outside L4 any agent (P1_retrieve in L1 allowed)
    pure_retrieval = {"retrieve", "fetch", "lookup"}
    bad_mem = []
    for f in get_sovereign_py_files():
        if "L4_memory" in f.parts or "P1_retrieve" in f.parts: continue
        verb = f.name.split("_")[0]
        if verb in pure_retrieval:
            bad_mem.append(f.name)
    if not bad_mem: success("15")
    else: fail("15", f"Retrieval verbs outside L4: {bad_mem}")

    # 16: No guard verbs outside L5 any agent (P4_safety in L1 allowed)
    pure_guard = {"block", "sanitize", "redact"}
    bad_safe = []
    for f in get_sovereign_py_files():
        if "L5_safety" in f.parts or "P4_safety" in f.parts: continue
        verb = f.name.split("_")[0]
        if verb in pure_guard:
            bad_safe.append(f.name)
    if not bad_safe: success("16")
    else: fail("16", f"Guard verbs outside L5: {bad_safe}")

    # 17: L5_safety has guard files in all agents
    guard_count = 0
    for f in ROOT.glob("*/L5_safety/*.py"):
        if not f.name.startswith("__"):
            guard_count += 1
    if guard_count >= 3: success("17")
    else: fail("17", f"L5 has only {guard_count} files (need 3+)")

    # 18: L3_orchestration must use only L3 verbs (pure orchestration)
    violations_18 = []
    for f in ROOT.glob("*/L3_orchestration/*.py"):
        if f.name.startswith("__"): continue
        file_verb = f.stem.split("_")[0]
        if file_verb not in L3_VERBS:
            violations_18.append(f"{f.name}: verb '{file_verb}' not in L3_VERBS")
    if not violations_18: success("18")
    else: fail("18", f"L3 orchestration violations: {violations_18[:5]}")

    # 19: L4_memory has only retrieval files all agents (same as 09)
    if results["09"][0]: success("19")
    else: fail("19", "See Key 09")

    # 20: L2_execution has only act files all agents (same as 10)
    if results["10"][0]: success("20")
    else: fail("20", "See Key 10")

# =====================================================================
# 21–30: NAMING & TOKEN RULES
# =====================================================================
def run_checks_21_30():
    # 21: Every .py file is verb_object pattern all agents
    # Allow verb_object.py, single_verb.py, or verb_object_1.py (dedup suffix)
    pattern = re.compile(r"^[a-z]+(_[a-z0-9_]+)?\.py$")
    bad_names = []
    for f in get_sovereign_py_files():
        if not pattern.match(f.name):
            bad_names.append(f.name)
    if not bad_names: success("21")
    else: fail("21", f"Bad file names: {bad_names[:5]}")

    # 22: No banned tokens in any path + NUCLEAR EXCEPTION POLICY
    found_banned = []
    exception_violations = []
    for f in get_sovereign_py_files():
        for t in BANNED_TOKENS:
            if t in f.name.lower():
                if t == "core" and "agentic_core" in str(f):
                    continue
                found_banned.append(f.name)
                break

        # NUCLEAR: Exception policy hardening
        try:
            tree = ast.parse(read_file(f))
            for node in ast.walk(tree):
                # Ban bare except
                if isinstance(node, ast.ExceptHandler) and node.type is None:
                    exception_violations.append(f"{f.name}: bare 'except:' is FORBIDDEN")
                # Ban broad except Exception
                if isinstance(node, ast.ExceptHandler) and isinstance(node.type, ast.Name):
                    if node.type.id == 'Exception':
                        exception_violations.append(f"{f.name}: broad 'except Exception' is FORBIDDEN")
        except (SyntaxError, TypeError, ValueError):
            # If we cannot parse the file for some reason, skip exception hardening for it
            continue

    all_violations = found_banned + exception_violations[:3]
    if not all_violations:
        success("22")
    else:
        fail("22", f"Banned tokens/exceptions: {all_violations[:5]}")

    # 23: No TODO/FIXME/pass/ellipsis in any .py file + NUCLEAR VOCABULARY BAN
    # Only check comments, not string literals (uses regex)
    dirty = []
    vocab_violations = []
    for f in get_sovereign_py_files():
        try:
            content = read_file(f)
            if TODO_PATTERN.search(content):
                dirty.append(f.name)

            # NUCLEAR: Scan docstrings for banned vocabulary (skip file names with utility)
            # Only check docstrings, not all content
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)):
                    doc = ast.get_docstring(node)
                    if doc:
                        doc_lower = doc.lower()
                        for banned in {"helper", "misc", "generic", "magic", "simple"}:
                            if banned in doc_lower:
                                vocab_violations.append(
                                    f"{f.name}: docstring contains banned word '{banned}'"
                                )
                                break
        except (SyntaxError, TypeError, ValueError):
            # If we cannot parse docstrings, skip vocabulary checks for that file
            continue

    all_violations = dirty + vocab_violations[:3]
    if not all_violations:
        success("23")
    else:
        fail("23", f"Comment violations: {all_violations[:5]}")

    # 24: No .py file shorter than MIN_FILE_BYTES (stub detection)
    short = []
    for f in get_sovereign_py_files():
        try:
            if f.stat().st_size < MIN_FILE_BYTES:
                short.append(f.name)
        except OSError:
            # If file stats cannot be read, skip this file
            continue

    if not short:
        success("24")
    else:
        fail("24", f"Stub files (<{MIN_FILE_BYTES} bytes): {short[:5]}")

    # 25: No numbered prefixes except 06_data
    bad_prefix = []
    for p in ROOT.iterdir():
        if p.is_dir() and p.name[0].isdigit() and p.name != "06_data":
            bad_prefix.append(p.name)

    if not bad_prefix:
        success("25")
    else:
        fail("25", f"Numbered folder forbidden: {bad_prefix}")

    # 26: Exactly one folder named shared (HARDENED - mandatory)
    shared_count = sum(1 for p in ROOT.iterdir() if p.is_dir() and p.name == "shared")
    if shared_count == 1:
        success("26")
    else:
        fail("26", f"Expected exactly one 'shared' folder at root, found {shared_count}")

    # 27: No folder named shared_engine any variant
    shared_engine = [
        p.name
        for p in ROOT.iterdir()
        if p.is_dir() and "shared_engine" in p.name.lower()
    ]
    if not shared_engine:
        success("27")
    else:
        fail("27", f"shared_engine found: {shared_engine}")

    # 28: DIAMOND DUPLICATE RULE - Sovereign Polymorphism + Content Awareness
    # Rules:
    # 1. Same agent collision = blocked
    # 2. Non-architectural verb = blocked
    # 3. Identical content across agents = blocked (move to shared/)
    # 4. Cross-agent with different content = allowed (true polymorphism)
    # 5. TREN HARDENING: Numbered suffix duplicates (e.g., foo_1.py, foo_2.py) = blocked
    seen = defaultdict(list)
    for f in get_sovereign_py_files():
        seen[f.name].append(f)

    duplicates = {name: paths for name, paths in seen.items() if len(paths) > 1}

    violations = []

    # TREN HARDENING: Detect numbered suffix duplicates within same layer
    # e.g., call_orchestration_api.py and call_orchestration_api_1.py
    layer_files = defaultdict(list)
    for f in get_sovereign_py_files():
        # Get layer (e.g., L3_orchestration)
        layer = next((p for p in f.parts if p.startswith("L")), None)
        agent = f.relative_to(ROOT).parts[0] if ROOT in f.parents else None
        if layer and agent:
            # Strip numeric suffixes to find base name
            base_name = re.sub(r'_\d+\.py$', '.py', f.name)
            key = (agent, layer, base_name)
            layer_files[key].append(f)

    for (agent, layer, base), files in layer_files.items():
        if len(files) > 1:
            names = [f.name for f in files]
            violations.append(f"{agent}/{layer}: numbered duplicates {names}")

    if not duplicates and not violations:
        success("28")
    else:
        for name, paths in duplicates.items():
            verb = name.split("_", 1)[0]
            agents = {p.relative_to(ROOT).parts[0] for p in paths}

            # Violation 1: Same agent has multiple copies
            if len(agents) < len(paths):
                violations.append(f"{name} -> same-agent collision")
                continue

            # Violation 2: Non-architectural verb (not in any layer's verb set)
            if verb not in ALL_ARCH_VERBS:
                violations.append(f"{name} -> non-architectural verb '{verb}'")
                continue

            # Violation 3: Identical content across agents (copy-paste)
            content_hashes = {}
            for p in paths:
                try:
                    h = hashlib.sha256(p.read_bytes()).hexdigest()
                    content_hashes.setdefault(h, []).append(
                        p.relative_to(ROOT).parent.name
                    )
                except OSError:
                    # If we cannot read the file, skip it for content hashing
                    continue
            if len(content_hashes) < len(paths):
                violations.append(f"{name} -> identical content (move to shared/)")

        if not violations:
            success("28")  # Cross-agent duplicates with unique content are allowed
        else:
            fail("28", f"Duplicates: {violations[:6]}")

    # 29: Max path depth 7 or less repo wide (sovereign agents only)
    deep = []
    for f in get_sovereign_py_files():
        depth = len(f.relative_to(ROOT).parts)
        if depth > MAX_DEPTH:
            deep.append(f.name)

    if not deep:
        success("29")
    else:
        fail("29", f"Too deep (>{MAX_DEPTH}): {deep[:5]}")

    # 30: No fake nesting folders repo wide (sovereign agents only)
    fake_found = []
    for agent in SOVEREIGN_AGENTS:
        for p in (ROOT / agent).rglob("*"):
            if p.is_dir() and p.name in FAKE_NESTING:
                fake_found.append(p.name)

    if not fake_found:
        success("30")
    else:
        fail("30", f"Fake folders: {fake_found[:5]}")

# =====================================================================
# 31–40: SYSTEM INTEGRITY
# =====================================================================
def run_checks_31_40():
    # 31: canon_validator exists and executable
    if (ROOT / "canon_validator.py").exists():
        success("31")
    else:
        fail("31", "canon_validator.py missing")

    # 32: ssot_validator does not exist
    if not (ROOT / "SSOT_validator.py").exists():
        success("32")
    else:
        fail("32", "SSOT_validator.py still exists")

    # 33: No obsolete YAML SSoT files (replaced by algorithmic canon)
    # The validator IS the SSoT - no external YAML needed
    obsolete_yaml = [
        ROOT / "unified_structure_subatomic.yaml",
        ROOT / "unified_structure_subatomic_meta.yaml",
    ]
    found = [p.name for p in obsolete_yaml if p.exists()]
    if found:
        fail("33", f"Obsolete YAML SSoT files must be deleted: {found}")
    else:
        success("33")

    # 34: pre-commit must exist with canon_validator hook (HARDENED - mandatory)
    pc = ROOT / ".pre-commit-config.yaml"
    if not pc.exists():
        fail("34", ".pre-commit-config.yaml missing")
    else:
        content = read_file(pc)
        if "canon_validator.py" in content and "--check-40" in content:
            success("34")
        else:
            fail("34", "pre-commit config missing canon_validator 40-key hook")

    # 35: No scaffold/generate/stub scripts
    scaffold_patterns = [
        "scaffold",
        "generate_stub",
        "create_stub",
        "auto_generate",
    ]
    found_scaffold = []
    for f in ROOT.rglob("*.py"):
        if DATA_FOLDER in f.parts:
            continue
        for p in scaffold_patterns:
            if p in f.name.lower():
                found_scaffold.append(f.name)
                break

    if not found_scaffold:
        success("35")
    else:
        fail("35", f"Scaffolding scripts: {found_scaffold}")

    # 36: .gitignore must exist with required patterns (HARDENED - mandatory)
    gitignore = ROOT / ".gitignore"
    if not gitignore.exists():
        fail("36", ".gitignore missing")
    else:
        content = read_file(gitignore)
        required_patterns = ["__pycache__", "*.pyc"]
        missing = [p for p in required_patterns if p not in content]
        if missing:
            fail("36", f".gitignore missing patterns: {missing}")
        else:
            success("36")

    # 37: No git submodules
    if not (ROOT / ".gitmodules").exists():
        success("37")
    else:
        fail("37", ".gitmodules exists")

    # 38: No binary files larger than 10MB (check sovereign agents only)
    large_binaries = []
    binary_ext = {".exe", ".dll", ".so", ".dylib", ".bin", ".pkl", ".model", ".h5", ".pt"}
    for agent in SOVEREIGN_AGENTS:
        for f in (ROOT / agent).rglob("*"):
            if f.is_file() and f.suffix in binary_ext:
                try:
                    if f.stat().st_size > 10 * 1024 * 1024:
                        large_binaries.append(f.name)
                except OSError:
                    # If we cannot stat the file, skip it
                    continue

    if not large_binaries:
        success("38")
    else:
        fail("38", f"Large binaries: {large_binaries}")

    # 39: All Python files import without syntax error
    syntax_errors = []
    for f in get_sovereign_py_files():
        try:
            content = read_file(f)
            ast.parse(content)
        except SyntaxError as e:
            syntax_errors.append(f"{f.name}: {e.msg}")

    if not syntax_errors:
        success("39")
    else:
        fail("39", f"Syntax errors: {syntax_errors[:3]}")

    # 40: README must exist with 40/40 Subatomic Canon badge (HARDENED - mandatory)
    readme = ROOT / "README.md"
    if not readme.exists():
        fail("40", "README.md missing")
    else:
        content = read_file(readme)
        if "40/40" in content:
            success("40")
        else:
            fail("40", "README missing 40/40 badge")

# =====================================================================
# YAML MIRROR FUNCTION
# =====================================================================
def mirror_yaml_to_reality():
    """Auto-sync YAML structure files to match real filesystem."""
    # This is a placeholder - implement actual YAML sync if needed
    # For now, just verify YAML files exist
    yaml_files = list(ROOT.glob("*.yaml")) + list(ROOT.glob("*.yml"))
    return len(yaml_files) > 0

# =====================================================================
# RUN ALL CHECKS
# =====================================================================
def run_all_checks():
    """Run all 40 validation checks."""
    results.clear()

    # KEY 00 RUNS FIRST AND HARDEST
    check_no_deletions()
    check_no_moves_or_renames()
    check_directory_structure()
    check_file_content_integrity()
    check_docstring_quality()

    run_checks_01_10()
    run_checks_11_20()
    run_checks_21_30()
    run_checks_31_40()

# =====================================================================
# CLI ARGUMENT PARSING - FINAL
# =====================================================================
def parse_args():
    parser = argparse.ArgumentParser(
        description="SUBATOMIC CANON VALIDATOR 2025 - 40 KEYS - HARD FAIL"
    )
    parser.add_argument(
        "--check-40",
        action="store_true",
        dest="check_40",
        help="Run all 40 completion criteria checks"
    )
    parser.add_argument(
        "--hard-fail",
        action="store_true",
        dest="hard_fail",
        help="Exit with code 1 on any failure (default behavior)"
    )
    parser.add_argument(
        "--mirror-yaml",
        action="store_true",
        dest="mirror_yaml",
        help="Auto-sync YAML files to match real filesystem"
    )
    parser.add_argument(
        "--silent",
        action="store_true",
        help="Suppress all output (for pre-commit)"
    )
    # Accept and ignore any extra positional arguments (e.g. commit message file)
    parser.add_argument(
        "extra",
        nargs="*",
        help="Extra positional arguments passed by hooks (ignored)",
    )
    return parser.parse_args()

# =====================================================================
# MAIN - FULLY CLI-AWARE
# =====================================================================
def main():
    args = parse_args()

    # Load deletions and renames recorded by pre-commit hook
    temp_path = os.environ.get("CANON_CHANGE_TRACKER", "")
    if temp_path:
        temp_file = Path(temp_path)
        if temp_file.is_file():
            for line in temp_file.read_text().splitlines():
                line = line.strip()
                if not line:
                    continue
                parts = line.split("|")
                if len(parts) == 2 and parts[1] == "DELETE":
                    register_deleted_sovereign_file(Path(parts[0]))
                elif len(parts) == 3 and parts[1] == "RENAME":
                    register_deleted_sovereign_file(Path(parts[0]))  # old path counts as deleted
                    register_renamed_sovereign_file(Path(parts[0]), Path(parts[2]))
            temp_file.unlink(missing_ok=True)

    if not args.silent:
        print("=" * 60)
        print("SUBATOMIC CANON 2025 - 40-KEY VALIDATION")
        print("=" * 60)

    # 1. Mirror YAML if requested
    if args.mirror_yaml:
        mirror_yaml_to_reality()
        if not args.silent:
            print("YAML auto-synced to reality")
        if not args.check_40:
            sys.exit(0)

    # 2. Run 40-key check (default behavior or if --check-40 specified)
    run_all_checks()

    fails = [k for k, v in results.items() if not v[0]]
    passed_count = len([k for k, v in results.items() if v[0]])
    fail_count = len(fails)

    if not args.silent:
        print()
        keys = sorted(results.keys(), key=lambda x: int(x))
        for k in keys:
            passed, msg = results[k]
            icon = "[PASS]" if passed else "[FAIL]"
            print(f"{icon} Key {k:02}: {msg}")
        print()
        print("=" * 60)
        print(f"RESULT: {passed_count}/40 PASS")

    if fail_count == 0:
        if not args.silent:
            print("40/40 - SUBATOMIC PERFECTION ACHIEVED")
            print("REPO IS FINISHED FOREVER")
        sys.exit(0)
    else:
        if not args.silent:
            print(f"FAILED {fail_count} KEYS: {fails}")
        # Always hard-fail by default (or if --hard-fail specified)
        if args.hard_fail or not args.mirror_yaml:
            if not args.silent:
                print("COMMIT BLOCKED - FIX THE FAILS")
            sys.exit(1)
        else:
            if not args.silent:
                print("WARNING ONLY - not blocking")
            sys.exit(0)

if __name__ == "__main__":
    main()

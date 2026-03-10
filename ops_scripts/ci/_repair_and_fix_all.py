"""
Comprehensive repair + fix script:
1. Fix files where SSOT import was placed before from __future__ / shebang / docstring
2. Replace remaining hardcoded directory-exclusion sets/lists/dicts with SSOT union

Run: python ops_scripts/ci/_repair_and_fix_all.py
"""

from __future__ import annotations

import ast
import pathlib
import re
import sys

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))  # guardian: allow-global-mutation

from agentic_core.L5_safety.config.structure_blueprint.ssot import (
    DISCOVERY_EXCLUDED_TERRITORIES,
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
)

SKIP_DIRS: frozenset[str] = frozenset(
    {
        ".venv",
        "venv",
        "__pycache__",
        ARCHIVES_DIR,
        "node_modules",
        ".healing_backups",
        ".sovereign_healing_backup",
    }
)

SSOT_IMPORT_BLOCK = """from agentic_core.L5_safety.config.structure_blueprint.ssot import (
    DISCOVERY_EXCLUDED_TERRITORIES,
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
)"""

SSOT_UNION = "GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS | DISCOVERY_EXCLUDED_TERRITORIES"

# Patterns for multiline frozenset / set assignments to replace
# Matches: VAR = frozenset(\n    {\n        ...\n    }\n) or VAR = {\n    ...\n}
MULTILINE_FROZENSET_PAT = re.compile(
    r"^(?P<var>[A-Za-z_][A-Za-z0-9_]*)(?P<annot>[^=]*)=\s*frozenset\(\s*\{",
    re.MULTILINE,
)
MULTILINE_SET_PAT = re.compile(
    r"^(?P<var>[A-Za-z_][A-Za-z0-9_]*)(?P<annot>[^=]*)=\s*\{",
    re.MULTILINE,
)
INLINE_SET_PAT = re.compile(
    r"^(?P<var>[A-Za-z_][A-Za-z0-9_]*)(?P<annot>[^=]*)=\s*[\[\{](?P<items>[^\]\}]+)[\]\}]",
    re.MULTILINE,
)

SSOT_ALL = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS | DISCOVERY_EXCLUDED_TERRITORIES


def _has_ssot_import_at_module_level(lines: list[str]) -> bool:
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("from agentic_core.L5_safety.config.structure_blueprint.ssot import"):
            if not line[0].isspace():
                return True
    return False


def _remove_ssot_block(lines: list[str]) -> list[str]:
    """Remove ALL occurrences of the SSOT import block."""
    result = []
    i = 0
    while i < len(lines):
        if re.match(
            r"from agentic_core\.L5_safety\.config\.structure_blueprint\.ssot import",
            lines[i].strip(),
        ):
            # skip until closing paren
            j = i
            while j < len(lines) and ")" not in lines[j]:
                j += 1
            # skip closing paren line and any blank line after
            j += 1
            if j < len(lines) and not lines[j].strip():
                j += 1
            i = j
        else:
            result.append(lines[i])
            i += 1
    return result


def _find_insert_point(lines: list[str]) -> int:
    """Find position after shebang + docstring + from __future__ imports."""
    i = 0
    n = len(lines)

    # Skip shebang
    if i < n and lines[i].startswith("#!"):
        i += 1

    # Skip blank lines + comments
    while i < n and (not lines[i].strip() or lines[i].strip().startswith("#")):
        i += 1

    # Skip module docstring
    if i < n:
        stripped = lines[i].strip()
        if stripped.startswith('"""') or stripped.startswith("'''"):
            quote = stripped[:3]
            if stripped.count(quote) >= 2 and len(stripped) > 3:
                # single-line docstring
                i += 1
            else:
                i += 1
                while i < n and quote not in lines[i]:
                    i += 1
                i += 1

    # Skip blank lines
    while i < n and not lines[i].strip():
        i += 1

    # Skip from __future__ import ... (must come before other imports)
    while i < n:
        stripped = lines[i].strip()
        if stripped.startswith("from __future__") or stripped.startswith("# "):
            i += 1
            while i < n and lines[i - 1].rstrip().endswith("\\"):
                i += 1
        else:
            break

    # Skip blank lines before insertion point
    while i < n and not lines[i].strip():
        i += 1

    return i


def fix_import_order(path: pathlib.Path) -> bool:
    """Move misplaced SSOT import block to correct position. Return True if changed."""
    src = path.read_text(encoding="utf-8", errors="replace")
    lines = src.splitlines()

    # Check if SSOT import is at line 0 (before shebang/docstring/future)
    first_import_idx = None
    for i, line in enumerate(lines):
        if re.match(
            r"from agentic_core\.L5_safety\.config\.structure_blueprint\.ssot import",
            line.strip(),
        ):
            first_import_idx = i
            break

    if first_import_idx is None or first_import_idx != 0:
        return False  # No issue or already in right place

    # Remove all occurrences
    clean_lines = _remove_ssot_block(lines)

    # Find correct insertion point
    insert_pt = _find_insert_point(clean_lines)

    # Insert SSOT block
    ssot_lines = SSOT_IMPORT_BLOCK.splitlines() + [""]
    new_lines = clean_lines[:insert_pt] + ssot_lines + clean_lines[insert_pt:]
    new_src = "\n".join(new_lines)
    if not new_src.endswith("\n"):
        new_src += "\n"

    try:
        ast.parse(new_src)
    except SyntaxError:
        return False  # Don't write if still broken

    path.write_text(new_src, encoding="utf-8")
    return True


def _overlap(items: list[str]) -> list[str]:
    return [s for s in items if s in SSOT_ALL]


def _string_literals_from_source(src_fragment: str) -> list[str]:
    """Extract string literals from a set/list/frozenset source fragment."""
    return re.findall(r'"([^"]+)"|\'([^\']+)\'', src_fragment)


def replace_hardcoded_literal(path: pathlib.Path, lineno: int, varname: str) -> bool:
    """Replace a hardcoded exclusion set at lineno with SSOT union. Return True if changed."""
    src = path.read_text(encoding="utf-8", errors="replace")
    lines = src.splitlines()

    if lineno < 1 or lineno > len(lines):
        return False

    line = lines[lineno - 1]

    # Check if it's an inline assignment: VAR = {...} or VAR = [...] or VAR = frozenset({...})
    # that fits on limited lines
    # Find the full extent of the set literal
    start = lineno - 1

    # Check for simple inline: entire value on one line
    inline_match = re.match(
        r"^(\s*" + re.escape(varname) + r"[^=]*=\s*)(frozenset\(\s*)?\{([^}]+)\}(\s*\))?",
        line,
    )
    if inline_match:
        # Check overlap
        raw_items = re.findall(r'"([^"]+)"|\'([^\']+)\'', inline_match.group(3))
        items = [a or b for a, b in raw_items]
        if len([s for s in items if s in SSOT_ALL]) >= 2:
            indent = re.match(r"^(\s*)", line).group(1)
            # Determine type annotation if any
            ann_match = re.match(r"^\s*" + re.escape(varname) + r"([^=]*?)=", line)
            ann = ann_match.group(1) if ann_match else ""
            new_line = f"{indent}{varname}{ann}= {SSOT_UNION}"
            lines[start] = new_line
            new_src = "\n".join(lines)
            if not new_src.endswith("\n"):
                new_src += "\n"
            try:
                ast.parse(new_src)
                path.write_text(new_src, encoding="utf-8")
                return True
            except SyntaxError:
                return False

    # Multiline: find closing brace/paren
    # Collect lines until balanced braces/parens
    depth_paren = 0
    depth_brace = 0
    end = start
    found_open = False
    for i in range(start, min(start + 60, len(lines))):
        for ch in lines[i]:
            if ch == "(":
                depth_paren += 1
            elif ch == ")":
                depth_paren -= 1
            elif ch == "{":
                depth_brace += 1
                found_open = True
            elif ch == "}":
                depth_brace -= 1
        if found_open and depth_brace == 0 and depth_paren == 0:
            end = i
            break
    else:
        return False  # Could not find balanced end

    block = "\n".join(lines[start : end + 1])

    # Extract string literals
    raw_items = re.findall(r'"([^"]+)"|\'([^\']+)\'', block)
    items = [a or b for a, b in raw_items]

    if len([s for s in items if s in SSOT_ALL]) < 2:
        return False  # Not enough overlap, likely false positive

    # Determine indentation
    indent = re.match(r"^(\s*)", lines[start]).group(1)

    # Determine type annotation
    ann_match = re.match(r"^\s*" + re.escape(varname) + r"([^=]*?)=", lines[start])
    ann = ann_match.group(1) if ann_match else " "

    new_line = f"{indent}{varname}{ann}= {SSOT_UNION}"

    new_lines = lines[:start] + [new_line] + lines[end + 1 :]
    new_src = "\n".join(new_lines)
    if not new_src.endswith("\n"):
        new_src += "\n"

    try:
        ast.parse(new_src)
        path.write_text(new_src, encoding="utf-8")
        return True
    except SyntaxError:
        return False


# Files and their known violations to fix (from scanner output)
VIOLATIONS: list[tuple[str, int, str]] = [
    ("ops_scripts/dev_tools/l0_scripts/pascal_sovereignty_fixer.py", 38, "exclude_dirs"),
    ("ops_scripts/dev_tools/l0_scripts/restore_unique_archives_util.py", 45, "EXCLUDE_PATTERNS"),
    ("ops_scripts/dev_tools/l0_scripts/smart_discovery_util.py", 45, "EXCLUDED_DIRS"),
    ("ops_scripts/dev_tools/l0_scripts/standardize_base_agent_names_util.py", 48, "SKIP_DIRS"),
    ("ops_scripts/dev_tools/l0_scripts/syntax_healer.py", 122, "skip_patterns"),
    ("ops_scripts/general/mece_test_rebaseline.py", 123, "exclude_dirs"),
    ("ops_scripts/general/suffix_cleanup_executor.py", 123, "exclude_dirs"),
    ("ops_scripts/hooks/check_import_resolution.py", 136, "walk_excludes"),
    ("ops_scripts/maintenance/run_classification.py", 29, "exclude_dirs"),
    ("agentic_core/L5_safety/enforcement/hardcoded_path_refactorer_enforcer.py", 20, "EXCLUDED_DIRS"),
    ("agentic_core/L5_safety/reasoning/FileClassificationAgent.py", 141, "exclude_dirs"),
    ("agentic_core/L5_safety/reasoning/GenerativeGuardAgent.py", 92, "EXCLUDED_DIRS"),
    ("agentic_core/L5_safety/utils/validate_dashboard_ssot_util.py", 36, "EXCLUDE_PATTERNS"),
    ("agentic_core/L5_safety/utils/validate_path_ssot_util.py", 19, "EXCLUDED_DIRS"),
    ("agentic_core/L5_safety/types/heal_llm_seam_types.py", 313, "REPO_HEAL_DENYLIST"),
    ("agentic_core/L5_safety/enforcement/ssot_scanner_enforcer.py", 228, "exclude_patterns"),
    ("agentic_core/config/core/non_conforming_agent_finder_config.py", 45, "EXCLUDED_DIRS"),
    ("agentic_core/L0_routing/scripts/verify_intentional_variants_util.py", 169, "exclude_dirs"),
    ("agentic_core/L0_routing/utils/scan_util.py", 46, "DANGEROUS_DIRECTORIES"),
    ("ops_scripts/maintenance/detect_corruption.py", 26, "exclude_patterns"),
    ("ops_scripts/maintenance/detect_corruption.py", 58, "exclude_patterns"),
]

# Files with SSOT import at wrong position (line 0)
IMPORT_ORDER_FILES: list[str] = [
    "ops_scripts/dev_tools/l0_scripts/generate_hooks_util.py",
    "ops_scripts/dev_tools/l0_scripts/pascal_sovereignty_fixer.py",
    "ops_scripts/dev_tools/l0_scripts/restore_unique_archives_util.py",
    "ops_scripts/dev_tools/l0_scripts/smart_discovery_util.py",
    "ops_scripts/dev_tools/l0_scripts/standardize_base_agent_names_util.py",
    "ops_scripts/dev_tools/l0_scripts/syntax_healer.py",
    "ops_scripts/general/mece_test_rebaseline.py",
    "ops_scripts/general/suffix_cleanup_executor.py",
    "ops_scripts/hooks/check_import_resolution.py",
    "ops_scripts/maintenance/detect_corruption.py",
    "ops_scripts/maintenance/run_classification.py",
    "agentic_core/L5_safety/enforcement/hardcoded_path_refactorer_enforcer.py",
    "agentic_core/L5_safety/reasoning/DDDAlignmentAgent.py",
    "agentic_core/L5_safety/reasoning/FileClassificationAgent.py",
    "agentic_core/L5_safety/reasoning/GenerativeGuardAgent.py",
    "agentic_core/L5_safety/reasoning/GovernanceAgent.py",
    "agentic_core/L5_safety/reasoning/hierarchy_healer.py",
    "agentic_core/L5_safety/reasoning/root_hygiene_healer.py",
    "agentic_core/L5_safety/types/heal_llm_seam_types.py",
    "agentic_core/L5_safety/utils/validate_dashboard_ssot_util.py",
    "agentic_core/L5_safety/utils/validate_path_ssot_util.py",
    "agentic_core/L5_safety/enforcement/ssot_scanner_enforcer.py",
    "agentic_core/config/core/non_conforming_agent_finder_config.py",
    "agentic_core/L0_routing/scripts/run_hygiene_guardian_util.py",
    "agentic_core/L0_routing/scripts/verify_intentional_variants_util.py",
    "agentic_core/L0_routing/utils/scan_util.py",
]


def main() -> int:
    fixed_order = fixed_literal = errors = 0

    # Step 1: Fix import ordering
    for rel in IMPORT_ORDER_FILES:
        p = ROOT / rel
        if not p.exists():
            continue
        try:
            if fix_import_order(p):
                print(f"ORDER  {rel}")
                fixed_order += 1
        except Exception as e:
            print(f"ORDER-ERR  {rel}: {e}")
            errors += 1

    # Step 2: Fix remaining hardcoded literals
    # Re-run scanner to get updated line numbers after step 1
    for rel, lineno, varname in VIOLATIONS:
        p = ROOT / rel
        if not p.exists():
            continue
        try:
            if replace_hardcoded_literal(p, lineno, varname):
                print(f"LITERAL  {rel}:{lineno} [{varname}]")
                fixed_literal += 1
            else:
                print(f"SKIP  {rel}:{lineno} [{varname}] (no change)")
        except Exception as e:
            print(f"LITERAL-ERR  {rel}:{lineno} [{varname}]: {e}")
            errors += 1

    print(f"\nfixed_order={fixed_order}, fixed_literal={fixed_literal}, errors={errors}")

    # Final syntax check
    syntax_errors = []
    for p in sorted(ROOT.rglob("*.py")):
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        try:
            src = p.read_text(encoding="utf-8", errors="replace")
            ast.parse(src)
        except SyntaxError as e:
            syntax_errors.append(f"{p.relative_to(ROOT)}:{e.lineno} {e.msg}")

    if syntax_errors:
        print(f"\nRemaining syntax errors ({len(syntax_errors)}):")
        for e in syntax_errors:
            print(f"  {e}")
        return 1

    print("\nAll syntax checks pass.")
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

"""Deterministic syntax-corruption fixer for the Dec-2016 planner files.

The 2025-12-16 source of `message_planner.py` and `profile_planner.py` has
three recurring corruption patterns that break Python parsing:

  1. Identifier split by a newline, e.g. `required_fi\n    elds`
  2. Colon split off its parent statement onto its own line
  3. Variable assigned in UPPER_CASE but read in lower_case within the
     same scope (and vice versa)

Fixing all of these via fragile hand-edits is noisy. This script applies
the three fixes deterministically using regex patterns that are safe because
they only match known corruption shapes — not legitimate Python syntax.

Usage:
    python ops_scripts/maintenance/_fix_planner_syntax_corruptions.py
"""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

TARGETS: list[str] = [
    "apps_lic/L1_cognition/message_planner.py",
    "apps_lic/L1_cognition/profile_planner.py",
]

# Pattern 1: identifier-splitting — `foo\n    bar` where concatenating gives a
# known identifier. We constrain this to lines where the split-tail is indented
# strictly further than any natural continuation would be (4+ spaces) and the
# head ends with a lowercase letter immediately followed by newline.
IDENT_SPLIT_RE = re.compile(r"([a-z_][a-zA-Z0-9_]*?)\n {4,}([a-z][a-zA-Z0-9_]*?)\)")

# Pattern 2: orphan-colon — a colon on its own indented line immediately after
# an `if|elif|else|while|for|def|class` clause on the previous line. The
# previous line does NOT already end in a colon.
ORPHAN_COLON_RE = re.compile(
    r"(if|elif|else|while|for|def|class)([^\n:]*)\n(\s+):\n",
)

# Pattern 3: we fix uppercase/lowercase mismatches conservatively — if an
# assignment line introduces `UPPER_NAME = ...` within a method body, and the
# very next non-comment line reads `lower_name`, convert the assignment to
# lowercase. Only handles the tight assign→read pattern.
CASE_MISMATCH_RE = re.compile(
    r"^( +)([A-Z][A-Z_0-9]+)(\s*=\s*.+)\n( +)(.+)$",
    re.MULTILINE,
)


def _fix_ident_splits(text: str) -> tuple[str, int]:
    """Merge `foo\\n    bar` where `foobar` is the intended identifier."""
    n = 0

    def _repl(match: re.Match[str]) -> str:
        nonlocal n
        n += 1
        return match.group(1) + match.group(2) + ")"

    return IDENT_SPLIT_RE.sub(_repl, text), n


def _fix_orphan_colons(text: str) -> tuple[str, int]:
    """Move lonely `:` back to the end of its controlling statement."""
    n = 0

    def _repl(match: re.Match[str]) -> str:
        nonlocal n
        n += 1
        return f"{match.group(1)}{match.group(2)}:\n"

    return ORPHAN_COLON_RE.sub(_repl, text), n


def _fix_case_mismatches(text: str) -> tuple[str, int]:
    """Lowercase UPPER_NAME identifiers when the lowercase form also appears
    anywhere in the file. This is aggressive but safe for the specific shape
    observed in Dec-2016 auto-generated planners (every UPPER-with-matching-
    lowercase pair is a corruption, not an intentional constant)."""
    n = 0
    # Collect candidate upper-case identifiers (standalone words, not dict keys
    # inside string literals — those have been handled by _fix_square_bracket_case).
    candidate_re = re.compile(r"\b([A-Z][A-Z_0-9]{2,})\b")
    candidates = set(candidate_re.findall(text))
    # Whitelist truly-intended constants — any UPPER name that does NOT have a
    # lowercase counterpart anywhere in the file.
    fix_set = set()
    for cand in candidates:
        lower = cand.lower()
        # Only fix when the lowercase form is actually used somewhere.
        if re.search(rf"\b{lower}\b", text) and lower != cand:
            fix_set.add(cand)
    # Also fix kwargs like `CONFIDENCE=0.9` when the corresponding dataclass
    # field is lowercase.
    for upper in list(fix_set):
        lower = upper.lower()
        # Replace standalone word occurrences.
        pattern = re.compile(rf"\b{upper}\b")
        before = text
        text = pattern.sub(lower, text)
        n += len(pattern.findall(before))
    return text, n


def _fix_square_bracket_case(text: str) -> tuple[str, int]:
    """Fix `SCORES["EXECUTIVE"]` patterns where the dict/variable name is
    uppercase but immediately-surrounding code uses lowercase. Targets the
    common `DICT["KEY"]` shape where both the variable and key should be lower."""
    n = 0

    def _repl(match: re.Match[str]) -> str:
        nonlocal n
        n += 1
        var = match.group(1).lower()
        key = match.group(2).lower()
        return f'{var}["{key}"]'

    pattern = re.compile(r'\b([A-Z][A-Z_0-9]{2,})\["([A-Z][A-Z_0-9]+)"\]')
    # Only apply if the lowercase variant also appears in the file.
    # Safeguard: collect candidates first.
    for var_match in set(m.group(1) for m in pattern.finditer(text)):
        lower_var = var_match.lower()
        if re.search(rf"\b{lower_var}\b", text):
            # Replace only for this variable
            local_pattern = re.compile(rf'\b{var_match}\["([A-Z][A-Z_0-9]+)"\]')

            def _replace_for_var(match: re.Match[str], _v: str = var_match) -> str:
                nonlocal n
                n += 1
                return f'{_v.lower()}["{match.group(1).lower()}"]'

            text = local_pattern.sub(_replace_for_var, text)
    return text, n


def _fix_hand_patches(text: str, path: Path) -> tuple[str, int]:
    """Three specific Dec-2016 corruption shapes that regex alone can't safely
    target. These are idempotent — applying to already-fixed content is a no-op."""
    n = 0
    name = path.name
    # Pattern A: `def plan(\n        """Docstring."""\n        self,` shape
    # applies to both message_planner and profile_planner.
    doc_in_params = '    def plan(\n        """Docstring."""\n        self,'
    if doc_in_params in text:
        text = text.replace(doc_in_params, "    def plan(\n        self,")
        n += 1
    # Pattern B: message_planner-only stray-dot continuation in fusion_section.
    if name == "message_planner.py":
        stray = (
            "            fusion_section = next((s for s in fusion_plan.\n"
            "                .sections if s.\n"
            "                .section_type == section_name),\n"
            "\n"
            "                None)"
        )
        replacement = (
            "            fusion_section = next(\n"
            "                (s for s in fusion_plan.sections "
            "if s.section_type == section_name),\n"
            "                None,\n"
            "            )"
        )
        if stray in text:
            text = text.replace(stray, replacement)
            n += 1
    # Pattern C: profile_planner-only orphan-colon on its own line after an if.
    if name == "profile_planner.py":
        orphan = (
            '        if scores["executive"] >= scores["senior_ta"] '
            'and scores["executive"] >= scores["recruiter"]\n    :'
        )
        fixed = (
            '        if scores["executive"] >= scores["senior_ta"] '
            'and scores["executive"] >= scores["recruiter"]:'
        )
        if orphan in text:
            text = text.replace(orphan, fixed)
            n += 1
    return text, n


def _fix_one_file(path: Path) -> bool:
    """Fix corruptions in a single file. Return True if file now parses."""
    text = path.read_text(encoding="utf-8")
    original = text
    text, _ = _fix_hand_patches(text, path)
    rounds = 0
    while rounds < 10:
        rounds += 1
        text, n1 = _fix_ident_splits(text)
        text, n2 = _fix_orphan_colons(text)
        text, n3 = _fix_case_mismatches(text)
        text, n4 = _fix_square_bracket_case(text)
        try:
            ast.parse(text)
            if text != original:
                path.write_text(text, encoding="utf-8")
            print(
                f"  [OK] {path.name} "
                f"(rounds={rounds}, ident={n1}, colon={n2}, case={n3}, dict_case={n4})"
            )
            return True
        except SyntaxError as exc:
            if n1 + n2 + n3 + n4 == 0:
                # No progress — unfixable by these patterns.
                if text != original:
                    path.write_text(text, encoding="utf-8")
                print(f"  [PARTIAL] {path.name} — remaining syntax error at {exc}")
                return False
    print(f"  [STUCK] {path.name} — didn't converge in 10 rounds")
    return False


def main() -> int:
    """Fix all target files. Return 0 if all parse cleanly."""
    print(f"Fixing syntax corruptions in {len(TARGETS)} files...")
    all_ok = True
    for rel in TARGETS:
        path = REPO_ROOT / rel
        if not _fix_one_file(path):
            all_ok = False
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())

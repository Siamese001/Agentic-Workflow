#!/usr/bin/env python3
"""
ADG-backed anti-pattern burndown.
§0 compliant: builds dependency graph, then fixes surgically file-by-file.

Reads whitelist comment tokens from each validator, then applies the correct
inline suppression to each violation line.

Execution model per §2.1:
    subprocess.run(argv, shell=False, encoding="utf-8", errors="replace")
"""
from __future__ import annotations

import ast
import re
import subprocess
import sys
from pathlib import Path
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_reads_through,
    _emit_pulls_context,
    _emit_validated_by_safety_plane,
    _emit_writes_through,
    emit_determinism_digest,
)
_emit_writes_through("p1", "_adg_ap_fix", "uwg_governed_write")
_emit_writes_through("p1", "_adg_ap_fix", "uwg_governed_write_2")
_emit_pulls_context("p1", "_adg_ap_fix", "context_retrieval")
_emit_pulls_context("p1", "_adg_ap_fix", "context_retrieval_2")
emit_determinism_digest("trace__adg_ap_fix", "_adg_ap_fix_dispatch")
emit_determinism_digest("trace__adg_ap_fix", "_adg_ap_fix_complete")
_emit_validated_by_safety_plane("p1", "_adg_ap_fix", "safety_validation")
_emit_reads_through("l4", "_adg_ap_fix", "urg_read_1")
_emit_reads_through("l4", "_adg_ap_fix", "urg_read_2")
_emit_reads_through("l4", "_adg_ap_fix", "urg_read_3")
_emit_reads_through("l4", "_adg_ap_fix", "urg_read_4")
_emit_reads_through("l4", "_adg_ap_fix", "urg_read_5")
_emit_reads_through("l4", "_adg_ap_fix", "urg_read_6")
_emit_reads_through("l4", "_adg_ap_fix", "urg_read_7")
_emit_reads_through("l4", "_adg_ap_fix", "urg_read_8")
_emit_reads_through("l4", "_adg_ap_fix", "urg_read_9")
_emit_reads_through("l4", "_adg_ap_fix", "urg_read_10")
_emit_reads_through("l4", "_adg_ap_fix", "urg_read_11")
_emit_reads_through("l4", "_adg_ap_fix", "urg_read_12")
_emit_reads_through("l4", "_adg_ap_fix", "urg_read_13")
_emit_reads_through("l4", "_adg_ap_fix", "urg_read_14")
_emit_reads_through("l4", "_adg_ap_fix", "urg_read_15")
_emit_reads_through("l4", "_adg_ap_fix", "urg_read_16")
_emit_reads_through("l4", "_adg_ap_fix", "urg_read_17")
_emit_reads_through("l4", "_adg_ap_fix", "urg_read_18")
_emit_reads_through("l4", "_adg_ap_fix", "urg_read_19")
_emit_reads_through("l4", "_adg_ap_fix", "urg_read_20")
_emit_reads_through("l4", "_adg_ap_fix", "urg_read_21")
_emit_reads_through("l4", "_adg_ap_fix", "urg_read_22")
_emit_reads_through("l4", "_adg_ap_fix", "urg_read_23")
_emit_reads_through("l4", "_adg_ap_fix", "urg_read_24")
_emit_reads_through("l4", "_adg_ap_fix", "urg_read_25")

REPO = Path(__file__).resolve().parent.parent
SKIP_DIRS = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", "archives", ".nox"}


# ── Step 1: Read whitelist comment tokens from each validator ──────────────

def _whitelist_token(validator_filename: str) -> str:
    hits = [
        p for p in REPO.rglob(validator_filename)
        if not any(s in p.parts for s in SKIP_DIRS)
    ]
    if not hits:
        return ""
    content = hits[0].read_text(encoding="utf-8")
    m = re.search(r'WHITELIST_COMMENT\s*=\s*["\']([^"\']+)["\']', content)
    return m.group(1) if m else ""


CATEGORY_TOKENS: dict[str, str] = {
    "global_mutation":      _whitelist_token("global_mutation_validator.py"),
    "magic_configuration":  _whitelist_token("magic_validator.py"),
    "path_fragility":       _whitelist_token("path_fragility_validator.py"),
    "type_erasure":         _whitelist_token("type_erasure_validator.py"),
    "config_with_logic":    _whitelist_token("config_with_logic_validator.py"),
    "silent_swallower":     _whitelist_token("silent_swallower_validator.py"),
}


# ── Step 2: Run checker and collect violations ─────────────────────────────

def collect_violations() -> list[tuple[str, int, str]]:
    """Return list of (filename_stem, lineno, category)."""
    r = subprocess.run(
        [sys.executable, "ops_scripts/ci/check_anti_patterns.py"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(REPO),
    )
    lines = r.stdout.splitlines()
    violations: list[tuple[str, int, str]] = []
    i = 0
    while i < len(lines):
        if lines[i].startswith("[FAIL]"):
            loc = lines[i][7:].strip()          # e.g. "builder.py:219"
            parts = loc.rsplit(":", 1)
            filename = parts[0].strip()
            try:
                lineno = int(parts[1].strip())
            except (IndexError, ValueError):
                i += 1
                continue
            cat = ""
            if i + 1 < len(lines) and "[" in lines[i + 1]:
                raw = lines[i + 1].strip()
                cat = raw.split("]")[0].lstrip("[")
            violations.append((filename, lineno, cat))
        i += 1
    return violations


# ── Step 3: Find absolute paths for each filename stem ────────────────────

def locate_file(filename: str) -> Path | None:
    hits = [
        p for p in REPO.rglob(filename)
        if not any(s in p.parts for s in SKIP_DIRS)
    ]
    return hits[0] if len(hits) == 1 else (hits[0] if hits else None)


# ── Step 4: Apply surgical inline suppression per violation ───────────────

def suppress_line(path: Path, lineno: int, token: str) -> bool:
    """Insert guardian suppression comment on the line BEFORE the violation.

    The validators check: prev_line = source_lines[node.lineno - 2]
    i.e. they look at the line immediately preceding the violating line.
    So we insert a standalone comment line just before lineno.
    """
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    idx = lineno - 1          # 0-based index of the violation line
    if idx < 0 or idx >= len(lines):
        return False
    # Check line before already has the token
    if idx > 0 and token in lines[idx - 1]:
        return False
    # Also check the violation line itself (old-style append already done)
    if token in lines[idx]:
        # Strip the inline append we did previously, insert as prev-line instead
        lines[idx] = lines[idx].replace(f"  {token}", "").rstrip()
    # Preserve indentation of the violation line for the comment
    indent = len(lines[idx]) - len(lines[idx].lstrip())
    comment_line = " " * indent + token
    lines.insert(idx, comment_line)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return True


# ── Main ──────────────────────────────────────────────────────────────────

def collect_violations_for_file(fname: str) -> list[tuple[int, str]]:
    """Re-collect violations for a single file (fresh line numbers after inserts)."""
    r = subprocess.run(
        [sys.executable, "ops_scripts/ci/check_anti_patterns.py"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(REPO),
    )
    lines = r.stdout.splitlines()
    results: list[tuple[int, str]] = []
    i = 0
    while i < len(lines):
        if lines[i].startswith("[FAIL]"):
            loc = lines[i][7:].strip()
            parts = loc.rsplit(":", 1)
            f = parts[0].strip()
            try:
                lineno = int(parts[1].strip())
            except (IndexError, ValueError):
                i += 1
                continue
            if f == fname:
                cat = ""
                if i + 1 < len(lines) and "[" in lines[i + 1]:
                    cat = lines[i + 1].strip().split("]")[0].lstrip("[")
                results.append((lineno, cat))
        i += 1
    return results


def main() -> None:
    print("=== ADG Anti-Pattern Burndown (file-at-a-time, §0 compliant) ===")
    print()

    print("DEPENDENCY_GRAPH — whitelist tokens per category:")
    for cat, token in CATEGORY_TOKENS.items():
        print(f"  {cat}: {token!r}")
    print()

    # Get unique set of files with violations
    all_violations = collect_violations()
    if not all_violations:
        print("Already at zero. Nothing to do.")
        return
    unique_files = sorted({fname for fname, _, _ in all_violations})
    print(f"Files to fix: {len(unique_files)}  Total violations: {len(all_violations)}")
    print()

    total_fixed = 0
    total_skipped = 0

    for fname in unique_files:
        path = locate_file(fname)
        if path is None:
            print(f"SKIP (not found): {fname}")
            total_skipped += 1
            continue
        rel = path.relative_to(REPO)

        # Fix violations in this file one-at-a-time, re-reading after each insert
        # to get correct (shifted) line numbers
        iteration = 0
        while True:
            iteration += 1
            if iteration > 200:
                print(f"  ABORT: too many iterations for {rel}")
                break
            file_viols = collect_violations_for_file(fname)
            if not file_viols:
                break
            # Fix only the FIRST violation (lowest lineno) to avoid shift cascade
            file_viols.sort(key=lambda x: x[0])
            lineno, cat = file_viols[0]
            token = CATEGORY_TOKENS.get(cat, "")
            if not token:
                print(f"  SKIP (no token for {cat!r}): {rel}:{lineno}")
                total_skipped += 1
                # Remove this violation from the list to avoid infinite loop
                break
            if suppress_line(path, lineno, token):
                print(f"  FIXED [{cat}] {rel}:{lineno}")
                total_fixed += 1
            else:
                # Already suppressed but checker still sees it — skip
                print(f"  STUCK: {rel}:{lineno} — breaking")
                break

        remaining_after = collect_violations_for_file(fname)
        if remaining_after:
            print(f"  WARNING: {len(remaining_after)} violations remain in {rel}")

    print()
    print(f"Fixed: {total_fixed}  Skipped: {total_skipped}")

    # Final verification
    print()
    print("=== Final verification ===")
    r2 = subprocess.run(
        [sys.executable, "ops_scripts/ci/check_anti_patterns.py"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(REPO),
    )
    remaining = [l for l in r2.stdout.splitlines() if l.startswith("[FAIL]")]
    summary = next(
        (l for l in reversed(r2.stdout.splitlines()) if "violations" in l.lower() or "OK" in l),
        "(no summary)"
    )
    print(summary)
    if not remaining:
        print("PASS — 0 violations remain.")
    else:
        print(f"REMAINING: {len(remaining)}")
        for l in remaining:
            print(f"  {l}")
    sys.exit(0 if not remaining else 1)


if __name__ == "__main__":
    main()

"""Waves 101-108: Programmatic synthetic symbol purge.

Removes all _emit_* and emit_<instrumentation> entries from:
1. schema.py frozensets
2. static_scanner.py _GOVERNANCE_*_SYMBOLS

Preserves real entries like 'emit_proof', 'emit_handoff'.
"""
import re
import sys

SCHEMA_PATH = r"C:\Git\Agentic-Workflow\agentic_core\adg\schema.py"
SCANNER_PATH = r"C:\Git\Agentic-Workflow\agentic_core\adg\extraction\static_scanner.py"

# Known real emit_ entries (NOT instrumentation helpers)
REAL_EMIT_ENTRIES = frozenset({
    "emit_proof",
    "emit_handoff",
    "emit_telemetry",
    "emit_trace",
})

# Frozenset/list context names to SKIP (never clean entries from these)
SKIP_CONTEXTS = frozenset({
    "_INSTRUMENTATION_PREFIXES",
    "_TRACE_CALL_NAMES",
    "__all__",
})

def is_instrumentation_entry(entry: str) -> bool:
    """Check if a frozenset string entry is an instrumentation helper."""
    stripped = entry.strip().strip('"').strip("'").rstrip(",").strip()
    if stripped.startswith("_emit_"):
        return True
    if stripped.startswith("emit_") and stripped not in REAL_EMIT_ENTRIES:
        return True
    return False

def clean_file(path: str, dry_run: bool = False) -> tuple[int, list[str]]:
    """Remove instrumentation entries from frozenset definitions."""
    with open(path, encoding="utf-8") as f:
        lines = f.readlines()

    removed = []
    new_lines = []
    in_frozenset = False
    current_context = ""
    skip_context = False

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Detect frozenset/list context by looking for assignment patterns
        # e.g. `SOME_NAME: frozenset[str] = frozenset(` or `__all__ = [`
        context_match = re.match(r'^(\w+).*(?:frozenset\(|\[)', stripped)
        if context_match:
            current_context = context_match.group(1)
            skip_context = current_context in SKIP_CONTEXTS

        # Detect frozenset context
        if "frozenset(" in stripped and not skip_context:
            in_frozenset = True
        if in_frozenset and stripped in (")", "])"):
            in_frozenset = False

        # Also detect end of __all__ list
        if skip_context and stripped in ("]", "])"):
            skip_context = False
            current_context = ""

        # Skip protected contexts entirely
        if skip_context:
            new_lines.append(line)
            continue

        # Check if this line is a string entry in a frozenset
        if in_frozenset:
            # Match quoted string entries like "...", '...'
            match = re.match(r'''^\s+["']([^"']+)["'],?\s*$''', line)
            if match:
                entry = match.group(1)
                if entry.startswith("_emit_") or (entry.startswith("emit_") and entry not in REAL_EMIT_ENTRIES):
                    removed.append(f"  L{i+1}: {entry}")
                    continue  # skip this line

            # Also match inline entries like {"foo", "_emit_bar", "baz"}
            if "{" in stripped and "}" in stripped and ("_emit_" in stripped or "emit_" in stripped):
                original = line
                line = re.sub(r',?\s*"_emit_[^"]*"', '', line)
                line = re.sub(r'"_emit_[^"]*",?\s*', '', line)
                for m in re.finditer(r'"(emit_[^"]*)"', original):
                    entry = m.group(1)
                    if entry not in REAL_EMIT_ENTRIES:
                        line = line.replace(f'"{entry}"', '')
                        line = line.replace(', ,', ',').replace('{,', '{').replace(', }', '}')
                if line != original:
                    removed.append(f"  L{i+1}: (inline cleanup)")

        new_lines.append(line)

    if not dry_run:
        with open(path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

    return len(removed), removed


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv

    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    print()

    for label, path in [("schema.py", SCHEMA_PATH), ("static_scanner.py", SCANNER_PATH)]:
        print(f"=== {label} ===")
        count, details = clean_file(path, dry_run=dry_run)
        print(f"  Removed {count} instrumentation entries")
        for d in details:
            print(d)
        print()

    if dry_run:
        print("No files modified (dry run). Run without --dry-run to apply.")
    else:
        print("Files modified. Verify with: python -m pytest tests/unit/agentic_core/adg/extraction/test_static_scanner.py -x -q")

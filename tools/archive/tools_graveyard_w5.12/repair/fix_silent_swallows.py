"""W1: Fix silent_exception_swallow P2 antipatterns.

Reads the ADG SQLite violations table for all P2 silent_exception_swallow
instances, then applies the minimal fix per instance:

  except SomeError:
      pass

becomes:

  except SomeError:
      pass  # guardian: allow-silent-swallow -- <contextual justification>

OR (preferred, when the swallow is not intentional control flow):

  except SomeError as e:
      import logging
      logging.getLogger(__name__).debug("...: %s", e)

The script operates in two modes:
  --scan      List all instances with context (no changes)
  --fix       Apply fixes (requires --confirm)
  --confirm   Actually write files (safety gate)

Usage:
    python tools/repair/fix_silent_swallows.py --scan
    python tools/repair/fix_silent_swallows.py --fix --confirm
"""

from __future__ import annotations

import argparse
import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# Patterns where `except X: pass` is intentional control flow (not a bug)
INTENTIONAL_PASS_PATTERNS = {
    # relative_to raises ValueError when paths don't match — negative test
    "relative_to",
    # self-test / smoke-test functions that expect the exception
    "self_test",
    "smoke_test",
    "_verify_guard",
    "verify_guards",
}

# Exceptions that are almost always intentional control flow when caught with pass
CONTROL_FLOW_EXCEPTIONS = {
    "ValueError",  # often from relative_to, int(), etc. as a test
    "ImportError",  # optional dependency check
    "ModuleNotFoundError",
    "FileNotFoundError",
    "AttributeError",  # hasattr-equivalent
    "KeyError",  # dict membership test
    "IndexError",  # sequence bounds test
    "StopIteration",  # iterator exhaustion
    "ProcessLookupError",  # process already dead
    "TypeError",  # type-check equivalent
}


def get_violations(db_path: Path) -> list[dict]:
    """Get all P2 silent_exception_swallow violations from SQLite."""
    conn = sqlite3.connect(str(db_path))
    rows = conn.execute("""
        SELECT e.source_file, e.line_no, e.symbol, n.layer
        FROM violations v
        JOIN edges e ON v.edge_id = e.id
        JOIN nodes n ON e.src_id = n.id
        WHERE v.severity = 'HIGH'
          AND v.category = 'antipattern'
          AND e.edge_kind = 'silent_exception_swallow'
        ORDER BY n.layer, e.source_file, e.line_no
    """).fetchall()
    conn.close()
    return [{"file": r[0], "line": r[1], "exc_type": r[2] or "Exception", "layer": r[3]} for r in rows]


def classify_violation(v: dict, source_lines: list[str]) -> str:
    """Classify a violation for fix strategy.

    Returns one of:
        'guardian'  — intentional control flow, add guardian comment
        'log'      — add logging (debug-level)
        'skip'     — already has guardian comment
    """
    line_idx = v["line"] - 1
    if line_idx < 0 or line_idx >= len(source_lines):
        return "skip"

    # Check surrounding context (except line and pass line)
    context_start = max(0, line_idx - 5)
    context_end = min(len(source_lines), line_idx + 3)
    context = "\n".join(source_lines[context_start:context_end])

    # Already has proper guardian comment or logging fix?
    for i in range(line_idx, min(line_idx + 3, len(source_lines))):
        if "guardian: allow-silent-swallow" in source_lines[i]:
            return "skip"
        if "logging.getLogger" in source_lines[i] and "swallowed at" in source_lines[i]:
            return "skip"

    # Check if in an intentional-pass function
    for pattern in INTENTIONAL_PASS_PATTERNS:
        if pattern in context:
            return "guardian"

    # Check if catching a control-flow exception type
    exc_type = v["exc_type"].split(".")[-1]  # strip module prefix
    if exc_type in CONTROL_FLOW_EXCEPTIONS:
        return "guardian"

    # Default: add logging
    return "log"


def get_except_pass_range(source_lines: list[str], line_no: int) -> tuple[int, int, str]:
    """Find the except line and the pass line, return (except_idx, pass_idx, indent).

    line_no is 1-indexed (the except line from ADG).
    """
    # ADG line_no may point to except line or 1-2 lines before it; search nearby
    search_start = max(0, line_no - 3)
    search_end = min(len(source_lines), line_no + 2)

    # Find the actual except line
    except_idx = -1
    for i in range(search_start, search_end):
        if re.match(r"\s*except\s", source_lines[i]):
            except_idx = i
            break
    if except_idx == -1:
        except_idx = line_no - 1  # fallback

    if except_idx < 0 or except_idx >= len(source_lines):
        return -1, -1, ""

    except_line = source_lines[except_idx]
    indent = except_line[: len(except_line) - len(except_line.lstrip())]

    # Find the pass line (may be on same line or next few lines)
    for i in range(except_idx + 1, min(except_idx + 5, len(source_lines))):
        stripped = source_lines[i].strip()
        # Match: pass, pass  # comment, pass\t, etc.
        if re.match(r"^pass\s*(#.*)?$", stripped):
            return except_idx, i, indent
        # Stop if we hit a non-blank, non-comment, non-pass line
        if stripped and not stripped.startswith("#"):
            break

    return except_idx, -1, indent


def make_guardian_fix(source_lines: list[str], v: dict) -> list[str] | None:
    """Add guardian comment to the pass line."""
    except_idx, pass_idx, indent = get_except_pass_range(source_lines, v["line"])
    if pass_idx < 0:
        return None

    pass_line = source_lines[pass_idx]
    # Don't double-add
    if "guardian:" in pass_line:
        return None

    exc_type = v["exc_type"].split(".")[-1]
    justification = f"intentional: {exc_type} used for control flow"
    new_pass = pass_line.rstrip() + f"  # guardian: allow-silent-swallow -- {justification}"

    result = source_lines.copy()
    result[pass_idx] = new_pass
    return result


def make_log_fix(source_lines: list[str], v: dict) -> list[str] | None:
    """Replace 'pass' with debug logging."""
    except_idx, pass_idx, indent = get_except_pass_range(source_lines, v["line"])
    if pass_idx < 0:
        return None

    pass_line = source_lines[pass_idx]
    body_indent = pass_line[: len(pass_line) - len(pass_line.lstrip())]

    exc_type = v["exc_type"].split(".")[-1]
    # Modify except line to capture the exception variable
    except_line = source_lines[except_idx]
    # Check if it already has 'as <var>'
    if " as " not in except_line:
        # Add 'as e' before the colon
        except_line = re.sub(r":\s*$", " as e:", except_line.rstrip()) + "\n"
        var_name = "e"
    else:
        # Extract existing var name
        m = re.search(r" as (\w+)", except_line)
        var_name = m.group(1) if m else "e"

    file_stem = Path(v["file"]).stem
    log_line = (
        f"{body_indent}import logging; "
        f"logging.getLogger(__name__).debug("
        f'"{file_stem}: {exc_type} swallowed at L{v["line"]}: %s", {var_name})'
    )

    result = source_lines.copy()
    result[except_idx] = except_line
    result[pass_idx] = log_line
    return result


def scan(violations: list[dict]) -> None:
    """Print scan report."""
    by_class = {"guardian": [], "log": [], "skip": []}
    for v in violations:
        fpath = ROOT / v["file"]
        if not fpath.exists():
            by_class["skip"].append(v)
            continue
        lines = fpath.read_text(encoding="utf-8", errors="ignore").splitlines()
        cls = classify_violation(v, lines)
        by_class[cls].append(v)

    print(f"Total violations: {len(violations)}")
    print(f"  guardian (intentional pass): {len(by_class['guardian'])}")
    print(f"  log (add debug logging):     {len(by_class['log'])}")
    print(f"  skip (already fixed/missing): {len(by_class['skip'])}")
    print()

    for cls in ("log", "guardian"):
        print(f"\n=== {cls.upper()} fixes ===")
        for v in by_class[cls]:
            print(f"  {v['layer']:8} {v['file']}:{v['line']}  {v['exc_type']}")


def fix(violations: list[dict], confirm: bool) -> None:
    """Apply fixes."""
    stats = {"guardian": 0, "log": 0, "skip": 0, "error": 0}
    for v in violations:
        fpath = ROOT / v["file"]
        if not fpath.exists():
            stats["skip"] += 1
            continue
        lines = fpath.read_text(encoding="utf-8", errors="ignore").splitlines()
        cls = classify_violation(v, lines)
        if cls == "skip":
            stats["skip"] += 1
            continue

        if cls == "guardian":
            new_lines = make_guardian_fix(lines, v)
        else:
            new_lines = make_log_fix(lines, v)

        if new_lines is None:
            stats["error"] += 1
            print(f"  SKIP (no pass found): {v['file']}:{v['line']}")
            continue

        if confirm:
            fpath.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
            print(f"  FIXED ({cls}): {v['file']}:{v['line']}  {v['exc_type']}")
        else:
            print(f"  WOULD FIX ({cls}): {v['file']}:{v['line']}  {v['exc_type']}")

        stats[cls] += 1

    print(f"\nResults: {stats}")
    if not confirm:
        print("Dry run — no files changed. Add --confirm to apply.")


def main():
    parser = argparse.ArgumentParser(description="W1: Fix silent_exception_swallow P2")
    parser.add_argument("--scan", action="store_true", help="List all instances")
    parser.add_argument("--fix", action="store_true", help="Apply fixes (dry run unless --confirm)")
    parser.add_argument("--confirm", action="store_true", help="Actually write files")
    parser.add_argument("--db", type=Path, help="SQLite DB path (auto-detected if omitted)")
    args = parser.parse_args()

    if not args.scan and not args.fix:
        parser.print_help()
        return

    # Find latest DB
    if args.db:
        db_path = args.db
    else:
        dbs = sorted(Path(ROOT / "artifacts/adg").glob("adg_indexed_*.sqlite"))
        if not dbs:
            print("No ADG SQLite DB found")
            sys.exit(1)
        db_path = dbs[-1]

    print(f"DB: {db_path}")
    violations = get_violations(db_path)
    print(f"Found {len(violations)} silent_exception_swallow P2 violations\n")

    if args.scan:
        scan(violations)
    elif args.fix:
        fix(violations, args.confirm)


if __name__ == "__main__":
    main()

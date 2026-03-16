#!/usr/bin/env python3
"""
Mass-fixer: narrow over-broad except Exception guards in test files.

Changes ONLY the specific `except` lines identified by TestSilentSkipDetector
as setting an availability flag to False.  Each targeted line is rewritten
as `except ImportError:` (preserving aliases and indentation).

Transformations applied:
    except Exception:            ->  except ImportError:
    except Exception as exc:     ->  except ImportError as exc:
    except BaseException:        ->  except ImportError:
    except BaseException as exc: ->  except ImportError as exc:
    except:                      ->  except ImportError:

Only lines at the exact line numbers flagged by the detector are modified —
no other `except` blocks are touched.

Usage:
    python ops_scripts/general/fix_test_silent_skips.py [--dry-run] [paths...]
    python ops_scripts/general/fix_test_silent_skips.py --dry-run tests/
    python ops_scripts/general/fix_test_silent_skips.py tests/

Exit codes:
    0 — All violations fixed (or dry-run complete)
    1 — Errors encountered
"""

from __future__ import annotations

import argparse
import io
import re
import sys
from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "fix_test_silent_skips")
_emit_applies_guardrail("p0", "fix_test_silent_skips", "p0_governance")
_emit_reads_policy_state("p0", "fix_test_silent_skips", "policy_binding")
_emit_snapshots_state("p0", "fix_test_silent_skips", "state_snapshot")
emit_replay_key("p0", "fix_test_silent_skips")
emit_determinism_digest("p0", "fix_test_silent_skips")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))  # guardian: allow-global-mutation -- CI bootstrap

from agentic_core.L5_safety.validators.test_skip_detector_validator import (
    TestSilentSkipDetector,
)

# Matches:  except Exception:
#           except Exception as exc:
#           except BaseException:
#           except BaseException as exc:
_BROAD_PATTERN = re.compile(
    r"^(\s*)except\s+(?:Exception|BaseException)(\s+as\s+\w+)?(\s*):(\s*)$"
)
# Matches:  except:
_BARE_PATTERN = re.compile(r"^(\s*)except(\s*):(\s*)$")


def _fix_line(line: str) -> str | None:
    """
    Return the fixed version of a line if it matches a broad except pattern.
    Returns None if the line does not match (should not be changed).
    """
    m = _BROAD_PATTERN.match(line.rstrip("\n"))
    if m:
        indent, alias, _ws, trailing = m.group(1), m.group(2) or "", m.group(3), m.group(4)
        eol = "\n" if line.endswith("\n") else ""
        return f"{indent}except ImportError{alias}:{trailing}{eol}"

    m = _BARE_PATTERN.match(line.rstrip("\n"))
    if m:
        indent, _ws, trailing = m.group(1), m.group(2), m.group(3)
        eol = "\n" if line.endswith("\n") else ""
        return f"{indent}except ImportError:{trailing}{eol}"

    return None


def _collect_test_files(roots: list[str]) -> list[Path]:
    files: list[Path] = []
    for root in roots:
        p = Path(root)
        if p.is_file() and p.suffix == ".py":
            files.append(p)
        elif p.is_dir():
            for f in p.rglob("*.py"):
                if "__pycache__" in f.parts:
                    continue
                if f.name.startswith("test_") or f.name.endswith("_test.py"):
                    files.append(f)
    return sorted(set(files))


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="fix_test_silent_skips",
        description="Narrow over-broad except guards in test files (except Exception → except ImportError)",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        metavar="PATH",
        default=["tests"],
        help="Directories or files to fix (default: tests/)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would change without writing any files",
    )
    args = parser.parse_args()

    detector = TestSilentSkipDetector()
    test_files = _collect_test_files(args.paths)

    if not test_files:
        print(f"No test files found under: {args.paths}")
        return 0

    # Collect all violations: {path: [line_number, ...]}
    violations_by_file: dict[Path, list[int]] = {}
    for f in test_files:
        result = detector.scan_file(f)
        active = [v.line_number for v in result.violations if not v.whitelisted]
        if active:
            violations_by_file[f] = active

    if not violations_by_file:
        print("No violations found — nothing to fix.")
        return 0

    files_fixed = 0
    lines_changed = 0
    errors = 0

    for file_path, violation_lines in sorted(violations_by_file.items()):
        try:
            original = file_path.read_text(encoding="utf-8")
        except Exception as exc:
            print(f"ERROR reading {file_path}: {exc}", file=sys.stderr)
            errors += 1
            continue

        lines = original.splitlines(keepends=True)
        changed_in_file = []

        for lineno in violation_lines:
            idx = lineno - 1  # 0-indexed
            if idx < 0 or idx >= len(lines):
                continue
            fixed = _fix_line(lines[idx])
            if fixed is None:
                print(
                    f"  WARNING: could not rewrite line {lineno} in {file_path.name}: "
                    f"{lines[idx].rstrip()!r}",
                    file=sys.stderr,
                )
                continue
            if fixed != lines[idx]:
                changed_in_file.append((lineno, lines[idx].rstrip(), fixed.rstrip()))
                lines[idx] = fixed

        if not changed_in_file:
            continue

        rel = file_path.relative_to(_REPO_ROOT) if file_path.is_absolute() else file_path
        if args.dry_run:
            for lineno, before, after in changed_in_file:
                print(f"  [DRY-RUN] {rel}:{lineno}")
                print(f"    - {before}")
                print(f"    + {after}")
        else:
            new_content = "".join(lines)
            try:
                file_path.write_text(new_content, encoding="utf-8")
            except Exception as exc:
                print(f"ERROR writing {file_path}: {exc}", file=sys.stderr)
                errors += 1
                continue
            for lineno, before, after in changed_in_file:
                print(f"  FIXED {rel}:{lineno}  {before!r} -> {after!r}")

        files_fixed += 1
        lines_changed += len(changed_in_file)

    action = "Would fix" if args.dry_run else "Fixed"
    print(f"\n{action} {lines_changed} line(s) across {files_fixed} file(s).")
    if errors:
        print(f"{errors} error(s) encountered.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""
ADG anti-pattern fixer — Accelerator #1.

Detects and fixes non-canonical guardian comment format violations in Python
source files. Eliminates the need for repeated one-liner "fix: correct guardian
comment format" commits by batch-fixing all violations at once.

The canonical guardian comment format is exactly:
    # guardian: allow-<type> -- <justification>

Where <type> is lowercase-kebab (e.g. magic-config, silent-swallower, global-mutation).

Non-canonical forms that are auto-corrected:
    # guardian: allow-magic-config -- reason          (missing colon)
    # guardian: allow-magic-config -- reason           (colon separator instead of --)
    # guardian: allow-magic-config -- reason         (wrong case)
    # guardian: allow-magic-config -- reason         (underscore type → kebab)
    # guardian: allow-magic-config -- reason           (camelCase type → kebab)
    # guardian: allow-magic-config -- reason          (missing space after --)
    # guardian: allow-magic-config -- (empty justification)  → warned, not fixed

Fail-closed on filesystem errors. No ADG dependency — runs on raw source.

Usage (CLI):
    python tools/adg/adg_antipattern_fixer.py <file> [<file> ...]
    python tools/adg/adg_antipattern_fixer.py --from-diff
    python tools/adg/adg_antipattern_fixer.py --check-only   # report without modifying
    python tools/adg/adg_antipattern_fixer.py --staged
"""

from __future__ import annotations

import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# ---------------------------------------------------------------------------
# Canonical type registry — maps all known normalised forms to canonical kebab
# ---------------------------------------------------------------------------

_CANONICAL_TYPES: dict[str, str] = {
    # magic-config
    "magic-config": "magic-config",
    "magic_config": "magic-config",
    "magicconfig": "magic-config",
    # silent-swallower
    "silent-swallower": "silent-swallower",
    "silent_swallower": "silent-swallower",
    "silentswallower": "silent-swallower",
    # global-mutation
    "global-mutation": "global-mutation",
    "global_mutation": "global-mutation",
    "globalmutation": "global-mutation",
    # bare-except
    "bare-except": "bare-except",
    "bare_except": "bare-except",
    "bareexcept": "bare-except",
    # broad-exception-catch
    "broad-exception-catch": "broad-exception-catch",
    "broad_exception_catch": "broad-exception-catch",
    "broadexceptioncatch": "broad-exception-catch",
    # log-and-swallow
    "log-and-swallow": "log-and-swallow",
    "log_and_swallow": "log-and-swallow",
    "logandswallow": "log-and-swallow",
    # return-none-swallow
    "return-none-swallow": "return-none-swallow",
    "return_none_swallow": "return-none-swallow",
    "returnnoneswallow": "return-none-swallow",
    # os-path — common in legacy code
    "os-path": "os-path",
    "os_path": "os-path",
    # string-path-concat
    "string-path-concat": "string-path-concat",
    "string_path_concat": "string-path-concat",
    # silent-degradation (umbrella)
    "silent-degradation": "silent-degradation",
    "silent_degradation": "silent-degradation",
    "silentdegradation": "silent-degradation",
    # availability-guard-skip (sub-pattern 1)
    "availability-guard-skip": "availability-guard-skip",
    "availability_guard_skip": "availability-guard-skip",
    "availabilityguardskip": "availability-guard-skip",
    # silent-success-on-noop (sub-pattern 2)
    "silent-success-on-noop": "silent-success-on-noop",
    "silent_success_on_noop": "silent-success-on-noop",
    "silentsuccessonnoop": "silent-success-on-noop",
    # phantom-module-import (sub-pattern 3)
    "phantom-module-import": "phantom-module-import",
    "phantom_module_import": "phantom-module-import",
    "phantommoduleimport": "phantom-module-import",
    # except-import-pass (sub-pattern 4)
    "except-import-pass": "except-import-pass",
    "except_import_pass": "except-import-pass",
    "exceptimportpass": "except-import-pass",
    # log-and-return-mock (sub-pattern 5)
    "log-and-return-mock": "log-and-return-mock",
    "log_and_return_mock": "log-and-return-mock",
    "logandreturnmock": "log-and-return-mock",
    # skip-string-return (sub-pattern 6)
    "skip-string-return": "skip-string-return",
    "skip_string_return": "skip-string-return",
    "skipstringreturn": "skip-string-return",
}

# Broad detection: any line that looks like a guardian comment (even malformed)
_GUARDIAN_DETECT_RE = re.compile(
    r"""
    ^(\s*\#\s*)          # indent + hash prefix (group 1)
    [Gg]uardian          # keyword (case-insensitive first letter)
    \s*:?\s*             # optional colon
    (allow[-_a-zA-Z0-9]*)  # allow-<type> chunk (group 2)
    \s*(?:--|:)\s*       # separator: -- or :
    (.*)                 # justification (group 3)
    $
    """,
    re.VERBOSE,
)

# Pattern that matches ALREADY CANONICAL lines (no change needed)
_CANONICAL_RE = re.compile(r"^\s*#\s*guardian:\s+allow-[a-z][a-z0-9-]+\s+--\s+\S.*$")


@dataclass
class FixChange:
    line_no: int  # 1-indexed
    old_line: str
    new_line: str


@dataclass
class FixResult:
    file_path: str
    fixed_count: int
    skipped_empty_justification: int
    changes: list[FixChange] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def had_violations(self) -> bool:
        return self.fixed_count > 0 or self.skipped_empty_justification > 0


def _camel_to_kebab(name: str) -> str:
    """Convert camelCase or PascalCase string to lowercase-kebab-case."""
    s = re.sub(r"([A-Z])", r"-\1", name).lower()
    s = s.replace("_", "-")
    s = re.sub(r"-+", "-", s)
    return s.strip("-")


def _normalize_type(raw: str) -> str:
    """Normalize a raw allow-<type> token to canonical kebab form.

    1. Strip the leading 'allow' prefix if present.
    2. camelCase → kebab-case.
    3. underscore → hyphen.
    4. Lookup in known canonical types; return canonical form if found.
    5. Otherwise return the normalized best-effort kebab form.
    """
    lowered = raw.lower().strip("-_ ")

    # Strip leading 'allow' prefix (handle allow-, allow_, allow)
    if lowered.startswith("allow-"):
        inner = lowered[len("allow-") :]
    elif lowered.startswith("allow_"):
        inner = lowered[len("allow_") :]
    elif lowered.startswith("allow"):
        inner_raw = raw[len("allow") :].lstrip("-_ ")
        inner = _camel_to_kebab(inner_raw) if inner_raw else ""
    else:
        inner = _camel_to_kebab(lowered)

    # Normalize inner to kebab
    inner = inner.replace("_", "-")
    inner = re.sub(r"-+", "-", inner).strip("-")

    # Lookup canonical form
    if inner in _CANONICAL_TYPES:
        return f"allow-{_CANONICAL_TYPES[inner]}"

    # Return best-effort
    return f"allow-{inner}" if inner else "allow-unknown"


def _is_canonical(line: str) -> bool:
    """Return True if the line is already in canonical guardian comment format."""
    return bool(_CANONICAL_RE.match(line))


def _fix_line(line: str) -> tuple[str | None, str | None]:
    """Attempt to fix a guardian comment line.

    Returns:
        (fixed_line, warning) — fixed_line is None if no change needed or cannot fix.
        warning is set if the line was skipped due to empty justification.
    """
    if _is_canonical(line):
        return None, None

    m = _GUARDIAN_DETECT_RE.match(line)
    if not m:
        return None, None

    indent_hash = m.group(1)  # e.g. "    # "
    raw_type = m.group(2).strip()  # e.g. "allow_magic_config"
    justification = m.group(3).strip()

    if not justification:
        return None, f"guardian comment at has empty justification — skipped: {line.rstrip()}"

    canonical_type = _normalize_type(raw_type)
    # Preserve original indentation; normalise to single space after #
    indent = re.match(r"^(\s*)", line).group(1)
    fixed = f"{indent}# guardian: {canonical_type} -- {justification}"

    if fixed == line.rstrip():
        return None, None

    return fixed, None


class GuardianCommentFixer:
    """Detect and fix non-canonical guardian comment format violations.

    Operates on raw Python source strings. No ADG dependency.
    """

    def scan_violations(self, source: str) -> list[tuple[int, str]]:
        """Return (1-indexed line_no, line) for every non-canonical guardian comment.

        Lines that are already canonical are NOT included.
        Lines with empty justifications ARE included (they need manual attention).
        """
        violations: list[tuple[int, str]] = []
        for i, line in enumerate(source.splitlines(), start=1):
            if _GUARDIAN_DETECT_RE.match(line) and not _is_canonical(line):
                violations.append((i, line))
        return violations

    def fix_source(self, source: str) -> tuple[str, list[FixChange], list[str]]:
        """Fix all fixable non-canonical guardian comments in source.

        Args:
            source: Python source code as string.

        Returns:
            (fixed_source, changes, warnings):
            - fixed_source: the corrected source string
            - changes: list of FixChange (line_no, old_line, new_line)
            - warnings: list of warning strings for skipped lines
        """
        lines = source.splitlines(keepends=True)
        changes: list[FixChange] = []
        warnings: list[str] = []

        for i, line in enumerate(lines):
            fixed, warn = _fix_line(line.rstrip("\n").rstrip("\r"))
            if warn:
                warnings.append(f"Line {i + 1}: {warn}")
            if fixed is not None:
                # Preserve original line ending
                ending = ""
                if line.endswith("\r\n"):
                    ending = "\r\n"
                elif line.endswith("\n"):
                    ending = "\n"
                elif line.endswith("\r"):
                    ending = "\r"
                changes.append(
                    FixChange(
                        line_no=i + 1,
                        old_line=line.rstrip("\r\n"),
                        new_line=fixed,
                    ),
                )
                lines[i] = fixed + ending

        return "".join(lines), changes, warnings

    def fix_file(self, file_path: Path, check_only: bool = False) -> FixResult:
        """Fix all non-canonical guardian comments in a file.

        Args:
            file_path: Path to the Python file.
            check_only: If True, report violations without modifying the file.

        Returns:
            FixResult with fixed_count, changes, and warnings.

        Raises:
            OSError: if file cannot be read or written.
        """
        source = file_path.read_text(encoding="utf-8")
        fixed_source, changes, warnings = self.fix_source(source)

        skipped = sum(1 for w in warnings if "empty justification" in w)

        if changes and not check_only:
            file_path.write_text(fixed_source, encoding="utf-8")

        return FixResult(
            file_path=str(file_path),
            fixed_count=len(changes),
            skipped_empty_justification=skipped,
            changes=changes,
            warnings=warnings,
        )


def _git_changed_files(staged: bool = False, repo_root: Path | None = None) -> list[str]:
    """Return changed Python file paths from git diff."""
    root = repo_root or ROOT
    cmd = ["git", "diff", "--name-only", "--diff-filter=ACMRT"]
    if staged:
        cmd.append("--cached")
    else:
        cmd.append("HEAD")
    try:
        result = subprocess.run(
            cmd,
            cwd=str(root),
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(f"git diff timed out: {exc}") from exc
    if result.returncode != 0:
        raise RuntimeError(f"git diff failed: {result.stderr.strip()}")
    return [f for f in result.stdout.splitlines() if f.endswith(".py")]


def _cli() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        prog="adg_antipattern_fixer",
        description=(
            "Detect and fix non-canonical guardian comment format violations. "
            "Canonical: # guardian: allow-<type> -- <justification>"
        ),
    )
    parser.add_argument(
        "files",
        nargs="*",
        metavar="FILE",
        help="Python files to fix",
    )
    parser.add_argument(
        "--from-diff",
        action="store_true",
        help="Use 'git diff HEAD' to determine changed files",
    )
    parser.add_argument(
        "--staged",
        action="store_true",
        help="Use 'git diff --cached' (staged files only) — implies --from-diff",
    )
    parser.add_argument(
        "--report",
        "-r",
        action="store_true",
        help="Report-only mode (no modifications)",
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help=argparse.SUPPRESS,  # Deprecated, use --report
    )
    args = parser.parse_args()

    use_diff = args.from_diff or args.staged
    if not args.files and not use_diff:
        parser.error("Provide FILE arguments or --from-diff / --staged")

    # Default to execute mode, report mode only if --report flag is set
    check_only = args.report

    fixer = GuardianCommentFixer()

    file_list: list[str] = list(args.files)
    if use_diff:
        try:
            file_list.extend(_git_changed_files(staged=args.staged))
        except RuntimeError as exc:  # guardian: Runtime errors should be prevented with proper validation
            print(f"ERROR: {exc}", file=sys.stderr)
            sys.exit(1)

    total_fixed = 0
    total_warnings = 0
    for f in file_list:
        p = Path(f)
        if not p.exists():
            print(f"SKIP (not found): {f}")
            continue
        try:
            result = fixer.fix_file(p, check_only=check_only)
        except OSError as exc:  # guardian: Add error context logging
            print(f"ERROR reading {f}: {exc}", file=sys.stderr)
            continue

        if result.had_violations:
            action = "WOULD FIX" if check_only else "FIXED"
            if result.fixed_count:
                print(f"{action}: {f} — {result.fixed_count} guardian comment(s) corrected")
                for ch in result.changes:
                    print(f"  L{ch.line_no}: {ch.old_line!r}")
                    print(f"        → {ch.new_line!r}")
            for w in result.warnings:
                print(f"  WARNING: {w}")
            total_fixed += result.fixed_count
            total_warnings += len(result.warnings)
        else:
            print(f"OK: {f}")

    if total_fixed or total_warnings:
        action = "would be fixed" if check_only else "fixed"
        print(f"\nTotal: {total_fixed} violation(s) {action}, {total_warnings} warning(s)")
        if check_only:
            sys.exit(1)
    else:
        print("\nAll guardian comments are canonical.")


if __name__ == "__main__":
    _cli()

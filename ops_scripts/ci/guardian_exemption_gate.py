"""
Guardian Exemption Gate — Exemption Quality Ratchet

Closes the scanner blind spot: the burndown gate tracks *unwhitelisted* violations,
but once a guardian comment is added the violation disappears from its view.
This gate tracks the exemptions themselves.

Two rules enforced on every commit
────────────────────────────────────────
Rule 1 — JUSTIFICATION REQUIRED (staged files only — zero-tolerance for new additions)
    Any `# guardian: allow-*` comment added or modified in a STAGED production
    file MUST have a `-- <justification>` suffix.  Empty or generic justifications
    are blocked.  Existing unjustified exemptions in untouched files are NOT blocked
    (they appear in the ratchet and must be fixed during normal cleanup).

Rule 2 — COUNT RATCHET (all production files)
    Tracks {rel_path: {exemption_type: count}} in guardian_exemption_budget.json.
    Any new exemption that raises the count above the ratchet ceiling is blocked.
    When counts fall the ratchet tightens automatically.

Scope
─────
Production directories only (agentic_core/, apps_*/,  system_learning/).
tools/, tests/, ops_scripts/ are excluded — utility scripts have looser rules.

Exit codes
──────────
  0  — all rules pass (commit allowed)
  1  — rule violation (commit blocked)

Environment overrides
─────────────────────
  ADG_EXEMPTION_BYPASS=1   — skip gate entirely (emergency; logged to stderr)
  ADG_EXEMPTION_DRY_RUN=1  — report without updating ratchet
  ADG_EXEMPTION_INIT=1     — (re)initialise ratchet from current state, exit 0
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
from collections import defaultdict
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

_emit_records_execution_trace("p0", "evidence", "guardian_exemption_gate")
_emit_applies_guardrail("p0", "guardian_exemption_gate", "p0_governance")
_emit_reads_policy_state("p0", "guardian_exemption_gate", "policy_binding")
_emit_snapshots_state("p0", "guardian_exemption_gate", "state_snapshot")
emit_replay_key("p0", "guardian_exemption_gate")
emit_determinism_digest("p0", "guardian_exemption_gate")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

# ---------------------------------------------------------------------------
# Bootstrap — works as pre-commit hook or direct invocation from repo root.
# ---------------------------------------------------------------------------
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(
        0, str(_REPO_ROOT)
    )  # guardian: allow-global-mutation -- CI bootstrap requires sys.path setup before package imports

from agentic_core.L0_routing.config.path_constants import (
    OPS_SCRIPTS_DIR,
    get_validated_project_root,
)

PROJECT_ROOT = get_validated_project_root()

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

RATCHET_FILE = PROJECT_ROOT / OPS_SCRIPTS_DIR / "hooks" / "guardian_exemption_budget.json"

# Production directories to scan — tools/, tests/, ops_scripts/ are excluded.
PRODUCTION_DIRS = [
    "agentic_core",
    "apps_lic",
    "apps_rg",
    "apps_shared",
    "apps_exec",
    "apps_eval",
    "apps_rfp",
    "apps_research",
    "system_learning",
]

EXCLUDE_DIRS = {
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    "env",
    ".nox",
    "archives",
    ".backup",
    ".test_artifacts",
    ".pytest_cache",
}

EXCLUDE_FILE_PATTERNS = ["test_*.py", "*_test.py", "conftest.py"]

# Generic justification tokens that provide no real signal.
# A justification consisting ONLY of these words (after stripping punctuation)
# is treated as empty.
_GENERIC_TOKENS = frozenset(
    {
        "needed",
        "required",
        "necessary",
        "legacy",
        "fixme",
        "todo",
        "temporary",
        "temp",
        "wip",
        "ignore",
        "skip",
        "bypass",
        "ok",
        "fine",
        "allowed",
        "allow",
        "exempt",
        "exception",
        "placeholder",
        "stub",
        "hack",
        "workaround",
    }
)

# Matches canonical guardian comment: # guardian: allow-<type> -- <justification>
_CANONICAL_RE = re.compile(r"^\s*#\s*guardian:\s+allow-([a-z][a-z0-9-]+)\s+--\s+(.+)$")

# Matches ANY guardian comment (including malformed) to detect missing justification.
_ANY_GUARDIAN_RE = re.compile(
    r"^\s*#\s*[Gg]uardian[:\s].*allow[-_]",
)

# Canonical form with NO justification (the exact bad pattern).
_NO_JUSTIFICATION_RE = re.compile(r"^\s*#\s*guardian:\s+allow-[a-z][a-z0-9-]+\s*$")

Budget = dict[str, dict[str, int]]  # {rel_path: {exemption_type: count}}


# ---------------------------------------------------------------------------
# Justification quality check
# ---------------------------------------------------------------------------


def _is_generic_justification(justification: str) -> bool:
    """Return True if the justification is empty or contains only generic tokens."""
    cleaned = re.sub(r"[^a-z\s]", "", justification.lower())
    tokens = set(cleaned.split())
    if not tokens:
        return True
    # All tokens must be non-generic for the justification to pass.
    return tokens.issubset(_GENERIC_TOKENS)


# ---------------------------------------------------------------------------
# File scanning
# ---------------------------------------------------------------------------


def _collect_production_files() -> list[Path]:
    files = []
    for prod_dir in PRODUCTION_DIRS:
        target = PROJECT_ROOT / prod_dir
        if not target.exists():
            continue
        for f in sorted(target.rglob("*.py")):
            parts = set(f.relative_to(PROJECT_ROOT).parts)
            if parts & EXCLUDE_DIRS:
                continue
            if any(f.match(pat) for pat in EXCLUDE_FILE_PATTERNS):
                continue
            files.append(f)
    return files


def _rel(fp: Path) -> str:
    return fp.relative_to(PROJECT_ROOT).as_posix()


def _scan_file(file_path: Path) -> list[tuple[int, str, str | None, str | None]]:
    """
    Scan a single file for guardian exemption comments.

    Returns list of (line_no, raw_line, exemption_type, justification).
    - exemption_type is None if the comment is malformed/unparseable.
    - justification is None if absent.
    """
    results = []
    try:
        lines = file_path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return results

    for i, line in enumerate(lines, start=1):
        if not _ANY_GUARDIAN_RE.search(line):
            continue

        m = _CANONICAL_RE.match(line)
        if m:
            results.append((i, line, m.group(1), m.group(2).strip()))
            continue

        # Malformed or missing justification — still record it.
        if _NO_JUSTIFICATION_RE.match(line):
            # Has type but no justification at all.
            type_match = re.search(r"allow-([a-z][a-z0-9-]+)", line)
            etype = type_match.group(1) if type_match else "unknown"
            results.append((i, line, etype, None))
        else:
            # Some other malformed variant.
            type_match = re.search(r"allow[-_]([a-z][a-z0-9_-]+)", line, re.IGNORECASE)
            etype = type_match.group(1).lower().replace("_", "-") if type_match else "unknown"
            results.append((i, line, etype, None))

    return results


# ---------------------------------------------------------------------------
# Ratchet I/O
# ---------------------------------------------------------------------------


def _load_ratchet() -> Budget:
    if not RATCHET_FILE.exists():
        return {}
    try:
        return json.loads(RATCHET_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _write_ratchet(ratchet: Budget) -> None:
    RATCHET_FILE.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(ratchet, indent=2, sort_keys=True) + "\n"
    fd, tmp = tempfile.mkstemp(
        dir=str(RATCHET_FILE.parent),
        prefix=".exemption_ratchet_",
        suffix=".tmp",
    )
    try:
        os.write(fd, content.encode("utf-8"))
        os.close(fd)
        if sys.platform == "win32" and RATCHET_FILE.exists():
            RATCHET_FILE.unlink()
        Path(tmp).replace(RATCHET_FILE)
    except BaseException:
        try:
            os.close(fd)
        except OSError:
            pass
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def _ratchet_total(ratchet: Budget) -> int:
    return sum(c for cats in ratchet.values() for c in cats.values())


# ---------------------------------------------------------------------------
# Core ratchet logic
# ---------------------------------------------------------------------------


def _scan_to_counts(scan_results: dict[str, list]) -> Budget:
    """Convert per-file scan results → {rel_path: {exemption_type: count}}."""
    counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for rel_path, hits in scan_results.items():
        for _lineno, _raw, etype, _just in hits:
            if etype:
                counts[rel_path][etype] += 1
    return {f: dict(cats) for f, cats in counts.items()}


def _check_ratchet(
    ratchet: Budget,
    current: Budget,
) -> list[tuple[str, str, int, int]]:
    """
    Return (rel_path, etype, allowed, actual) for every ratchet violation.

    Rule 2: any exemption_type count that exceeds its ratchet ceiling is blocked.
    New file+type pairs (allowed=0, actual>0) are also blocked.
    """
    out = []
    for rel_path, types in current.items():
        ratchet_file = ratchet.get(rel_path, {})
        for etype, actual in types.items():
            allowed = ratchet_file.get(etype, 0)
            if actual > allowed:
                out.append((rel_path, etype, allowed, actual))
    return sorted(out)


def _tighten_ratchet(ratchet: Budget, current: Budget) -> tuple[Budget, int]:
    """Tighten ratchet to current counts.  Only shrinks, never grows."""
    new_ratchet: Budget = {}
    improved = 0
    for rel_path, types in ratchet.items():
        current_types = current.get(rel_path, {})
        new_types: dict[str, int] = {}
        for etype, ceiling in types.items():
            actual = current_types.get(etype, 0)
            new_val = min(ceiling, actual)
            if new_val > 0:
                new_types[etype] = new_val
            if actual < ceiling:
                improved += 1
        if new_types:
            new_ratchet[rel_path] = new_types
    return new_ratchet, improved


# ---------------------------------------------------------------------------
# Staged file detection
# ---------------------------------------------------------------------------


def _get_staged_production_files() -> set[str]:
    """
    Return a set of repo-relative POSIX paths for staged Python files that
    are within production directories.  Returns an empty set if git is
    unavailable or no files are staged.
    """
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMRT"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        if result.returncode != 0:
            return set()
        staged = set()
        for line in result.stdout.splitlines():
            line = line.strip()
            if not line.endswith(".py"):
                continue
            # Must be under a production directory.
            first_part = line.split("/")[0]
            if first_part in set(PRODUCTION_DIRS):
                staged.add(line)
        return staged
    except Exception:  # noqa: BLE001
        return set()


def _get_added_lines_per_file() -> dict[str, set[int]]:
    """
    Parse ``git diff --cached -U0`` to get the set of *added* line numbers
    per file.  Only lines starting with ``+`` (excluding the ``+++`` header)
    are considered added.  Returns {posix_rel_path: {line_numbers}}.
    """
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "-U0", "--no-color"],
            capture_output=True,
            cwd=str(PROJECT_ROOT),
        )
        if result.returncode != 0:
            return {}
    except Exception:  # noqa: BLE001
        return {}

    added: dict[str, set[int]] = defaultdict(set)
    current_file: str | None = None
    stdout_text = result.stdout.decode("utf-8", errors="replace")
    for raw_line in stdout_text.splitlines():
        if raw_line.startswith("+++ b/"):
            current_file = raw_line[6:]
            continue
        if raw_line.startswith("@@ ") and current_file:
            # Parse hunk header: @@ -old,count +new,count @@
            hunk = raw_line.split("@@")[1].strip()
            plus_part = hunk.split("+")[1].split()[0]
            if "," in plus_part:
                start, count = plus_part.split(",")
                start, count = int(start), int(count)
            else:
                start, count = int(plus_part), 1
            for ln in range(start, start + count):
                added[current_file].add(ln)
    return dict(added)


# ---------------------------------------------------------------------------
# Main gate logic
# ---------------------------------------------------------------------------


def main() -> int:  # noqa: C901
    bypass = os.getenv("ADG_EXEMPTION_BYPASS", "").strip() == "1"
    dry_run = os.getenv("ADG_EXEMPTION_DRY_RUN", "").strip() == "1"
    init_mode = os.getenv("ADG_EXEMPTION_INIT", "").strip() == "1"

    if bypass:
        print("[guardian-exemption-gate] BYPASS active — skipping gate", file=sys.stderr)
        return 0

    files = _collect_production_files()
    if not files:
        print("[guardian-exemption-gate] No production files found — nothing to check.")
        return 0

    # Scan all production files.
    scan_results: dict[str, list] = {}
    for f in files:
        hits = _scan_file(f)
        if hits:
            scan_results[_rel(f)] = hits

    # ---------------------------------------------------------------------------
    # Init mode — write ratchet from current state and exit.
    # ---------------------------------------------------------------------------
    ratchet = _load_ratchet()
    current_counts = _scan_to_counts(scan_results)
    total_exemptions = _ratchet_total(current_counts)

    if init_mode:
        _write_ratchet(current_counts)
        print(
            f"[guardian-exemption-gate] INIT: ratchet written — "
            f"{len(current_counts)} files, {total_exemptions} total exemptions"
        )
        return 0

    # ---------------------------------------------------------------------------
    # Rule 1 — JUSTIFICATION REQUIRED (staged files only)
    # Applies only to files that are staged for this commit — prevents new
    # unjustified exemptions from being added without blocking legacy ones.
    # ---------------------------------------------------------------------------
    staged_files = _get_staged_production_files()
    added_lines = _get_added_lines_per_file()
    rule1_failures: list[tuple[str, int, str, str]] = []

    for rel_path, hits in scan_results.items():
        if rel_path not in staged_files:
            continue  # Only check files being committed right now.
        # Convert POSIX rel_path to match git diff output (already POSIX).
        file_added = added_lines.get(rel_path, set())
        # Also try backslash variant for Windows compatibility.
        if not file_added:
            file_added = added_lines.get(rel_path.replace("/", "\\"), set())
        for lineno, raw_line, etype, justification in hits:
            # Rule 1 only applies to ADDED lines — skip pre-existing exemptions.
            if lineno not in file_added:
                continue
            if justification is None:
                rule1_failures.append((rel_path, lineno, raw_line.strip(), "missing -- <justification>"))
            elif _is_generic_justification(justification):
                rule1_failures.append(
                    (rel_path, lineno, raw_line.strip(), f"generic justification: '{justification}'")
                )

    # ---------------------------------------------------------------------------
    # Rule 2 — COUNT RATCHET (all production files)
    # ---------------------------------------------------------------------------
    ratchet_violations = _check_ratchet(ratchet, current_counts)

    # ---------------------------------------------------------------------------
    # Reporting
    # ---------------------------------------------------------------------------
    passed = not rule1_failures and not ratchet_violations

    staged_label = f"{len(staged_files)} staged" if staged_files else "no staged production"
    print(
        f"[guardian-exemption-gate] Scanned {len(files)} production files ({staged_label} files checked for Rule 1)"
    )
    print(
        f"[guardian-exemption-gate] Total guardian exemptions: {total_exemptions} (ratchet ceiling: {_ratchet_total(ratchet)})"
    )

    if rule1_failures:
        print(f"\n{'=' * 70}")
        print(f"RULE 1 VIOLATION — {len(rule1_failures)} new exemption(s) missing real justification")
        print(f"{'=' * 70}")
        print("Staged files may not add `# guardian: allow-*` without a specific `-- <justification>`.")
        print("Generic words (needed, required, temporary, legacy) are not accepted.\n")
        for rel_path, lineno, raw, reason in rule1_failures:
            print(f"  {rel_path}:{lineno}")
            print(f"    {raw}")
            print(f"    >>  {reason}")
            print()
        print("Fix: add a real justification, e.g.:")
        print(
            "  # guardian: allow-magic-config -- DEFAULT_TIMEOUT is deploy-environment-specific, owner: infra"
        )
        print(
            "  # guardian: allow-silent-swallow -- MCP write-back is non-critical telemetry; failure logged above"
        )
        print()

    if ratchet_violations:
        print(f"\n{'=' * 70}")
        print(f"RULE 2 VIOLATION — {len(ratchet_violations)} ratchet ceiling(s) exceeded")
        print(f"{'=' * 70}")
        print("Exemption counts in production code may only decrease.\n")
        for rel_path, etype, allowed, actual in ratchet_violations:
            delta = actual - allowed
            print(f"  {rel_path}  [{etype}]  ceiling={allowed}  actual={actual}  (+{delta} new)")
        print()
        print("To legitimately add a new exemption:")
        print("  1. Get HITL approval via ask_user_question in Cascade")
        print("  2. Add `# guardian: allow-<type> -- <specific justification>`")
        print("  3. Re-init: ADG_EXEMPTION_INIT=1 python ops_scripts/ci/guardian_exemption_gate.py")
        print()

    if passed:
        new_ratchet, improved = _tighten_ratchet(ratchet, current_counts)
        if improved and not dry_run:
            _write_ratchet(new_ratchet)
            print(f"[guardian-exemption-gate] PASS -- ratchet tightened ({improved} slot(s) improved)")
        else:
            print("[guardian-exemption-gate] PASS -- all exemptions justified")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())

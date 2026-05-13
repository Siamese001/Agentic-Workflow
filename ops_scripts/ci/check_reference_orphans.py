"""CI gate: fail if predecessor/orphan doctrine files leak into the SSOT tree.

Rationale: `docs/reference/` is the canonical doctrine SSOT (Tier A — REQ_ID
validated contracts). Predecessor files (from the REQ-ID rewrite) and
hand-authored `_exec` drafts re-appear via bulk-WIP sync commits and
external-bundler MANIFEST re-drops (see RCA, 2026-04-27). The tier-split
plan (`a3c9f1`) carved hand-authored content into two sentinel folders:
  - `docs/reference/_notes/`    Tier B — exec sketches, gap reports
  - `docs/reference/_primers/`  Tier C — neutral technical primers
  - `docs/reference/_archive/`  predecessors / superseded files

This gate enforces three invariants that survive bulk re-adds:

  1. No `*.pre-reqid-rewrite.bak` outside `_archive/`
  2. No `* exec.md` (with embedded space) anywhere except the explicit
     keep-list `_ALLOWED_EXEC_FILES`
  3. No `*.md` at the SSOT root except the canonical allowlist
     `_ALLOWED_ROOT_MD` (Tier A traceability + README)

Sentinel folders (`_notes/`, `_primers/`, `_archive/`) are exempt from
rules 1 and 2 — they hold user-curated, non-SSOT content.

Exit codes:
  0 — clean
  1 — violations detected (list printed to stderr)
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
REF = REPO / "docs" / "reference"

# Sentinel folders carve non-SSOT content out of the canonical tree.
# Anything inside is exempt from orphan-pattern checks (rules 1 and 2).
_SENTINEL_DIRS: frozenset[str] = frozenset({"_archive", "_notes", "_primers"})

# Files intentionally kept outside sentinels despite matching a flagged pattern.
# Each entry is a path relative to REF.
_ALLOWED_EXEC_FILES: frozenset[str] = frozenset(set())

# Tier A canonical files allowed directly at `docs/reference/*.md`.
# Anything else at root must move into _notes/ or _primers/.
_ALLOWED_ROOT_MD: frozenset[str] = frozenset(
    {
        "00X_Requirements_Traceability_and_No_Loss_Map.md",
        "README.md",
        # Pre-existing domain contract discovery/acceptance/status docs (2026-05-12 adg-snapshot-regen)
        "apps_domain_contract_acceptance.md",
        "apps_domain_contract_discovery.md",
        "apps_domain_contract_implementation_status.md",
        "archive_lifecycle_policy.md",
    }
)

_BAK_GLOB = "**/*.pre-reqid-rewrite.bak"
_EXEC_GLOB = "**/* exec.md"


def _is_in_sentinel(path: Path) -> bool:
    try:
        rel = path.relative_to(REF)
    except ValueError:
        return False
    return rel.parts[0] in _SENTINEL_DIRS if rel.parts else False


def _find_violations() -> list[tuple[str, Path]]:
    violations: list[tuple[str, Path]] = []
    if not REF.is_dir():
        return violations

    # Rule 1: no `*.pre-reqid-rewrite.bak` outside sentinels.
    for p in REF.glob(_BAK_GLOB):
        if p.is_file() and not _is_in_sentinel(p):
            violations.append(("pre-reqid-rewrite.bak", p))

    # Rule 2: no `* exec.md` outside sentinels (allowlisted exceptions exempt).
    for p in REF.glob(_EXEC_GLOB):
        if not p.is_file() or _is_in_sentinel(p):
            continue
        rel = p.relative_to(REF).as_posix()
        if rel in _ALLOWED_EXEC_FILES:
            continue
        violations.append(("'<name> exec.md' orphan", p))

    # Rule 3: root-level `.md` allowlist (Tier A discipline).
    for p in REF.glob("*.md"):
        if not p.is_file():
            continue
        if p.name in _ALLOWED_ROOT_MD:
            continue
        violations.append(("non-Tier-A .md at SSOT root", p))

    return violations


def main() -> int:
    violations = _find_violations()
    if not violations:
        print("check_reference_orphans: OK (no orphan predecessor files outside _archive/)")
        return 0

    print(
        f"check_reference_orphans: FAIL — {len(violations)} violation(s) "
        f"in {REF.relative_to(REPO).as_posix()}/",
        file=sys.stderr,
    )
    for kind, path in violations:
        rel = path.relative_to(REPO).as_posix()
        print(f"  [{kind}] {rel}", file=sys.stderr)
    print(
        "\nFix:"
        "\n  - `*.pre-reqid-rewrite.bak`  -> `git mv` to `docs/reference/_archive/`"
        "\n  - `* exec.md` orphan        -> `git mv` to `_notes/` or `_archive/`,"
        " or add to `_ALLOWED_EXEC_FILES` if intentional"
        "\n  - non-Tier-A `.md` at root  -> `git mv` to `_notes/` (sketches/reports)"
        " or `_primers/` (technical primers), or add to `_ALLOWED_ROOT_MD`"
        " if it is genuinely Tier A SSOT.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())

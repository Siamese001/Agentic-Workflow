"""CI gate: fail if predecessor/orphan doctrine files leak outside `_archive/`.

Rationale: `docs/reference/` is the canonical doctrine SSOT. Predecessor files
(from the REQ-ID rewrite) and hand-authored `_exec` drafts have a pattern of
re-appearing via bulk-WIP sync commits and external-bundler MANIFEST re-drops
(see RCA, 2026-04-27). This gate is the only mechanism that survives those
re-adds: it fails the build if any file matching the orphan patterns exists
outside `docs/reference/_archive/`.

Patterns flagged:
  - `*.pre-reqid-rewrite.bak`        (REQ-ID rewrite predecessors)
  - `* exec.md`                      (hand-authored draft with embedded space)

Allowlist:
  - Anything under `docs/reference/_archive/`
  - Explicit keep-list in `_ALLOWED_EXEC_FILES` (e.g. doctrine-level
    `agentic_system_process_map_exec.md` intentionally kept at the root).

Exit codes:
  0 — clean
  1 — violations detected (list printed to stderr)
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
REF = REPO / "docs" / "reference"
ARCHIVE = REF / "_archive"

# Files intentionally kept outside _archive/ despite matching a flagged pattern.
# Each entry is a path relative to REF.
_ALLOWED_EXEC_FILES: frozenset[str] = frozenset(
    {
        # Intentionally kept at doctrine root (user decision, 2026-04-27).
        "agentic_system_process_map_exec.md",
        # Sibling to v1/v2/v3/v4 canonicals in Python/. Out of the numbered
        # layer-folder cleanup scope; revisit separately.
        "Python/Error & Exception Handling exec.md",
    }
)

_BAK_GLOB = "**/*.pre-reqid-rewrite.bak"
_EXEC_GLOB = "**/* exec.md"


def _is_under_archive(path: Path) -> bool:
    try:
        path.relative_to(ARCHIVE)
        return True
    except ValueError:
        return False


def _find_violations() -> list[tuple[str, Path]]:
    violations: list[tuple[str, Path]] = []
    if not REF.is_dir():
        return violations

    for p in REF.glob(_BAK_GLOB):
        if p.is_file() and not _is_under_archive(p):
            violations.append(("pre-reqid-rewrite.bak", p))

    for p in REF.glob(_EXEC_GLOB):
        if not p.is_file() or _is_under_archive(p):
            continue
        rel = p.relative_to(REF).as_posix()
        if rel in _ALLOWED_EXEC_FILES:
            continue
        violations.append(("'<name> exec.md' orphan", p))

    return violations


def main() -> int:
    violations = _find_violations()
    if not violations:
        print("check_reference_orphans: OK (no orphan predecessor files outside _archive/)")
        return 0

    print(
        f"check_reference_orphans: FAIL — {len(violations)} orphan(s) outside "
        f"{ARCHIVE.relative_to(REPO).as_posix()}/",
        file=sys.stderr,
    )
    for kind, path in violations:
        rel = path.relative_to(REPO).as_posix()
        print(f"  [{kind}] {rel}", file=sys.stderr)
    print(
        "\nFix: `git mv <file> docs/reference/_archive/...` or add to "
        "`_ALLOWED_EXEC_FILES` in this script if the keep is intentional.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())

"""Junction/symlink the gitignored runtime-data cache dirs into a fresh worktree.

Item #2 of the worktree-lifecycle streamline. A fresh ``git worktree`` checks out
only tracked files, so gitignored runtime caches (``data/cache/chromadb``,
``data/cache/sparse``, ``data/cache/r1b``, …) are **absent** in a new worktree.
That is the documented cause of "C0.2 BM25 UNAVAILABLE on every lane" the first
time apps_rg runs in a fresh worktree (see project memory
``worktree-runtime-data-junctions``): the fix is to **link** the caches back to
the primary checkout, never to rebuild them.

This module is the SSOT for that linking. It is consumed by:
  * ``.codex/hooks/session_start_branch_guard.py`` (auto-link on worktree create),
  * ``tools/git/worktree_doctor.py --link`` (repair an existing worktree),
  * ``.codex/governance/scripts/post_setup_worktree.py`` (bootstrap),
and exercised directly by ``tests/unit/tools/git/test_worktree_runtime_links.py``.

Design contract:
  * **Junction on Windows** (``mklink /J``) — works for directories without admin /
    Developer Mode, unlike ``os.symlink``. POSIX uses a directory symlink.
  * **Idempotent** — an existing destination (dir/file/link) is left untouched.
  * **Conservative** — only links dirs that exist in the primary and are absent in
    the worktree; never deletes or overwrites.
  * **Fail-soft** — never raises; returns a structured report. Linking is advisory:
    a failure degrades to "run ``worktree_doctor --link`` manually", never a block.

Configuration (env):
  * ``WORKTREE_LINK_DIRS`` — csv of repo-relative dirs to link (overrides the default).
  * ``WORKTREE_LINK_DIRS_DISABLE=1`` — no-op (link nothing).
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

# Gitignored runtime caches a fresh worktree needs but does not check out.
# Kept narrow on purpose (targeted dirs, not all of ``data/cache``) so we never
# link transient/huge trees a worktree should not share by default.
DEFAULT_LINK_DIRS: tuple[str, ...] = (
    "data/cache/chromadb",
    "data/cache/sparse",
    "data/cache/r1b",
)


def link_dirs_from_env(env: dict | None = None) -> tuple[str, ...]:
    """Resolve the set of repo-relative dirs to link, honoring ``WORKTREE_LINK_DIRS``."""
    env = env if env is not None else os.environ
    raw = (env.get("WORKTREE_LINK_DIRS") or "").strip()
    if raw:
        return tuple(p.strip().replace("\\", "/") for p in raw.split(",") if p.strip())
    return DEFAULT_LINK_DIRS


def _disabled(env: dict | None) -> bool:
    env = env if env is not None else os.environ
    return (env.get("WORKTREE_LINK_DIRS_DISABLE") or "") == "1"


def _make_dir_link(link: Path, target: Path) -> tuple[bool, str]:
    """Create a directory link ``link`` -> ``target``. Returns (ok, mechanism|error)."""
    if os.name == "nt":
        # Junctions (/J) need no admin and no Developer Mode, unlike symlinks on Windows.
        try:
            proc = subprocess.run(
                ["cmd", "/c", "mklink", "/J", str(link), str(target)],
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            # Fall through to a symlink attempt below.
            proc = None  # type: ignore[assignment]
            mklink_err = str(exc)
        else:
            if proc.returncode == 0 and link.exists():
                return True, "junction"
            mklink_err = (proc.stderr or proc.stdout or "mklink failed").strip()
        # Best-effort symlink fallback (works when Developer Mode is on).
        try:
            os.symlink(str(target), str(link), target_is_directory=True)
            return True, "symlink"
        except OSError as exc:
            return False, f"junction+symlink failed: {mklink_err}; {exc}"
    # POSIX: a directory symlink needs no special privilege.
    try:
        os.symlink(str(target), str(link), target_is_directory=True)
        return True, "symlink"
    except OSError as exc:
        return False, f"symlink failed: {exc}"


def link_runtime_dirs(
    primary_root: str | os.PathLike,
    worktree_root: str | os.PathLike,
    dirs: tuple[str, ...] | None = None,
    env: dict | None = None,
) -> dict:
    """Link the runtime-cache dirs from ``primary_root`` into ``worktree_root``.

    Returns a report ``{linked, skipped, errors, disabled}`` and never raises.
    """
    report: dict = {"linked": [], "skipped": [], "errors": [], "disabled": False}

    if _disabled(env):
        report["disabled"] = True
        return report

    primary = Path(primary_root).resolve()
    worktree = Path(worktree_root).resolve()

    # A worktree linking to itself (or to a non-existent primary) is a no-op.
    if primary == worktree or not primary.exists():
        report["skipped"].append({"dir": "*", "reason": "primary_unresolved_or_same"})
        return report

    rels = dirs if dirs is not None else link_dirs_from_env(env)
    for rel in rels:
        rel = rel.replace("\\", "/").strip("/")
        if not rel:
            continue
        src = primary / rel
        dst = worktree / rel
        if not src.exists() or not src.is_dir():
            report["skipped"].append({"dir": rel, "reason": "source_absent"})
            continue
        # Path.exists() follows links; an existing junction/symlink/dir is left as-is.
        if dst.exists() or dst.is_symlink():
            report["skipped"].append({"dir": rel, "reason": "destination_exists"})
            continue
        try:
            dst.parent.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            report["errors"].append({"dir": rel, "reason": f"mkdir_parent: {exc}"})
            continue
        ok, mech = _make_dir_link(dst, src)
        if ok:
            report["linked"].append({"dir": rel, "mechanism": mech, "target": str(src)})
        else:
            report["errors"].append({"dir": rel, "reason": mech})

    return report


def summarize(report: dict) -> str:
    """One-line human summary of a link report (for hook ``additionalContext``)."""
    if report.get("disabled"):
        return "runtime-data links: disabled (WORKTREE_LINK_DIRS_DISABLE=1)."
    linked = report.get("linked") or []
    errors = report.get("errors") or []
    if not linked and not errors:
        return "runtime-data links: nothing to link (caches already present or absent in primary)."
    parts = []
    if linked:
        parts.append(f"linked {len(linked)} runtime cache dir(s): " + ", ".join(d["dir"] for d in linked))
    if errors:
        parts.append(f"{len(errors)} link error(s) — run `python tools/git/worktree_doctor.py --link`")
    return "runtime-data links: " + "; ".join(parts) + "."

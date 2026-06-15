"""worktree-doctor — classify every git worktree and repair runtime links.

The current model is explicit named sibling worktrees. Preferred durable lanes use
``work/*`` branches; ``feat/*`` is accepted legacy durable work; ``chat/*`` is legacy
ephemeral work that should not be used for new work. This tool gives the visibility
that prevents pileup without auto-deleting human-named branches:

  * ``report`` (default) — list every worktree, classify it (protected / ephemeral
    ``chat/`` / durable ``work/`` or ``feat/`` / non-canonical / detached), and
    recommend an action (stale-merged -> remove explicitly / active).
  * ``--link [<worktree>]`` — (re)create the gitignored runtime-cache junctions for a
    worktree that is missing them (the C0.2-on-fresh-worktree fix). Item #2 repair path.
  * ``--json`` — machine-readable classification.

Read-only by default: ``report`` never deletes anything. ``--link`` only *adds*
junctions, never removes. Stdlib only; fail-soft.

Examples:
    python tools/git/worktree_doctor.py                 # classify all worktrees
    python tools/git/worktree_doctor.py --json
    python tools/git/worktree_doctor.py --link           # link runtime caches into every worktree
    python tools/git/worktree_doctor.py --link <path>    # ... into one worktree
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

# Make ``tools.git.worktree_runtime_links`` importable when run as a script.
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

try:
    from tools.git.worktree_runtime_links import link_runtime_dirs, summarize
except ImportError:  # pragma: no cover - fallback when package layout differs
    link_runtime_dirs = None  # type: ignore[assignment]
    summarize = None  # type: ignore[assignment]

PROTECTED = ("main", "master", "release")
CANONICAL_PREFIXES = ("work/", "feat/", "chat/")
EPHEMERAL_PREFIX = "chat/"
DURABLE_PREFIXES = ("work/", "feat/")


def _git(*args: str, cwd: Path | None = None) -> tuple[int, str]:
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=str(cwd or _REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return 1, ""
    return proc.returncode, (proc.stdout or "").strip()


def _parse_worktrees(porcelain: str) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    cur: dict[str, str] = {}
    for line in porcelain.splitlines():
        if not line.strip():
            if cur:
                out.append(cur)
                cur = {}
            continue
        if line.startswith("worktree "):
            cur = {"path": line[len("worktree ") :].strip()}
        elif line.startswith("HEAD "):
            cur["head"] = line[len("HEAD ") :].strip()
        elif line.startswith("branch "):
            ref = line[len("branch ") :].strip()
            cur["branch"] = ref[len("refs/heads/") :] if ref.startswith("refs/heads/") else ref
        elif line.strip() == "detached":
            cur["detached"] = "1"
    if cur:
        out.append(cur)
    return out


def _trunk_ref() -> str:
    return os.environ.get("WORKTREE_CLEANUP_TRUNK_REF", "").strip() or "origin/main"


def classify(repo_root: Path, trunk_ref: str = "origin/main", do_fetch: bool = False) -> dict:
    """Classify every worktree. Returns {trunk, primary, worktrees:[...]}. Never raises."""
    if do_fetch:
        _git("fetch", "origin", "main", "--quiet", cwd=repo_root)
    rc, porcelain = _git("worktree", "list", "--porcelain", cwd=repo_root)
    entries = _parse_worktrees(porcelain) if rc == 0 else []
    primary = str(Path(entries[0]["path"]).resolve()) if entries else str(repo_root)

    rows: list[dict] = []
    for i, wt in enumerate(entries):
        path = Path(wt.get("path", "")).resolve()
        branch = wt.get("branch", "")
        detached = wt.get("detached") == "1" or not branch
        keep = (path / ".keep-worktree").exists()

        if detached:
            kind = "detached"
        elif branch in PROTECTED:
            kind = "protected"
        elif branch.startswith(EPHEMERAL_PREFIX):
            kind = "ephemeral"
        elif branch.startswith(DURABLE_PREFIXES):
            kind = "durable"
        else:
            kind = "non-canonical"

        merged = clean = None
        if kind not in ("protected", "detached"):
            rc_anc, _ = _git("merge-base", "--is-ancestor", branch, trunk_ref, cwd=repo_root)
            merged = rc_anc == 0
            rc_st, st = _git("status", "--porcelain", cwd=path)
            clean = rc_st == 0 and not st.strip()

        # Recommended action. The .keep-worktree marker is an ABSOLUTE exemption (matches
        # the reaper, which checks it before clean/merged), so it takes precedence over the
        # merged/clean detail — otherwise the untracked marker file itself reads as "dirty".
        if kind == "protected":
            action = "protected — never reaped"
        elif kind == "detached":
            action = "detached HEAD — inspect/remove manually"
        elif keep:
            action = "kept — .keep-worktree marker (exempt from reaping)"
        elif not merged:
            action = "active — unmerged work (keep)"
        elif not clean:
            action = "active — uncommitted changes (keep)"
        elif kind == "ephemeral":
            action = "stale-merged legacy chat worktree — remove explicitly"
        else:
            action = "stale-merged — remove explicitly: git worktree remove <path>"

        rows.append(
            {
                "index": i,
                "path": str(path),
                "branch": branch or "(detached)",
                "kind": kind,
                "merged": merged,
                "clean": clean,
                "keep_marker": keep,
                "canonical": kind in ("protected", "ephemeral", "durable"),
                "action": action,
            }
        )

    return {"trunk": trunk_ref, "primary": primary, "worktrees": rows}


def _render_table(result: dict) -> str:
    rows = result["worktrees"]
    lines = [
        f"worktree-doctor — {len(rows)} worktree(s); trunk={result['trunk']}",
        f"primary: {result['primary']}",
        "",
    ]
    for r in rows:
        flags = []
        if r["merged"] is True:
            flags.append("merged")
        if r["clean"] is False:
            flags.append("dirty")
        if r["keep_marker"]:
            flags.append("keep")
        if not r["canonical"]:
            flags.append("non-canonical-prefix")
        flag_s = f" [{', '.join(flags)}]" if flags else ""
        lines.append(f"  • {r['branch']}  ({r['kind']}){flag_s}")
        lines.append(f"      {r['path']}")
        lines.append(f"      → {r['action']}")
    # Advisory summary.
    stale = [r for r in rows if r["action"].startswith("stale-merged")]
    noncanon = [r for r in rows if not r["canonical"] and r["kind"] != "detached"]
    if stale:
        lines.append("")
        lines.append(f"{len(stale)} stale-merged worktree(s) — safe to remove manually:")
        for r in stale:
            lines.append(f"    git worktree remove {r['path']}")
    if noncanon:
        lines.append("")
        lines.append(
            f"{len(noncanon)} non-canonical branch prefix(es) — preferred taxonomy is work/* "
            "(durable), feat/* (legacy durable), and chat/* (legacy ephemeral); migrate or set "
            ".keep-worktree."
        )
    return "\n".join(lines)


def _do_link(repo_root: Path, result: dict, target: str | None) -> int:
    if link_runtime_dirs is None:
        sys.stderr.write("worktree-doctor: runtime-link module unavailable.\n")
        return 1
    primary = Path(result["primary"])
    if target:
        targets = [Path(target).resolve()]
    else:
        # Link every non-primary, non-protected worktree.
        targets = [
            Path(r["path"])
            for r in result["worktrees"]
            if Path(r["path"]) != primary and r["kind"] not in ("protected",)
        ]
    if not targets:
        print("worktree-doctor: no eligible worktrees to link.")
        return 0
    rc = 0
    for wt in targets:
        report = link_runtime_dirs(primary, wt)
        msg = summarize(report) if summarize else json.dumps(report)
        print(f"  {wt}\n    {msg}")
        if report.get("errors"):
            rc = 1
    return rc


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Classify and repair git worktrees.")
    ap.add_argument("--json", action="store_true", help="machine-readable classification")
    ap.add_argument(
        "--link",
        nargs="?",
        const="__all__",
        default=None,
        metavar="WORKTREE",
        help="(re)create runtime-cache junctions for a worktree (default: all)",
    )
    ap.add_argument("--fetch", action="store_true", help="git fetch origin/main before classifying")
    ap.add_argument("--trunk", default=None, help="trunk ref (default: origin/main)")
    args = ap.parse_args(argv)

    repo_root = _REPO_ROOT
    trunk = args.trunk or _trunk_ref()
    result = classify(repo_root, trunk_ref=trunk, do_fetch=args.fetch)

    if args.link is not None:
        target = None if args.link == "__all__" else args.link
        return _do_link(repo_root, result, target)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(_render_table(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

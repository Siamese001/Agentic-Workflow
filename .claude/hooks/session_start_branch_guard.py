"""SessionStart — named worktree advisor.

This hook is intentionally non-mutating. It does not create branches, add worktrees,
fast-forward trunks, link runtime caches, or clean up old worktrees.

The sustainable model is one registered sibling worktree per durable workstream, not
one timestamped worktree per chat. If a session starts on a protected branch
(``main``/``master`` by default), this hook emits guidance for choosing or creating a
named sibling worktree such as:

    git worktree add ../Agentic-Workflow-FRESH-worktrees/claude-apps-rg -b claude-apps-rg origin/main

The hard enforcement remains in ``before_file_edit_branch_guard.py``: edits to a
protected checkout are blocked, and editable worktrees must use the agent-owned
same-name branch/folder contract.

Bypass: ``BRANCH_PER_CHAT_BYPASS=1`` or ``WORKTREE_PER_CHAT_BYPASS=1``.
Protected set override: ``BRANCH_PER_CHAT_PROTECTED=main,master,release`` (csv).
Worktree parent override: ``CHAT_WORKTREE_ROOT=/abs/path`` (default
``<repo-parent>/<repo-name>-worktrees``).
Execution owner override: ``WORKTREE_IDE_OWNER=codex|claude`` (default ``claude`` here).
The branch prefix is derived only from that owner; ``WORKTREE_BRANCH_PREFIX`` is ignored.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PROTECTED = ("main", "master")
DEFAULT_TOPIC = "apps-rg"
DEFAULT_IDE_OWNER = "claude"
AGENT_OWNERS = {"codex", "claude"}
BRANCH_TOPIC_RE = re.compile(r"^[a-z0-9][a-z0-9-]*[a-z0-9]$")
LOW_SIGNAL_GENERATED_RE = re.compile(r"^[a-z]+-[a-z]+-[0-9a-f]{6,}$")
GENERIC_TOPIC_TOKENS = {
    "branch",
    "change",
    "changes",
    "fix",
    "misc",
    "task",
    "temp",
    "test",
    "update",
    "wip",
    "work",
}


def _git(*args: str, cwd: Path | None = None) -> tuple[int, str]:
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=str(cwd or REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return 1, ""
    return proc.returncode, (proc.stdout or "").strip()


def _trunk_ref() -> str:
    return os.environ.get("WORKTREE_CLEANUP_TRUNK_REF", "").strip() or "origin/main"


def _ide_owner() -> str:
    raw = os.environ.get("WORKTREE_IDE_OWNER", "").strip().lower()
    if raw in {"codex", "claude"}:
        return raw
    # This is a Claude hook, so Claude is the safe default. Codex callers can set
    # WORKTREE_IDE_OWNER=codex when reusing the helper logic outside Claude Code.
    return DEFAULT_IDE_OWNER


def _branch_prefix() -> str:
    return f"{_ide_owner()}-"


def _worktree_parent() -> Path:
    override = os.environ.get("CHAT_WORKTREE_ROOT", "").strip()
    if override:
        return Path(override)
    return REPO_ROOT.parent / f"{_primary_checkout_name()}-worktrees"


def _primary_checkout_name() -> str:
    rc, common = _git("rev-parse", "--git-common-dir", cwd=REPO_ROOT)
    if rc != 0 or not common:
        return REPO_ROOT.name
    common_path = Path(common)
    if not common_path.is_absolute():
        common_path = (REPO_ROOT / common_path).resolve()
    if common_path.name == ".git":
        return common_path.parent.name
    return REPO_ROOT.name


def _branch_name(topic: str = DEFAULT_TOPIC) -> str:
    return f"{_branch_prefix()}{topic}"


def _worktree_dir_name(topic: str = DEFAULT_TOPIC) -> str:
    return _branch_name(topic)


def _worktree_path(topic: str = DEFAULT_TOPIC) -> Path:
    return _worktree_parent() / _worktree_dir_name(topic)


def _worktree_root() -> Path | None:
    rc, root = _git("rev-parse", "--show-toplevel")
    if rc != 0 or not root:
        return None
    return Path(root).resolve()


def _protected() -> set[str]:
    raw = os.environ.get("BRANCH_PER_CHAT_PROTECTED", "")
    if raw.strip():
        return {b.strip() for b in raw.split(",") if b.strip()}
    return set(DEFAULT_PROTECTED)


def _bypass() -> bool:
    return (
        os.environ.get("BRANCH_PER_CHAT_BYPASS") == "1"
        or os.environ.get("WORKTREE_PER_CHAT_BYPASS") == "1"
    )


def _read_payload() -> dict:
    try:
        raw = sys.stdin.read()
    except OSError:
        return {}
    try:
        obj = json.loads(raw) if raw.strip() else {}
        return obj if isinstance(obj, dict) else {}
    except json.JSONDecodeError:
        return {}


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
        elif line.startswith("branch "):
            ref = line[len("branch ") :].strip()
            cur["branch"] = ref[len("refs/heads/") :] if ref.startswith("refs/heads/") else ref
    if cur:
        out.append(cur)
    return out


def _worktree_summary(limit: int = 8) -> str:
    rc, porcelain = _git("worktree", "list", "--porcelain")
    if rc != 0:
        return "Existing worktrees: unavailable (`git worktree list` failed)."
    rows = _parse_worktrees(porcelain)
    if not rows:
        return "Existing worktrees: none registered."
    rendered = [
        f"  - {row.get('branch', '(detached)')}  {row.get('path', '')}".rstrip()
        for row in rows[:limit]
    ]
    extra = len(rows) - len(rendered)
    if extra > 0:
        rendered.append(f"  - ... {extra} more")
    return "Existing worktrees:\n" + "\n".join(rendered)


def _emit_context(message: str) -> None:
    out = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": message,
        }
    }
    sys.stdout.write(json.dumps(out))


def _owner_label() -> str:
    return "Codex" if _ide_owner() == "codex" else "Claude Code"


def _topic_from_agent_branch(branch: str) -> str:
    prefix = _branch_prefix()
    if branch.startswith(prefix):
        return branch[len(prefix) :]
    return ""


def _topic_is_high_signal(topic: str) -> bool:
    if not topic or "/" in topic or "\\" in topic:
        return False
    if topic != topic.lower():
        return False
    if LOW_SIGNAL_GENERATED_RE.fullmatch(topic):
        return False
    tokens = [part for part in topic.split("-") if part]
    if len(tokens) < 2:
        return False
    if topic in GENERIC_TOPIC_TOKENS:
        return False
    if all(token in GENERIC_TOPIC_TOKENS for token in tokens):
        return False
    return True


def _contract_violations(branch: str, worktree_root: Path | None) -> list[str]:
    violations: list[str] = []
    prefix = _branch_prefix()
    if "/" in branch or "\\" in branch:
        violations.append("branch must not contain slash path separators")
    if not branch.startswith(prefix):
        violations.append(f"branch must start with `{prefix}` for this agent")
    else:
        topic = _topic_from_agent_branch(branch)
        if not BRANCH_TOPIC_RE.fullmatch(topic):
            violations.append("branch topic must use lowercase letters, numbers, and hyphens")
        elif not _topic_is_high_signal(topic):
            violations.append("branch topic must be high-signal, not a generated or generic name")
    if worktree_root is not None and worktree_root.name != branch:
        violations.append("worktree folder basename must exactly equal the local branch name")
    return violations


def _guidance(branch: str) -> str:
    wt_path = _worktree_path()
    new_branch = _branch_name()
    trunk = _trunk_ref()
    prefix = _branch_prefix()
    return (
        f"worktree-isolation: this session is on protected branch '{branch}'. "
        "Claude no longer auto-creates timestamped chat worktrees.\n\n"
        "REUSE-FIRST (default): before creating anything, scan the existing worktrees "
        "below and REUSE the one whose workstream matches this task. A new chat on the "
        "same or overlapping scope continues in the SAME sibling worktree; do not mint a "
        "fresh worktree per chat or per wave. A later wave in the same plan/app/workstream "
        "is NOT a material scope change. Create a NEW worktree ONLY when the scope "
        "MATERIALLY changes (a genuinely different durable workstream, not a follow-up "
        "on the current one).\n\n"
        "Create a new one explicitly ONLY on a material scope change "
        "(replace `apps-rg` with the durable topic name, e.g. `apps-rg-hotspot-tests`; "
        "do not use `apps-rg-wave4-tests`):\n"
        f"    git worktree add {wt_path} -b {new_branch} {trunk}\n"
        f"    cd {wt_path}\n\n"
        f"This {_owner_label()} context must use `{prefix}<high-signal-topic>` branches; "
        "do not use the other agent's prefix. When the work touches a specific app, name it "
        f"first: `{prefix}apps-<x>-<scope>` (e.g. `{prefix}apps-rg-competencies-finish`); "
        "core/agentic_core/infrastructure work needs no app segment. Make the worktree folder "
        "basename exactly match the branch name. Avoid `chat/<timestamp>` branches and generated "
        "adjective-name hashes. Codex reuse of this helper must set "
        "`WORKTREE_IDE_OWNER=codex` before branch names are generated. "
        "Edits to protected checkouts are still blocked by the PreToolUse edit guard.\n\n"
        f"{_worktree_summary()}\n\n"
        "Cleanup is explicit: run "
        "`python .claude/hooks/prune_merged_chat_worktrees.py --dry-run` to inspect, "
        "then `--delete-merged` when you intentionally want to remove delivered local "
        "worktrees/branches."
    )


def _naming_warning(branch: str, violations: list[str], worktree_root: Path | None) -> str:
    root_detail = f" Current worktree root: `{worktree_root}`." if worktree_root else ""
    return (
        f"worktree-naming-contract: this session is on non-canonical branch '{branch}' "
        f"because {'; '.join(violations)}.{root_detail}\n"
        "Before editing, rename/move to an agent-owned high-signal branch whose worktree "
        "folder basename matches exactly, e.g.:\n"
        f"    git branch -m {_branch_name()}\n"
        f"    git worktree move {worktree_root or '<old-path>'} {_worktree_path()}\n\n"
        f"This {_owner_label()} context must use `{_branch_prefix()}<high-signal-topic>` "
        "branches. Avoid slash namespaces, generated adjective-name hashes, and folders "
        "whose basename differs from the branch. The PreToolUse edit guard will block "
        "file edits until the naming contract is satisfied."
    )


def main() -> int:
    _read_payload()  # drain SessionStart stdin; contents are not needed.

    if _bypass():
        return 0

    rc, branch = _git("rev-parse", "--abbrev-ref", "HEAD")
    if rc != 0 or not branch:
        return 0  # not a git repo / git unavailable — fail-soft
    if branch not in _protected():
        if branch == "HEAD":
            return 0  # detached helper worktrees are not durable edit lanes
        worktree_root = _worktree_root()
        violations = _contract_violations(branch, worktree_root)
        if not violations:
            return 0  # already isolated and canonical
        msg = _naming_warning(branch, violations, worktree_root)
        sys.stderr.write("[HOOK] " + msg + "\n")
        _emit_context(msg)
        return 0

    msg = _guidance(branch)
    sys.stderr.write("[HOOK] " + msg + "\n")
    _emit_context(msg)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

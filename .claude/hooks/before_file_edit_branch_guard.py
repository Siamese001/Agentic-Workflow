"""PreToolUse (Edit|Write|MultiEdit) — named worktree edit gate.

Hard enforcement for named worktree isolation. The branch is resolved from the
**working tree that owns the file being edited** (git is run with ``cwd`` set to
the target file's directory), so:

* Edits inside a registered named workstream worktree whose branch and folder both
  satisfy the naming contract -> ALLOW.
* Edits to the primary checkout while it is on a protected branch
  (``main``/``master``) -> BLOCK (exit 2) with a remediation pointing at the
  worktree. This nudges all mutation into an explicit named sibling worktree.

Resolving the branch per-file (rather than from a fixed repo root) is what makes
the gate worktree-aware: a sibling worktree has its own HEAD/branch, which git
reports correctly when invoked from inside it.

Allow conditions (fail-soft / non-blocking):
* Not a git repo / git unavailable / no resolvable path.
* Owning working tree on an agent-owned, high-signal branch such as
  ``codex-worktree-naming-contract`` whose folder basename is exactly the branch name.
* ``BRANCH_PER_CHAT_BYPASS=1`` or ``WORKTREE_PER_CHAT_BYPASS=1``.

App-scope segment: when the file being edited lives under an ``apps_<x>`` package
(``apps_rg``/``apps_lic``/``apps01``/...), the branch topic MUST name that app as its first
segment -> ``<owner>-apps-<x>-<scope>`` (e.g. ``claude-apps-rg-competencies-finish``). The app
token is the package name with ``_`` normalised to ``-`` to fit the all-hyphen topic contract.
Core / ``agentic_core`` / infrastructure / governance edits touch no ``apps_<x>`` file, so they
require NO app segment (``claude-governance-hooks`` stays valid).

Self-contained: no dependency on ``lib.claude_hook_common`` (absent in some
checkouts). Protected set override: ``BRANCH_PER_CHAT_PROTECTED=main,master`` (csv).
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
# App-package directory shape: ``apps_rg`` / ``apps_lic`` (underscore) or ``apps01`` (numeric).
APP_DIR_RE = re.compile(r"^apps(?:_[a-z0-9]+|[0-9]+)$")
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


def _target_path(payload: dict) -> str:
    ti = payload.get("tool_input")
    if isinstance(ti, dict):
        for key in ("file_path", "path", "notebook_path"):
            val = ti.get(key)
            if isinstance(val, str) and val:
                return val
    return ""


def _is_plan_file(file_path: str) -> bool:
    """True for a plan SSOT markdown file (parent dir == ``plans``, not under an ``_archive/`` tree).

    Plans are a shared, always-on SSOT — not feature-branch work — so they are EXEMPT from
    named-worktree isolation and must land in the primary checkout's ``plans/`` folder
    (``C:\\Git\\Agentic-Workflow-FRESH\\plans``). Without this exemption a plan written during an
    isolated session is trapped in a non-primary worktree and never reaches the canonical SSOT
    (plan ``plan-ssot-notion-pipeline-d2f7a1`` W1). Matches repo-root ``plans/`` and legacy
    ``.claude/plans/`` (both have parent dir ``plans``).
    """
    if not file_path:
        return False
    norm = file_path.replace("\\", "/")
    if not norm.endswith(".md"):
        return False
    if "/plans/_archive/" in norm:
        return False
    if Path(norm).parent.name != "plans":
        return False
    # Exclude docs/reports/plans/ — that is a reports tree, not the plan SSOT (the rule forbids it
    # as a plan location). Canonical plan dirs (repo-root plans/, .claude/plans/) have no docs/reports
    # ancestor, so this denylist is safe.
    lowered = {p.lower() for p in Path(norm).parts}
    if "reports" in lowered or "docs" in lowered:
        return False
    return True


def _owning_dir(file_path: str) -> Path:
    """Directory to run git in: the file's parent if resolvable, else REPO_ROOT."""
    if file_path:
        p = Path(file_path)
        if not p.is_absolute():
            p = REPO_ROOT / p
        parent = p.parent
        # Walk up to the nearest existing ancestor (file may not exist yet on Write).
        while not parent.exists() and parent != parent.parent:
            parent = parent.parent
        if parent.exists():
            return parent
    return REPO_ROOT


def _branch_of(cwd: Path) -> str:
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return ""
    if proc.returncode != 0:
        return ""
    return (proc.stdout or "").strip()


def _worktree_root(cwd: Path) -> Path | None:
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if proc.returncode != 0:
        return None
    root = (proc.stdout or "").strip()
    return Path(root).resolve() if root else None


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


def _ide_owner() -> str:
    raw = os.environ.get("WORKTREE_IDE_OWNER", "").strip().lower()
    if raw in {"codex", "claude"}:
        return raw
    return DEFAULT_IDE_OWNER


def _branch_prefix() -> str:
    return f"{_ide_owner()}-"


def _primary_checkout_name() -> str:
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "--git-common-dir"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return REPO_ROOT.name
    common = (proc.stdout or "").strip()
    if proc.returncode != 0 or not common:
        return REPO_ROOT.name
    common_path = Path(common)
    if not common_path.is_absolute():
        common_path = (REPO_ROOT / common_path).resolve()
    if common_path.name == ".git":
        return common_path.parent.name
    return REPO_ROOT.name


def _worktree_parent() -> Path:
    override = os.environ.get("CHAT_WORKTREE_ROOT", "").strip()
    if override:
        return Path(override)
    return REPO_ROOT.parent / f"{_primary_checkout_name()}-worktrees"


def _branch_name(topic: str = DEFAULT_TOPIC) -> str:
    return f"{_branch_prefix()}{topic}"


def _worktree_dir_name(topic: str = DEFAULT_TOPIC) -> str:
    return _branch_name(topic)


def _worktree_path(topic: str = DEFAULT_TOPIC) -> Path:
    return _worktree_parent() / _worktree_dir_name(topic)


def _remediation_example(topic: str = DEFAULT_TOPIC) -> str:
    return (
        f"    git worktree add {_worktree_path(topic)} -b {_branch_name(topic)} origin/main\n"
        f"    cd {_worktree_path(topic)}"
    )


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


def _app_token_for_path(file_path: str) -> str:
    """Return the hyphenated app segment (e.g. ``apps-rg``) when the target file lives under an
    ``apps_<x>`` package, else ``""``.

    App-impacting edits must name the app in the branch topic (``<owner>-apps-<x>-<scope>``);
    core / ``agentic_core`` / infrastructure edits are exempt and carry no app segment. The token is
    derived from the first path component matching the app-package shape, with ``_`` normalised to
    ``-`` so it composes with the all-hyphen branch-topic contract (``apps_rg`` -> ``apps-rg``).
    """
    if not file_path:
        return ""
    norm = file_path.replace("\\", "/")
    for part in norm.split("/"):
        if APP_DIR_RE.fullmatch(part):
            return part.replace("_", "-")
    return ""


def _app_segment_violation(branch: str, app_token: str) -> str:
    """If editing an app file, the branch topic must be ``apps-<x>-<scope>`` for that app.

    Returns the violation string, or ``""`` when the branch already names the app (or no app
    segment is required). Only meaningful for an agent-owned, slash-free branch.
    """
    if not app_token:
        return ""
    if "/" in branch or "\\" in branch or not branch.startswith(_branch_prefix()):
        return ""  # other violations already cover prefix/slash; don't double-report
    topic = _topic_from_agent_branch(branch)
    needle = f"{app_token}-"
    if topic.startswith(needle) and topic[len(needle) :]:
        return ""
    app_pkg = app_token.replace("-", "_")
    return (
        f"app-scoped edit under `{app_pkg}/` requires the branch topic to start with "
        f"`{app_token}-<scope>` (e.g. `{_branch_prefix()}{app_token}-<high-signal-scope>`)"
    )


def _contract_violations(
    branch: str, worktree_root: Path | None, app_token: str = ""
) -> list[str]:
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
    app_violation = _app_segment_violation(branch, app_token)
    if app_violation:
        violations.append(app_violation)
    if worktree_root is not None and worktree_root.name != branch:
        violations.append("worktree folder basename must exactly equal the local branch name")
    return violations


def main() -> int:
    if _bypass():
        return 0

    payload = _read_payload()
    target = _target_path(payload)

    # Plans are a shared SSOT, exempt from worktree isolation — they always write to the primary
    # checkout's plans/ folder (plan-ssot-notion-pipeline-d2f7a1 W1). Without this, plans get trapped
    # in ephemeral chat worktrees and never reach C:\Git\Agentic-Workflow-FRESH\plans.
    if _is_plan_file(target):
        return 0

    cwd = _owning_dir(target)
    branch = _branch_of(cwd)
    if not branch:
        return 0  # fail-soft
    if branch not in _protected():
        worktree_root = _worktree_root(cwd)
        app_token = _app_token_for_path(target)
        violations = _contract_violations(branch, worktree_root, app_token)
        if not violations:
            return 0  # owning worktree is isolated and follows the naming contract
        suggested_topic = f"{app_token}-<scope>" if app_token else DEFAULT_TOPIC
        root_detail = f" Current worktree root: `{worktree_root}`." if worktree_root else ""
        reason = (
            f"worktree-naming-contract: editing branch '{branch}' is blocked because "
            f"{'; '.join(violations)}.{root_detail}\n"
            "Rename/move the worktree so the branch and folder are identical, "
            "scope-bearing, and agent-owned, e.g.:\n"
            f"{_remediation_example(suggested_topic)}\n"
            "Use `git branch -m <new-name>` for the checked-out branch and "
            "`git worktree move <old-path> <new-path>` for the folder."
        )
        sys.stderr.write(reason + "\n")
        return 2

    reason = (
        f"worktree-isolation: editing a protected checkout on branch '{branch}' is blocked. "
        "Use or create a named sibling worktree for the durable workstream, with an "
        "agent-owned high-signal branch whose worktree folder basename matches exactly, e.g.:\n"
        f"{_remediation_example()}\n"
        f"This {_owner_label()} context must use `{_branch_prefix()}<high-signal-topic>` branches; "
        "do not use the other agent's prefix. Avoid slash namespaces, timestamped `chat/*` "
        "branches, and generated adjective-name hashes. (Set WORKTREE_PER_CHAT_BYPASS=1 only for an "
        "intentional on-primary change.)"
    )
    sys.stderr.write(reason + "\n")
    return 2  # block


if __name__ == "__main__":
    raise SystemExit(main())

import re
import shlex
import subprocess
import sys
from pathlib import Path

from lib.codex_hook_common import (
    allow,
    block,
    contains_legacy_execution_token,
    read_payload,
    text_from_payload,
    write_receipt,
)

# Wire the turn-hanging command guards (python -c quote-hazard + interactive/pager) from the
# governance gate into this live PreToolUse Bash hook. Previously pre_run_gate.py implemented
# these but was never dispatched, so the bans (constitutional §26 + python-dash-c-quote-hazard.md)
# were doctrine-only. Fail-open if the module is unavailable — a missing gate must never wedge shells.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "governance" / "scripts"))
try:
    from pre_run_gate import shell_command_block_reason
except Exception:  # guardian: allow-broad-exception -- hook fail-open if gate module is unavailable
    shell_command_block_reason = None


def _command_text(p: dict) -> str:
    """Best-effort extraction of the shell command string from the PreToolUse payload."""
    ti = p.get("tool_input")
    if isinstance(ti, dict) and isinstance(ti.get("command"), str):
        return ti["command"]
    if isinstance(p.get("command"), str):
        return p["command"]
    info = p.get("tool_info")
    if isinstance(info, dict) and isinstance(info.get("command_line"), str):
        return info["command_line"]
    return ""


def _normal_command(command: str) -> str:
    return re.sub(r"\s+", " ", command.strip())


REPO_ROOT = Path(__file__).resolve().parents[2]


def _git_common_dir() -> Path | None:
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
        return None
    common = (proc.stdout or "").strip()
    if proc.returncode != 0 or not common:
        return None
    path = Path(common)
    if not path.is_absolute():
        path = (REPO_ROOT / path).resolve()
    return path


def _primary_checkout_root() -> Path:
    common = _git_common_dir()
    if common and common.name == ".git":
        return common.parent
    return REPO_ROOT


def _worktree_ssot_root() -> Path:
    primary = _primary_checkout_root()
    return primary.parent / f"{primary.name}-worktrees"


def _normalize_path(path: Path) -> str:
    return str(path.resolve()).replace("/", "\\").casefold()


def _is_inside_ssot(path_text: str) -> bool:
    raw = path_text.strip().strip("'\"")
    if not raw:
        return False
    path = Path(raw)
    if not path.is_absolute():
        path = REPO_ROOT / path
    target = _normalize_path(path)
    root = _normalize_path(_worktree_ssot_root())
    return target == root or target.startswith(root.rstrip("\\") + "\\")


def _split_args(args: str) -> list[str]:
    try:
        return [part.strip("'\"") for part in shlex.split(args, posix=False)]
    except ValueError:
        return []


def _worktree_add_paths(command: str) -> list[str]:
    paths: list[str] = []
    for match in re.finditer(
        r"(?i)(?:^|[;&|]\s*)git(?:\.exe)?\s+worktree\s+add\b(?P<args>[^;&|]*)",
        command,
    ):
        args = _split_args(match.group("args"))
        idx = 0
        while idx < len(args):
            token = args[idx]
            if token in {"-b", "-B", "--orphan", "--reason"}:
                idx += 2
                continue
            if token.startswith("--reason="):
                idx += 1
                continue
            if token.startswith("-"):
                idx += 1
                continue
            paths.append(token)
            break
    return paths


def worktree_ssot_block_reason(command: str) -> str | None:
    bad_paths = [path for path in _worktree_add_paths(command) if not _is_inside_ssot(path)]
    if not bad_paths:
        return None
    root = _worktree_ssot_root()
    return (
        "git worktree add must target the Agentic-Workflow worktree SSOT root: "
        f"{root}. Offending path(s): {', '.join(bad_paths)}"
    )


def _is_pr_completion_command(command: str) -> bool:
    """Return True for commands that complete PR/main publication locally."""
    normalized = _normal_command(command)
    if re.search(r"(?i)(^|[;&|]\s*)gh(?:\.exe)?\s+pr\s+merge\b", normalized):
        return True
    return bool(
        re.search(
            r"(?i)(^|[;&|]\s*)git(?:\.exe)?\s+push\s+origin\s+"
            r"(?:main\b|head:main\b|head:refs/heads/main\b|[^\s;&|]+:refs/heads/main\b)",
            normalized,
        )
        or re.search(
            r"(?i)(^|[;&|]\s*)git(?:\.exe)?\s+push\s+(?:-[^\s]+\s+)+origin\s+"
            r"(?:main\b|head:main\b|head:refs/heads/main\b|[^\s;&|]+:refs/heads/main\b)",
            normalized,
        )
    )


def _has_main_closeout_chain(command: str) -> bool:
    """Require same-command closeout proof after PR/main completion."""
    normalized = _normal_command(command).casefold()
    return (
        "&&" in normalized
        and normalized.count("codex_main_closeout.py") >= 2
        and re.search(
            r"codex_main_closeout\.py\b[^&|;]*--apply\b[^&|;]*--fetch\b[^&|;]*--publication-only\b[^&|;]*--require-governance-health\b",
            normalized,
        )
        and re.search(
            r"codex_main_closeout\.py\b[^&|;]*--check\b[^&|;]*--fetch\b[^&|;]*--publication-only\b[^&|;]*--require-governance-health\b",
            normalized,
        )
    )


def pr_completion_block_reason(command: str) -> str | None:
    if not _is_pr_completion_command(command):
        return None
    if _has_main_closeout_chain(command):
        return None
    return (
        "PR/main completion commands must chain publication closeout proof in the same command: "
        "python scripts/governance/codex_main_closeout.py --apply --fetch --json --publication-only --require-governance-health && "
        "python scripts/governance/codex_main_closeout.py --check --fetch --json --publication-only --require-governance-health"
    )


payload = read_payload()
text = text_from_payload(payload)
legacy = contains_legacy_execution_token(text)
if legacy:
    reason = "Shell command targets legacy execution surface: " + ", ".join(legacy)
    write_receipt("beforeShellExecution", payload, "block", reason)
    raise SystemExit(block(reason))

risky = []
for token in ("rm -rf .cursor", "rmdir /s .cursor", "del /s .cursor", "Remove-Item .cursor"):
    if token in text:
        risky.append(token)
if risky:
    reason = "Shell command risks deleting active legacy editor controls: " + ", ".join(risky)
    write_receipt("beforeShellExecution", payload, "block", reason)
    raise SystemExit(block(reason))

command = _command_text(payload)
completion_reason = pr_completion_block_reason(command)
if completion_reason:
    write_receipt("beforeShellExecution", payload, "block", completion_reason)
    raise SystemExit(block(completion_reason))

worktree_reason = worktree_ssot_block_reason(command)
if worktree_reason:
    write_receipt("beforeShellExecution", payload, "block", worktree_reason)
    raise SystemExit(block(worktree_reason))

# Turn-hanging command guard (quote-hazard / interactive / pager), enforced via pre_run_gate.
if shell_command_block_reason is not None:
    if command:
        hang_reason = shell_command_block_reason(command)
        if hang_reason:
            write_receipt("beforeShellExecution", payload, "block", hang_reason)
            raise SystemExit(block(hang_reason))

# Branch/worktree naming is advisory on Bash commands. Worktree root placement is
# enforced here because `git worktree add` creates filesystem state before edits happen.

write_receipt("beforeShellExecution", payload, "allow", "command accepted")
raise SystemExit(allow("command accepted"))

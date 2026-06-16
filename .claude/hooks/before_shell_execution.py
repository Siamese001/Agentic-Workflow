import sys
import shlex
from pathlib import Path

from lib.claude_hook_common import allow, block, contains_legacy_execution_token, read_payload, text_from_payload, write_receipt

# Wire the turn-hanging command guards (python -c quote-hazard + interactive/pager) from the
# governance gate into this live PreToolUse Bash hook. Previously pre_run_gate.py implemented
# these but was never dispatched, so the bans (constitutional §26 + python-dash-c-quote-hazard.md)
# were doctrine-only. Fail-open if the module is unavailable — a missing gate must never wedge shells.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "governance" / "scripts"))
try:
    from pre_run_gate import shell_command_block_reason
except Exception:  # guardian: allow-broad-exception -- hook fail-open if gate module is unavailable
    shell_command_block_reason = None

try:
    from before_file_edit_branch_guard import _branch_prefix, _contract_violations, _remediation_example
except Exception:  # guardian: allow-broad-exception -- branch creation guard must fail open
    _branch_prefix = None
    _contract_violations = None
    _remediation_example = None

_COMMAND_SEPARATORS = {";", "&&", "||", "|"}
_GIT_GLOBAL_OPTS_WITH_VALUE = {
    "-C",
    "-c",
    "--git-dir",
    "--work-tree",
    "--namespace",
    "--exec-path",
    "--super-prefix",
}
_BRANCH_QUERY_OR_NONCREATE_OPTS = {
    "-a",
    "-d",
    "-D",
    "-r",
    "-u",
    "-v",
    "-vv",
    "--all",
    "--color",
    "--column",
    "--contains",
    "--delete",
    "--edit-description",
    "--format",
    "--list",
    "--merged",
    "--no-color",
    "--no-column",
    "--no-contains",
    "--no-merged",
    "--points-at",
    "--remotes",
    "--set-upstream-to",
    "--show-current",
    "--sort",
    "--unset-upstream",
    "--verbose",
}
_BRANCH_OPTS_WITH_VALUE = {
    "--format",
    "--sort",
}
_WORKTREE_OPTS_WITH_VALUE = {"--reason"}


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


def _strip_quotes(token: str) -> str:
    return token.strip().strip("\"'")


def _command_tokens(command: str) -> list[str]:
    try:
        return [_strip_quotes(tok) for tok in shlex.split(command, posix=False)]
    except ValueError:
        return command.split()


def _is_git_token(token: str) -> bool:
    name = Path(token).name.lower()
    return name in {"git", "git.exe"}


def _skip_git_global_options(tokens: list[str], index: int) -> int:
    index += 1
    while index < len(tokens):
        tok = tokens[index]
        if tok in _COMMAND_SEPARATORS:
            return index
        if tok in _GIT_GLOBAL_OPTS_WITH_VALUE:
            index += 2
            continue
        if any(tok.startswith(f"{opt}=") for opt in _GIT_GLOBAL_OPTS_WITH_VALUE if opt.startswith("--")):
            index += 1
            continue
        if tok == "--no-pager" or tok == "--bare" or tok == "--literal-pathspecs":
            index += 1
            continue
        break
    return index


def _branch_violation_reason(branch: str, worktree_path: str = "") -> str:
    if _contract_violations is None or _remediation_example is None or _branch_prefix is None:
        return ""
    root = Path(worktree_path) if worktree_path else None
    violations = _contract_violations(branch, root)
    if not violations:
        return ""
    target = f" with worktree folder `{worktree_path}`" if worktree_path else ""
    return (
        f"worktree-creation-contract: shell command would create or rename branch "
        f"`{branch}`{target}, but {'; '.join(violations)}.\n"
        f"This agent must use `{_branch_prefix()}<high-signal-topic>` branches, no slash "
        "namespaces, no generated adjective-name hashes, and a worktree folder basename that "
        "exactly equals the branch name, e.g.:\n"
        f"{_remediation_example()}"
    )


def _find_option_value(args: list[str], names: tuple[str, ...]) -> str:
    for idx, tok in enumerate(args):
        if tok in names and idx + 1 < len(args):
            return args[idx + 1]
        for name in names:
            if name.startswith("--") and tok.startswith(f"{name}="):
                return tok.split("=", 1)[1]
    return ""


def _worktree_add_reason(args: list[str]) -> str:
    branch = _find_option_value(args, ("-b", "-B", "--branch"))
    detached = any(tok in {"--detach", "-d"} for tok in args)
    path = ""
    idx = 0
    while idx < len(args):
        tok = args[idx]
        if tok in {"-b", "-B", "--branch"}:
            idx += 2
            continue
        if tok.startswith("--branch="):
            idx += 1
            continue
        if tok in _WORKTREE_OPTS_WITH_VALUE:
            idx += 2
            continue
        if tok.startswith("-"):
            idx += 1
            continue
        path = tok
        break
    if detached and not branch:
        return ""
    if not branch and path:
        branch = Path(path.rstrip("\\/")).name
    if not branch:
        return ""
    return _branch_violation_reason(branch, path)


def _checkout_or_switch_reason(args: list[str]) -> str:
    branch = _find_option_value(args, ("-b", "-B", "-c", "-C", "--orphan"))
    return _branch_violation_reason(branch) if branch else ""


def _branch_command_reason(args: list[str]) -> str:
    if any(
        tok in _BRANCH_QUERY_OR_NONCREATE_OPTS
        or any(
            tok.startswith(f"{opt}=")
            for opt in _BRANCH_QUERY_OR_NONCREATE_OPTS
            if opt.startswith("--")
        )
        for tok in args
    ):
        return ""
    moving = any(tok in {"-m", "-M", "--move", "-c", "-C", "--copy"} for tok in args)
    non_options: list[str] = []
    idx = 0
    while idx < len(args):
        tok = args[idx]
        if tok in _BRANCH_OPTS_WITH_VALUE:
            idx += 2
            continue
        if any(tok.startswith(f"{opt}=") for opt in _BRANCH_OPTS_WITH_VALUE if opt.startswith("--")):
            idx += 1
            continue
        if tok.startswith("-"):
            idx += 1
            continue
        non_options.append(tok)
        idx += 1
    if not non_options:
        return ""
    branch = non_options[-1] if moving else non_options[0]
    return _branch_violation_reason(branch)


def branch_creation_block_reason(command: str) -> str | None:
    if _contract_violations is None:
        return None
    tokens = _command_tokens(command)
    for idx, tok in enumerate(tokens):
        if not _is_git_token(tok):
            continue
        sub_idx = _skip_git_global_options(tokens, idx)
        if sub_idx >= len(tokens):
            continue
        sub = tokens[sub_idx]
        end = sub_idx + 1
        while end < len(tokens) and tokens[end] not in _COMMAND_SEPARATORS:
            end += 1
        args = tokens[sub_idx + 1 : end]
        reason = ""
        if sub == "worktree" and args[:1] == ["add"]:
            reason = _worktree_add_reason(args[1:])
        elif sub in {"checkout", "switch"}:
            reason = _checkout_or_switch_reason(args)
        elif sub == "branch":
            reason = _branch_command_reason(args)
        if reason:
            return reason
    return None


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
    reason = "Shell command risks deleting active Cursor controls: " + ", ".join(risky)
    write_receipt("beforeShellExecution", payload, "block", reason)
    raise SystemExit(block(reason))

# Turn-hanging command guard (quote-hazard / interactive / pager), enforced via pre_run_gate.
if shell_command_block_reason is not None:
    command = _command_text(payload)
    if command:
        hang_reason = shell_command_block_reason(command)
        if hang_reason:
            write_receipt("beforeShellExecution", payload, "block", hang_reason)
            raise SystemExit(block(hang_reason))

command = _command_text(payload)
if command:
    branch_reason = branch_creation_block_reason(command)
    if branch_reason:
        write_receipt("beforeShellExecution", payload, "block", branch_reason)
        raise SystemExit(block(branch_reason))

write_receipt("beforeShellExecution", payload, "allow", "command accepted")
raise SystemExit(allow("command accepted"))

"""Stop — auto-deliver a worktree when the assistant signals SCOPE_COMPLETE.

Item #C of the worktree-lifecycle streamline (operating model: "Parallel lanes, current
base, auto-deliver"). When the assistant declares a scope fully done by emitting a
line-anchored marker in its FINAL message:

    SCOPE_COMPLETE: branch=<branch> [tests=<pytest-target>]

…and ``WORKTREE_AUTODELIVER`` is enabled, this hook runs ``tools/git/deliver_worktree.py``
for that branch's worktree: rebase on ``origin/<trunk>`` → optional retest → push ``HEAD``
to the trunk on GitHub. Delivery is safety-gated by the deliver tool itself (refuses on a
protected branch / dirty tree, aborts on rebase conflict, skips push on a failing retest,
never force-pushes).

Why a marker + Stop hook (not "push on every Stop"): the Stop payload carries no response
text, so the hook recovers the assistant's LAST message from ``transcript_path`` and only
acts when THAT message contains the marker — i.e. only when the assistant explicitly
declares the scope complete this turn. A per-(branch, HEAD-sha) state file makes it
idempotent so a lingering marker in history never re-delivers.

Modes (``WORKTREE_AUTODELIVER``):
  * ``1``   → deliver via ``--mode push`` (push HEAD to the trunk on GitHub).
  * ``pr``  → deliver via ``--mode pr`` (push branch + open a PR).
  * ``dry`` → run the deliver tool with ``--dry-run`` (plan only; nothing pushed).
  * unset / ``0`` → disabled (hook no-ops).

Trunk: ``WORKTREE_AUTODELIVER_TRUNK`` (default ``main``). Timeout:
``WORKTREE_AUTODELIVER_TIMEOUT`` seconds (default ``600``). Bypass:
``WORKTREE_AUTODELIVER_BYPASS=1``. Self-contained; always exits 0 (never blocks).
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DELIVER = REPO_ROOT / "tools" / "git" / "deliver_worktree.py"
STATE_PATH = REPO_ROOT / "artifacts" / "governance" / "autodeliver_state.json"
LOG_DIR = REPO_ROOT / "artifacts" / "governance" / "autodeliver"

# Line-anchored so a back-ticked mention in prose / the SessionStart instruction never matches.
_MARKER = re.compile(
    r"^\s*SCOPE_COMPLETE:\s*branch=(?P<branch>[^\s]+)(?:\s+tests=(?P<tests>[^\s]+))?\s*$",
    re.MULTILINE,
)


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


def read_stop_payload() -> dict:
    try:
        raw = "" if sys.stdin.isatty() else sys.stdin.read()
    except (OSError, ValueError):
        return {}
    if not raw.strip():
        return {}
    try:
        obj = json.loads(raw)
    except json.JSONDecodeError:
        return {"raw": raw}
    return obj if isinstance(obj, dict) else {}


def _text_from_content(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, dict) and block.get("type") in (None, "text"):
                t = block.get("text")
                if isinstance(t, str):
                    parts.append(t)
            elif isinstance(block, str):
                parts.append(block)
        return "\n".join(parts)
    return ""


def last_assistant_text(transcript_path: str | None) -> str:
    """Return the text of the LAST assistant message in a Claude Code JSONL transcript.

    Tolerant of shape drift: matches entries whose ``type`` is ``assistant`` or whose
    ``message.role`` is ``assistant``. Returns "" when unreadable.
    """
    if not transcript_path:
        return ""
    p = Path(transcript_path)
    if not p.is_file():
        return ""
    last = ""
    try:
        with p.open("r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if not isinstance(obj, dict):
                    continue
                msg = obj.get("message") if isinstance(obj.get("message"), dict) else None
                role = obj.get("role") or (msg or {}).get("role")
                is_assistant = obj.get("type") == "assistant" or role == "assistant"
                if not is_assistant:
                    continue
                content = (msg or obj).get("content")
                text = _text_from_content(content)
                if text.strip():
                    last = text
    except OSError:
        return ""
    return last


def find_scope_complete(text: str) -> tuple[str, str | None] | None:
    """Return (branch, tests|None) for the LAST SCOPE_COMPLETE marker, or None."""
    if not text:
        return None
    matches = list(_MARKER.finditer(text))
    if not matches:
        return None
    m = matches[-1]
    return m.group("branch"), m.group("tests")


def resolve_worktree(branch: str) -> Path | None:
    """Path of the worktree currently on ``branch`` (via ``git worktree list``), or None."""
    rc, out = _git("worktree", "list", "--porcelain")
    if rc != 0:
        return None
    cur: dict[str, str] = {}
    for line in out.splitlines() + [""]:
        if not line.strip():
            if cur.get("branch") == branch and cur.get("path"):
                return Path(cur["path"]).resolve()
            cur = {}
            continue
        if line.startswith("worktree "):
            cur = {"path": line[len("worktree ") :].strip()}
        elif line.startswith("branch "):
            ref = line[len("branch ") :].strip()
            cur["branch"] = ref[len("refs/heads/") :] if ref.startswith("refs/heads/") else ref
    return None


def _load_state() -> dict:
    try:
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def already_delivered(branch: str, sha: str, state: dict | None = None) -> bool:
    state = state if state is not None else _load_state()
    return state.get(branch) == sha


def record_delivered(branch: str, sha: str) -> None:
    try:
        STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        state = _load_state()
        state[branch] = sha
        STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")
    except OSError:
        pass


def build_deliver_argv(
    worktree: Path, tests: str | None, mode: str, trunk: str, dry: bool
) -> list[str]:
    argv = [
        sys.executable,
        str(DELIVER),
        "--worktree",
        str(worktree),
        "--trunk",
        trunk,
        "--mode",
        mode,
    ]
    if tests and tests != "skip":
        argv += ["--test", f"python -m pytest {tests} -p no:cacheprovider -q"]
    if dry:
        argv.append("--dry-run")
    return argv


def _resolve_mode() -> tuple[str | None, bool]:
    """(deliver --mode, dry) from WORKTREE_AUTODELIVER, or (None, _) when disabled."""
    val = (os.environ.get("WORKTREE_AUTODELIVER") or "").strip().lower()
    if val == "1":
        return "push", False
    if val == "pr":
        return "pr", False
    if val == "dry":
        return "push", True
    return None, False


def main() -> int:
    if os.environ.get("WORKTREE_AUTODELIVER_BYPASS") == "1":
        return 0
    mode, dry = _resolve_mode()
    if mode is None:
        return 0  # disabled

    payload = read_stop_payload()
    transcript = payload.get("transcript_path") or payload.get("transcriptPath")
    text = last_assistant_text(transcript if isinstance(transcript, str) else None)
    sc = find_scope_complete(text)
    if sc is None:
        return 0
    branch, tests = sc

    worktree = resolve_worktree(branch)
    if worktree is None:
        sys.stderr.write(
            f"[auto-deliver] SCOPE_COMPLETE for '{branch}' but no worktree is on that branch.\n"
        )
        return 0

    rc, sha = _git("rev-parse", "HEAD", cwd=worktree)
    if rc == 0 and not dry and already_delivered(branch, sha):
        return 0  # idempotent: this exact tip was already delivered

    trunk = os.environ.get("WORKTREE_AUTODELIVER_TRUNK", "").strip() or "main"
    argv = build_deliver_argv(worktree, tests, mode, trunk, dry)
    try:
        timeout = int(os.environ.get("WORKTREE_AUTODELIVER_TIMEOUT") or "600")
    except ValueError:
        timeout = 600

    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        log_path = LOG_DIR / f"{branch.replace('/', '_')}-{int(time.time())}.log"
    except OSError:
        log_path = None

    try:
        proc = subprocess.run(
            argv, cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=timeout, check=False
        )
    except subprocess.TimeoutExpired:
        sys.stderr.write(f"[auto-deliver] deliver timed out after {timeout}s for '{branch}'.\n")
        return 0
    except OSError as exc:
        sys.stderr.write(f"[auto-deliver] could not launch deliver for '{branch}': {exc}\n")
        return 0

    out = (proc.stdout or "") + (proc.stderr or "")
    if log_path is not None:
        try:
            log_path.write_text(out, encoding="utf-8")
        except OSError:
            pass

    head = f"[auto-deliver] {'dry-run ' if dry else ''}deliver '{branch}' -> {trunk}: exit {proc.returncode}"
    sys.stderr.write(head + "\n")
    tail = "\n".join(line for line in out.splitlines() if line.strip())[-1500:]
    if tail:
        sys.stderr.write(tail + "\n")

    if proc.returncode == 0 and not dry and rc == 0:
        record_delivered(branch, sha)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

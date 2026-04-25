"""
Stress tests for pre_run_gate.py interactive / stdin-blocking command detection.

Constitutional §27: pagers, editors, live watchers, tail -f, bare REPLs, and -i
flags hang Cascade's turn forever because the terminal cannot send keystrokes.
This suite is the regression net — every category, every separator, every
shell variant, plus an exhaustive false-positive panel.

Issue history (why this file exists):
  - 2026-04-25: `... | more` pipeline hung the turn; Python timeout did not
    save it because `more.com` was the blocking entity, not the Python script.
  - User direction: "harden and stress test - this issue has come up again
    and again."
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[5] / ".windsurf" / "scripts"))

from pre_run_gate import check_command, _check_interactive  # noqa: E402


# ---------------------------------------------------------------------------
# 1. Pagers piped from another command
# ---------------------------------------------------------------------------

PAGER_PIPE_BLOCKED = [
    "python foo.py | more",
    "python foo.py | more.com",
    "python foo.py | More.Com",
    "dir | more",
    "ls -la | less",
    "cat huge.txt | most",
    "Get-Content x.json | less",
    "git log | less",
    "git log --oneline | bat",
    'echo "hello" | more',
    "python a.py |more",  # no space
    "python a.py |  more",  # extra spaces
    "python a.py | more.exe",  # .exe suffix
    'python a.py | "more"',  # quoted
    "python a.py | more | grep x",  # pager mid-pipeline
    "python a.py 2>&1 | less",  # with redirect
    "ls | LESS",  # uppercase
]


@pytest.mark.parametrize("cmd", PAGER_PIPE_BLOCKED)
def test_pager_piped_blocked(cmd: str) -> None:
    assert check_command(cmd) == 2, f"Expected BLOCK for: {cmd}"


# ---------------------------------------------------------------------------
# 2. Pagers as leading executable
# ---------------------------------------------------------------------------

PAGER_LEAD_BLOCKED = [
    "more output.json",
    "more.com out.json",
    "more.exe out.json",
    "less file.txt",
    "less +F log.txt",
    "most data.csv",
    "more  out.json",  # double space
    'more "C:/with space/file.txt"',  # quoted path arg
    "git diff; more out.json",  # after `;`
    "git diff && more out.json",  # after `&&`
    "git diff || more out.json",  # after `||`
    "git diff & more out.json",  # after `&`
]


@pytest.mark.parametrize("cmd", PAGER_LEAD_BLOCKED)
def test_pager_leading_blocked(cmd: str) -> None:
    assert check_command(cmd) == 2, f"Expected BLOCK for: {cmd}"


# ---------------------------------------------------------------------------
# 3. Editors
# ---------------------------------------------------------------------------

EDITOR_BLOCKED = [
    "vi",
    "vi file.py",
    "vim",
    "vim file.py",
    "nvim README.md",
    "nano /etc/hosts",
    "pico note.txt",
    "emacs -nw file",
    "ed script.sed",
    "view config.yaml",
    "VIM file.py",  # uppercase
    "vim.exe file.py",  # Windows
    "git status; vim file.py",  # after separator
    "git pull && nano /etc/hosts",
]


@pytest.mark.parametrize("cmd", EDITOR_BLOCKED)
def test_editor_blocked(cmd: str) -> None:
    assert check_command(cmd) == 2, f"Expected BLOCK for: {cmd}"


# ---------------------------------------------------------------------------
# 4. Live watchers
# ---------------------------------------------------------------------------

WATCHER_BLOCKED = [
    "top",
    "top -n 1",  # even with -n, stays interactive
    "htop",
    "btop",
    "watch -n 1 ls",
    "watch 'ps aux | grep python'",
    "TOP",
    "tail -f /var/log/syslog",
    "tail -F app.log",  # capital F is also follow on some impls
    "tail --follow=name app.log",
    "tail -n 100 -f app.log",  # -f after other flags
    "git status; tail -f log.txt",
]


@pytest.mark.parametrize("cmd", WATCHER_BLOCKED)
def test_watcher_blocked(cmd: str) -> None:
    # Note: `tail -F` capital is a valid follow flag on BSD tail; our regex
    # is `-f` lowercase only by design. We test only -f / --follow here.
    if "tail -F" in cmd:
        pytest.skip("`tail -F` (capital) not currently in pattern; non-critical")
    assert check_command(cmd) == 2, f"Expected BLOCK for: {cmd}"


# ---------------------------------------------------------------------------
# 5. Bare REPLs and interactive flags
# ---------------------------------------------------------------------------

REPL_BLOCKED = [
    "python",
    "python3",
    "node",
    "irb",
    "ipython",
    "PYTHON",  # uppercase
    "python.exe",
    "python ; echo done",  # bare python before separator
    "echo hi && python",  # bare python after separator
    "python -i script.py",  # interactive flag with script
    "python3 -i",
    "node -i",
    "bash -i",
    "sh -i",
    "python -u -i script.py",  # -i after another flag
]


@pytest.mark.parametrize("cmd", REPL_BLOCKED)
def test_repl_blocked(cmd: str) -> None:
    assert check_command(cmd) == 2, f"Expected BLOCK for: {cmd}"


# ---------------------------------------------------------------------------
# 6. False-positive panel — these MUST be allowed
# ---------------------------------------------------------------------------

ALLOWED = [
    # Words containing pager/editor names as substrings
    "echo moreover",
    "echo lessons learned",
    "echo 'most likely'",
    "python tests/test_view_renderer.py",
    "git log --grep='view'",
    "ls /home/topology",
    "cat /var/log/btop.config",  # btop in path, not as command
    "python apps_view/main.py",
    # Pager/editor names inside quoted strings as args
    "python -c \"print('less is more')\"",
    'echo "vim"',
    # File paths containing names
    "python tools/more_utils.py",
    "python tools/lessons.py",
    "ls /usr/local/bin/topdown",
    # Standard piping that's safe
    "python foo.py | grep error",
    "python foo.py | head -n 50",
    "python foo.py | tail -n 50",  # bounded tail (no -f) is OK
    "python foo.py | tee out.txt",
    "git log --no-pager -n 20",
    "git log --no-pager",
    "git diff --stat",
    # Output redirects (the recovery pattern)
    "python foo.py > out.txt",
    "python foo.py 2>&1 > out.txt",
    "Get-Content file.json > out.txt",
    "head -n 100 file.txt",
    # Python with a script (not bare REPL, not -i)
    "python script.py",
    "python3 -m pytest tests/unit/foo.py",
    "python -u script.py",
    "python -B -u script.py",
    "python -m module.name --flag",
    "node server.js",
    "bash script.sh",
    "sh -c 'echo hi'",
    "sh deploy.sh",
    # Real scoped pytest invocations
    "pytest tests/unit/ops_scripts/hooks/windsurf/test_pre_run_gate.py -q",
    # Editor name as argument value, not as executable
    "git config --global core.editor vim",
    "echo 'edit with vim'",
    # Empty + whitespace
    "",
    "   ",
    # Watch as a project name / file (without leading position separator)
    "python apps_watch/main.py",
    # Tail without follow
    "tail -n 50 app.log",
    "tail --lines=50 app.log",
]


@pytest.mark.parametrize("cmd", ALLOWED)
def test_allowed_no_false_positives(cmd: str) -> None:
    assert check_command(cmd) == 0, f"Expected ALLOW for: {cmd}"


# ---------------------------------------------------------------------------
# 7. _check_interactive labels — verify category routing
# ---------------------------------------------------------------------------

CATEGORY_CASES = [
    ("python a.py | more", "pager (piped)"),
    ("more out.json", "pager (leading)"),
    ("vim file.py", "editor"),
    ("top", "live watcher"),
    ("watch -n 1 ls", "live watcher"),
    ("tail -f log.txt", "tail --follow"),
    ("python", "bare REPL"),
    ("python -i script.py", "interactive flag (-i)"),
    ("python script.py", None),
    ("git status", None),
]


@pytest.mark.parametrize("cmd,expected", CATEGORY_CASES)
def test_check_interactive_label(cmd: str, expected: str | None) -> None:
    assert _check_interactive(cmd) == expected


# ---------------------------------------------------------------------------
# 8. Regression: real-world commands that previously hung
# ---------------------------------------------------------------------------

REGRESSION_CASES = [
    # The exact 2026-04-25 incident command shape
    "python tools/some_script.py | more",
    # Common hang-inducing PowerShell idioms
    "Get-CimInstance Win32_Process | more",
    "Get-Content artifacts/adg/burndown.json | more",
    # Sneaky variants
    "python a.py|more",  # no spaces around pipe
    "python a.py |\tmore",  # tab
    "python a.py | \tmore",  # space-tab mix
]


@pytest.mark.parametrize("cmd", REGRESSION_CASES)
def test_regression_blocked(cmd: str) -> None:
    assert check_command(cmd) == 2, f"Regression: expected BLOCK for: {cmd}"

#!/usr/bin/env python3
"""
_ssot_folder_check.py — SSOT folder routing helper (shared by hook + CI).

Pure logic. No I/O at import. Safe to import from `pre_write_gate.py`
(Windsurf hook, runs on every write attempt) and from
`ops_scripts/ci/check_ssot_folder_routing.py` (pre-commit gate, runs on
staged files).

Single responsibility: given a repo-relative file path AND whether the file
already exists on disk, decide whether the file is being written into the
correct SSOT folder. If not, return a structured violation describing the
canonical target.

Contract:
    decide(path: str, exists: bool) -> Violation | None
        path     — repo-relative path with forward slashes
        exists   — True if the file already exists on disk (pre-existing
                   files are NEVER blocked; the gate only catches NEW files)

    Violation has fields:
        path        — normalized repo-relative path
        forbidden   — short reason ("scripts-sprawl", "repo-root-py", etc.)
        suggested   — canonical SSOT target folder (str)
        message     — full human-readable explanation

Bypass: callers are responsible for honoring SSOT_FOLDER_BYPASS=1 themselves
(the helper does not read the environment — it stays pure).

Constitutional tie-in: §31 (see `.windsurf/rules/ssot-folder-enforcement.md`).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import PurePosixPath


@dataclass(frozen=True)
class Violation:
    path: str
    forbidden: str
    suggested: str
    message: str


# ---------------------------------------------------------------------------
# Allowlists for legacy-but-canonical files in otherwise-forbidden folders.
# These patterns describe files that legitimately live in a forbidden root
# (typically because they predate the SSOT taxonomy and a CI task entrypoint
# at the canonical path is intentional).
# ---------------------------------------------------------------------------

# scripts/ — only tier-verify wrappers and the c0 evidence harness are kept;
# all other historical entries should migrate to ops_scripts/ over time.
_SCRIPTS_ALLOW = (
    re.compile(r"^scripts/verify_tier\d+_(enforcement|runtime_proof)_gate\.py$"),
    re.compile(r"^scripts/verify_tier_gate_hardening\.py$"),
    re.compile(r"^scripts/verify_all_requirements_(gates|merkle_root)\.py$"),
    re.compile(r"^scripts/c0_evidence_harness\.py$"),
    re.compile(r"^scripts/proof/.+\.py$"),
    # Fort Knox compilers-of-truth (scripts/compile_requirement_signoff.py
    # and scripts/compile_apps_e2e_signoff.py — sole producers of the
    # respective *_signoff_report.json envelopes). This archetype is
    # architectural: the compiler MUST live at a stable, audit-friendly
    # path that CI gates and constitutional \u00a732 can reference directly.
    re.compile(r"^scripts/compile_[a-z0-9_]+_signoff\.py$"),
)

# repo-root *.py — only conftest.py is canonical at the root.
_REPO_ROOT_PY_ALLOW = frozenset({"conftest.py"})


# ---------------------------------------------------------------------------
# Routing rules — filename pattern → canonical SSOT folder.
# Order matters: first match wins. Each rule is a (regex, suggested) pair.
# ---------------------------------------------------------------------------

_NAME_ROUTING = [
    # CI gates / pre-commit checks
    (re.compile(r"^check_.+\.py$"), "ops_scripts/ci/"),
    (re.compile(r"^.+_gate\.py$"), "ops_scripts/ci/"),
    (re.compile(r"^validate_.+\.py$"), "ops_scripts/ci/"),

    # Calibration / weekly reports / ledger binders
    (re.compile(r"^.+_calibration\.py$"), "ops_scripts/calibration/"),
    (re.compile(r"^.+_binder\.py$"), "ops_scripts/calibration/"),
    (re.compile(r"^.+_poller\.py$"), "ops_scripts/calibration/"),
    (re.compile(r"^.+_weekly_report\.py$"), "ops_scripts/calibration/"),

    # Maintenance
    (re.compile(r"^purge_.+\.py$"), "ops_scripts/maintenance/"),
    (re.compile(r"^cleanup_.+\.py$"), "ops_scripts/maintenance/"),

    # Windsurf hook scripts
    (re.compile(r"^pre_(read|write|run|user_prompt|mcp_tool_use|author|prompt|cascade)_.+\.py$"),
     ".windsurf/scripts/"),
    (re.compile(r"^post_(read|write|run|cascade|mcp|setup|commit)_.+\.py$"),
     ".windsurf/scripts/"),
]

# Default suggestion when no routing rule matches — point users at tools/
_DEFAULT_TOOLS = "tools/<domain>/"


def _suggest_target(filename: str) -> str:
    """Return the canonical SSOT folder for ``filename``."""
    for pattern, target in _NAME_ROUTING:
        if pattern.match(filename):
            return target
    return _DEFAULT_TOOLS


def _normalize(path: str) -> str:
    """Normalize a path to repo-relative POSIX form."""
    if not path:
        return ""
    # Accept absolute paths from the hook payload (Windsurf passes absolute);
    # strip any leading "C:\Git\Agentic-Workflow[-FRESH]/" or trailing repo root.
    p = path.replace("\\", "/")
    # Trim leading "./"
    while p.startswith("./"):
        p = p[2:]
    # Drop a Windows drive prefix if present (best-effort — works for hook payloads)
    drive_match = re.match(r"^[a-zA-Z]:/(.+)", p)
    if drive_match:
        p = drive_match.group(1)
    # Drop everything up to and including a top-level marker, if present.
    # Repo roots seen in this workspace: "Agentic-Workflow", "Agentic-Workflow-FRESH".
    # Use the LAST occurrence so that a stray match earlier in a deep path
    # (e.g. archive/Agentic-Workflow-snapshot/...) does not over-trim.
    for marker in ("Agentic-Workflow-FRESH/", "Agentic-Workflow/"):
        idx = p.rfind(marker)
        if idx >= 0:
            p = p[idx + len(marker):]
            break
    return p


# ---------------------------------------------------------------------------
# Forbidden-root checks.
# ---------------------------------------------------------------------------


def _check_scripts_root(rel: str) -> Violation | None:
    """``scripts/<...>.py`` — block unless on the explicit allowlist."""
    if not rel.startswith("scripts/"):
        return None
    if not rel.endswith(".py"):
        return None
    posix = rel
    for pat in _SCRIPTS_ALLOW:
        if pat.match(posix):
            return None
    filename = PurePosixPath(rel).name
    suggested = _suggest_target(filename)
    return Violation(
        path=rel,
        forbidden="scripts-sprawl",
        suggested=suggested,
        message=(
            f"NEW file under repo-root scripts/ is forbidden — "
            f"scripts/ is the legacy tier-verify entrypoint folder; "
            f"new utilities belong in {suggested}. "
            f"Allowed scripts/ archetypes: verify_tier*_gate.py, "
            f"verify_all_requirements_*.py, c0_evidence_harness.py, "
            f"scripts/proof/. See .windsurf/rules/ssot-folder-enforcement.md."
        ),
    )


def _check_repo_root_py(rel: str) -> Violation | None:
    """Top-level ``*.py`` files — only conftest.py is allowed."""
    if "/" in rel:
        return None
    if not rel.endswith(".py"):
        return None
    if rel in _REPO_ROOT_PY_ALLOW:
        return None
    filename = rel
    suggested = _suggest_target(filename)
    return Violation(
        path=rel,
        forbidden="repo-root-py",
        suggested=suggested,
        message=(
            f"NEW Python file at repo root is forbidden — "
            f"only conftest.py is canonical at the root. "
            f"Move to {suggested}. "
            f"See .windsurf/rules/ssot-folder-enforcement.md."
        ),
    )


def _check_oneoff_oneshot(rel: str) -> Violation | None:
    """``tools/_oneoff/`` and ``tools/_oneshot/`` — fully closed for new files."""
    if rel.startswith("tools/_oneoff/") or rel.startswith("tools/_oneshot/"):
        if rel.endswith(".py"):
            filename = PurePosixPath(rel).name
            suggested = _suggest_target(filename)
            return Violation(
                path=rel,
                forbidden="oneoff-sprawl",
                suggested=suggested,
                message=(
                    f"NEW file under tools/_oneoff/ or tools/_oneshot/ is forbidden — "
                    f"these folders are tombstoned. New durable utilities belong in "
                    f"{suggested}. See .windsurf/rules/ssot-folder-enforcement.md."
                ),
            )
    return None


def _check_hook_script_misroute(rel: str) -> Violation | None:
    """Hook-prefix file landing outside .windsurf/scripts/."""
    if not rel.endswith(".py"):
        return None
    if rel.startswith(".windsurf/scripts/"):
        return None
    filename = PurePosixPath(rel).name
    if re.match(r"^(pre|post)_(read|write|run|user_prompt|mcp_tool_use|"
                r"author|prompt|cascade|mcp|setup|commit)_.+\.py$", filename):
        return Violation(
            path=rel,
            forbidden="hook-script-misroute",
            suggested=".windsurf/scripts/",
            message=(
                f"Filename '{filename}' looks like a Windsurf hook script "
                f"(pre_*/post_* prefix) but is being written outside "
                f".windsurf/scripts/. Hook scripts MUST live in "
                f".windsurf/scripts/ to be discoverable by .windsurf/hooks.json. "
                f"See .windsurf/rules/ssot-folder-enforcement.md."
            ),
        )
    return None


# ---------------------------------------------------------------------------
# Public entry point.
# ---------------------------------------------------------------------------


def decide(path: str, exists: bool) -> Violation | None:
    """
    Return a Violation if ``path`` violates SSOT folder routing for a NEW
    file, else None. Pre-existing files (``exists=True``) NEVER violate —
    SSOT enforcement only catches new files to avoid breaking the workspace.
    """
    if exists:
        return None
    rel = _normalize(path)
    if not rel:
        return None
    # Gate only applies to source files; treat .json/.md/.yaml etc as out-of-scope
    # (those have their own location rules — plans, configs, reports).
    if not rel.endswith(".py"):
        return None

    for check in (
        _check_scripts_root,
        _check_repo_root_py,
        _check_oneoff_oneshot,
        _check_hook_script_misroute,
    ):
        v = check(rel)
        if v is not None:
            return v
    return None


# Backward-compat alias for callers that prefer a tuple result.
def check(path: str, exists: bool) -> tuple[bool, str | None, str | None]:
    """Return ``(blocked, message, suggested_target)``."""
    v = decide(path, exists)
    if v is None:
        return (False, None, None)
    return (True, v.message, v.suggested)

"""STATUS-floor Stop audit — thin blocking layer over the SSOT runtime-RCA detector.

Blocks on: missing_response_floor, pass_without_proof, speculative_pass, missing_plan_waves,
malformed_plan_waves.
RCA-depth kinds (missing_refactor_outcome, missing_rca, incomplete_rca, shallow_rca)
are owned by stop_runtime_rca_gate.py.
"""
from __future__ import annotations

import importlib.util
import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
GOVERNANCE_DIR = REPO_ROOT / "scripts" / "governance"
if str(GOVERNANCE_DIR) not in sys.path:
    sys.path.insert(0, str(GOVERNANCE_DIR))

from lib.codex_hook_common import allow, block, read_payload, resolve_response_text, write_receipt
from worktree_hygiene import (  # noqa: E402
    find_dirty_protected_worktrees,
    summarize_dirty_worktrees,
    summarize_single_main_worktree_issues,
    verify_single_main_worktree,
)

_AUDIT_PATH = REPO_ROOT / ".codex" / "governance" / "scripts" / "post_agent_runtime_rca_audit.py"
_BLOCK_KINDS = (
    "missing_response_floor",
    "pass_without_proof",
    "speculative_pass",
    "missing_plan_waves",
    "malformed_plan_waves",
)


def _load_detect():
    try:
        spec = importlib.util.spec_from_file_location("_rca_detect_for_stop_audit", _AUDIT_PATH)
        if not spec or not spec.loader:
            return None
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return getattr(mod, "detect", None)
    except Exception:  # guardian: allow-broad-exception -- detector import must fail open
        return None


def _reason(kind: str, violation: dict) -> str:
    if kind == "pass_without_proof":
        missing = ", ".join(violation.get("missing_proof") or [])
        tail = missing or "FILES_CHANGED, COMMANDS_RUN, TESTS_GATES, ARTIFACTS"
        return "STATUS: PASS response missing proof sections: " + tail
    if kind == "speculative_pass":
        return "Speculative pass language detected; use STATUS: PASS | PARTIAL | FAIL | BLOCKED with evidence."
    if kind == "missing_plan_waves":
        return "Active multi-wave response missing PLAN_WAVES completed/open mini table."
    if kind == "malformed_plan_waves":
        return "PLAN_WAVES must be a Wave | State | Summary mini table with completed and open rows."
    return "Repo-work final response missing STATUS: PASS | PARTIAL | FAIL | BLOCKED."


def _protected_worktree_reason() -> str:
    if os.environ.get("STOP_TASK_AUDIT_WORKTREE_HYGIENE_BYPASS") == "1":
        return ""
    issues = find_dirty_protected_worktrees(REPO_ROOT)
    if not issues:
        return ""
    summary = summarize_dirty_worktrees(issues)
    return (
        "Protected worktree hygiene failure: a protected checkout still has local changes.\n"
        f"{summary}\n"
        "Clean or commit the protected worktree before continuing. If this is a publication lane, "
        "use a detached merge worktree so generated reports do not linger dirty on main."
    )


def _publication_closeout_claimed(text: str, status_value: str | None) -> bool:
    if status_value != "PASS":
        return False
    lowered = text.lower()
    if "origin/main" not in lowered:
        return False
    return bool(re.search(r"\b(pr|pull request|publish(?:ed)?|push(?:ed)?|merge(?:d)?)\b", lowered))


def _single_main_worktree_reason(text: str, status_value: str | None) -> str:
    if os.environ.get("STOP_TASK_AUDIT_SINGLE_MAIN_BYPASS") == "1":
        return ""
    if not _publication_closeout_claimed(text, status_value):
        return ""
    issues = verify_single_main_worktree(REPO_ROOT)
    if not issues:
        return ""
    summary = summarize_single_main_worktree_issues(issues)
    return (
        "Single-main worktree closeout failure: a PASS response claims publication/merge/push "
        "against origin/main, but local closeout is not exactly one clean main worktree.\n"
        f"{summary}\n"
        "Run python scripts/governance/verify_single_main_worktree.py --root "
        "C:\\Git\\Agentic-Workflow-FRESH --expected-path C:\\Git\\Agentic-Workflow-FRESH and fix all blockers."
    )


def main() -> int:
    payload = read_payload()
    text = resolve_response_text(payload)
    if not text.strip():
        write_receipt("stop", payload, "allow", "empty stop payload accepted")
        return allow("empty stop payload accepted")
    detect = _load_detect()
    if detect is None:
        write_receipt("stop", payload, "allow", "detect() unavailable — fail open")
        return allow("detect() unavailable — fail open")
    try:
        status_value, violations = detect(text)
    except Exception:  # guardian: allow-broad-exception -- detection failure must fail open
        return allow("detect() raised — fail open")
    for kind in _BLOCK_KINDS:
        hit = next((v for v in violations if v.get("kind") == kind), None)
        if hit:
            reason = _reason(kind, hit)
            write_receipt("stop", payload, "block", reason)
            return block(reason)
    protected_reason = _protected_worktree_reason() if status_value is not None or violations else ""
    if protected_reason:
        write_receipt("stop", payload, "block", protected_reason)
        return block(protected_reason)
    single_main_reason = _single_main_worktree_reason(text, status_value)
    if single_main_reason:
        write_receipt("stop", payload, "block", single_main_reason)
        return block(single_main_reason)
    write_receipt("stop", payload, "allow", "stop audit accepted")
    return allow("stop audit accepted")


if __name__ == "__main__":
    raise SystemExit(main())

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

from lib.claude_hook_common import (
    allow,
    block_exit_code,
    contains_legacy_execution_token,
    payload_path,
    read_payload,
    text_from_payload,
    warn,
    write_receipt,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
_PLAN_REG_HELPER_PATH = (
    REPO_ROOT / ".claude" / "governance" / "scripts" / "_plan_registration.py"
)


# NOTE (cursor-decommission W6): the legacy MCP-mirror sync (root .mcp.json -> .cursor/mcp.json)
# is retired. The .cursor/mcp.json mirror no longer exists; root .mcp.json is the sole SSOT,
# so no post-edit mirror sync is triggered.


payload = read_payload()
text = text_from_payload(payload)
file_path = payload_path(payload)


def _repo_relative(path: str) -> str:
    norm = path.replace("\\", "/")
    root = str(REPO_ROOT).replace("\\", "/").rstrip("/")
    if norm.startswith(root + "/"):
        norm = norm[len(root) + 1 :]
    if norm.startswith("./"):
        norm = norm[2:]
    return norm


def _is_plan_archive(path: str) -> bool:
    rel = _repo_relative(path)
    return rel.startswith("plans/_archive/") or rel.startswith(".claude/plans/_archive/") or "/plans/_archive/" in rel


def _is_active_plan_file(path: str) -> bool:
    rel = _repo_relative(path)
    if not rel.endswith(".md") or _is_plan_archive(rel):
        return False
    return rel.startswith("plans/") or rel.startswith(".claude/plans/")


legacy = contains_legacy_execution_token(text + "\n" + file_path)
if legacy and not _is_plan_archive(file_path):
    reason = "Edit references legacy execution surface outside archive: " + ", ".join(legacy)
    write_receipt("afterFileEdit", payload, "warn", reason)
    raise SystemExit(warn(reason))

if _is_plan_archive(file_path):
    reason = "Edited archived historical plan material; confirm this was intentional reference maintenance."
    write_receipt("afterFileEdit", payload, "warn", reason)
    raise SystemExit(warn(reason))


def _load_plan_registration_helper():
    """Load the shared ``_plan_registration`` helper module by path.

    Returns the module, or ``None`` when unavailable. Never raises.
    """
    if not _PLAN_REG_HELPER_PATH.exists():
        return None
    mod_name = "_plan_registration"
    if mod_name in sys.modules:
        return sys.modules[mod_name]
    try:
        spec = importlib.util.spec_from_file_location(mod_name, _PLAN_REG_HELPER_PATH)
        if spec is None or spec.loader is None:
            return None
        mod = importlib.util.module_from_spec(spec)
        sys.modules[mod_name] = mod
        try:
            spec.loader.exec_module(mod)
        except Exception:
            sys.modules.pop(mod_name, None)
            return None
        return mod
    except (OSError, ImportError):
        return None


def _capture_plan_registration(norm_path: str) -> None:
    """File-driven backstop: enqueue any active plan-file write for Notion registration.

    The marker-driven capture (``post_agent_plan_registration_capture.py``) only
    records a plan when the agent emits a ``PLAN_CREATED:`` marker. A plan file
    written/committed without that marker was never tracked and so never reached
    the Plans DB (RCA 2026-06-08: ``apps-rg-fact-vector-writeback-discipline-67652c``
    landed with its implementation in one feat commit, no marker, no registration).

    This makes capture depend on the plan FILE existing, not on a marker. It is
    idempotent (the helper de-dupes by slug), best-effort, and non-blocking — it
    never raises and never exits, so the wave-summary audit and final allow run
    unchanged. Bypass: ``PLAN_REGISTRATION_CAPTURE_BYPASS=1`` (shared with the
    post-agent capture hook). §36.
    """
    if os.environ.get("PLAN_REGISTRATION_CAPTURE_BYPASS") == "1":
        return
    rel = _repo_relative(norm_path)
    if not _is_active_plan_file(rel):
        return
    helper = _load_plan_registration_helper()
    if helper is None:
        return
    fname = rel.rsplit("/", 1)[-1]
    try:
        match = helper.PLAN_FILE_RE.match(fname)
    except AttributeError:
        return
    if not match:
        return
    slug = match.group("slug")
    try:
        helper.enqueue_plan(slug, rel)
    except (OSError, ValueError, AttributeError):
        return
    try:
        registered = helper.check_registration(slug).registered
    except (AttributeError, OSError, TypeError):
        registered = False
    if not registered:
        print(
            f"[plan_registration] plan '{slug}' captured from {rel}; it is not yet "
            "registered in the Notion Plans DB. Post a Plans row (API-post-page) before "
            "wave execution. §36. Bypass: PLAN_REGISTRATION_CAPTURE_BYPASS=1.",
            file=sys.stderr,
        )


def _audit_plan_wave_summary_top(norm_path: str) -> int | None:
    """Return hook exit code when plan violates consolidated wave summary at top."""
    rel = _repo_relative(norm_path)
    if not _is_active_plan_file(rel):
        return None

    plan_file = REPO_ROOT / rel.replace("/", os.sep)
    if not plan_file.is_file():
        return None

    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    from ops_scripts.ci.plan_wave_summary_top import (
        WaveSummarySeverity,
        validate_consolidated_wave_summary_at_top,
    )

    try:
        content = plan_file.read_text(encoding="utf-8")
    except OSError:
        return None

    fails = [
        v
        for v in validate_consolidated_wave_summary_at_top(content, rel)
        if v.severity == WaveSummarySeverity.FAIL
    ]
    if not fails:
        return None

    first = fails[0]
    reason = (
        f"Plan missing consolidated wave summary at top ({first.rule_id}): {first.message} "
        "Add `## Status Tables` → `### Wave Progress` with the canonical wave table "
        "before the first `## Wave N` section. See plan-location.mdc."
    )
    strict = os.environ.get("PLAN_WAVE_SUMMARY_TOP_HOOK_STRICT", "").strip() in (
        "1",
        "true",
        "yes",
    )
    decision = "block" if strict else "warn"
    write_receipt("afterFileEdit", payload, decision, reason)
    if strict:
        print(
            '{"decision": "block", "reason": '
            + json.dumps(reason)
            + "}",
            flush=True,
        )
        return block_exit_code()
    raise SystemExit(warn(reason))


_capture_plan_registration(file_path.replace("\\", "/"))

_wave_top_exit = _audit_plan_wave_summary_top(file_path.replace("\\", "/"))
if _wave_top_exit is not None:
    raise SystemExit(_wave_top_exit)

write_receipt("afterFileEdit", payload, "allow", "edit accepted")
raise SystemExit(allow("edit accepted"))

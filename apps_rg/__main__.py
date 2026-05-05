"""Canonical entrypoint for apps_rg — pure transport shim.

Usage:
    python -m apps_rg --target-company <company> --target-role <role>

Delegates immediately to ``agentic_core.runtime.entrypoints
.integrated_r4_deterministic_pipeline_run`` with ``app_name="apps_rg"``.

apps_rg MUST NOT:
  - resolve L2 recipe
  - construct or pass l2_callable
  - run HOPs, narrative pass, DOCX export
  - call models or build prompts
  - commit cache or write L4
  - call Exit or emit X3

All domain execution is owned by agentic_core via registered L2 step
adapters in ``apps_rg.l2_recipe.steps``.

If the agentic_core runner is unavailable, apps_rg **fails closed** (exit 1).
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
_log = logging.getLogger("apps_rg")


# ---------------------------------------------------------------------------
# Fail-closed import of the R4 deterministic pipeline runner
# ---------------------------------------------------------------------------
try:
    from agentic_core.runtime.entrypoints.integrated_r4_deterministic_pipeline_run import (
        run_integrated_r4_deterministic_pipeline,
        R4IntegratedRunResult,
    )

    _RUNNER_AVAILABLE = True
except ImportError as _import_err:
    _RUNNER_AVAILABLE = False
    _RUNNER_IMPORT_ERROR = _import_err


# ---------------------------------------------------------------------------
# Helpers — transport-level only, no domain logic
# ---------------------------------------------------------------------------


def _get_current_policy_hash() -> str:
    return os.environ.get("APPS_RG_POLICY_HASH", "policy_v1")


def _get_current_blueprint_hash() -> str:
    return os.environ.get("APPS_RG_BLUEPRINT_HASH", "blueprint_v1")


def _hash_file_content(path: Path) -> str:
    """SHA-256 of file content, first 32 hex chars."""
    if not path.exists():
        return "none"
    return hashlib.sha256(path.read_bytes()).hexdigest()[:32]


def _build_raw_request(args) -> dict[str, Any]:
    """Build the raw_request envelope from parsed CLI args.

    This dict is the contract surface between apps_rg and the R4 pipeline.
    It contains only transport-level data — no executable code.
    """
    jd_path = Path(getattr(args, "jd", "") or "apps_rg/scripts/job_description.json")
    brief_path = Path(getattr(args, "manual_brief", "") or "apps_rg/scripts/company_research.json")
    candidate_path = (
        Path(args.candidate) if getattr(args, "candidate", None) else Path("apps_rg/scripts/candidate_profile.yaml")
    )

    jd_payload: dict[str, Any] = {}
    if jd_path.exists():
        try:
            jd_payload = json.loads(jd_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass

    return {
        "transport": "cli",
        "method": "POST",
        "content_type": "application/json",
        "source_channel": "apps_rg_cli",
        "declared_schema": "apps_rg_jd_v1",
        "body_text": json.dumps(jd_payload) if jd_payload else "{}",
        "tenant_id": getattr(args, "tenant_id", "default"),
        "user_id": "u-apps_rg",
        "target_company": args.target_company or "",
        "target_role": args.target_role or "",
        "jd_payload": jd_payload,
        "jd_hash": _hash_file_content(jd_path),
        "brief_hash": _hash_file_content(brief_path),
        "resume_hash": _hash_file_content(candidate_path),
        "policy_hash": _get_current_policy_hash(),
        "blueprint_hash": _get_current_blueprint_hash(),
        "manual_brief": str(brief_path),
        "research_via": getattr(args, "research_via", None),
        "auto_research_internal": getattr(args, "auto_research_internal", False),
        "auto_research_tavily": getattr(args, "auto_research_tavily", False),
    }


# ---------------------------------------------------------------------------
# Interactive JD prompt — collects inputs from stdin when args are absent
# ---------------------------------------------------------------------------


def _prompt_jd_interactive() -> tuple[str, str, str, str]:
    """Interactively collect company, role, location, and JD text from stdin.

    Returns (company, role, location, jd_text).
    Prompts are written to stdout so they appear even when stdout is a TTY.
    """
    print("\n=== apps_rg — Resume Generator ===")
    print("Paste the job description details below.")
    print("(Tip: you can also use --target-company / --target-role / --jd flags)\n")

    company = ""
    while not company.strip():
        company = input("Target company: ").strip()

    role = ""
    while not role.strip():
        role = input("Target role title: ").strip()

    location = input("Location (optional, press Enter to skip): ").strip()

    print()
    print("Paste the full job description text.")
    print("When done, enter a line containing only '---' (three dashes) and press Enter:")
    lines: list[str] = []
    while True:
        line = input()
        if line.strip() == "---":
            break
        lines.append(line)
    jd_text = "\n".join(lines).strip()

    return company, role, location, jd_text


# ---------------------------------------------------------------------------
# Main entrypoint — pure shim
# ---------------------------------------------------------------------------


def main() -> None:
    """Parse transport args → delegate to agentic_core R4 pipeline."""

    # ── Fail-closed guard ──
    if not _RUNNER_AVAILABLE:
        print(
            f"FATAL: agentic_core runner unavailable — apps_rg fails closed.\n"
            f"  ImportError: {_RUNNER_IMPORT_ERROR}",
            file=sys.stderr,
        )
        sys.exit(1)

    import argparse

    parser = argparse.ArgumentParser(prog="apps_rg", add_help=True)
    parser.add_argument("--target-company", default=None, help="Target company")
    parser.add_argument("--target-role", default=None, help="Target role title")
    parser.add_argument("--research-via", default=None, choices=["apps_research"])
    parser.add_argument("--auto-research-internal", action="store_true")
    parser.add_argument("--auto-research-tavily", action="store_true")
    parser.add_argument("--manual-brief", default="apps_rg/scripts/company_research.json")
    parser.add_argument("--candidate", default=None, help="Candidate profile path")
    parser.add_argument("--target-level", default=None)
    parser.add_argument("--jd", default=None, help="Job description JSON path")
    args, _unknown = parser.parse_known_args()

    # ── Interactive mode when required args are absent and stdin is a TTY ──
    _interactive_jd_payload: dict[str, Any] | None = None
    if (not args.target_company or not args.target_role) and sys.stdin.isatty():
        company, role, location, jd_text = _prompt_jd_interactive()
        args.target_company = args.target_company or company
        args.target_role = args.target_role or role
        _interactive_jd_payload = {
            "title": role,
            "company": company,
            "location": location,
            "description": jd_text,
        }
    elif not args.target_company:
        parser.error("--target-company is required")
    elif not args.target_role:
        parser.error("--target-role is required")

    # ── Build request envelope (transport data only) ──
    raw_request = _build_raw_request(args)
    if _interactive_jd_payload is not None:
        raw_request["jd_payload"] = _interactive_jd_payload
        raw_request["body_text"] = json.dumps(_interactive_jd_payload)
    artifact_dir = Path("artifacts/apps_rg/runs") / f"r4_{raw_request['resume_hash'][:8]}"

    # ── Delegate to agentic_core R4 pipeline (core resolves L2 recipe) ──
    result: R4IntegratedRunResult = run_integrated_r4_deterministic_pipeline(
        app_name="apps_rg",
        raw_request=raw_request,
        artifact_dir=artifact_dir,
        policy_hash=raw_request["policy_hash"],
        blueprint_hash=raw_request["blueprint_hash"],
    )

    _log.info(
        "[apps_rg] R4 pipeline complete: run_id=%s x3=%s terminal_r5=%s fault=%s",
        result.run_id,
        result.x3_disposition,
        result.terminal_r5,
        result.fault or "(none)",
    )

    if result.fault:
        _log.error("[apps_rg] Pipeline fault: %s", result.fault)
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()

"""Canonical entrypoint for apps_lic — product runtime is canonical_dispatch only.

Usage:
    python -m apps_lic [options]

This module:
- Parses CLI args
- Builds AppsLicIngressContractV1 raw JSON
- Calls ``apps_lic.runtime.dispatch.canonical_dispatch.run_canonical_apps_lic_spine``
- Propagates exit code

Hard invariants:
- No l2_callable construction in CLI
- No direct HOP agent imports from CLI
- No YAML L2 recipe resolver
- No GovernedLicRun / integrated_r4 / symbolic cert branches
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any

import apps_lic.cert  # noqa: F401 — FEC producer side-effect registration

_DEFAULT_BRIEF_PATH = "apps_lic/scripts/_interactive_brief.json"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
_log = logging.getLogger("apps_lic")


def _parse_args(argv: list[str]) -> argparse.Namespace:
    """Parse CLI arguments into namespace."""
    parser = argparse.ArgumentParser(
        prog="apps_lic",
        description="Generate governed professional outreach drafts.",
    )
    parser.add_argument(
        "--recipient-class", type=str, default="",
        help="Target recipient class (executive, hiring_manager, etc.)",
    )
    parser.add_argument(
        "--channel", type=str, default="",
        help="Outreach channel (linkedin, email, etc.)",
    )
    parser.add_argument(
        "--outreach-mode", type=str, default="",
        help="Outreach mode (cold, warm, referral, etc.)",
    )
    parser.add_argument(
        "--manifest-id", type=str, default="",
        help="PreloadedOutreachContextManifest ID",
    )
    parser.add_argument(
        "--manifest-hash", type=str, default="",
        help="PreloadedOutreachContextManifest content hash",
    )
    parser.add_argument(
        "--policy-hash", type=str, default="",
        help="Policy binding hash",
    )
    parser.add_argument(
        "--blueprint-hash", type=str, default="",
        help="Blueprint binding hash",
    )
    parser.add_argument(
        "--request-id", type=str, default="",
        help="Explicit request ID (default: auto-generated)",
    )
    parser.add_argument(
        "--artifact-dir", type=str, default="",
        help="Directory for run artifacts",
    )
    parser.add_argument(
        "--manual-brief", type=str, default="",
        help=(
            "Path to pre-generated company/recipient briefing JSON. "
            "When provided, skips R3R4 managed workflow."
        ),
    )
    return parser.parse_args(argv)


def _load_manual_brief_text(manual_brief: str) -> str:
    """Load briefing from inline text or filesystem path."""
    if not manual_brief:
        return ""
    path = Path(manual_brief)
    if path.is_file():
        return path.read_text(encoding="utf-8")
    return manual_brief


def _allow_research_from_args(args: argparse.Namespace, manual_brief_text: str) -> bool:
    """True only when interactive wizard explicitly selected auto-research."""
    if manual_brief_text.strip():
        return False
    return bool(getattr(args, "auto_research", False))


def _emit_r5_terminal_via_exit(
    reason_code: str,
    detail: str = "",
    *,
    exit_code: int = 1,
) -> None:
    """Emit R5 terminal through Exit V6 before process exit."""
    _log.error("[apps_lic] R5 terminal: reason=%s detail=%s", reason_code, detail or "(none)")
    try:
        from agentic_core.L3_orchestration.exit_eval.v6.pipeline import ExitEvalPipeline

        exit_pipeline = ExitEvalPipeline(app_name="apps_lic")
        receipts = {
            "run_id": "",
            "request_id": "",
            "trace_root": "",
            "route_id": "R4_MANAGED_DRAFT",
            "chain_kind": "R4_MANAGED_DRAFT",
            "app_name": "apps_lic",
            "terminal_r5": True,
            "r5_reason_code": reason_code,
            "l2_executed": False,
            "timestamp_utc": "",
        }
        exit_result = exit_pipeline.run(receipts)
        _log.info("[apps_lic] Exit V6 disposition: %s", exit_result.x3_disposition.value)
    except Exception as exc:
        _log.warning("[apps_lic] Exit V6 emission failed: %s", exc)
    sys.exit(exit_code)


def _interactive_wizard(args: Any) -> None:
    """Prompt for mandatory inputs and mutate ``args`` in place."""
    from apps_shared.cli.interactive_wizard import WizardField, run_wizard  # noqa: PLC0415

    fields: list[WizardField] = []
    if not args.recipient_class:
        fields.append(WizardField(
            "recipient_class",
            "Recipient class (executive, hiring_manager, recruiter, etc.)",
            kind="string",
        ))
    if not args.channel:
        fields.append(WizardField(
            "channel",
            "Outreach channel (linkedin, email, text)",
            kind="string",
        ))
    if not args.outreach_mode:
        fields.append(WizardField(
            "outreach_mode",
            "Outreach mode (cold, warm, referral, followup)",
            kind="string",
        ))
    fields.append(
        WizardField(
            "briefing",
            "Company/recipient briefing document",
            kind="multiline_or_file_or_auto",
            choices_help=(
                "auto delegates to apps_research via L3 managed workflow; "
                "@path loads an existing JSON brief; paste JSON or freeform text"
            ),
        )
    )

    header = (
        "apps_lic interactive setup — mandatory inputs\n"
        "======================================================================\n"
        "Cascade discipline: recipient_class / channel / outreach_mode / "
        "briefing were not supplied on the command line."
    )

    values = run_wizard(
        fields,
        header=header,
        input_path=Path("apps_lic/scripts/_wizard_input.json"),
    )

    if "recipient_class" in values:
        args.recipient_class = values["recipient_class"]  # type: ignore[assignment]
    if "channel" in values:
        args.channel = values["channel"]  # type: ignore[assignment]
    if "outreach_mode" in values:
        args.outreach_mode = values["outreach_mode"]  # type: ignore[assignment]

    brief = values["briefing"]
    assert isinstance(brief, dict)
    mode = brief.get("mode")
    if mode == "auto":
        args.manual_brief = ""
        args.auto_research = True  # type: ignore[attr-defined]
        print("      → auto-research ENABLED; L3 managed workflow will produce briefing")
    elif mode == "file":
        args.manual_brief = brief.get("source")
        print(f"      → manual_brief = {args.manual_brief}")
    elif mode == "paste":
        text = brief.get("text") or ""
        try:
            brief_payload = json.loads(text)
        except json.JSONDecodeError:
            brief_payload = {
                "_source": "interactive_paste_freeform",
                "freeform_text": text,
            }
        wizard_brief_path = Path("apps_lic/scripts/_interactive_brief.json")
        wizard_brief_path.parent.mkdir(parents=True, exist_ok=True)
        wizard_brief_path.write_text(
            json.dumps(brief_payload, indent=2), encoding="utf-8",
        )
        args.manual_brief = str(wizard_brief_path)
        print(f"      → wrote briefing to {args.manual_brief}")

    print(f"Ready: recipient_class={args.recipient_class!r} channel={args.channel!r}")
    print(f"       outreach_mode={args.outreach_mode!r}")
    print(f"       brief={'auto-research' if mode == 'auto' else args.manual_brief}")
    print()


def main() -> int:
    """Product entrypoint — canonical AG-8 spine dispatch only."""
    if "--apps-e2e-live" in sys.argv:
        _log.error(
            "[apps_lic] --apps-e2e-live is removed (was symbolic cert theater). "
            "Use: python -m apps_lic with canonical_dispatch."
        )
        return 2

    args = _parse_args(sys.argv[1:])

    if not args.recipient_class or not args.channel or not args.outreach_mode or not args.manual_brief:
        _interactive_wizard(args)

    manual_brief_text = _load_manual_brief_text(args.manual_brief)
    allow_research = _allow_research_from_args(args, manual_brief_text)

    try:
        from apps_lic.runtime.dispatch.canonical_dispatch import (
            build_cli_ingress_raw,
            run_canonical_apps_lic_spine,
        )

        raw_ingress = build_cli_ingress_raw(
            request_id=args.request_id or None,
            manual_brief=manual_brief_text,
            allow_research=allow_research,
        )
        artifact_root = Path(args.artifact_dir) if args.artifact_dir else None
        result = run_canonical_apps_lic_spine(
            raw_ingress,
            artifact_root=artifact_root,
        )

        _log.info(
            "[apps_lic] Canonical spine complete: run_id=%s route_family=%s "
            "x3=%s terminal_r5=%s artifacts=%s",
            result.run_id,
            result.route_family,
            result.x3_disposition,
            result.terminal_r5,
            result.artifact_dir,
        )

        if result.terminal_r5:
            return 1
        return 0

    except Exception as exc:
        _log.error("[apps_lic] Canonical spine failed: %s", exc)
        _emit_r5_terminal_via_exit(
            reason_code="PIPELINE_EXECUTION_FAILED",
            detail=str(exc),
            exit_code=1,
        )
        return 1  # pragma: no cover


if __name__ == "__main__":
    sys.exit(main())

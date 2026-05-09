"""apps_rg — Declarative Ingress-Only Entry Point (AG-RGGOV-1)

W5-compliant ingress-only __main__.py.

Responsible ONLY for:
1. CLI/wizard input collection
2. Building AppsRgIngressPayload
3. Building RequestEnvelope  
4. Submitting to AppIngressRunner
5. Presenting Exit-approved output

NO runtime authority: no planning, routing, orchestration, execution,
provider calls, judging, disposition, or state writes.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from agentic_core.runtime.contracts.apps_rg_ingress_payload import (
    AppsRgIngressPayload,
)


def _interactive_wizard() -> dict[str, Any]:
    """Launch interactive wizard to collect inputs from user."""
    print("=" * 60)
    print("Resume Generation Wizard")
    print("=" * 60)
    print()

    inputs: dict[str, Any] = {}

    # Target context
    print("Step 1: Target Context")
    print("-" * 30)
    try:
        inputs["target_company"] = input("Target company: ").strip() or None
        inputs["target_role"] = input("Target role: ").strip() or None
        inputs["target_level"] = input("Target level (e.g., SENIOR, STAFF): ").strip() or None
    except EOFError:
        print("\nERROR: Interactive input not available. Run with CLI flags:", file=sys.stderr)
        print("  python -m apps_rg --target-company 'Company' --target-role 'Role' --source-resume 'path/to/resume.md'", file=sys.stderr)
        sys.exit(2)
    print()

    # Source resume
    print("Step 2: Source Resume")
    print("-" * 30)
    use_file = input("Use resume file? (y/n): ").strip().lower() == "y"
    if use_file:
        inputs["source_resume_ref"] = input("Resume file path: ").strip() or None
    else:
        print("Paste resume text (Ctrl+D or empty line to finish):")
        lines = []
        while True:
            try:
                line = input()
                if line.strip() == "":
                    break
                lines.append(line)
            except EOFError:
                break
        inputs["source_resume_text"] = "\n".join(lines) if lines else None
    print()

    # Job description
    print("Step 3: Job Description")
    print("-" * 30)
    use_jd_file = input("Use JD file? (y/n): ").strip().lower() == "y"
    if use_jd_file:
        inputs["job_description_ref"] = input("JD file path: ").strip() or None
    else:
        print("Paste JD text (Ctrl+D or empty line to finish):")
        lines = []
        while True:
            try:
                line = input()
                if line.strip() == "":
                    break
                lines.append(line)
            except EOFError:
                break
        inputs["job_description_text"] = "\n".join(lines) if lines else None
    print()

    # Research briefing
    print("Step 4: Research Briefing (Optional)")
    print("-" * 30)
    use_brief = input("Use pre-built research briefing? (y/n): ").strip().lower() == "y"
    if use_brief:
        inputs["manual_brief_path"] = input("Briefing file path: ").strip() or None
    else:
        auto_research = input("Auto-generate research? (y/n): ").strip().lower() == "y"
        if auto_research:
            inputs["auto_research_internal"] = True
            inputs["research_via"] = "apps_research"
    print()

    print("=" * 60)
    print("Wizard complete. Building ingress payload...")
    print("=" * 60)

    return inputs


def main() -> int:
    """Main entry point — ingress-only, no runtime authority."""
    parser = argparse.ArgumentParser(
        description="Generate tailored resume via declarative ingress"
    )
    parser.add_argument(
        "--target-company",
        type=str,
        help="Target company name",
    )
    parser.add_argument(
        "--target-role",
        type=str,
        help="Target role title",
    )
    parser.add_argument(
        "--target-level",
        type=str,
        help="Target seniority level",
    )
    parser.add_argument(
        "--source-resume",
        type=str,
        help="Path to source resume file",
    )
    parser.add_argument(
        "--source-resume-text",
        type=str,
        help="Inline source resume text",
    )
    parser.add_argument(
        "--jd",
        type=str,
        help="Path to job description JSON file",
    )
    parser.add_argument(
        "--jd-text",
        type=str,
        help="Inline job description text",
    )
    parser.add_argument(
        "--manual-brief",
        type=str,
        help="Path to pre-built research briefing JSON",
    )
    parser.add_argument(
        "--auto-research-internal",
        action="store_true",
        help="Delegate research to apps_research (internal)",
    )
    parser.add_argument(
        "--auto-research-tavily",
        action="store_true",
        help="Delegate research to Tavily web search",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="artifacts/apps_rg/runs",
        help="Output directory for generated artifacts",
    )
    parser.add_argument(
        "--idempotency-key",
        type=str,
        help="Idempotency key for request deduplication",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate inputs without executing",
    )
    parser.add_argument(
        "--wizard",
        action="store_true",
        help="Launch interactive wizard for input collection",
    )
    args = parser.parse_args()

    # Launch wizard if requested or if no args provided
    needs_wizard = args.wizard or (not args.target_company and not args.target_role and not args.source_resume)
    if needs_wizard:
        if not sys.stdin.isatty():
            print("ERROR: Interactive wizard requires a terminal (TTY).", file=sys.stderr)
            print("Run with CLI flags instead:", file=sys.stderr)
            print("  python -m apps_rg --target-company 'Company' --target-role 'Role' --source-resume 'path/to/resume.md'", file=sys.stderr)
            print("Or use --wizard flag in an interactive terminal.", file=sys.stderr)
            return 2
        wizard_inputs = _interactive_wizard()
    else:
        wizard_inputs = {}

    # Build ingress payload (declarative only)
    ingress_payload = {
        "app_id": "apps_rg",
        "task_class": "resume_generation",
        "target_company": args.target_company or wizard_inputs.get("target_company"),
        "target_role": args.target_role or wizard_inputs.get("target_role"),
        "target_level": args.target_level or wizard_inputs.get("target_level"),
        "source_resume_ref": args.source_resume or wizard_inputs.get("source_resume_ref"),
        "source_resume_text": args.source_resume_text or wizard_inputs.get("source_resume_text"),
        "job_description_ref": args.jd or wizard_inputs.get("job_description_ref"),
        "job_description_text": args.jd_text or wizard_inputs.get("job_description_text"),
        "manual_brief_path": args.manual_brief or wizard_inputs.get("manual_brief_path"),
        "auto_research_internal": args.auto_research_internal or wizard_inputs.get("auto_research_internal", False),
        "auto_research_tavily": args.auto_research_tavily,
        "research_via": args.research_via or wizard_inputs.get("research_via"),
        "output_directory": args.output,
        "idempotency_key": args.idempotency_key,
    }

    # Validate minimum inputs
    if not (ingress_payload["target_company"] or ingress_payload["target_role"]):
        if not (ingress_payload["source_resume_ref"] or ingress_payload["source_resume_text"]):
            print("ERROR: At least one of (target_company, target_role) or resume source required.", file=sys.stderr)
            return 1

    if args.dry_run:
        print("DRY RUN: Ingress payload validated successfully.")
        print(json.dumps(ingress_payload, indent=2))
        return 0

    # Submit to AppIngressRunner (core runtime entry)
    try:
        from agentic_core.runtime.entry.app_ingress_runner import AppIngressRunner
    except ImportError:
        raise RuntimeError(
            "AppIngressRunner not available. Runtime not initialized. "
            "Core runtime must be initialized before apps_rg can submit ingress payloads."
        )

    runner = AppIngressRunner()

    try:
        result = runner.run(ingress_payload)
    except Exception as e:
        print(f"ERROR: Runtime execution failed: {e}", file=sys.stderr)
        return 3

    # Present output
    print("=" * 60)
    print("Resume Generation Complete")
    print("=" * 60)
    print(f"Output location: {result.get('output_path', 'N/A')}")
    print(f"Exit status: {result.get('exit_status', 'UNKNOWN')}")

    if result.get("exit_status") != "SUCCESS":
        return 4

    return 0


if __name__ == "__main__":
    sys.exit(main())

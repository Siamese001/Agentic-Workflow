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


def _assert_artifact_matches_company(
    artifact_path: Path | str,
    target_company: str,
    artifact_type: str,
) -> None:
    """Guard: if artifact_path exists and carries a `company` field, verify it
    matches target_company (case-insensitive).  Missing file, empty
    target_company, non-JSON/YAML extension, missing `company` key, and parse
    errors are all treated as no-ops so the guard stays fail-soft on ambiguity.

    Raises SystemExit with a FATAL message on company mismatch.
    """
    p = Path(artifact_path)
    if not p.exists() or not target_company:
        return
    suffix = p.suffix.lower()
    if suffix not in (".json", ".yaml", ".yml"):
        return
    try:
        text = p.read_text(encoding="utf-8")
        if suffix == ".json":
            data = json.loads(text)
        else:
            try:
                import yaml  # type: ignore[import-untyped]
                data = yaml.safe_load(text)
            except ImportError:
                import re as _re
                m = _re.search(r'^company:\s*(.+)$', text, _re.MULTILINE)
                data = {"company": m.group(1).strip()} if m else {}
    except Exception:  # guardian: allow-broad-exception -- fail-soft parse guard; never block valid runs
        return
    if not isinstance(data, dict):
        return
    artifact_company: str = data.get("company", "")
    if not artifact_company:
        return
    if artifact_company.lower().strip() != target_company.lower().strip():
        sys.exit(
            f"FATAL: {artifact_type} company mismatch — "
            f"artifact declares '{artifact_company}' but --target-company is '{target_company}'. "
            "Remove or replace the artifact before running for this target company."
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


_CANONICAL_SOURCE_RESUME: str = "ops_scripts/apps_rg/source_resume_2026_05_12.json"
"""Canonical, immutable source resume snapshot (2026-05-12, SVP Engineering Resume_Ayer.docx).
Always use this as the default — never the April-dated docx files."""


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
        help="Path to source resume file. PDF/DOCX paths auto-resolve to canonical JSON (SSOT)",
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
    parser.add_argument(
        "--cascade-prompts",
        action="store_true",
        help="Sentinel mode for Cascade: write prompt sentinel + exit 7 instead of launching TTY wizard",
    )
    parser.add_argument(
        "--ingest-master-resume",
        action="store_true",
        help="Ingest DOCX template and save as JSON master resume (one-time operation)",
    )
    args = parser.parse_args()

    # Ingest master resume from DOCX template (one-time operation)
    if getattr(args, 'ingest_master_resume', False):
        # DOCX template path (per user directive)
        docx_template_path = Path("C:/Users/amita/Documents/Resumes/SVP Engineering Resume_Ayer.docx")
        if not docx_template_path.exists():
            print(f"ERROR: DOCX template not found: {docx_template_path}", file=sys.stderr)
            return 1

        # Master resume JSON output path
        repo_root = Path(__file__).parent.parent
        master_resume_path = repo_root / "artifacts" / "apps_rg" / "master_resume.json"

        from apps_rg.runtime.bindings.exit_binding import _ingest_docx_to_master_resume
        master_resume = _ingest_docx_to_master_resume(docx_template_path, master_resume_path)

        if master_resume:
            print("=" * 60)
            print("Master resume ingested successfully")
            print("=" * 60)
            print(f"Source: {docx_template_path}")
            print(f"Output: {master_resume_path}")
            print(f"Name: {master_resume.get('header', {}).get('name', 'N/A')}")
            print(f"Experience entries: {len(master_resume.get('experience', []))}")
            return 0
        else:
            print("ERROR: Failed to ingest master resume", file=sys.stderr)
            return 1

    # Cascade sentinel mode: when --cascade-prompts is set, require both
    # target_company and target_role to be explicitly supplied; exit 7 if either
    # is missing so that Cascade can surface the mandatory-fields prompt.
    if getattr(args, 'cascade_prompts', False):
        if not args.target_company or not args.target_role:
            print(
                "CASCADE SENTINEL: mandatory inputs required — "
                "provide --target-company and --target-role to proceed.",
                file=sys.stderr,
            )
            return 7

    # Launch wizard if requested or if no args provided
    needs_wizard = args.wizard or (
        not args.target_company and not args.target_role and not args.source_resume
    )
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
        "source_resume_ref": (
            args.source_resume
            or wizard_inputs.get("source_resume_ref")
            or _CANONICAL_SOURCE_RESUME
        ),
        "source_resume_text": args.source_resume_text or wizard_inputs.get("source_resume_text"),
        "job_description_ref": args.jd or wizard_inputs.get("job_description_ref"),
        "job_description_text": args.jd_text or wizard_inputs.get("job_description_text"),
        "manual_brief_path": args.manual_brief or wizard_inputs.get("manual_brief_path"),
        "auto_research_internal": args.auto_research_internal or wizard_inputs.get("auto_research_internal", False),
        "auto_research_tavily": args.auto_research_tavily,
        "research_via": wizard_inputs.get("research_via") or ("apps_research" if args.auto_research_internal else None),
        "output_directory": args.output,
        "idempotency_key": args.idempotency_key,
    }

    # Validate minimum inputs
    if not (ingress_payload["target_company"] or ingress_payload["target_role"]):
        if not (ingress_payload["source_resume_ref"] or ingress_payload["source_resume_text"]):
            print("ERROR: At least one of (target_company, target_role) or resume source required.", file=sys.stderr)
            return 1

    # D1 W6 caller wiring: intake prerequisite checks before submitting to runner
    _target_company: str = ingress_payload.get("target_company") or ""

    # Contamination guard: verify artifact company fields match target
    if ingress_payload.get("job_description_ref"):
        _assert_artifact_matches_company(
            ingress_payload["job_description_ref"], _target_company, "jd"
        )
    if ingress_payload.get("manual_brief_path"):
        _assert_artifact_matches_company(
            ingress_payload["manual_brief_path"], _target_company, "manual_brief"
        )

    # Prerequisite check: if explicit --manual-brief path provided but missing,
    # the caller made a specific choice — surface it rather than silently stubbing.
    if ingress_payload.get("manual_brief_path"):
        _brief_path = Path(ingress_payload["manual_brief_path"])
        if not _brief_path.exists():
            print(
                f"MISSING: manual_brief file not found at '{_brief_path}'. "
                "Provide a valid briefing path or use --auto-research-internal "
                "to delegate to apps_research.",
                file=sys.stderr,
            )
            return 1

    if args.dry_run:
        print("DRY RUN: Ingress payload validated successfully.")
        print(json.dumps(ingress_payload, indent=2))
        # apps-rg-u0-reflection-live-wiring-105147 W6.P6.1: dry-run proves
        # the live U0 path emits the reflection receipt before L1. We
        # build the envelope and run u0_validate_apps_rg, then surface the
        # receipt's pass_status + digests so the operator sees the harness
        # is on the live path. No L1+ stage runs.
        try:
            # W0A: Use canonical dispatch path only — apps_rg/runtime/dispatch
            from apps_rg.runtime.dispatch import apps_rg_parse
            from apps_rg.runtime.bindings.u0_binding import u0_validate_apps_rg
            envelope = apps_rg_parse(ingress_payload)
            if envelope is None:
                print("DRY RUN: U0 harness — envelope build skipped (parse returned None).")
                return 0
            validated = u0_validate_apps_rg(envelope)
            receipt = validated.reflection_receipt
            print()
            print("DRY RUN: U0 reflection harness on live path — verdict:")
            print(f"  pass_status:              {receipt.pass_status}")
            print(f"  pointers_total:           {receipt.pointers_total}")
            print(f"  pointers_mapped:          {receipt.pointers_mapped}")
            print(f"  pointers_derived:         {receipt.pointers_derived}")
            print(f"  pointers_deferred:        {receipt.pointers_deferred}")
            print(f"  silently_dropped:         {receipt.silently_dropped}")
            print(f"  unknown_mappings:         {receipt.unknown_mappings}")
            print(f"  input_payload_digest:     {receipt.input_payload_digest[:16]}...")
            print(f"  validated_request_digest: {receipt.validated_request_digest[:16]}...")
            print(f"  audit_refs:               {validated.audit_refs}")
        except Exception as e:  # guardian: allow-broad -- dry-run smoke surface; surface message + non-zero exit
            print(f"DRY RUN: U0 harness FAILED: {type(e).__name__}: {e}", file=sys.stderr)
            return 1
        return 0

    # Submit to AppIngressRunner (core runtime entry).
    # W0.5C: profile-based constructor — AppIngressRunner(profile=profile, dispatch=apps_rg_dispatch).
    # AppIngressRunner populates proof fields (profile_digest, binding_digest_map) before dispatch.
    try:
        from agentic_core.runtime.entry.app_ingress_runner import AppIngressRunner
        from apps_rg.runtime.dispatch import apps_rg_dispatch
        from apps_rg.runtime.profile_builder import build_app_runtime_contract
    except ImportError as exc:
        print(
            "ERROR: Core runtime entry not importable. "
            f"Cannot proceed without AppIngressRunner + apps_rg profile: {exc}",
            file=sys.stderr,
        )
        return 3

    profile = build_app_runtime_contract()
    runner = AppIngressRunner(
        profile=profile,
        dispatch=apps_rg_dispatch,
    )

    try:
        result = runner.run(ingress_payload)
    except Exception as e:  # guardian: allow-broad-exception -- CLI error boundary; surface message + non-zero exit
        print(f"ERROR: Runtime execution failed: {e}", file=sys.stderr)
        return 3

    # Result is either an X3Disposition (happy path) or ClarificationRequired.
    # Detect via attribute presence (avoids importing both contract types here).
    print("=" * 60)
    print("apps_rg ingress submission complete")
    print("=" * 60)

    if hasattr(result, "exit_status"):
        # X3Disposition path
        print(f"Exit status:    {result.exit_status}")
        print(f"Request ID:     {getattr(result, 'request_id', 'N/A')}")
        print(f"Run ID:         {getattr(result, 'run_id', 'N/A')}")
        print(f"Trace ID:       {getattr(result, 'trace_id', 'N/A')}")
        print(f"Authorized:     {getattr(result, 'outcome_authorized', False)}")
        if getattr(result, "output_artifact_path", None):
            print(f"Artifact path:  {result.output_artifact_path}")
        final_output = getattr(result, "final_output", {}) or {}
        if final_output:
            print("Final output:")
            print(json.dumps(dict(final_output), indent=2, default=str))
        if result.exit_status == "success":
            return 0
        return 4

    # ClarificationRequired path
    if hasattr(result, "reason"):
        print(f"Clarification required: {result.reason}", file=sys.stderr)
        for f in getattr(result, "suggested_followups", ()) or ():
            print(f"  - {f}", file=sys.stderr)
        return 5

    print(f"Unexpected result type: {type(result).__name__}", file=sys.stderr)
    return 6


if __name__ == "__main__":
    sys.exit(main())

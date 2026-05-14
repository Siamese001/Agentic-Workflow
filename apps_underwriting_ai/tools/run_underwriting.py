"""Thin CLI wrapper over the apps_underwriting_ai profile-sequenced pipeline.

Delegates to AppIngressRunner(profile=build_app_runtime_contract()).run(payload).
No dispatch callable. AppIngressRunner owns stage sequencing.

Usage::

    python -m apps_underwriting_ai.tools.run_underwriting --request path.yaml
    python -m apps_underwriting_ai.tools.run_underwriting --request path.json --format json
    python -m apps_underwriting_ai.tools.run_underwriting --request path.yaml --out artifacts/

Bundle B — shadow pipeline removed. Profile-only runtime.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint — delegates to the full dispatch chain."""
    parser = argparse.ArgumentParser(prog="run_underwriting")
    parser.add_argument("--request", required=False, help="Path to YAML/JSON request file.")
    parser.add_argument("--format", choices=["json", "text"], default="text",
                        help="Output format (default: text).")
    parser.add_argument("--out", default=None, help="Artifact output directory.")
    args = parser.parse_args(argv)

    if not args.request:
        parser.print_help(sys.stderr)
        return 2

    p = Path(args.request)
    if not p.exists():
        print(f"error: request file not found: {args.request}", file=sys.stderr)
        return 2

    # Parse request file
    try:
        text = p.read_text(encoding="utf-8")
        if p.suffix in {".yaml", ".yml"}:
            import yaml  # noqa: PLC0415
            payload: dict = yaml.safe_load(text) or {}
        else:
            payload = json.loads(text)
    except Exception as exc:  # noqa: BLE001
        # guardian: allow-broad-except -- CLI file errors must surface as exit 2
        print(f"error: failed to read request file: {exc}", file=sys.stderr)
        return 2

    for required in ("request_id", "applicant_id", "product_class"):
        if required not in payload:
            print(f"error: request file missing required field: {required}", file=sys.stderr)
            return 2

    from agentic_core.runtime.entry.app_ingress_runner import AppIngressRunner  # noqa: PLC0415
    from agentic_core.L5_safety.enforcement.ingress_envelope_check import ClarificationRequired  # noqa: PLC0415
    from apps_underwriting_ai.runtime.bindings.u0_binding import U0ValidationError  # noqa: PLC0415
    from apps_underwriting_ai.runtime.profile_builder import build_app_runtime_contract  # noqa: PLC0415

    os.environ.setdefault("UW_DISPATCH_SKIP_LLM", "1")
    profile = build_app_runtime_contract()
    runner = AppIngressRunner(profile=profile)
    try:
        result = runner.run(payload)
    except U0ValidationError as exc:
        print(f"error: U0 validation failed: {exc}", file=sys.stderr)
        return 5

    if isinstance(result, ClarificationRequired):
        print(f"error: ClarificationRequired: {result.reason}", file=sys.stderr)
        return 4

    if args.format == "json":
        out_dict = {
            "request_id": result.request_id,
            "applicant_id": result.applicant_id,
            "product_class": result.product_class,
            "verdict": result.verdict,
            "aggregate_score": result.aggregate_score,
            "reason_codes": result.reason_codes,
            "c0_state": result.c0_state,
            "support_score": result.support_score,
            "hitl_posture": result.hitl_posture,
            "x3_disposition": result.x3_disposition,
            "rationale_source": result.rationale_source,
            "rationale": result.rationale,
            "success": result.success,
            "error": result.error,
        }
        print(json.dumps(out_dict, indent=2))
    else:
        print(
            f"verdict={result.verdict} score={result.aggregate_score:.4f} "
            f"x3={result.x3_disposition} hitl={result.hitl_posture} "
            f"success={result.success}"
        )

    if args.out:
        out_dir = Path(args.out)
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "result.json").write_text(
            json.dumps(result.__dict__, indent=2, default=str), encoding="utf-8"
        )
        (out_dir / "summary.md").write_text(
            f"# Underwriting Result\n\n"
            f"- **Verdict**: {result.verdict}\n"
            f"- **Score**: {result.aggregate_score:.4f}\n"
            f"- **X3**: {result.x3_disposition}\n"
            f"- **HITL**: {result.hitl_posture}\n"
            f"- **Rationale**: {result.rationale}\n",
            encoding="utf-8",
        )

    return 0 if result.success else 6


if __name__ == "__main__":
    raise SystemExit(main())

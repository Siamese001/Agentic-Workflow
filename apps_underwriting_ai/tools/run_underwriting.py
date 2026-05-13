"""Thin CLI wrapper over the apps_underwriting_ai dispatch chain.

Previously drove the deleted parallel pipeline. Now delegates to U0 →
dispatch → Exit via apps_underwriting_ai.__main__._run_from_file.

Usage::

    python -m apps_underwriting_ai.tools.run_underwriting --request path.yaml
    python -m apps_underwriting_ai.tools.run_underwriting --request path.json --format json
    python -m apps_underwriting_ai.tools.run_underwriting --request path.yaml --out artifacts/

Plan: apps-underwriting-ai-kill-parallel-pipelines-a3f7e2 W4.
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

    from apps_underwriting_ai.runtime.bindings.u0_binding import (  # noqa: PLC0415
        U0ValidationError,
        u0_validate_underwriting,
    )
    from apps_underwriting_ai.runtime.contracts.underwriting_ingress_payload import (  # noqa: PLC0415
        UnderwritingIngressEnvelope,
    )
    from apps_underwriting_ai.runtime.dispatch.underwriting_dispatch import (  # noqa: PLC0415
        run_underwriting_dispatch,
    )

    envelope = UnderwritingIngressEnvelope(
        request_id=str(payload["request_id"]),
        applicant_id=str(payload["applicant_id"]),
        product_class=str(payload["product_class"]),
        documents=tuple(payload.get("documents") or ()),
        metadata=payload.get("metadata") or {},
        trace_id=str(payload.get("trace_id") or ""),
    )
    try:
        validated = u0_validate_underwriting(envelope)
    except U0ValidationError as exc:
        print(f"error: U0 validation failed: {exc}", file=sys.stderr)
        return 5

    os.environ.setdefault("UW_DISPATCH_SKIP_LLM", "1")
    result = run_underwriting_dispatch(validated)

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

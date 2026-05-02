"""CLI: run apps_underwriting_ai end-to-end on a request file.

Mirrors the ``apps_rfp`` runner shape. Drives
:class:`UnderwritingIngressRunner` for ingress + renders the decision
via :class:`EnterpriseUnderwritingRenderer`.

Usage::

    python -m apps_underwriting_ai.tools.run_underwriting --request path.yaml
    python -m apps_underwriting_ai.tools.run_underwriting --request path.json --out artifacts/uw
    python -m apps_underwriting_ai.tools.run_underwriting --help
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from apps_underwriting_ai.integrations.underwriting_ingress_runner import (
    UnderwritingIngressRunner,
)
from apps_underwriting_ai.outputs.decision_renderer import DecisionRenderer
from apps_underwriting_ai.outputs.enterprise_underwriting_renderer import (
    EnterpriseUnderwritingRenderer,
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="apps_underwriting_ai.tools.run_underwriting",
        description=(
            "Run apps_underwriting_ai end-to-end on a request file. "
            "Emits a DecisionPacket + optionally writes artifacts to disk."
        ),
    )
    parser.add_argument(
        "--request",
        type=Path,
        required=True,
        help="Path to YAML or JSON request file (see UnderwritingIngressRunner).",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="If set, write enterprise-format artifacts to this directory.",
    )
    parser.add_argument(
        "--trace-id",
        type=str,
        default=None,
        help="Optional trace_id to stamp on the result.",
    )
    parser.add_argument(
        "--format",
        choices=("markdown", "json"),
        default="markdown",
        help="stdout render format (default: markdown).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    runner = UnderwritingIngressRunner()
    try:
        result = runner.run_from_file(args.request, trace_id=args.trace_id)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except ValueError as exc:
        print(f"error: invalid request — {exc}", file=sys.stderr)
        return 2

    renderer = DecisionRenderer()
    if args.format == "json":
        print(renderer.to_json(result))
    else:
        print(renderer.to_markdown(result))

    if args.out is not None:
        paths = EnterpriseUnderwritingRenderer(artifact_dir=args.out).render_to_disk(
            result
        )
        print(f"\nartifacts written:\n  {json.dumps(paths, indent=2)}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

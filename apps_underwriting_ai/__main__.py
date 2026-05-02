"""apps_underwriting_ai CLI entrypoint.

Usage::

    python -m apps_underwriting_ai --request input/request.yaml
    python -m apps_underwriting_ai --demo

The `--demo` flag runs a deterministic synthetic underwriting request
end-to-end through the 5-stage pipeline and prints the decision packet.
Useful as a smoke test.
"""

from __future__ import annotations

import argparse
import sys

from apps_underwriting_ai.integrations.governed_underwriting_run import (
    governed_underwriting_run,
)
from apps_underwriting_ai.integrations.underwriting_ingress_runner import (
    UnderwritingIngressRunner,
)
from apps_underwriting_ai.outputs.decision_renderer import DecisionRenderer
from apps_underwriting_ai.outputs.enterprise_underwriting_renderer import (
    EnterpriseUnderwritingRenderer,
)


def _run_demo() -> int:
    """Run a synthetic underwriting request end-to-end."""
    result = governed_underwriting_run(
        request_id="demo-0001",
        applicant_id="applicant-demo",
        product_class="small_business_loan",
        documents=(
            {"kind": "tax_return", "year": 2025},
            {"kind": "bank_statement", "month": "2026-04"},
        ),
        metadata={"source": "demo"},
        trace_id="trace-demo",
    )
    print(DecisionRenderer().to_markdown(result))
    return 0


def _run_from_file(request_path: str, artifact_dir: str | None) -> int:
    runner = UnderwritingIngressRunner()
    result = runner.run_from_file(request_path)
    if artifact_dir:
        renderer = EnterpriseUnderwritingRenderer(artifact_dir=artifact_dir)
        emitted = renderer.render_to_disk(result)
        print(f"emitted: {emitted}")
    print(DecisionRenderer().to_markdown(result))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="apps_underwriting_ai")
    parser.add_argument(
        "--request",
        help="Path to YAML/JSON underwriting request file.",
    )
    parser.add_argument(
        "--artifact-dir",
        default=None,
        help="Optional directory to emit decision artifacts to.",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run a synthetic demo underwriting request.",
    )
    args = parser.parse_args(argv)

    if args.demo:
        return _run_demo()
    if args.request:
        return _run_from_file(args.request, args.artifact_dir)

    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())

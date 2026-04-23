"""Exemplar coverage gate \u2014 W4 RH4.3.

Asserts that prompts flagged as exemplar-eligible carry at least 3 examples.

Usage at assembly time::

    from agentic_core.prompt_governance.validation.check_exemplar_coverage import (
        check_exemplar_coverage,
    )
    ok, errs = check_exemplar_coverage(
        task_class="rfp_section_draft",
        exemplars_provided=3,
        eligibility=True,
    )
    if not ok:
        raise AssemblyError("; ".join(errs))

The ``eligibility`` flag is driven by ``AgentSpec.exemplar_eligible``
(added in W5). When an agent spec has not opted in, the gate is a no-op.

CI invocation (W5 will wire ops_scripts/ci/check_exemplar_coverage.py
against the agent-spec registry):

    python -m agentic_core.prompt_governance.validation.check_exemplar_coverage \\
        --task-class rfp_section_draft --provided 3 --eligible
"""

from __future__ import annotations

import argparse
import sys


MINIMUM_EXAMPLES = 3


def check_exemplar_coverage(
    *,
    task_class: str,
    exemplars_provided: int,
    eligibility: bool,
) -> tuple[bool, list[str]]:
    """Return ``(ok, errors)``.

    Parameters
    ----------
    task_class:
        Label of the prompt's task class.
    exemplars_provided:
        Number of E0 records the assembler has resolved for this call.
    eligibility:
        Whether this prompt category opts into the few-shot requirement.
    """
    errors: list[str] = []

    if not task_class:
        errors.append("task_class must not be empty")

    if exemplars_provided < 0:
        errors.append(
            f"exemplars_provided must be >= 0, got {exemplars_provided}"
        )

    if eligibility and exemplars_provided < MINIMUM_EXAMPLES:
        errors.append(
            f"exemplar-eligible task_class={task_class!r} has "
            f"{exemplars_provided} example(s), required minimum {MINIMUM_EXAMPLES}"
        )

    return (len(errors) == 0, errors)


def _cli(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate exemplar coverage for a single prompt slot.",
    )
    parser.add_argument("--task-class", required=True)
    parser.add_argument("--provided", type=int, required=True)
    parser.add_argument(
        "--eligible", action="store_true", help="Prompt opts into E0 coverage"
    )
    args = parser.parse_args(argv)
    ok, errs = check_exemplar_coverage(
        task_class=args.task_class,
        exemplars_provided=args.provided,
        eligibility=args.eligible,
    )
    if not ok:
        for err in errs:
            print(f"FAIL: {err}", file=sys.stderr)
        return 1
    print("OK: exemplar coverage satisfied")
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli())


__all__ = ["check_exemplar_coverage", "MINIMUM_EXAMPLES"]

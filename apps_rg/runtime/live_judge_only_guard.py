"""Production runtime guard for the apps_rg section CLI.

Historically this enforced *live PROVIDER_MODEL external model* (no offline stub) in addition to the live-judge
policy. The PROVIDER_MODEL/external model local provider was removed; the external generation provider owns its
own transport, so the PROVIDER_MODEL-readiness env checks are gone. The non-PROVIDER_MODEL production policy
remains: ``python -m apps_rg`` never accepts mock-judge CLI flags (X1D judges are always live;
mock judges are test-harness env-only).
"""
from __future__ import annotations

import os
import sys

ENV_APPS_RG_TEST_HARNESS = "APPS_RG_TEST_HARNESS"
ENV_APPS_RG_MOCK_JUDGES = "APPS_RG_MOCK_JUDGES"

_MOCK_JUDGE_CLI_FLAGS = frozenset({"--mock-judges", "--allow-test-mock-judges"})

_TRUE = frozenset({"1", "true", "yes", "on", "y"})


def _env_on(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in _TRUE


def is_test_harness() -> bool:
    return _env_on(ENV_APPS_RG_TEST_HARNESS)


def production_mock_judge_cli_violations(
    argv: list[str] | None = None,
    *,
    mock_judges: bool = False,
    allow_test_mock_judges: bool = False,
) -> list[str]:
    """Reject mock-judge CLI flags on the product entry (``python -m apps_rg``)."""
    av = list(argv if argv is not None else sys.argv)
    hits = sorted(f for f in _MOCK_JUDGE_CLI_FLAGS if f in av)
    if mock_judges and "--mock-judges" not in hits:
        hits.append("--mock-judges")
    if allow_test_mock_judges and "--allow-test-mock-judges" not in hits:
        hits.append("--allow-test-mock-judges")
    if not hits:
        return []
    return [
        "Production CLI does not accept "
        + ", ".join(hits)
        + ": X1D judges are always live. "
        f"Test plumbing only: {ENV_APPS_RG_TEST_HARNESS}=1 and {ENV_APPS_RG_MOCK_JUDGES}=1."
    ]


def production_mock_judge_args_violations(args: object) -> list[str]:
    return production_mock_judge_cli_violations(
        mock_judges=bool(getattr(args, "mock_judges", False)),
        allow_test_mock_judges=bool(getattr(args, "allow_test_mock_judges", False)),
    )


def assert_production_cli_no_mock_judge_flags(
    argv: list[str] | None = None,
    *,
    args: object | None = None,
) -> None:
    """Exit 2 when argv/args request mock judges (no opt-out flags on product runs)."""
    violations = production_mock_judge_cli_violations(argv)
    if args is not None:
        violations = violations or production_mock_judge_args_violations(args)
    if not violations:
        return
    print(f"ERROR: {violations[0]}", file=sys.stderr, flush=True)
    raise SystemExit(2)


def resolve_cli_mock_judges() -> tuple[bool, bool]:
    """(mock_judges, allow_test_mock_judges) for section dispatch — env-only in test harness."""
    if not is_test_harness():
        return False, False
    if not _env_on(ENV_APPS_RG_MOCK_JUDGES):
        return False, False
    return True, True


def assert_production_runtime(
    *,
    context: str = "apps_rg",
    argv: list[str] | None = None,
    args: object | None = None,
) -> None:
    """Product default: no mock-judge CLI flags (X1D judges are always live)."""
    assert_production_cli_no_mock_judge_flags(argv, args=args)


__all__ = [
    "ENV_APPS_RG_MOCK_JUDGES",
    "ENV_APPS_RG_TEST_HARNESS",
    "assert_production_cli_no_mock_judge_flags",
    "assert_production_runtime",
    "is_test_harness",
    "production_mock_judge_args_violations",
    "production_mock_judge_cli_violations",
    "resolve_cli_mock_judges",
]

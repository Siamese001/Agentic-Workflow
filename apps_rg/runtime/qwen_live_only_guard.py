"""Fail-closed production runtime: live Qwen vLLM and live X1D judges on product CLI."""

from __future__ import annotations

import os
import sys

from apps_rg.runtime.qwen_offline_contract_stub import ENV_APPS_RG_QWEN_OFFLINE_CONTRACT_STUB

ENV_APPS_RG_TEST_HARNESS = "APPS_RG_TEST_HARNESS"
ENV_APPS_RG_MOCK_JUDGES = "APPS_RG_MOCK_JUDGES"

_MOCK_JUDGE_CLI_FLAGS = frozenset({"--mock-judges", "--allow-test-mock-judges"})

_TRUE = frozenset({"1", "true", "yes", "on", "y"})


def _env_on(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in _TRUE


def _l2_stub_mode() -> bool:
    raw = (os.environ.get("APPS_RG_L2_PROVIDER_MODE") or "").strip().lower()
    return raw in ("stub_only", "stub", "off", "0", "false", "no")


def live_qwen_mock_env_violations() -> list[str]:
    """Human-readable reasons when mock/offline Qwen paths are requested."""
    out: list[str] = []
    if _env_on(ENV_APPS_RG_QWEN_OFFLINE_CONTRACT_STUB):
        out.append(
            f"{ENV_APPS_RG_QWEN_OFFLINE_CONTRACT_STUB}=1 is forbidden: "
            "section lanes require live qwen_vllm HTTP (no offline contract stub)."
        )
    if _env_on("APPS_RG_SKIP_QWEN_VLLM_HEALTH"):
        out.append(
            "APPS_RG_SKIP_QWEN_VLLM_HEALTH=1 is forbidden: "
            "vLLM /v1/models preflight must run before generation."
        )
    if _env_on("APPS_RG_L2_FORCE_STUB"):
        out.append(
            "APPS_RG_L2_FORCE_STUB=1 is forbidden for apps_rg runs that use qwen_vllm."
        )
    if _l2_stub_mode():
        out.append(
            "APPS_RG_L2_PROVIDER_MODE=stub_only (or stub) is forbidden for live qwen_vllm runs."
        )
    return out


def assert_live_qwen_vllm_no_mocks(*, context: str = "apps_rg") -> None:
    """Exit 2 when any env requests non-live Qwen for product/runtime execution."""
    violations = live_qwen_mock_env_violations()
    if not violations:
        return
    msg = f"{context}: live qwen_vllm required — " + " | ".join(violations)
    print(f"ERROR: {msg}", file=sys.stderr, flush=True)
    raise SystemExit(2)


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
    """Live Qwen + no mock-judge CLI flags (product default)."""
    assert_production_cli_no_mock_judge_flags(argv, args=args)
    assert_live_qwen_vllm_no_mocks(context=context)


__all__ = [
    "ENV_APPS_RG_MOCK_JUDGES",
    "ENV_APPS_RG_TEST_HARNESS",
    "assert_live_qwen_vllm_no_mocks",
    "assert_production_cli_no_mock_judge_flags",
    "assert_production_runtime",
    "is_test_harness",
    "live_qwen_mock_env_violations",
    "production_mock_judge_args_violations",
    "production_mock_judge_cli_violations",
    "resolve_cli_mock_judges",
]

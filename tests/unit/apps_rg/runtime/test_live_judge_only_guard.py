from __future__ import annotations

import pytest

from apps_rg.runtime import live_judge_only_guard as guard


def test_production_mock_judge_cli_violations_rejects_cli_and_args_flags() -> None:
    violations = guard.production_mock_judge_cli_violations(
        ["apps_rg", "--mock-judges"],
        allow_test_mock_judges=True,
    )

    assert len(violations) == 1
    assert "--mock-judges" in violations[0]
    assert "--allow-test-mock-judges" in violations[0]
    assert "X1D judges are always live" in violations[0]


def test_assert_production_cli_no_mock_judge_flags_exits_two(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        guard.assert_production_cli_no_mock_judge_flags(["apps_rg", "--allow-test-mock-judges"])

    assert exc.value.code == 2
    assert "Production CLI does not accept" in capsys.readouterr().err


def test_resolve_cli_mock_judges_is_env_only_in_test_harness(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv(guard.ENV_APPS_RG_TEST_HARNESS, raising=False)
    monkeypatch.delenv(guard.ENV_APPS_RG_MOCK_JUDGES, raising=False)
    assert guard.resolve_cli_mock_judges() == (False, False)

    monkeypatch.setenv(guard.ENV_APPS_RG_TEST_HARNESS, "1")
    assert guard.resolve_cli_mock_judges() == (False, False)

    monkeypatch.setenv(guard.ENV_APPS_RG_MOCK_JUDGES, "yes")
    assert guard.resolve_cli_mock_judges() == (True, True)


def test_assert_production_runtime_allows_clean_args_object() -> None:
    args = type(
        "Args",
        (),
        {"mock_judges": False, "allow_test_mock_judges": False},
    )()

    guard.assert_production_runtime(argv=["apps_rg"], args=args)

"""Eval trial isolation conftest (ADR-038 / plan W4.2).

Provides the ``per_trial_workdir`` fixture and enforces trial isolation
invariants for every test under ``tests/eval/``.

Invariants:
  - Each trial runs in a clean ``tmp_path`` subtree.
  - Function-scope fixtures only (module/session scope is rejected).
  - Env-var whitelist; unknown vars are wiped.
  - Outbound DNS resolution is blocked unless the trial opts in via
    ``@pytest.mark.eval_network``.
"""

from __future__ import annotations

import os
import socket
from pathlib import Path

import pytest

_ENV_ALLOWLIST: frozenset[str] = frozenset({
    "PATH", "PYTHONPATH", "HOME", "USERPROFILE", "TEMP", "TMP",
    "PYTEST_CURRENT_TEST", "CI", "GITHUB_ACTIONS",
    "EVAL_TRIAL_ID",
})


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        "eval_network: allow outbound DNS resolution for this eval trial.",
    )
    config.addinivalue_line(
        "markers",
        "eval_cache_allowed: allow reading cached artifacts across eval trials.",
    )


@pytest.fixture(scope="function")
def per_trial_workdir(tmp_path: Path) -> Path:
    """Yield a clean, trial-local workspace.

    Asserts the directory is empty on entry. The runner writes artifacts to
    ``workdir / "artifacts"`` and inputs to ``workdir / "inputs"``.
    """
    assert not any(tmp_path.iterdir()), f"per_trial_workdir must start empty: {tmp_path}"
    (tmp_path / "artifacts").mkdir()
    (tmp_path / "inputs").mkdir()
    return tmp_path


@pytest.fixture(autouse=True, scope="function")
def _wipe_env_outside_allowlist(monkeypatch: pytest.MonkeyPatch) -> None:
    """Hide env vars not on the eval allowlist for every trial."""
    for key in list(os.environ):
        if key not in _ENV_ALLOWLIST:
            monkeypatch.delenv(key, raising=False)


@pytest.fixture(autouse=True, scope="function")
def _block_network(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch) -> None:
    """Block DNS resolution unless the trial is marked ``eval_network``."""
    if request.node.get_closest_marker("eval_network"):
        return

    def _raise(*_args: object, **_kwargs: object) -> None:
        raise RuntimeError(
            "network access is blocked in eval trials; "
            "add @pytest.mark.eval_network to opt in"
        )

    monkeypatch.setattr(socket, "getaddrinfo", _raise)
    monkeypatch.setattr(socket, "gethostbyname", _raise)

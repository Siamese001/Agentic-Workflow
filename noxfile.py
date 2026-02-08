"""
Nox sessions for test isolation and integration testing.

Sessions:
    unit_min_deps:          Run unit tests that require only stdlib + pytest.
    integration_full_deps:  Install pydantic, then run integration tests.
    decorators:             Run decorator/timeout AST enforcement + contract tests.

Usage:
    nox -s unit_min_deps
    nox -s integration_full_deps
    nox -s decorators
"""

from __future__ import annotations

import nox

nox.options.reuse_existing_virtualenvs = True


@nox.session(python=False)
def unit_min_deps(session: nox.Session) -> None:
    """Run unit_min_deps tests — no optional deps required."""
    session.run("python", "-m", "pytest", "-m", "unit_min_deps", "-q")


@nox.session
def integration_full_deps(session: nox.Session) -> None:
    """Install optional deps and run integration tests."""
    session.install("pytest")
    session.install("pydantic")
    session.run(
        "python",
        "-m",
        "pytest",
        "-m",
        "integration_full_deps",
        "-q",
        env={"INTEGRATION_FULL_DEPS_REQUIRED": "1"},
    )


@nox.session(python=False)
def decorators(session: nox.Session) -> None:
    """Run decorator/timeout AST enforcement and contract tests."""
    session.run(
        "python",
        "-m",
        "pytest",
        "tests/unit/agentic_core/structure/test_decorator_timeout_layer_constraints.py",
        "tests/unit/agentic_core/base_agents/test_decorator_shim_contract.py",
        "-v",
    )

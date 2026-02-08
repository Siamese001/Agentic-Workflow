"""
Nox sessions for test isolation and integration testing.

Sessions:
    unit_min_deps:   Run tests/unit_min_deps/ — stdlib + pytest only, no optional deps.
    integration:     Install pydantic, run tests/integration/ with real agent validation.
    decorators:      Run decorator/timeout AST enforcement + contract tests.

Usage:
    nox -s unit_min_deps
    nox -s integration
    nox -s decorators
"""

from __future__ import annotations

import nox

nox.options.reuse_existing_virtualenvs = True


@nox.session(python=False)
def unit_min_deps(session: nox.Session) -> None:
    """Run tests/unit_min_deps/ — no optional deps required."""
    session.run("python", "-m", "pytest", "tests/unit_min_deps/", "-q")


@nox.session
def integration(session: nox.Session) -> None:
    """Install optional deps and run tests/integration/."""
    session.install("pytest")
    session.install("pydantic")
    session.run(
        "python",
        "-m",
        "pytest",
        "tests/integration/",
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
        "tests/unit_min_deps/test_decorator_timeout_layer_constraints.py",
        "tests/unit_min_deps/test_decorator_shim_contract.py",
        "-v",
    )

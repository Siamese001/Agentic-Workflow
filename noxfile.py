"""
Nox sessions for test isolation and integration testing.

Sessions:
    unit_min_deps:   Run tests/unit_min_deps/ — stdlib + pytest only, no optional deps.
    integration:     Install pydantic, run tests/integration/agentic_core/ (explicit allowlist).
    decorators:      Run decorator/timeout AST enforcement + contract tests.
    legacy_unit:     Run tests/unit/ — legacy suite, NOT part of default pytest.

Usage:
    nox -s unit_min_deps
    nox -s integration
    nox -s decorators
    nox -s legacy_unit
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
    """Install optional deps and run allowed integration subtree."""
    session.install("pytest")
    session.install("pydantic")
    session.run(
        "python",
        "-m",
        "pytest",
        "tests/integration/agentic_core/",
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


@nox.session(python=False)
def legacy_unit(session: nox.Session) -> None:
    """Run tests/unit/ — legacy suite, not part of default pytest collection."""
    session.run("python", "-m", "pytest", "tests/unit/", "-q")

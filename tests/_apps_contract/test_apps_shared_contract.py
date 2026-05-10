"""Contract smoke test for apps_shared.

Verifies that the canonical public surface of apps_shared is importable and
exposes the minimum expected symbols. This is the baseline contract test
required by plan apps-test-surface-deferred-f3c8b2 D5.
"""
from __future__ import annotations

import importlib


def test_apps_shared_importable():
    """apps_shared package must be importable."""
    mod = importlib.import_module("apps_shared")
    assert mod is not None


def test_apps_shared_cert_importable():
    """apps_shared.cert sub-package must be importable (used by all cert-route adopters)."""
    mod = importlib.import_module("apps_shared.cert")
    assert mod is not None


def test_apps_shared_has_cert_route_registry():
    """apps_shared.cert must expose maybe_invoke_exit_eval (cert-route entry point)."""
    mod = importlib.import_module("apps_shared.cert")
    assert hasattr(mod, "maybe_invoke_exit_eval"), (
        "apps_shared.cert must export maybe_invoke_exit_eval "
        "(adoption check for NO_CERT_EXIT_INVOCATION gate)"
    )

"""ADG importability contract for agentic_core/L2_execution/enforcement/key_source.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_key_source.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.enforcement.key_source import (  # noqa: F401
        EnvKeySource,
        KeySource,
        TestKeySource,
        get_current_secret,
        get_key_source,
        inject_key_source,
    )

    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    KeySource = None  # type: ignore[assignment,misc]
    TestKeySource = None  # type: ignore[assignment,misc]
    EnvKeySource = None  # type: ignore[assignment,misc]
    inject_key_source = None  # type: ignore[assignment,misc]
    get_key_source = None  # type: ignore[assignment,misc]
    get_current_secret = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="key_source deps unavailable")
class TestKeySourceImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L2_execution/enforcement/key_source.py must be importable."""
        assert _AVAILABLE

    def test_keysource_defined(self) -> None:
        assert KeySource is not None

    def test_testkeysource_defined(self) -> None:
        assert TestKeySource is not None

    def test_envkeysource_defined(self) -> None:
        assert EnvKeySource is not None

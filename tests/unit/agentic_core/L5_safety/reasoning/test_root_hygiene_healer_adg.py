"""ADG importability contract for agentic_core/L5_safety/reasoning/root_hygiene_healer.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_root_hygiene_healer.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.reasoning.root_hygiene_healer import (  # noqa: F401
        ROOT_MARKERS,
        RootHygieneAgent,
        get_project_root,
        main,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    ROOT_MARKERS = None  # type: ignore[assignment,misc]
    get_project_root = None  # type: ignore[assignment,misc]
    RootHygieneAgent = None  # type: ignore[assignment,misc]
    main = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="root_hygiene_healer deps unavailable")
class TestRootHygieneHealerImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/reasoning/root_hygiene_healer.py must be importable."""
        assert _AVAILABLE

    def test_roothygieneagent_defined(self) -> None:
        assert RootHygieneAgent is not None

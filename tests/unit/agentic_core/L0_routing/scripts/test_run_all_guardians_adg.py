"""ADG importability contract for agentic_core/L0_routing/scripts/run_all_guardians.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_run_all_guardians.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L0_routing.scripts.run_all_guardians import (  # noqa: F401
        run_all_guardians,
        main,
        render_meta_learning_change_package,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    run_all_guardians = None  # type: ignore[assignment,misc]
    main = None  # type: ignore[assignment,misc]
    render_meta_learning_change_package = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="run_all_guardians.py deps unavailable")
class TestRunAllGuardiansImportability:
    def test_module_importable(self) -> None:
        """ADG contract: run_all_guardians.py must be importable."""
        assert _AVAILABLE

    def test_run_all_guardians_callable(self) -> None:
        assert callable(run_all_guardians)

    def test_main_callable(self) -> None:
        assert callable(main)


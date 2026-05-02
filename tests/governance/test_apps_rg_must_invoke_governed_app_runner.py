"""Test 1 — apps_rg/__main__.py must route through the governed substrate.

Fails today because ``apps_rg/__main__.py`` calls
``apps_rg.scripts.generate_resume.main`` directly (the HOP overlay), bypassing
``apps_rg.integrations.governed_rg_run.GovernedRgRun`` (the governed substrate).

Remediation: plan ``apps-rg-governed-runtime-b8d4f1.md`` Wave 7 Phase 7.1.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from tests.governance.conftest import REPO_ROOT


@pytest.mark.governance
@pytest.mark.xfail(
    reason="Governance gap: __main__ calls generate_resume.main, bypassing GovernedRgRun. "
    "Remediation: plan apps-rg-governed-runtime-b8d4f1.md Wave 7 P7.1.",
    strict=True,
)
def test_apps_rg_main_invokes_governed_substrate() -> None:
    main_py = REPO_ROOT / "apps_rg" / "__main__.py"
    assert main_py.exists(), f"missing {main_py}"
    src = main_py.read_text(encoding="utf-8")

    # Forbidden: direct route to the HOP overlay.
    assert "generate_resume.main" not in src and "generate_resume import main" not in src, (
        "apps_rg/__main__.py must NOT route directly to apps_rg.scripts.generate_resume.main "
        "(that path bypasses U0/L1/L0/C0/PA/L2/Exit/UWG/L6 governance)."
    )

    # Required: must invoke the governed substrate.
    assert "GovernedRgRun" in src or "GovernedAppRunner" in src or "integrated_grounded_read_run" in src, (
        "apps_rg/__main__.py must invoke GovernedRgRun, GovernedAppRunner, or "
        "integrated_grounded_read_run (R3 entrypoint) — none found."
    )

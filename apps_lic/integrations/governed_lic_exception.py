"""Compensating-control verifier for the apps_lic governed-run exception."""

from __future__ import annotations

import importlib
import importlib.util
from typing import Callable

ControlResult = tuple[str, bool, str]


class GovernedLicException:
    """Machine-checkable controls for the canonical-dispatch exception."""

    def check_compensating_controls(self) -> list[ControlResult]:
        dispatch = importlib.import_module("apps_lic.runtime.dispatch.canonical_dispatch")
        run_spine = getattr(dispatch, "run_canonical_apps_lic_spine", None)
        legacy_runner_absent = importlib.util.find_spec(
            "apps_lic.integrations.governed_lic_run"
        ) is None
        return [
            (
                "CC-LIC-01",
                callable(run_spine),
                "run_canonical_apps_lic_spine is callable",
            ),
            (
                "CC-LIC-02",
                legacy_runner_absent,
                "legacy GovernedLicRun module remains deleted",
            ),
        ]


__all__ = ["GovernedLicException", "ControlResult"]


"""Legacy headline dispatcher — intentionally unmappable.

The headline lane SSOT lives under ``apps_rg.runtime.sections.headline_lane``.
Canonical CLI route is ``python -m apps_rg --section headline``.
"""

from __future__ import annotations

_MSG = (
    "apps_rg.runtime.dispatch.headline_dispatch was removed as an executable/import SSOT path; "
    "use apps_rg.runtime.sections.headline_lane and python -m apps_rg --section headline."
)


def __getattr__(name: str) -> object:
    raise ImportError(_MSG)


def __dir__() -> list[str]:
    return []


__all__: list[str] = []

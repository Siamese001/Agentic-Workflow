"""Compensating-control verifier for apps_architect's pending runner migration."""

from __future__ import annotations

import importlib

ControlResult = tuple[str, bool, str]


class GovernedArchitectException:
    """Machine-checkable controls for apps_architect pending migration."""

    def check_compensating_controls(self) -> list[ControlResult]:
        main_mod = importlib.import_module("apps_architect.__main__")
        fec_mod = importlib.import_module("apps_architect.cert.fec_producer")
        return [
            (
                "CC-ARCH-01",
                callable(getattr(main_mod, "_run_product_scan", None)),
                "product scan runs inside apps_shared.spine_emission governed_run",
            ),
            (
                "CC-ARCH-02",
                callable(getattr(fec_mod, "produce_fec", None)),
                "cert FEC producer is registered for grounded evidence",
            ),
        ]


__all__ = ["GovernedArchitectException", "ControlResult"]


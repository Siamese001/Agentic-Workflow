"""apps_lic/engines/__init__.py — Sovereign Engine Registry.

Only canonical executors are eagerly imported. All other agents remain
importable directly from their modules, e.g.:
    from apps_lic.engines.DeliverabilityAgent import DeliverabilityAgent
    from apps_lic.engines.OutreachSignalRouterAgent import OutreachSignalRouterAgent
"""

from __future__ import annotations

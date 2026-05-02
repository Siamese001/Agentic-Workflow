"""Static-source scan for runtime-spine wiring signals.

For a given app, scans its top-level entrypoint files (`__main__.py`,
`bootstrap_runtime.py` if present, `engines/`) for either:

  (a) Direct contract use — file mentions canonical contract types
      (RouteContract, L1PlanContract, ExitReviewPacket, etc.)
  (b) Adapter-based wiring — file imports a `governed_run` adapter from
      the app's runtime package.

Either is sufficient evidence that the app is on the spine. Used by the
proof-bundle emitter to compute `app_overlay_authority_status` and add a
blocking gap when neither pattern is present.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from tools.certification.apps_e2e.hash_utils import REPO_ROOT, sha256_file


SIGNAL_KEYS: tuple[str, ...] = (
    "RouteContract",
    "L1PlanContract",
    "L3StepContract",
    "ExitReviewPacket",
    "RuntimeExhaustBundle",
    "SovereignBaseAgent",
    "agentic_core.L0_routing",
    "agentic_core.L3_orchestration",
    "governed_run_adapter",
)


def _scan_one(src: str, app_package: str) -> dict[str, bool]:
    return {
        "RouteContract": "RouteContract" in src,
        "L1PlanContract": "L1PlanContract" in src,
        "L3StepContract": "L3StepContract" in src,
        "ExitReviewPacket": "ExitReviewPacket" in src,
        "RuntimeExhaustBundle": "RuntimeExhaustBundle" in src,
        "SovereignBaseAgent": "SovereignBaseAgent" in src,
        "agentic_core.L0_routing": "from agentic_core.L0_routing" in src,
        "agentic_core.L3_orchestration": "from agentic_core.L3_orchestration" in src,
        "governed_run_adapter": (
            f"from {app_package}.runtime" in src and "governed_run" in src
        ) or (
            f"{app_package}.integrations.governed_" in src
        ),
    }


def scan_app(app_package: str) -> dict[str, dict[str, Any]]:
    """Return signals dict keyed by repo-relative source path.

    Scans:
      - <app>/__main__.py
      - <app>/bootstrap_runtime.py (if exists)
      - <app>/integrations/*.py (if exists)
    """
    out: dict[str, dict[str, Any]] = {}
    candidates: list[Path] = []
    base = REPO_ROOT / app_package
    for rel in ("__main__.py", "bootstrap_runtime.py", "__init__.py"):
        p = base / rel
        if p.exists():
            candidates.append(p)
    integrations = base / "integrations"
    if integrations.is_dir():
        candidates.extend(sorted(integrations.glob("*.py")))

    for p in candidates:
        rel = p.relative_to(REPO_ROOT).as_posix()
        if not p.exists():
            out[rel] = {"exists": False, "signals": {}, "sha256": None}
            continue
        try:
            src = p.read_text(encoding="utf-8")
        except OSError:
            out[rel] = {"exists": True, "signals": {}, "sha256": None, "read_error": True}
            continue
        out[rel] = {
            "exists": True,
            "signals": _scan_one(src, app_package),
            "sha256": sha256_file(p),
        }
    return out


def any_signal_fires(scan: dict[str, dict[str, Any]]) -> bool:
    """True iff any source file shows any spine wiring signal."""
    for entry in scan.values():
        sigs = entry.get("signals") or {}
        if any(sigs.values()):
            return True
    return False


__all__ = ["SIGNAL_KEYS", "scan_app", "any_signal_fires"]

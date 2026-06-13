"""Registry loading for the deterministic harness."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REGISTRY_DIR = Path(__file__).resolve().parent
ALLOWED_APPS = {"apps_rg", "apps_lic"}
OLD_SUITE_NAMES = {
    "routing_enforcement",
    "determinism_contracts",
    "orchestration_hop",
    "output_contracts",
    "exec_brief_generation",
    "ml_metrics_validation",
}


def _load_registry(name: str) -> dict[str, Any]:
    path = REGISTRY_DIR / name
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"registry {name} must contain a mapping")
    return data


def load_apps_registry() -> dict[str, Any]:
    data = _load_registry("apps.yaml")
    apps = data.get("apps", {})
    if set(apps) != ALLOWED_APPS:
        raise ValueError(f"apps registry must contain only {sorted(ALLOWED_APPS)}")
    return apps


def load_suites_registry() -> dict[str, Any]:
    data = _load_registry("suites.yaml")
    suites = data.get("suites", {})
    if not isinstance(suites, dict):
        raise ValueError("suites registry must contain a suites mapping")
    for suite_id, suite in suites.items():
        if suite_id in OLD_SUITE_NAMES:
            raise ValueError(f"old suite name is not allowed: {suite_id}")
        app_id = suite.get("app_id")
        if app_id not in ALLOWED_APPS:
            raise ValueError(f"suite {suite_id} targets unsupported app {app_id}")
    return suites


def load_suite(suite_id: str) -> dict[str, Any]:
    if suite_id in OLD_SUITE_NAMES:
        raise ValueError(f"old suite name is rejected: {suite_id}")
    suites = load_suites_registry()
    if suite_id not in suites:
        raise KeyError(f"unknown suite: {suite_id}")
    suite = dict(suites[suite_id])
    suite["suite_id"] = suite_id
    return suite


def load_graders_registry() -> list[str]:
    data = _load_registry("graders.yaml")
    graders = data.get("graders", [])
    if not isinstance(graders, list) or not all(isinstance(item, str) for item in graders):
        raise ValueError("graders registry must be a list of strings")
    return graders


def load_thresholds_registry() -> dict[str, Any]:
    data = _load_registry("thresholds.yaml")
    thresholds = data.get("thresholds", {})
    if not isinstance(thresholds, dict):
        raise ValueError("thresholds registry must contain a thresholds mapping")
    return thresholds

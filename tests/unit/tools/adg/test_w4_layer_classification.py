"""W4 contract: every apps_* package must be classified as L_APP in the ADG SSOT.

Locks in the W4 invariant: when a new ``apps_<name>/`` package is added to the
repo, it MUST receive a corresponding ``apps_<name>/*: L_APP`` entry in
``tools/adg/adg_layer_overrides.yaml``. Without this, ADG generation classifies
the new app's nodes as ``L_UNKNOWN``, regressing the runtime spine views.

Plan ``apps-runtime-first-principles-e6ba58`` W4.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[4]
LAYER_OVERRIDES_YAML = REPO_ROOT / "tools" / "adg" / "adg_layer_overrides.yaml"


def _load_layer_overrides() -> dict[str, str]:
    with LAYER_OVERRIDES_YAML.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data["overrides"]


def _discover_apps_packages() -> list[str]:
    """Return all ``apps_*`` directory names at the repo root that contain a
    ``__init__.py`` (real Python packages, not stubs)."""
    apps: list[str] = []
    for entry in REPO_ROOT.iterdir():
        if not entry.is_dir():
            continue
        if not entry.name.startswith("apps_"):
            continue
        # Must be a Python package (or contain Python source).
        has_python = any(entry.rglob("*.py"))
        if has_python:
            apps.append(entry.name)
    return sorted(apps)


def test_every_apps_package_is_classified_as_l_app() -> None:
    """W4: every apps_* package must have a yaml override mapping to L_APP."""
    overrides = _load_layer_overrides()
    discovered = _discover_apps_packages()

    missing: list[str] = []
    misclassified: list[tuple[str, str]] = []
    for app in discovered:
        key = f"{app}/*"
        if key not in overrides:
            missing.append(app)
        elif overrides[key] != "L_APP":
            misclassified.append((app, overrides[key]))

    msg_parts = []
    if missing:
        msg_parts.append(
            "Apps packages missing from adg_layer_overrides.yaml (add "
            f"`\"<name>/*\": \"L_APP\"`): {missing}"
        )
    if misclassified:
        msg_parts.append(
            f"Apps packages classified as non-L_APP: {misclassified}"
        )
    assert not msg_parts, "\n".join(msg_parts)


def test_apps_underwriting_ai_explicitly_classified() -> None:
    """W4 regression: apps_underwriting_ai must be present (was the original
    L_UNKNOWN regression in plan apps-runtime-first-principles-e6ba58 §1)."""
    overrides = _load_layer_overrides()
    assert overrides.get("apps_underwriting_ai/*") == "L_APP", (
        "apps_underwriting_ai must be classified as L_APP. "
        "Add `\"apps_underwriting_ai/*\": \"L_APP\"` to "
        "tools/adg/adg_layer_overrides.yaml under `overrides:`."
    )


def test_repair_rule_app_patterns_match_yaml() -> None:
    """W4 consistency: the repair rule's APP_PATTERNS list must cover every
    apps_* package present in the SSOT yaml. Drift between these two
    classifiers caused the original bug."""
    from tools.adg.repair.rules.fix_layer_assignment import FixLayerAssignmentRule

    overrides = _load_layer_overrides()
    yaml_apps = {
        key.removesuffix("/*")
        for key, value in overrides.items()
        if key.startswith("apps_") and value == "L_APP"
    }

    rule_apps = set(FixLayerAssignmentRule.APP_PATTERNS)

    missing_in_rule = yaml_apps - rule_apps
    assert not missing_in_rule, (
        f"FixLayerAssignmentRule.APP_PATTERNS missing apps that are in the SSOT yaml: "
        f"{sorted(missing_in_rule)}"
    )


def test_repair_orchestrator_apps_list_covers_yaml() -> None:
    """W4 consistency: the repair orchestrator's embedded apps tuple must cover
    every apps_* package in the SSOT yaml."""
    import inspect

    from tools.adg.repair import repair_orchestrator

    src = inspect.getsource(repair_orchestrator._RepairOrchestrator._infer_layer_from_path
                            if hasattr(repair_orchestrator, "_RepairOrchestrator")
                            else repair_orchestrator)
    overrides = _load_layer_overrides()
    yaml_apps = {
        key.removesuffix("/*")
        for key, value in overrides.items()
        if key.startswith("apps_") and value == "L_APP"
    }

    missing = [app for app in yaml_apps if f'"{app}"' not in src]
    assert not missing, (
        f"repair_orchestrator._infer_layer_from_path missing apps from SSOT yaml: "
        f"{sorted(missing)}"
    )

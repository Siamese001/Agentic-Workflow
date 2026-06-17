"""apps_rg whole-run path delegates missing briefing to apps_research."""

from __future__ import annotations

import ast
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pytest
import yaml

from agentic_core.L0_routing.u0_intake_validator import AuthorityValidationReceipt
from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest

from apps_rg.runtime.bindings.briefing_u0_signals import BriefingMissingError
from apps_rg.runtime.bindings.l1_binding import l1_plan_apps_rg
from apps_rg.runtime.bindings.u0_profile_manifest import (
    l1_planning_profile_digest,
    l1_planning_profile_ref,
)
from apps_rg.runtime.orchestration.r3r4_whole_run_orchestration import (
    ROUTE_FAMILY_R3R4,
    should_delegate_apps_research,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
ROUTE_PROFILES = REPO_ROOT / "apps_rg" / "config" / "domain_contract" / "route_profiles.yaml"
QUARANTINED = {
    "apps_rg/integrations/apps_research_bridge.py",
    "apps_rg/integrations/managed_research_delegation.py",
}


def _auth() -> AuthorityValidationReceipt:
    return AuthorityValidationReceipt(
        validation_timestamp=datetime.now(timezone.utc).isoformat(),
    )


def _pm() -> dict[str, str]:
    return {
        "l1_planning_profile_ref": l1_planning_profile_ref(),
        "l1_planning_profile_digest": l1_planning_profile_digest(allow_missing=False),
    }


def _vr(app_payload: dict[str, Any]) -> ValidatedRequest:
    return ValidatedRequest(
        request_id="req-research",
        run_id="run-research",
        app_id="apps_rg",
        task_class="resume_generation",
        trace_id="trace-research",
        payload_digest="sha256:test",
        authority_validation_receipt=_auth(),
        l5_certification_ref="test:valid:w6",
        app_payload=app_payload,
    )


def test_route_profiles_contain_no_apps_research_delegated_profile() -> None:
    text = ROUTE_PROFILES.read_text(encoding="utf-8")
    assert "apps_research_delegated_managed" not in text


def test_route_profiles_contain_no_apps_research_required_true_condition() -> None:
    profiles = yaml.safe_load(ROUTE_PROFILES.read_text(encoding="utf-8"))
    assert isinstance(profiles, list)
    for profile in profiles:
        conditions = profile.get("conditions") or {}
        assert conditions.get("apps_research_call_required") is not True


def test_whole_run_delegation_decision_is_enabled_when_briefing_missing() -> None:
    assert (
        should_delegate_apps_research(
            route_family=ROUTE_FAMILY_R3R4,
            manual_brief="",
            auto_research_internal=True,
            research_via="apps_research",
        )
        is True
    )


def test_missing_product_briefing_fails_before_research_delegation(tmp_path: Path) -> None:
    with pytest.raises(BriefingMissingError):
        l1_plan_apps_rg(
            _vr(
                {
                    "task_spec": {"generation_mode": "strategic_tailor"},
                    "profile_manifest": _pm(),
                }
            )
        )
    assert not list(tmp_path.rglob("*delegated_briefing*"))


def test_production_modules_do_not_import_apps_research_delegation_bridges() -> None:
    forbidden_modules = {
        "apps_rg.integrations.apps_research_bridge",
        "apps_rg.integrations.managed_research_delegation",
    }
    offenders: list[str] = []
    for path in sorted((REPO_ROOT / "apps_rg").rglob("*.py")):
        rel = path.relative_to(REPO_ROOT).as_posix()
        if rel in QUARANTINED or "__pycache__" in path.parts:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in forbidden_modules:
                        offenders.append(f"{rel}:{node.lineno}:{alias.name}")
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                if module in forbidden_modules:
                    offenders.append(f"{rel}:{node.lineno}:{module}")
    assert offenders == []

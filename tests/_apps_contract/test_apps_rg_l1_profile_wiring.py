"""p3.1 W2 — U0→L1 planning profile ref + digest wiring."""

from __future__ import annotations

import hashlib

import pytest

from agentic_core.runtime.contracts.apps_rg_ingress_payload import (
    ValidatedRequest,
)
from apps_rg.runtime.bindings.u0_binding import u0_validate_apps_rg
from apps_rg.runtime.bindings.l1_binding import l1_plan_apps_rg
from apps_rg.runtime.bindings.u0_profile_manifest import (
    l1_planning_profile_digest,
    l1_planning_profile_ref,
    repo_root,
)
from apps_rg.runtime.dispatch.apps_rg_dispatch import apps_rg_parse


def test_u0_emits_l1_planning_profile_ref_and_digest() -> None:
    thin = {
        "app_id": "apps_rg",
        "task_class": "resume_generation",
        "target_company": "Acme",
        "target_role": "SWE",
        "source_resume_text": "x",
        "job_description_text": "y",
    }
    env = apps_rg_parse(thin)
    vr = u0_validate_apps_rg(env)
    pm = vr.app_payload["profile_manifest"]
    assert pm["l1_planning_profile_ref"] == l1_planning_profile_ref()
    dig = pm["l1_planning_profile_digest"]
    assert len(dig) == 64
    expected = hashlib.sha256(
        (repo_root() / l1_planning_profile_ref()).read_bytes()
    ).hexdigest()
    assert dig == expected


def test_l1_rejects_digest_mismatch(monkeypatch: pytest.MonkeyPatch) -> None:
    thin = {
        "app_id": "apps_rg",
        "task_class": "resume_generation",
        "target_company": "Acme",
        "target_role": "SWE",
        "source_resume_text": "x",
        "job_description_text": "y",
    }
    env = apps_rg_parse(thin)
    vr = u0_validate_apps_rg(env)
    bad = dict(vr.app_payload)
    pm = dict(bad["profile_manifest"])
    pm["l1_planning_profile_digest"] = "0" * 64
    bad["profile_manifest"] = pm
    vr2 = ValidatedRequest(
        request_id=vr.request_id,
        run_id=vr.run_id,
        app_id=vr.app_id,
        task_class=vr.task_class,
        payload_digest=vr.payload_digest,
        authority_validation_receipt=vr.authority_validation_receipt,
        trace_id=vr.trace_id,
        tenant_id=vr.tenant_id,
        target_level=vr.target_level,
        replay_key=vr.replay_key,
        l5_certification_ref=vr.l5_certification_ref,
        app_payload=bad,
    )
    with pytest.raises(ValueError, match="digest mismatch"):
        l1_plan_apps_rg(vr2)


def test_l1_accepts_matching_digest() -> None:
    thin = {
        "app_id": "apps_rg",
        "task_class": "resume_generation",
        "target_company": "Acme",
        "target_role": "SWE",
        "source_resume_text": "x",
        "job_description_text": "y",
    }
    env = apps_rg_parse(thin)
    vr = u0_validate_apps_rg(env)
    plan = l1_plan_apps_rg(vr)
    assert plan.planning_prior_refs[0] == l1_planning_profile_ref()

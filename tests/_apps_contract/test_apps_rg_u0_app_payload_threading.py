"""apps_rg U0 app_payload — downstream-threading smoke tests.

The companion suite ``test_apps_rg_downstream_field_consumption.py`` proves
the field map status taxonomy is correct. **These** tests prove that on the
LIVE runtime path, key apps_rg fields placed in ``ValidatedRequest.app_payload``
by the harness are reachable in the shape downstream contracts expect for
W2-onward wiring (per Author-Gate decisions AG-3, AG-4, AG-7, AG-8, AG-13,
AG-14).

Coverage:
    1. generation_mode reachable for L1PlanContract / L1 app context
    2. capability_requirements reachable for L0 model_registry routing
    3. prompt_registry_ref reachable for PA template chaining
    4. quality_thresholds reachable for ExitReviewPacket / G22
    5. output_requirements.formats reachable for output callback registry
    6. hitl_policy_ref reachable for HITL registry (AG-13.b)
    7. provenance_requirements reachable for verbatim_provenance_gate
    8. determinism: same envelope → same app_payload digest

These are NOT functional tests — they prove the *plumbing* is in place.
Actual consumption by L1/L0/PA/Exit lands in subsequent waves.

Plan: .windsurf/plans/apps-rg-u0-reflection-live-wiring-105147.md (W4)
"""
from __future__ import annotations

import json
import hashlib
from typing import Any

import pytest

from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest
from agentic_core.runtime.entry.apps_rg_dispatch import apps_rg_parse
from agentic_core.runtime.entry.u0_apps_rg_binding import u0_validate_apps_rg


@pytest.fixture
def vr() -> ValidatedRequest:
    """A live ValidatedRequest produced by the on-the-live-path U0 binding."""

    thin = {
        "app_id": "apps_rg",
        "task_class": "resume_generation",
        "target_company": "Acme Corp",
        "target_role": "Senior Director of AI Engineering",
        "target_level": "EXECUTIVE",
        "source_resume_text": "Amit Ayer — leadership profile content.",
        "job_description_text": "Senior Director of AI Engineering — applied research org.",
        "manual_brief_path": None,
        "auto_research_internal": False,
        "auto_research_tavily": False,
        "research_via": None,
        "output_directory": "artifacts/apps_rg/runs",
        "idempotency_key": None,
    }
    envelope = apps_rg_parse(thin)
    assert envelope is not None
    return u0_validate_apps_rg(envelope)


# ---------------------------------------------------------------------------
# 1. generation_mode reachable for L1PlanContract / L1 app context
# ---------------------------------------------------------------------------


def test_generation_mode_reachable_for_l1(vr: ValidatedRequest) -> None:
    """Per AG-3.a — apps_rg user-chosen mode flows to PA template selection."""

    mode = vr.app_payload["generation_mode"]
    assert mode in {
        "strategic_tailor", "tailor_existing", "generate_scratch",
        "enhance_current", "healing_fact_check", "healing_unsupported_claim",
        "repair",
    }


# ---------------------------------------------------------------------------
# 2. capability_requirements reachable for L0 model_registry routing
# ---------------------------------------------------------------------------


def test_capability_requirements_reachable_for_l0(vr: ValidatedRequest) -> None:
    """Per AG-4.b — apps_rg declares semantic needs; L0 model_registry maps."""

    requirements = vr.app_payload["capability_requirements"]
    assert isinstance(requirements, (list, tuple)), (
        f"capability_requirements must be sequence, got {type(requirements).__name__}"
    )


# ---------------------------------------------------------------------------
# 3. prompt_registry_ref reachable for PA template chaining
# ---------------------------------------------------------------------------


def test_prompt_registry_ref_reachable_for_pa(vr: ValidatedRequest) -> None:
    """Per AG-11.a — PA chaining reads prompt_registry_ref from manifest."""

    ref = vr.app_payload["profile_manifest"]["prompt_registry_ref"]
    assert isinstance(ref, str) and ref.strip()


# ---------------------------------------------------------------------------
# 4. quality_thresholds reachable for ExitReviewPacket / G22
# ---------------------------------------------------------------------------


def test_quality_thresholds_reachable_for_exit_review(vr: ValidatedRequest) -> None:
    """Per AG-7.c + AG-8.c W1 — ExitReviewPacket builder consumes thresholds."""

    thresholds = vr.app_payload["quality_thresholds"]
    assert 0.0 <= thresholds["min_quality"] <= 1.0
    assert 0 <= thresholds["min_ats"] <= 100
    assert thresholds["word_min"] <= thresholds["word_max"]


# ---------------------------------------------------------------------------
# 5. output_requirements.formats reachable for output callback registry
# ---------------------------------------------------------------------------


def test_output_requirements_reachable_for_callback_registry(vr: ValidatedRequest) -> None:
    """Per AG-14.a — apps_rg-owned Exit-stage callbacks dispatch on formats."""

    out_req = vr.app_payload["output_requirements"]
    assert isinstance(out_req["formats"], (list, tuple)) and len(out_req["formats"]) >= 1
    assert isinstance(out_req["provenance_required"], bool)
    assert isinstance(out_req["fact_checked_required"], bool)


# ---------------------------------------------------------------------------
# 6. hitl_policy_ref reachable for HITL registry
# ---------------------------------------------------------------------------


def test_hitl_policy_ref_reachable_for_hitl_registry(vr: ValidatedRequest) -> None:
    """Per AG-13.b — apps_rg-owned HITL emitter registered against this ref."""

    ref = vr.app_payload["profile_manifest"]["hitl_policy_ref"]
    assert isinstance(ref, str) and ref.strip()


# ---------------------------------------------------------------------------
# 7. provenance_requirements reachable for verbatim_provenance_gate
# ---------------------------------------------------------------------------


def test_provenance_requirements_reachable_for_provenance_gate(
    vr: ValidatedRequest,
) -> None:
    """Per AG-9.b — registered apps_rg provenance gate reads these flags."""

    prov = vr.app_payload["provenance_requirements"]
    assert isinstance(prov["per_bullet_required"], bool)
    assert isinstance(prov["source_quote_required"], bool)


# ---------------------------------------------------------------------------
# 8. Determinism — same envelope → same app_payload digest
# ---------------------------------------------------------------------------


def test_app_payload_digest_is_deterministic_across_runs() -> None:
    """Same pinned envelope → identical app_payload canonical digest.

    Determinism is a prerequisite for replay (X1G) — if the same input
    produces a different app_payload, downstream replay verification fails.
    """

    from dataclasses import replace as _replace

    thin = {
        "app_id": "apps_rg", "task_class": "resume_generation",
        "target_company": "Acme", "target_role": "SVP AI",
        "target_level": "EXECUTIVE",
        "source_resume_text": "stable resume content",
        "job_description_text": "stable JD content",
    }
    envelope = apps_rg_parse(thin)
    assert envelope is not None

    pinned: dict[str, str] = {
        "request_id": "rg-req-pin-A", "run_id": "rg-run-pin-A",
        "trace_id": "rg-trace-pin-A", "submitted_at": "2026-05-10T12:00:00+00:00",
        "tenant_id": "apps_rg",
    }
    e1 = _replace(envelope, **pinned)
    e2 = _replace(envelope, **pinned)

    vr1 = u0_validate_apps_rg(e1)
    vr2 = u0_validate_apps_rg(e2)

    def _canon_digest(payload: Any) -> str:
        return hashlib.sha256(
            json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        ).hexdigest()

    assert _canon_digest(dict(vr1.app_payload)) == _canon_digest(dict(vr2.app_payload))


# ---------------------------------------------------------------------------
# Composite — all section pointers reachable in a single sweep
# ---------------------------------------------------------------------------


def test_all_seven_target_sections_reachable_in_one_sweep(vr: ValidatedRequest) -> None:
    """Single test that touches each downstream section, proving the
    harness produced a fully populated app_payload usable by every wave."""

    # Required pointer set per the user's W4 spec.
    accessor_path = [
        "generation_mode",
        "capability_requirements",
        "profile_manifest.prompt_registry_ref",
        "quality_thresholds.min_quality",
        "output_requirements.formats",
        "profile_manifest.hitl_policy_ref",
        "provenance_requirements.per_bullet_required",
    ]

    for path in accessor_path:
        cur: Any = vr.app_payload
        for part in path.split("."):
            assert part in cur, f"missing path component: {part} (full: {path})"
            cur = cur[part]
        assert cur is not None

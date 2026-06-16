"""LinkedIn recruiter apps_lic refactor regression tests."""

from __future__ import annotations

import json
from pathlib import Path

from apps_lic.runtime.bindings.l0_binding import (
    ROUTE_FAMILY_R4_MANAGED_DRAFT,
    ROUTE_FAMILY_R5_FALLBACK,
    l0_route_apps_lic,
)
from apps_lic.runtime.bindings.l1_binding import l1_plan_apps_lic
from apps_lic.runtime.dispatch.canonical_dispatch import (
    build_cli_ingress_raw,
    run_canonical_apps_lic_spine,
)
from apps_lic.runtime.u0.adapter import apps_lic_u0_adapt
from tests.apps_lic.canonical_readiness_fixtures import ready_governed_opportunity_facts


def test_cli_ingress_defaults_to_linkedin_recruiter_and_disables_research() -> None:
    raw = build_cli_ingress_raw(allow_research=True)

    assert raw["campaign"]["request_type"] == "linkedin_recruiter_outreach_draft"
    assert raw["campaign"]["channel"] == "linkedin"
    assert raw["entity_refs"]["lead_profile"]["verified_name"] == "Recruiter"
    assert raw["entity_refs"]["sender_profile"]["name"] == "Amit Ayer"
    assert raw["output_format"]["include_subject_line"] is True
    assert raw["personalization"]["inputs"]["linkedin_route_envelope"]["route"] == "INMAIL"
    assert raw["personalization"]["inputs"]["linkedin_route_envelope"]["channel"] == "linkedin_inmail"

    research = raw["research_requirements"]
    assert research["allow_research"] is False
    assert research["research_disabled_by_policy"] is True
    assert research["requested_but_disabled"] is True
    assert research["apps_research_deprecated"] is True
    assert research["deprecation_reason"] == "APPS_RESEARCH_DEPRECATED"


def test_l0_maps_deprecated_research_request_to_r5() -> None:
    raw = build_cli_ingress_raw(allow_research=True)
    validated, _reflection = apps_lic_u0_adapt(raw)
    plan = l1_plan_apps_lic(validated)
    route = l0_route_apps_lic(plan)

    assert route.route_family == ROUTE_FAMILY_R5_FALLBACK
    assert route.execution_form == "terminal_fallback"
    assert any("research_requested_but_disabled=true" in code for code in route.reason_codes)


def test_deprecated_research_spine_short_circuits_without_execution(tmp_path: Path) -> None:
    raw = build_cli_ingress_raw(allow_research=True)
    result = run_canonical_apps_lic_spine(raw, artifact_root=tmp_path / "r5")

    assert result.terminal_r5 is True
    assert result.route_family == ROUTE_FAMILY_R5_FALLBACK
    assert result.terminal_r5_reason == "APPS_RESEARCH_DEPRECATED"
    assert result.c0_invoked is False
    assert result.pa_invoked is False
    assert result.l3_participated is False
    assert result.l2_executed is False
    assert result.exit_status == "blocked"

    manifest = json.loads((result.artifact_dir / "spine_run_manifest.json").read_text())
    assert manifest["apps_research_invoked"] is False
    assert manifest["r3r4_research_invoked"] is False
    assert manifest["no_send_assertion"] is True
    assert manifest["exit_disposition_receipt_ref"] == "exit_disposition_receipt.json"
    assert (result.artifact_dir / "exit_disposition_receipt.json").is_file()
    assert not (result.artifact_dir / "c0_final_evidence_contract.json").exists()
    assert not (result.artifact_dir / "l2_execution_receipt.json").exists()


def test_manual_brief_r4_uses_frontier_stub_and_l2_hop(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("APPS_LIC_TEST_PROVIDER_STUB", "1")
    raw = build_cli_ingress_raw(
        manual_brief="Recruiter brief for AI engineering leadership roles.",
        governed_opportunity_facts=ready_governed_opportunity_facts(),
    )
    result = run_canonical_apps_lic_spine(raw, artifact_root=tmp_path / "r4")

    assert result.terminal_r5 is False
    assert result.route_family == ROUTE_FAMILY_R4_MANAGED_DRAFT
    assert result.l3_participated is True
    assert result.c0_invoked is True
    assert result.pa_invoked is True
    assert result.l2_executed is True
    assert result.l2_execution_status in {"completed", "completed_with_gate_halt"}

    manifest = json.loads((result.artifact_dir / "spine_run_manifest.json").read_text())
    assert manifest["apps_research_invoked"] is False
    assert manifest["r3r4_research_invoked"] is False
    assert manifest["no_l4_write_assertion"] is True

    l2 = json.loads((result.artifact_dir / "l2_execution_receipt.json").read_text())
    draft = json.loads(l2["payload"]["generated_content"])
    assert draft["channel"] == "linkedin_inmail"
    assert draft["subject_line"]
    assert draft["recipient_class"] == "recruiter"
    assert draft["provider_profile"] == "claude_opus_4_8_primary"
    assert draft["model"] == "Claude Opus 4.8"
    assert len(draft["message_text"]) <= 1900
    assert "—" not in draft["message_text"]


def test_no_live_apps_research_imports_in_apps_lic_runtime_surfaces() -> None:
    roots = [
        Path("apps_lic/runtime"),
        Path("apps_lic/engines"),
        Path("apps_lic/reasoning"),
    ]
    forbidden = ("from apps_research", "import apps_research")
    hits: list[str] = []
    for root in roots:
        for path in root.rglob("*.py"):
            src = path.read_text(encoding="utf-8")
            if any(term in src for term in forbidden):
                hits.append(str(path))
    assert hits == []


def test_l3_boundary_has_no_hop_or_research_execution() -> None:
    src = Path("apps_lic/runtime/bindings/l3_binding.py").read_text(encoding="utf-8")
    forbidden = (
        "from apps_shared.orchestration import HopPipelineExecutor",
        "HopPipelineExecutor(",
        "AppsResearchBridge",
        "dispatch_managed_briefing",
        "from apps_research",
        "import apps_research",
    )
    assert [term for term in forbidden if term in src] == []


def test_provider_profile_documented_in_env_example() -> None:
    src = Path(".env.example").read_text(encoding="utf-8")
    assert "APPS_LIC_GENERATOR_TRANSPORT_MODEL_ID=claude-opus-4-8" in src
    assert "APPS_LIC_GENERATOR_MODEL=Claude Opus 4.8" in src
    assert "APPS_LIC_TEST_PROVIDER_STUB=0" in src

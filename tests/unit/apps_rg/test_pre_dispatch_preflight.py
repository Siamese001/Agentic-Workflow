"""apps-test-model: APP CONTRACT.

Unit tests for centralized pre-dispatch preflight.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from apps_research.integrations.apps_rg_handoff import (
    persist_apps_rg_targeting_brief_artifacts,
)
from apps_rg.runtime.pre_dispatch_preflight import (
    evaluate_jd_cli_input,
    run_pre_dispatch_preflight,
    targeting_override_allowed,
    write_pre_dispatch_preflight_receipt,
)
from apps_rg.runtime.section_cli_defaults import (
    CLI_PROVIDER_RESOLUTION_DEV_DEFAULT_EXTERNAL_CLAUDE,
    CLI_PROVIDER_RESOLUTION_DEV_DEFAULT_EXTERNAL_OPENAI,
)
from tests.unit.apps_research.test_apps_rg_handoff_canonical_exit import _record
from tests.unit.apps_rg.section_rigor.unify_ibm_lane_fixtures import unify_bullets_parsed_from_mock

REPO = Path(__file__).resolve().parents[3]
_FRESH_JD = REPO / "tests" / "_fixtures" / "ci-probe-jd.txt"
_DEFAULT_JD = REPO / "apps_rg" / "config" / "default_jd_targeting.txt"


def test_fresh_jd_fixture_passes() -> None:
    status, _ = evaluate_jd_cli_input(str(_FRESH_JD))
    assert status == "PASS"


def test_default_jd_path_blocked_without_override() -> None:
    status, _ = evaluate_jd_cli_input(str(_DEFAULT_JD))
    assert status == "DEFAULT_BLOCKED"


def test_default_jd_path_allowed_with_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APPS_RG_ALLOW_STALE_TARGETING_SSOT", "1")
    assert targeting_override_allowed()
    status, _ = evaluate_jd_cli_input(str(_DEFAULT_JD))
    assert status == "PASS"


def test_run_preflight_dispatch_false_when_jd_missing() -> None:
    result = run_pre_dispatch_preflight(
        section="competencies",
        jd="",
        manual_brief="Updated briefing for unit test lane validation.",
        lane_provider="external_openai",
        provider_resolution_source=CLI_PROVIDER_RESOLUTION_DEV_DEFAULT_EXTERNAL_OPENAI,
    )
    assert result.dispatch_started is False
    assert result.jd_status == "MISSING"
    assert "targeting" in result.decisive_reason.lower()


def test_provider_readiness_not_applicable_after_local_provider_removal() -> None:
    """Local-provider readiness gate is retired; preflight reports NOT_APPLICABLE."""
    result = run_pre_dispatch_preflight(
        section="headline",
        jd=str(_FRESH_JD),
        manual_brief="Lane briefing with non-default digest for pytest unit scope.",
        lane_provider="external_claude",
        provider_resolution_source=CLI_PROVIDER_RESOLUTION_DEV_DEFAULT_EXTERNAL_CLAUDE,
    )
    assert result.dispatch_started is True
    assert result.provider_health_status == "NOT_APPLICABLE"
    assert result.provider_model_ready_status == "NOT_APPLICABLE"


def _write_apps_research_handoff_v2(tmp_path: Path) -> tuple[Path, Path]:
    bundle = persist_apps_rg_targeting_brief_artifacts(
        record=_record("research-run-preflight"),
        target_company="Anthropic",
        target_role="Manager Applied AI Architecture Partnerships",
        jd_text=_FRESH_JD.read_text(encoding="utf-8"),
        runs_root=tmp_path / "runs",
    )
    assert bundle.normalized_input_path is not None
    return bundle.briefing_path, bundle.normalized_input_path


def test_apps_research_handoff_gate_blocks_digest_mismatch(tmp_path: Path) -> None:
    brief, jd = _write_apps_research_handoff_v2(tmp_path)
    brief.write_text(brief.read_text(encoding="utf-8") + "tampered", encoding="utf-8")

    result = run_pre_dispatch_preflight(
        section="competencies",
        jd=str(jd),
        manual_brief=str(brief),
        lane_provider="mock",
        provider_resolution_source=CLI_PROVIDER_RESOLUTION_DEV_DEFAULT_EXTERNAL_OPENAI,
    )

    assert result.dispatch_started is False
    assert "apps_research handoff gate blocked" in result.decisive_reason
    assert "artifact_" in result.decisive_reason
    assert result.apps_research_handoff_validation is not None
    assert result.apps_research_handoff_validation["status"] == "BLOCKED"


def test_apps_research_handoff_receipts_written(tmp_path: Path) -> None:
    brief, jd = _write_apps_research_handoff_v2(tmp_path)
    result = run_pre_dispatch_preflight(
        section="competencies",
        jd=str(jd),
        manual_brief=str(brief),
        lane_provider="mock",
        provider_resolution_source=CLI_PROVIDER_RESOLUTION_DEV_DEFAULT_EXTERNAL_OPENAI,
    )
    assert result.dispatch_started is True

    receipt_path = tmp_path / "apps_rg_pre_dispatch_preflight.json"
    write_pre_dispatch_preflight_receipt(receipt_path, result)

    validation = json.loads(
        (tmp_path / "apps_research_handoff_validation_receipt.json").read_text(
            encoding="utf-8"
        )
    )
    assert validation["status"] == "PASS"
    assert validation["identity"]["brief_sha256"].startswith("sha256:")
    assert not (tmp_path / "apps_research_briefing_envelope.json").exists()


def test_strict_apps_research_handoff_blocks_static_json() -> None:
    brief = REPO / "tests" / "fixtures" / "apps_rg" / "brief_anthropic_partnerships_2026.json"
    jd = REPO / "apps_rg" / "config" / "targeting" / "jd_anthropic_partnerships_2026.json"

    result = run_pre_dispatch_preflight(
        section="competencies",
        jd=str(jd),
        manual_brief=str(brief),
        lane_provider="mock",
        provider_resolution_source=CLI_PROVIDER_RESOLUTION_DEV_DEFAULT_EXTERNAL_OPENAI,
        require_apps_research_handoff=True,
        require_apps_research_x1_x3=True,
    )

    assert result.dispatch_started is False
    assert "apps_research handoff gate blocked" in result.decisive_reason
    assert "missing_apps_research_handoff_v2" in result.decisive_reason
    assert result.apps_research_handoff_validation is not None
    assert result.apps_research_handoff_validation["valid"] is False


def test_strict_apps_research_handoff_blocks_legacy_v1(tmp_path: Path) -> None:
    brief = tmp_path / "briefing.md"
    jd = tmp_path / "jd.txt"
    brief.write_text("retired legacy handoff", encoding="utf-8")
    jd.write_text(_FRESH_JD.read_text(encoding="utf-8"), encoding="utf-8")
    (tmp_path / "apps_research_briefing_envelope.json").write_text(
        json.dumps({"schema_version": "apps_research.apps_rg_briefing_envelope.v1"}),
        encoding="utf-8",
    )

    result = run_pre_dispatch_preflight(
        section="competencies",
        jd=str(jd),
        manual_brief=str(brief),
        lane_provider="mock",
        provider_resolution_source=CLI_PROVIDER_RESOLUTION_DEV_DEFAULT_EXTERNAL_OPENAI,
        require_apps_research_handoff=True,
        require_apps_research_x1_x3=True,
    )

    assert result.dispatch_started is False
    assert "legacy_only_handoff_rejected" in result.decisive_reason


def test_strict_apps_research_handoff_blocks_stale_v2(tmp_path: Path) -> None:
    past = datetime.now(timezone.utc) - timedelta(days=10)
    brief, jd = _write_apps_research_handoff_v2(tmp_path)
    manifest_path = brief.parent / "apps_research_apps_rg_handoff_v2.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["created_at_utc"] = past.isoformat()
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    result = run_pre_dispatch_preflight(
        section="competencies",
        jd=str(jd),
        manual_brief=str(brief),
        lane_provider="mock",
        provider_resolution_source=CLI_PROVIDER_RESOLUTION_DEV_DEFAULT_EXTERNAL_OPENAI,
        require_apps_research_handoff=True,
        require_apps_research_x1_x3=True,
    )

    assert result.dispatch_started is False
    assert "stale_handoff" in result.decisive_reason


def test_strict_apps_research_handoff_allows_committed_v2(tmp_path: Path) -> None:
    brief, jd = _write_apps_research_handoff_v2(tmp_path)

    result = run_pre_dispatch_preflight(
        section="competencies",
        jd=str(jd),
        manual_brief=str(brief),
        lane_provider="mock",
        provider_resolution_source=CLI_PROVIDER_RESOLUTION_DEV_DEFAULT_EXTERNAL_OPENAI,
        require_apps_research_handoff=True,
        require_apps_research_x1_x3=True,
    )

    assert result.dispatch_started is True
    assert result.apps_research_handoff_validation is not None
    assert result.apps_research_handoff_validation["status"] == "PASS"


def test_narrative_preflight_blocked_without_upstream_bullets(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("APPS_RG_TEST_HARNESS", raising=False)
    empty_modular = (
        REPO / "artifacts" / "apps_rg" / "runtime_proofs" / "contract_harness" / "_modular_narrative_preflight_empty"
    )
    empty_modular.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("APPS_RG_MODULAR_R4_SECTIONS_ROOT", str(empty_modular.resolve()))
    monkeypatch.setattr(
        "apps_rg.runtime.validators.companion_bullet_finalization._l2_from_legacy_stale_fallback",
        lambda *_a, **_k: None,
    )
    result = run_pre_dispatch_preflight(
        section="unify_narrative",
        jd=str(_FRESH_JD),
        manual_brief="Lane briefing with non-default digest for pytest unit scope.",
        lane_provider="mock",
        provider_resolution_source=CLI_PROVIDER_RESOLUTION_DEV_DEFAULT_EXTERNAL_OPENAI,
    )
    assert result.dispatch_started is False
    assert result.upstream_bullets_status == "BLOCKED"
    assert result.upstream_bullets_lane == "unify_bullets"
    assert "UPSTREAM_BULLETS_NOT_FINALIZED" in result.decisive_reason


def test_ibm_narrative_preflight_blocked_without_upstream_bullets(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("APPS_RG_TEST_HARNESS", raising=False)
    empty_modular = (
        REPO
        / "artifacts"
        / "apps_rg"
        / "runtime_proofs"
        / "contract_harness"
        / "_modular_ibm_narrative_preflight_empty"
    )
    empty_modular.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("APPS_RG_MODULAR_R4_SECTIONS_ROOT", str(empty_modular.resolve()))
    monkeypatch.setattr(
        "apps_rg.runtime.validators.companion_bullet_finalization._l2_from_legacy_stale_fallback",
        lambda *_a, **_k: None,
    )
    result = run_pre_dispatch_preflight(
        section="ibm_narrative",
        jd=str(_FRESH_JD),
        manual_brief="Lane briefing with non-default digest for pytest unit scope.",
        lane_provider="mock",
        provider_resolution_source=CLI_PROVIDER_RESOLUTION_DEV_DEFAULT_EXTERNAL_OPENAI,
    )
    assert result.dispatch_started is False
    assert result.upstream_bullets_lane == "ibm_bullets"


def test_narrative_preflight_passes_with_modular_finalized_upstream(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("APPS_RG_TEST_HARNESS", raising=False)
    parsed, _ = unify_bullets_parsed_from_mock()
    sections_root = (
        REPO / "artifacts" / "apps_rg" / "runtime_proofs" / "contract_harness" / "_modular_narrative_preflight"
    )
    sections_root.mkdir(parents=True, exist_ok=True)
    lane_base = sections_root / "unify_bullets"
    run_dir = lane_base / "real" / "unify_bullets_preflight_gate"
    run_dir.mkdir(parents=True, exist_ok=True)
    l2 = {
        "section_id": "unify_bullets",
        "product_quality_status": "PASS",
        "runtime_generation_status": "REAL_LLM",
        "bullets": parsed["bullets"],
    }
    (run_dir / "l2_output.json").write_text(json.dumps(l2), encoding="utf-8")
    (run_dir / "x3_disposition.json").write_text(
        json.dumps({"x3_code": "X3_ALLOW"}),
        encoding="utf-8",
    )
    rel = os.path.relpath(run_dir, REPO).replace("\\", "/")
    (lane_base / "latest_successful_real_run.json").write_text(
        json.dumps({"run_dir": rel}),
        encoding="utf-8",
    )
    monkeypatch.setenv("APPS_RG_MODULAR_R4_SECTIONS_ROOT", str(sections_root.resolve()))
    result = run_pre_dispatch_preflight(
        section="unify_narrative",
        jd=str(_FRESH_JD),
        manual_brief="Lane briefing with non-default digest for pytest unit scope.",
        lane_provider="mock",
        provider_resolution_source=CLI_PROVIDER_RESOLUTION_DEV_DEFAULT_EXTERNAL_OPENAI,
    )
    assert result.upstream_bullets_status == "PASS"
    assert result.upstream_bullets_lane == "unify_bullets"

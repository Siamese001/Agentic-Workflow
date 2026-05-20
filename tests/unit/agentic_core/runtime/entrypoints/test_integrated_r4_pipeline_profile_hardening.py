"""Architectural hardening: R4 integrated path must read apps SSOT profiles in core generically."""
from __future__ import annotations

import re
from pathlib import Path

import pytest

from agentic_core.L3_orchestration.exit_eval.v6.pipeline import _preflight_deny_packet
from agentic_core.L3_orchestration.exit_eval.v6.preflight import (
    PreflightFailure,
    bind_run_identity,
    normalize_to_packet,
    validate_required_receipts,
)
from agentic_core.L3_orchestration.exit_eval.v6.types import GateResult
from agentic_core.L3_orchestration.exit_eval.v6.x1_gates import eval_x1a
from agentic_core.L3_orchestration.exit_eval.v6.x3_dispositions import (
    SPINE_EXIT_V6_PREFLIGHT_DENIAL_CARRIER_REF,
)
from agentic_core.runtime.entrypoints import integrated_single_action_spine_run as r4
from agentic_core.runtime.profiles.profile_resolver import RuntimeProfileResolver


def test_apps_rg_pipeline_defaults_resolves_with_exit_eval_wire() -> None:
    profile = RuntimeProfileResolver().resolve("apps_rg", "pipeline_defaults")
    assert profile.raw_data.get("exit_eval_wire", {}).get("grader_roster")
    assert profile.raw_data["exit_eval_wire"]["spine_exit_packet_carrier_refs"]
    assert profile.typed_payload.get("exit_eval_wire") == profile.raw_data["exit_eval_wire"]


def test_hydrate_raw_request_populates_sha256_when_hashes_absent(tmp_path, monkeypatch) -> None:
    """Digest helper binds file SHAs when raw_request lacks content digests."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "apps_rg").mkdir(parents=True)
    pol = tmp_path / "apps_rg" / "prompt_registry.yaml"
    pol.parent.mkdir(parents=True, exist_ok=True)
    pol.write_text("# fixture policy\n", encoding="utf-8")
    bp = tmp_path / "apps_rg" / "route_profiles.yaml"
    bp.parent.mkdir(parents=True, exist_ok=True)
    bp.write_text("# fixture routes\n", encoding="utf-8")

    raw: dict = {"jd_hash": "a" * 64}
    payload = {
        **RuntimeProfileResolver().resolve("apps_rg", "pipeline_defaults").raw_data,
        "policy_refs": {
            "l0_policy": "apps_rg/prompt_registry.yaml",
            "agent_spec": "apps_rg/route_profiles.yaml",
        },
        "exit_eval_wire": RuntimeProfileResolver()
        .resolve("apps_rg", "pipeline_defaults")
        .raw_data.get("exit_eval_wire"),
    }

    monkeypatch.setattr(r4, "_load_pipeline_defaults_payload", lambda _: payload)
    r4._hydrate_raw_request_evidence_digests(
        raw,
        app_name="apps_rg",
        policy_override="",
        blueprint_override="",
    )
    assert raw["policy_hash"].startswith("sha256:")
    assert raw["blueprint_hash"].startswith("sha256:")
    assert len(raw["policy_hash"]) == 7 + 64


def test_l2_exit_receipt_uses_profile_spine_carriers_not_test_token() -> None:
    receipts = r4._build_l2_exit_receipts(
        run_id="r",
        request_id="q",
        trace_root="t",
        c0_bypass_digest="sha256:ab",
        l2_result={},
        effective_route_id="R4_SINGLE_ACTION",
        route_contract_id="cid",
        replay_key="r4:key",
        policy_digest="sha256:" + "a" * 64,
        blueprint_digest="sha256:" + "b" * 64,
        terminal_class="success",
        app_name="apps_rg",
    )
    assert receipts.get("l5_certification_refs")
    assert "test:valid:w6" not in receipts["l5_certification_refs"]
    assert "apps_rg::spine:r4:l5_packet_carrier" in receipts["l5_certification_refs"][0]


def test_integrated_r4_source_has_no_literal_test_l5_token() -> None:
    """Core must not embed ``test:valid:w6`` as the integrated R4 carrier."""
    src = Path(r4.__file__).read_text(encoding="utf-8")
    assert "test:valid:w6" not in src


def test_integrated_r4_source_has_no_hardcoded_apps_rg_policy_paths() -> None:
    """apps_rg repository paths belong in config/profiles — not string literals in core."""
    src = Path(r4.__file__).read_text(encoding="utf-8")
    without_docs = re.sub(r'""".*?"""', '""', src, flags=re.DOTALL)
    without_docs = re.sub(r"'''.*?'''", "''", without_docs, flags=re.DOTALL)
    assert "apps_rg/prompt_assembly" not in without_docs
    assert "apps_rg/config/" not in without_docs


def test_preflight_deny_uses_structural_spine_carrier_not_test_token() -> None:
    pkt = _preflight_deny_packet(
        {},
        [PreflightFailure(field="policy_hash", reason_code="POLICY_HASH_MISSING")],
    )
    assert pkt.l5_certification_ref == SPINE_EXIT_V6_PREFLIGHT_DENIAL_CARRIER_REF
    assert "test:valid:w6" not in pkt.l5_certification_ref


def test_replay_key_includes_hydrated_policy_blueprint_hashes(tmp_path, monkeypatch) -> None:
    """Hydration must run before replay_key in the pipeline: binding changes when SHAs appear."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "apps_rg" / "prompt_assembly").mkdir(parents=True, exist_ok=True)
    (tmp_path / "apps_rg" / "config" / "domain_contract").mkdir(parents=True, exist_ok=True)
    (tmp_path / "apps_rg" / "prompt_assembly" / "prompt_registry.yaml").write_text(
        "policy: x\n", encoding="utf-8"
    )
    (tmp_path / "apps_rg" / "config" / "domain_contract" / "route_profiles.yaml").write_text(
        "routes: []\n", encoding="utf-8"
    )

    raw: dict[str, str] = {
        "jd_hash": "d" * 64,
        "brief_hash": "e" * 64,
        "resume_hash": "f" * 64,
    }
    key_before = r4._compute_replay_key(raw)
    r4._hydrate_raw_request_evidence_digests(
        raw,
        app_name="apps_rg",
        policy_override="",
        blueprint_override="",
    )
    key_after = r4._compute_replay_key(raw)
    assert raw["policy_hash"].startswith("sha256:")
    assert raw["blueprint_hash"].startswith("sha256:")
    assert key_before != key_after


def test_r5_exit_receipts_satisfy_section_5_0_preflight() -> None:
    """L0 R5 path feeds Exit with the same mandatory receipt fields as L2."""
    rcpt = r4._build_r5_exit_receipts(
        run_id="r1",
        request_id="q1",
        trace_root="t1",
        reason_code="R5_TEST",
        app_name="apps_rg",
        effective_route_id="R4_SINGLE_ACTION",
        route_contract_id="cid-r5",
        replay_key="r4:fixturekey0001",
        policy_digest="sha256:" + "a" * 64,
        blueprint_digest="sha256:" + "b" * 64,
    )
    assert validate_required_receipts(rcpt) == []
    assert bind_run_identity(rcpt) == []
    assert rcpt["terminal_class"] == "failure"
    assert rcpt["route_contract"]["request_id"] == "q1"
    pkt = normalize_to_packet(rcpt)
    assert eval_x1a(pkt).result is GateResult.PASS


def test_l7_disposition_includes_x3d_for_successful_mock_run(tmp_path: Path) -> None:
    """Contract: mock successful runs may surface V6 X3D ALLOW-equivalent disposition."""
    from unittest.mock import MagicMock, patch

    art = tmp_path / "art"
    art.mkdir()
    mock_l2 = MagicMock(return_value={"status": "success"})
    with patch("agentic_core.runtime.l2_recipe_resolver.resolve_l2_recipe") as mock_res:
        mock_res.return_value = mock_l2
        from agentic_core.runtime.entrypoints.integrated_single_action_spine_run import (
            run_integrated_single_action_spine,
        )

        result = run_integrated_single_action_spine(
            raw_request={
                "jd_payload": {"title": "T", "description": "D"},
                "jd_hash": "aa",
                "brief_hash": "bb",
                "resume_hash": "cc",
            },
            app_name="apps_rg",
            artifact_dir=art,
            _test_mode=True,
            l2_callable=mock_l2,
        )
    assert result.fault == ""
    assert result.x3_disposition == "X3D"

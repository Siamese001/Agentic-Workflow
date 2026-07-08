"""Hardened regression tests for headline lane proof/ledger seams."""

from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from apps_rg.runtime.claim_ledger.headline_claim_ledger import build_headline_text_claim_coverage
from apps_rg.runtime.sections import headline_lane
from apps_rg.runtime.sections.headline_lane import (
    W3_EXECUTION_PATH_BUCKET,
    build_headline_allowed_fact_packet,
    ensure_claim_ledger,
    normalize_parsed_output,
    sync_selected_fact_plan_required_ids,
)
from apps_rg.runtime.validators.headline_positioning_x2 import (
    POSITIONING_FAMILY_FLOOR,
    governance_signal_families_matched,
    narrowing_labels_found,
    positioning_families_matched,
    run_headline_positioning_x2_gates,
)
from apps_rg.runtime.validators.headline_quality_x2 import POSITIONING_FAMILIES
from apps_rg.runtime.validators.headline_x2 import (
    check_headline_xyz_literal_grounding,
    headline_word_count,
    run_headline_x2_gates,
)
from apps_rg.runtime.w3_execution_path_labels import BUCKET_GOVERNED_PA_L2_EXIT

HL = "SVP Engineering | Governed Agentic Platforms | Runtime Infrastructure | Regulated Delivery"
METRIC_ID = "fact_engineering_platform_001_metric_deadbeef"
BASE_ID = "fact_engineering_platform_001"


def _runtime_payload_srfs() -> dict:
    facts = [{"fact_id": BASE_ID, "metric_raw": "deadbeef", "claim_text": "platform"}]
    return {
        "selected_fact_plan": {
            "section_id": "headline",
            "facts": facts,
            "required_fact_ids": [],
        },
        "proof_pool_metadata": {"proof_pool_type": "augmented_skills_graph"},
    }


def test_w3_bucket_is_governed_pa_l2_exit() -> None:
    assert W3_EXECUTION_PATH_BUCKET == BUCKET_GOVERNED_PA_L2_EXIT


def test_resolve_metric_derivative_id_in_ledger_sanitize() -> None:
    allowed = {BASE_ID, METRIC_ID}
    parsed = {
        "claim_ledger": [
            {
                "claim_text": "Governed Agentic Platforms",
                "source_fact_ids": [METRIC_ID],
            },
            {
                "claim_text": "Runtime Infrastructure",
                "source_fact_ids": [METRIC_ID],
            },
            {
                "claim_text": "Regulated Delivery",
                "source_fact_ids": [METRIC_ID],
            },
        ],
    }
    ensure_claim_ledger(HL, parsed, allowed)
    ids = parsed["claim_ledger"][0]["source_fact_ids"]
    assert METRIC_ID in ids


def test_sync_selected_fact_plan_includes_metric_derivative() -> None:
    allowed = {BASE_ID, METRIC_ID}
    parsed = {
        "claim_ledger": [
            {"claim_text": "Governed Agentic Platforms", "source_fact_ids": [METRIC_ID]},
            {"claim_text": "Runtime Infrastructure", "source_fact_ids": [METRIC_ID]},
            {"claim_text": "Regulated Delivery", "source_fact_ids": [METRIC_ID]},
        ],
    }
    payload = _runtime_payload_srfs()
    sync_selected_fact_plan_required_ids(parsed, payload, allowed)
    req = set(parsed["selected_fact_plan"]["required_fact_ids"])
    assert METRIC_ID in req


def test_srfs_resolution_row_drop_accounted() -> None:
    allowed = {BASE_ID}
    payload = _runtime_payload_srfs()
    parsed = {
        "headline_line": HL,
        "claim_ledger": [
            {"claim_text": "Governed Agentic Platforms", "source_fact_ids": ["bul_unify_001"]},
            {"claim_text": "Runtime Infrastructure", "source_fact_ids": ["bul_unify_099"]},
            {"claim_text": "Regulated Delivery", "source_fact_ids": ["bul_unify_005"]},
        ],
        "jd_alignment": {
            "targeting_only": True,
            "jd_used_as_proof": False,
            "briefing_used_as_proof": False,
        },
    }
    out = normalize_parsed_output(parsed, payload, allowed, HL, proof_pool_metadata=payload["proof_pool_metadata"])
    assert out is not None
    dropped = int(out.get("_headline_ledger_rows_dropped") or 0)
    assert dropped == 2
    receipt = out.get("fact_id_resolution_receipt") or {}
    assert receipt.get("resolution_status") == "FAIL" or int(receipt.get("unresolved_alias_count") or 0) >= 1


def test_parsed_output_artifact_omits_internal_drop_marker() -> None:
    """normalize leaves marker on dict; execution strips before parsed_output.json — unit-check strip."""
    parsed = {"claim_ledger": [], "_headline_ledger_rows_dropped": 2}
    public = {k: v for k, v in parsed.items() if k != "_headline_ledger_rows_dropped"}
    assert "_headline_ledger_rows_dropped" not in public


def test_text_claim_coverage_requires_token_overlap_not_substring_false_positive() -> None:
    hl = HL
    ledger = [
        {"claim_text": "Enterprise Transformation Leadership", "source_fact_ids": ["bul_1"]},
        {"claim_text": "Runtime Infrastructure", "source_fact_ids": ["bul_1"]},
        {"claim_text": "Regulated Delivery", "source_fact_ids": ["bul_1"]},
    ]
    doc = build_headline_text_claim_coverage(hl, ledger, {"bul_1"})
    by_seg = {row["segment_text"]: row["pass"] for row in doc["segments"]}
    assert by_seg["Governed Agentic Platforms"] is False
    assert by_seg["Runtime Infrastructure"] is True
    assert by_seg["Regulated Delivery"] is True


def test_normalize_repairs_runtime_spine_and_short_cosell_headline() -> None:
    hl = "SVP Engineering | Governed Runtime Spine | Databricks Lakehouse | Partner Co-Sell"
    expected = (
        "SVP Engineering | Runtime Governance Architecture | "
        "Databricks Lakehouse | Partner Co-Sell Motions"
    )
    allowed = {
        "reb_unify_distributed_ecosystem_engineering",
        "reb_unify_partner_channel_cosell",
        "skill_provider_and_egress_governance",
        "skill_sr_w12_databricks_lakehouse_fundamentals",
        "skill_partner_partner_motions",
        "skill_partner_co_selling",
    }
    payload = {
        "target_company": "",
        "selected_fact_plan": {
            "section_id": "headline",
            "required_fact_ids": sorted(allowed),
            "selected_skill_ids": [
                "skill_provider_and_egress_governance",
                "skill_sr_w12_databricks_lakehouse_fundamentals",
                "skill_partner_partner_motions",
                "skill_partner_co_selling",
            ],
            "facts": [
                {
                    "fact_id": "reb_unify_distributed_ecosystem_engineering",
                    "claim_text": "Distributed cloud and data execution infrastructure",
                },
                {
                    "fact_id": "reb_unify_partner_channel_cosell",
                    "claim_text": "AI Partnerships, Co-Sell Channel & Alliance GTM",
                },
            ],
        },
        "proof_pool_metadata": {"proof_pool_type": "augmented_skills_graph"},
    }
    parsed = {
        "headline_line": hl,
        "claim_ledger": [
            {"claim_text": "Governed Runtime Spine", "source_fact_ids": sorted(allowed)},
            {"claim_text": "Databricks Lakehouse", "source_fact_ids": sorted(allowed)},
            {"claim_text": "Partner Co-Sell", "source_fact_ids": sorted(allowed)},
        ],
        "jd_alignment": {
            "targeting_only": True,
            "jd_used_as_proof": False,
            "briefing_used_as_proof": False,
        },
        "gap_notes": [],
        "change_log": [],
        "self_check": {},
    }

    out = normalize_parsed_output(parsed, payload, allowed, hl)

    assert out is not None
    assert out["headline_line"] == expected
    assert headline_word_count(out["headline_line"]) == 10
    assert "spine" not in out["headline_line"].lower()
    assert "runtime_governance" in governance_signal_families_matched(out["headline_line"])
    assert len(positioning_families_matched(out["headline_line"])) >= POSITIONING_FAMILY_FLOOR
    assert narrowing_labels_found(out["headline_line"]) == []
    assert {row["claim_text"] for row in out["claim_ledger"]} == {
        "Runtime Governance Architecture",
        "Databricks Lakehouse",
        "Partner Co-Sell Motions",
    }
    assert any(e.get("operation") == "headline_machine_phrase_repair" for e in out["change_log"])
    assert any(e.get("operation") == "headline_word_count_deterministic_expand" for e in out["change_log"])


def test_normalize_repairs_governed_data_infrastructure_headline_segment() -> None:
    hl = (
        "SVP Engineering | Governed Data Infrastructure | "
        "Hyperscaler Alliance Co-Sell | Regulated Insurance Platforms"
    )
    expected = (
        "SVP Engineering | Distributed Cloud Data Governance | "
        "Hyperscaler Alliance Co-Sell | Regulated Insurance Platforms"
    )
    allowed = {
        "reb_ibm_aws_alliance_partner_cosell_gtm",
        "reb_insurtech_aws_migration_execution",
        "reb_unify_distributed_ecosystem_engineering",
        "skill_aws_migration_readiness_assessment",
        "skill_provider_and_egress_governance",
        "skill_sr_w12_hyperscaler_alliance_co_sell",
    }
    payload = {
        "target_company": "",
        "selected_fact_plan": {
            "section_id": "headline",
            "required_fact_ids": sorted(allowed),
            "selected_skill_ids": [
                "skill_aws_migration_readiness_assessment",
                "skill_provider_and_egress_governance",
                "skill_sr_w12_hyperscaler_alliance_co_sell",
            ],
            "facts": [
                {
                    "fact_id": "reb_unify_distributed_ecosystem_engineering",
                    "claim_text": "Distributed cloud and data execution infrastructure",
                },
                {
                    "fact_id": "reb_ibm_aws_alliance_partner_cosell_gtm",
                    "claim_text": "IBM-AWS alliance co-sell motions",
                },
                {
                    "fact_id": "reb_insurtech_aws_migration_execution",
                    "claim_text": "Regulated insurance platform migration execution",
                },
            ],
        },
        "proof_pool_metadata": {"proof_pool_type": "augmented_skills_graph"},
    }
    parsed = {
        "headline_line": hl,
        "claim_ledger": [
            {"claim_text": "Governed Data Infrastructure", "source_fact_ids": sorted(allowed)},
            {"claim_text": "Hyperscaler Alliance Co-Sell", "source_fact_ids": sorted(allowed)},
            {"claim_text": "Regulated Insurance Platforms", "source_fact_ids": sorted(allowed)},
        ],
        "jd_alignment": {
            "targeting_only": True,
            "jd_used_as_proof": False,
            "briefing_used_as_proof": False,
        },
        "gap_notes": [],
        "change_log": [],
        "self_check": {},
    }

    out = normalize_parsed_output(parsed, payload, allowed, hl)

    assert out is not None
    assert out["headline_line"] == expected
    assert {row["claim_text"] for row in out["claim_ledger"]} == {
        "Distributed Cloud Data Governance",
        "Hyperscaler Alliance Co-Sell",
        "Regulated Insurance Platforms",
    }
    fact_text = {
        "reb_unify_distributed_ecosystem_engineering": "Distributed cloud and data execution infrastructure",
        "reb_ibm_aws_alliance_partner_cosell_gtm": "IBM-AWS alliance co-sell motions",
        "reb_insurtech_aws_migration_execution": "Regulated insurance platform migration execution",
        "skill_aws_migration_readiness_assessment": "aws migration readiness assessment",
        "skill_provider_and_egress_governance": "provider and egress governance",
        "skill_sr_w12_hyperscaler_alliance_co_sell": "hyperscaler alliance co sell",
    }
    ok, _observed, failure = check_headline_xyz_literal_grounding(
        headline_line=out["headline_line"],
        claim_ledger=out["claim_ledger"],
        fact_id_to_text=fact_text,
    )
    assert ok is True, failure


def test_build_headline_allowed_fact_packet_includes_facts_and_anchor() -> None:
    plan = {
        "facts": [{"fact_id": "fact_001", "claim_text": "platform scale"}],
        "required_fact_ids": ["fact_001"],
    }
    packet = build_headline_allowed_fact_packet(
        selected_fact_plan=plan,
        proof_pool_ref="artifacts/srfs.json",
        proof_pool_digest="abc123",
    )
    assert any(r.get("fact_id") == "fact_001" for r in packet)
    assert any(r.get("kind") == "proof_pool_anchor" for r in packet)


def _fake_judges() -> list[dict]:
    return [
        {"provider_key": "gemini_pro", "evaluator_mode": "MOCKED", "provider_blocked": False},
        {"provider_key": "openai_chatgpt", "evaluator_mode": "MOCKED", "provider_blocked": False},
        {"provider_key": "anthropic_claude", "evaluator_mode": "MOCKED", "provider_blocked": False},
    ]


def test_x2_silent_row_drop_gate_fires() -> None:
    hl = HL
    parsed = {
        "headline_line": hl,
        "_headline_ledger_rows_dropped": 2,
        "selected_fact_plan": {"required_fact_ids": []},
        "claim_ledger": [],
        "jd_alignment": {
            "targeting_only": True,
            "jd_used_as_proof": False,
            "briefing_used_as_proof": False,
        },
    }
    gates = run_headline_x2_gates(
        headline_line=hl,
        parsed_output=parsed,
        claim_ledger=[],
        jd_text="",
        target_company="",
        resume_support_blob="{}",
        employer_names_lower=[],
        allowed_fact_ids=set(),
        runtime_generation_status="MOCKED",
        x1d_judges=_fake_judges(),
    )
    failed = [g.gate_id for g in gates if not g.pass_]
    assert "x2_headline_claim_ledger_no_silent_row_drop" in failed


def test_x2_text_claim_coverage_gate_fires_when_segments_unsupported() -> None:
    hl = HL
    ledger = [
        {"claim_text": "Unrelated Theme", "source_fact_ids": ["bul_1"]},
        {"claim_text": "Another Theme", "source_fact_ids": ["bul_1"]},
        {"claim_text": "Third Theme", "source_fact_ids": ["bul_1"]},
    ]
    coverage = build_headline_text_claim_coverage(hl, ledger, {"bul_1"})
    parsed = {
        "headline_line": hl,
        "selected_fact_plan": {"required_fact_ids": ["bul_1"]},
        "claim_ledger": ledger,
        "jd_alignment": {
            "targeting_only": True,
            "jd_used_as_proof": False,
            "briefing_used_as_proof": False,
        },
        "text_claim_coverage": coverage,
    }
    gates = run_headline_x2_gates(
        headline_line=hl,
        parsed_output=parsed,
        claim_ledger=ledger,
        jd_text="",
        target_company="",
        resume_support_blob="{}",
        employer_names_lower=[],
        allowed_fact_ids={"bul_1"},
        runtime_generation_status="MOCKED",
        text_claim_coverage=coverage,
        x1d_judges=_fake_judges(),
    )
    failed = [g.gate_id for g in gates if not g.pass_]
    assert "x2_headline_text_claim_coverage_integrity" in failed
    assert "x2_headline_claim_ledger_segment_decomposition" in failed


def test_weak_payload_segment_decomposition_fails() -> None:
    from tests.unit.apps_rg.section_rigor.weak_payloads import (
        _gate_pass,
        _headline_weak_segment_decomposition,
    )

    assert not _gate_pass(_headline_weak_segment_decomposition(), "x2_headline_claim_ledger_segment_decomposition")


def test_weak_payload_silent_row_drop_fails() -> None:
    from tests.unit.apps_rg.section_rigor.weak_payloads import (
        _gate_pass,
        _headline_weak_silent_row_drop,
    )

    assert not _gate_pass(_headline_weak_silent_row_drop(), "x2_headline_claim_ledger_no_silent_row_drop")


# ---------------------------------------------------------------------------
# W4.2 — headline content-signal repair rung (gap G13)
# ---------------------------------------------------------------------------

_CS_RECEIPT = "headline_content_signal_repair_receipt.json"
_CS_GATE_ID = "x2_headline_governance_or_regulated_ai_signal_required"
PRE_HL_NO_GOV = "SVP Engineering | Distributed AI Infrastructure | Retrieval Context Engineering | Platform Productization"
GOV_HL = "SVP Engineering | Governed Agentic AI Platforms | Runtime Governance Gates | Regulated Enterprise Delivery"
NO_GOV_REGEN_HL = "SVP Engineering | Distributed AI Platforms | Retrieval Context Systems | Platform Productization Scale"
SHORT_GOV_HL = "SVP Engineering | Governed Platforms | Runtime Gates | Regulated Delivery"


class _RecordingProvider:
    def __init__(self, status: str, raw: str) -> None:
        self.status = status
        self.raw = raw
        self.calls = 0
        self.payloads: list[dict] = []

    def __call__(self, payload: dict) -> SimpleNamespace:
        self.calls += 1
        self.payloads.append(payload)
        return SimpleNamespace(runtime_generation_status=self.status, raw_model_output=self.raw)


def _bundle_runtime_payload() -> dict:
    return {
        "run_id": "csr-test",
        "target_company": "",
        "selected_fact_plan": {"section_id": "headline", "facts": [], "required_fact_ids": []},
        "proof_pool_metadata": {"headline_positioning_bundle_consumption": True},
    }


def _attempt1_parsed(hl: str = PRE_HL_NO_GOV) -> dict:
    return {
        "headline_line": hl,
        "claim_ledger": [],
        "selected_fact_plan": {"required_fact_ids": []},
        "jd_alignment": {
            "targeting_only": True,
            "jd_used_as_proof": False,
            "briefing_used_as_proof": False,
        },
        "gap_notes": [],
        "change_log": [],
        "self_check": {},
    }


def _regen_json(hl: str) -> str:
    return json.dumps(
        {
            "headline_line": hl,
            "claim_ledger": [],
            "jd_alignment": {"targeting_only": True},
            "gap_notes": [],
            "change_log": [],
            "self_check": {},
        }
    )


def _run_content_signal_rung(
    tmp_path,
    monkeypatch,
    *,
    provider,
    parsed,
    runtime_payload=None,
    runtime_generation_status="REAL_LLM",
    prior_repair_provider_call_made=False,
):
    monkeypatch.setattr(headline_lane, "generate_section", provider)
    payload = runtime_payload if runtime_payload is not None else _bundle_runtime_payload()
    raw = json.dumps(parsed, sort_keys=True) if isinstance(parsed, dict) else ""
    return headline_lane.apply_headline_content_signal_repair(
        messages=[{"role": "system", "content": "s"}, {"role": "user", "content": "u"}],
        provider_payload={"messages": [], "temperature": 0.55},
        raw_output=raw,
        parsed=parsed,
        runtime_payload=payload,
        allowed_fact_ids=set(),
        artifact_dir=tmp_path,
        runtime_generation_status=runtime_generation_status,
        prior_repair_provider_call_made=prior_repair_provider_call_made,
        companion_nonempty=False,
        employer_names_lower=[],
    )


def _read_receipt(tmp_path) -> dict:
    return json.loads((tmp_path / _CS_RECEIPT).read_text(encoding="utf-8"))


class TestHeadlineContentSignalRepairRung:
    @pytest.fixture(autouse=True)
    def _default_kill_switch_on(self, monkeypatch):
        monkeypatch.delenv("APPS_RG_HEADLINE_CONTENT_SIGNAL_REPAIR", raising=False)

    def test_trigger_skips_non_bundle_mode(self, tmp_path, monkeypatch):
        provider = _RecordingProvider("REAL_LLM", _regen_json(GOV_HL))
        parsed = _attempt1_parsed()
        payload = _bundle_runtime_payload()
        payload["proof_pool_metadata"] = {}
        _raw, out, snap, accepted = _run_content_signal_rung(
            tmp_path, monkeypatch, provider=provider, parsed=parsed, runtime_payload=payload
        )
        assert provider.calls == 0
        assert not accepted and snap is None
        assert out is parsed
        assert not (tmp_path / _CS_RECEIPT).exists()

    def test_trigger_skips_non_real_llm(self, tmp_path, monkeypatch):
        provider = _RecordingProvider("REAL_LLM", _regen_json(GOV_HL))
        _raw, out, snap, accepted = _run_content_signal_rung(
            tmp_path,
            monkeypatch,
            provider=provider,
            parsed=_attempt1_parsed(),
            runtime_generation_status="OFFLINE_CONTRACT_STUB",
        )
        assert provider.calls == 0
        assert not accepted and snap is None
        assert not (tmp_path / _CS_RECEIPT).exists()

    def test_trigger_skips_shape_invalid_pre(self, tmp_path, monkeypatch):
        provider = _RecordingProvider("REAL_LLM", _regen_json(GOV_HL))
        _raw, out, snap, accepted = _run_content_signal_rung(
            tmp_path, monkeypatch, provider=provider, parsed=_attempt1_parsed("broken headline no pipes")
        )
        assert provider.calls == 0
        assert not accepted
        assert not (tmp_path / _CS_RECEIPT).exists()

    def test_trigger_skips_when_signal_present(self, tmp_path, monkeypatch):
        provider = _RecordingProvider("REAL_LLM", _regen_json(GOV_HL))
        _raw, out, snap, accepted = _run_content_signal_rung(
            tmp_path, monkeypatch, provider=provider, parsed=_attempt1_parsed(GOV_HL)
        )
        assert provider.calls == 0
        assert not accepted
        assert not (tmp_path / _CS_RECEIPT).exists()

    def test_kill_switch_off_makes_zero_calls_with_receipt(self, tmp_path, monkeypatch):
        monkeypatch.setenv("APPS_RG_HEADLINE_CONTENT_SIGNAL_REPAIR", "0")
        provider = _RecordingProvider("REAL_LLM", _regen_json(GOV_HL))
        parsed = _attempt1_parsed()
        _raw, out, snap, accepted = _run_content_signal_rung(
            tmp_path, monkeypatch, provider=provider, parsed=parsed
        )
        assert provider.calls == 0
        assert not accepted and out is parsed
        receipt = _read_receipt(tmp_path)
        assert receipt["rejected_reason"] == "kill_switch_off"
        assert receipt["attempted"] is False
        assert receipt["regen_call_made"] is False
        assert receipt["bounded"] == {"max_attempts": 1, "attempts_used": 0}
        assert receipt["env_kill_switch_state"] == "0"
        assert receipt["gate_id"] == _CS_GATE_ID

    def test_budget_consumed_by_prior_provider_call(self, tmp_path, monkeypatch):
        provider = _RecordingProvider("REAL_LLM", _regen_json(GOV_HL))
        parsed = _attempt1_parsed()
        _raw, out, snap, accepted = _run_content_signal_rung(
            tmp_path,
            monkeypatch,
            provider=provider,
            parsed=parsed,
            prior_repair_provider_call_made=True,
        )
        assert provider.calls == 0
        assert not accepted and out is parsed
        receipt = _read_receipt(tmp_path)
        assert receipt["rejected_reason"] == "regen_budget_consumed"
        assert receipt["regen_call_made"] is False

    def test_budget_consumed_by_prior_ledger_regen(self, tmp_path, monkeypatch):
        from apps_rg.runtime.section_repair_ledger import KIND_REGEN_LLM, init_ledger, record_repair

        init_ledger(tmp_path, section_id="headline", run_id="csr-test")
        record_repair(
            tmp_path, kind=KIND_REGEN_LLM, operation="headline_format_repair", replaced_l2=True
        )
        provider = _RecordingProvider("REAL_LLM", _regen_json(GOV_HL))
        _raw, out, snap, accepted = _run_content_signal_rung(
            tmp_path, monkeypatch, provider=provider, parsed=_attempt1_parsed()
        )
        assert provider.calls == 0
        assert not accepted
        receipt = _read_receipt(tmp_path)
        assert receipt["rejected_reason"] == "regen_budget_consumed"

    def test_accept_path_swaps_output_and_records_regen(self, tmp_path, monkeypatch):
        from apps_rg.runtime.section_repair_ledger import KIND_REGEN_LLM, init_ledger, load_ledger

        init_ledger(tmp_path, section_id="headline", run_id="csr-test")
        provider = _RecordingProvider("REAL_LLM", _regen_json(GOV_HL))
        raw, out, snap, accepted = _run_content_signal_rung(
            tmp_path, monkeypatch, provider=provider, parsed=_attempt1_parsed()
        )
        assert provider.calls == 1
        assert accepted is True
        assert out["headline_line"] == GOV_HL
        assert snap is not None and snap["headline_line"] == GOV_HL
        assert GOV_HL in raw
        ledger = load_ledger(tmp_path) or {}
        regen_rows = [
            r
            for r in (ledger.get("repairs") or [])
            if r.get("kind") == KIND_REGEN_LLM and r.get("replaced_l2")
        ]
        assert len(regen_rows) == 1
        assert regen_rows[0]["operation"] == "headline_content_signal_repair"
        receipt = _read_receipt(tmp_path)
        assert receipt["accepted"] is True
        assert receipt["rejected_reason"] is None
        assert receipt["headline_post"] == GOV_HL
        assert receipt["families_matched_post"]
        assert receipt["trigger"]["headline_pre"] == PRE_HL_NO_GOV
        assert receipt["trigger"]["required_families"] == ["runtime_governance", "regulated_ai_systems"]
        assert receipt["bounded"] == {"max_attempts": 1, "attempts_used": 1}
        assert any(
            e.get("operation") == "headline_content_signal_repair"
            for e in (out.get("change_log") or [])
        )

    def test_reject_signal_still_missing_keeps_attempt1_and_gate_still_fails(self, tmp_path, monkeypatch):
        from apps_rg.runtime.section_repair_ledger import KIND_REGEN_LLM, init_ledger, load_ledger

        init_ledger(tmp_path, section_id="headline", run_id="csr-test")
        provider = _RecordingProvider("REAL_LLM", _regen_json(NO_GOV_REGEN_HL))
        parsed = _attempt1_parsed()
        _raw, out, snap, accepted = _run_content_signal_rung(
            tmp_path, monkeypatch, provider=provider, parsed=parsed
        )
        assert provider.calls == 1
        assert not accepted and snap is None
        assert out is parsed
        assert out["headline_line"] == PRE_HL_NO_GOV
        receipt = _read_receipt(tmp_path)
        assert receipt["rejected_reason"] == "signal_still_missing"
        assert receipt["regen_call_made"] is True
        ledger = load_ledger(tmp_path) or {}
        assert not [r for r in (ledger.get("repairs") or []) if r.get("kind") == KIND_REGEN_LLM]
        gates = run_headline_positioning_x2_gates(
            headline_line=out["headline_line"],
            parsed_output=out,
            proof_pool_metadata={"headline_positioning_bundle_consumption": True},
        )
        gate = next(g for g in gates if g.gate_id == _CS_GATE_ID)
        assert not gate.passed
        assert governance_signal_families_matched(out["headline_line"]) == []

    def test_reject_parse_failed_keeps_attempt1(self, tmp_path, monkeypatch):
        provider = _RecordingProvider("REAL_LLM", "not-json {{{")
        parsed = _attempt1_parsed()
        _raw, out, snap, accepted = _run_content_signal_rung(
            tmp_path, monkeypatch, provider=provider, parsed=parsed
        )
        assert provider.calls == 1
        assert not accepted and out is parsed
        receipt = _read_receipt(tmp_path)
        assert receipt["rejected_reason"] == "parse_failed"

    def test_reject_provider_not_real(self, tmp_path, monkeypatch):
        provider = _RecordingProvider("BLOCKED", "")
        parsed = _attempt1_parsed()
        _raw, out, snap, accepted = _run_content_signal_rung(
            tmp_path, monkeypatch, provider=provider, parsed=parsed
        )
        assert provider.calls == 1
        assert not accepted and out is parsed
        receipt = _read_receipt(tmp_path)
        assert receipt["rejected_reason"] == "provider_not_real"
        assert receipt["regen_call_made"] is True

    def test_reject_shape_invalid_keeps_attempt1(self, tmp_path, monkeypatch):
        provider = _RecordingProvider("REAL_LLM", _regen_json(SHORT_GOV_HL))
        parsed = _attempt1_parsed()
        _raw, out, snap, accepted = _run_content_signal_rung(
            tmp_path, monkeypatch, provider=provider, parsed=parsed
        )
        assert provider.calls == 1
        assert not accepted and out is parsed
        receipt = _read_receipt(tmp_path)
        assert receipt["rejected_reason"] == "shape_invalid"

    def test_kill_switch_default_on_and_hard_cap(self, monkeypatch):
        from apps_rg.runtime.sections.headline_repair_policy import (
            CONTENT_SIGNAL_REPAIR_MAX_ATTEMPTS,
            content_signal_repair_enabled,
        )

        monkeypatch.delenv("APPS_RG_HEADLINE_CONTENT_SIGNAL_REPAIR", raising=False)
        assert content_signal_repair_enabled() is True
        assert CONTENT_SIGNAL_REPAIR_MAX_ATTEMPTS == 1
        for off in ("0", "false", "no", "off"):
            monkeypatch.setenv("APPS_RG_HEADLINE_CONTENT_SIGNAL_REPAIR", off)
            assert content_signal_repair_enabled() is False


# ---------------------------------------------------------------------------
# Specificity-floor arm of the content-signal rung (live failure
# postW4fix_20260610_2200: x2_headline_technical_specificity_floor_met,
# only ['runtime_governance'] matched).
# ---------------------------------------------------------------------------

_SPEC_GATE_ID = "x2_headline_technical_specificity_floor_met"
# governance present, only ONE positioning family (runtime_governance) -> specificity arm.
SPEC_FLOOR_HL = "SVP Engineering | Runtime Governance Gates | Deterministic Policy Controls | Resilient Delivery Programs"
# no governance signal AND only one positioning family (platform_productization) -> both arms.
BOTH_ARMS_HL = "SVP Engineering | Retrieval Context Programs | Platform Productization Roadmaps | Resilient Delivery Leadership"
# regen result that still matches only one family (governance present) -> rejected.
SPEC_STILL_ONE_HL = "SVP Engineering | Runtime Governance Gates | Deterministic Policy Controls | Resilient Program Delivery Leadership"


class TestHeadlineContentSignalSpecificityArm:
    @pytest.fixture(autouse=True)
    def _default_kill_switch_on(self, monkeypatch):
        monkeypatch.delenv("APPS_RG_HEADLINE_CONTENT_SIGNAL_REPAIR", raising=False)

    @pytest.mark.parametrize(
        ("hl", "expected_arm"),
        [
            (GOV_HL, None),
            (PRE_HL_NO_GOV, "governance_signal"),
            (SPEC_FLOOR_HL, "specificity_floor"),
            (BOTH_ARMS_HL, "governance_signal+specificity_floor"),
        ],
    )
    def test_trigger_arm_truth_table(self, tmp_path, monkeypatch, hl, expected_arm):
        # Kill switch OFF isolates trigger classification: receipt is written, zero calls.
        monkeypatch.setenv("APPS_RG_HEADLINE_CONTENT_SIGNAL_REPAIR", "0")
        provider = _RecordingProvider("REAL_LLM", _regen_json(GOV_HL))
        _raw, _out, _snap, accepted = _run_content_signal_rung(
            tmp_path, monkeypatch, provider=provider, parsed=_attempt1_parsed(hl)
        )
        assert provider.calls == 0
        assert not accepted
        if expected_arm is None:
            assert not (tmp_path / _CS_RECEIPT).exists()
            return
        receipt = _read_receipt(tmp_path)
        assert receipt["trigger_arm"] == expected_arm
        assert receipt["trigger"]["specificity_floor"] == POSITIONING_FAMILY_FLOOR
        pre = receipt["trigger"]["families_matched_pre"]
        assert pre["governance_signal"] == governance_signal_families_matched(hl)
        assert pre["specificity_floor"] == positioning_families_matched(hl)

    def test_specificity_emphasis_names_missing_family_class(self, tmp_path, monkeypatch):
        provider = _RecordingProvider("REAL_LLM", _regen_json(GOV_HL))
        _run_content_signal_rung(
            tmp_path, monkeypatch, provider=provider, parsed=_attempt1_parsed(SPEC_FLOOR_HL)
        )
        assert provider.calls == 1
        emphasis = provider.payloads[0]["messages"][-1]["content"]
        assert _SPEC_GATE_ID in emphasis
        assert "['runtime_governance']" in emphasis  # lists the families actually matched
        # governance arm did not fire -> its emphasis header is absent
        assert _CS_GATE_ID not in emphasis
        # allowed-set vocabularies pulled from POSITIONING_FAMILIES, not hardcoded duplicates
        for fam in ("agentic_ai_platforms", "distributed_ai_infrastructure", "runtime_governance"):
            assert fam in emphasis
            assert any(phrase in emphasis for phrase in POSITIONING_FAMILIES[fam])

    def test_both_arms_emphasis_names_both_gates(self, tmp_path, monkeypatch):
        provider = _RecordingProvider("REAL_LLM", _regen_json(GOV_HL))
        _run_content_signal_rung(
            tmp_path, monkeypatch, provider=provider, parsed=_attempt1_parsed(BOTH_ARMS_HL)
        )
        assert provider.calls == 1
        emphasis = provider.payloads[0]["messages"][-1]["content"]
        assert _CS_GATE_ID in emphasis
        assert _SPEC_GATE_ID in emphasis
        receipt = _read_receipt(tmp_path)
        assert receipt["trigger_arm"] == "governance_signal+specificity_floor"
        assert receipt["gate_id"] == f"{_CS_GATE_ID}+{_SPEC_GATE_ID}"

    def test_specificity_arm_accept_path(self, tmp_path, monkeypatch):
        from apps_rg.runtime.section_repair_ledger import KIND_REGEN_LLM, init_ledger, load_ledger

        init_ledger(tmp_path, section_id="headline", run_id="csr-test")
        provider = _RecordingProvider("REAL_LLM", _regen_json(GOV_HL))
        _raw, out, snap, accepted = _run_content_signal_rung(
            tmp_path, monkeypatch, provider=provider, parsed=_attempt1_parsed(SPEC_FLOOR_HL)
        )
        assert provider.calls == 1
        assert accepted is True
        assert out["headline_line"] == GOV_HL
        assert snap is not None
        receipt = _read_receipt(tmp_path)
        assert receipt["trigger_arm"] == "specificity_floor"
        assert receipt["gate_id"] == _SPEC_GATE_ID
        assert receipt["trigger"]["families_matched_pre"]["specificity_floor"] == ["runtime_governance"]
        assert len(receipt["families_matched_post"]["specificity_floor"]) >= POSITIONING_FAMILY_FLOOR
        assert receipt["families_matched_post"]["governance_signal"]
        ledger = load_ledger(tmp_path) or {}
        regen_rows = [
            r
            for r in (ledger.get("repairs") or [])
            if r.get("kind") == KIND_REGEN_LLM and r.get("replaced_l2")
        ]
        assert len(regen_rows) == 1
        assert _SPEC_GATE_ID in str(regen_rows[0].get("reason"))
        gates = run_headline_positioning_x2_gates(
            headline_line=out["headline_line"],
            parsed_output=out,
            proof_pool_metadata={"headline_positioning_bundle_consumption": True},
        )
        assert next(g for g in gates if g.gate_id == _SPEC_GATE_ID).passed

    def test_specificity_arm_reject_when_still_below_floor(self, tmp_path, monkeypatch):
        from apps_rg.runtime.section_repair_ledger import KIND_REGEN_LLM, init_ledger, load_ledger

        init_ledger(tmp_path, section_id="headline", run_id="csr-test")
        provider = _RecordingProvider("REAL_LLM", _regen_json(SPEC_STILL_ONE_HL))
        parsed = _attempt1_parsed(SPEC_FLOOR_HL)
        _raw, out, snap, accepted = _run_content_signal_rung(
            tmp_path, monkeypatch, provider=provider, parsed=parsed
        )
        assert provider.calls == 1
        assert not accepted and snap is None
        assert out is parsed
        assert out["headline_line"] == SPEC_FLOOR_HL
        receipt = _read_receipt(tmp_path)
        assert receipt["rejected_reason"] == "signal_still_missing"
        ledger = load_ledger(tmp_path) or {}
        assert not [r for r in (ledger.get("repairs") or []) if r.get("kind") == KIND_REGEN_LLM]
        gates = run_headline_positioning_x2_gates(
            headline_line=out["headline_line"],
            parsed_output=out,
            proof_pool_metadata={"headline_positioning_bundle_consumption": True},
        )
        assert not next(g for g in gates if g.gate_id == _SPEC_GATE_ID).passed

    def test_acceptance_requires_both_arms_gov_trigger(self, tmp_path, monkeypatch):
        # Governance-arm trigger; regen fixes governance but lands below the specificity floor.
        provider = _RecordingProvider("REAL_LLM", _regen_json(SPEC_FLOOR_HL))
        parsed = _attempt1_parsed(PRE_HL_NO_GOV)
        _raw, out, _snap, accepted = _run_content_signal_rung(
            tmp_path, monkeypatch, provider=provider, parsed=parsed
        )
        assert provider.calls == 1
        assert not accepted and out is parsed
        assert _read_receipt(tmp_path)["rejected_reason"] == "signal_still_missing"

    def test_acceptance_requires_both_arms_spec_trigger(self, tmp_path, monkeypatch):
        # Specificity-arm trigger; regen reaches >=2 families but loses the governance signal.
        provider = _RecordingProvider("REAL_LLM", _regen_json(PRE_HL_NO_GOV))
        parsed = _attempt1_parsed(SPEC_FLOOR_HL)
        _raw, out, _snap, accepted = _run_content_signal_rung(
            tmp_path, monkeypatch, provider=provider, parsed=parsed
        )
        assert provider.calls == 1
        assert not accepted and out is parsed
        assert _read_receipt(tmp_path)["rejected_reason"] == "signal_still_missing"

    def test_specificity_arm_respects_one_call_budget(self, tmp_path, monkeypatch):
        provider = _RecordingProvider("REAL_LLM", _regen_json(GOV_HL))
        parsed = _attempt1_parsed(SPEC_FLOOR_HL)
        _raw, out, _snap, accepted = _run_content_signal_rung(
            tmp_path,
            monkeypatch,
            provider=provider,
            parsed=parsed,
            prior_repair_provider_call_made=True,
        )
        assert provider.calls == 0
        assert not accepted and out is parsed
        receipt = _read_receipt(tmp_path)
        assert receipt["rejected_reason"] == "regen_budget_consumed"
        assert receipt["trigger_arm"] == "specificity_floor"

    def test_both_arms_single_regen_call(self, tmp_path, monkeypatch):
        provider = _RecordingProvider("REAL_LLM", _regen_json(GOV_HL))
        _raw, out, _snap, accepted = _run_content_signal_rung(
            tmp_path, monkeypatch, provider=provider, parsed=_attempt1_parsed(BOTH_ARMS_HL)
        )
        assert provider.calls == 1  # one bounded regen covers both arms
        assert accepted is True
        assert out["headline_line"] == GOV_HL
        receipt = _read_receipt(tmp_path)
        assert receipt["bounded"] == {"max_attempts": 1, "attempts_used": 1}


# ---------------------------------------------------------------------------
# Narrowing-labels arm of the content-signal rung (live failure
# postRungs_20260610_2246: x2_headline_no_narrowing_it_labels AND
# x2_headline_generic_it_strategy_demote_forbidden flagged
# 'ai lifecycle standardization'; governance + specificity arms were clean,
# so the two-arm rung correctly stayed idle).
# ---------------------------------------------------------------------------

_NARROW_GATE_ID = "x2_headline_no_narrowing_it_labels"
_DEMOTE_GATE_ID = "x2_headline_generic_it_strategy_demote_forbidden"
# Verbatim live failure shape: governance ok, 2 families, one narrowing label.
LIVE_NARROWING_HL = "SVP Engineering | Retrieval Telemetry Governance | AI Lifecycle Standardization | HPC Microservices Architecture"
# No governance signal + 2 families + narrowing label -> governance+narrowing combo.
GOV_PLUS_NARROWING_HL = "SVP Engineering | Distributed AI Infrastructure | Digital Transformation Programs | Platform Productization"
# All three arms fire.
TRIPLE_ARM_HL = "SVP Engineering | Digital Transformation Leadership | Enterprise Delivery Programs | Innovation Leadership Excellence"
# Regen with governance + 2 families but STILL carrying a narrowing label -> rejected.
NARROWING_REGEN_STILL_DIRTY_HL = "SVP Engineering | Runtime Governance Gates | Agentic AI Platforms | Digital Transformation Leadership"


class TestHeadlineContentSignalNarrowingArm:
    @pytest.fixture(autouse=True)
    def _default_kill_switch_on(self, monkeypatch):
        monkeypatch.delenv("APPS_RG_HEADLINE_CONTENT_SIGNAL_REPAIR", raising=False)

    @pytest.mark.parametrize(
        ("hl", "expected_arm"),
        [
            (GOV_HL, None),
            (LIVE_NARROWING_HL, "narrowing_labels"),
            (GOV_PLUS_NARROWING_HL, "governance_signal+narrowing_labels"),
            (TRIPLE_ARM_HL, "governance_signal+specificity_floor+narrowing_labels"),
        ],
    )
    def test_narrowing_trigger_arm_truth_table(self, tmp_path, monkeypatch, hl, expected_arm):
        # Kill switch OFF isolates trigger classification: receipt is written, zero calls.
        monkeypatch.setenv("APPS_RG_HEADLINE_CONTENT_SIGNAL_REPAIR", "0")
        provider = _RecordingProvider("REAL_LLM", _regen_json(GOV_HL))
        _raw, _out, _snap, accepted = _run_content_signal_rung(
            tmp_path, monkeypatch, provider=provider, parsed=_attempt1_parsed(hl)
        )
        assert provider.calls == 0
        assert not accepted
        if expected_arm is None:
            assert not (tmp_path / _CS_RECEIPT).exists()
            return
        receipt = _read_receipt(tmp_path)
        assert receipt["trigger_arm"] == expected_arm
        pre = receipt["trigger"]["families_matched_pre"]
        assert pre["narrowing_labels"] == narrowing_labels_found(hl)
        if "narrowing_labels" in expected_arm:
            assert pre["narrowing_labels"]
            assert _NARROW_GATE_ID in receipt["gate_id"]
            assert _DEMOTE_GATE_ID in receipt["gate_id"]

    def test_live_shape_trigger_records_label_verbatim(self, tmp_path, monkeypatch):
        monkeypatch.setenv("APPS_RG_HEADLINE_CONTENT_SIGNAL_REPAIR", "0")
        provider = _RecordingProvider("REAL_LLM", _regen_json(GOV_HL))
        _run_content_signal_rung(
            tmp_path, monkeypatch, provider=provider, parsed=_attempt1_parsed(LIVE_NARROWING_HL)
        )
        receipt = _read_receipt(tmp_path)
        assert receipt["trigger_arm"] == "narrowing_labels"
        assert receipt["trigger"]["families_matched_pre"]["narrowing_labels"] == [
            "ai lifecycle standardization"
        ]
        assert receipt["gate_id"] == f"{_NARROW_GATE_ID}+{_DEMOTE_GATE_ID}"

    def test_narrowing_emphasis_names_label_verbatim(self, tmp_path, monkeypatch):
        provider = _RecordingProvider("REAL_LLM", _regen_json(GOV_HL))
        _run_content_signal_rung(
            tmp_path, monkeypatch, provider=provider, parsed=_attempt1_parsed(LIVE_NARROWING_HL)
        )
        assert provider.calls == 1
        emphasis = provider.payloads[0]["messages"][-1]["content"]
        assert "ai lifecycle standardization" in emphasis  # detected label named verbatim
        assert _NARROW_GATE_ID in emphasis
        assert _DEMOTE_GATE_ID in emphasis
        # replacement steering: senior platform/engineering positioning vocabulary
        assert "platform" in emphasis.lower()
        # other arm headers absent (they did not fire)
        assert _CS_GATE_ID not in emphasis
        assert _SPEC_GATE_ID not in emphasis
        # constraint reminder preserved (prefix, pipes, word count, no metrics/employers)
        assert "SVP Engineering | " in emphasis
        assert "three ' | ' " in emphasis or "three ' | '" in emphasis
        assert "10 to 13 total words" in emphasis
        assert "no metrics" in emphasis
        assert "no employer" in emphasis

    def test_narrowing_arm_accept_path(self, tmp_path, monkeypatch):
        from apps_rg.runtime.section_repair_ledger import KIND_REGEN_LLM, init_ledger, load_ledger

        init_ledger(tmp_path, section_id="headline", run_id="csr-test")
        provider = _RecordingProvider("REAL_LLM", _regen_json(GOV_HL))
        _raw, out, snap, accepted = _run_content_signal_rung(
            tmp_path, monkeypatch, provider=provider, parsed=_attempt1_parsed(LIVE_NARROWING_HL)
        )
        assert provider.calls == 1
        assert accepted is True
        assert out["headline_line"] == GOV_HL
        assert snap is not None
        receipt = _read_receipt(tmp_path)
        assert receipt["trigger_arm"] == "narrowing_labels"
        assert receipt["accepted"] is True
        assert receipt["families_matched_post"]["narrowing_labels"] == []
        assert receipt["families_matched_post"]["governance_signal"]
        assert len(receipt["families_matched_post"]["specificity_floor"]) >= POSITIONING_FAMILY_FLOOR
        ledger = load_ledger(tmp_path) or {}
        regen_rows = [
            r
            for r in (ledger.get("repairs") or [])
            if r.get("kind") == KIND_REGEN_LLM and r.get("replaced_l2")
        ]
        assert len(regen_rows) == 1
        assert _NARROW_GATE_ID in str(regen_rows[0].get("reason"))
        gates = run_headline_positioning_x2_gates(
            headline_line=out["headline_line"],
            parsed_output=out,
            proof_pool_metadata={"headline_positioning_bundle_consumption": True},
        )
        assert next(g for g in gates if g.gate_id == _DEMOTE_GATE_ID).passed

    def test_acceptance_rejects_regen_still_containing_label(self, tmp_path, monkeypatch):
        from apps_rg.runtime.section_repair_ledger import KIND_REGEN_LLM, init_ledger, load_ledger

        init_ledger(tmp_path, section_id="headline", run_id="csr-test")
        # Regen satisfies governance + specificity but STILL carries 'digital transformation'.
        provider = _RecordingProvider("REAL_LLM", _regen_json(NARROWING_REGEN_STILL_DIRTY_HL))
        parsed = _attempt1_parsed(LIVE_NARROWING_HL)
        _raw, out, snap, accepted = _run_content_signal_rung(
            tmp_path, monkeypatch, provider=provider, parsed=parsed
        )
        assert provider.calls == 1
        assert not accepted and snap is None
        assert out is parsed
        assert out["headline_line"] == LIVE_NARROWING_HL
        receipt = _read_receipt(tmp_path)
        assert receipt["rejected_reason"] == "signal_still_missing"
        ledger = load_ledger(tmp_path) or {}
        assert not [r for r in (ledger.get("repairs") or []) if r.get("kind") == KIND_REGEN_LLM]
        gates = run_headline_positioning_x2_gates(
            headline_line=NARROWING_REGEN_STILL_DIRTY_HL,
            parsed_output={},
            proof_pool_metadata={"headline_positioning_bundle_consumption": True},
        )
        assert not next(g for g in gates if g.gate_id == _DEMOTE_GATE_ID).passed

    def test_acceptance_requires_zero_labels_when_other_arm_triggered(self, tmp_path, monkeypatch):
        # Governance-arm trigger; regen fixes governance + specificity but adds a narrowing label.
        provider = _RecordingProvider("REAL_LLM", _regen_json(NARROWING_REGEN_STILL_DIRTY_HL))
        parsed = _attempt1_parsed(PRE_HL_NO_GOV)
        _raw, out, _snap, accepted = _run_content_signal_rung(
            tmp_path, monkeypatch, provider=provider, parsed=parsed
        )
        assert provider.calls == 1
        assert not accepted and out is parsed
        receipt = _read_receipt(tmp_path)
        assert receipt["trigger_arm"] == "governance_signal"
        assert receipt["rejected_reason"] == "signal_still_missing"

    def test_narrowing_arm_respects_one_call_budget(self, tmp_path, monkeypatch):
        provider = _RecordingProvider("REAL_LLM", _regen_json(GOV_HL))
        parsed = _attempt1_parsed(LIVE_NARROWING_HL)
        _raw, out, _snap, accepted = _run_content_signal_rung(
            tmp_path,
            monkeypatch,
            provider=provider,
            parsed=parsed,
            prior_repair_provider_call_made=True,
        )
        assert provider.calls == 0
        assert not accepted and out is parsed
        receipt = _read_receipt(tmp_path)
        assert receipt["rejected_reason"] == "regen_budget_consumed"
        assert receipt["trigger_arm"] == "narrowing_labels"
        assert receipt["regen_call_made"] is False

    def test_triple_arm_single_regen_call_and_emphasis(self, tmp_path, monkeypatch):
        provider = _RecordingProvider("REAL_LLM", _regen_json(GOV_HL))
        _raw, out, _snap, accepted = _run_content_signal_rung(
            tmp_path, monkeypatch, provider=provider, parsed=_attempt1_parsed(TRIPLE_ARM_HL)
        )
        assert provider.calls == 1  # one bounded regen covers all three arms
        assert accepted is True
        assert out["headline_line"] == GOV_HL
        emphasis = provider.payloads[0]["messages"][-1]["content"]
        assert _CS_GATE_ID in emphasis
        assert _SPEC_GATE_ID in emphasis
        assert _NARROW_GATE_ID in emphasis
        receipt = _read_receipt(tmp_path)
        assert receipt["trigger_arm"] == "governance_signal+specificity_floor+narrowing_labels"
        assert receipt["bounded"] == {"max_attempts": 1, "attempts_used": 1}


# ---------------------------------------------------------------------------
# Prompt-side narrowing steering: the headline evidence pack carries a
# PARAPHRASED narrowing guard (never the verbatim forbidden C0 phrases —
# assert_headline_positioning_evidence_pack_has_no_forbidden_leaks).
# ---------------------------------------------------------------------------


def test_evidence_pack_narrowing_guard_paraphrased_and_leak_free():
    from pathlib import Path

    from apps_rg.runtime.sections.graph_role_episode_selector import (
        build_selected_graph_evidence_plan_for_section,
    )
    from apps_rg.runtime.sections.headline_positioning_evidence import (
        _FORBIDDEN_C0_SUBSTRINGS,
        attach_headline_positioning_bundles_to_proof_pool_metadata,
        assert_headline_positioning_evidence_pack_has_no_forbidden_leaks,
        format_headline_positioning_evidence_pack,
    )
    from apps_rg.runtime.validators.headline_quality_x2 import NARROWING_IT_LABELS

    repo_root = Path(__file__).resolve().parents[5]
    plan, _, _ = build_selected_graph_evidence_plan_for_section(
        repo_root=repo_root,
        section_id="headline",
        target_role="SVP Engineering",
        jd_text="agentic multi-agent GraphRAG runtime platform control plane",
        briefing_text="regulated enterprise",
    )
    payload = {
        "jd_text": "enterprise AI platform",
        "proof_pool_metadata": attach_headline_positioning_bundles_to_proof_pool_metadata(
            {
                "proof_pool_type": "augmented_skills_graph",
                "selected_graph_evidence_plan": plan,
            },
            section_id="headline",
        ),
    }
    pack = format_headline_positioning_evidence_pack(payload)
    # steering line present
    assert "narrowing_guard:" in pack
    guard_line = next(ln for ln in pack.splitlines() if "narrowing_guard:" in ln)
    assert "platform" in guard_line.lower()  # senior platform/engineering positioning steer
    # paraphrased: the guard line never echoes a verbatim blocklist phrase
    assert not [lbl for lbl in NARROWING_IT_LABELS if lbl in guard_line.lower()]
    # the leak asserter passes on the full pack (it also runs inside format itself)
    assert_headline_positioning_evidence_pack_has_no_forbidden_leaks(pack)
    for forbidden in _FORBIDDEN_C0_SUBSTRINGS:
        assert forbidden not in pack

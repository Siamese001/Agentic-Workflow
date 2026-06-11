"""ibm_narrative theme-overpack repair rung (live flap postW4fix_20260610_2200).

Structural math: the clause decomposer splits on ', establishing' (maxsplit=1 → max 2 ledger
rows) and clause-decomposition allows max 2 bul_ibm_* roots per row → ledger union ≤ 4 roots.
A narrative tripping 5 theme triggers can NEVER pass both x2_ibm_narrative_claim_theme_coverage
and x2_ibm_narrative_claim_ledger_clause_decomposition. The rung is ONE bounded same-authority
regen (headline content-signal idiom, PR #284) with fail-closed acceptance; gates unchanged.
"""
from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from apps_rg.runtime.sections import ibm_narrative_lane_runtime as lane_runtime
from apps_rg.runtime.validators.ibm_narrative_x2 import (
    check_ibm_narrative_claim_ledger_clause_decomposition,
    ibm_narrative_material_fact_ids_for_sentence,
)

_RECEIPT = lane_runtime.THEME_REPAIR_RECEIPT_FILENAME
ALL_IBM_POOL = ["bul_ibm_001", "bul_ibm_002", "bul_ibm_003", "bul_ibm_004", "bul_ibm_005"]

# 5-theme overpack (today's flap shape): clause 1 trips 001/002/004, clause 2 trips 003/005.
OVERPACK_CLAUSE_1 = (
    "At IBM led cloud modernization, lineage and observability programs "
    "for regulated financial services"
)
OVERPACK_CLAUSE_2 = (
    "establishing reusable platform discipline and hyperscaler partnership "
    "execution across complex delivery portfolios"
)
OVERPACK_NARRATIVE = f"{OVERPACK_CLAUSE_1}, {OVERPACK_CLAUSE_2}."

# 4-theme regen within budget: ≤2 theme families per clause (002/004 then 003/005).
GOOD_REGEN_NARRATIVE = (
    "At IBM led cloud modernization and data lineage programs across complex institutions, "
    "establishing reusable platform discipline and hyperscaler partnership execution "
    "for governed delivery."
)

# 3 themes but single clause (no ', establishing') — one row, max 2 roots → coverage must miss one.
SINGLE_CLAUSE_3_THEME_NARRATIVE = (
    "At IBM led cloud modernization with data lineage and hyperscaler partnership programs."
)


def _post_chain_overpack_ledger() -> list[dict]:
    """Attempt-1 ledger as the deterministic chain leaves it: 2 rows, 2 roots each, 004 uncovered."""
    return [
        {"claim_text": OVERPACK_CLAUSE_1, "source_fact_ids": ["bul_ibm_001", "bul_ibm_002"]},
        {"claim_text": OVERPACK_CLAUSE_2, "source_fact_ids": ["bul_ibm_003", "bul_ibm_005"]},
    ]


def _attempt1_parsed(narrative: str = OVERPACK_NARRATIVE, ledger: list[dict] | None = None) -> dict:
    return {
        "narrative_sentence": narrative,
        "claim_ledger": _post_chain_overpack_ledger() if ledger is None else ledger,
        "selected_fact_plan": {"section_id": "ibm_narrative", "facts": []},
        "jd_alignment": {"targeting_only": True, "jd_used_as_proof": False},
        "gap_notes": [],
        "change_log": [],
        "self_check": {},
    }


def _runtime_payload() -> dict:
    return {
        "run_id": "theme-repair-test",
        "allowed_fact_ids": list(ALL_IBM_POOL),
        "selected_fact_plan": {"section_id": "ibm_narrative", "facts": []},
        "proof_pool_metadata": {},
    }


def _regen_json(narrative: str) -> str:
    return json.dumps(
        {
            "narrative_sentence": narrative,
            "selected_fact_plan": {"section_id": "ibm_narrative", "facts": []},
            "claim_ledger": [],
            "jd_alignment": {"targeting_only": True},
            "gap_notes": [],
            "change_log": [],
            "self_check": {},
        }
    )


class _RecordingProvider:
    def __init__(self, status: str, raw: str) -> None:
        self.status = status
        self.raw = raw
        self.calls = 0

    def __call__(self, payload: dict) -> SimpleNamespace:
        self.calls += 1
        self.last_payload = payload
        return SimpleNamespace(runtime_generation_status=self.status, raw_model_output=self.raw)


def _run_rung(
    tmp_path,
    monkeypatch,
    *,
    provider,
    parsed,
    runtime_payload=None,
    runtime_generation_status="REAL_LLM",
):
    monkeypatch.setattr(lane_runtime, "generate_section", provider)
    payload = runtime_payload if runtime_payload is not None else _runtime_payload()
    raw = json.dumps(parsed, sort_keys=True) if isinstance(parsed, dict) else ""
    return lane_runtime.apply_ibm_narrative_theme_overpack_repair(
        messages=[{"role": "system", "content": "s"}, {"role": "user", "content": "u"}],
        provider_payload={"messages": [], "temperature": 0.35},
        raw_output=raw,
        parsed=parsed,
        runtime_payload=payload,
        artifact_dir=tmp_path,
        runtime_generation_status=runtime_generation_status,
    )


def _read_receipt(tmp_path) -> dict:
    return json.loads((tmp_path / _RECEIPT).read_text(encoding="utf-8"))


def test_fixture_sentences_have_expected_theme_counts() -> None:
    """Structural premise of the suite: 5-theme overpack, 4-theme regen, 3-theme single clause."""
    assert ibm_narrative_material_fact_ids_for_sentence(OVERPACK_NARRATIVE) == frozenset(
        ALL_IBM_POOL
    )
    assert ibm_narrative_material_fact_ids_for_sentence(GOOD_REGEN_NARRATIVE) == frozenset(
        {"bul_ibm_002", "bul_ibm_003", "bul_ibm_004", "bul_ibm_005"}
    )
    assert ibm_narrative_material_fact_ids_for_sentence(
        SINGLE_CLAUSE_3_THEME_NARRATIVE
    ) == frozenset({"bul_ibm_002", "bul_ibm_004", "bul_ibm_005"})


class TestThemeOverpackRepairRung:
    @pytest.fixture(autouse=True)
    def _default_kill_switch_on(self, monkeypatch):
        monkeypatch.delenv("APPS_RG_IBM_NARRATIVE_THEME_REPAIR", raising=False)

    def test_trigger_skips_non_real_llm(self, tmp_path, monkeypatch):
        provider = _RecordingProvider("REAL_LLM", _regen_json(GOOD_REGEN_NARRATIVE))
        _raw, out, accepted = _run_rung(
            tmp_path,
            monkeypatch,
            provider=provider,
            parsed=_attempt1_parsed(),
            runtime_generation_status="MOCKED",
        )
        assert provider.calls == 0
        assert not accepted
        assert not (tmp_path / _RECEIPT).exists()

    def test_trigger_skips_when_themes_within_budget_and_covered(self, tmp_path, monkeypatch):
        provider = _RecordingProvider("REAL_LLM", _regen_json(GOOD_REGEN_NARRATIVE))
        parsed = _attempt1_parsed(
            GOOD_REGEN_NARRATIVE,
            ledger=[
                {
                    "claim_text": "At IBM led cloud modernization and data lineage programs",
                    "source_fact_ids": ["bul_ibm_002", "bul_ibm_004"],
                },
                {
                    "claim_text": "establishing reusable platform discipline and hyperscaler partnership execution",
                    "source_fact_ids": ["bul_ibm_003", "bul_ibm_005"],
                },
            ],
        )
        _raw, out, accepted = _run_rung(tmp_path, monkeypatch, provider=provider, parsed=parsed)
        assert provider.calls == 0
        assert not accepted and out is parsed
        assert not (tmp_path / _RECEIPT).exists()

    def test_trigger_skips_srfs_membership_mode(self, tmp_path, monkeypatch):
        import apps_rg.runtime.validators.proof_pool_source_fact_validation as ppv

        monkeypatch.setattr(ppv, "proof_source_from_metadata", lambda _m: "srfs")
        provider = _RecordingProvider("REAL_LLM", _regen_json(GOOD_REGEN_NARRATIVE))
        _raw, out, accepted = _run_rung(
            tmp_path, monkeypatch, provider=provider, parsed=_attempt1_parsed()
        )
        assert provider.calls == 0
        assert not accepted
        assert not (tmp_path / _RECEIPT).exists()

    def test_kill_switch_off_makes_zero_calls_with_receipt(self, tmp_path, monkeypatch):
        monkeypatch.setenv("APPS_RG_IBM_NARRATIVE_THEME_REPAIR", "0")
        provider = _RecordingProvider("REAL_LLM", _regen_json(GOOD_REGEN_NARRATIVE))
        parsed = _attempt1_parsed()
        _raw, out, accepted = _run_rung(tmp_path, monkeypatch, provider=provider, parsed=parsed)
        assert provider.calls == 0
        assert not accepted and out is parsed
        receipt = _read_receipt(tmp_path)
        assert receipt["fired"] is False
        assert receipt["rejected_reason"] == "kill_switch_off"
        assert receipt["kill_switch"] == "0"
        assert receipt["bounded"] == {"max_attempts": 1, "attempts_used": 0}
        assert receipt["trigger"]["count_pre"] == 5
        assert receipt["trigger"]["themes_detected_pre"] == ALL_IBM_POOL
        assert receipt["trigger"]["missing_in_ledger_union_pre"] == ["bul_ibm_004"]

    def test_budget_consumed_by_prior_ledger_regen(self, tmp_path, monkeypatch):
        from apps_rg.runtime.section_repair_ledger import (
            KIND_REGEN_LLM,
            init_ledger,
            record_repair,
        )

        init_ledger(tmp_path, section_id="ibm_narrative", run_id="theme-repair-test")
        record_repair(
            tmp_path,
            kind=KIND_REGEN_LLM,
            operation="companion_metric_budget_regen",
            replaced_l2=True,
        )
        provider = _RecordingProvider("REAL_LLM", _regen_json(GOOD_REGEN_NARRATIVE))
        _raw, out, accepted = _run_rung(
            tmp_path, monkeypatch, provider=provider, parsed=_attempt1_parsed()
        )
        assert provider.calls == 0
        assert not accepted
        receipt = _read_receipt(tmp_path)
        assert receipt["rejected_reason"] == "regen_budget_consumed"
        assert receipt["fired"] is False

    def test_accept_path_swaps_output_records_regen_and_passes_both_predicates(
        self, tmp_path, monkeypatch
    ):
        from apps_rg.runtime.section_repair_ledger import KIND_REGEN_LLM, init_ledger, load_ledger
        from tests.unit.apps_rg.section_rigor.repair_authority import (
            assert_single_repair_authority_path,
        )

        init_ledger(tmp_path, section_id="ibm_narrative", run_id="theme-repair-test")
        provider = _RecordingProvider("REAL_LLM", _regen_json(GOOD_REGEN_NARRATIVE))
        raw, out, accepted = _run_rung(
            tmp_path, monkeypatch, provider=provider, parsed=_attempt1_parsed()
        )
        assert provider.calls == 1
        assert accepted is True
        narrative_post = str(out["narrative_sentence"]).strip()
        themes_post = ibm_narrative_material_fact_ids_for_sentence(narrative_post)
        assert len(themes_post) <= 4
        rows = [r for r in out["claim_ledger"] if isinstance(r, dict)]
        cited = {
            str(s).split("_metric_")[0]
            for r in rows
            for s in (r.get("source_fact_ids") or [])
        }
        assert themes_post <= cited  # theme-coverage predicate
        ok, detail = check_ibm_narrative_claim_ledger_clause_decomposition(narrative_post, rows)
        assert ok is True, detail  # clause-decomposition predicate
        ledger = load_ledger(tmp_path) or {}
        regen_rows = [
            r
            for r in (ledger.get("repairs") or [])
            if r.get("kind") == KIND_REGEN_LLM and r.get("replaced_l2")
        ]
        assert len(regen_rows) == 1
        assert regen_rows[0]["operation"] == "ibm_narrative_theme_overpack_repair"
        ok_auth, reason = assert_single_repair_authority_path(ledger)
        assert ok_auth, reason
        receipt = _read_receipt(tmp_path)
        assert receipt["fired"] is True
        assert receipt["accepted"] is True
        assert receipt["rejected_reason"] is None
        assert receipt["bounded"] == {"max_attempts": 1, "attempts_used": 1}
        assert receipt["themes_post"] == sorted(themes_post)
        assert any(
            e.get("operation") == "ibm_narrative_theme_overpack_repair"
            for e in (out.get("change_log") or [])
        )
        # Precise-miss feedback reached the provider.
        regen_user_msg = provider.last_payload["messages"][-1]["content"]
        assert "5 theme families" in regen_user_msg
        assert "at most 2 per" in regen_user_msg.lower()
        assert "', establishing'" in regen_user_msg

    def test_reject_themes_still_overpacked_keeps_attempt1(self, tmp_path, monkeypatch):
        from apps_rg.runtime.section_repair_ledger import KIND_REGEN_LLM, init_ledger, load_ledger

        init_ledger(tmp_path, section_id="ibm_narrative", run_id="theme-repair-test")
        provider = _RecordingProvider("REAL_LLM", _regen_json(OVERPACK_NARRATIVE))
        parsed = _attempt1_parsed()
        _raw, out, accepted = _run_rung(tmp_path, monkeypatch, provider=provider, parsed=parsed)
        assert provider.calls == 1
        assert not accepted and out is parsed
        assert out["narrative_sentence"] == OVERPACK_NARRATIVE
        receipt = _read_receipt(tmp_path)
        assert receipt["rejected_reason"] == "themes_still_overpacked"
        assert receipt["fired"] is True
        assert receipt["accepted"] is False
        ledger = load_ledger(tmp_path) or {}
        assert not [
            r for r in (ledger.get("repairs") or []) if r.get("kind") == KIND_REGEN_LLM
        ]

    def test_reject_theme_coverage_unsatisfied_keeps_attempt1(self, tmp_path, monkeypatch):
        provider = _RecordingProvider("REAL_LLM", _regen_json(SINGLE_CLAUSE_3_THEME_NARRATIVE))
        parsed = _attempt1_parsed()
        _raw, out, accepted = _run_rung(tmp_path, monkeypatch, provider=provider, parsed=parsed)
        assert provider.calls == 1
        assert not accepted and out is parsed
        receipt = _read_receipt(tmp_path)
        assert receipt["rejected_reason"] == "theme_coverage_unsatisfied"
        assert sorted(receipt["themes_post"]) == ["bul_ibm_002", "bul_ibm_004", "bul_ibm_005"]

    def test_reject_parse_failed_keeps_attempt1(self, tmp_path, monkeypatch):
        provider = _RecordingProvider("REAL_LLM", "not-json {{{")
        parsed = _attempt1_parsed()
        _raw, out, accepted = _run_rung(tmp_path, monkeypatch, provider=provider, parsed=parsed)
        assert provider.calls == 1
        assert not accepted and out is parsed
        receipt = _read_receipt(tmp_path)
        assert receipt["rejected_reason"] == "parse_failed"

    def test_reject_provider_not_real_keeps_attempt1(self, tmp_path, monkeypatch):
        provider = _RecordingProvider("BLOCKED", "")
        parsed = _attempt1_parsed()
        _raw, out, accepted = _run_rung(tmp_path, monkeypatch, provider=provider, parsed=parsed)
        assert provider.calls == 1
        assert not accepted and out is parsed
        receipt = _read_receipt(tmp_path)
        assert receipt["rejected_reason"] == "provider_not_real"
        assert receipt["fired"] is True

    def test_attempt1_failure_shape_still_fails_gate_honestly(self, tmp_path, monkeypatch):
        """Fail-open: rejected regen leaves attempt 1 with the exact live-flap X2 failure."""
        from apps_rg.runtime.validators.ibm_narrative_x2 import (
            _ledger_fact_ids,
        )

        provider = _RecordingProvider("BLOCKED", "")
        parsed = _attempt1_parsed()
        _raw, out, accepted = _run_rung(tmp_path, monkeypatch, provider=provider, parsed=parsed)
        assert not accepted
        themes = ibm_narrative_material_fact_ids_for_sentence(out["narrative_sentence"])
        cited = {s for s in _ledger_fact_ids(out["claim_ledger"]) if s.startswith("bul_ibm_")}
        assert sorted(themes - cited) == ["bul_ibm_004"]  # theme-coverage gate still fails

    def test_kill_switch_default_on_and_hard_cap(self, monkeypatch):
        from apps_rg.runtime.sections.ibm_narrative_repair_policy import (
            THEME_REPAIR_MAX_ATTEMPTS,
            theme_repair_enabled,
        )

        monkeypatch.delenv("APPS_RG_IBM_NARRATIVE_THEME_REPAIR", raising=False)
        assert theme_repair_enabled() is True
        assert THEME_REPAIR_MAX_ATTEMPTS == 1
        for off in ("0", "false", "no", "off"):
            monkeypatch.setenv("APPS_RG_IBM_NARRATIVE_THEME_REPAIR", off)
            assert theme_repair_enabled() is False


class TestThemeBudgetPromptContract:
    def _i0(self) -> str:
        from apps_rg.runtime.sections.ibm_narrative_pa import _i0_from_spec

        return _i0_from_spec(
            {
                "ibm_header": {
                    "employer": "IBM",
                    "title": "Lead Client Partner",
                    "location": "Edgewater, NJ",
                    "start_date": "2017-04",
                    "end_date": "2022-10",
                },
                "allowed_fact_ids": list(ALL_IBM_POOL),
            }
        )

    def test_prompt_states_structural_theme_budget(self):
        i0 = self._i0()
        assert "THEME BUDGET (STRUCTURAL" in i0
        assert "AT MOST 4 of the 5 IBM bullet theme" in i0
        assert "AT MOST 2 theme families per clause" in i0
        assert "', establishing'" in i0

    def test_prompt_theme_families_derive_from_gate_triggers(self):
        from apps_rg.runtime.validators.ibm_narrative_x2 import IBM_NARRATIVE_THEME_TRIGGERS

        i0 = self._i0()
        for fid, phrases in IBM_NARRATIVE_THEME_TRIGGERS:
            assert f"- {fid}:" in i0
            # At least one trigger phrase from each family is summarized in the prompt.
            assert any(p in i0 for p in phrases), fid

    def test_prompt_does_not_dump_full_trigger_lists(self):
        from apps_rg.runtime.validators.ibm_narrative_x2 import IBM_NARRATIVE_THEME_TRIGGERS

        i0 = self._i0()
        budget_block = i0.split("THEME BUDGET (STRUCTURAL", 1)[1]
        budget_block = budget_block.split("\n\n", 1)[0]
        for _fid, phrases in IBM_NARRATIVE_THEME_TRIGGERS:
            present = sum(1 for p in phrases if p in budget_block)
            assert present <= 3, _fid

    def test_yaml_spec_carries_same_budget_statement(self):
        from apps_rg.runtime.sections.ibm_narrative_pa import _ibm_position_narrative_spec

        contract = str(_ibm_position_narrative_spec().get("claim_ledger_coverage_contract") or "")
        assert "STRUCTURAL THEME BUDGET" in contract
        assert "AT MOST 4 of the 5 theme families" in contract

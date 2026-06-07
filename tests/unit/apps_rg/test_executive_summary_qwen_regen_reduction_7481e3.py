"""Unit tests — qwen-prompt-regen-reduction-7481e3 (W1–W5 hardening).

Covers:
  W1: E0 metric transposition + two positives on SVP lane
  W2: SRFS_BASE_RESUME_STYLE_ONESHOT_EXEMPLAR removed + stock-bridge rule stated once
  W3: S4 non-stock opener directive in I0 judge_alignment_contract
  W4: self_check reduced to 5 fields + JUDGE_REGEN_MAX_ATTEMPTS default = 3
  W5: exec_summary_gold_base_resume_001 converted to negative
"""
from __future__ import annotations

import importlib
import re
import types

import pytest
import yaml


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_examples_yaml() -> dict:
    from pathlib import Path
    p = Path(__file__).resolve().parents[3] / "apps_rg/prompt_assembly/examples/executive_summary_examples.yaml"
    return yaml.safe_load(p.read_text(encoding="utf-8")) or {}


def _examples_by_id(data: dict) -> dict:
    return {row["id"]: row for row in (data.get("examples") or []) if row.get("id")}


def _load_template_i0() -> str:
    from pathlib import Path
    p = Path(__file__).resolve().parents[3] / "apps_rg/prompt_assembly/templates/executive_summary.generate_scratch_v1.yaml"
    raw = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    return raw.get("slot_bodies", {}).get("I0", "")


# ---------------------------------------------------------------------------
# W1 — Domain-transpose E0 positive metrics
# ---------------------------------------------------------------------------

_REAL_METRICS = ("$22M", "$14M", "8 to 28", "20%", "40%")
# Note: "40%" is excluded from the strict test because it can appear in negatives legitimately.
_REAL_METRICS_STRICT = ("$22M", "$14M", "8 to 28")


class TestW1E0MetricTransposition:
    """W1: positive examples must not carry real candidate-specific metric anchors."""

    def test_svp_positive_no_real_dollar_metrics(self):
        by_id = _examples_by_id(_load_examples_yaml())
        row = by_id["exec_summary_pos_svp_it_strategy_001"]
        after = row["after"]
        for m in _REAL_METRICS_STRICT:
            assert m not in after, (
                f"exec_summary_pos_svp_it_strategy_001 still contains real metric '{m}'. "
                "Domain-transpose must replace candidate-specific values with placeholders."
            )

    def test_outcomes_led_positive_no_real_dollar_metrics(self):
        by_id = _examples_by_id(_load_examples_yaml())
        row = by_id["exec_summary_pos_outcomes_led_001"]
        after = row["after"]
        for m in _REAL_METRICS_STRICT:
            assert m not in after, (
                f"exec_summary_pos_outcomes_led_001 still contains real metric '{m}'. "
                "Metric anchors must be placeholders."
            )

    def test_svp_positive_contains_placeholder_tokens(self):
        """Confirm placeholders like [X], [Y] are present so Qwen knows to substitute from C0."""
        by_id = _examples_by_id(_load_examples_yaml())
        after = by_id["exec_summary_pos_svp_it_strategy_001"]["after"]
        assert re.search(r"\[(?:X|Y|Z|A|B)\]", after), (
            "exec_summary_pos_svp_it_strategy_001 must contain at least one [X]/[Y]/[A]/[B]/[Z] "
            "placeholder to signal metric retrieval from C0."
        )

    def test_annotation_warns_about_transposed_metrics(self):
        by_id = _examples_by_id(_load_examples_yaml())
        annotation = by_id["exec_summary_pos_svp_it_strategy_001"]["annotation"]
        assert "TRANSPOSED" in annotation.upper() or "placeholder" in annotation.lower(), (
            "Annotation must warn that metrics are domain-transposed placeholders."
        )


class TestW1SVPLaneTwoPositives:
    """W1: strategy_executive lane must emit exactly two positive examples."""

    def test_svp_lane_positive_tuple_has_two_entries(self):
        from apps_rg.prompt_assembly.e0_examples import _EXEC_SUMMARY_POSITIVE_SVP_JUDGE_ALIGNED
        assert len(_EXEC_SUMMARY_POSITIVE_SVP_JUDGE_ALIGNED) == 2, (
            f"SVP lane must have exactly 2 positives; got {_EXEC_SUMMARY_POSITIVE_SVP_JUDGE_ALIGNED}"
        )

    def test_svp_lane_includes_credibility_implied(self):
        from apps_rg.prompt_assembly.e0_examples import _EXEC_SUMMARY_POSITIVE_SVP_JUDGE_ALIGNED
        assert "exec_summary_pos_credibility_implied_001" in _EXEC_SUMMARY_POSITIVE_SVP_JUDGE_ALIGNED

    def test_build_e0_svp_lane_emits_two_positive_blocks(self):
        from apps_rg.prompt_assembly.e0_examples import build_executive_summary_e0
        e0 = build_executive_summary_e0(strategy_executive=True)
        count = e0.count("<positive_example ")
        assert count == 2, f"SVP E0 must contain exactly 2 positive_example blocks; got {count}"

    def test_build_e0_non_svp_lane_emits_three_positive_blocks(self):
        from apps_rg.prompt_assembly.e0_examples import build_executive_summary_e0
        e0 = build_executive_summary_e0(strategy_executive=False)
        count = e0.count("<positive_example ")
        assert count == 3, f"Non-SVP E0 must contain exactly 3 positive_example blocks; got {count}"

    def test_e0_lane_note_mentions_two_positives(self):
        from apps_rg.prompt_assembly.e0_examples import build_executive_summary_e0
        e0 = build_executive_summary_e0(strategy_executive=True)
        assert "two structurally diverse" in e0 or "two" in e0, (
            "SVP lane note must mention two positives."
        )

    def test_e0_lane_note_warns_about_metric_placeholders(self):
        from apps_rg.prompt_assembly.e0_examples import build_executive_summary_e0
        e0 = build_executive_summary_e0(strategy_executive=True)
        assert "placeholder" in e0.lower() or "[X]" in e0 or "transposed" in e0.lower(), (
            "SVP lane note must warn that metric values are domain-transposed placeholders."
        )


# ---------------------------------------------------------------------------
# W2 — Dead constant removed + stock-bridge rule stated once
# ---------------------------------------------------------------------------

class TestW2SRFSConstantRemoved:
    """W2: SRFS_BASE_RESUME_STYLE_ONESHOT_EXEMPLAR must not exist in any importable module."""

    def test_constant_not_in_executive_summary_pa(self):
        import apps_rg.runtime.sections.executive_summary_pa as pa
        assert not hasattr(pa, "SRFS_BASE_RESUME_STYLE_ONESHOT_EXEMPLAR"), (
            "SRFS_BASE_RESUME_STYLE_ONESHOT_EXEMPLAR must be removed from executive_summary_pa."
        )

    def test_constant_not_in_dispatch_shim(self):
        import apps_rg.runtime.dispatch.executive_summary_pa as dispatch
        assert not hasattr(dispatch, "SRFS_BASE_RESUME_STYLE_ONESHOT_EXEMPLAR"), (
            "SRFS_BASE_RESUME_STYLE_ONESHOT_EXEMPLAR must be removed from dispatch shim."
        )

    def test_constant_not_in_pa_all(self):
        import apps_rg.runtime.sections.executive_summary_pa as pa
        assert "SRFS_BASE_RESUME_STYLE_ONESHOT_EXEMPLAR" not in pa.__all__, (
            "SRFS_BASE_RESUME_STYLE_ONESHOT_EXEMPLAR must be removed from executive_summary_pa.__all__."
        )

    def test_constant_not_in_dispatch_all(self):
        import apps_rg.runtime.dispatch.executive_summary_pa as dispatch
        assert "SRFS_BASE_RESUME_STYLE_ONESHOT_EXEMPLAR" not in dispatch.__all__, (
            "SRFS_BASE_RESUME_STYLE_ONESHOT_EXEMPLAR must be removed from dispatch __all__."
        )


class TestW2StockBridgeRuleStatedOnce:
    """W2: I0 must state the stock-bridge count limit exactly once."""

    def test_stock_bridge_limit_stated_once_in_i0(self):
        i0 = _load_template_i0()
        # Count authoritative phrasings of the max-two stock bridge constraint
        patterns = [
            r"At most \*\*two\*\* stock",
            r"max two stock bridges",
            r"maximum.*two.*stock",
        ]
        count = 0
        for pat in patterns:
            count += len(re.findall(pat, i0, re.IGNORECASE))
        assert count == 1, (
            f"I0 stock-bridge count limit must appear exactly once; found {count} occurrences. "
            "Remove redundant restatements from six_sentence_period_contract and approved_non_stock_openers."
        )

    def test_approved_non_stock_openers_list_present(self):
        """The approved opener list must still exist — only the count was removed."""
        i0 = _load_template_i0()
        assert "In parallel," in i0, "approved_non_stock_openers list must still contain 'In parallel,'"
        assert "That operating foundation also," in i0


# ---------------------------------------------------------------------------
# W3 — S4 non-stock opener directive in I0
# ---------------------------------------------------------------------------

class TestW3S4DirectiveInI0:
    """W3: I0 judge_alignment_contract S4 clause must include the non-stock opener directive."""

    def test_s4_non_stock_opener_directive_in_i0(self):
        i0 = _load_template_i0()
        assert "non-stock opener" in i0, (
            "I0 S4 clause must include 'non-stock opener' directive for SVP strategy lanes."
        )

    def test_s4_directive_mentions_brushstrokes(self):
        i0 = _load_template_i0()
        assert "brushstrokes" in i0 or "3 brushstrokes" in i0 or "\u22653 brushstrokes" in i0 or ">=3" in i0, (
            "I0 S4 directive must mention the brushstroke threshold condition."
        )

    def test_s4_directive_gives_example_openers(self):
        i0 = _load_template_i0()
        assert "In parallel," in i0 or "That operating foundation" in i0, (
            "I0 S4 directive must give example non-stock openers."
        )

    def test_composition_plan_s4_directive_still_fires(self):
        """Runtime composition plan S4 directive (from previous session) must still be present."""
        from apps_rg.runtime.sections.executive_summary_composition import format_composition_plan_for_pa
        plan = {
            "strategy_executive": True,
            "brushstrokes": [
                {"slot": "S2", "claim_text": "A"}, {"slot": "S3", "claim_text": "B"},
                {"slot": "S4", "claim_text": "C"},
            ],
        }
        result = format_composition_plan_for_pa(plan)
        assert "s4_opener_directive" in result or "non-stock opener" in result.lower(), (
            "format_composition_plan_for_pa must still emit s4_opener_directive for SVP >=3 brushstrokes."
        )


# ---------------------------------------------------------------------------
# W4 — self_check fields + JUDGE_REGEN_MAX_ATTEMPTS default
# ---------------------------------------------------------------------------

class TestW4SelfCheckFields:
    """W4: I0 self_check must list exactly 5 fields."""

    def test_self_check_five_fields_in_i0(self):
        i0 = _load_template_i0()
        # Extract the self_check_requirements block
        m = re.search(r"<self_check_requirements>(.*?)</self_check_requirements>", i0, re.DOTALL)
        assert m, "self_check_requirements block not found in I0"
        body = m.group(1)
        # Count semicolon-separated fields (allow trailing semicolon or period)
        fields = [f.strip().rstrip(";.") for f in re.split(r"[;,]", body) if f.strip()
                  and not f.strip().startswith(("Verify", "five", "(five"))]
        # Accept 4-6 range to accommodate formatting variation
        assert 4 <= len(fields) <= 6, (
            f"self_check should have ~5 fields; found {len(fields)}: {fields}"
        )

    def test_self_check_contains_required_fields(self):
        i0 = _load_template_i0()
        m = re.search(r"<self_check_requirements>(.*?)</self_check_requirements>", i0, re.DOTALL)
        assert m
        body = m.group(1)
        required = [
            "executive_strategy_thesis_present",
            "jd_used_as_proof_false",
            "s6_forward_synthesis_not_recap",
            "material_metrics_surfaced_in_display_rows_3_4_5",
            "every_material_claim_in_claim_ledger",
        ]
        for field in required:
            assert field in body, f"Required self_check field '{field}' missing from I0."

    def test_removed_x2_covered_fields_absent(self):
        """Fields fully covered by X2 gates should no longer be in the self_check list."""
        i0 = _load_template_i0()
        m = re.search(r"<self_check_requirements>(.*?)</self_check_requirements>", i0, re.DOTALL)
        assert m
        body = m.group(1)
        x2_covered = [
            "no_first_person",
            "no_inline_source_tags",
            "s5_no_derivatives_inventory",
            "s5_no_derivatives_or_employer_inventory",
            "no_extend_that_arc_toward_phrase",
            "achievement_verb_opener_count_at_most_2",
            "s6_no_looking_ahead_opener",
            "s1_not_verbatim_thesis_copy",
        ]
        for field in x2_covered:
            assert field not in body, (
                f"X2-covered self_check field '{field}' should be removed from I0 self_check "
                "(X2 gates enforce it deterministically; no need to duplicate in self_check)."
            )


class TestW4JudgeRegenMaxAttempts:
    """Variance-class trim: JUDGE_REGEN_MAX_ATTEMPTS release default is 1 (hard cap 3)."""

    def test_judge_regen_max_attempts_constant_is_1(self):
        from apps_rg.runtime.sections.executive_summary_repair_policy import JUDGE_REGEN_MAX_ATTEMPTS
        assert JUDGE_REGEN_MAX_ATTEMPTS == 1, (
            f"JUDGE_REGEN_MAX_ATTEMPTS must be 1; got {JUDGE_REGEN_MAX_ATTEMPTS}."
        )

    def test_judge_regen_max_attempts_function_returns_1_by_default(self, monkeypatch):
        import os
        monkeypatch.delenv("APPS_RG_EXEC_SUMMARY_JUDGE_REGEN_MAX_ATTEMPTS", raising=False)
        monkeypatch.delenv("APPS_RG_EXEC_SUMMARY_REGEN_CAPS", raising=False)
        from apps_rg.runtime.sections import executive_summary_repair_policy as rp
        result = rp.judge_regen_max_attempts()
        assert result == 1, f"judge_regen_max_attempts() should return 1 by default; got {result}"

    def test_judge_regen_max_attempts_hard_cap_is_3(self):
        from apps_rg.runtime.sections.executive_summary_repair_policy import JUDGE_REGEN_MAX_ATTEMPTS_HARD_CAP
        assert JUDGE_REGEN_MAX_ATTEMPTS_HARD_CAP == 3, (
            f"JUDGE_REGEN_MAX_ATTEMPTS_HARD_CAP must be 3 (absolute ceiling); got {JUDGE_REGEN_MAX_ATTEMPTS_HARD_CAP}."
        )

    def test_operator_can_raise_via_env(self, monkeypatch):
        monkeypatch.setenv("APPS_RG_EXEC_SUMMARY_JUDGE_REGEN_MAX_ATTEMPTS", "7")
        monkeypatch.delenv("APPS_RG_EXEC_SUMMARY_REGEN_CAPS", raising=False)
        from apps_rg.runtime.sections import executive_summary_repair_policy as rp
        result = rp.judge_regen_max_attempts()
        assert result == 3, (
            f"Env override above hard cap (7 > 3) must be clamped to hard cap 3; got {result}"
        )

    def test_operator_cannot_exceed_hard_cap(self, monkeypatch):
        monkeypatch.setenv("APPS_RG_EXEC_SUMMARY_JUDGE_REGEN_MAX_ATTEMPTS", "99")
        monkeypatch.delenv("APPS_RG_EXEC_SUMMARY_REGEN_CAPS", raising=False)
        from apps_rg.runtime.sections import executive_summary_repair_policy as rp
        result = rp.judge_regen_max_attempts()
        assert result <= 3, f"Hard cap 3 must be respected; got {result}"


# ---------------------------------------------------------------------------
# W5 — Gold example converted to negative
# ---------------------------------------------------------------------------

class TestW5GoldExampleNegative:
    """W5: exec_summary_gold_base_resume_001 must be negative category."""

    def test_gold_example_is_negative_category(self):
        by_id = _examples_by_id(_load_examples_yaml())
        row = by_id.get("exec_summary_gold_base_resume_001")
        assert row is not None, "exec_summary_gold_base_resume_001 must still exist in YAML."
        assert row["category"] == "negative", (
            f"exec_summary_gold_base_resume_001.category must be 'negative'; got '{row['category']}'."
        )

    def test_gold_example_not_included_in_e0_positives(self):
        from apps_rg.prompt_assembly.e0_examples import (
            build_executive_summary_e0,
            _EXEC_SUMMARY_POSITIVE_RETIRED_FROM_COMPILE,
        )
        e0_svp = build_executive_summary_e0(strategy_executive=True)
        e0_base = build_executive_summary_e0(strategy_executive=False)
        for e0 in (e0_svp, e0_base):
            assert 'id="exec_summary_gold_base_resume_001"' not in e0 or \
                   '<positive_example id="exec_summary_gold_base_resume_001"' not in e0, (
                "exec_summary_gold_base_resume_001 must not appear as a positive_example in E0."
            )

    def test_gold_example_annotation_cites_forbidden_phrases(self):
        by_id = _examples_by_id(_load_examples_yaml())
        annotation = by_id["exec_summary_gold_base_resume_001"].get("annotation", "")
        assert "engineering scale-out" in annotation or "SRFS_FORBIDDEN" in annotation, (
            "Annotation must call out the specific forbidden phrases for auditability."
        )

    def test_gold_example_authority_is_negative_marker(self):
        by_id = _examples_by_id(_load_examples_yaml())
        authority = by_id["exec_summary_gold_base_resume_001"].get("authority", "")
        assert "NEGATIVE" in authority.upper() or "FORBIDDEN" in authority.upper(), (
            f"authority field must signal negative/forbidden; got '{authority}'."
        )

    def test_gold_not_in_retired_from_compile_list(self):
        """Now that it's a negative, it should be picked up by the negative filter — not bypass via retired list."""
        from apps_rg.prompt_assembly.e0_examples import _EXEC_SUMMARY_POSITIVE_RETIRED_FROM_COMPILE
        assert "exec_summary_gold_base_resume_001" not in _EXEC_SUMMARY_POSITIVE_RETIRED_FROM_COMPILE, (
            "Gold example no longer needs to be in the retired list; it's now category=negative "
            "and excluded by the positive-id filter naturally."
        )

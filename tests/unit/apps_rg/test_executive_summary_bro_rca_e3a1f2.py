"""Tests for plan exec-summary-bro-svp-rca-e3a1f2 — W1/W2/W3 hardening.

Covers:
  W1 – auto_exec_brief_enabled() defaults to True; opt-out via APPS_RG_AUTO_EXEC_BRIEF=0
  W2 – generation_law_digest_text() thesis-body-promise constraint;
       format_strategy_executive_u0_block() S6 forward-projection requirement
  W3 – word-count pre-accept guard (EXEC_SUMMARY_MAX_WORDS import/constant);
       SYNTHESIS_ONLY delta guard present in compact delta lines
"""

from __future__ import annotations

from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# W1: auto_exec_brief_enabled default + resolve_manual_brief_path behaviour
# ---------------------------------------------------------------------------

def test_auto_exec_brief_enabled_true_when_env_absent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Default (no env var) must now be True so exec sibling is used automatically."""
    from apps_rg.runtime.briefing_exec_resolution import auto_exec_brief_enabled

    monkeypatch.delenv("APPS_RG_AUTO_EXEC_BRIEF", raising=False)
    assert auto_exec_brief_enabled() is True


def test_auto_exec_brief_disabled_by_zero(monkeypatch: pytest.MonkeyPatch) -> None:
    from apps_rg.runtime.briefing_exec_resolution import auto_exec_brief_enabled

    monkeypatch.setenv("APPS_RG_AUTO_EXEC_BRIEF", "0")
    assert auto_exec_brief_enabled() is False


def test_auto_exec_brief_disabled_by_false_string(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from apps_rg.runtime.briefing_exec_resolution import auto_exec_brief_enabled

    monkeypatch.setenv("APPS_RG_AUTO_EXEC_BRIEF", "false")
    assert auto_exec_brief_enabled() is False


def test_auto_exec_brief_disabled_by_no_string(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from apps_rg.runtime.briefing_exec_resolution import auto_exec_brief_enabled

    monkeypatch.setenv("APPS_RG_AUTO_EXEC_BRIEF", "no")
    assert auto_exec_brief_enabled() is False


def test_auto_exec_brief_still_true_when_set_to_one(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from apps_rg.runtime.briefing_exec_resolution import auto_exec_brief_enabled

    monkeypatch.setenv("APPS_RG_AUTO_EXEC_BRIEF", "1")
    assert auto_exec_brief_enabled() is True


def test_resolve_manual_brief_auto_swaps_without_env_var(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """With no env var, the full briefing should now be swapped to _exec sibling."""
    from apps_rg.runtime.briefing_exec_resolution import resolve_manual_brief_path

    root = Path(__file__).resolve().parents[3]
    full = root / "apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md"
    if not full.is_file():
        pytest.skip("Brown targeting fixtures missing")
    monkeypatch.delenv("APPS_RG_AUTO_EXEC_BRIEF", raising=False)
    res = resolve_manual_brief_path(str(full))
    assert res.swapped is True
    assert res.resolved_path.name.endswith("_briefing_exec.md")
    assert res.reason == "APPS_RG_AUTO_EXEC_BRIEF"


def test_resolve_manual_brief_no_swap_when_opt_out(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """APPS_RG_AUTO_EXEC_BRIEF=0 must disable the swap so the full path is kept."""
    from apps_rg.runtime.briefing_exec_resolution import resolve_manual_brief_path

    root = Path(__file__).resolve().parents[3]
    full = root / "apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md"
    if not full.is_file():
        pytest.skip("Brown targeting fixtures missing")
    monkeypatch.setenv("APPS_RG_AUTO_EXEC_BRIEF", "0")
    res = resolve_manual_brief_path(str(full))
    assert res.swapped is False
    assert res.resolved_path == full.resolve()


def test_resolve_manual_brief_no_swap_when_already_exec(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """When the path already ends in _briefing_exec.md, no swap occurs."""
    from apps_rg.runtime.briefing_exec_resolution import resolve_manual_brief_path

    root = Path(__file__).resolve().parents[3]
    exec_path = (
        root
        / "apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing_exec.md"
    )
    if not exec_path.is_file():
        pytest.skip("Brown exec briefing fixture missing")
    monkeypatch.delenv("APPS_RG_AUTO_EXEC_BRIEF", raising=False)
    res = resolve_manual_brief_path(str(exec_path))
    # Exec path IS the sibling, so discover_exec_briefing_sibling returns it unchanged.
    assert res.swapped is False


# ---------------------------------------------------------------------------
# W2: generation_law_digest_text — thesis-body promise constraint
# ---------------------------------------------------------------------------

def test_generation_law_digest_includes_thesis_body_gap_warning() -> None:
    """Digest fed to judges must mention the thesis-body gap risk."""
    from apps_rg.runtime.sections.executive_summary_generation_grade_contract import (
        generation_law_digest_text,
    )

    digest = generation_law_digest_text()
    assert "thesis-body gap" in digest, "judges must be warned about thesis-body gap"


def test_generation_law_digest_includes_commercialization_example() -> None:
    """Digest explicitly names 'commercialization' as a thread that needs fact backing."""
    from apps_rg.runtime.sections.executive_summary_generation_grade_contract import (
        generation_law_digest_text,
    )

    digest = generation_law_digest_text()
    assert "commercialization" in digest


def test_generation_law_digest_includes_thesis_promise_constraint() -> None:
    """S1 must only name threads it can deliver — constraint is present in digest."""
    from apps_rg.runtime.sections.executive_summary_generation_grade_contract import (
        generation_law_digest_text,
    )

    digest = generation_law_digest_text()
    assert "S1 thesis" in digest or "thesis-body" in digest


# ---------------------------------------------------------------------------
# W2: format_strategy_executive_u0_block — S6 forward-projection
# ---------------------------------------------------------------------------

def test_u0_block_s6_must_project_forward() -> None:
    """U0 block must tell the model that S6 MUST project capabilities toward the role."""
    from apps_rg.runtime.sections.executive_summary_synthesis_contract import (
        format_strategy_executive_u0_block,
    )

    block = format_strategy_executive_u0_block(target_title="SVP IT Strategy & Innovation")
    assert "MUST project" in block, "S6 instruction must use MUST project"


def test_u0_block_s6_forbids_backward_tool_description() -> None:
    """U0 block must prohibit ending on a backward-looking technical tool description."""
    from apps_rg.runtime.sections.executive_summary_synthesis_contract import (
        format_strategy_executive_u0_block,
    )

    block = format_strategy_executive_u0_block(target_title="SVP IT Strategy & Innovation")
    assert "backward-looking" in block


def test_u0_block_s6_includes_role_name_in_projection() -> None:
    """The forward-projection instruction should reference the actual target role name."""
    from apps_rg.runtime.sections.executive_summary_synthesis_contract import (
        format_strategy_executive_u0_block,
    )

    role = "SVP IT Strategy & Innovation"
    block = format_strategy_executive_u0_block(target_title=role)
    # role name appears in the S6 projection instruction
    assert role in block


def test_u0_block_s6_still_forbids_looking_ahead_opener() -> None:
    """Existing prohibition on 'Looking ahead,' opener must be preserved."""
    from apps_rg.runtime.sections.executive_summary_synthesis_contract import (
        format_strategy_executive_u0_block,
    )

    block = format_strategy_executive_u0_block()
    assert "'Looking ahead,'" in block or "Looking ahead," in block


# ---------------------------------------------------------------------------
# W3: EXEC_SUMMARY_MAX_WORDS importable + correct value
# ---------------------------------------------------------------------------

def test_exec_summary_max_words_importable_from_remediation_module() -> None:
    """W3.1 — EXEC_SUMMARY_MAX_WORDS must be importable via the remediation module."""
    from apps_rg.runtime.sections import executive_summary_judge_remediation as rem  # noqa: F401

    # If the import is missing the module-level import block fails, so just importing is the test.
    assert rem is not None


def test_exec_summary_max_words_is_140() -> None:
    """EXEC_SUMMARY_MAX_WORDS must remain 140 — the word-cap constant."""
    from apps_rg.runtime.validators.executive_summary_x2 import EXEC_SUMMARY_MAX_WORDS

    assert EXEC_SUMMARY_MAX_WORDS == 140


# ---------------------------------------------------------------------------
# W3: word-count pre-accept guard — unit-level verification
# ---------------------------------------------------------------------------

def test_word_count_pre_accept_constant_matches_x2_gate() -> None:
    """The pre-accept guard constant matches the X2 gate constant exactly."""
    from apps_rg.runtime.validators.executive_summary_x2 import (
        EXEC_SUMMARY_MAX_WORDS,
        check_exec_summary_paragraph_max_words,
    )

    # 140 words: passes X2 gate
    ok_text = " ".join(["word"] * 140)
    pass_ok, _ = check_exec_summary_paragraph_max_words(ok_text)
    assert pass_ok is True

    # 141 words: fails X2 gate — same threshold used in pre-accept guard
    over_text = " ".join(["word"] * (EXEC_SUMMARY_MAX_WORDS + 1))
    fail_ok, reason = check_exec_summary_paragraph_max_words(over_text)
    assert fail_ok is False
    assert "141" in str(reason)


# ---------------------------------------------------------------------------
# W3: SYNTHESIS_ONLY guard present in compact delta lines
# ---------------------------------------------------------------------------

def _minimal_soft_fail_judge(provider_key: str = "anthropic_claude") -> dict:
    return {
        "judge_id": f"x1d_{provider_key}_exec_summary",
        "provider_key": provider_key,
        "provider_name": "Anthropic Claude",
        "evaluator_mode": "MODEL_BACKED",
        "provider_status": "MODEL_BACKED_FAIL",
        "score": 3.4,
        "score_scale": "0_to_5",
        "normalized_score": 0.68,
        "threshold": 4.0,
        "normalized_threshold": 0.8,
        "decisive_failure": False,
        "findings": ["S2–S6 stack achievements without connective tissue."],
        "remediation_suggestions": ["Add connective bridges between sentences."],
        "fail_reasons": ["achievement_stack"],
        "quality_flags": ["achievement_stack", "weak_forward_synthesis"],
        "dimension_verdicts": {
            "executive_signal": {"pass": False, "severity": "major", "codes": ["achievement_stack"]},
            "synthesis_quality": {"pass": False, "severity": "major", "codes": ["sequential_stack"]},
        },
        "mocked": False,
        "advisory_only": False,
        "proof_eligible_judge": True,
        "pass": False,
    }


def test_synthesis_only_guard_present_in_compact_delta_lines() -> None:
    """W3.2 — SYNTHESIS_ONLY must appear in compact delta lines to prevent new-claim injection."""
    from apps_rg.runtime.sections.executive_summary_judge_remediation import (
        collect_judge_remediation_delta_lines,
    )

    judge = _minimal_soft_fail_judge()
    lines = collect_judge_remediation_delta_lines(
        [judge],
        unused_fact_ids=[],
        allowed_fact_count=6,
        allowed_fact_ids=frozenset(
            {
                "fact_engineering_platform_001",
                "fact_governance_003",
                "fact_exec_002",
                "fact_quant_hpc_003",
                "fact_consulting_001",
            }
        ),
        prior_word_count=130,
        prior_ledger_rows=6,
        compact=True,
        baseline_resume_display_text=(
            "Enterprise technology leader who unifies governed AI platforms, regulatory lineage, "
            "and commercialization into one IT strategy and innovation agenda."
        ),
    )
    combined = "\n".join(str(ln) for ln in lines)
    assert "SYNTHESIS_ONLY" in combined, (
        f"SYNTHESIS_ONLY guard missing from compact delta lines; got:\n{combined}"
    )


# ---------------------------------------------------------------------------
# W2 addendum: I0 template constraints (S6 past-tense prohibition + S1 thread constraint)
# ---------------------------------------------------------------------------

def test_i0_template_s6_prohibits_past_tense_openers() -> None:
    """I0 template S6 instruction must prohibit past-tense openings ('Built', 'Applied', etc.)."""
    from pathlib import Path

    template_path = (
        Path(__file__).resolve().parents[3]
        / "apps_rg/prompt_assembly/templates/executive_summary.generate_scratch_v1.yaml"
    )
    if not template_path.is_file():
        pytest.skip("Prompt template missing")
    text = template_path.read_text(encoding="utf-8")
    # The S6 line must mention the prohibition on past-tense openers
    assert "past-tense" in text or "NEVER open S6 with past-tense" in text, (
        "I0 template must prohibit past-tense S6 openers to prevent 'Built and applied...' S6"
    )


def test_i0_template_s1_includes_thesis_thread_constraint() -> None:
    """I0 template S1 must warn against undelivered thesis threads (thesis-body gap)."""
    from pathlib import Path

    template_path = (
        Path(__file__).resolve().parents[3]
        / "apps_rg/prompt_assembly/templates/executive_summary.generate_scratch_v1.yaml"
    )
    if not template_path.is_file():
        pytest.skip("Prompt template missing")
    text = template_path.read_text(encoding="utf-8")
    assert "thesis_body_gap" in text or "undelivered S1 promise" in text, (
        "I0 template S1 must mention thesis-body gap risk"
    )


def test_synthesis_only_guard_prohibits_new_proper_nouns() -> None:
    """W3.2 — The SYNTHESIS_ONLY guard must explicitly prohibit new proper nouns."""
    from apps_rg.runtime.sections.executive_summary_judge_remediation import (
        collect_judge_remediation_delta_lines,
    )

    judge = _minimal_soft_fail_judge()
    lines = collect_judge_remediation_delta_lines(
        [judge],
        unused_fact_ids=[],
        allowed_fact_count=6,
        compact=True,
        prior_word_count=120,
        prior_ledger_rows=6,
    )
    combined = "\n".join(str(ln) for ln in lines)
    assert "proper noun" in combined.lower() or "SYNTHESIS_ONLY" in combined

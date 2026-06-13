"""Tests for apps-eval-harness-terminal-3c9f81.

W1: response_likelihood_judge v2
W2: brand_voice_judge v2
W4: holdout seed fixtures scaffolded
W5: verified elsewhere (test_w_final_deferred.py header-state flip)
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


# ----- W1: response_likelihood_judge v2 -----


def test_response_likelihood_judge_is_promoted():
    from apps_lic.engines.judges import response_likelihood_judge as mod

    assert mod.IS_STUB is False
    assert mod.GRADER_ID.endswith("::v2")


def test_response_likelihood_judge_scores_realistic_outreach():
    from apps_lic.engines.judges.response_likelihood_judge import grade

    text = "Hi Alex, noticed your work at Acme on AI governance. Would you be open to a quick chat next week?"
    score, refs = grade(None, {"output": {"text": text}})
    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0
    assert score >= 0.5  # has question, CTA (chat), personalization, good length
    assert any("response_likelihood::v2" in r for r in refs)


def test_response_likelihood_judge_abstains_on_empty():
    from apps_lic.engines.judges.response_likelihood_judge import grade
    from agentic_core.L3_orchestration.exit_eval.v6.app_grader_registry import (
        GRADER_UNKNOWN_SENTINEL,
    )

    score, refs = grade(None, {"output": {"text": ""}})
    assert score is GRADER_UNKNOWN_SENTINEL
    assert refs == []


# ----- W2: brand_voice_judge v2 -----


def test_brand_voice_judge_is_promoted():
    from apps_lic.engines.judges import brand_voice_judge as mod

    assert mod.IS_STUB is False
    assert mod.GRADER_ID.endswith("::v2")


def test_brand_voice_judge_penalizes_forbidden_lexicon():
    from apps_lic.engines.judges.brand_voice_judge import grade

    text_clean = "Please find attached our proposal. We look forward to your response."
    text_dirty = "Please find attached our proposal. Anyway, lol, we'll chat whenever."
    profile = {"forbidden_lexicon": ["lol", "whenever"], "register": "formal"}
    score_clean, _ = grade(None, {"output": {"text": text_clean}, "brand_voice_profile": profile})
    score_dirty, _ = grade(None, {"output": {"text": text_dirty}, "brand_voice_profile": profile})
    assert score_clean > score_dirty


def test_brand_voice_judge_with_no_profile_does_not_crash():
    from apps_lic.engines.judges.brand_voice_judge import grade

    score, refs = grade(None, {"output": {"text": "A short neutral sentence. Another one here."}})
    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0
    assert refs


# ----- W4: holdout seed scaffold -----


@pytest.mark.parametrize(
    "app_id",
    [
        "apps_qna",
        "apps_research",
        "apps_exec",
        "apps_underwriting_ai",
        "apps_rg",
        "apps_lic",
        "apps_eval",
    ],
)
def test_holdout_seed_exists_and_labeled(app_id: str):
    """AG dec_19dede3a5e4d6507f flipped tags from SYNTHETIC_SEED_ONLY → RELEASE_GATE
    after user-as-curator approval. Test now asserts each row carries exactly one
    of the two tags (gate-enforced by check_holdout_isolation.py)."""
    fixture = REPO_ROOT / "apps_eval" / "fixtures" / "holdout" / f"{app_id}.jsonl"
    assert fixture.is_file(), f"missing holdout seed: {fixture}"
    rows = [json.loads(line) for line in fixture.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert rows, f"empty holdout seed: {fixture}"
    assert rows[0]["app_id"] == app_id
    tags = rows[0].get("tags", [])
    has_synth = "SYNTHETIC_SEED_ONLY" in tags
    has_release = "RELEASE_GATE" in tags
    assert has_synth ^ has_release, (
        f"Holdout seed {app_id} must carry EXACTLY one of "
        f"SYNTHETIC_SEED_ONLY|RELEASE_GATE, got tags={tags}"
    )


# ----- Promotion registry sanity -----


def test_judge_registry_reports_4_promoted_judges():
    import importlib
    from apps_shared import judge_registry as mod

    importlib.reload(mod)
    # After terminal-3c9f81: exec_positioning + response_likelihood +
    # brand_voice + win_theme_alignment = 4 promoted, 0 stubs remaining.
    assert mod.promoted_count() == 4
    assert mod.stub_count() == 0

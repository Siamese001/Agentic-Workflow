"""v5 parity tests — Exit Eval & Control v5 §X3A reason-code list + X1G rubric.

Covers:
- ``ReasonCode`` enum carries every v5 §X3A reason code (full list).
- ``config/exit_eval_rubrics/x1g_v1.yaml`` exists and loads via ``load_rubric``.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_core.L3_orchestration.exit_eval.disposition import ReasonCode
from agentic_core.L3_orchestration.exit_eval.rubric import load_rubric

# v5 §X3A "reason_codes:" list (verbatim from the spec).
V5_REASON_CODES = {
    "POLICY_CONFLICT",
    "HARD_FAIL",
    "SCHEMA_VIOLATION",
    "FORMAT_MISMATCH",
    "INSTRUCTION_BYPASS",
    "SANDBOX_BREACH",
    "UNAUTHORIZED_MUTATION",
    "ENV_CONTAMINATED",
    "TRIAL_STATE_LEAK",
    "UNGROUNDED",
    "CITATION_INVALID",
    "LOW_FAITHFULNESS",
    "WRONG_TOOL",
    "ARG_EXTRACTION_FAIL",
    "STEP_INEFFICIENT",
    "REASONING_INCOHERENT",
    "HANDOFF_MISROUTED",
    "TRAJECTORY_SUSPECT",
    "TRAJECTORY_INVALID",
    "PROMPT_INJECTION_DETECTED",
    "SYSTEM_PROMPT_LEAK",
    "JAILBREAK_DETECTED",
    "BIAS_DELTA_EXCEEDED",
    "ADVERSARIAL_CRASH",
    "ADVERSARIAL_DETECTED",
    "CONSISTENCY_FAIL",
}

REPO_ROOT = Path(__file__).resolve().parents[4]
RUBRIC_DIR = REPO_ROOT / "config" / "exit_eval_rubrics"


def test_reason_code_enum_carries_full_v5_x3a_list():
    """Every v5 §X3A reason code must be present in the ReasonCode enum."""
    actual = {m.value for m in ReasonCode}
    missing = V5_REASON_CODES - actual
    assert not missing, f"v5 §X3A reason codes missing from enum: {sorted(missing)}"


@pytest.mark.parametrize(
    "code",
    ["HARD_FAIL", "TRAJECTORY_INVALID", "ADVERSARIAL_DETECTED"],
)
def test_v5_added_codes_have_unique_values(code):
    """The three codes added in plan exit-eval-v5-gap-c0aa47 are present and unique."""
    members = [m for m in ReasonCode if m.value == code]
    assert len(members) == 1, f"reason code {code!r} should appear exactly once"


def test_bucket_key_from_context_extracts_trajectory_class():
    """v5 §X1G mandates per-trajectory_class pass^k history."""
    from agentic_core.L3_orchestration.exit_eval.consistency import (
        BucketKey,
        bucket_key_from_context,
    )

    ctx = {
        "trajectory_class": "brief_assembly",
        "rubric_version": "X1D@v3",
        "agent_version": "v42",
        "policy_version": "2026-04-25",
    }
    key = bucket_key_from_context(ctx)
    assert isinstance(key, BucketKey)
    assert key.trajectory_class == "brief_assembly"
    assert key.rubric_version == "X1D@v3"


def test_bucket_key_from_context_missing_field_raises():
    from agentic_core.L3_orchestration.exit_eval.consistency import (
        bucket_key_from_context,
    )

    with pytest.raises(KeyError):
        bucket_key_from_context({"trajectory_class": "x"})  # missing versions


def test_bucket_key_rubric_version_bump_invalidates_history():
    """v5 §X1G invariant: any tuple change resets the bucket."""
    from agentic_core.L3_orchestration.exit_eval.consistency import (
        BucketKey,
        PassKStore,
        TrialRecord,
    )

    store = PassKStore()
    k_old = BucketKey("brief", "X1D@v1", "v1", "v1")
    k_new = BucketKey("brief", "X1D@v2", "v1", "v1")  # rubric bumped
    for i in range(5):
        store.record(k_old, TrialRecord(run_id=f"r{i}", passed=True, timestamp=float(i)))
    # Old bucket has full history; new bucket starts empty.
    old_chk = store.check(k_old, k=3, theta=0.5)
    new_chk = store.check(k_new, k=3, theta=0.5)
    assert old_chk.has_history is True
    assert new_chk.has_history is False
    assert new_chk.reason == "INSUFFICIENT_HISTORY"


def test_x1g_rubric_yaml_exists_and_loads():
    """``x1g_v1.yaml`` exists for the consistency gate and parses cleanly."""
    path = RUBRIC_DIR / "x1g_v1.yaml"
    assert path.exists(), f"missing rubric file: {path}"
    rubric = load_rubric(path)
    assert rubric.gate == "X1G"
    assert rubric.version == "X1G@v1"
    # Spec is binary: at least one hard-gate dimension named for pass^k.
    assert any(d.name == "passk_consistency" for d in rubric.dimensions)
    hard = [d for d in rubric.dimensions if d.is_hard_gate]
    assert hard, "X1G rubric must declare a hard gate dimension"

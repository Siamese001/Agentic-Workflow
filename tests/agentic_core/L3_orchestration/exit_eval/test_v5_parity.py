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

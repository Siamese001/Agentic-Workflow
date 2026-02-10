"""V15 P8.2c — Enforcement Mode Transition Safety Matrix.

Proves the exactly-one rule for every valid/invalid V15_ENFORCEMENT value:
- OFF:       enforced=False, soft=False, hard=False
- LOG_ONLY:  enforced=True,  soft=False, hard=False
- SOFT_FAIL: enforced=True,  soft=True,  hard=False
- HARD_FAIL: enforced=True,  soft=False, hard=True

Covers case variants, whitespace, synonyms, and garbage inputs.
"""

from __future__ import annotations

import pytest

from agentic_core.L0_maintenance.types.guardian_contract import (
    is_v15_enforced,
    is_v15_hard_fail,
    is_v15_soft_fail,
)

# ===========================================================================
# Parametrized mode matrix
# ===========================================================================

# (env_value, expected_enforced, expected_soft, expected_hard, label)
OFF_CASES = [
    (None, False, False, False, "unset"),
    ("", False, False, False, "empty"),
    ("0", False, False, False, "zero"),
    ("false", False, False, False, "false_lower"),
    ("FALSE", False, False, False, "false_upper"),
    ("off", False, False, False, "off_lower"),
    ("OFF", False, False, False, "off_upper"),
    ("no", False, False, False, "no_lower"),
    ("NO", False, False, False, "no_upper"),
    ("garbage", False, False, False, "garbage"),
    ("2", False, False, False, "two"),
]

LOG_CASES = [
    ("log", True, False, False, "log_lower"),
    ("LOG", True, False, False, "log_upper"),
    ("Log", True, False, False, "log_title"),
]

SOFT_CASES = [
    ("soft", True, True, False, "soft_lower"),
    ("SOFT", True, True, False, "soft_upper"),
    ("Soft", True, True, False, "soft_title"),
]

HARD_CASES = [
    ("1", True, False, True, "one"),
    ("true", True, False, True, "true_lower"),
    ("TRUE", True, False, True, "true_upper"),
    ("True", True, False, True, "true_title"),
    ("yes", True, False, True, "yes_lower"),
    ("YES", True, False, True, "yes_upper"),
    ("Yes", True, False, True, "yes_title"),
]

# Whitespace variants — these MUST parse identically after normalization
WHITESPACE_CASES = [
    (" log ", True, False, False, "log_padded"),
    (" soft ", True, True, False, "soft_padded"),
    (" True ", True, False, True, "true_padded"),
    (" 1 ", True, False, True, "one_padded"),
    ("\tsoft\t", True, True, False, "soft_tabbed"),
    ("\nlog\n", True, False, False, "log_newline"),
]

ALL_CASES = OFF_CASES + LOG_CASES + SOFT_CASES + HARD_CASES + WHITESPACE_CASES


def _set_env(monkeypatch, value):
    """Set or unset V15_ENFORCEMENT."""
    if value is None:
        monkeypatch.delenv("V15_ENFORCEMENT", raising=False)
    else:
        monkeypatch.setenv("V15_ENFORCEMENT", value)


# ===========================================================================
# A) Full Matrix
# ===========================================================================


class TestModeMatrix:
    """Exhaustive mode matrix: every input → exactly one mode selected."""

    @pytest.mark.parametrize(
        "env_val, exp_enforced, exp_soft, exp_hard, label",
        ALL_CASES,
        ids=[c[4] for c in ALL_CASES],
    )
    def test_mode_selection(self, monkeypatch, env_val, exp_enforced, exp_soft, exp_hard, label):
        _set_env(monkeypatch, env_val)
        enforced = is_v15_enforced()
        soft = is_v15_soft_fail()
        hard = is_v15_hard_fail()

        assert enforced == exp_enforced, f"[{label}] enforced: got {enforced}, expected {exp_enforced}"
        assert soft == exp_soft, f"[{label}] soft: got {soft}, expected {exp_soft}"
        assert hard == exp_hard, f"[{label}] hard: got {hard}, expected {exp_hard}"


# ===========================================================================
# B) Exactly-One Rule
# ===========================================================================


class TestExactlyOneRule:
    """When enforced, exactly one of (log, soft, hard) must be active."""

    @pytest.mark.parametrize(
        "env_val, exp_enforced, exp_soft, exp_hard, label",
        [c for c in ALL_CASES if c[1]],  # only enforced cases
        ids=[c[4] for c in ALL_CASES if c[1]],
    )
    def test_exactly_one_active_mode(self, monkeypatch, env_val, exp_enforced, exp_soft, exp_hard, label):
        _set_env(monkeypatch, env_val)
        soft = is_v15_soft_fail()
        hard = is_v15_hard_fail()
        log_only = not soft and not hard

        # Exactly one must be True
        active = sum([log_only, soft, hard])
        assert active == 1, (
            f"[{label}] Expected exactly 1 active mode, got {active} (log={log_only}, soft={soft}, hard={hard})"
        )

    @pytest.mark.parametrize(
        "env_val, exp_enforced, exp_soft, exp_hard, label",
        [c for c in ALL_CASES if not c[1]],  # only OFF cases
        ids=[c[4] for c in ALL_CASES if not c[1]],
    )
    def test_off_means_all_false(self, monkeypatch, env_val, exp_enforced, exp_soft, exp_hard, label):
        _set_env(monkeypatch, env_val)
        assert not is_v15_enforced()
        assert not is_v15_soft_fail()
        assert not is_v15_hard_fail()


# ===========================================================================
# C) Mutual Exclusion
# ===========================================================================


class TestMutualExclusion:
    """soft and hard must never both be True simultaneously."""

    @pytest.mark.parametrize(
        "env_val, exp_enforced, exp_soft, exp_hard, label",
        ALL_CASES,
        ids=[c[4] for c in ALL_CASES],
    )
    def test_soft_and_hard_never_both_true(
        self,
        monkeypatch,
        env_val,
        exp_enforced,
        exp_soft,
        exp_hard,
        label,
    ):
        _set_env(monkeypatch, env_val)
        soft = is_v15_soft_fail()
        hard = is_v15_hard_fail()
        assert not (soft and hard), f"[{label}] soft and hard both True — mode ambiguity!"


# ===========================================================================
# D) Determinism
# ===========================================================================


class TestDeterminism:
    """Same input must always produce same output."""

    @pytest.mark.parametrize("env_val", ["log", "soft", "1", "0", ""])
    def test_idempotent_across_calls(self, monkeypatch, env_val):
        monkeypatch.setenv("V15_ENFORCEMENT", env_val)
        results = [(is_v15_enforced(), is_v15_soft_fail(), is_v15_hard_fail()) for _ in range(10)]
        assert len(set(results)) == 1, f"Non-deterministic for '{env_val}': {set(results)}"

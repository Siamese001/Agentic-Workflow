"""Unit tests for system_learning.validators.dampening."""

import pytest

from system_learning.validators.dampening import (
    CooldownPolicy,
    CooldownViolation,
    SampleSizePolicy,
    SampleSizeViolation,
    assert_cooldown_ok,
    assert_min_sample_size,
)

pytestmark = pytest.mark.unit_min_deps


class TestCooldownPolicy:
    def test_cooldown_elapsed_passes(self):
        policy = CooldownPolicy(min_seconds_between_updates=3600)
        last_update = 1700000000
        now = 1700003600
        assert_cooldown_ok(last_update, now, policy)
        assert True  # no-exception contract

    def test_cooldown_not_elapsed_raises(self):
        policy = CooldownPolicy(min_seconds_between_updates=3600)
        last_update = 1700000000
        now = 1700001800
        with pytest.raises(CooldownViolation, match="COOLDOWN_VIOLATION"):
            assert_cooldown_ok(last_update, now, policy)

    def test_cooldown_exactly_elapsed_passes(self):
        policy = CooldownPolicy(min_seconds_between_updates=3600)
        last_update = 1700000000
        now = 1700003600
        assert_cooldown_ok(last_update, now, policy)
        assert True  # no-exception contract


class TestSampleSizePolicy:
    def test_sufficient_samples_passes(self):
        policy = SampleSizePolicy(min_observations=1000)
        assert_min_sample_size(1500, policy)
        assert True  # no-exception contract

    def test_insufficient_samples_raises(self):
        policy = SampleSizePolicy(min_observations=1000)
        with pytest.raises(SampleSizeViolation, match="SAMPLE_SIZE_VIOLATION"):
            assert_min_sample_size(500, policy)

    def test_exactly_min_samples_passes(self):
        policy = SampleSizePolicy(min_observations=1000)
        assert_min_sample_size(1000, policy)
        assert True  # no-exception contract


class TestDeterminism:
    def test_cooldown_deterministic(self):
        policy = CooldownPolicy(min_seconds_between_updates=3600)
        assert_cooldown_ok(1700000000, 1700003600, policy)
        assert_cooldown_ok(1700000000, 1700003600, policy)
        assert True  # no-exception contract

    def test_sample_size_deterministic(self):
        policy = SampleSizePolicy(min_observations=1000)
        assert_min_sample_size(1500, policy)
        assert_min_sample_size(1500, policy)
        assert True  # no-exception contract

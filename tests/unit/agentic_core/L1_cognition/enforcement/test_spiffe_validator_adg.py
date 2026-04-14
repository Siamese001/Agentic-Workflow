"""Behavioral tests for spiffe_validator_adg."""

from __future__ import annotations

import pytest

from agentic_core.spiffe_validator_adg import SpiffeValidatorAdg


def test_spiffe_validator_accepts_domain():
    assert SpiffeValidatorAdg(trust_domain="example.org").validate().trust_domain == "example.org"


def test_spiffe_validator_rejects_blank_domain():
    with pytest.raises(ValueError):
        SpiffeValidatorAdg(trust_domain="").validate()

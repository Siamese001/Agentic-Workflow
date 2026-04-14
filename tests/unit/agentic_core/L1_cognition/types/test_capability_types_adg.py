"""Behavioral tests for capability_types_adg."""

from __future__ import annotations

import pytest

from agentic_core.capability_types_adg import CapabilityDescriptor


def test_capability_descriptor_accepts_valid_name():
    assert CapabilityDescriptor(name="retrieval").validate().enabled is True


def test_capability_descriptor_rejects_blank_name():
    with pytest.raises(ValueError):
        CapabilityDescriptor(name=" ").validate()

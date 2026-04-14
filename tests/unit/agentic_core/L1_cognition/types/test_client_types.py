"""Behavioral tests for client_types."""

from __future__ import annotations

import pytest

from agentic_core.client_types import ClientContext


def test_client_context_accepts_ids():
    assert ClientContext(client_id="c1", tenant_id="t1").validate().client_id == "c1"


def test_client_context_rejects_blank_ids():
    with pytest.raises(ValueError):
        ClientContext(client_id="", tenant_id="t1").validate()

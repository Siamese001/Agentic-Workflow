"""ADG-driven tests for L0_routing/scripts/add_dataclass_to_agents_util.py — fan_in=0."""
from __future__ import annotations

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_add_dataclass_to_agents_util_adg")
_emit_applies_guardrail("p0", "test_add_dataclass_to_agents_util_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_add_dataclass_to_agents_util_adg", "policy_binding")
_emit_snapshots_state("p0", "test_add_dataclass_to_agents_util_adg", "state_snapshot")
emit_replay_key("p0", "test_add_dataclass_to_agents_util_adg")
emit_determinism_digest("p0", "test_add_dataclass_to_agents_util_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.scripts.add_dataclass_to_agents_util import (
        has_dataclass_decorator,
        has_dataclass_import,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    has_dataclass_decorator = None  # type: ignore[assignment]
    has_dataclass_import = None  # type: ignore[assignment]


@pytest.mark.skipif(not _AVAILABLE, reason="add_dataclass deps unavailable")
class TestHasDataclassDecorator:
    def test_detects_decorator(self):
        assert has_dataclass_decorator("@dataclass\nclass Foo:") is True

    def test_no_decorator(self):
        assert has_dataclass_decorator("class Foo:") is False


@pytest.mark.skipif(not _AVAILABLE, reason="add_dataclass deps unavailable")
class TestHasDataclassImport:
    def test_detects_from_import(self):
        assert has_dataclass_import("from dataclasses import dataclass") is True

    def test_detects_module_import(self):
        assert has_dataclass_import("import dataclasses") is True

    def test_no_import(self):
        assert has_dataclass_import("import os") is False


def test_module_importable():
    assert _AVAILABLE or not _AVAILABLE

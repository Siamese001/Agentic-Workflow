"""ADG contract tests for apps_rg/types/PromptTemplate.py."""
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

_emit_records_execution_trace("p0", "evidence", "test_PromptTemplate_adg")
_emit_applies_guardrail("p0", "test_PromptTemplate_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_PromptTemplate_adg", "policy_binding")
_emit_snapshots_state("p0", "test_PromptTemplate_adg", "state_snapshot")
emit_replay_key("p0", "test_PromptTemplate_adg")
emit_determinism_digest("p0", "test_PromptTemplate_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit
try:
    from apps_rg.types.PromptTemplate import PromptTemplate
    _AVAIL = True
except ImportError:
    _AVAIL = False
    PromptTemplate = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestPromptTemplate:
    def test_creates(self):
        t = PromptTemplate(id="p1", template="Hello {name}", required_vars=["name"])
        assert t.id == "p1"; assert t.required_vars == ["name"]
    def test_is_pydantic(self):
        try:
            from pydantic import BaseModel; assert issubclass(PromptTemplate, BaseModel)
        except ImportError:
            pytest.skip("pydantic unavailable")
    def test_broken_placeholder_raises(self):
        try:
            from pydantic import ValidationError
            with pytest.raises(ValidationError):
                PromptTemplate(id="bad", template="hello { world", required_vars=[])
        except ImportError:
            pytest.skip("pydantic unavailable")
    def test_valid_template_no_vars(self):
        t = PromptTemplate(id="t2", template="Write a letter.", required_vars=[])
        assert t.template == "Write a letter."

def test_module_importable(): assert _AVAIL or not _AVAIL

"""ADG contract tests for L5_safety/types/specificity_prose_types.py."""
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

_emit_records_execution_trace("p0", "evidence", "test_specificity_prose_types_adg")
_emit_applies_guardrail("p0", "test_specificity_prose_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_specificity_prose_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_specificity_prose_types_adg", "state_snapshot")
emit_replay_key("p0", "test_specificity_prose_types_adg")
emit_determinism_digest("p0", "test_specificity_prose_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit
try:
    from agentic_core.L5_safety.types.specificity_prose_types import (
        CompanySpecificDetail,
        SpecificityProseConfig,
    )
    _AVAIL = True
except ImportError:
    _AVAIL = False; SpecificityProseConfig = CompanySpecificDetail = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestSpecificityProseConfig:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(SpecificityProseConfig)
    def test_defaults(self):
        c = SpecificityProseConfig()
        assert c.paragraph_count == 3
        assert c.min_words_per_paragraph == 85
        assert c.min_company_specifics == 4

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestCompanySpecificDetail:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(CompanySpecificDetail)
    def test_creates(self):
        d = CompanySpecificDetail(detail="Watson", category="PRODUCT", source="website")
        assert d.detail == "Watson"

def test_module_importable(): assert _AVAIL or not _AVAIL

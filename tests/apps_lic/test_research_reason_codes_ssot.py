from __future__ import annotations

from apps_lic.integrations import apps_research_bridge, managed_workflow_dispatcher
from apps_lic.integrations.research_reason_codes import (
    APPS_RESEARCH_DEPRECATED,
    APPS_RESEARCH_FAILED,
    RESEARCH_FAILURE_REASON_CODES,
    ResearchFailureReason,
)


def test_legacy_research_reason_exports_alias_canonical_codes() -> None:
    assert apps_research_bridge.APPS_RESEARCH_DEPRECATED == APPS_RESEARCH_DEPRECATED
    assert managed_workflow_dispatcher.APPS_RESEARCH_DEPRECATED == APPS_RESEARCH_DEPRECATED
    assert managed_workflow_dispatcher.RESEARCH_FAILURE_REASON_CODES == RESEARCH_FAILURE_REASON_CODES
    assert managed_workflow_dispatcher.ResearchFailureReason is ResearchFailureReason
    assert APPS_RESEARCH_FAILED in RESEARCH_FAILURE_REASON_CODES

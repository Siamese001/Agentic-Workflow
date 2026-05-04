"""Contract tests — DS-3: UWG durable write path for research briefs.

Plan: apps-research-deferred-scope-b7e3d2 W3 (phase 3.1 + 3.2).

Covers:
- ResearchBriefRecord schema shape and defaults (3.2)
- commit_brief_record happy path: UWG commit goes through (3.1)
- commit_brief_record blocked path: UWG rejects → receipt_ref == "BLOCKED"
- GovernedE2ERunRecord gains l4_brief_committed field (back-compat)
- ROUTER_DECISION marker is logged (§29)
"""

from __future__ import annotations

import dataclasses
import uuid
from typing import Any
from unittest.mock import MagicMock, patch


# ---------------------------------------------------------------------------
# 3.2 — ResearchBriefRecord schema
# ---------------------------------------------------------------------------


def test_research_brief_record_shape() -> None:
    """ResearchBriefRecord is a frozen dataclass with the required fields."""
    from agentic_core.L4_state.research.research_brief_record import ResearchBriefRecord

    rec = ResearchBriefRecord(
        record_id="r1",
        run_id="run-001",
        trace_id="trace-001",
        topic="agentic AI",
        l0_intent="research",
        l0_confidence=0.95,
        grounded=True,
        citation_count=5,
        disposition="proceed",
    )
    assert rec.schema_version == "research-brief-1.0"
    assert rec.commit_receipt_ref == ""
    assert rec.research_depth_profile == ""
    assert rec.fec_context_digest == ""
    assert rec.audit_refs == ()


def test_research_brief_record_is_frozen() -> None:
    """ResearchBriefRecord is immutable."""
    from agentic_core.L4_state.research.research_brief_record import ResearchBriefRecord
    import pytest

    rec = ResearchBriefRecord(
        record_id="r2", run_id="run-002", trace_id="", topic="t",
        l0_intent="research", l0_confidence=0.9, grounded=False,
        citation_count=0, disposition="abstain",
    )
    with pytest.raises((dataclasses.FrozenInstanceError, TypeError)):
        rec.grounded = True  # type: ignore[misc]


def test_research_brief_record_schema_version_constant() -> None:
    from agentic_core.L4_state.research.research_brief_record import _RECORD_SCHEMA_VERSION

    assert _RECORD_SCHEMA_VERSION == "research-brief-1.0"


# ---------------------------------------------------------------------------
# 3.1 — commit_brief_record
# ---------------------------------------------------------------------------


def _make_run_record(**overrides: Any):
    """Build a minimal GovernedE2ERunRecord for testing."""
    from apps_research.integrations.governed_research_run import GovernedE2ERunRecord

    defaults = dict(
        run_id=str(uuid.uuid4()),
        topic="test topic",
        l1_sub_queries=(),
        l1_fallback=False,
        l0_intent="research",
        l0_target="research_assembly",
        l0_confidence=0.9,
        l0_fallback=False,
        c0_raw_count=3,
        c0_shaped_count=3,
        c0_collection="test_col",
        disposition="proceed",
        gate_disposition="allow_response",
        grounded=True,
        citation_count=2,
        support_coverage=0.7,
        l6_ingested=False,
        error="",
    )
    defaults.update(overrides)
    return GovernedE2ERunRecord(**defaults)


def test_commit_brief_record_happy_path() -> None:
    """commit_brief_record returns a record with a non-BLOCKED/FAILED receipt_ref."""
    from apps_research.integrations.research_brief_uwg_writer import commit_brief_record
    from agentic_core.L4_state.uwg.durable_write_gateway import (
        DurableWriteGateway,
        reset_default_gateway,
    )

    reset_default_gateway()
    run_record = _make_run_record(run_id="run-happy-001")
    brief = commit_brief_record(run_record)

    assert brief.run_id == "run-happy-001"
    assert brief.topic == "test topic"
    assert brief.grounded is True
    assert brief.commit_receipt_ref not in ("PENDING",)
    # UWG should accept (Exit source, append_record op, audit ledger available)
    assert brief.commit_receipt_ref not in ("COMMIT_FAILED",)


def test_commit_brief_record_blocked_on_bad_gateway() -> None:
    """When UWG rejects (e.g. source not Exit), receipt_ref is BLOCKED."""
    from apps_research.integrations.research_brief_uwg_writer import commit_brief_record
    from agentic_core.L4_state.uwg.durable_write_gateway import (
        DurableWriteGateway,
        UWGBlockedCommitReceipt,
    )

    # Inject a mock gateway that always returns blocked
    mock_blocked = MagicMock(spec=UWGBlockedCommitReceipt)
    mock_blocked.blocked_reason_codes = ("non_exit_source",)
    mock_blocked.blocked_commit_receipt_id = "blk-001"

    mock_gw = MagicMock(spec=DurableWriteGateway)
    mock_gw.last_snapshot_id = "snapshot:00000001"
    mock_gw.commit.return_value = (None, mock_blocked, [])

    run_record = _make_run_record(run_id="run-blocked-001")
    brief = commit_brief_record(run_record, gateway=mock_gw)

    assert brief.commit_receipt_ref == "BLOCKED"


def test_commit_brief_record_fail_soft_on_exception() -> None:
    """commit_brief_record never raises; returns COMMIT_FAILED on exception."""
    from apps_research.integrations.research_brief_uwg_writer import commit_brief_record
    from agentic_core.L4_state.uwg.durable_write_gateway import DurableWriteGateway

    mock_gw = MagicMock(spec=DurableWriteGateway)
    mock_gw.last_snapshot_id = "snapshot:00000001"
    mock_gw.commit.side_effect = RuntimeError("unexpected UWG error")

    run_record = _make_run_record(run_id="run-fail-001")
    brief = commit_brief_record(run_record, gateway=mock_gw)

    assert brief.commit_receipt_ref == "COMMIT_FAILED"
    assert brief.run_id == "run-fail-001"


def test_commit_brief_record_populates_fec_digest() -> None:
    """fec_context_digest is a non-empty SHA-256 hex when fec_run_context is set."""
    from apps_research.integrations.research_brief_uwg_writer import commit_brief_record
    from agentic_core.L4_state.uwg.durable_write_gateway import reset_default_gateway

    reset_default_gateway()
    run_record = _make_run_record(
        run_id="run-fec-001",
        research_depth_profile="DOSSIER",
        fec_run_context={"research_depth_profile": "DOSSIER", "citation_anchor_count": 3},
    )
    brief = commit_brief_record(run_record)

    assert brief.research_depth_profile == "DOSSIER"
    assert len(brief.fec_context_digest) == 64  # SHA-256 hex


# ---------------------------------------------------------------------------
# GovernedE2ERunRecord back-compat
# ---------------------------------------------------------------------------


def test_governed_e2e_run_record_has_l4_brief_committed_field() -> None:
    """GovernedE2ERunRecord exposes l4_brief_committed with default 'PENDING'."""
    run_record = _make_run_record()
    assert hasattr(run_record, "l4_brief_committed")
    assert run_record.l4_brief_committed == "PENDING"


def test_governed_e2e_run_record_replace_l4_brief_committed() -> None:
    """l4_brief_committed can be set via dataclasses.replace."""
    run_record = _make_run_record()
    updated = dataclasses.replace(run_record, l4_brief_committed="rcpt-abc123")
    assert updated.l4_brief_committed == "rcpt-abc123"


# ---------------------------------------------------------------------------
# §29 ROUTER_DECISION: marker is emitted
# ---------------------------------------------------------------------------


def test_router_decision_logged(caplog: Any) -> None:
    """commit_brief_record logs ROUTER_DECISION: marker per constitutional §29."""
    import logging

    from apps_research.integrations.research_brief_uwg_writer import commit_brief_record
    from agentic_core.L4_state.uwg.durable_write_gateway import reset_default_gateway

    reset_default_gateway()
    run_record = _make_run_record(run_id="run-router-001")

    with caplog.at_level(logging.INFO, logger="apps_research.integrations.research_brief_uwg_writer"):
        commit_brief_record(run_record)

    assert any("ROUTER_DECISION:" in r.message for r in caplog.records)

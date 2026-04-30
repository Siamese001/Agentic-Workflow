"""Tests for apps_qna.integrations.spine_handoff (W7 build_time_compiler overlay).

Pins:
  - ValidatedRequest is constructible from any Interview without raising
  - The intake invariants hold (downstream_authority="none",
    permitted_next_layer="L1") -- enforced by the contract's __post_init__
  - The hash fields are deterministic per Interview content
  - build_pack_via_spine emits a 'validated_request_emit' ledger event
  - The underlying CardPackBuilder.build() is still called and returns a
    real CardPackManifest
  - The scanner now classifies apps_qna as APP_OVERLAY_STATIC_EVIDENCE
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest
import yaml

from apps_qna.integrations.spine_handoff import (
    _build_time_validated_request,
    build_pack_via_spine,
)
from apps_qna.types.qna_types import Interview


def _ledger_path() -> Path | None:
    try:
        from tools.ledgers.schema_registry import get
        return get("apps_qna_pack_lifecycle").db_path
    except (ImportError, KeyError):
        return None


@pytest.fixture
def ledger_db() -> Path:
    p = _ledger_path()
    if p is None or not p.is_file():
        pytest.skip("apps_qna_pack_lifecycle ledger not materialized")
    return p


def _searce_interview() -> Interview | None:
    """Load the live Searce interview YAML when available."""
    yaml_path = Path("reports/qna/searce-applied-ai/interview.yaml")
    if not yaml_path.is_file():
        return None
    payload = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    payload.pop("extra_context", None)
    return Interview.model_validate(payload)


# ---------------------------------------------------------------------------
# _build_time_validated_request -- intake invariants
# ---------------------------------------------------------------------------


def test_validated_request_constructs_for_searce_interview() -> None:
    interview = _searce_interview()
    if interview is None:
        pytest.skip("Searce interview YAML not available")
    vr = _build_time_validated_request(interview)
    assert vr is not None


def test_validated_request_honors_intake_invariants() -> None:
    """downstream_authority == 'none' and permitted_next_layer == 'L1'."""
    interview = _searce_interview()
    if interview is None:
        pytest.skip("Searce interview YAML not available")
    vr = _build_time_validated_request(interview)
    assert vr.downstream_authority == "none"
    assert vr.permitted_next_layer == "L1"


def test_validated_request_request_id_is_unique_per_call() -> None:
    interview = _searce_interview()
    if interview is None:
        pytest.skip("Searce interview YAML not available")
    vr1 = _build_time_validated_request(interview)
    vr2 = _build_time_validated_request(interview)
    assert vr1.request_id != vr2.request_id


def test_validated_request_explicit_request_id_is_honored() -> None:
    interview = _searce_interview()
    if interview is None:
        pytest.skip("Searce interview YAML not available")
    explicit = "test-request-id-abc123"
    vr = _build_time_validated_request(interview, request_id=explicit)
    assert vr.request_id == explicit
    assert vr.trace_root == explicit


def test_validated_request_payload_hash_is_deterministic() -> None:
    """Same Interview content -> same raw_payload_hash."""
    interview = _searce_interview()
    if interview is None:
        pytest.skip("Searce interview YAML not available")
    vr1 = _build_time_validated_request(interview)
    vr2 = _build_time_validated_request(interview)
    assert vr1.raw_payload_hash == vr2.raw_payload_hash
    assert vr1.normalized_payload_hash == vr2.normalized_payload_hash


def test_validated_request_uses_pass_equivalent_verdicts() -> None:
    """Build-time invocations declare PASS-equivalent verdicts."""
    interview = _searce_interview()
    if interview is None:
        pytest.skip("Searce interview YAML not available")
    vr = _build_time_validated_request(interview)
    assert vr.schema_verdict.value == "valid"
    assert vr.auth_verdict.value == "service-bound"
    assert vr.quota_verdict.value == "allowed"
    assert vr.principal_type.value == "service"


# ---------------------------------------------------------------------------
# build_pack_via_spine end-to-end
# ---------------------------------------------------------------------------


def test_build_pack_via_spine_returns_manifest(tmp_path: Path) -> None:
    """The wrapper still returns a CardPackManifest from CardPackBuilder."""
    interview = _searce_interview()
    if interview is None:
        pytest.skip("Searce interview YAML not available")
    output_dir = tmp_path / "test-spine-handoff-pack"
    manifest = build_pack_via_spine(interview, output_dir)
    assert manifest is not None
    assert manifest.cards
    assert output_dir.is_dir()


def test_build_pack_via_spine_emits_validated_request_event(
    tmp_path: Path, ledger_db: Path
) -> None:
    """The wrapper emits event_kind='validated_request_emit'."""
    interview = _searce_interview()
    if interview is None:
        pytest.skip("Searce interview YAML not available")
    output_dir = tmp_path / "test-spine-handoff-emit"
    build_pack_via_spine(interview, output_dir)

    # Confirm the event lands in the ledger.
    con = sqlite3.connect(ledger_db)
    try:
        cur = con.cursor()
        cur.execute(
            """SELECT event_kind, prediction_json FROM events
               WHERE event_kind = 'validated_request_emit'
                 AND repo_area = ?
               ORDER BY ts_utc DESC LIMIT 1""",
            (str(output_dir),),
        )
        row = cur.fetchone()
    finally:
        con.close()
    assert row is not None
    assert row[0] == "validated_request_emit"
    # The prediction JSON includes the canonical fields.
    pred = row[1] or ""
    assert "interview_slug" in pred
    assert "schema_verdict" in pred


# ---------------------------------------------------------------------------
# Scanner integration: apps_qna is now APP_OVERLAY_STATIC_EVIDENCE
# ---------------------------------------------------------------------------


def test_apps_qna_classified_as_overlay_static_evidence_post_w7() -> None:
    """After W7 (manifest + spine_handoff.py), the scanner must classify
    apps_qna as APP_OVERLAY_STATIC_EVIDENCE."""
    from tools.analysis.apps_spine_coverage import classify_app, scan_app

    repo_root = Path(__file__).resolve().parents[2]
    apps_qna = repo_root / "apps_qna"
    if not apps_qna.is_dir():
        pytest.skip("apps_qna not present in this checkout")
    sc = scan_app(apps_qna)
    runtime_mode, evidence = classify_app(sc)
    assert sc["manifest_present"] is True
    assert "build_time_compiler" in sc["manifest_claimed_routes"]
    assert runtime_mode == "APP_OVERLAY_STATIC_EVIDENCE", (
        f"got runtime_mode={runtime_mode}; evidence={evidence}"
    )


def test_apps_qna_imports_validated_request() -> None:
    """The W7 spine_handoff must import ValidatedRequest from agentic_core.

    This is the load-bearing static evidence: the canonical contract
    type is imported AT MODULE LEVEL, not lazily, so the scanner sees
    it without having to execute the module.
    """
    handoff_path = (
        Path(__file__).resolve().parents[1]
        / "integrations"
        / "spine_handoff.py"
    )
    assert handoff_path.is_file()
    text = handoff_path.read_text(encoding="utf-8")
    # Hard-pinned: the spine intake contract import must be present.
    assert "from agentic_core.L0_routing.intake.validated_request import ValidatedRequest" in text


def test_apps_qna_spine_manifest_yaml_exists_and_declares_build_time_compiler() -> None:
    """The manifest must declare build_time_compiler explicitly."""
    manifest_path = (
        Path(__file__).resolve().parents[1] / "spine_manifest.yaml"
    )
    assert manifest_path.is_file()
    data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    assert data["app"] == "apps_qna"
    routes = data["claimed_routes"]
    types = [r["type"] for r in routes if isinstance(r, dict)]
    assert "build_time_compiler" in types

"""Envelope roundtrip, hash, TTL, and schema-gate tests.

Plan: apps-cross-app-precursors-c94c71 Wave 2.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from apps_shared.contracts.cross_app import (
    EnvelopeExpiredError,
    EnvelopeHashMismatchError,
    EnvelopeSchemaError,
    ExecutiveBriefEnvelope,
    ExperienceLibraryEnvelope,
    ResearchBriefEnvelope,
    ResumeBankEnvelope,
    compute_sha256,
)
from apps_shared.contracts.cross_app.executive_brief import ExecutiveBriefPayload
from apps_shared.contracts.cross_app.experience_library import (
    ExperienceBullet,
    ExperienceLibraryPayload,
)
from apps_shared.contracts.cross_app.research_brief import (
    ResearchBriefPayload,
    ResearchClaimRow,
)
from apps_shared.contracts.cross_app.resume_bank import ResumeBankPayload


def _experience_payload() -> ExperienceLibraryPayload:
    return ExperienceLibraryPayload(
        source_file="apps_shared/data/master_resume.json",
        variant="default",
        executive_summary="Summary",
        competency_areas=[{"area": "Agentic", "skills": ["python"]}],
        bullets=[
            ExperienceBullet(
                label="Lead",
                text="Led X.",
                tags=["leadership"],
                role_title="VP",
            )
        ],
    )


def _research_payload() -> ResearchBriefPayload:
    return ResearchBriefPayload(
        brief_path="reports/research/research_brief_abc123.md",
        register_path="reports/research/source_register_abc123.json",
        company_brief="Acme is a widget leader.",
        role_areas_of_focus=["platform", "governance"],
        industry_trends=["verticalization"],
        source_register=[
            ResearchClaimRow(
                claim="Revenue grew 20%",
                claim_type="direct_evidence",
                source_id="SRC-001",
                section_id="financials",
            )
        ],
    )


def _exec_payload() -> ExecutiveBriefPayload:
    return ExecutiveBriefPayload(
        brief_path="reports/executive/exec_brief_abc.md",
        close_patterns=["pattern 1", "pattern 2"],
        thesis_lines=["thesis"],
    )


def _resume_bank_payload() -> ResumeBankPayload:
    return ResumeBankPayload(
        source_file="apps_rg/data/resume_bank.yaml",
        master_resume_source_sha256="0" * 64,
        points=[{"title": "t", "one_liner": "o"}],
        star_bank={"stories": []},
        rca_bank=[],
    )


# ------- emit + load roundtrip -------


def _roundtrip(tmp_path: Path, cls, payload) -> None:
    env = cls.emit(trace_id="abc123", payload=payload)
    assert env.source_sha256 == compute_sha256(payload)
    assert env.schema_name == cls.SCHEMA_NAME
    path = tmp_path / "env.json"
    env.write_sidecar(path)
    loaded = cls.load(path)
    assert loaded.payload == payload
    assert loaded.source_sha256 == env.source_sha256


def test_experience_library_roundtrip(tmp_path):
    _roundtrip(tmp_path, ExperienceLibraryEnvelope, _experience_payload())


def test_research_brief_roundtrip(tmp_path):
    _roundtrip(tmp_path, ResearchBriefEnvelope, _research_payload())


def test_executive_brief_roundtrip(tmp_path):
    _roundtrip(tmp_path, ExecutiveBriefEnvelope, _exec_payload())


def test_resume_bank_roundtrip(tmp_path):
    _roundtrip(tmp_path, ResumeBankEnvelope, _resume_bank_payload())


# ------- hash mismatch -------


def test_hash_mismatch_detected(tmp_path):
    env = ExecutiveBriefEnvelope.emit(
        trace_id="abc", payload=_exec_payload()
    )
    path = tmp_path / "env.json"
    env.write_sidecar(path)
    # Tamper: rewrite payload.close_patterns without updating hash.
    data = json.loads(path.read_text(encoding="utf-8"))
    data["payload"]["close_patterns"] = ["tampered"]
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(EnvelopeHashMismatchError):
        ExecutiveBriefEnvelope.load(path)


# ------- schema gate -------


def test_schema_name_mismatch(tmp_path):
    env = ExecutiveBriefEnvelope.emit(
        trace_id="abc", payload=_exec_payload()
    )
    path = tmp_path / "env.json"
    env.write_sidecar(path)
    # Try to load as a different envelope type.
    with pytest.raises(EnvelopeSchemaError):
        ResearchBriefEnvelope.load(path)


def test_schema_version_major_mismatch(tmp_path):
    env = ExecutiveBriefEnvelope.emit(
        trace_id="abc",
        payload=_exec_payload(),
        schema_version="2.0.0",
    )
    path = tmp_path / "env.json"
    env.write_sidecar(path)
    with pytest.raises(EnvelopeSchemaError):
        ExecutiveBriefEnvelope.load(path)


def test_schema_version_malformed(tmp_path):
    # Construct directly since emit() will validate semver shape elsewhere.
    payload = _exec_payload()
    env = ExecutiveBriefEnvelope(
        schema_name=ExecutiveBriefEnvelope.SCHEMA_NAME,
        schema_version="not-a-semver",
        trace_id="abc",
        producer_app="apps_exec",
        emitted_at=datetime.now(timezone.utc),
        source_sha256=compute_sha256(payload),
        ttl_days=30,
        payload=payload,
    )
    path = tmp_path / "env.json"
    env.write_sidecar(path)
    with pytest.raises(EnvelopeSchemaError):
        ExecutiveBriefEnvelope.load(path)


# ------- TTL -------


def test_expired_raises(tmp_path):
    payload = _exec_payload()
    env = ExecutiveBriefEnvelope(
        schema_name=ExecutiveBriefEnvelope.SCHEMA_NAME,
        schema_version="1.0.0",
        trace_id="abc",
        producer_app="apps_exec",
        emitted_at=datetime.now(timezone.utc) - timedelta(days=100),
        source_sha256=compute_sha256(payload),
        ttl_days=30,
        payload=payload,
    )
    path = tmp_path / "env.json"
    env.write_sidecar(path)
    with pytest.raises(EnvelopeExpiredError):
        ExecutiveBriefEnvelope.load(path)
    # But skippable:
    loaded = ExecutiveBriefEnvelope.load(path, check_expiry=False)
    assert loaded.is_expired()


def test_ttl_zero_never_expires(tmp_path):
    payload = _exec_payload()
    env = ExecutiveBriefEnvelope(
        schema_name=ExecutiveBriefEnvelope.SCHEMA_NAME,
        schema_version="1.0.0",
        trace_id="abc",
        producer_app="apps_exec",
        emitted_at=datetime.now(timezone.utc) - timedelta(days=3650),
        source_sha256=compute_sha256(payload),
        ttl_days=0,
        payload=payload,
    )
    path = tmp_path / "env.json"
    env.write_sidecar(path)
    loaded = ExecutiveBriefEnvelope.load(path)
    assert not loaded.is_expired()


# ------- default sidecar path -------


def test_default_sidecar_paths(tmp_path):
    env = ResearchBriefEnvelope.emit(
        trace_id="deadbeef", payload=_research_payload()
    )
    assert env.default_sidecar_path().name == (
        "research_brief_deadbeef.envelope.json"
    )
    env2 = ExperienceLibraryEnvelope.emit(
        trace_id="t", payload=_experience_payload()
    )
    assert env2.default_sidecar_path().name == "master_resume.envelope.json"

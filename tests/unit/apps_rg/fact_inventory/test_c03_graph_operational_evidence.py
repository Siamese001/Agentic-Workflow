"""apps-test-model: LAW."""

from __future__ import annotations

import json
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pytest

from apps_rg.fact_inventory import c03_graph_operational_evidence as operational_evidence
from apps_rg.fact_inventory.c03_graph_operational_evidence import (
    METRIC_IDS,
    ArtifactReferenceInput,
    OperationalEvidenceError,
    OperationalTrustContext,
    ProducerBindingInput,
    assemble_operational_evidence_envelope,
    compute_binding_anchor_digest,
    compute_envelope_integrity,
    verify_operational_evidence_envelope,
)

OBSERVED_AT = datetime(2026, 7, 19, 16, 0, tzinfo=timezone.utc)
CANDIDATE_SHA = "a" * 40
GRAPH_SHA256 = "b" * 64
POLICY_SHA256 = "c" * 64
HEALTH_RUN_ID = "health-run-001"
KNOWN_PRODUCER = "apps_rg.resume_graph_w6_ci_receipt.v1"
KNOWN_SCHEMA = "apps_rg.resume_graph_w6_ci_receipt.v1"


def _context(
    root: Path,
    *,
    anchors: dict[str, str] | None = None,
    candidate_sha: str = CANDIDATE_SHA,
    observed_at: datetime = OBSERVED_AT,
    max_replay_age: timedelta = timedelta(days=7),
) -> OperationalTrustContext:
    return OperationalTrustContext(
        artifact_roots={"run-output": root},
        authority_anchors=anchors or {},
        expected_candidate_commit_sha=candidate_sha,
        expected_canonical_graph_sha256=GRAPH_SHA256,
        expected_health_policy_sha256=POLICY_SHA256,
        expected_health_run_id=HEALTH_RUN_ID,
        observed_at_utc=observed_at,
        max_replay_age=max_replay_age,
    )


def _write_ci_receipt(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "schema_version": KNOWN_SCHEMA,
                "record_digest": "d" * 64,
                "gate_results": {},
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )


def _binding(
    *,
    producer_id: str = KNOWN_PRODUCER,
    producer_schema_version: str = KNOWN_SCHEMA,
    role: str = "ci_receipt",
    relative_path: str = "w6_ci_receipt.json",
    cohort_as_of: datetime | None = None,
    cohort_closed_at: datetime | None = None,
) -> ProducerBindingInput:
    return ProducerBindingInput(
        producer_id=producer_id,
        producer_schema_version=producer_schema_version,
        producer_run_id=HEALTH_RUN_ID,
        cohort_id="decision-safe-cohort-001",
        cohort_as_of_utc=cohort_as_of or OBSERVED_AT - timedelta(hours=2),
        cohort_closed_at_utc=cohort_closed_at or OBSERVED_AT - timedelta(hours=1),
        authority_anchor_id="anchor:w6-ci",
        artifact_refs=(
            ArtifactReferenceInput(
                role=role,
                artifact_root_id="run-output",
                relative_path=relative_path,
            ),
        ),
    )


def _assemble(
    root: Path,
    *,
    context: OperationalTrustContext | None = None,
    binding: ProducerBindingInput | None = None,
) -> dict[str, Any]:
    selected_context = context or _context(root)
    return assemble_operational_evidence_envelope(
        envelope_id="operational-envelope-001",
        assembled_at_utc=OBSERVED_AT,
        bindings={"decision_safe_regression": binding or _binding()},
        context=selected_context,
    )


def _metric(report: Any, metric_id: str) -> Any:
    return next(row for row in report.metrics if row.metric_id == metric_id)


def _retag_integrity(envelope: dict[str, Any]) -> None:
    envelope["integrity_sha256"] = compute_envelope_integrity(envelope)


def _anchored_context(root: Path, envelope: dict[str, Any]) -> OperationalTrustContext:
    binding = envelope["bindings"]["decision_safe_regression"]
    anchor_digest = compute_binding_anchor_digest(
        "decision_safe_regression",
        binding,
        subject=envelope["subject"],
        producer_registry_version=envelope["producer_registry_version"],
    )
    return _context(
        root,
        anchors={binding["authority_anchor_id"]: anchor_digest},
        candidate_sha=envelope["subject"]["candidate_commit_sha"],
    )


def test_v1_verified_self_hash_is_rejected() -> None:
    evidence = {
        "schema_version": "apps_rg.c03_graph_health_operational_evidence.v1",
        "authority_status": "VERIFIED",
        "cohort_id": "caller-authored",
        "cohort_digest": "a" * 64,
        "decision_safe_regression": {"passed": 1, "total": 1},
    }

    report = verify_operational_evidence_envelope(
        evidence,
        context=_context(Path.cwd()),
    )

    assert report.schema_valid is False
    assert {row.status for row in report.metrics} == {"UNKNOWN"}
    assert all("envelope_schema_invalid" in row.reason_codes for row in report.metrics)


@pytest.mark.parametrize(
    "untrusted_fields",
    [
        {"authority_status": "VERIFIED"},
        {"numerator": 7, "denominator": 7},
        {"metrics": {"decision_safe_regression": {"status": "PASS"}}},
    ],
)
def test_caller_status_and_counts_are_schema_rejected(
    tmp_path: Path,
    untrusted_fields: dict[str, Any],
) -> None:
    artifact = tmp_path / "w6_ci_receipt.json"
    _write_ci_receipt(artifact)
    envelope = _assemble(tmp_path)
    envelope.update(untrusted_fields)
    _retag_integrity(envelope)

    report = verify_operational_evidence_envelope(envelope, context=_context(tmp_path))

    assert report.schema_valid is False
    assert {row.status for row in report.metrics} == {"UNKNOWN"}


@pytest.mark.parametrize(
    ("binding", "reason_code"),
    [
        (_binding(producer_id="caller.fake.producer.v1"), "producer_not_registered"),
        (
            _binding(producer_schema_version="apps_rg.resume_graph_w6_ci_receipt.v999"),
            "producer_schema_not_registered",
        ),
        (_binding(role="caller_supplied_role"), "producer_artifact_role_not_registered"),
    ],
)
def test_unknown_producer_schema_and_role_remain_unknown(
    tmp_path: Path,
    binding: ProducerBindingInput,
    reason_code: str,
) -> None:
    artifact = tmp_path / "w6_ci_receipt.json"
    _write_ci_receipt(artifact)
    envelope = _assemble(tmp_path, binding=binding)

    report = verify_operational_evidence_envelope(envelope, context=_context(tmp_path))

    result = _metric(report, "decision_safe_regression")
    assert result.status == "UNKNOWN"
    assert reason_code in result.reason_codes


def test_missing_out_of_band_anchor_remains_unknown_without_artifact_io(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    artifact = tmp_path / "w6_ci_receipt.json"
    _write_ci_receipt(artifact)
    envelope = _assemble(tmp_path)
    monkeypatch.setattr(
        operational_evidence,
        "_read_trusted_artifact_snapshot",
        lambda _root, _relative_path: pytest.fail(
            "artifact bytes were read before authority was established"
        ),
    )

    report = verify_operational_evidence_envelope(envelope, context=_context(tmp_path))

    result = _metric(report, "decision_safe_regression")
    assert result.status == "UNKNOWN"
    assert "authority_anchor_missing" in result.reason_codes


def test_missing_artifact_after_assembly_remains_unknown(tmp_path: Path) -> None:
    artifact = tmp_path / "w6_ci_receipt.json"
    _write_ci_receipt(artifact)
    envelope = _assemble(tmp_path)
    pinned_context = _anchored_context(tmp_path, envelope)
    artifact.unlink()

    report = verify_operational_evidence_envelope(envelope, context=pinned_context)

    result = _metric(report, "decision_safe_regression")
    assert result.status == "UNKNOWN"
    assert "artifact_missing" in result.reason_codes


def test_artifact_hash_mismatch_after_assembly_remains_unknown(tmp_path: Path) -> None:
    artifact = tmp_path / "w6_ci_receipt.json"
    _write_ci_receipt(artifact)
    envelope = _assemble(tmp_path)
    pinned_context = _anchored_context(tmp_path, envelope)
    artifact.write_text("{}", encoding="utf-8")

    report = verify_operational_evidence_envelope(envelope, context=pinned_context)

    result = _metric(report, "decision_safe_regression")
    assert result.status == "UNKNOWN"
    assert "artifact_sha256_mismatch" in result.reason_codes


def test_artifact_size_limit_fails_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    artifact = tmp_path / "w6_ci_receipt.json"
    _write_ci_receipt(artifact)
    envelope = _assemble(tmp_path)
    pinned_context = _anchored_context(tmp_path, envelope)
    monkeypatch.setattr(operational_evidence, "MAX_ARTIFACT_BYTES", 1)

    report = verify_operational_evidence_envelope(envelope, context=pinned_context)

    result = _metric(report, "decision_safe_regression")
    assert result.status == "UNKNOWN"
    assert "artifact_size_limit_exceeded" in result.reason_codes


def test_root_escape_is_rejected_by_assembler_and_verifier(tmp_path: Path) -> None:
    artifact = tmp_path / "w6_ci_receipt.json"
    _write_ci_receipt(artifact)
    unsafe_binding = _binding(relative_path="../outside.json")

    with pytest.raises(OperationalEvidenceError, match="relative path"):
        _assemble(tmp_path, binding=unsafe_binding)

    envelope = _assemble(tmp_path)
    envelope["bindings"]["decision_safe_regression"]["artifact_refs"][0]["relative_path"] = "../outside.json"
    _retag_integrity(envelope)
    report = verify_operational_evidence_envelope(envelope, context=_context(tmp_path))

    result = _metric(report, "decision_safe_regression")
    assert result.status == "UNKNOWN"
    assert report.schema_valid is False
    assert "envelope_schema_invalid" in result.reason_codes


def test_wrong_subject_invalidates_every_metric(tmp_path: Path) -> None:
    artifact = tmp_path / "w6_ci_receipt.json"
    _write_ci_receipt(artifact)
    envelope = _assemble(tmp_path)
    wrong_context = _context(tmp_path, candidate_sha="f" * 40)

    report = verify_operational_evidence_envelope(envelope, context=wrong_context)

    assert report.subject_valid is False
    assert {row.status for row in report.metrics} == {"UNKNOWN"}
    assert all("envelope_subject_mismatch" in row.reason_codes for row in report.metrics)


def test_replayed_cohort_outside_window_remains_unknown(tmp_path: Path) -> None:
    artifact = tmp_path / "w6_ci_receipt.json"
    _write_ci_receipt(artifact)
    stale_binding = _binding(
        cohort_as_of=OBSERVED_AT - timedelta(days=10, hours=1),
        cohort_closed_at=OBSERVED_AT - timedelta(days=10),
    )
    envelope = _assemble(tmp_path, binding=stale_binding)

    report = verify_operational_evidence_envelope(envelope, context=_context(tmp_path))

    result = _metric(report, "decision_safe_regression")
    assert result.status == "UNKNOWN"
    assert "cohort_replay_window_exceeded" in result.reason_codes


def test_subsecond_reverse_order_and_future_cohorts_fail_closed(
    tmp_path: Path,
) -> None:
    artifact = tmp_path / "w6_ci_receipt.json"
    _write_ci_receipt(artifact)
    closed_at = OBSERVED_AT - timedelta(seconds=1, microseconds=200)
    reversed_envelope = _assemble(
        tmp_path,
        binding=_binding(
            cohort_as_of=closed_at + timedelta(microseconds=100),
            cohort_closed_at=closed_at,
        ),
    )
    reversed_binding = reversed_envelope["bindings"]["decision_safe_regression"]
    assert reversed_binding["cohort_as_of_utc"] != reversed_binding["cohort_closed_at_utc"]

    reversed_report = verify_operational_evidence_envelope(
        reversed_envelope,
        context=_context(tmp_path),
    )
    assert (
        "cohort_timestamp_order_invalid"
        in _metric(
            reversed_report,
            "decision_safe_regression",
        ).reason_codes
    )

    future_envelope = _assemble(
        tmp_path,
        binding=_binding(
            cohort_as_of=OBSERVED_AT - timedelta(seconds=1),
            cohort_closed_at=OBSERVED_AT + timedelta(microseconds=1),
        ),
    )
    future_report = verify_operational_evidence_envelope(
        future_envelope,
        context=_context(tmp_path),
    )
    assert (
        "cohort_timestamp_in_future"
        in _metric(
            future_report,
            "decision_safe_regression",
        ).reason_codes
    )


def test_subsecond_replay_boundary_is_exact(tmp_path: Path) -> None:
    artifact = tmp_path / "w6_ci_receipt.json"
    _write_ci_receipt(artifact)
    exact_closed_at = OBSERVED_AT - timedelta(days=7)
    exact_envelope = _assemble(
        tmp_path,
        binding=_binding(
            cohort_as_of=exact_closed_at - timedelta(hours=1),
            cohort_closed_at=exact_closed_at,
        ),
    )
    exact_report = verify_operational_evidence_envelope(
        exact_envelope,
        context=_anchored_context(tmp_path, exact_envelope),
    )
    exact_result = _metric(exact_report, "decision_safe_regression")
    assert "cohort_replay_window_exceeded" not in exact_result.reason_codes
    assert "producer_not_registered_for_metric" in exact_result.reason_codes

    expired_envelope = _assemble(
        tmp_path,
        binding=_binding(
            cohort_as_of=exact_closed_at - timedelta(hours=1),
            cohort_closed_at=exact_closed_at - timedelta(microseconds=1),
        ),
    )
    expired_report = verify_operational_evidence_envelope(
        expired_envelope,
        context=_context(tmp_path),
    )
    assert (
        "cohort_replay_window_exceeded"
        in _metric(
            expired_report,
            "decision_safe_regression",
        ).reason_codes
    )


def test_integrity_tamper_invalidates_every_metric(tmp_path: Path) -> None:
    artifact = tmp_path / "w6_ci_receipt.json"
    _write_ci_receipt(artifact)
    envelope = _assemble(tmp_path)
    envelope["bindings"]["decision_safe_regression"]["cohort_id"] = "tampered"

    report = verify_operational_evidence_envelope(envelope, context=_context(tmp_path))

    assert report.integrity_valid is False
    assert {row.status for row in report.metrics} == {"UNKNOWN"}
    assert all("envelope_integrity_mismatch" in row.reason_codes for row in report.metrics)


def test_authority_anchor_cannot_be_transplanted_to_another_subject(tmp_path: Path) -> None:
    artifact = tmp_path / "w6_ci_receipt.json"
    _write_ci_receipt(artifact)
    envelope = _assemble(tmp_path)
    original_context = _anchored_context(tmp_path, envelope)
    envelope["subject"]["candidate_commit_sha"] = "f" * 40
    _retag_integrity(envelope)
    transplanted_context = replace(
        original_context,
        expected_candidate_commit_sha="f" * 40,
    )

    report = verify_operational_evidence_envelope(envelope, context=transplanted_context)

    assert report.subject_valid is True
    result = _metric(report, "decision_safe_regression")
    assert result.status == "UNKNOWN"
    assert "authority_anchor_mismatch" in result.reason_codes


def test_digest_and_schema_use_one_artifact_snapshot(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    artifact = tmp_path / "w6_ci_receipt.json"
    _write_ci_receipt(artifact)
    envelope = _assemble(tmp_path)
    pinned_context = _anchored_context(tmp_path, envelope)
    read_snapshot = operational_evidence._read_trusted_artifact_snapshot

    def _read_then_replace(root: Path, relative_path: str) -> bytes:
        snapshot = read_snapshot(root, relative_path)
        root.joinpath(*relative_path.split("/")).write_text("{}", encoding="utf-8")
        return snapshot

    monkeypatch.setattr(
        operational_evidence,
        "_read_trusted_artifact_snapshot",
        _read_then_replace,
    )

    report = verify_operational_evidence_envelope(envelope, context=pinned_context)

    result = _metric(report, "decision_safe_regression")
    assert result.status == "UNKNOWN"
    assert "producer_not_registered_for_metric" in result.reason_codes
    assert "producer_artifact_schema_mismatch" not in result.reason_codes


def test_symlink_artifact_is_rejected_even_when_target_is_inside_root(
    tmp_path: Path,
) -> None:
    artifact = tmp_path / "real_receipt.json"
    link = tmp_path / "w6_ci_receipt.json"
    _write_ci_receipt(artifact)
    try:
        link.symlink_to(artifact.name)
    except OSError as exc:
        pytest.skip(f"symlink creation unavailable: {exc}")

    with pytest.raises(OperationalEvidenceError, match="symlinks or junctions"):
        _assemble(tmp_path)


def test_emulated_linklike_component_fails_closed_on_all_platforms(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    artifact = tmp_path / "w6_ci_receipt.json"
    _write_ci_receipt(artifact)
    real_link_check = operational_evidence._is_link_or_junction
    monkeypatch.setattr(
        operational_evidence,
        "_is_link_or_junction",
        lambda path: path == artifact or real_link_check(path),
    )

    with pytest.raises(OperationalEvidenceError, match="symlinks or junctions"):
        _assemble(tmp_path)


def test_artifact_replacement_during_open_snapshot_fails_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    artifact = tmp_path / "w6_ci_receipt.json"
    replacement = tmp_path / "replacement.json"
    _write_ci_receipt(artifact)
    _write_ci_receipt(replacement)
    envelope = _assemble(tmp_path)
    pinned_context = _anchored_context(tmp_path, envelope)
    validate_identity = operational_evidence._validate_open_artifact_identity
    calls = 0

    def _replace_before_final_identity_check(handle: Any, **kwargs: Any) -> Any:
        nonlocal calls
        calls += 1
        if calls == 2:
            try:
                replacement.replace(kwargs["candidate"])
            except OSError as exc:
                pytest.skip(f"open-file replacement unavailable on this platform: {exc}")
        return validate_identity(handle, **kwargs)

    monkeypatch.setattr(
        operational_evidence,
        "_validate_open_artifact_identity",
        _replace_before_final_identity_check,
    )
    report = verify_operational_evidence_envelope(envelope, context=pinned_context)

    result = _metric(report, "decision_safe_regression")
    assert "artifact_identity_changed" in result.reason_codes


def test_opened_path_identity_mismatch_fails_closed_on_all_platforms(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    artifact = tmp_path / "w6_ci_receipt.json"
    _write_ci_receipt(artifact)
    envelope = _assemble(tmp_path)
    pinned_context = _anchored_context(tmp_path, envelope)
    monkeypatch.setattr(operational_evidence.os.path, "samestat", lambda _left, _right: False)

    report = verify_operational_evidence_envelope(envelope, context=pinned_context)

    result = _metric(report, "decision_safe_regression")
    assert "artifact_identity_changed" in result.reason_codes


def test_assembly_is_refs_only_and_verification_is_immutable(tmp_path: Path) -> None:
    artifact = tmp_path / "w6_ci_receipt.json"
    _write_ci_receipt(artifact)
    before_bytes = artifact.read_bytes()
    before_names = sorted(path.name for path in tmp_path.iterdir())
    context = _context(tmp_path)

    envelope = _assemble(tmp_path, context=context)
    binding = envelope["bindings"]["decision_safe_regression"]
    pinned_context = _anchored_context(tmp_path, envelope)
    report = verify_operational_evidence_envelope(envelope, context=pinned_context)

    encoded = json.dumps(envelope, sort_keys=True)
    assert "VERIFIED" not in encoded
    assert not ({"authority_status", "status", "numerator", "denominator", "metrics"} & envelope.keys())
    assert binding["artifact_refs"][0]["sha256"]
    assert compute_envelope_integrity(envelope) == envelope["integrity_sha256"]
    assert artifact.read_bytes() == before_bytes
    assert sorted(path.name for path in tmp_path.iterdir()) == before_names
    assert len(report.metrics) == len(METRIC_IDS)
    assert {row.status for row in report.metrics} == {"UNKNOWN"}
    assert (
        "producer_not_registered_for_metric"
        in _metric(
            report,
            "decision_safe_regression",
        ).reason_codes
    )

from __future__ import annotations

import json
from dataclasses import asdict, replace
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from apps_rg.runtime.bindings.l2_authority import (
    _validate_u0_authority_receipt_binding,
)
from apps_rg.runtime.bindings.u0_binding import (
    APPS_RG_U0_AUTHORITY_CONTRACT_ID,
    AppsRgU0AuthorityReceipt,
    apps_rg_u0_authority_receipt_digest,
    u0_validate_apps_rg,
)
from apps_rg.runtime.dispatch.apps_rg_dispatch import apps_rg_parse
from apps_rg.runtime.runtime_proof_layout import MODULAR_R4_SECTIONS_ROOT_ENV
from apps_rg.runtime.spine.front_contracts import (
    build_section_front_spine_from_args,
    emit_section_front_spine_receipts,
)
from apps_rg.runtime.spine.spine_contract_loaders import (
    load_validated_request_from_artifact_dir,
)
from apps_rg.runtime.spine.validated_request_contract import (
    CANONICAL_APPS_RG_VALIDATED_REQUEST_FILENAME,
    ValidatedRequestContractError,
    load_validated_request_contract,
    write_validated_request_contract,
)


def _validated_request() -> Any:
    envelope = apps_rg_parse(
        {
            "app_id": "apps_rg",
            "task_class": "resume_generation",
            "target_company": "Unify Consulting",
            "target_role": "SVP Technical Pre-Sales, Enterprise Cloud & AI Solutions",
            "source_resume_text": "Grounded resume source.",
            "job_description_text": "Lead enterprise cloud and AI pre-sales.",
            "briefing_artifact_ref": "artifact:grounded-unify-brief",
            "l5_certification_ref": "test:valid:w6",
            "request_id": "req-s2u0",
            "run_id": "run-s2u0",
            "trace_id": "trace-s2u0",
            "tenant_id": "tenant-s2u0",
        }
    )
    assert envelope is not None
    return u0_validate_apps_rg(envelope)


def _resign(receipt: AppsRgU0AuthorityReceipt, **changes: Any) -> AppsRgU0AuthorityReceipt:
    changed = replace(receipt, authority_receipt_digest="", **changes)
    return replace(
        changed,
        authority_receipt_digest=apps_rg_u0_authority_receipt_digest(changed),
    )


def test_genuine_u0_receipt_round_trips_losslessly(tmp_path: Path) -> None:
    original = _validated_request()
    path = tmp_path / CANONICAL_APPS_RG_VALIDATED_REQUEST_FILENAME

    write_validated_request_contract(path, original, consumer_stage="section_lane_modular")
    loaded = load_validated_request_contract(path)

    assert asdict(loaded) == asdict(original)
    assert loaded.authority_validation_receipt == original.authority_validation_receipt
    assert loaded.request_id == original.request_id
    assert loaded.run_id == original.run_id
    assert loaded.trace_id == original.trace_id
    assert loaded.tenant_id == original.tenant_id
    assert loaded.payload_digest == original.payload_digest
    _validate_u0_authority_receipt_binding(loaded)


def test_whole_run_section_front_reuses_canonical_u0_without_minting(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original = _validated_request()
    run_root = tmp_path / "run"
    sections_root = run_root / "modular_r4" / "sections"
    sections_root.mkdir(parents=True)
    write_validated_request_contract(
        run_root / CANONICAL_APPS_RG_VALIDATED_REQUEST_FILENAME,
        original,
        consumer_stage="section_lane_modular",
    )
    monkeypatch.setenv("APPS_RG_WHOLE_RUN_ENVELOPE", "1")
    monkeypatch.setenv(MODULAR_R4_SECTIONS_ROOT_ENV, str(sections_root))

    def _forbidden_second_u0(*_args: Any, **_kwargs: Any) -> Any:
        raise AssertionError("whole-run section dispatch must not mint another U0 receipt")

    monkeypatch.setattr(
        "apps_rg.runtime.bindings.u0_binding.u0_validate_apps_rg",
        _forbidden_second_u0,
    )
    args = SimpleNamespace(
        target_company="Unify Consulting",
        target_title="SVP Technical Pre-Sales, Enterprise Cloud & AI Solutions",
        target_role="SVP Technical Pre-Sales, Enterprise Cloud & AI Solutions",
        target_level="EXECUTIVE",
        jd_text="Lead enterprise cloud and AI pre-sales.",
        briefing="Grounded public company and role evidence.",
        base_resume_ref="",
        tenant_id="tenant-s2u0",
    )

    front = build_section_front_spine_from_args(
        section_id="competencies",
        args=args,
        repo_root=Path(__file__).resolve().parents[5],
    )

    assert front.validated_request.authority_validation_receipt is original.authority_validation_receipt or (
        front.validated_request.authority_validation_receipt
        == original.authority_validation_receipt
    )
    assert front.validated_request.request_id == original.request_id
    assert front.validated_request.run_id == original.run_id
    assert front.validated_request.trace_id == original.trace_id
    _validate_u0_authority_receipt_binding(front.validated_request)

    lane_artifacts = sections_root / "competencies"
    emit_section_front_spine_receipts(lane_artifacts, front)
    loaded_for_l2 = load_validated_request_from_artifact_dir(lane_artifacts)
    assert loaded_for_l2 is not None
    assert loaded_for_l2.authority_validation_receipt == original.authority_validation_receipt
    _validate_u0_authority_receipt_binding(loaded_for_l2)


@pytest.mark.parametrize(
    "mutation",
    (
        "missing",
        "failed",
        "malformed",
        "wrong_run",
        "wrong_request",
        "digest_drift",
        "apps_research_substitution",
        "unknown",
    ),
)
def test_l2_rejects_invalid_or_substituted_u0_receipts(mutation: str) -> None:
    request = _validated_request()
    receipt = request.authority_validation_receipt
    if mutation == "missing":
        candidate = replace(request, authority_validation_receipt=None)
    elif mutation == "failed":
        candidate = replace(request, authority_validation_receipt=_resign(receipt, validation_passed=False))
    elif mutation == "malformed":
        candidate = replace(request, authority_validation_receipt={"validation_passed": True})
    elif mutation == "wrong_run":
        candidate = replace(request, authority_validation_receipt=_resign(receipt, run_id="run-other"))
    elif mutation == "wrong_request":
        candidate = replace(
            request,
            authority_validation_receipt=_resign(receipt, request_id="req-other"),
        )
    elif mutation == "digest_drift":
        candidate = replace(request, payload_digest="0" * 64)
    elif mutation == "apps_research_substitution":
        candidate = replace(
            request,
            authority_validation_receipt={
                "authority_contract_id": "apps_research.u0.authority_validation.v1",
                "validation_passed": True,
            },
        )
    else:
        candidate = replace(
            request,
            authority_validation_receipt=_resign(receipt, validation_passed="UNKNOWN"),
        )

    with pytest.raises(Exception, match="V0_U0_AUTHORITY_RECEIPT"):
        _validate_u0_authority_receipt_binding(candidate)


def test_authority_contract_and_receipt_digest_are_bound_at_u0() -> None:
    request = _validated_request()
    receipt = request.authority_validation_receipt

    assert receipt.authority_contract_id == APPS_RG_U0_AUTHORITY_CONTRACT_ID
    assert receipt.request_id == request.request_id
    assert receipt.run_id == request.run_id
    assert receipt.trace_id == request.trace_id
    assert receipt.trace_root == request.trace_root
    assert receipt.tenant_id == request.tenant_id
    assert receipt.validated_input_digest == request.payload_digest
    assert receipt.authority_receipt_digest == apps_rg_u0_authority_receipt_digest(receipt)


def test_validated_request_contract_digest_detects_serialized_drift(tmp_path: Path) -> None:
    path = tmp_path / CANONICAL_APPS_RG_VALIDATED_REQUEST_FILENAME
    write_validated_request_contract(path, _validated_request(), consumer_stage="competencies")
    raw = path.read_text(encoding="utf-8")
    path.write_text(raw.replace("run-s2u0", "run-other", 1), encoding="utf-8")

    with pytest.raises(ValidatedRequestContractError, match="artifact_hash"):
        load_validated_request_contract(path)


def test_validated_request_contract_requires_artifact_hash(tmp_path: Path) -> None:
    path = tmp_path / CANONICAL_APPS_RG_VALIDATED_REQUEST_FILENAME
    write_validated_request_contract(path, _validated_request(), consumer_stage="competencies")
    document = json.loads(path.read_text(encoding="utf-8"))
    del document["artifact_hash"]
    path.write_text(json.dumps(document), encoding="utf-8")

    with pytest.raises(ValidatedRequestContractError, match="artifact_hash"):
        load_validated_request_contract(path)

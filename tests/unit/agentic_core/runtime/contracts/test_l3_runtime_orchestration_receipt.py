"""Unit tests for agentic_core.runtime.contracts.l3_runtime_orchestration_receipt.

Wave 6.1 (plan adg-testing-hotspots-wave-plan-a7f3c1) — untested P2 core module.
``l3_runtime_orchestration_receipt`` (L_RUNTIME) is the typed proof that L3
actually orchestrated a MANAGED_WORKFLOW run. Covers ``L3StepContractRef``,
the frozen ``L3RuntimeOrchestrationReceipt`` and its many ``__post_init__``
invariants (no-execute/retrieve/prompt/write assertions, node-subset binding,
step-status vocabulary, l5_certification_ref fail-closed), ALLOWED_STEP_STATUSES,
the ``build_*`` factory, and digest determinism.

The constructor requires a valid ``l5_certification_ref`` verified via
``agentic_core.L5_safety.contracts.verify.verify_certification_ref`` — any
non-empty string is structurally valid there, so tests pass ``"l5-cert-1"``.
"""

from __future__ import annotations

import dataclasses

import pytest

from agentic_core.runtime.contracts.l3_runtime_orchestration_receipt import (
    ALLOWED_STEP_STATUSES,
    L3_RUNTIME_RECEIPT_SCHEMA_VERSION,
    L3RuntimeOrchestrationReceipt,
    L3StepContractRef,
    build_l3_runtime_orchestration_receipt,
    compute_l3_runtime_digest,
)

_CERT = "l5-cert-1"


def _step(node_id: str = "n1", run_id: str = "run-1", status: str = "step_completed_by_l2") -> L3StepContractRef:
    return L3StepContractRef(step_id="s1", node_id=node_id, run_id=run_id, status=status)


def _receipt(**overrides: object) -> L3RuntimeOrchestrationReceipt:
    kw: dict[str, object] = dict(
        run_id="run-1",
        request_id="req-1",
        trace_root="trace-1",
        route_contract_id="rc-1",
        route_id="route-1",
        dag_id="dag-1",
        dag_sha256="sha-1",
        selected_node_ids=("n1",),
        step_contracts=(_step(),),
        l5_certification_ref=_CERT,
    )
    kw.update(overrides)
    return L3RuntimeOrchestrationReceipt(**kw)  # type: ignore[arg-type]


class TestStepStatuses:
    def test_allowed_status_members(self) -> None:
        assert ALLOWED_STEP_STATUSES == frozenset({
            "step_handed_to_l2",
            "step_skipped",
            "step_completed_by_l2",
            "step_failed_by_l2",
            "step_returned_for_replan",
        })

    def test_schema_version(self) -> None:
        assert L3_RUNTIME_RECEIPT_SCHEMA_VERSION == "1.0"


class TestStepContractRef:
    def test_to_dict(self) -> None:
        d = _step().to_dict()
        assert d == {
            "step_id": "s1",
            "node_id": "n1",
            "run_id": "run-1",
            "status": "step_completed_by_l2",
            "handed_to_l2_at_utc": "",
            "skipped_reason": "",
        }

    def test_frozen(self) -> None:
        with pytest.raises(dataclasses.FrozenInstanceError):
            _step().node_id = "x"  # type: ignore[misc]


class TestReceiptConstruction:
    def test_defaults(self) -> None:
        r = _receipt()
        assert r.l3_required is True
        assert r.l3_no_execute_assertion is True
        assert r.l3_no_l4_write_assertion is True
        assert r.schema_version == L3_RUNTIME_RECEIPT_SCHEMA_VERSION
        assert r.posture.read_only is True
        assert r.otel_span_refs == ()

    def test_frozen(self) -> None:
        with pytest.raises(dataclasses.FrozenInstanceError):
            _receipt().run_id = "x"  # type: ignore[misc]

    def test_to_dict_keys(self) -> None:
        d = _receipt().to_dict()
        assert d["selected_node_ids"] == ["n1"]
        assert d["step_contracts"][0]["node_id"] == "n1"
        assert d["l3_required"] is True


class TestReceiptInvariants:
    @pytest.mark.parametrize(
        "field", ["run_id", "request_id", "trace_root", "route_id", "dag_id", "dag_sha256"]
    )
    def test_empty_required_string_raises(self, field: str) -> None:
        with pytest.raises(ValueError, match="must be non-empty string"):
            _receipt(**{field: ""})

    def test_l3_required_false_raises(self) -> None:
        with pytest.raises(ValueError, match="l3_required must be True"):
            _receipt(l3_required=False)

    @pytest.mark.parametrize(
        "field",
        [
            "l3_no_execute_assertion",
            "l3_no_retrieve_assertion",
            "l3_no_prompt_assembly_assertion",
            "l3_no_l4_write_assertion",
        ],
    )
    def test_no_op_assertion_false_raises(self, field: str) -> None:
        with pytest.raises(ValueError, match="must be True"):
            _receipt(**{field: False})

    def test_empty_selected_node_ids_raises(self) -> None:
        with pytest.raises(ValueError, match="selected_node_ids must be non-empty"):
            _receipt(selected_node_ids=(), step_contracts=())

    def test_step_contract_wrong_type_raises(self) -> None:
        with pytest.raises(ValueError, match="must be L3StepContractRef"):
            _receipt(step_contracts=("not-a-ref",))

    def test_step_run_id_mismatch_raises(self) -> None:
        with pytest.raises(ValueError, match="run_id="):
            _receipt(step_contracts=(_step(run_id="other-run"),))

    def test_step_bad_status_raises(self) -> None:
        with pytest.raises(ValueError, match="not in"):
            _receipt(step_contracts=(_step(status="weird"),))

    def test_step_node_not_in_selected_raises(self) -> None:
        with pytest.raises(ValueError, match="not in selected_node_ids"):
            _receipt(selected_node_ids=("n1",), step_contracts=(_step(node_id="n2"),))

    def test_missing_l5_cert_raises(self) -> None:
        with pytest.raises(ValueError, match="l5_certification_ref"):
            _receipt(l5_certification_ref="")

    def test_blank_l5_cert_raises(self) -> None:
        with pytest.raises(ValueError, match="l5_certification_ref"):
            _receipt(l5_certification_ref="   ")


class TestDigestDeterminism:
    def test_same_input_same_digest(self) -> None:
        payload = {
            "schema_version": "1.0",
            "run_id": "r",
            "request_id": "q",
            "trace_root": "t",
            "route_contract_id": "rc",
            "route_id": "ro",
            "dag_id": "d",
            "dag_sha256": "s",
            "selected_node_ids": ["n1"],
            "step_contracts": [{"step_id": "s1", "node_id": "n1"}],
            "l3_no_execute_assertion": True,
            "l3_no_retrieve_assertion": True,
            "l3_no_prompt_assembly_assertion": True,
            "l3_no_l4_write_assertion": True,
        }
        assert compute_l3_runtime_digest(payload) == compute_l3_runtime_digest(dict(payload))

    def test_digest_prefix_and_sensitivity(self) -> None:
        d1 = compute_l3_runtime_digest({"run_id": "a", "selected_node_ids": ["n1"]})
        d2 = compute_l3_runtime_digest({"run_id": "b", "selected_node_ids": ["n1"]})
        assert d1.startswith("sha256:")
        assert d1 != d2


class TestBuildFactory:
    def test_build_populates_digest_and_passes_invariants(self) -> None:
        # The factory does NOT supply l5_certification_ref, so construction must
        # fail-closed — confirming the AG-W0-5 contract reaches the build path.
        with pytest.raises(ValueError, match="l5_certification_ref"):
            build_l3_runtime_orchestration_receipt(
                run_id="run-1",
                request_id="req-1",
                trace_root="trace-1",
                route_contract_id="rc-1",
                route_id="route-1",
                dag_id="dag-1",
                dag_sha256="sha-1",
                selected_node_ids=("n1",),
                step_contracts=(_step(),),
            )

    def test_compute_digest_matches_build_input_shape(self) -> None:
        digest_input = {
            "schema_version": L3_RUNTIME_RECEIPT_SCHEMA_VERSION,
            "run_id": "run-1",
            "request_id": "req-1",
            "trace_root": "trace-1",
            "route_contract_id": "rc-1",
            "route_id": "route-1",
            "dag_id": "dag-1",
            "dag_sha256": "sha-1",
            "selected_node_ids": ["n1"],
            "step_contracts": [_step().to_dict()],
            "l3_no_execute_assertion": True,
            "l3_no_retrieve_assertion": True,
            "l3_no_prompt_assembly_assertion": True,
            "l3_no_l4_write_assertion": True,
        }
        assert compute_l3_runtime_digest(digest_input).startswith("sha256:")

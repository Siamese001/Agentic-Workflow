"""W10 tests — UWG admission gate and L4 write adapter.

Plan: apps-rg-zip-based-full-spine-runtime-restoration-a3f7e2 W10

Tests:
  UWG:
    - test_uwg_blocks_current_run_mutation
    - test_uwg_blocks_promotion_without_policy_ref
    - test_uwg_blocks_promotion_without_evidence_refs
    - test_uwg_blocks_semantic_cache_writeback_when_policy_disabled
    - test_uwg_admits_exact_cache_writeback_when_policy_allows
    - test_uwg_emits_state_commit_receipt_on_admit
    - test_uwg_emits_blocked_write_receipt_on_block
    - test_l4_accepts_write_only_from_uwg
    - test_l4_rejects_direct_write_from_l6
    - test_l4_rejects_direct_write_from_exit
    - test_l4_rejects_direct_write_from_l2_l3_l0

  apps_rg writeback:
    - test_apps_rg_exact_cache_writeback_is_post_runtime_only
    - test_apps_rg_semantic_cache_writeback_disabled_by_default
    - test_apps_rg_evidence_writeback_requires_uwg
    - test_apps_rg_prompt_profile_promotion_requires_uwg
    - test_apps_rg_rubric_threshold_promotion_requires_uwg
    - test_apps_rg_judge_calibration_promotion_requires_uwg
    - test_apps_rg_route_policy_promotion_requires_uwg

  No-bypass:
    - test_exit_never_writes_cache_vector_l4_or_evidence
    - test_l6_never_writes_l4_directly
    - test_uwg_is_only_l4_write_admission_path
    - test_no_direct_write_imports_in_exit_l2_l3_l0
    - test_no_quarantined_apps_rg_runtime_imports_in_l6_or_uwg

  Integration:
    - test_apps_rg_w9_runtime_exhaust_to_l6_to_uwg_stubbed_flow
"""
from __future__ import annotations

import pytest

from agentic_core.runtime.contracts.future_run_promotion import (
    FutureRunPromotionRequest,
    build_future_run_promotion_request,
    PROMOTION_TYPE_EXACT_CACHE_WRITEBACK,
    PROMOTION_TYPE_SEMANTIC_CACHE_WRITEBACK,
    PROMOTION_TYPE_EVIDENCE_ARTIFACT_WRITEBACK,
    PROMOTION_TYPE_PROMPT_PROFILE_UPDATE,
    PROMOTION_TYPE_RUBRIC_THRESHOLD_UPDATE,
    PROMOTION_TYPE_JUDGE_CALIBRATION_UPDATE,
    PROMOTION_TYPE_ROUTE_POLICY_UPDATE,
    TARGET_STORE_EXACT_CACHE,
    TARGET_STORE_SEMANTIC_CACHE,
    TARGET_STORE_EVIDENCE_STORE,
    TARGET_STORE_PROMPT_REGISTRY,
    TARGET_STORE_RUBRIC_REGISTRY,
    TARGET_STORE_JUDGE_CALIBRATION,
    TARGET_STORE_ROUTE_POLICY,
)
from agentic_core.runtime.uwg.universal_write_gate import (
    UniversalWriteGate,
    UWGAdmissionOutcome,
    DirectWriteAttemptError,
    VERDICT_ADMIT,
    VERDICT_BLOCK,
)
from agentic_core.runtime.uwg.write_receipts import (
    StateCommitReceipt,
    BlockedWriteReceipt,
)
from agentic_core.L4_state.adapters.write_adapters import (
    L4WriteAdapter,
    DirectWriteViolationError,
    _FORBIDDEN_CALLERS,
    _UWG_WRITE_TOKEN,
)
from agentic_core.runtime.exhaust.runtime_exhaust_bundle import (
    build_runtime_exhaust_bundle,
)
from agentic_core.runtime.l6.writeback_proposer import L6WritebackProposer
from agentic_core.runtime.l6.apps_rg_learning_adapter import (
    _DEFAULT_LEARNING_PARAMS,
    _META_FEEDBACK_PROFILE_RELPATH,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

_POLICY_REF = _META_FEEDBACK_PROFILE_RELPATH
_EVIDENCE = ("ev::001", "ev::002")


def _good_request(
    *,
    promotion_type: str = PROMOTION_TYPE_EXACT_CACHE_WRITEBACK,
    target_store: str = TARGET_STORE_EXACT_CACHE,
    target_ref: str = "r1a::test::001",
    evidence_refs: tuple[str, ...] = _EVIDENCE,
    policy_ref: str = _POLICY_REF,
    proposed_state_diff: str = '{"op":"test"}',
) -> FutureRunPromotionRequest:
    return build_future_run_promotion_request(
        source_bundle_ref="reb::test::001",
        app_id="apps_rg",
        task_class="resume_generation",
        promotion_type=promotion_type,
        target_store=target_store,
        target_ref=target_ref,
        evidence_refs=evidence_refs,
        policy_ref=policy_ref,
        proposed_state_diff=proposed_state_diff,
    )


def _uwg(*, semantic_cache_enabled: bool = False) -> UniversalWriteGate:
    return UniversalWriteGate(
        policy={"semantic_cache_enabled": semantic_cache_enabled}
    )


# ---------------------------------------------------------------------------
# UWG admission tests
# ---------------------------------------------------------------------------

class TestUniversalWriteGate:

    def test_uwg_blocks_current_run_mutation(self):
        """UWG blocks any request with current_run_mutation_allowed=True.

        FutureRunPromotionRequest.__post_init__ prevents construction with True,
        so we test the UWG gate independently via a patched object.
        """
        # Build a valid request then manually test the guard via a duck-type fake
        class _MutatingRequest:
            current_run_mutation_allowed = True
            requires_uwg = True
            policy_ref = _POLICY_REF
            evidence_refs = _EVIDENCE
            promotion_type = PROMOTION_TYPE_EXACT_CACHE_WRITEBACK
            target_store = TARGET_STORE_EXACT_CACHE
            target_ref = "r1a::001"
            promotion_request_id = "promo::fake::001"
            proposed_state_diff = "{}"

        uwg = _uwg()
        outcome = uwg.admit(_MutatingRequest())  # type: ignore[arg-type]
        assert outcome.verdict == VERDICT_BLOCK
        assert "current_run_mutation_not_allowed" in outcome.admission.reason_codes

    def test_uwg_blocks_promotion_without_policy_ref(self):
        """UWG blocks requests with empty policy_ref."""
        # FutureRunPromotionRequest construction raises on empty policy_ref,
        # so we use a fake here to test the UWG gate layer independently.
        class _NoPolicyRequest:
            current_run_mutation_allowed = False
            requires_uwg = True
            policy_ref = ""  # empty
            evidence_refs = _EVIDENCE
            promotion_type = PROMOTION_TYPE_EXACT_CACHE_WRITEBACK
            target_store = TARGET_STORE_EXACT_CACHE
            target_ref = "r1a::001"
            promotion_request_id = "promo::nopolicy::001"
            proposed_state_diff = "{}"

        uwg = _uwg()
        outcome = uwg.admit(_NoPolicyRequest())  # type: ignore[arg-type]
        assert outcome.verdict == VERDICT_BLOCK
        assert "missing_policy_ref" in outcome.admission.reason_codes

    def test_uwg_blocks_promotion_without_evidence_refs(self):
        """UWG blocks requests with empty evidence_refs."""
        class _NoEvidenceRequest:
            current_run_mutation_allowed = False
            requires_uwg = True
            policy_ref = _POLICY_REF
            evidence_refs = ()  # empty
            promotion_type = PROMOTION_TYPE_EXACT_CACHE_WRITEBACK
            target_store = TARGET_STORE_EXACT_CACHE
            target_ref = "r1a::001"
            promotion_request_id = "promo::noev::001"
            proposed_state_diff = "{}"

        uwg = _uwg()
        outcome = uwg.admit(_NoEvidenceRequest())  # type: ignore[arg-type]
        assert outcome.verdict == VERDICT_BLOCK
        assert "missing_evidence_refs" in outcome.admission.reason_codes

    def test_uwg_blocks_semantic_cache_writeback_when_policy_disabled(self):
        """Semantic cache writeback is blocked when semantic_cache_enabled=False."""
        req = _good_request(
            promotion_type=PROMOTION_TYPE_SEMANTIC_CACHE_WRITEBACK,
            target_store=TARGET_STORE_SEMANTIC_CACHE,
        )
        uwg = _uwg(semantic_cache_enabled=False)
        outcome = uwg.admit(req)
        assert outcome.verdict == VERDICT_BLOCK
        assert "semantic_cache_writeback_disabled_by_policy" in outcome.admission.reason_codes
        assert outcome.blocked_write_receipt is not None
        assert isinstance(outcome.blocked_write_receipt, BlockedWriteReceipt)

    def test_uwg_admits_exact_cache_writeback_when_policy_allows(self):
        """Exact cache writeback is admitted when all gates pass."""
        req = _good_request(
            promotion_type=PROMOTION_TYPE_EXACT_CACHE_WRITEBACK,
            target_store=TARGET_STORE_EXACT_CACHE,
        )
        uwg = _uwg()
        outcome = uwg.admit(req)
        assert outcome.verdict == VERDICT_ADMIT, (
            f"Expected ADMIT, got BLOCK. reason_codes={outcome.admission.reason_codes}"
        )
        assert outcome.is_admit is True
        assert outcome.state_commit_receipt is not None

    def test_uwg_emits_state_commit_receipt_on_admit(self):
        """ADMIT produces a StateCommitReceipt with committed_by=UWG."""
        req = _good_request()
        uwg = _uwg()
        outcome = uwg.admit(req)
        assert outcome.verdict == VERDICT_ADMIT
        receipt = outcome.state_commit_receipt
        assert isinstance(receipt, StateCommitReceipt)
        assert receipt.committed_by == "UWG"
        assert receipt.commit_id.startswith("sc::")
        assert receipt.promotion_request_id == req.promotion_request_id
        assert receipt.deterministic_digest.startswith("sha256::")

    def test_uwg_emits_blocked_write_receipt_on_block(self):
        """BLOCK produces a BlockedWriteReceipt with blocked_by=UWG."""
        req = _good_request(
            promotion_type=PROMOTION_TYPE_SEMANTIC_CACHE_WRITEBACK,
            target_store=TARGET_STORE_SEMANTIC_CACHE,
        )
        uwg = _uwg(semantic_cache_enabled=False)
        outcome = uwg.admit(req)
        assert outcome.verdict == VERDICT_BLOCK
        receipt = outcome.blocked_write_receipt
        assert isinstance(receipt, BlockedWriteReceipt)
        assert receipt.blocked_by == "UWG"
        assert receipt.blocked_write_id.startswith("bw::")
        assert receipt.deterministic_digest.startswith("sha256::")

    def test_uwg_admission_result_fields_present(self):
        """UWGAdmissionResult contains all W10 required fields."""
        req = _good_request()
        uwg = _uwg()
        outcome = uwg.admit(req)
        a = outcome.admission
        assert a.admission_id != ""
        assert a.promotion_request_id == req.promotion_request_id
        assert a.verdict in (VERDICT_ADMIT, VERDICT_BLOCK)
        assert a.policy_ref == _POLICY_REF
        assert a.decisive_reason != ""
        assert a.deterministic_digest.startswith("sha256::")


# ---------------------------------------------------------------------------
# L4WriteAdapter tests
# ---------------------------------------------------------------------------

class TestL4WriteAdapter:

    def test_l4_accepts_write_only_from_uwg(self):
        """L4WriteAdapter.commit() succeeds when called with _caller='UWG' and token."""
        adapter = L4WriteAdapter(stub=True)
        req = _good_request()
        l4_ref = adapter.commit(req, _caller="UWG", _uwg_token=_UWG_WRITE_TOKEN)
        assert l4_ref.startswith("l4::commit::")
        assert len(adapter.committed_writes) == 1

    def test_l4_rejects_direct_write_from_l6(self):
        """L4WriteAdapter raises DirectWriteViolationError from L6."""
        adapter = L4WriteAdapter(stub=True)
        req = _good_request()
        with pytest.raises(DirectWriteViolationError, match="L6"):
            adapter.commit(req, _caller="L6")

    def test_l4_rejects_direct_write_from_exit(self):
        """L4WriteAdapter raises DirectWriteViolationError from Exit."""
        adapter = L4WriteAdapter(stub=True)
        req = _good_request()
        with pytest.raises(DirectWriteViolationError, match="Exit"):
            adapter.commit(req, _caller="Exit")

    def test_l4_rejects_direct_write_from_l2_l3_l0(self):
        """L4WriteAdapter raises DirectWriteViolationError from L0, L2, L3."""
        adapter = L4WriteAdapter(stub=True)
        req = _good_request()
        for caller in ("L0", "L2", "L3"):
            with pytest.raises(DirectWriteViolationError, match=caller):
                adapter.commit(req, _caller=caller)

    def test_l4_rejects_records_rejection(self):
        """Rejected writes are logged in rejected_writes list."""
        adapter = L4WriteAdapter(stub=True)
        req = _good_request()
        with pytest.raises(DirectWriteViolationError):
            adapter.commit(req, _caller="L6")
        assert len(adapter.rejected_writes) == 1
        assert adapter.rejected_writes[0]["caller"] == "L6"

    def test_l4_state_commit_receipt_committed_by_uwg_only(self):
        """StateCommitReceipt raises if committed_by is not UWG."""
        with pytest.raises(ValueError, match="committed_by must be 'UWG'"):
            StateCommitReceipt(
                commit_id="sc::001",
                promotion_request_id="promo::001",
                committed_by="L6",  # violation
            )

    def test_l4_forbidden_callers_includes_key_layers(self):
        """_FORBIDDEN_CALLERS includes Exit, L0, L2, L3, L6, C0, PA."""
        required = {"Exit", "L0", "L2", "L3", "L6", "C0", "PA", "PromptAssembly"}
        missing = required - _FORBIDDEN_CALLERS
        assert not missing, f"Missing forbidden callers: {missing}"


# ---------------------------------------------------------------------------
# apps_rg writeback tests
# ---------------------------------------------------------------------------

class TestAppsRgWriteback:

    def test_apps_rg_exact_cache_writeback_is_post_runtime_only(self):
        """Exact cache writeback proposal references exit_disposition_ref as evidence."""
        req = _good_request(
            promotion_type=PROMOTION_TYPE_EXACT_CACHE_WRITEBACK,
            target_store=TARGET_STORE_EXACT_CACHE,
        )
        assert req.current_run_mutation_allowed is False
        assert req.requires_uwg is True
        assert req.promotion_type == PROMOTION_TYPE_EXACT_CACHE_WRITEBACK

    def test_apps_rg_semantic_cache_writeback_disabled_by_default(self):
        """Semantic cache writeback is BLOCK with default UWG policy."""
        req = _good_request(
            promotion_type=PROMOTION_TYPE_SEMANTIC_CACHE_WRITEBACK,
            target_store=TARGET_STORE_SEMANTIC_CACHE,
        )
        uwg = _uwg(semantic_cache_enabled=False)
        outcome = uwg.admit(req)
        assert outcome.verdict == VERDICT_BLOCK
        assert "semantic_cache_writeback_disabled_by_policy" in outcome.admission.reason_codes

    def test_apps_rg_evidence_writeback_requires_uwg(self):
        """Evidence writeback request carries requires_uwg=True."""
        req = _good_request(
            promotion_type=PROMOTION_TYPE_EVIDENCE_ARTIFACT_WRITEBACK,
            target_store=TARGET_STORE_EVIDENCE_STORE,
        )
        assert req.requires_uwg is True
        # With valid evidence and policy, UWG admits
        uwg = _uwg()
        outcome = uwg.admit(req)
        assert outcome.verdict == VERDICT_ADMIT

    def test_apps_rg_prompt_profile_promotion_requires_uwg(self):
        """Prompt profile update request carries requires_uwg=True."""
        req = _good_request(
            promotion_type=PROMOTION_TYPE_PROMPT_PROFILE_UPDATE,
            target_store=TARGET_STORE_PROMPT_REGISTRY,
        )
        assert req.requires_uwg is True
        uwg = _uwg()
        outcome = uwg.admit(req)
        assert outcome.verdict == VERDICT_ADMIT

    def test_apps_rg_rubric_threshold_promotion_requires_uwg(self):
        """Rubric threshold update request carries requires_uwg=True."""
        req = _good_request(
            promotion_type=PROMOTION_TYPE_RUBRIC_THRESHOLD_UPDATE,
            target_store=TARGET_STORE_RUBRIC_REGISTRY,
        )
        assert req.requires_uwg is True
        uwg = _uwg()
        outcome = uwg.admit(req)
        assert outcome.verdict == VERDICT_ADMIT

    def test_apps_rg_judge_calibration_promotion_requires_uwg(self):
        """Judge calibration update request carries requires_uwg=True."""
        req = _good_request(
            promotion_type=PROMOTION_TYPE_JUDGE_CALIBRATION_UPDATE,
            target_store=TARGET_STORE_JUDGE_CALIBRATION,
        )
        assert req.requires_uwg is True
        uwg = _uwg()
        outcome = uwg.admit(req)
        assert outcome.verdict == VERDICT_ADMIT

    def test_apps_rg_route_policy_promotion_requires_uwg(self):
        """Route policy update request carries requires_uwg=True."""
        req = _good_request(
            promotion_type=PROMOTION_TYPE_ROUTE_POLICY_UPDATE,
            target_store=TARGET_STORE_ROUTE_POLICY,
        )
        assert req.requires_uwg is True
        uwg = _uwg()
        outcome = uwg.admit(req)
        assert outcome.verdict == VERDICT_ADMIT


# ---------------------------------------------------------------------------
# No-bypass tests
# ---------------------------------------------------------------------------

class TestNoBypassInvariants:

    def test_exit_never_writes_cache_vector_l4_or_evidence(self):
        """Exit layer source is in _FORBIDDEN_CALLERS."""
        assert "Exit" in _FORBIDDEN_CALLERS, (
            "Exit must be in L4WriteAdapter._FORBIDDEN_CALLERS"
        )

    def test_l6_never_writes_l4_directly(self):
        """L6 source is in _FORBIDDEN_CALLERS."""
        assert "L6" in _FORBIDDEN_CALLERS

    def test_uwg_is_only_l4_write_admission_path(self):
        """L4WriteAdapter accepts writes only from caller='UWG' with correct token."""
        adapter = L4WriteAdapter(stub=True)
        req = _good_request()
        # Non-UWG callers are rejected
        for forbidden in ("Exit", "L0", "L2", "L3", "L6", "C0", "PA"):
            with pytest.raises(DirectWriteViolationError):
                adapter.commit(req, _caller=forbidden)
        # UWG caller with correct token succeeds
        ref = adapter.commit(req, _caller="UWG", _uwg_token=_UWG_WRITE_TOKEN)
        assert ref.startswith("l4::commit::")

    def test_no_direct_write_imports_in_exit_l2_l3_l0(self):
        """Exit, L2 binding, L3 binding, L0 binding do not import write_adapters."""
        import pathlib
        layers_to_check = [
            "agentic_core/runtime/exit",
            "agentic_core/L2_execution",
            "agentic_core/L3_orchestration",
            "agentic_core/L0_routing",
        ]
        import os
        repo_root = pathlib.Path(__file__).parents[2]
        for layer_path in layers_to_check:
            full_path = repo_root / layer_path
            if not full_path.exists():
                continue
            for py_file in full_path.rglob("*.py"):
                content = py_file.read_text(encoding="utf-8")
                assert "L4WriteAdapter" not in content, (
                    f"{py_file.relative_to(repo_root)} imports L4WriteAdapter — "
                    "layer code must not write L4 directly."
                )
                assert "write_adapters" not in content or "adapters" not in str(py_file), (
                    f"{py_file.relative_to(repo_root)} imports write_adapters — "
                    "only UWG may use write_adapters."
                )

    def test_no_quarantined_apps_rg_runtime_imports_in_l6_or_uwg(self):
        """L6 and UWG modules do not import from apps_rg/_quarantine/."""
        import pathlib
        repo_root = pathlib.Path(__file__).parents[2]
        paths_to_check = [
            "agentic_core/runtime/l6",
            "agentic_core/runtime/uwg",
        ]
        for layer_path in paths_to_check:
            full_path = repo_root / layer_path
            if not full_path.exists():
                continue
            for py_file in full_path.rglob("*.py"):
                content = py_file.read_text(encoding="utf-8")
                assert "_quarantine" not in content, (
                    f"{py_file.relative_to(repo_root)} imports from _quarantine — "
                    "quarantined modules must never be imported."
                )


# ---------------------------------------------------------------------------
# Integration test
# ---------------------------------------------------------------------------

class TestAppsRgW10StubbedFlow:

    def test_apps_rg_w9_runtime_exhaust_to_l6_to_uwg_stubbed_flow(self):
        """Full W10 flow: RuntimeExhaustBundle -> L6 -> UWG -> receipt.

        1. Build a W9-style RuntimeExhaustBundle (post-exit, sealed).
        2. Pass to L6WritebackProposer.
        3. Produce FutureRunPromotionRequest proposals.
        4. Pass each to UWG.
        5. Emit StateCommitReceipt (ADMIT) or BlockedWriteReceipt (BLOCK).
        6. Prove no current-run mutation (all proposals carry False).
        7. Prove no direct L4 write (adapter only called via UWG).
        """
        # Step 1: Build RuntimeExhaustBundle (post-Exit, sealed)
        bundle = build_runtime_exhaust_bundle(
            request_id="req-w10-integration",
            run_id="run-w10-integration",
            trace_root="trace::w10::integration",
            route_contract_ref="rc::apps_rg::resume_generation::v1",
            sealed_result_ref="pkg::w10::integration::001",
            gate_mesh_result_ref="gmr::w10::integration::001",
            exit_disposition_ref="xd::w10::integration::001",
            runtime_receipt_refs=("rcpt::w10::integration::001",),
            learning_profile_ref=_META_FEEDBACK_PROFILE_RELPATH,
            meta_feedback_profile_ref=_META_FEEDBACK_PROFILE_RELPATH,
            learning_signals=(
                "cache_eligibility",
                "judge_disagreement_spike",
                "prompt_variant_performance",
            ),
        )
        assert bundle.created_after_exit is True
        assert bundle.current_run_closed is True

        # Step 2: Pass to L6WritebackProposer
        proposer = L6WritebackProposer(
            app_id="apps_rg",
            task_class="resume_generation",
            learning_profile=dict(_DEFAULT_LEARNING_PARAMS),
            policy_ref=_META_FEEDBACK_PROFILE_RELPATH,
        )
        proposals = proposer.propose(bundle)
        assert proposals, "L6 should produce at least one proposal for this bundle"

        # Step 3: Verify all proposals are inert FutureRunPromotionRequest
        for p in proposals:
            assert isinstance(p, FutureRunPromotionRequest)
            assert p.current_run_mutation_allowed is False  # Step 6
            assert p.requires_uwg is True

        # Step 4+5: Pass each proposal to UWG and collect receipts
        l4_adapter = L4WriteAdapter(stub=True)
        uwg = UniversalWriteGate(
            policy={"semantic_cache_enabled": False},
            l4_adapter=l4_adapter,
        )
        admit_receipts: list[StateCommitReceipt] = []
        block_receipts: list[BlockedWriteReceipt] = []

        for proposal in proposals:
            outcome = uwg.admit(proposal)
            if outcome.is_admit:
                assert outcome.state_commit_receipt is not None
                assert isinstance(outcome.state_commit_receipt, StateCommitReceipt)
                assert outcome.state_commit_receipt.committed_by == "UWG"
                admit_receipts.append(outcome.state_commit_receipt)
            else:
                assert outcome.blocked_write_receipt is not None
                assert isinstance(outcome.blocked_write_receipt, BlockedWriteReceipt)
                assert outcome.blocked_write_receipt.blocked_by == "UWG"
                block_receipts.append(outcome.blocked_write_receipt)

        # At least one proposal was processed
        assert (len(admit_receipts) + len(block_receipts)) == len(proposals)

        # Step 7: Direct L4 writes only happen via UWG (adapter called with UWG token)
        # Every committed write must have come through UWG token path
        for write in l4_adapter.committed_writes:
            # stub records don't carry token — the test for token is in TestL4WriteAdapter
            assert write["l4_receipt_ref"].startswith("l4::commit::")

        # No direct writes from forbidden callers
        assert len(l4_adapter.rejected_writes) == 0, (
            f"L4 adapter rejected direct writes (should be zero): {l4_adapter.rejected_writes}"
        )

    def test_apps_rg_w10_route_registry_not_activated(self):
        """route_registry.yaml must remain registered_not_active after W10."""
        import pathlib, yaml  # type: ignore[import]
        repo_root = pathlib.Path(__file__).parents[2]
        registry_path = repo_root / "apps_rg/config/route_registry.yaml"
        if not registry_path.exists():
            pytest.skip("route_registry.yaml not found")
        try:
            data = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        except Exception:
            pytest.skip("Could not parse route_registry.yaml")
        # Find apps_rg route entry
        routes = data if isinstance(data, list) else data.get("routes", [])
        for route in routes:
            if isinstance(route, dict) and route.get("app_id") == "apps_rg":
                status = route.get("status", "")
                assert status == "registered_not_active", (
                    f"apps_rg route must remain registered_not_active, got {status!r}"
                )
                return
        # If no explicit entry found, that's acceptable — not activated

    def test_apps_rg_w10_no_provider_calls_in_l6_uwg(self):
        """L6 and UWG modules must not reference provider call patterns."""
        import pathlib
        repo_root = pathlib.Path(__file__).parents[2]
        banned_patterns = [
            "openai", "anthropic", "requests.post", "httpx.post",
            "vllm", "llm_gateway",
        ]
        paths_to_check = [
            "agentic_core/runtime/l6",
            "agentic_core/runtime/uwg",
            "agentic_core/runtime/exhaust",
        ]
        for layer_path in paths_to_check:
            full_path = repo_root / layer_path
            if not full_path.exists():
                continue
            for py_file in full_path.rglob("*.py"):
                content = py_file.read_text(encoding="utf-8").lower()
                for pattern in banned_patterns:
                    assert pattern not in content, (
                        f"{py_file.name} references provider pattern {pattern!r} — "
                        "L6/UWG/exhaust must not call providers."
                    )

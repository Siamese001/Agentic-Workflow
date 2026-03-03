"""
Phase 9 — Wave 3 Tests: End-to-end gateway replay emission + static audit.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from agentic_core.L4_state.enforcement.replay_bundle_store import (
    ReplayBundleStore,
    ReplayVerificationError,
    ReplayVerifier,
    VerifiedReplay,
)
from agentic_core.L4_state.engines.replay_bundle_emitter import emit_replay_bundle
from agentic_core.L4_state.types.replay_bundle_types import ReplayBundle

pytestmark = pytest.mark.unit_min_deps

_MH = "m" * 64
_CONFIG = {"policy_hash": "ph1", "routing_hash": "rh1", "model_hash": "mh1", "budget_hash": "bh1"}

_EMITTER_MODULE = (
    Path(__file__).parent.parent.parent / "agentic_core" / "L4_state" / "engines" / "replay_bundle_emitter.py"
)

_STORE_MODULE = (
    Path(__file__).parent.parent.parent
    / "agentic_core"
    / "L4_state"
    / "enforcement"
    / "replay_bundle_store.py"
)


class TestCaseANoRetrievalNoTools:
    def test_bundle_emitted_no_retrieval_no_tools(self):
        """
        Case A: no retrieval, no tools -> bundle emitted, verifier passes.
        """
        store = ReplayBundleStore()
        bundle = emit_replay_bundle(
            mission_id="m1",
            execution_start_tick=5,
            execution_end_tick=10,
            manifest_hash=_MH,
            active_config_hashes=_CONFIG,
            store=store,
        )
        assert isinstance(bundle, ReplayBundle)
        assert len(bundle.replay_hash) == 64
        assert store.count() == 1

    def test_bundle_persisted_and_fetchable(self):
        store = ReplayBundleStore()
        bundle = emit_replay_bundle(
            mission_id="m1",
            execution_start_tick=5,
            execution_end_tick=10,
            manifest_hash=_MH,
            active_config_hashes=_CONFIG,
            store=store,
        )
        fetched = store.fetch_replay_bundle(bundle.replay_hash)
        assert fetched is bundle

    def test_verifier_passes_case_a(self):
        store = ReplayBundleStore()
        bundle = emit_replay_bundle(
            mission_id="m1",
            execution_start_tick=5,
            execution_end_tick=10,
            manifest_hash=_MH,
            active_config_hashes=_CONFIG,
            store=store,
        )
        verifier = ReplayVerifier()
        result = verifier.verify(bundle)
        assert isinstance(result, VerifiedReplay)
        assert "hash_integrity" in result.checks_passed

    def test_bundle_hash_stable_case_a(self):
        store1 = ReplayBundleStore()
        store2 = ReplayBundleStore()
        b1 = emit_replay_bundle(
            mission_id="m1",
            execution_start_tick=5,
            execution_end_tick=10,
            manifest_hash=_MH,
            active_config_hashes=_CONFIG,
            store=store1,
        )
        b2 = emit_replay_bundle(
            mission_id="m1",
            execution_start_tick=5,
            execution_end_tick=10,
            manifest_hash=_MH,
            active_config_hashes=_CONFIG,
            store=store2,
        )
        assert b1.replay_hash == b2.replay_hash

    def test_no_retrieval_citation_hash_empty(self):
        store = ReplayBundleStore()
        bundle = emit_replay_bundle(
            mission_id="m1",
            execution_start_tick=5,
            execution_end_tick=10,
            manifest_hash=_MH,
            active_config_hashes=_CONFIG,
            store=store,
        )
        assert bundle.citation_hash == ""
        assert bundle.retrieval_used is False


class TestCaseBRetrievalUsed:
    def test_bundle_emitted_with_retrieval(self):
        """
        Case B: retrieval used -> citation_hash present, verifier passes.
        """
        store = ReplayBundleStore()
        bundle = emit_replay_bundle(
            mission_id="m1",
            execution_start_tick=5,
            execution_end_tick=10,
            manifest_hash=_MH,
            active_config_hashes=_CONFIG,
            store=store,
            retrieval_used=True,
            citation_hash="c" * 64,
        )
        assert bundle.retrieval_used is True
        assert bundle.citation_hash == "c" * 64

    def test_verifier_passes_case_b(self):
        store = ReplayBundleStore()
        bundle = emit_replay_bundle(
            mission_id="m1",
            execution_start_tick=5,
            execution_end_tick=10,
            manifest_hash=_MH,
            active_config_hashes=_CONFIG,
            store=store,
            retrieval_used=True,
            citation_hash="c" * 64,
        )
        verifier = ReplayVerifier()
        result = verifier.verify(
            bundle,
            known_citation_hashes={"c" * 64},
        )
        assert isinstance(result, VerifiedReplay)
        assert "citation_hash_present" in result.checks_passed

    def test_citation_hash_in_canonical_bytes(self):
        store = ReplayBundleStore()
        bundle = emit_replay_bundle(
            mission_id="m1",
            execution_start_tick=5,
            execution_end_tick=10,
            manifest_hash=_MH,
            active_config_hashes=_CONFIG,
            store=store,
            retrieval_used=True,
            citation_hash="c" * 64,
        )
        assert b"citation_hash" in bundle.canonical_bytes()

    def test_bundle_with_prior_violations_and_tools(self):
        store = ReplayBundleStore()
        bundle = emit_replay_bundle(
            mission_id="m1",
            execution_start_tick=10,
            execution_end_tick=15,
            manifest_hash=_MH,
            active_config_hashes=_CONFIG,
            store=store,
            prior_detection_signal_hash="sh1",
            prior_violation_event_hashes=["vh1", "vh2"],
            tool_intent_hashes=["ih1"],
            tool_result_hashes=["rh1"],
        )
        assert "vh1" in bundle.prior_violation_event_hashes
        assert "ih1" in bundle.tool_intent_hashes
        assert "rh1" in bundle.tool_result_hashes

    def test_verifier_passes_with_all_registries(self):
        store = ReplayBundleStore()
        bundle = emit_replay_bundle(
            mission_id="m1",
            execution_start_tick=10,
            execution_end_tick=15,
            manifest_hash=_MH,
            active_config_hashes=_CONFIG,
            store=store,
            retrieval_used=True,
            citation_hash="c" * 64,
            prior_detection_signal_hash="sh1",
            prior_violation_event_hashes=["vh1"],
            tool_intent_hashes=["ih1"],
            tool_result_hashes=["rh1"],
        )
        verifier = ReplayVerifier()
        result = verifier.verify(
            bundle,
            known_citation_hashes={"c" * 64},
            known_signal_hashes={"sh1"},
            known_violation_hashes={"vh1"},
            known_intent_hashes={"ih1"},
            known_result_hashes={"rh1"},
            prior_signal_tick=9,
            prior_violation_ticks={"vh1": 9},
        )
        assert isinstance(result, VerifiedReplay)
        assert "hash_integrity" in result.checks_passed
        assert "signal_prior_only" in result.checks_passed
        assert "violations_prior_only" in result.checks_passed


class TestCaseCInjectSameCycleSignal:
    def test_verifier_fails_same_cycle_signal_deterministically(self):
        """
        Case C: inject same-cycle signal at execution_start_tick -> verifier fails.
        """
        store = ReplayBundleStore()
        bundle = emit_replay_bundle(
            mission_id="m1",
            execution_start_tick=10,
            execution_end_tick=15,
            manifest_hash=_MH,
            active_config_hashes=_CONFIG,
            store=store,
            prior_detection_signal_hash="sh1",
        )
        verifier = ReplayVerifier()
        with pytest.raises(ReplayVerificationError) as exc_info:
            verifier.verify(bundle, prior_signal_tick=10)  # same-cycle
        assert exc_info.value.code == "SAME_CYCLE_SIGNAL"

    def test_verifier_fails_same_cycle_violation_deterministically(self):
        store = ReplayBundleStore()
        bundle = emit_replay_bundle(
            mission_id="m1",
            execution_start_tick=10,
            execution_end_tick=15,
            manifest_hash=_MH,
            active_config_hashes=_CONFIG,
            store=store,
            prior_violation_event_hashes=["vh1"],
        )
        verifier = ReplayVerifier()
        with pytest.raises(ReplayVerificationError) as exc_info:
            verifier.verify(bundle, prior_violation_ticks={"vh1": 10})
        assert exc_info.value.code == "SAME_CYCLE_VIOLATION"

    def test_verifier_fails_tampered_hash_deterministically(self):
        store = ReplayBundleStore()
        bundle = emit_replay_bundle(
            mission_id="m1",
            execution_start_tick=5,
            execution_end_tick=10,
            manifest_hash=_MH,
            active_config_hashes=_CONFIG,
            store=store,
        )
        object.__setattr__(bundle, "replay_hash", "tampered" + "0" * 57)
        verifier = ReplayVerifier()
        with pytest.raises(ReplayVerificationError) as exc_info:
            verifier.verify(bundle)
        assert exc_info.value.code == "REPLAY_HASH_MISMATCH"


class TestStaticAuditNonMutatingEmitter:
    def test_emitter_module_exists(self):
        assert _EMITTER_MODULE.exists(), f"Not found: {_EMITTER_MODULE}"

    def test_store_module_exists(self):
        assert _STORE_MODULE.exists(), f"Not found: {_STORE_MODULE}"

    def test_emitter_contains_zero_upsert_calls(self):
        """
        Static AST audit: replay_bundle_emitter.py must contain zero
        upsert/setex calls (knowledge index mutation forbidden).
        """
        source = _EMITTER_MODULE.read_text(encoding="utf-8")
        tree = ast.parse(source)
        forbidden: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if node.func.attr in ("upsert", "setex", "set"):
                    forbidden.append(node.func.attr)
        assert forbidden == [], (
            f"replay_bundle_emitter.py contains knowledge-index mutation calls: {forbidden}"
        )

    def test_store_module_contains_zero_upsert_calls(self):
        """
        Static AST audit: replay_bundle_store.py must contain zero
        upsert/setex calls.
        """
        source = _STORE_MODULE.read_text(encoding="utf-8")
        tree = ast.parse(source)
        forbidden: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if node.func.attr in ("upsert", "setex"):
                    forbidden.append(node.func.attr)
        assert forbidden == [], f"replay_bundle_store.py contains knowledge-index mutation calls: {forbidden}"

    def test_emitter_imports_replay_bundle_store(self):
        source = _EMITTER_MODULE.read_text(encoding="utf-8")
        assert "ReplayBundleStore" in source

    def test_emitter_imports_build_replay_bundle(self):
        source = _EMITTER_MODULE.read_text(encoding="utf-8")
        assert "build_replay_bundle" in source

    def test_store_module_defines_verifier(self):
        source = _STORE_MODULE.read_text(encoding="utf-8")
        assert "ReplayVerifier" in source

    def test_store_module_defines_verification_error(self):
        source = _STORE_MODULE.read_text(encoding="utf-8")
        assert "ReplayVerificationError" in source

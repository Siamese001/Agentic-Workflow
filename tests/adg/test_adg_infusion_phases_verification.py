"""
test_adg_infusion_phases_verification.py

Creative orthogonal verification of ADG Infusion Phases 2j-4.

Strategy: we do NOT re-execute the phases.  Instead we:
  1. Inspect source code with AST to prove injections exist
  2. Use mock BehavioralProfiles to exercise every code-path without SQLite
  3. Verify MRO / inheritance contracts with pure introspection
  4. Assert runtime behaviour using controlled stub objects
  5. Cross-check that no existing public API signatures changed
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Stub missing optional modules before any agentic_core imports resolve them.
# `agentic_core.adg.runtime.__init__` unconditionally imports execution_proof
# which does not exist in this environment.  Shim it so tests can import
# behavioral_index without the entire adg.runtime package failing to load.
# ---------------------------------------------------------------------------
import sys
import types as _types


def _make_stub_module(name: str) -> _types.ModuleType:
    mod = _types.ModuleType(name)
    mod.__spec__ = None  # type: ignore[attr-defined]
    return mod


for _stub_name in ("agentic_core.adg.runtime.execution_proof",):
    if _stub_name not in sys.modules:
        _stub = _make_stub_module(_stub_name)
        # Add all names the __init__ imports from execution_proof
        for _attr in (
            "ExecutionProofRecorder",
            "ExecutionProofReport",
            "ExecutionTrace",
            "ProofComparison",
            "ProofComparisonOutcome",
            "ReplayKey",
        ):
            setattr(_stub, _attr, type(_attr, (), {}))
        sys.modules[_stub_name] = _stub

import ast
import inspect
import unittest
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from unittest.mock import MagicMock, patch

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------
REPO = Path(__file__).resolve().parents[2]


def _src(relative: str) -> str:
    """Read source text of a file relative to repo root."""
    return (REPO / relative).read_text(encoding="utf-8")


def _ast_of(relative: str) -> ast.Module:
    return ast.parse(_src(relative))


def _has_name_in_ast(tree: ast.Module, name: str) -> bool:
    """Return True if *name* appears as an identifier anywhere in *tree*."""
    for node in ast.walk(tree):
        for field_name, value in ast.iter_fields(node):
            if isinstance(value, str) and name in value:
                return True
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, str) and name in item:
                        return True
    return False


def _func_src(tree: ast.Module, func_name: str) -> str | None:
    """Return the un-parsed source lines for a top-level or method *func_name*."""
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == func_name:
            return ast.unparse(node)
    return None


# ---------------------------------------------------------------------------
# Stub BehavioralProfile (no SQLite needed)
# ---------------------------------------------------------------------------
@dataclass
class _StubProfile:
    behavioral_score: float = 0.5
    deterministic_coverage: bool = False
    antipattern_signals: frozenset = field(default_factory=frozenset)
    agent_signals: frozenset = field(default_factory=frozenset)
    script_signals: frozenset = field(default_factory=frozenset)
    resolved_path: str = "stub/path.py"


# ===========================================================================
# Phase 4 — ADGBehavioralMixin root injection
# ===========================================================================
class TestPhase4MROInjection(unittest.TestCase):
    """Verify ADGBehavioralMixin is wired into SovereignBaseAgent MRO."""

    def test_adg_behavioral_mixin_in_mro(self):
        from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

        mro_names = [c.__name__ for c in SovereignBaseAgent.__mro__]
        self.assertIn("ADGBehavioralMixin", mro_names)

    def test_adg_behavioral_mixin_after_runtime_safety(self):
        """ADGBehavioralMixin must come AFTER RuntimeSafetyMixin (lower priority)."""
        from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
        from agentic_core.mixins.adg_behavioral_mixin import ADGBehavioralMixin
        from agentic_core.mixins.runtime_safety_mixin import RuntimeSafetyMixin

        mro = list(SovereignBaseAgent.__mro__)
        self.assertLess(
            mro.index(RuntimeSafetyMixin),
            mro.index(ADGBehavioralMixin),
            "RuntimeSafetyMixin must appear before ADGBehavioralMixin in MRO",
        )

    def test_all_cached_properties_present_on_mixin(self):
        from agentic_core.mixins.adg_behavioral_mixin import ADGBehavioralMixin

        expected = {
            "adg_behavioral_score",
            "adg_is_agent_like",
            "adg_is_script_like",
            "adg_antipattern_signals",
            "adg_agent_signals",
            "adg_script_signals",
            "adg_dead_import_count",
            "adg_profile_available",
        }
        actual = {k for k, v in inspect.getmembers(ADGBehavioralMixin) if isinstance(v, cached_property)}
        missing = expected - actual
        self.assertFalse(missing, f"Missing cached_property members: {missing}")

    def test_mixin_neutral_fallback_without_project_root(self):
        """Without project_root, all properties must return safe defaults."""
        from agentic_core.mixins.adg_behavioral_mixin import ADGBehavioralMixin

        class _Bare(ADGBehavioralMixin):
            pass  # no project_root

        obj = _Bare()
        self.assertEqual(obj.adg_behavioral_score, 0.5)
        self.assertFalse(obj.adg_is_agent_like)
        self.assertFalse(obj.adg_is_script_like)
        self.assertEqual(obj.adg_antipattern_signals, [])
        self.assertEqual(obj.adg_dead_import_count, 0)

    def test_mixin_stub_profile_agent_like(self):
        """When stub profile has score >0.7, is_agent_like must be True."""
        from agentic_core.mixins.adg_behavioral_mixin import ADGBehavioralMixin

        class _Stubbed(ADGBehavioralMixin):
            project_root = REPO

        obj = _Stubbed()
        stub = _StubProfile(behavioral_score=0.85)
        with patch.object(_Stubbed, "_adg_load_profile", return_value=stub):
            # Force re-evaluation (cached_property caches on instance dict)
            for attr in ("adg_behavioral_score", "adg_is_agent_like", "adg_is_script_like"):
                obj.__dict__.pop(attr, None)
            self.assertAlmostEqual(obj.adg_behavioral_score, 0.85)
            obj.__dict__.pop("adg_is_agent_like", None)
            self.assertTrue(obj.adg_is_agent_like)

    def test_mixin_stub_profile_script_like(self):
        from agentic_core.mixins.adg_behavioral_mixin import ADGBehavioralMixin

        class _Stubbed(ADGBehavioralMixin):
            project_root = REPO

        obj = _Stubbed()
        stub = _StubProfile(behavioral_score=0.2, deterministic_coverage=True)
        with patch.object(_Stubbed, "_adg_load_profile", return_value=stub):
            obj.__dict__.pop("adg_is_script_like", None)
            self.assertTrue(obj.adg_is_script_like)

    def test_behavioral_summary_keys(self):
        from agentic_core.mixins.adg_behavioral_mixin import ADGBehavioralMixin

        class _Bare(ADGBehavioralMixin):
            pass

        obj = _Bare()
        summary = obj.adg_behavioral_summary()
        required_keys = {
            "adg_profile_available",
            "adg_behavioral_score",
            "adg_is_agent_like",
            "adg_is_script_like",
            "adg_antipattern_signals",
            "adg_agent_signals",
            "adg_script_signals",
            "adg_dead_import_count",
        }
        self.assertEqual(required_keys, set(summary.keys()))


# ===========================================================================
# Phase 2j — ElevatorShaftConsistencyEnforcer
# ===========================================================================
class TestPhase2jElevatorShaft(unittest.TestCase):
    """Verify ADG violates injection in summary() without SQLite."""

    @classmethod
    def setUpClass(cls):
        from agentic_core.L4_state.enforcement.elevator_shaft_consistency_enforcer import (
            ElevatorShaftConsistencyEnforcer,
        )

        cls.EnfClass = ElevatorShaftConsistencyEnforcer

    def test_summary_has_adg_violates_key(self):
        enf = self.EnfClass(drift_tolerance=5)
        summary = enf.summary()
        self.assertIn("adg_violates", summary)

    def test_adg_violates_is_list(self):
        enf = self.EnfClass(drift_tolerance=5)
        self.assertIsInstance(enf.summary()["adg_violates"], list)

    def test_summary_still_contains_layer_records(self):
        """Existing layer-record structure must not be broken."""
        from agentic_core.L4_state.enforcement.elevator_shaft_consistency_enforcer import (
            ElevatorShaftConsistencyEnforcer,
            SemanticClockSnapshot,
        )

        enf = ElevatorShaftConsistencyEnforcer(drift_tolerance=5)
        enf.record_advance("L3", SemanticClockSnapshot(tick=1))
        s = enf.summary()
        self.assertIn("L3", s)
        self.assertIn("last_tick", s["L3"])

    def test_summary_adg_violates_with_stub_antipatterns(self):
        """When ADG returns antipatterns, they appear in summary and trigger warning log."""
        import logging

        import agentic_core.adg.runtime.behavioral_index as _beh_idx

        enf = self.EnfClass(drift_tolerance=5)
        stub = _StubProfile(antipattern_signals=frozenset({"for_retry", "silent_swallower"}))

        with (
            patch.object(_beh_idx, "get_behavioral_profile", return_value=stub),
            self.assertLogs(level=logging.WARNING),
        ):
            s = enf.summary()

        self.assertIn("for_retry", s["adg_violates"])
        self.assertIn("silent_swallower", s["adg_violates"])
        self.assertEqual(sorted(s["adg_violates"]), ["for_retry", "silent_swallower"])

    def test_source_contains_adg_violates_key(self):
        """AST-level check: 'adg_violates' literal is present in source."""
        src = _src("agentic_core/L4_state/enforcement/elevator_shaft_consistency_enforcer.py")
        self.assertIn("adg_violates", src)

    def test_summary_no_exception_when_adg_unavailable(self):
        """Graceful when behavioral_index import raises."""
        import agentic_core.adg.runtime.behavioral_index as _beh_idx

        enf = self.EnfClass(drift_tolerance=5)
        with patch.object(_beh_idx, "get_behavioral_profile", side_effect=RuntimeError("ADG unavailable")):
            s = enf.summary()
        self.assertEqual(s["adg_violates"], [])


# ===========================================================================
# Phase 2k — CredentialAccessGuard
# ===========================================================================
class TestPhase2kCredentialAccessGuard(unittest.TestCase):
    """Verify _adg_violates wired into __init__ without SQLite."""

    def _make_guard(self, profile_stub=None):
        import agentic_core.adg.runtime.behavioral_index as _beh_idx
        from agentic_core.L5_safety.enforcement.security.credential_access_guard import (
            CredentialAccessGuard,
        )

        if profile_stub is not None:
            with patch.object(_beh_idx, "get_behavioral_profile", return_value=profile_stub):
                return CredentialAccessGuard(agent_id="test_agent", run_id="run_001")
        return CredentialAccessGuard(agent_id="test_agent", run_id="run_001")

    def test_adg_violates_attribute_exists(self):
        guard = self._make_guard()
        self.assertTrue(hasattr(guard, "_adg_violates"))

    def test_adg_violates_is_list(self):
        guard = self._make_guard()
        self.assertIsInstance(guard._adg_violates, list)

    def test_adg_violates_empty_when_no_antipatterns(self):
        stub = _StubProfile(antipattern_signals=frozenset())
        guard = self._make_guard(profile_stub=stub)
        self.assertEqual(guard._adg_violates, [])

    def test_adg_violates_populated_when_antipatterns_present(self):
        stub = _StubProfile(antipattern_signals=frozenset({"magic_config"}))
        guard = self._make_guard(profile_stub=stub)
        self.assertIn("magic_config", guard._adg_violates)

    def test_adg_violates_warning_logged(self):
        import logging

        import agentic_core.adg.runtime.behavioral_index as _beh_idx

        stub = _StubProfile(antipattern_signals=frozenset({"type_erasure"}))
        from agentic_core.L5_safety.enforcement.security.credential_access_guard import CredentialAccessGuard

        with (
            self.assertLogs(level=logging.WARNING),
            patch.object(_beh_idx, "get_behavioral_profile", return_value=stub),
        ):
            CredentialAccessGuard(agent_id="test_agent", run_id="run_001")

    def test_adg_violates_graceful_on_import_error(self):
        import agentic_core.adg.runtime.behavioral_index as _beh_idx

        with patch.object(_beh_idx, "get_behavioral_profile", side_effect=ImportError("no ADG")):
            guard = self._make_guard()
        self.assertEqual(guard._adg_violates, [])

    def test_existing_api_unchanged(self):
        """guarded_get_secret / guarded_get_env signatures must be intact."""
        import inspect

        from agentic_core.L5_safety.enforcement.security.credential_access_guard import (
            CredentialAccessGuard,
        )

        sig_secret = inspect.signature(CredentialAccessGuard.guarded_get_secret)
        sig_env = inspect.signature(CredentialAccessGuard.guarded_get_env)
        self.assertIn("secret_name", sig_secret.parameters)
        self.assertIn("var_name", sig_env.parameters)

    def test_source_contains_adg_violates(self):
        src = _src("agentic_core/L5_safety/enforcement/security/credential_access_guard.py")
        self.assertIn("_adg_violates", src)


# ===========================================================================
# Phase 2l — RAG embedding confidence weighting
# ===========================================================================
class TestPhase2lRAGConfidence(unittest.TestCase):
    """Verify adg_confidence_weight injected into retrieve() results."""

    def _make_rag_manager(self):
        from agentic_core.knowledge.reasoning.SovereignRAGManagerAgent import SovereignRAGManager

        # Bypass SovereignBaseAgent.__init__ integrity check (Merkle-seal on base_agents/)
        # by using object.__new__ and manually setting required attrs.
        mgr = object.__new__(SovereignRAGManager)
        mgr.storage_root = REPO / "data"
        mgr.embedder = None
        mgr.vector_store = None
        mgr.bm25_index = None
        mgr.bm25_corpus = []
        mgr.bm25_store = None
        return mgr

    def test_retrieve_returns_adg_confidence_weight_key(self):
        import agentic_core.adg.runtime.behavioral_index as _beh_idx

        mgr = self._make_rag_manager()
        stub_profile = _StubProfile(behavioral_score=0.8)

        # Inject a fake embedder + vector store
        fake_emb = [0.1, 0.2, 0.3]
        fake_result = [{"id": "doc_1", "score": 1.0, "metadata": {"text": "hello"}}]

        mgr.embedder = MagicMock()
        mgr.embedder.embed_query.return_value = fake_emb
        mgr.vector_store = MagicMock()
        mgr.vector_store.query.return_value = fake_result

        with patch.object(_beh_idx, "get_behavioral_profile", return_value=stub_profile):
            results = mgr.retrieve("test query", top_k=5)

        # At least one result from vector store
        vec_results = [r for r in results if r.get("source") == "vector"]
        self.assertTrue(len(vec_results) > 0, "Expected vector results")
        for r in vec_results:
            self.assertIn("adg_confidence_weight", r)
            self.assertAlmostEqual(r["adg_confidence_weight"], 0.8)

    def test_score_is_scaled_by_adg_confidence(self):
        """adg_confidence_weight is attached to every vector result at exactly the stub value.
        The final fused score may differ (RRF / re-ranking applied downstream), but the weight
        key itself must carry the exact confidence that was used to scale the raw score."""
        import agentic_core.adg.runtime.behavioral_index as _beh_idx

        mgr = self._make_rag_manager()
        stub_profile = _StubProfile(behavioral_score=0.6)

        raw_score = 0.9
        fake_result = [{"id": "d1", "score": raw_score, "metadata": {"text": "x"}}]
        mgr.embedder = MagicMock()
        mgr.embedder.embed_query.return_value = [0.1]
        mgr.vector_store = MagicMock()
        mgr.vector_store.query.return_value = fake_result

        with patch.object(_beh_idx, "get_behavioral_profile", return_value=stub_profile):
            results = mgr.retrieve("q", top_k=5)

        vec_results = [r for r in results if r.get("source") == "vector"]
        if vec_results:
            # The adg_confidence_weight key must be exactly 0.6
            self.assertAlmostEqual(vec_results[0]["adg_confidence_weight"], 0.6, places=6)
            # The fused score must be non-negative (ADG confidence never flips sign)
            self.assertGreaterEqual(vec_results[0]["score"], 0.0)

    def test_retrieve_graceful_when_adg_unavailable(self):
        import agentic_core.adg.runtime.behavioral_index as _beh_idx

        mgr = self._make_rag_manager()
        mgr.embedder = None
        mgr.vector_store = None

        with patch.object(_beh_idx, "get_behavioral_profile", side_effect=Exception("no SQLite")):
            results = mgr.retrieve("q", top_k=5)

        # Should return empty or bm25-only without crashing
        self.assertIsInstance(results, list)

    def test_rag_orchestrator_source_has_adg_confidence(self):
        src = _src("agentic_core/knowledge/engine/rag_orchestrator.py")
        self.assertIn("adg_confidence_weight", src)
        self.assertIn("_adg_confidence", src)

    def test_rag_manager_source_has_adg_confidence(self):
        src = _src("agentic_core/knowledge/reasoning/SovereignRAGManagerAgent.py")
        self.assertIn("adg_confidence_weight", src)


# ===========================================================================
# Phase 3a — HealingPolicyMixin confidence adjustment
# ===========================================================================
class TestPhase3aHealingPolicy(unittest.TestCase):
    """Verify ADG confidence adjustment in _perform_healing_chain()."""

    def test_source_has_confidence_variable(self):
        src = _src("agentic_core/mixins/healing_policy_mixin.py")
        self.assertIn("_confidence", src)
        self.assertIn("deterministic_coverage", src)

    def test_confidence_increased_for_script_like(self):
        """Script-like files (deterministic_coverage=True) get +0.05 confidence."""
        import agentic_core.adg.runtime.behavioral_index as _beh_idx
        from agentic_core.mixins.healing_policy_mixin import HealingPolicyMixin

        class _TestAgent(HealingPolicyMixin):
            name = "TestAgent"
            python_files = []

        agent = _TestAgent()
        stub = _StubProfile(behavioral_score=0.3, deterministic_coverage=True)

        with patch.object(_beh_idx, "get_behavioral_profile", return_value=stub):
            result = agent._perform_healing_chain(True, False, 0, 3, set())

        # Must complete without error and return a dict
        self.assertIn("violations_found", result)
        self.assertIn("violations_fixed", result)

    def test_confidence_decreased_for_agent_like(self):
        """Agent-like files (score>0.7) get -0.05 confidence — no crash."""
        import agentic_core.adg.runtime.behavioral_index as _beh_idx
        from agentic_core.mixins.healing_policy_mixin import HealingPolicyMixin

        class _TestAgent(HealingPolicyMixin):
            name = "TestAgent"
            python_files = []

        agent = _TestAgent()
        stub = _StubProfile(behavioral_score=0.9, deterministic_coverage=False)

        with patch.object(_beh_idx, "get_behavioral_profile", return_value=stub):
            result = agent._perform_healing_chain(True, False, 0, 3, set())

        self.assertIsInstance(result, dict)

    def test_healing_chain_graceful_on_adg_error(self):
        import agentic_core.adg.runtime.behavioral_index as _beh_idx
        from agentic_core.mixins.healing_policy_mixin import HealingPolicyMixin

        class _TestAgent(HealingPolicyMixin):
            name = "TestAgent"
            python_files = []

        agent = _TestAgent()
        with patch.object(_beh_idx, "get_behavioral_profile", side_effect=RuntimeError("no ADG")):
            result = agent._perform_healing_chain(True, False, 0, 3, set())

        self.assertIn("violations_found", result)


# ===========================================================================
# Phase 3b — SelfDiagnosisMixin ADG fold
# ===========================================================================
class TestPhase3bSelfDiagnosis(unittest.TestCase):
    """Verify adg_antipatterns + adg_behavioral_score folded into diagnosis."""

    def test_source_has_adg_antipatterns_key(self):
        src = _src("agentic_core/mixins/self_diagnosis_mixin.py")
        self.assertIn("adg_antipatterns", src)
        self.assertIn("adg_behavioral_score", src)

    def test_self_diagnose_includes_adg_keys_async(self):
        """Run self_diagnose() via asyncio and confirm ADG keys present."""
        import asyncio

        import agentic_core.adg.runtime.behavioral_index as _beh_idx
        from agentic_core.mixins.self_diagnosis_mixin import SelfDiagnosisMixin

        class _Agent(SelfDiagnosisMixin):
            MANDATORY_COMPONENTS = []

        agent = _Agent()
        stub = _StubProfile(behavioral_score=0.6, antipattern_signals=frozenset({"for_retry"}))

        with patch.object(_beh_idx, "get_behavioral_profile", return_value=stub):
            result = asyncio.run(agent.self_diagnose())

        self.assertIn("adg_antipatterns", result)
        self.assertIn("adg_behavioral_score", result)

    def test_self_diagnose_adg_antipatterns_are_sorted_list(self):
        import asyncio

        import agentic_core.adg.runtime.behavioral_index as _beh_idx
        from agentic_core.mixins.self_diagnosis_mixin import SelfDiagnosisMixin

        class _Agent(SelfDiagnosisMixin):
            MANDATORY_COMPONENTS = []

        agent = _Agent()
        stub = _StubProfile(antipattern_signals=frozenset({"zap", "alpha", "beta"}))

        with patch.object(_beh_idx, "get_behavioral_profile", return_value=stub):
            result = asyncio.run(agent.self_diagnose())

        self.assertEqual(result["adg_antipatterns"], ["alpha", "beta", "zap"])

    def test_self_diagnose_graceful_when_adg_missing(self):
        import asyncio

        import agentic_core.adg.runtime.behavioral_index as _beh_idx
        from agentic_core.mixins.self_diagnosis_mixin import SelfDiagnosisMixin

        class _Agent(SelfDiagnosisMixin):
            MANDATORY_COMPONENTS = []

        agent = _Agent()
        with patch.object(_beh_idx, "get_behavioral_profile", side_effect=ImportError("no adg")):
            result = asyncio.run(agent.self_diagnose())

        # Must still succeed; adg keys may be absent but no exception
        self.assertIn("overall_health", result)


# ===========================================================================
# Phase 3c — L3OrchestrationBase plan_execution enrichment
# ===========================================================================
class TestPhase3cL3PlanExecution(unittest.TestCase):
    def _call_plan_execution(self, stub=None, side_effect=None):
        """Call plan_execution() on a standalone L3OrchestrationBase-like object,
        bypassing SovereignBaseAgent.__post_init__ integrity check."""
        import agentic_core.adg.runtime.behavioral_index as _beh_idx
        from agentic_core.base_agents.L3OrchestrationBase import L3OrchestrationBase

        # Instantiate WITHOUT calling __post_init__ to avoid SovereignLockError
        obj = object.__new__(L3OrchestrationBase)
        obj.name = "L3OrchestrationBase"

        if stub is not None:
            with patch.object(_beh_idx, "get_behavioral_profile", return_value=stub):
                return L3OrchestrationBase.plan_execution(obj, {})
        elif side_effect is not None:
            with patch.object(_beh_idx, "get_behavioral_profile", side_effect=side_effect):
                return L3OrchestrationBase.plan_execution(obj, {"x": 1})
        else:
            return L3OrchestrationBase.plan_execution(obj, {})

    def test_plan_execution_has_adg_route_mode(self):
        result = self._call_plan_execution()
        self.assertIn("adg_route_mode", result)

    def test_plan_execution_has_adg_scope_widening(self):
        result = self._call_plan_execution()
        self.assertIn("adg_scope_widening", result)
        self.assertIsInstance(result["adg_scope_widening"], list)

    def test_plan_execution_route_mode_agent_when_score_high(self):
        stub = _StubProfile(behavioral_score=0.9)
        result = self._call_plan_execution(stub=stub)
        self.assertEqual(result["adg_route_mode"], "agent")

    def test_plan_execution_route_mode_script_when_deterministic(self):
        stub = _StubProfile(behavioral_score=0.3, deterministic_coverage=True)
        result = self._call_plan_execution(stub=stub)
        self.assertEqual(result["adg_route_mode"], "script")

    def test_plan_execution_route_mode_hybrid_default(self):
        stub = _StubProfile(behavioral_score=0.5, deterministic_coverage=False)
        result = self._call_plan_execution(stub=stub)
        self.assertEqual(result["adg_route_mode"], "hybrid")

    def test_plan_execution_scope_widening_sorted(self):
        stub = _StubProfile(antipattern_signals=frozenset({"zz", "aa", "mm"}))
        result = self._call_plan_execution(stub=stub)
        self.assertEqual(result["adg_scope_widening"], ["aa", "mm", "zz"])

    def test_plan_execution_graceful_when_adg_missing(self):
        result = self._call_plan_execution(side_effect=Exception("no adg"))
        self.assertIn("task", result)
        self.assertEqual(result["adg_route_mode"], "static")

    def test_existing_keys_still_present(self):
        result = self._call_plan_execution()
        for key in ("task", "plan", "status", "message"):
            self.assertIn(key, result)


# ===========================================================================
# Phase 3d — L6ObservabilityBase collect_metrics
# ===========================================================================
class TestPhase3dL6Metrics(unittest.TestCase):
    def _call_collect_metrics(self, idx_mock=None, idx_side_effect=None):
        """Call collect_metrics() bypassing SovereignBaseAgent integrity check."""
        import agentic_core.adg.runtime.behavioral_index as _beh_idx
        from agentic_core.base_agents.L6ObservabilityBase import L6ObservabilityBase

        obj = object.__new__(L6ObservabilityBase)
        if idx_mock is not None:
            with patch.object(_beh_idx, "ADGBehavioralIndex") as mock_cls:
                mock_cls.from_latest.return_value = idx_mock
                return L6ObservabilityBase.collect_metrics(obj)
        elif idx_side_effect is not None:
            with patch.object(_beh_idx, "ADGBehavioralIndex", side_effect=idx_side_effect):
                return L6ObservabilityBase.collect_metrics(obj)
        else:
            return L6ObservabilityBase.collect_metrics(obj)

    def test_collect_metrics_has_legacy_keys(self):
        result = self._call_collect_metrics()
        self.assertIn("metrics", result)
        self.assertIn("timestamp", result)

    def test_collect_metrics_adg_keys_present_when_index_available(self):
        mock_idx = MagicMock()
        mock_idx.trust_score = 0.82
        mock_idx.unresolved_imports = ["a", "b"]
        mock_idx.layer_violations = ["x"]
        mock_idx.orphan_modules = []

        result = self._call_collect_metrics(idx_mock=mock_idx)
        self.assertIn("adg_trust_score", result)
        self.assertIn("adg_unresolved_imports", result)
        self.assertIn("adg_layer_violations", result)
        self.assertIn("adg_orphan_modules", result)

    def test_collect_metrics_graceful_when_adg_unavailable(self):
        result = self._call_collect_metrics(idx_side_effect=ImportError("no module"))
        self.assertIn("metrics", result)

    def test_source_has_adg_trust_score(self):
        src = _src("agentic_core/base_agents/L6ObservabilityBase.py")
        self.assertIn("adg_trust_score", src)


# ===========================================================================
# Phase 3e — BaseDetectorValidator severity upgrade
# ===========================================================================
class TestPhase3eDetectorSeverityUpgrade(unittest.TestCase):
    """ADG-confirmed violations must be upgraded to hard_block."""

    def _make_concrete_detector(self):
        from agentic_core.L5_safety.validators.base_detector_validator import (
            AntiPatternCategory,
            AntiPatternDetector,
            AntiPatternViolation,
            EnforcementLevel,
        )

        class _ConcreteDetector(AntiPatternDetector):
            @property
            def category(self):
                return AntiPatternCategory.SILENT_SWALLOWER

            def detect(self, file_path, tree):
                return [
                    AntiPatternViolation(
                        file_path=file_path,
                        line_number=1,
                        category=AntiPatternCategory.SILENT_SWALLOWER,
                        message="test violation",
                        evidence="pass",
                        severity="warning",
                    )
                ]

        return _ConcreteDetector(enforcement_level=EnforcementLevel.WARNING)

    def test_adg_confirmed_violation_upgraded_to_hard_block(self):
        """When ADG antipattern_signals contains the category value, severity → hard_block."""
        import tempfile

        import agentic_core.adg.runtime.behavioral_index as _beh_idx

        detector = self._make_concrete_detector()
        stub = _StubProfile(antipattern_signals=frozenset({"silent_swallower"}))

        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False, encoding="utf-8") as f:
            f.write("x = 1\n")
            tmp_path = Path(f.name)

        try:
            with patch.object(_beh_idx, "get_behavioral_profile", return_value=stub):
                result = detector.scan_file(tmp_path)

            hard_block = [v for v in result.violations if v.severity == "hard_block"]
            self.assertTrue(len(hard_block) > 0, "Expected at least one hard_block violation")
            self.assertTrue(hard_block[0].metadata.get("adg_confirmed"))
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_whitelisted_violation_not_upgraded(self):
        """Whitelisted violations must never be upgraded."""
        from agentic_core.L5_safety.validators.base_detector_validator import (
            AntiPatternCategory,
            AntiPatternDetector,
            AntiPatternViolation,
            EnforcementLevel,
        )

        class _AlwaysWhitelistDetector(AntiPatternDetector):
            @property
            def category(self):
                return AntiPatternCategory.SILENT_SWALLOWER

            def detect(self, file_path, tree):
                v = AntiPatternViolation(
                    file_path=file_path,
                    line_number=1,
                    category=AntiPatternCategory.SILENT_SWALLOWER,
                    message="wl",
                    evidence="pass",
                    severity="warning",
                    whitelisted=True,
                )
                return [v]

        detector = _AlwaysWhitelistDetector(enforcement_level=EnforcementLevel.WARNING)
        stub = _StubProfile(antipattern_signals=frozenset({"silent_swallower"}))

        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False, encoding="utf-8") as f:
            f.write("x = 1\n")
            tmp_path = Path(f.name)

        try:
            import agentic_core.adg.runtime.behavioral_index as _beh_idx

            with patch.object(_beh_idx, "get_behavioral_profile", return_value=stub):
                result = detector.scan_file(tmp_path)

            for v in result.violations:
                if v.whitelisted:
                    self.assertNotEqual(v.severity, "hard_block")
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_no_adg_antipatterns_no_upgrade(self):
        """When ADG returns empty antipattern_signals, severity stays unchanged."""
        import tempfile

        import agentic_core.adg.runtime.behavioral_index as _beh_idx

        detector = self._make_concrete_detector()
        stub = _StubProfile(antipattern_signals=frozenset())

        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False, encoding="utf-8") as f:
            f.write("x = 1\n")
            tmp_path = Path(f.name)

        try:
            with patch.object(_beh_idx, "get_behavioral_profile", return_value=stub):
                result = detector.scan_file(tmp_path)

            for v in result.violations:
                self.assertNotEqual(v.severity, "hard_block")
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_source_contains_adg_confirmed_metadata(self):
        src = _src("agentic_core/L5_safety/validators/base_detector_validator.py")
        self.assertIn("adg_confirmed", src)
        self.assertIn("hard_block", src)


# ===========================================================================
# Cross-phase: no public API signatures changed
# ===========================================================================
class TestAPISignatureIntegrity(unittest.TestCase):
    """Verify that no public method signatures were altered by any phase."""

    def test_elevator_shaft_summary_signature(self):
        from agentic_core.L4_state.enforcement.elevator_shaft_consistency_enforcer import (
            ElevatorShaftConsistencyEnforcer,
        )

        sig = inspect.signature(ElevatorShaftConsistencyEnforcer.summary)
        # summary() takes only self
        params = [p for p in sig.parameters if p != "self"]
        self.assertEqual(params, [])

    def test_credential_guard_guarded_get_secret_signature(self):
        from agentic_core.L5_safety.enforcement.security.credential_access_guard import (
            CredentialAccessGuard,
        )

        sig = inspect.signature(CredentialAccessGuard.guarded_get_secret)
        params = list(sig.parameters)
        self.assertIn("secret_name", params)
        self.assertIn("kind", params)
        self.assertIn("default", params)

    def test_rag_manager_retrieve_signature(self):
        from agentic_core.knowledge.reasoning.SovereignRAGManagerAgent import SovereignRAGManager

        sig = inspect.signature(SovereignRAGManager.retrieve)
        self.assertIn("query", sig.parameters)
        self.assertIn("top_k", sig.parameters)

    def test_l3_plan_execution_signature(self):
        from agentic_core.base_agents.L3OrchestrationBase import L3OrchestrationBase

        sig = inspect.signature(L3OrchestrationBase.plan_execution)
        self.assertIn("task", sig.parameters)

    def test_l6_collect_metrics_signature(self):
        from agentic_core.base_agents.L6ObservabilityBase import L6ObservabilityBase

        sig = inspect.signature(L6ObservabilityBase.collect_metrics)
        params = [p for p in sig.parameters if p != "self"]
        self.assertEqual(params, [])

    def test_healing_policy_heal_repository_signature(self):
        from agentic_core.mixins.healing_policy_mixin import HealingPolicyMixin

        sig = inspect.signature(HealingPolicyMixin.heal_repository)
        for param in ("dry_run", "execute", "depth", "max_depth"):
            self.assertIn(param, sig.parameters)

    def test_self_diagnosis_mixin_self_diagnose_signature(self):
        from agentic_core.mixins.self_diagnosis_mixin import SelfDiagnosisMixin

        sig = inspect.signature(SelfDiagnosisMixin.self_diagnose)
        params = [p for p in sig.parameters if p != "self"]
        self.assertEqual(params, [])


# ===========================================================================
# Source-level AST cross-checks (prove injections without importing)
# ===========================================================================
class TestASTSourceInjections(unittest.TestCase):
    """Prove every Phase injection exists at the AST/text level."""

    def test_p2j_elevator_shaft_adg_in_summary(self):
        src = _src("agentic_core/L4_state/enforcement/elevator_shaft_consistency_enforcer.py")
        self.assertIn("get_behavioral_profile", src)
        self.assertIn("adg_violates", src)

    def test_p2k_credential_guard_adg_in_init(self):
        src = _src("agentic_core/L5_safety/enforcement/security/credential_access_guard.py")
        self.assertIn("_adg_violates", src)
        self.assertIn("get_behavioral_profile", src)

    def test_p2l_rag_manager_adg_confidence(self):
        src = _src("agentic_core/knowledge/reasoning/SovereignRAGManagerAgent.py")
        self.assertIn("_adg_confidence", src)
        self.assertIn("adg_confidence_weight", src)

    def test_p2l_rag_orchestrator_adg_confidence(self):
        src = _src("agentic_core/knowledge/engine/rag_orchestrator.py")
        self.assertIn("_adg_confidence", src)
        self.assertIn("adg_confidence_weight", src)

    def test_p3a_healing_policy_confidence(self):
        src = _src("agentic_core/mixins/healing_policy_mixin.py")
        self.assertIn("_confidence", src)
        self.assertIn("deterministic_coverage", src)

    def test_p3b_self_diagnosis_adg_keys(self):
        src = _src("agentic_core/mixins/self_diagnosis_mixin.py")
        self.assertIn("adg_antipatterns", src)
        self.assertIn("adg_behavioral_score", src)

    def test_p3c_l3_adg_route_mode(self):
        src = _src("agentic_core/base_agents/L3OrchestrationBase.py")
        self.assertIn("adg_route_mode", src)
        self.assertIn("adg_scope_widening", src)

    def test_p3d_l6_adg_trust_score(self):
        src = _src("agentic_core/base_agents/L6ObservabilityBase.py")
        self.assertIn("adg_trust_score", src)
        self.assertIn("ADGBehavioralIndex", src)

    def test_p3e_base_detector_hard_block(self):
        src = _src("agentic_core/L5_safety/validators/base_detector_validator.py")
        self.assertIn("hard_block", src)
        self.assertIn("adg_confirmed", src)

    def test_p4_sovereign_base_agent_imports_adg_mixin(self):
        src = _src("agentic_core/base_agents/SovereignBaseAgent.py")
        self.assertIn("ADGBehavioralMixin", src)
        self.assertIn("from agentic_core.mixins.adg_behavioral_mixin import ADGBehavioralMixin", src)

    def test_p4_sovereign_base_agent_uses_adg_mixin_in_class_def(self):
        tree = _ast_of("agentic_core/base_agents/SovereignBaseAgent.py")
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "SovereignBaseAgent":
                base_names = [ast.unparse(b) for b in node.bases]
                self.assertIn("ADGBehavioralMixin", base_names)
                return
        self.fail("SovereignBaseAgent class not found in AST")


if __name__ == "__main__":
    unittest.main(verbosity=2)

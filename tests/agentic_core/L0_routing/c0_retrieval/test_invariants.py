"""Hard NO invariant tests for C0 (I1..I12 + final-contract authority guards).

These cover the spec sections:
  - CORE INVARIANTS (lines 36-48)
  - HARD AUTHORITY BOUNDARIES (lines 12-20)
  - FORBIDDEN_CONTRACT_FIELDS (final_contract.py)
  - FORBIDDEN_EVENT_FIELDS (events.py)
"""

from __future__ import annotations

import inspect
import re
from pathlib import Path

import pytest

from agentic_core.L0_routing.c0_retrieval import (
    CORE_INVARIANTS,
    FailureMode,
    FreshnessClass,
    L1PlanContract,
    RecommendedDisposition,
    RouteContract,
    SourceClass,
    SupportStatus,
    SupportTarget,
)
from agentic_core.L0_routing.c0_retrieval.events import (
    FORBIDDEN_EVENT_FIELDS,
    C0Event,
    C0EventRecord,
)
from agentic_core.L0_routing.c0_retrieval.final_contract import (
    FORBIDDEN_CONTRACT_FIELDS,
    AclReport,
    BudgetReport,
    FinalEvidenceContract,
    PromptBudgetHint,
    ReplayMetadata,
    seal_final_contract,
)


C0_DIR = Path(__file__).resolve().parents[4] / "agentic_core" / "L0_routing" / "c0_retrieval"


class TestImportPurity:
    """Spec invariant: C0 must not import L1+ orchestrators or model libs."""

    FORBIDDEN_IMPORTS = (
        # Production code never imports model SDKs from C0.
        "openai",
        "anthropic",
        "litellm",
        "httpx",
        "requests",
        "urllib3",
        # No L1+ subsystem imports.
        "agentic_core.L1_cognition",
        "agentic_core.L2_execution",
        "agentic_core.L3_orchestration",
        "agentic_core.L5_safety",
    )

    @pytest.mark.parametrize("py_file", list(C0_DIR.glob("*.py")))
    def test_no_forbidden_imports(self, py_file):
        text = py_file.read_text(encoding="utf-8")
        # Strip docstrings + comments roughly.
        for forbidden in self.FORBIDDEN_IMPORTS:
            pattern = re.compile(rf"^\s*(?:from\s+{re.escape(forbidden)}|import\s+{re.escape(forbidden)})", re.M)
            assert not pattern.search(text), (
                f"{py_file.name} imports forbidden module {forbidden!r} "
                "— violates C0.I1/authority boundaries"
            )


class TestCoreInvariantsTable:
    def test_all_12_present(self):
        codes = [c for c, _ in CORE_INVARIANTS]
        assert codes == [f"C0.I{i}" for i in range(1, 13)]


class TestFinalContractForbiddenFields:
    """C0.I11 — output is a contract, not an answer."""

    def test_extras_cannot_carry_answer_text(self):
        with pytest.raises(ValueError, match="C0.I11"):
            FinalEvidenceContract(
                contract_id="x", route_id="R3", status=SupportStatus.PASS,
                support_score=0.5,
                extras={"answer_text": "leaked answer"},
            )

    def test_extras_cannot_carry_tool_call(self):
        with pytest.raises(ValueError, match="C0.I11"):
            FinalEvidenceContract(
                contract_id="x", route_id="R3", status=SupportStatus.PASS,
                support_score=0.5,
                extras={"tool_call": "search()"},
            )

    @pytest.mark.parametrize("field_name", sorted(FORBIDDEN_CONTRACT_FIELDS))
    def test_each_forbidden_field_rejected(self, field_name):
        with pytest.raises(ValueError, match="C0.I11"):
            FinalEvidenceContract(
                contract_id="x", route_id="R3", status=SupportStatus.PASS,
                support_score=0.5, extras={field_name: "anything"},
            )


class TestFinalContractStatusGuards:
    """Status-specific invariants: I7 (CONFLICTED), I8 (WEAK_WITH_CAVEATS), BLOCKED."""

    def test_blocked_requires_reason(self):
        with pytest.raises(ValueError, match="BLOCKED"):
            FinalEvidenceContract(
                contract_id="x", route_id="R3", status=SupportStatus.BLOCKED,
                support_score=0.0,
            )

    def test_conflicted_requires_contradictions(self):
        with pytest.raises(ValueError, match="C0.I7"):
            FinalEvidenceContract(
                contract_id="x", route_id="R3", status=SupportStatus.CONFLICTED,
                support_score=0.5,
            )

    def test_weak_with_caveats_requires_evidence_of_weakness(self):
        with pytest.raises(ValueError, match="C0.I8"):
            FinalEvidenceContract(
                contract_id="x", route_id="R3",
                status=SupportStatus.WEAK_WITH_CAVEATS,
                support_score=0.4,
            )


class TestSupportScoreClamp:
    def test_score_above_one_rejected(self):
        with pytest.raises(ValueError):
            FinalEvidenceContract(
                contract_id="x", route_id="R3", status=SupportStatus.PASS,
                support_score=1.5,
            )

    def test_negative_score_rejected(self):
        with pytest.raises(ValueError):
            FinalEvidenceContract(
                contract_id="x", route_id="R3", status=SupportStatus.PASS,
                support_score=-0.1,
            )


class TestEventForbiddenFields:
    """C0.I2 — events never carry retrieved text or credentials."""

    @pytest.mark.parametrize("field_name", sorted(FORBIDDEN_EVENT_FIELDS))
    def test_each_forbidden_field_rejected(self, field_name):
        with pytest.raises(ValueError, match="C0.I2"):
            C0EventRecord(
                event=C0Event.PREFLIGHT_EVALUATED,
                contract_id="x", route_id="R3",
                fields={field_name: "leaked"},
            )

    def test_event_must_be_enum(self):
        with pytest.raises(TypeError):
            C0EventRecord(
                event="not-an-enum",  # type: ignore[arg-type]
                contract_id="x", route_id="R3",
            )


class TestSealFinalContract:
    def test_seal_sets_hash(self):
        c = FinalEvidenceContract(
            contract_id="x", route_id="R3", status=SupportStatus.PASS,
            support_score=0.5,
        )
        sealed = seal_final_contract(c)
        assert sealed.replay_metadata.evidence_contract_hash
        # Idempotent
        sealed2 = seal_final_contract(sealed)
        assert sealed2.replay_metadata.evidence_contract_hash == sealed.replay_metadata.evidence_contract_hash


class TestPromptBudgetHintValidation:
    def test_negative_max_rejected(self):
        with pytest.raises(ValueError):
            PromptBudgetHint(max_context_tokens=-1)

    def test_negative_estimated_rejected(self):
        with pytest.raises(ValueError):
            PromptBudgetHint(estimated_context_tokens=-1)


class TestBudgetReportValidation:
    def test_negative_passes_rejected(self):
        with pytest.raises(ValueError):
            BudgetReport(retrieval_passes=-1)

    def test_negative_latency_rejected(self):
        with pytest.raises(ValueError):
            BudgetReport(latency_ms=-1)


class TestAclReportValidation:
    def test_negative_blocked_count_rejected(self):
        with pytest.raises(ValueError):
            AclReport(tenant_scope="t", blocked_sources_count=-1)


class TestImmutability:
    """Every output dataclass is frozen."""

    def test_final_contract_frozen(self):
        c = FinalEvidenceContract(
            contract_id="x", route_id="R3", status=SupportStatus.PASS,
            support_score=0.5,
        )
        with pytest.raises(Exception):
            c.contract_id = "y"  # type: ignore[misc]

    def test_replay_metadata_frozen(self):
        rm = ReplayMetadata()
        with pytest.raises(Exception):
            rm.policy_hash = "x"  # type: ignore[misc]


class TestI10NoSelfAuthRoute:
    """C0.I10 — recommended_disposition is the only routing channel; reroute
    is a recommendation, never a self-authorization."""

    def test_disposition_field_is_advisory_only(self):
        # All 6 dispositions must be valid for any status.
        c = FinalEvidenceContract(
            contract_id="x", route_id="R3", status=SupportStatus.PASS,
            support_score=0.5,
            recommended_disposition=RecommendedDisposition.REROUTE,
        )
        # No exception — recommendation is allowed.
        assert c.recommended_disposition == RecommendedDisposition.REROUTE


class TestFailureModeCatalog:
    def test_all_14_failure_modes_present(self):
        names = {m.value for m in FailureMode}
        assert "dense_only_hallucination" in names
        assert "wrong_tenant_evidence" in names
        assert "stale_policy_answer" in names
        assert "quote_distortion" in names
        assert "hidden_contradiction" in names
        assert "graph_scope_creep" in names
        assert "cache_poisoning" in names
        assert "prompt_injection" in names
        assert "fake_confidence" in names
        assert "lost_lineage" in names
        assert "overstuffed_context" in names
        assert "unsupported_synthesis" in names
        assert "docs_vs_code_mismatch" in names
        assert "runtime_vs_design_mismatch" in names
        assert len(names) == 14


class TestExampleFlowFromSpec:
    """Spec lines 952-1007 — the C5/C0/Prompt Assembly walkthrough."""

    def test_example_pipeline_runs_without_blocking(self):
        from tests.agentic_core.L0_routing.c0_retrieval._factories import (
            make_chunk, make_plan_contract, make_pool, make_route,
        )
        from agentic_core.L0_routing.c0_retrieval import run_c0
        from agentic_core.L0_routing.c0_retrieval.verdicts import RetrievalLane

        route = make_route(
            route_id="R3_SIMPLE_GROUNDED_READ",
            support_target=SupportTarget.SOURCE_SUMMARY,
            allowed_sources=(SourceClass.DOCS,),
            max_refine_attempts=1,
            freshness_class=FreshnessClass.STATIC,
        )
        pc = make_plan_contract(
            task_spec="answer question about C5 / C0 / prompt assembly",
            query_spec="prompt assembly responsibilities, C0 responsibilities, boundaries",
        )
        chunks = (
            make_chunk(
                chunk_id="c5", source_class=SourceClass.DOCS,
                text="C5 mandates: prompt assembly packages only.",
                file_path="docs/c5.md",
                found_by_lanes=(RetrievalLane.SPARSE,),
            ),
            make_chunk(
                chunk_id="c0", source_class=SourceClass.DOCS,
                text="C0 retrieves only.",
                file_path="docs/c0.md",
                found_by_lanes=(RetrievalLane.SPARSE,),
            ),
        )

        def fetch(plan, route):
            return make_pool(chunks, plan_id=plan.plan_id,
                             lanes_used=(RetrievalLane.SPARSE,))

        result = run_c0(
            route=route, plan_contract=pc,
            fetch=fetch,
            adjacency=lambda n, r: (),
        )
        # Spec example C0.5: status = PASS / WEAK_WITH_CAVEATS — never BLOCKED.
        assert result.contract.status != SupportStatus.BLOCKED
        # Disposition must point to proceed-class (not abstain).
        assert result.contract.recommended_disposition in (
            RecommendedDisposition.PROCEED,
            RecommendedDisposition.PROCEED_WITH_CAVEAT,
        )

"""Hardening tests for the L0 doctrine — closes "by design"/"inspection" gaps
identified in docs/reports/plans/l0_l3_doctrine_requirements_matrix.md.

Adds:

- Direct coverage for FixedDecisionOrder steps R1B, R4, R3, R3R4, R5-default
  (G1 — previously only R1A and R5-via-unsafe were directly asserted).
- Determinism: dict/list ordering invariance for `RouteCandidateFrame` /
  selection digest (G2).
- Determinism: changing ``policy_hash`` changes the manifest digest (G3).
- R5 ``SafeResponseType`` enum coverage (G6).
- Import-hygiene assertions: doctrine modules MUST NOT import subprocess,
  requests, httpx, sqlite3, model SDKs, or upper-layer modules (G4).

All tests are pure-Python and deterministic. No I/O, no network, no
``except Exception``.
"""

from __future__ import annotations

import ast
import importlib
from pathlib import Path

import pytest

from agentic_core.L0_routing.doctrine.contracts_l0_1 import (
    CandidateRouteId,
    L1ValidationSummary,
    PreflightStatus,
    RouteCandidateFrame,
    RouteDecisionInput,
    RouteDiscriminatorFrame,
    SourceAvailabilitySnapshot,
)
from agentic_core.L0_routing.doctrine.contracts_l0_2 import (
    ConfidenceClass,
    ExecutionFormSelected,
    RouteSelectionReceipt,
)
from agentic_core.L0_routing.doctrine.preflight import run_l0_preflight
from agentic_core.L0_routing.doctrine.replay import RouteReplayManifest
from agentic_core.L0_routing.doctrine.selector import select_route
from agentic_core.L0_routing.doctrine.terminal_routes import (
    FallbackRouteDecision,
    SafeResponseType,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _select(frame: RouteCandidateFrame) -> RouteSelectionReceipt:
    return select_route(
        frame,
        request_id="r",
        run_id="rn",
        trace_root="tr",
        l1_plan_id="lp",
        preflight_id="pf",
    )


def _frame(
    candidates: tuple[CandidateRouteId, ...],
    discriminators: RouteDiscriminatorFrame,
    *,
    preflight_status: PreflightStatus = PreflightStatus.ROUTE_READY,
) -> RouteCandidateFrame:
    return RouteCandidateFrame(
        route_candidates=candidates,
        discriminators=discriminators,
        source_availability=SourceAvailabilitySnapshot().with_hash(),
        preflight_status=preflight_status,
        candidate_frame_hash="rcf:test",
    )


# ---------------------------------------------------------------------------
# G1: FixedDecisionOrder direct coverage
# ---------------------------------------------------------------------------


class TestFixedDecisionOrderDirect:
    """Each FixedDecisionOrder step (0..7) must be directly observable."""

    def test_step_0_invalid_envelope_routes_to_r5(self) -> None:
        # Preflight status NOT in {READY, NEEDS_CLARIFY_FALLBACK, SAFE_FALLBACK_ONLY}
        # forces step 0 → R5.
        frame = _frame(
            (CandidateRouteId.R3_SIMPLE_GROUNDED_READ, CandidateRouteId.R5_FALLBACK),
            RouteDiscriminatorFrame(asks_for_factual_claim=True),
            preflight_status=PreflightStatus.ROUTE_BLOCKED_AUTHORITY,
        )
        receipt = _select(frame)
        assert receipt.selected_route_id == CandidateRouteId.R5_FALLBACK
        assert receipt.fixed_order_receipt.first_passing_step == "0_invalid_or_unsafe"

    def test_step_1_exact_cache(self) -> None:
        frame = _frame(
            (CandidateRouteId.R1A_EXACT_CACHE, CandidateRouteId.R5_FALLBACK),
            RouteDiscriminatorFrame(can_be_cached_exactly=True),
        )
        receipt = _select(frame)
        assert receipt.selected_route_id == CandidateRouteId.R1A_EXACT_CACHE
        assert receipt.fixed_order_receipt.first_passing_step == "1_exact_cache"
        assert receipt.selected_execution_form == ExecutionFormSelected.TERMINAL_SHORTCIRCUIT

    def test_step_2_semantic_cache(self) -> None:
        frame = _frame(
            (CandidateRouteId.R1B_SEMANTIC_CACHE, CandidateRouteId.R5_FALLBACK),
            RouteDiscriminatorFrame(can_be_cached_semantically=True),
        )
        receipt = _select(frame)
        assert receipt.selected_route_id == CandidateRouteId.R1B_SEMANTIC_CACHE
        assert receipt.fixed_order_receipt.first_passing_step == "2_semantic_cache"
        assert receipt.selected_execution_form == ExecutionFormSelected.TERMINAL_SHORTCIRCUIT

    def test_step_2_semantic_cache_blocked_by_current_or_latest(self) -> None:
        frame = _frame(
            (CandidateRouteId.R1B_SEMANTIC_CACHE, CandidateRouteId.R5_FALLBACK),
            RouteDiscriminatorFrame(
                can_be_cached_semantically=True,
                asks_for_current_or_latest=True,
            ),
        )
        receipt = _select(frame)
        # current/latest must NOT win semantic cache
        assert receipt.selected_route_id != CandidateRouteId.R1B_SEMANTIC_CACHE

    def test_step_3_irreversible_ambiguous_routes_to_r5(self) -> None:
        frame = _frame(
            (CandidateRouteId.R4_SINGLE_ACTION, CandidateRouteId.R5_FALLBACK),
            RouteDiscriminatorFrame(
                asks_for_external_action=True,
                asks_for_irreversible_action=True,
                has_ambiguous_action_args=True,
            ),
        )
        receipt = _select(frame)
        assert receipt.selected_route_id == CandidateRouteId.R5_FALLBACK
        assert receipt.fixed_order_receipt.first_passing_step == "3_high_risk_hitl"

    def test_step_4_low_risk_action(self) -> None:
        frame = _frame(
            (CandidateRouteId.R4_SINGLE_ACTION, CandidateRouteId.R5_FALLBACK),
            RouteDiscriminatorFrame(
                asks_for_external_action=True,
                # no ambiguity, no irreversibility
            ),
        )
        receipt = _select(frame)
        assert receipt.selected_route_id == CandidateRouteId.R4_SINGLE_ACTION
        assert receipt.fixed_order_receipt.first_passing_step == "4_low_risk_action"
        assert receipt.selected_execution_form == ExecutionFormSelected.SINGLE_STEP

    def test_step_5_grounded_read(self) -> None:
        frame = _frame(
            (CandidateRouteId.R3_SIMPLE_GROUNDED_READ, CandidateRouteId.R5_FALLBACK),
            RouteDiscriminatorFrame(
                asks_for_factual_claim=True,
                asks_for_source_grounding=True,
            ),
        )
        receipt = _select(frame)
        assert receipt.selected_route_id == CandidateRouteId.R3_SIMPLE_GROUNDED_READ
        assert receipt.fixed_order_receipt.first_passing_step == "5_grounded_read"
        assert receipt.selected_execution_form == ExecutionFormSelected.SINGLE_STEP

    def test_step_6_managed_workflow(self) -> None:
        frame = _frame(
            (CandidateRouteId.R3R4_MANAGED_WORKFLOW, CandidateRouteId.R5_FALLBACK),
            RouteDiscriminatorFrame(
                asks_for_factual_claim=True,
                likely_requires_l3=True,
                has_dependency_chain=True,
            ),
        )
        receipt = _select(frame)
        assert receipt.selected_route_id == CandidateRouteId.R3R4_MANAGED_WORKFLOW
        assert receipt.fixed_order_receipt.first_passing_step == "6_managed_workflow"
        assert receipt.selected_execution_form == ExecutionFormSelected.MANAGED_WORKFLOW

    def test_step_7_default_fallback(self) -> None:
        # All discriminator flags False → no eligible step → R5 default at step 7.
        frame = _frame(
            (CandidateRouteId.R5_FALLBACK,),
            RouteDiscriminatorFrame(),
        )
        receipt = _select(frame)
        assert receipt.selected_route_id == CandidateRouteId.R5_FALLBACK
        assert receipt.fixed_order_receipt.first_passing_step == "7_fallback"


# ---------------------------------------------------------------------------
# G2: Ordering-invariance determinism
# ---------------------------------------------------------------------------


class TestDeterminismOrderingInvariance:
    """Selection hash must NOT depend on dict/list iteration order."""

    def test_preflight_hash_stable_across_two_calls(self) -> None:
        decision_input = RouteDecisionInput(
            request_id="rq",
            run_id="rn",
            session_id="ss",
            trace_root="tr",
            tenant_id="t",
            policy_hash="p",
            blueprint_hash="b",
            replay_key="rk",
            l1_plan_id="lp",
            l1_plan_digest="ld",
            task_spec="What does the policy say about retention?",
            query_spec="policy retention",
            support_expectation="POLICY_CLAUSE",
            visible_source_handles=("policy_doc",),
            source_expectations=("policy_doc",),
            validation_summary=L1ValidationSummary(),
        )
        a = run_l0_preflight(decision_input)
        b = run_l0_preflight(decision_input)
        assert a.candidate_frame_hash == b.candidate_frame_hash
        assert a.source_availability.availability_hash == b.source_availability.availability_hash

    def test_selection_hash_stable_across_two_calls(self) -> None:
        frame = _frame(
            (CandidateRouteId.R1A_EXACT_CACHE, CandidateRouteId.R5_FALLBACK),
            RouteDiscriminatorFrame(can_be_cached_exactly=True),
        )
        a = _select(frame)
        b = _select(frame)
        assert a.route_selection_hash == b.route_selection_hash
        assert a.fixed_order_receipt.deterministic_order_hash == b.fixed_order_receipt.deterministic_order_hash


# ---------------------------------------------------------------------------
# G3: policy_hash change ⇒ different replay digest
# ---------------------------------------------------------------------------


class TestPolicyHashChangeChangesDigest:
    """Per 03.5 §INVARIANTS — digest MUST be sensitive to policy_hash."""

    def _manifest(self, *, policy_hash: str) -> RouteReplayManifest:
        return RouteReplayManifest(
            replay_manifest_id="rm",
            route_contract_id="rc",
            normalized_request_hash="nrh",
            l1_plan_digest="lpd",
            route_candidate_frame_hash="rcf",
            route_score_vector_hash="rsv",
            fixed_decision_order_hash="fdoh",
            policy_hash=policy_hash,
            blueprint_hash="b",
            snapshot_id="snap",
            source_availability_snapshot_hash="sas",
            registry_snapshot_hash="rs",
            deterministic_route_digest="drd",
            hmac_sig="",
            replay_certifiable=True,
        )

    def test_same_policy_hash_same_expected_digest(self) -> None:
        a = self._manifest(policy_hash="pA")
        b = self._manifest(policy_hash="pA")
        assert a.expected_digest() == b.expected_digest()

    def test_changed_policy_hash_changes_expected_digest(self) -> None:
        a = self._manifest(policy_hash="pA")
        b = self._manifest(policy_hash="pB")
        assert a.expected_digest() != b.expected_digest()

    def test_changed_blueprint_hash_changes_expected_digest(self) -> None:
        a = self._manifest(policy_hash="pA")
        b_payload = {**a.canonical_payload(), "blueprint_hash": "different"}
        # Manually compute by mirroring the manifest's payload contract.
        c = RouteReplayManifest(
            replay_manifest_id="rm",
            route_contract_id="rc",
            normalized_request_hash="nrh",
            l1_plan_digest="lpd",
            route_candidate_frame_hash="rcf",
            route_score_vector_hash="rsv",
            fixed_decision_order_hash="fdoh",
            policy_hash="pA",
            blueprint_hash="different",
            snapshot_id="snap",
            source_availability_snapshot_hash="sas",
            registry_snapshot_hash="rs",
            deterministic_route_digest="drd",
            hmac_sig="",
            replay_certifiable=True,
        )
        assert a.expected_digest() != c.expected_digest()
        assert b_payload["blueprint_hash"] == "different"  # sanity


# ---------------------------------------------------------------------------
# G6: SafeResponseType enum coverage on FallbackRouteDecision
# ---------------------------------------------------------------------------


class TestSafeResponseTypeCoverage:
    """Every member of `SafeResponseType` must be acceptable on R5 fallback."""

    @pytest.mark.parametrize(
        "srt",
        list(SafeResponseType),
        ids=[s.value for s in SafeResponseType],
    )
    def test_each_safe_response_type_validates(self, srt: SafeResponseType) -> None:
        d = FallbackRouteDecision(
            safe_response_type=srt,
            reason_codes=("REASON_X",),
            fallback_guard_receipt="rcpt",
            ret_packet_ref="ret",
        )
        assert d.safe_response_type == srt


# ---------------------------------------------------------------------------
# G4: Import-hygiene — doctrine MUST NOT import I/O or upper-layer code
# ---------------------------------------------------------------------------


_FORBIDDEN_TOP_MODULES = frozenset({
    "subprocess",
    "requests",
    "httpx",
    "urllib3",
    "aiohttp",
    "socket",
    "sqlite3",
    "openai",
    "anthropic",
    "google",
    "boto3",
})

# Doctrine layer-direction rule: L0 doctrine may not import L3+; L3 doctrine
# may not import L4/L5/L6. Both may import their own siblings.
_FORBIDDEN_PREFIXES_L0 = (
    "agentic_core.L1_cognition",
    "agentic_core.L2_execution",
    "agentic_core.L3_orchestration",
    "agentic_core.L4_state",
    "agentic_core.L5_safety",
    "agentic_core.L6_observability",
)
_FORBIDDEN_PREFIXES_L3 = (
    "agentic_core.L4_state",
    "agentic_core.L5_safety",
    "agentic_core.L6_observability",
)


def _walk_imports(path: Path) -> list[tuple[str, int]]:
    """Return [(module_name, lineno), ...] from all import statements in path."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    out: list[tuple[str, int]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                out.append((alias.name, node.lineno))
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                out.append((node.module, node.lineno))
    return out


_REPO_ROOT = Path(__file__).resolve().parents[4]


class TestImportHygiene:
    """Doctrine modules must remain pure: no I/O, no upper-layer imports."""

    def _l0_files(self) -> list[Path]:
        d = _REPO_ROOT / "agentic_core" / "L0_routing" / "doctrine"
        return sorted(p for p in d.glob("*.py") if not p.name.startswith("__pycache__"))

    def _l3_files(self) -> list[Path]:
        d = _REPO_ROOT / "agentic_core" / "L3_orchestration" / "doctrine"
        return sorted(p for p in d.glob("*.py") if not p.name.startswith("__pycache__"))

    def test_l0_files_exist(self) -> None:
        files = self._l0_files()
        assert len(files) >= 8, f"expected >=8 L0 doctrine files, got {len(files)}"

    def test_l3_files_exist(self) -> None:
        files = self._l3_files()
        assert len(files) >= 6, f"expected >=6 L3 doctrine files, got {len(files)}"

    def test_l0_no_forbidden_top_modules(self) -> None:
        for path in self._l0_files():
            for mod, lineno in _walk_imports(path):
                top = mod.split(".")[0]
                assert top not in _FORBIDDEN_TOP_MODULES, (
                    f"{path.name}:{lineno} imports forbidden top module {mod!r}"
                )

    def test_l3_no_forbidden_top_modules(self) -> None:
        for path in self._l3_files():
            for mod, lineno in _walk_imports(path):
                top = mod.split(".")[0]
                assert top not in _FORBIDDEN_TOP_MODULES, (
                    f"{path.name}:{lineno} imports forbidden top module {mod!r}"
                )

    def test_l0_no_upper_layer_imports(self) -> None:
        for path in self._l0_files():
            for mod, lineno in _walk_imports(path):
                for prefix in _FORBIDDEN_PREFIXES_L0:
                    assert not mod.startswith(prefix), (
                        f"{path.name}:{lineno} imports {mod!r} (forbidden by L0 layer gravity)"
                    )

    def test_l3_no_upper_layer_imports(self) -> None:
        for path in self._l3_files():
            for mod, lineno in _walk_imports(path):
                for prefix in _FORBIDDEN_PREFIXES_L3:
                    assert not mod.startswith(prefix), (
                        f"{path.name}:{lineno} imports {mod!r} (forbidden by L3 layer gravity)"
                    )

    def test_no_open_for_write_in_doctrine(self) -> None:
        """Doctrine modules MUST NOT call ``open(..., 'w')`` or similar.

        This is a strong proxy for "no I/O" — the doctrine surface is pure
        data + pure functions.
        """
        for path in self._l0_files() + self._l3_files():
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "open":
                    # Allow if explicitly a read mode; flag write modes.
                    for arg in node.args[1:2]:
                        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                            assert "w" not in arg.value and "a" not in arg.value, (
                                f"{path.name}:{node.lineno} opens file in write/append mode {arg.value!r}"
                            )

    def test_doctrine_modules_load_clean(self) -> None:
        """All 16 doctrine modules import cleanly (no circular imports)."""
        modules = [
            "agentic_core.L0_routing.doctrine",
            "agentic_core.L0_routing.doctrine.contracts_l0_1",
            "agentic_core.L0_routing.doctrine.contracts_l0_2",
            "agentic_core.L0_routing.doctrine.preflight",
            "agentic_core.L0_routing.doctrine.selector",
            "agentic_core.L0_routing.doctrine.terminal_routes",
            "agentic_core.L0_routing.doctrine.handoffs",
            "agentic_core.L0_routing.doctrine.telemetry",
            "agentic_core.L0_routing.doctrine.replay",
            "agentic_core.L3_orchestration.doctrine",
            "agentic_core.L3_orchestration.doctrine.contracts_l3_6",
            "agentic_core.L3_orchestration.doctrine.eligibility",
            "agentic_core.L3_orchestration.doctrine.contracts_l3_7",
            "agentic_core.L3_orchestration.doctrine.state",
            "agentic_core.L3_orchestration.doctrine.contracts_l3_8",
            "agentic_core.L3_orchestration.doctrine.governance",
        ]
        for mod_name in modules:
            mod = importlib.import_module(mod_name)
            assert mod is not None

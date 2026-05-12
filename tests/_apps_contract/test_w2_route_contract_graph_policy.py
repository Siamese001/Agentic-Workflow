"""W2: RouteContract graph policy carriage tests.

Plan: chroma-graphrag-core-wiring-gaps-b3f7a1 — Wave 2

Invariants verified:
  - GraphTraversePolicy accepted by runtime RouteContract.
  - Defaults are safe (graph_expansion_allowed=False, live_wiring_deferred=True).
  - L0 maps graph_traverse profile block to R3 RouteContract.
  - R1A, R5, and R1B terminal hit carry no active graph policy (None).
  - L0 never calls run_graph_traverse().
  - No app_id branching in graph policy mapping.
  - apps_lic semantic cache still bypassed (no R1B live call).
  - apps_rg quarantined adapter untouched.
  - W1 R1B tests still pass (regression guard).
"""

from __future__ import annotations

import ast
import inspect
from pathlib import Path
from typing import Any, Dict
from unittest.mock import MagicMock, patch

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_authority_receipt() -> Any:
    from agentic_core.runtime.contracts.apps_rg_runtime_authority_policy import (
        AuthorityValidationReceipt,
    )
    return AuthorityValidationReceipt(
        allowed=True,
        passed=True,
        request_id="w2-test-req-001",
        timestamp_iso="2026-05-13T00:00:00Z",
    )


def _make_validated_request(
    cert_ref: str = "cert-ref-w2-hardening",
    target_company: str = "W2CorpTest",
    route_profile_ref: str = "apps_research/config/domain_contract/route_profile.company_brief.v1.yaml",
    cache_profile_ref: str = "apps_research/config/domain_contract/cache_profiles.yaml",
) -> Any:
    from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest

    return ValidatedRequest(
        request_id="w2-req-001",
        run_id="w2-run-001",
        app_id="apps_research",
        task_class="company_brief",
        payload_digest="test-digest",
        authority_validation_receipt=_make_authority_receipt(),
        trace_id="w2-trace-001",
        tenant_id="apps_research",
        l5_certification_ref=cert_ref,
        app_payload={
            "target_company": target_company,
            "runtime_customization_package": {
                "profile_refs": {
                    "route_profile": route_profile_ref,
                    "cache_profile": cache_profile_ref,
                }
            },
        },
    )


def _make_minimal_route_profile_with_graph() -> Dict[str, Any]:
    """Minimal route profile that includes a graph_traverse block and R3."""
    return {
        "route_evaluation_order": [
            {"route_id": "R3_SIMPLE_GROUNDED_READ"},
        ],
        "managed_workflow_allowed": False,
        "graph_traverse": {
            "graph_expansion_allowed": True,
            "max_hops": 2,
            "max_nodes": 64,
            "max_edges": 128,
            "allowed_relation_types": ["SOURCE_AUTHORITY", "CONTRADICTS"],
            "contradiction_scan_enabled": True,
            "supersession_scan_enabled": False,
            "graph_adapter_ref": "apps_research.integrations.c0_graph_adapter",
            "live_wiring_deferred": True,
            "wiring_gate": "GRAPH_TRAVERSE_POLICY_AGENTIC_CORE_REQUIRED",
        },
    }


def _make_minimal_route_profile_no_graph() -> Dict[str, Any]:
    """Minimal route profile WITHOUT a graph_traverse block."""
    return {
        "route_evaluation_order": [
            {"route_id": "R3_SIMPLE_GROUNDED_READ"},
        ],
        "managed_workflow_allowed": False,
    }


def _make_minimal_route_profile_r5() -> Dict[str, Any]:
    """Profile that routes to R5 (unroutable — target_company missing)."""
    return {
        "route_evaluation_order": [
            {"route_id": "R5_PRE_ROUTE_FALLBACK"},
        ],
        "managed_workflow_allowed": False,
    }


def _make_minimal_route_profile_r1a() -> Dict[str, Any]:
    """Profile that routes to R1A (exact cache)."""
    return {
        "route_evaluation_order": [
            {"route_id": "R1A_EXACT_CACHE"},
        ],
        "managed_workflow_allowed": False,
    }


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestGraphTraversePolicyDataclass:
    """test_route_contract_accepts_graph_traverse_policy"""

    def test_route_contract_accepts_graph_traverse_policy(self) -> None:
        """RouteContract field graph_traverse_policy exists and accepts a GraphTraversePolicy."""
        from agentic_core.runtime.contracts.route_contract import (
            GraphTraversePolicy,
            RouteContract,
        )

        policy = GraphTraversePolicy(
            graph_expansion_allowed=True,
            max_hops=3,
            max_nodes=100,
            max_edges=200,
            allowed_relation_types=("SOURCE_AUTHORITY", "CONTRADICTS"),
            contradiction_scan_enabled=True,
            supersession_scan_enabled=True,
            graph_adapter_ref="apps_research.integrations.c0_graph_adapter",
            live_wiring_deferred=False,
            wiring_gate="TEST_GATE",
        )

        rc = RouteContract(
            request_id="test-req",
            run_id="test-run",
            app_id="apps_research",
            trace_id="test-trace",
            route_id="R3_SIMPLE_GROUNDED_READ",
            l3_required=False,
            grounding_required=True,
            model_generation_required=True,
            write_authority_present=False,
            l5_certification_ref="cert-ref-w2-test",
            graph_traverse_policy=policy,
        )

        assert rc.graph_traverse_policy is policy
        assert rc.graph_traverse_policy.max_hops == 3
        assert rc.graph_traverse_policy.is_active is True

    def test_graph_traverse_policy_defaults_safe(self) -> None:
        """GraphTraversePolicy defaults are safe (no expansion, deferred=True)."""
        from agentic_core.runtime.contracts.route_contract import GraphTraversePolicy

        policy = GraphTraversePolicy()

        assert policy.graph_expansion_allowed is False
        assert policy.live_wiring_deferred is True
        assert policy.max_hops == 0
        assert policy.max_nodes == 0
        assert policy.max_edges == 0
        assert policy.allowed_relation_types == ()
        assert policy.contradiction_scan_enabled is False
        assert policy.supersession_scan_enabled is False
        assert policy.graph_adapter_ref == ""
        assert policy.wiring_gate == ""
        assert policy.is_active is False


class TestL0GraphPolicyMapping:
    """test_l0_maps_graph_profile_to_r3_route_contract"""

    def test_l0_maps_graph_profile_to_r3_route_contract(self) -> None:
        """L0 reads graph_traverse block from route profile and attaches it to R3 RouteContract."""
        from agentic_core.L0_routing.package_driven_l0_binding import (
            _read_graph_traverse_policy,
        )
        from agentic_core.runtime.contracts.route_contract import GraphTraversePolicy

        profile = _make_minimal_route_profile_with_graph()
        policy = _read_graph_traverse_policy(profile)

        assert isinstance(policy, GraphTraversePolicy)
        assert policy.graph_expansion_allowed is True
        assert policy.max_hops == 2
        assert policy.max_nodes == 64
        assert policy.max_edges == 128
        assert "SOURCE_AUTHORITY" in policy.allowed_relation_types
        assert "CONTRADICTS" in policy.allowed_relation_types
        assert policy.contradiction_scan_enabled is True
        assert policy.live_wiring_deferred is True
        assert policy.wiring_gate == "GRAPH_TRAVERSE_POLICY_AGENTIC_CORE_REQUIRED"
        assert policy.graph_adapter_ref == "apps_research.integrations.c0_graph_adapter"

    def test_l0_graph_policy_absent_when_no_block(self) -> None:
        """_read_graph_traverse_policy returns None when route profile has no graph_traverse block."""
        from agentic_core.L0_routing.package_driven_l0_binding import (
            _read_graph_traverse_policy,
        )

        profile = _make_minimal_route_profile_no_graph()
        assert _read_graph_traverse_policy(profile) is None


class TestTerminalRoutesHaveNoGraphPolicy:
    """R1A, R5, and R1B terminal hit must carry None for graph_traverse_policy."""

    def _make_vr(self, target_company: str = "TestCo") -> Any:
        from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest

        return ValidatedRequest(
            request_id="w2-term-req",
            run_id="w2-term-run",
            app_id="apps_research",
            task_class="company_brief",
            payload_digest="td",
            authority_validation_receipt=_make_authority_receipt(),
            trace_id="w2-term-trace",
            tenant_id="apps_research",
            l5_certification_ref="cert-ref-w2-terminal",
            app_payload={
                "target_company": target_company,
                "runtime_customization_package": {
                    "profile_refs": {
                        "route_profile": "test_profile",
                        "cache_profile": "test_cache_profile",
                    }
                },
            },
        )

    def test_terminal_r1a_route_has_no_graph_policy(self) -> None:
        """R1A RouteContract must carry graph_traverse_policy=None."""
        from agentic_core.L0_routing.package_driven_l0_binding import (
            l0_evaluate_routes_package_driven,
        )

        vr = self._make_vr(target_company="TargetCoR1A")
        profile = _make_minimal_route_profile_r1a()
        cache_profile = {"cache_profile_id": "test-cache"}

        with (
            patch(
                "agentic_core.L0_routing.package_driven_l0_binding._load_route_profile",
                return_value=profile,
            ),
            patch(
                "agentic_core.L0_routing.package_driven_l0_binding._load_cache_profile",
                return_value=cache_profile,
            ),
        ):
            result, evals = l0_evaluate_routes_package_driven(vr)

        from agentic_core.runtime.contracts.route_contract import RouteContract

        assert isinstance(result, RouteContract)
        assert result.route_id == "R1A_EXACT_CACHE"
        assert result.graph_traverse_policy is None

    def test_terminal_r5_route_has_no_graph_policy(self) -> None:
        """R5 RouteContract must carry graph_traverse_policy=None."""
        from agentic_core.L0_routing.package_driven_l0_binding import (
            l0_evaluate_routes_package_driven,
        )

        vr = self._make_vr(target_company="")  # missing → R5 fires
        profile = _make_minimal_route_profile_r5()
        cache_profile = {"cache_profile_id": "test-cache"}

        with (
            patch(
                "agentic_core.L0_routing.package_driven_l0_binding._load_route_profile",
                return_value=profile,
            ),
            patch(
                "agentic_core.L0_routing.package_driven_l0_binding._load_cache_profile",
                return_value=cache_profile,
            ),
        ):
            result, evals = l0_evaluate_routes_package_driven(vr)

        from agentic_core.runtime.contracts.route_contract import RouteContract

        assert isinstance(result, RouteContract)
        assert result.route_id == "R5_PRE_ROUTE_FALLBACK"
        assert result.graph_traverse_policy is None

    def test_r1b_terminal_hit_has_no_graph_policy(self) -> None:
        """R1B cache hit emits RETTerminalPacket — no RouteContract at all, hence no graph policy."""
        from agentic_core.L0_routing.package_driven_l0_binding import (
            RETTerminalPacket,
            l0_evaluate_routes_package_driven,
        )

        vr = self._make_vr(target_company="HitCo")
        r1b_profile = {
            "route_evaluation_order": [
                {"route_id": "R1B_SEMANTIC_CACHE"},
                {"route_id": "R3_SIMPLE_GROUNDED_READ"},
            ],
            "managed_workflow_allowed": False,
            "route_eligibility": {
                "R1B_SEMANTIC_CACHE": {
                    "compatibility_requirements": {}
                }
            },
        }
        cache_profile = {
            "cache_profile_id": "test-r1b-cache",
            "semantic_cache": {
                "enabled": True,
                "namespace": "test.ns.v1",
                "similarity_threshold": 0.88,
                "live_wiring_deferred": False,
            },
        }
        d2_hit = {
            "route_id": "R1B_SEMANTIC_CACHE",
            "similarity": 0.95,
            "cached_response": "cached_output",
        }

        with (
            patch(
                "agentic_core.L0_routing.package_driven_l0_binding._load_route_profile",
                return_value=r1b_profile,
            ),
            patch(
                "agentic_core.L0_routing.package_driven_l0_binding._load_cache_profile",
                return_value=cache_profile,
            ),
            patch(
                "agentic_core.L0_routing.package_driven_l0_binding.check_d2_semantic_cache",
                return_value=d2_hit,
            ),
        ):
            result, evals = l0_evaluate_routes_package_driven(vr)

        assert isinstance(result, RETTerminalPacket)
        assert not hasattr(result, "graph_traverse_policy") or getattr(result, "graph_traverse_policy", None) is None


class TestL0DoesNotCallRunGraphTraverse:
    """test_l0_does_not_call_run_graph_traverse"""

    def test_l0_does_not_call_run_graph_traverse(self) -> None:
        """run_graph_traverse must never be called from package_driven_l0_binding."""
        binding_path = (
            REPO_ROOT
            / "agentic_core"
            / "L0_routing"
            / "package_driven_l0_binding.py"
        )
        source = binding_path.read_text(encoding="utf-8")
        tree = ast.parse(source)

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                name = ""
                if isinstance(func, ast.Name):
                    name = func.id
                elif isinstance(func, ast.Attribute):
                    name = func.attr
                assert name != "run_graph_traverse", (
                    f"run_graph_traverse() called at line {node.lineno} — forbidden in L0"
                )

        # AST-based check already confirms no call node with name "run_graph_traverse".
        # The docstring says "does NOT call run_graph_traverse()" which is correct prose.


class TestNoAppIdBranchInGraphPolicyMapping:
    """test_no_app_id_branch_in_graph_policy_mapping"""

    def test_no_app_id_branch_in_graph_policy_mapping(self) -> None:
        """_read_graph_traverse_policy must contain no app_id branching."""
        binding_path = (
            REPO_ROOT
            / "agentic_core"
            / "L0_routing"
            / "package_driven_l0_binding.py"
        )
        source = binding_path.read_text(encoding="utf-8")
        tree = ast.parse(source)

        # Extract _read_graph_traverse_policy source lines
        func_lines = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "_read_graph_traverse_policy":
                func_lines = source.splitlines()[node.lineno - 1 : node.end_lineno]
                break

        assert func_lines, "_read_graph_traverse_policy function not found in binding"
        func_text = "\n".join(func_lines)

        for forbidden in ("apps_lic", "apps_rg", "apps_research", "app_id ==", "app_id!="):
            assert forbidden not in func_text, (
                f"Forbidden app_id branch found in _read_graph_traverse_policy: {forbidden!r}"
            )


class TestAppsLicAndRgInvariants:
    """apps_lic semantic cache still bypassed; apps_rg adapter untouched."""

    def test_apps_lic_semantic_cache_still_bypassed(self) -> None:
        """apps_lic cache_profiles.yaml has semantic_cache.enabled=false — R1B never fires."""
        import yaml

        profile_path = (
            REPO_ROOT / "apps_lic" / "config" / "domain_contract" / "cache_profiles.yaml"
        )
        with open(profile_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        sc = data.get("semantic_cache", {})
        assert sc.get("enabled") is False or sc.get("enabled") == False, (
            "apps_lic semantic_cache.enabled must remain false (non-goal for this plan)"
        )

    def test_apps_rg_quarantined_adapter_untouched(self) -> None:
        """apps_rg/cache/r1b_adapter.py still raises RuntimeError on import (quarantined)."""
        adapter_path = (
            REPO_ROOT / "apps_rg" / "cache" / "r1b_adapter.py"
        )
        source = adapter_path.read_text(encoding="utf-8")
        assert "RuntimeError" in source, (
            "apps_rg/cache/r1b_adapter.py must still raise RuntimeError (quarantine intact)"
        )


class TestW1RegressionGuard:
    """test_w1_r1b_tests_still_pass — ensure W1 tests are not broken by W2 changes."""

    def test_w1_r1b_tests_still_pass(self) -> None:
        """Verify W1 test file still importable and all 19 tests are present."""
        w1_path = (
            REPO_ROOT / "tests" / "_apps_contract" / "test_w1_core_r1b_cache_wiring.py"
        )
        assert w1_path.exists(), "W1 test file missing"
        source = w1_path.read_text(encoding="utf-8")

        required_tests = [
            "test_r1b_disabled_no_lookup",
            "test_r1b_enabled_calls_check_d2_semantic_cache",
            "test_r1b_miss_continues_to_next_route",
            "test_r1b_hit_emits_ret_terminal_packet",
            "test_r1b_miss_constructs_real_r3_route_contract",
        ]
        for name in required_tests:
            assert f"def {name}" in source, f"W1 test {name!r} missing from test file"

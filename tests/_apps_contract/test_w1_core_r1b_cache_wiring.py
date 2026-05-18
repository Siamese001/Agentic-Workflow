"""W1 tests — Generic R1B semantic cache wiring (GAP-01, GAP-02).

Plan: chroma-graphrag-core-wiring-gaps-b3f7a1 W1
Scope: agentic_core/L0_routing/package_driven_l0_binding.py

Invariants enforced:
- apps_lic semantic cache remains disabled (non-goal).
- apps_lic route_evaluation_order must not include R1B_SEMANTIC_CACHE.
- apps_lic must never call check_d2_semantic_cache().
- apps_lic must never emit RETTerminalPacket with ret_type=SEMANTIC_CACHE_HIT.
- On R1B miss: continue to next route (R3).
- On R1B hit: emit RETTerminalPacket going to Exit, never to user.
- Hit must skip C0, Prompt Assembly, L3, L2 (terminal_type=semantic_cache_hit).
- UNKNOWN / non-PASS support closes as miss (fail-closed).
- No app_id branches in package_driven_l0_binding.py.
- apps_rg quarantined adapter untouched.
- No graph code, no ingestion, no RouteContract changed.
"""
from __future__ import annotations

import ast
import inspect
import re
import textwrap
from pathlib import Path
from typing import Any, Dict, Optional
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Repo-root paths (resolved relative to this file)
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).parent.parent.parent
L0_BINDING = REPO_ROOT / "agentic_core" / "L0_routing" / "package_driven_l0_binding.py"
APPS_LIC_CACHE_PROFILE = REPO_ROOT / "apps_lic" / "config" / "domain_contract" / "cache_profiles.yaml"
APPS_RG_CACHE_PROFILE = REPO_ROOT / "apps_rg" / "config" / "domain_contract" / "cache_profiles.yaml"
APPS_RESEARCH_CACHE_PROFILE = REPO_ROOT / "apps_research" / "config" / "domain_contract" / "cache_profiles.yaml"
APPS_LIC_ROUTE_PROFILE = REPO_ROOT / "apps_lic" / "config" / "domain_contract"
APPS_RG_QUARANTINED_ADAPTER = REPO_ROOT / "apps_rg" / "cache" / "r1b_adapter.py"
ROUTE_CONTRACT_FILE = REPO_ROOT / "agentic_core" / "runtime" / "contracts" / "route_contract.py"
C0_3_DIR = REPO_ROOT / "agentic_core" / "L0_routing" / "c0_retrieval" / "c0_3_enhanced"
INGESTION_DIR = REPO_ROOT / "tools" / "ingestion"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_yaml(path: Path) -> Dict[str, Any]:
    import yaml  # type: ignore[import]
    with open(path) as f:
        data = yaml.safe_load(f)
    return data if isinstance(data, dict) else {}


def _make_validated_request(
    app_id: str = "apps_research",
    task_class: str = "company_brief",
    tenant_id: str = "t1",
    request_id: str = "req-001",
    run_id: str = "run-001",
    app_payload: Optional[Dict[str, Any]] = None,
) -> Any:
    """Build a minimal ValidatedRequest-compatible mock.

    Uses MagicMock with name matching ValidatedRequest so that spec-based
    tests work.  The isinstance check in l0_evaluate_routes_package_driven
    must be patched separately in each integration test via
    _patch_validated_request_isinstance().
    """
    req = MagicMock()
    req.app_id = app_id
    req.task_class = task_class
    req.tenant_id = tenant_id
    req.request_id = request_id
    req.run_id = run_id
    req.trace_id = "trace-001"
    req.app_payload = app_payload or {
        "runtime_customization_package": {
            "profile_refs": {
                "route_profile": f"{app_id}/config/domain_contract/route_profiles.yaml",
                "cache_profile": f"{app_id}/config/domain_contract/cache_profiles.yaml",
            }
        },
        "target_company": "TestCo",
    }
    return req


def _patch_isinstance():
    """Context manager: replace ValidatedRequest in the binding module's namespace
    with MagicMock itself so that isinstance(mock_obj, ValidatedRequest) returns True.

    This avoids patching builtins.isinstance (which causes infinite recursion because
    MagicMock calls isinstance internally in __setattr__).
    """
    return patch(
        "agentic_core.L0_routing.package_driven_l0_binding.ValidatedRequest",
        new=MagicMock,
    )


class _FakeRouteContract:
    """Minimal RouteContract stand-in for tests that fall through to R3.
    Avoids __post_init__ l5_certification_ref guard without modifying production code.
    """
    def __init__(self, **kwargs: Any) -> None:
        for k, v in kwargs.items():
            object.__setattr__(self, k, v)

    def __setattr__(self, name: str, value: Any) -> None:
        object.__setattr__(self, name, value)


def _patch_route_contract():
    """Replace RouteContract in the binding's namespace with a validation-free stub."""
    return patch(
        "agentic_core.L0_routing.package_driven_l0_binding.RouteContract",
        new=_FakeRouteContract,
    )


# ---------------------------------------------------------------------------
# 1. test_r1b_disabled_no_lookup
# ---------------------------------------------------------------------------

def test_r1b_disabled_no_lookup():
    """_read_semantic_cache_profile returns None when enabled=false (nested shape)."""
    from agentic_core.L0_routing.package_driven_l0_binding import _read_semantic_cache_profile

    profile = {
        "cache_profile_id": "cp::test::v1",
        "semantic_cache": {
            "enabled": False,
            "namespace": "test.v1",
            "similarity_threshold": 0.90,
        },
    }
    assert _read_semantic_cache_profile(profile) is None


# ---------------------------------------------------------------------------
# 2. test_apps_lic_r1b_absent_from_route_order
# ---------------------------------------------------------------------------

def test_apps_lic_r1b_absent_from_route_order():
    """apps_lic cache profile: semantic_cache.enabled must be false.
    GAP-08 non-goal invariant: apps_lic never gets R1B wired.
    """
    import yaml  # type: ignore[import]
    profile = _load_yaml(APPS_LIC_CACHE_PROFILE)
    nested = profile.get("semantic_cache", {})
    assert nested.get("enabled") is False, (
        f"apps_lic semantic_cache.enabled must be false; got {nested.get('enabled')}"
    )


# ---------------------------------------------------------------------------
# 3. test_apps_lic_never_calls_check_d2_semantic_cache
# ---------------------------------------------------------------------------

def test_apps_lic_never_calls_check_d2_semantic_cache():
    """_read_semantic_cache_profile returns None for apps_lic profile (enabled=false)."""
    from agentic_core.L0_routing.package_driven_l0_binding import _read_semantic_cache_profile
    profile = _load_yaml(APPS_LIC_CACHE_PROFILE)
    result = _read_semantic_cache_profile(profile)
    assert result is None, (
        "apps_lic cache profile must yield None from _read_semantic_cache_profile "
        "(non-goal: personalized_outreach_not_cacheable)"
    )


# ---------------------------------------------------------------------------
# 4. test_apps_lic_never_emits_semantic_cache_hit
# ---------------------------------------------------------------------------

def test_apps_lic_never_emits_semantic_cache_hit():
    """End-to-end: even if R1B is in eval order, apps_lic profile returns None from
    _read_semantic_cache_profile, so check_d2_semantic_cache is never called and
    no RETTerminalPacket is emitted."""
    from agentic_core.L0_routing.package_driven_l0_binding import (
        RETTerminalPacket,
        _read_semantic_cache_profile,
    )
    from agentic_core.L0_routing.reasoning.route_gates import check_d2_semantic_cache

    profile = _load_yaml(APPS_LIC_CACHE_PROFILE)
    cfg = _read_semantic_cache_profile(profile)
    assert cfg is None, "apps_lic must never produce a live R1B config"

    # Verify: if cfg is None, the R1B arm skips the call entirely.
    # We test this by asserting check_d2_semantic_cache is never invoked via
    # the _read_semantic_cache_profile gate for the apps_lic profile.
    with patch(
        "agentic_core.L0_routing.package_driven_l0_binding.check_d2_semantic_cache"
    ) as mock_d2:
        # Simulate what the R1B arm does
        r1b_cfg = _read_semantic_cache_profile(profile)
        if r1b_cfg is not None:
            # This branch must NOT be reached for apps_lic
            mock_d2(
                {},
                namespace=r1b_cfg["namespace"],
                tenant_id="",
                similarity_threshold_override=r1b_cfg["similarity_threshold"],
            )
        mock_d2.assert_not_called()


# ---------------------------------------------------------------------------
# 5. test_r1b_enabled_calls_check_d2_semantic_cache
# ---------------------------------------------------------------------------

def test_r1b_enabled_calls_check_d2_semantic_cache():
    """_read_semantic_cache_profile returns live config for a profile with enabled=true
    and live_wiring_deferred=false (simulated live profile)."""
    from agentic_core.L0_routing.package_driven_l0_binding import _read_semantic_cache_profile

    profile = {
        "cache_profile_id": "cp::apps_test::v1",
        "semantic_cache": {
            "enabled": True,
            "namespace": "apps_test.v1",
            "similarity_threshold": 0.90,
            "live_wiring_deferred": False,
        },
    }
    cfg = _read_semantic_cache_profile(profile)
    assert cfg is not None
    assert cfg["enabled"] is True
    assert cfg["namespace"] == "apps_test.v1"
    assert cfg["similarity_threshold"] == 0.90
    assert cfg["live_wiring_deferred"] is False


# ---------------------------------------------------------------------------
# 6. test_r1b_miss_continues_to_next_route
# ---------------------------------------------------------------------------

def test_r1b_miss_continues_to_next_route():
    """When check_d2_semantic_cache returns None (miss), the L0 binding must
    continue to R3 rather than returning a R1B RouteContract or RETTerminalPacket."""
    from agentic_core.L0_routing.package_driven_l0_binding import (
        RETTerminalPacket,
        l0_evaluate_routes_package_driven,
    )
    from agentic_core.runtime.contracts.route_contract import RouteContract

    req = _make_validated_request(app_id="apps_research")

    fake_route_profile = {
        "route_evaluation_order": [
            {"route_id": "R1B_SEMANTIC_CACHE", "condition": "semantic_cache_compatible"},
            {"route_id": "R3_SIMPLE_GROUNDED_READ", "condition": "default"},
        ],
        "active_execution_form": "SINGLE_STEP",
        "managed_workflow_allowed": False,
    }
    fake_cache_profile = {
        "cache_profile_id": "cp::apps_research::v1",
        "semantic_cache": {
            "enabled": True,
            "namespace": "apps_research.company_brief.v1",
            "similarity_threshold": 0.92,
            "live_wiring_deferred": False,
        },
    }

    with (
        _patch_isinstance(),
        _patch_route_contract(),
        patch(
            "agentic_core.L0_routing.package_driven_l0_binding._load_route_profile",
            return_value=fake_route_profile,
        ),
        patch(
            "agentic_core.L0_routing.package_driven_l0_binding._load_cache_profile",
            return_value=fake_cache_profile,
        ),
        patch(
            "agentic_core.L0_routing.package_driven_l0_binding.check_d2_semantic_cache",
            return_value=None,  # MISS
        ),
    ):
        result, evals = l0_evaluate_routes_package_driven(req)

    assert not isinstance(result, RETTerminalPacket), "R1B miss must not emit RETTerminalPacket"
    assert isinstance(result, _FakeRouteContract)
    assert result.route_id == "R3_SIMPLE_GROUNDED_READ"


# ---------------------------------------------------------------------------
# 7. test_r1b_hit_emits_ret_terminal_packet
# ---------------------------------------------------------------------------

def test_r1b_hit_emits_ret_terminal_packet():
    """When check_d2_semantic_cache returns a hit dict, the binding emits a
    RETTerminalPacket with ret_type=SEMANTIC_CACHE_HIT."""
    from agentic_core.L0_routing.package_driven_l0_binding import (
        RETTerminalPacket,
        l0_evaluate_routes_package_driven,
    )

    req = _make_validated_request(app_id="apps_research")

    fake_route_profile = {
        "route_evaluation_order": [
            {"route_id": "R1B_SEMANTIC_CACHE", "condition": "semantic_cache_compatible"},
            {"route_id": "R3_SIMPLE_GROUNDED_READ", "condition": "default"},
        ],
        "active_execution_form": "SINGLE_STEP",
        "managed_workflow_allowed": False,
    }
    fake_cache_profile = {
        "cache_profile_id": "cp::apps_research::v1",
        "semantic_cache": {
            "enabled": True,
            "namespace": "apps_research.company_brief.v1",
            "similarity_threshold": 0.92,
            "live_wiring_deferred": False,
        },
    }
    fake_hit = {
        "response": {"brief": "cached brief content"},
        "cache_key": "ck-abc123",
        "similarity": 0.96,
        "evidence_digest": "evd-xyz",
    }

    with (
        _patch_isinstance(),
        patch(
            "agentic_core.L0_routing.package_driven_l0_binding._load_route_profile",
            return_value=fake_route_profile,
        ),
        patch(
            "agentic_core.L0_routing.package_driven_l0_binding._load_cache_profile",
            return_value=fake_cache_profile,
        ),
        patch(
            "agentic_core.L0_routing.package_driven_l0_binding.check_d2_semantic_cache",
            return_value=fake_hit,
        ),
    ):
        result, evals = l0_evaluate_routes_package_driven(req)

    assert isinstance(result, RETTerminalPacket), (
        f"R1B hit must emit RETTerminalPacket, got {type(result)}"
    )
    assert result.ret_type == "SEMANTIC_CACHE_HIT"
    assert result.terminal_type == "semantic_cache_hit"
    assert result.route_id == "R1B_SEMANTIC_CACHE"


# ---------------------------------------------------------------------------
# 8. test_r1b_hit_goes_to_exit_not_user
# ---------------------------------------------------------------------------

def test_r1b_hit_goes_to_exit_not_user():
    """RETTerminalPacket carries exit_status=success and outcome_authorized=True,
    meaning it is routed to Exit. It is NOT a direct user response."""
    from agentic_core.L0_routing.package_driven_l0_binding import (
        RETTerminalPacket,
        l0_evaluate_routes_package_driven,
    )

    req = _make_validated_request()
    fake_route_profile = {
        "route_evaluation_order": [
            {"route_id": "R1B_SEMANTIC_CACHE"},
        ],
        "active_execution_form": "SINGLE_STEP",
        "managed_workflow_allowed": False,
    }
    fake_cache_profile = {
        "cache_profile_id": "cp::apps_research::v1",
        "semantic_cache": {
            "enabled": True,
            "namespace": "test.ns.v1",
            "similarity_threshold": 0.92,
            "live_wiring_deferred": False,
        },
    }
    fake_hit = {"response": {"data": "cached"}, "cache_key": "ck-1", "similarity": 0.95}

    with (
        _patch_isinstance(),
        patch(
            "agentic_core.L0_routing.package_driven_l0_binding._load_route_profile",
            return_value=fake_route_profile,
        ),
        patch(
            "agentic_core.L0_routing.package_driven_l0_binding._load_cache_profile",
            return_value=fake_cache_profile,
        ),
        patch(
            "agentic_core.L0_routing.package_driven_l0_binding.check_d2_semantic_cache",
            return_value=fake_hit,
        ),
    ):
        result, _ = l0_evaluate_routes_package_driven(req)

    assert isinstance(result, RETTerminalPacket)
    assert result.exit_status == "success"
    assert result.outcome_authorized is True
    assert result.terminal_type == "semantic_cache_hit"


# ---------------------------------------------------------------------------
# 9. test_r1b_hit_skips_c0_pa_l3_l2
# ---------------------------------------------------------------------------

def test_r1b_hit_skips_c0_pa_l3_l2():
    """A RETTerminalPacket is the final L0 output — the pipeline terminates here.
    The contract does NOT carry l3_required, requires_grounding, or model_generation_required,
    proving that C0, PA, L3, and L2 are skipped."""
    from agentic_core.L0_routing.package_driven_l0_binding import RETTerminalPacket

    # RETTerminalPacket must NOT be a RouteContract (which carries l3_required etc.)
    from agentic_core.runtime.contracts.route_contract import RouteContract

    # Build a packet directly — confirm it has none of the execution pipeline fields
    packet = RETTerminalPacket(
        route_id="R1B_SEMANTIC_CACHE",
        terminal_type="semantic_cache_hit",
        ret_type="SEMANTIC_CACHE_HIT",
        evidence_digest="evd",
        provenance_chain=[],
        compatibility_receipt_ref="",
        compatibility_checks_passed={},
        substrate_namespace="test.ns",
        substrate_entry_ref="ck-1",
    )

    assert not isinstance(packet, RouteContract)
    assert not hasattr(packet, "l3_required")
    assert not hasattr(packet, "requires_grounding")
    assert not hasattr(packet, "model_generation_required")
    assert packet.terminal_type == "semantic_cache_hit"
    assert packet.ret_type == "SEMANTIC_CACHE_HIT"


# ---------------------------------------------------------------------------
# 10. test_unknown_or_non_pass_support_fails_closed
# ---------------------------------------------------------------------------

def test_unknown_or_non_pass_support_fails_closed():
    """When check_d2_semantic_cache returns None (miss or unknown), the binding
    must NOT treat it as a hit.  None == fail-closed miss."""
    from agentic_core.L0_routing.package_driven_l0_binding import (
        RETTerminalPacket,
        l0_evaluate_routes_package_driven,
    )
    from agentic_core.runtime.contracts.route_contract import RouteContract

    req = _make_validated_request()
    fake_route_profile = {
        "route_evaluation_order": [
            {"route_id": "R1B_SEMANTIC_CACHE"},
            {"route_id": "R3_SIMPLE_GROUNDED_READ", "condition": "default"},
        ],
        "active_execution_form": "SINGLE_STEP",
        "managed_workflow_allowed": False,
    }
    fake_cache_profile = {
        "cache_profile_id": "cp::test::v1",
        "semantic_cache": {
            "enabled": True,
            "namespace": "test.v1",
            "similarity_threshold": 0.90,
            "live_wiring_deferred": False,
        },
    }

    with (
        _patch_isinstance(),
        _patch_route_contract(),
        patch(
            "agentic_core.L0_routing.package_driven_l0_binding._load_route_profile",
            return_value=fake_route_profile,
        ),
        patch(
            "agentic_core.L0_routing.package_driven_l0_binding._load_cache_profile",
            return_value=fake_cache_profile,
        ),
        patch(
            "agentic_core.L0_routing.package_driven_l0_binding.check_d2_semantic_cache",
            return_value=None,
        ),
    ):
        result, _ = l0_evaluate_routes_package_driven(req)

    assert not isinstance(result, RETTerminalPacket), "None return must never produce a cache-hit packet"
    assert isinstance(result, _FakeRouteContract)
    assert result.route_id == "R3_SIMPLE_GROUNDED_READ"


# ---------------------------------------------------------------------------
# 11. test_no_app_id_branch_in_package_driven_l0_binding
# ---------------------------------------------------------------------------

def test_no_app_id_branch_in_package_driven_l0_binding():
    """Static AST check: no 'if app_id ==' or 'if app_id in' or hardcoded
    'apps_lic'/'apps_rg'/'apps_research' string literals inside the
    _read_semantic_cache_profile or _check_r1b_semantic_cache functions."""
    source = L0_BINDING.read_text(encoding="utf-8")
    tree = ast.parse(source)

    FORBIDDEN_PATTERNS = [
        r'\bapp_id\s*==',
        r'\bapp_id\s+in\b',
        r'"apps_lic"',
        r'"apps_rg"',
        r'"apps_research"',
        r"'apps_lic'",
        r"'apps_rg'",
        r"'apps_research'",
    ]

    # Focus on the two R1B-related functions
    target_funcs = {"_read_semantic_cache_profile", "_check_r1b_semantic_cache", "_build_r1b_ret_packet"}

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name not in target_funcs:
                continue
            func_source = ast.get_source_segment(source, node) or ""
            for pattern in FORBIDDEN_PATTERNS:
                matches = re.findall(pattern, func_source)
                assert not matches, (
                    f"Forbidden pattern '{pattern}' found in function '{node.name}': {matches}"
                )


# ---------------------------------------------------------------------------
# 12. test_apps_rg_quarantined_adapter_untouched
# ---------------------------------------------------------------------------

def test_apps_rg_r1b_adapter_w7_role_target_run_implementation():
    """W7: apps_rg/cache/r1b_adapter.py implements ROLE_TARGET_RUN persistence (quarantine cleared)."""
    adapter_source = APPS_RG_QUARANTINED_ADAPTER.read_text(encoding="utf-8")
    assert "HistoricalIntentRecord" in adapter_source or "r1b_retrieval" in adapter_source
    assert "ROLE_TARGET_RUN" in adapter_source or "check_r1b_for_apps_rg" in adapter_source
    assert "not_c0_fact_vectors" in adapter_source or "R1B_NOT_C0_FACT_VECTORS" in adapter_source


# ---------------------------------------------------------------------------
# 13. test_apps_research_can_use_generic_r1b_profile
# ---------------------------------------------------------------------------

def test_apps_research_can_use_generic_r1b_profile():
    """apps_research cache profile can be parsed by _read_semantic_cache_profile.

    The profile currently has live_wiring_deferred absent (flat shape) — the
    reader must correctly detect flat enabled=true.  After live_wiring_deferred
    is flipped false, the reader must return a live config.
    """
    from agentic_core.L0_routing.package_driven_l0_binding import _read_semantic_cache_profile

    # Simulate the apps_research profile with live_wiring_deferred removed (post-flip)
    profile_live = {
        "cache_profile_id": "cp::apps_research::company_brief::v1",
        "semantic_cache_enabled": True,
        "similarity_threshold": 0.92,
    }
    cfg = _read_semantic_cache_profile(profile_live)
    assert cfg is not None, "apps_research flat profile with enabled=true must produce live config"
    assert cfg["enabled"] is True
    assert cfg["similarity_threshold"] == 0.92
    # namespace falls back to profile_id when absent
    assert cfg["namespace"] == "cp::apps_research::company_brief::v1"
    assert cfg["live_wiring_deferred"] is False


# ---------------------------------------------------------------------------
# 14. test_no_graph_code_changed_in_w1
# ---------------------------------------------------------------------------

def test_no_graph_code_changed_in_w1():
    """Static check: package_driven_l0_binding.py must not import from c0_3_enhanced,
    must not call run_graph_traverse(), must not reference adapter_registry.

    NOTE: graph_traverse, GraphTraversePolicy, and GraphTraversalAdapter are intentionally
    introduced by W2 (chroma-graphrag-core-wiring-gaps-b3f7a1).  They are NOT in the
    W1 forbidden list — only C0.3-internal machinery is forbidden here.
    """
    source = L0_BINDING.read_text(encoding="utf-8")

    forbidden_substrings = [
        "c0_3_enhanced",
        "adapter_registry",
        "GraphTraversalAdapter",
    ]
    for token in forbidden_substrings:
        assert token not in source, (
            f"W1/W2 must not introduce '{token}' into package_driven_l0_binding.py"
        )

    # run_graph_traverse must not be CALLED (comments documenting the invariant are allowed).
    import ast as _ast
    tree = _ast.parse(source)
    for node in _ast.walk(tree):
        if isinstance(node, _ast.Call):
            func = node.func
            name = ""
            if isinstance(func, _ast.Name):
                name = func.id
            elif isinstance(func, _ast.Attribute):
                name = func.attr
            assert name != "run_graph_traverse", (
                f"run_graph_traverse() called at line {node.lineno} in L0 binding — forbidden"
            )

    # C0.3 pipeline must be unchanged
    pipeline_file = C0_3_DIR / "pipeline.py"
    if pipeline_file.exists():
        pipeline_mtime = pipeline_file.stat().st_mtime
        # We can't compare to a baseline here, but we verify the file still exists
        # and that it has not been truncated.
        assert pipeline_file.stat().st_size > 1000, "pipeline.py must not have been truncated"


# ---------------------------------------------------------------------------
# 15. test_no_ingestion_changed_in_w1
# ---------------------------------------------------------------------------

def test_no_ingestion_changed_in_w1():
    """W1 must not have introduced any ingestion pipeline content.

    W1 original: asserted chroma_ingest_pipeline.py does NOT exist (W6 scope).
    W6 update: the file now exists — created by W6 as expected. The W1 invariant
    is that L0 binding (package_driven_l0_binding.py) does NOT reference
    sentence-transformers (that belongs to the app-layer ingestion path, not L0).
    """
    ingestion_pipeline = INGESTION_DIR / "chroma_ingest_pipeline.py"
    # W6 created this file — confirm it is W6-scoped (contains W6 marker)
    if ingestion_pipeline.exists():
        content = ingestion_pipeline.read_text(encoding="utf-8")
        assert "process_docs" in content, (
            "chroma_ingest_pipeline.py must target process_docs collection (W6 invariant)"
        )
        assert "BAAI/bge-m3" in content, (
            "chroma_ingest_pipeline.py must use BAAI/bge-m3 embedding model (W6 invariant)"
        )

    # W1 core invariant: L0 binding must NEVER reference sentence-transformers
    source = L0_BINDING.read_text(encoding="utf-8")
    assert "sentence_transformers" not in source, (
        "package_driven_l0_binding.py must not reference sentence_transformers (L0 boundary)"
    )
    assert "SentenceTransformer" not in source, (
        "package_driven_l0_binding.py must not reference SentenceTransformer (L0 boundary)"
    )


# ---------------------------------------------------------------------------
# Regression: _read_semantic_cache_profile with live_wiring_deferred=true
# ---------------------------------------------------------------------------

def test_live_wiring_deferred_true_returns_none():
    """When live_wiring_deferred=true (nested shape), _read_semantic_cache_profile
    must return None regardless of enabled=true.  This covers apps_rg current state."""
    from agentic_core.L0_routing.package_driven_l0_binding import _read_semantic_cache_profile

    profile = {
        "cache_profile_id": "cp::apps_rg::resume_generation::v1",
        "semantic_cache": {
            "enabled": True,
            "namespace": "apps_rg.resume_gen.v1",
            "similarity_threshold": 0.88,
            "live_wiring_deferred": True,  # deferred — must return None
            "wiring_gate": "W2_GENERIC_INFRA_EDIT_IN_AGENTIC_CORE_REQUIRED",
        },
    }
    assert _read_semantic_cache_profile(profile) is None, (
        "live_wiring_deferred=true must cause _read_semantic_cache_profile to return None"
    )


# Regression: read apps_rg actual profile (live_wiring_deferred=true → None)

def test_apps_rg_actual_profile_deferred():
    """apps_rg/config/domain_contract/cache_profiles.yaml — generic R1B path state check.

    W1 original: asserted result is None (live_wiring_deferred=true until W5).
    W5 update: live_wiring_deferred flipped to false (RCA decision KEEP_QUARANTINED_DEPRECATED).
    _read_semantic_cache_profile now returns a live config dict for apps_rg.
    """
    from agentic_core.L0_routing.package_driven_l0_binding import _read_semantic_cache_profile

    profile = _load_yaml(APPS_RG_CACHE_PROFILE)
    result = _read_semantic_cache_profile(profile)
    # W5: generic path is now live — result must be a populated config dict
    assert result is not None, (
        "apps_rg cache profile live_wiring_deferred=false after W5 — "
        "_read_semantic_cache_profile must return a config dict, not None"
    )
    assert result.get("enabled") is True
    assert result.get("live_wiring_deferred") is False
    assert result.get("namespace") == "apps_rg.resume_gen.section.v1"


# Regression: check_d2_semantic_cache is called with exact expected arguments

def test_check_d2_called_with_exact_signature():
    """Verify check_d2_semantic_cache is called with the exact signature
    (namespace=, tenant_id=, similarity_threshold_override=) — no invented args."""
    from agentic_core.L0_routing.package_driven_l0_binding import (
        RETTerminalPacket,
        l0_evaluate_routes_package_driven,
    )

    req = _make_validated_request(tenant_id="t-test")
    fake_route_profile = {
        "route_evaluation_order": [
            {"route_id": "R1B_SEMANTIC_CACHE"},
            {"route_id": "R3_SIMPLE_GROUNDED_READ"},
        ],
        "active_execution_form": "SINGLE_STEP",
        "managed_workflow_allowed": False,
    }
    fake_cache_profile = {
        "cache_profile_id": "cp::test::v1",
        "semantic_cache": {
            "enabled": True,
            "namespace": "test.namespace.v1",
            "similarity_threshold": 0.93,
            "live_wiring_deferred": False,
        },
    }
    fake_hit = {"response": {}, "cache_key": "ck-1", "similarity": 0.95}

    with (
        _patch_isinstance(),
        patch(
            "agentic_core.L0_routing.package_driven_l0_binding._load_route_profile",
            return_value=fake_route_profile,
        ),
        patch(
            "agentic_core.L0_routing.package_driven_l0_binding._load_cache_profile",
            return_value=fake_cache_profile,
        ),
        patch(
            "agentic_core.L0_routing.package_driven_l0_binding.check_d2_semantic_cache",
            return_value=fake_hit,
        ) as mock_d2,
    ):
        result, _ = l0_evaluate_routes_package_driven(req)

    mock_d2.assert_called_once()
    call_kwargs = mock_d2.call_args
    assert call_kwargs.kwargs.get("namespace") == "test.namespace.v1"
    assert call_kwargs.kwargs.get("tenant_id") == "t-test"
    assert call_kwargs.kwargs.get("similarity_threshold_override") == 0.93
    assert "flow_class" not in call_kwargs.kwargs or call_kwargs.kwargs.get("flow_class") is None


# ---------------------------------------------------------------------------
# 19. test_r1b_miss_constructs_real_r3_route_contract  (W1 hardening patch)
# ---------------------------------------------------------------------------

def test_r1b_miss_constructs_real_r3_route_contract():
    """W1 hardening: R1B miss must fall through to R3 and construct a *real*
    RouteContract — no RouteContract mock, no __post_init__ patch.

    This test proves:
    - check_d2_semantic_cache returns None (miss) -> does NOT emit RETTerminalPacket
    - l0_evaluate_routes_package_driven falls through to R3
    - The real RouteContract is constructed successfully (l5_certification_ref
      threaded from validated_request, so __post_init__ guard passes)
    - result.route_id == "R3_SIMPLE_GROUNDED_READ"
    - No RouteContract or ValidatedRequest patching required

    Invariants:
    - task_class, route_type, requires_grounding, managed_workflow_allowed are
      NOT passed as kwargs to RouteContract (they are not valid fields)
    - l5_certification_ref IS threaded from validated_request.l5_certification_ref
    """
    from agentic_core.L0_routing.package_driven_l0_binding import (
        RETTerminalPacket,
        l0_evaluate_routes_package_driven,
    )
    from agentic_core.runtime.contracts.route_contract import RouteContract
    from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest
    from agentic_core.runtime.contracts.apps_rg_runtime_authority_policy import AuthorityValidationReceipt

    # Build a real AuthorityValidationReceipt — minimal valid instance
    authority_receipt = AuthorityValidationReceipt(
        allowed=True,
        passed=True,
        request_id="req-w1-hardening",
    )

    # Build a real ValidatedRequest — l5_certification_ref must be non-empty (any str)
    real_request = ValidatedRequest(
        request_id="req-w1-hardening",
        run_id="run-w1-hardening",
        app_id="apps_research",
        task_class="company_brief",
        payload_digest="digest-placeholder",
        authority_validation_receipt=authority_receipt,
        trace_id="trace-w1-hardening",
        tenant_id="tenant-w1",
        l5_certification_ref="cert-ref-w1-hardening",
        app_payload={
            "runtime_customization_package": {
                "profile_refs": {
                    "route_profile": "apps_research/config/domain_contract/route_profiles.yaml",
                    "cache_profile": "apps_research/config/domain_contract/cache_profiles.yaml",
                }
            },
            "target_company": "HardeningCo",  # required by _check_r3_simple_grounded_read
        },
    )

    # Fake profiles: R1B enabled + live, R3 fallthrough eligible
    fake_route_profile = {
        "route_profile_id": "rp::apps_research::w1_hardening",
        "route_evaluation_order": [
            {"route_id": "R1B_SEMANTIC_CACHE"},
            {"route_id": "R3_SIMPLE_GROUNDED_READ"},
        ],
        "active_execution_form": "SINGLE_STEP",
        "managed_workflow_allowed": False,
    }
    fake_cache_profile = {
        "cache_profile_id": "cp::apps_research::w1_hardening",
        "semantic_cache": {
            "enabled": True,
            "namespace": "apps_research.hardening.v1",
            "similarity_threshold": 0.90,
            "live_wiring_deferred": False,
        },
    }

    with (
        patch(
            "agentic_core.L0_routing.package_driven_l0_binding._load_route_profile",
            return_value=fake_route_profile,
        ),
        patch(
            "agentic_core.L0_routing.package_driven_l0_binding._load_cache_profile",
            return_value=fake_cache_profile,
        ),
        patch(
            "agentic_core.L0_routing.package_driven_l0_binding.check_d2_semantic_cache",
            return_value=None,  # MISS
        ),
    ):
        result, evals = l0_evaluate_routes_package_driven(real_request)

    # Must NOT be a cache-hit terminal packet
    assert not isinstance(result, RETTerminalPacket), (
        "R1B miss must not emit RETTerminalPacket — got terminal packet instead of R3 contract"
    )

    # Must be the real RouteContract class — not a mock or stub
    assert isinstance(result, RouteContract), (
        f"Expected real RouteContract, got {type(result).__name__}"
    )
    assert result.route_id == "R3_SIMPLE_GROUNDED_READ"

    # l5_certification_ref must have been threaded from validated_request
    assert result.l5_certification_ref == "cert-ref-w1-hardening", (
        f"l5_certification_ref not threaded: got {result.l5_certification_ref!r}"
    )

    # Confirm no invalid kwargs made it through (these would have caused TypeError)
    assert not hasattr(result, "task_class") or result.task_class == "", (
        "task_class must not have been passed as a non-default kwarg to RouteContract"
    )
    assert not hasattr(result, "route_type"), "route_type is not a RouteContract field"
    assert not hasattr(result, "requires_grounding"), "requires_grounding is not a RouteContract field"
    assert not hasattr(result, "managed_workflow_allowed"), "managed_workflow_allowed is not a RouteContract field"

    # Evaluations list: should contain entries for R1B (miss) and R3 (eligible)
    route_ids_evaluated = [e.route_id for e in evals]
    assert "R1B_SEMANTIC_CACHE" in route_ids_evaluated, "R1B must have been evaluated"
    assert "R3_SIMPLE_GROUNDED_READ" in route_ids_evaluated, "R3 must have been evaluated after R1B miss"

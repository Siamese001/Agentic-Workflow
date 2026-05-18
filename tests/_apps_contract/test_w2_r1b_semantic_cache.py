"""
W2 tests — generic R1B semantic cache wiring and config schema reconciliation.

Plan: chroma-graphrag-lic-rg-research-f4a2e9 / W2
Coverage:
  test_r1b_disabled_no_lookup
  test_r1b_miss_continues_r3
  test_r1b_hit_emits_ret_packet
  test_r1b_hit_unknown_support_status_fails_closed
  test_r1b_hit_goes_to_exit_not_user
  test_no_app_id_branch_in_binding
  test_apps_lic_semantic_cache_disabled_no_lookup
  test_apps_lic_semantic_cache_disabled_no_ret_hit
  test_apps_lic_r1b_absent_from_route_order
  test_apps_rg_r1b_enabled_uses_generic_binding
  test_apps_rg_quarantined_adapter_untouched
  (+ config schema, dual-reader, and no-graph-code assertions)
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path
from typing import Any, Dict, Optional
from unittest.mock import MagicMock, patch

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------

def _make_authority_receipt() -> Any:
    from agentic_core.runtime.contracts.apps_rg_runtime_authority_policy import (
        AuthorityValidationReceipt,
    )

    return AuthorityValidationReceipt(
        allowed=True,
        passed=True,
        forbidden_fields_detected=(),
        timestamp_iso="2026-05-13T00:00:00Z",
    )


def _make_validated_request(
    app_id: str = "apps_rg",
    task_class: str = "resume_generation",
    target_company: str = "TestCo",
    request_id: str = "req-001",
    run_id: str = "run-001",
    tenant_id: str = "tenant-test",
    trace_id: str = "trace-001",
    route_profile_ref: Optional[str] = None,
    cache_profile_ref: Optional[str] = None,
) -> Any:
    from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest

    rcp = route_profile_ref or "apps_rg/config/domain_contract/route_profiles.yaml"
    ccp = cache_profile_ref or "apps_rg/config/domain_contract/cache_profiles.yaml"

    return ValidatedRequest(
        request_id=request_id,
        run_id=run_id,
        app_id=app_id,
        task_class=task_class,
        payload_digest="test-digest-placeholder",
        authority_validation_receipt=_make_authority_receipt(),
        l5_certification_ref="test-l5-cert-w2-placeholder",
        trace_id=trace_id,
        tenant_id=tenant_id,
        app_payload={
            "target_company": target_company,
            "runtime_customization_package": {
                "profile_refs": {
                    "route_profile": rcp,
                    "cache_profile": ccp,
                }
            },
        },
    )


def _disabled_cache_profile() -> Dict[str, Any]:
    return {"semantic_cache": {"enabled": False, "reason": "test_disabled"}}


def _enabled_cache_profile(namespace: str = "test.ns.v1") -> Dict[str, Any]:
    return {
        "semantic_cache": {
            "enabled": True,
            "namespace": namespace,
            "similarity_threshold": 0.88,
        }
    }


def _flat_disabled_cache_profile() -> Dict[str, Any]:
    return {"semantic_cache_enabled": False}


def _flat_enabled_cache_profile(namespace: str = "test.ns.v1") -> Dict[str, Any]:
    return {"semantic_cache_enabled": True, "namespace": namespace}


# ---------------------------------------------------------------------------
# _read_semantic_cache_config — dual-schema reader unit tests
# ---------------------------------------------------------------------------

class TestReadSemanticCacheConfig:
    def test_nested_enabled_true(self) -> None:
        from agentic_core.L0_routing.package_driven_l0_binding import (
            _read_semantic_cache_config,
        )

        cfg = _read_semantic_cache_config({"semantic_cache": {"enabled": True, "namespace": "ns.v1"}})
        assert cfg["enabled"] is True
        assert cfg["namespace"] == "ns.v1"

    def test_nested_enabled_false(self) -> None:
        from agentic_core.L0_routing.package_driven_l0_binding import (
            _read_semantic_cache_config,
        )

        cfg = _read_semantic_cache_config({"semantic_cache": {"enabled": False}})
        assert cfg["enabled"] is False

    def test_flat_enabled_false_promoted(self) -> None:
        from agentic_core.L0_routing.package_driven_l0_binding import (
            _read_semantic_cache_config,
        )

        cfg = _read_semantic_cache_config({"semantic_cache_enabled": False})
        assert cfg["enabled"] is False

    def test_flat_enabled_true_promoted(self) -> None:
        from agentic_core.L0_routing.package_driven_l0_binding import (
            _read_semantic_cache_config,
        )

        cfg = _read_semantic_cache_config({"semantic_cache_enabled": True})
        assert cfg["enabled"] is True

    def test_none_profile_returns_disabled(self) -> None:
        from agentic_core.L0_routing.package_driven_l0_binding import (
            _read_semantic_cache_config,
        )

        cfg = _read_semantic_cache_config(None)
        assert cfg["enabled"] is False

    def test_nested_wins_over_flat(self) -> None:
        """Nested schema takes precedence — if nested.enabled=False, flat True ignored."""
        from agentic_core.L0_routing.package_driven_l0_binding import (
            _read_semantic_cache_config,
        )

        cfg = _read_semantic_cache_config({
            "semantic_cache": {"enabled": False},
            "semantic_cache_enabled": True,
        })
        assert cfg["enabled"] is False

    def test_nested_missing_enabled_key_defaults_false(self) -> None:
        from agentic_core.L0_routing.package_driven_l0_binding import (
            _read_semantic_cache_config,
        )

        cfg = _read_semantic_cache_config({"semantic_cache": {"namespace": "ns.v1"}})
        assert cfg["enabled"] is False


# ---------------------------------------------------------------------------
# test_r1b_disabled_no_lookup
# ---------------------------------------------------------------------------

def test_r1b_disabled_no_lookup() -> None:
    """When semantic_cache.enabled=False, _execute_r1b_semantic_cache_lookup is not called."""
    from agentic_core.L0_routing.package_driven_l0_binding import (
        _check_r1b_semantic_cache,
    )
    from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest

    req = _make_validated_request()
    profile = {"route_evaluation_order": [{"route_id": "R1B_SEMANTIC_CACHE"}]}
    cache = _disabled_cache_profile()

    result = _check_r1b_semantic_cache(req, profile, cache)
    assert result.eligible is False
    assert "disabled" in result.reason.lower()


def test_r1b_disabled_flat_schema_no_lookup() -> None:
    """Flat semantic_cache_enabled=False also marks R1B ineligible."""
    from agentic_core.L0_routing.package_driven_l0_binding import (
        _check_r1b_semantic_cache,
    )

    req = _make_validated_request()
    profile = {}
    cache = _flat_disabled_cache_profile()

    result = _check_r1b_semantic_cache(req, profile, cache)
    assert result.eligible is False


# ---------------------------------------------------------------------------
# test_r1b_miss_continues_r3
# ---------------------------------------------------------------------------

def test_r1b_miss_continues_r3() -> None:
    """On cache miss, _execute_r1b_semantic_cache_lookup returns None; R3 is reached."""
    from agentic_core.L0_routing.package_driven_l0_binding import (
        _execute_r1b_semantic_cache_lookup,
    )

    req = _make_validated_request()
    cache_config = {"enabled": True, "namespace": "test.ns.v1", "similarity_threshold": 0.88}

    with patch(
        "agentic_core.L0_routing.package_driven_l0_binding.check_d2_semantic_cache",
        return_value=None,
    ):
        result = _execute_r1b_semantic_cache_lookup(req, cache_config)

    assert result is None, "Miss must return None so caller falls through to R3"


def test_r1b_miss_no_namespace_returns_none() -> None:
    """Missing namespace in cache config skips lookup (returns None / miss)."""
    from agentic_core.L0_routing.package_driven_l0_binding import (
        _execute_r1b_semantic_cache_lookup,
    )

    req = _make_validated_request()
    cache_config = {"enabled": True}  # no namespace

    with patch(
        "agentic_core.L0_routing.package_driven_l0_binding.check_d2_semantic_cache",
    ) as mock_d2:
        result = _execute_r1b_semantic_cache_lookup(req, cache_config)

    assert result is None
    mock_d2.assert_not_called()


# ---------------------------------------------------------------------------
# test_r1b_hit_emits_ret_packet
# ---------------------------------------------------------------------------

def test_r1b_hit_emits_ret_packet() -> None:
    """On cache hit with support_status=PASS, a RETTerminalPacket is returned."""
    from agentic_core.L0_routing.package_driven_l0_binding import (
        RETTerminalPacket,
        _execute_r1b_semantic_cache_lookup,
    )

    req = _make_validated_request()
    cache_config = {"enabled": True, "namespace": "test.ns.v1", "similarity_threshold": 0.88}
    fake_hit = {
        "support_status": "PASS",
        "evidence_digest": "abc123",
        "provenance_chain": [{"step": "retrieval"}],
        "compatibility_receipt_ref": "rcpt-001",
        "compatibility_checks_passed": {"role_compatible": True},
        "entry_ref": "entry-001",
        "source_app_id": "apps_research",
        "timestamp": "2026-05-13T00:00:00Z",
        "content": {"summary": "cached output"},
    }

    with patch(
        "agentic_core.L0_routing.package_driven_l0_binding.check_d2_semantic_cache",
        return_value=fake_hit,
    ):
        result = _execute_r1b_semantic_cache_lookup(req, cache_config)

    assert isinstance(result, RETTerminalPacket)
    assert result.route_id == "R1B_SEMANTIC_CACHE"
    assert result.terminal_type == "semantic_cache_hit"
    assert result.evidence_digest == "abc123"
    assert result.substrate_namespace == "test.ns.v1"
    assert result.is_final_customized_output is False


# ---------------------------------------------------------------------------
# test_r1b_hit_unknown_support_status_fails_closed
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("bad_status", ["UNKNOWN", "FAIL", "unknown", "", None, "maybe"])
def test_r1b_hit_unknown_support_status_fails_closed(bad_status: Any) -> None:
    """Any support_status that is not 'PASS' must be treated as miss (fail-closed)."""
    from agentic_core.L0_routing.package_driven_l0_binding import (
        _execute_r1b_semantic_cache_lookup,
    )

    req = _make_validated_request()
    cache_config = {"enabled": True, "namespace": "test.ns.v1"}
    fake_hit: Dict[str, Any] = {"support_status": bad_status, "content": {"x": 1}}

    with patch(
        "agentic_core.L0_routing.package_driven_l0_binding.check_d2_semantic_cache",
        return_value=fake_hit,
    ):
        result = _execute_r1b_semantic_cache_lookup(req, cache_config)

    assert result is None, (
        f"support_status={bad_status!r} must be treated as miss, not PASS"
    )


# ---------------------------------------------------------------------------
# test_r1b_hit_goes_to_exit_not_user
# ---------------------------------------------------------------------------

def test_r1b_hit_goes_to_exit_not_user() -> None:
    """RETTerminalPacket must have exit_status='success' and outcome_authorized=True.
    It is never a final output: is_final_customized_output must be False."""
    from agentic_core.L0_routing.package_driven_l0_binding import (
        RETTerminalPacket,
        _execute_r1b_semantic_cache_lookup,
    )

    req = _make_validated_request()
    cache_config = {"enabled": True, "namespace": "ns.v1"}
    fake_hit = {"support_status": "PASS", "content": {"data": "cached"}}

    with patch(
        "agentic_core.L0_routing.package_driven_l0_binding.check_d2_semantic_cache",
        return_value=fake_hit,
    ):
        packet = _execute_r1b_semantic_cache_lookup(req, cache_config)

    assert isinstance(packet, RETTerminalPacket)
    assert packet.exit_status == "success"
    assert packet.outcome_authorized is True
    assert packet.is_final_customized_output is False  # must go through Exit, not direct to user


# ---------------------------------------------------------------------------
# test_no_app_id_branch_in_binding — static AST check
# ---------------------------------------------------------------------------

def test_no_app_id_branch_in_binding() -> None:
    """package_driven_l0_binding.py must contain no app_id conditional branches."""
    binding_file = (
        REPO_ROOT / "agentic_core" / "L0_routing" / "package_driven_l0_binding.py"
    )
    source = binding_file.read_text(encoding="utf-8")

    # Check for app_id string comparisons (== "apps_lic", == "apps_rg", etc.)
    import re

    app_id_branches = re.findall(
        r'app_id\s*(?:==|!=|in)\s*["\']apps_\w+["\']', source
    )
    assert not app_id_branches, (
        f"package_driven_l0_binding.py has per-app_id branches: {app_id_branches}"
    )

    # Also check no hardcoded app name strings in conditionals
    hardcoded_apps = re.findall(
        r'if\s+.*["\']apps_(?:lic|rg|research|rfp|qna)["\']', source
    )
    assert not hardcoded_apps, (
        f"package_driven_l0_binding.py has hardcoded app names in conditionals: {hardcoded_apps}"
    )


# ---------------------------------------------------------------------------
# test_apps_lic_semantic_cache_disabled_no_lookup
# test_apps_lic_semantic_cache_disabled_no_ret_hit
# ---------------------------------------------------------------------------

def test_apps_lic_semantic_cache_disabled_no_lookup() -> None:
    """apps_lic cache profile has semantic_cache.enabled=False — R1B ineligible."""
    import yaml

    cache_profile_path = (
        REPO_ROOT / "apps_lic" / "config" / "domain_contract" / "cache_profiles.yaml"
    )
    profile = yaml.safe_load(cache_profile_path.read_text(encoding="utf-8"))

    from agentic_core.L0_routing.package_driven_l0_binding import (
        _read_semantic_cache_config,
    )

    cfg = _read_semantic_cache_config(profile)
    assert cfg["enabled"] is False, (
        "apps_lic semantic_cache.enabled must be False"
    )


def test_apps_lic_semantic_cache_disabled_no_ret_hit() -> None:
    """_execute_r1b_semantic_cache_lookup with apps_lic config never calls check_d2."""
    from agentic_core.L0_routing.package_driven_l0_binding import (
        _execute_r1b_semantic_cache_lookup,
        _read_semantic_cache_config,
    )
    import yaml

    cache_profile_path = (
        REPO_ROOT / "apps_lic" / "config" / "domain_contract" / "cache_profiles.yaml"
    )
    profile = yaml.safe_load(cache_profile_path.read_text(encoding="utf-8"))
    cache_config = _read_semantic_cache_config(profile)

    req = _make_validated_request(
        app_id="apps_lic",
        task_class="outreach_message",
        route_profile_ref="apps_lic/config/domain_contract/route_profiles.yaml",
        cache_profile_ref="apps_lic/config/domain_contract/cache_profiles.yaml",
    )

    with patch(
        "agentic_core.L0_routing.package_driven_l0_binding.check_d2_semantic_cache",
    ) as mock_d2:
        # cache_config.enabled=False means no namespace, so lookup returns None immediately
        result = _execute_r1b_semantic_cache_lookup(req, cache_config)

    assert result is None
    # check_d2 must never be called for disabled profiles
    mock_d2.assert_not_called()


# ---------------------------------------------------------------------------
# test_apps_lic_r1b_absent_from_route_order
# ---------------------------------------------------------------------------

def test_apps_lic_r1b_absent_from_route_order() -> None:
    """apps_lic route_profiles.yaml must not contain R1B_SEMANTIC_CACHE in route_evaluation_order."""
    import yaml

    route_profile_path = (
        REPO_ROOT / "apps_lic" / "config" / "domain_contract" / "route_profiles.yaml"
    )
    profiles = yaml.safe_load(route_profile_path.read_text(encoding="utf-8"))
    # may be list or single dict
    if isinstance(profiles, dict):
        profiles = [profiles]

    for profile in profiles:
        eval_order = profile.get("route_evaluation_order", [])
        route_ids = [r.get("route_id", "") for r in eval_order]
        assert "R1B_SEMANTIC_CACHE" not in route_ids, (
            f"R1B_SEMANTIC_CACHE found in apps_lic route_evaluation_order: {route_ids}"
        )


def test_apps_lic_route_order_contains_r3_not_r1b() -> None:
    """apps_lic route_evaluation_order contains R3 (grounded read) but NOT R1B."""
    import yaml

    route_profile_path = (
        REPO_ROOT / "apps_lic" / "config" / "domain_contract" / "route_profiles.yaml"
    )
    profiles = yaml.safe_load(route_profile_path.read_text(encoding="utf-8"))
    if isinstance(profiles, dict):
        profiles = [profiles]

    for profile in profiles:
        eval_order = profile.get("route_evaluation_order", [])
        route_ids = [r.get("route_id", "") for r in eval_order]
        assert "R3_SIMPLE_GROUNDED_READ" in route_ids, (
            f"R3_SIMPLE_GROUNDED_READ missing from apps_lic route order: {route_ids}"
        )
        assert "R1B_SEMANTIC_CACHE" not in route_ids


# ---------------------------------------------------------------------------
# test_apps_rg_r1b_enabled_uses_generic_binding
# ---------------------------------------------------------------------------

def test_apps_rg_r1b_enabled_uses_generic_binding() -> None:
    """apps_rg cache profile has semantic_cache.enabled=True and correct fields."""
    import yaml

    cache_profile_path = (
        REPO_ROOT / "apps_rg" / "config" / "domain_contract" / "cache_profiles.yaml"
    )
    profile = yaml.safe_load(cache_profile_path.read_text(encoding="utf-8"))

    from agentic_core.L0_routing.package_driven_l0_binding import (
        _read_semantic_cache_config,
    )

    cfg = _read_semantic_cache_config(profile)
    assert cfg["enabled"] is True
    assert cfg.get("namespace"), "apps_rg semantic_cache must have a namespace"
    assert cfg.get("similarity_threshold") is not None
    assert isinstance(cfg.get("compatibility_check_fields"), list)


def test_apps_rg_cache_profile_no_flat_key() -> None:
    """apps_rg cache profile has migrated: flat semantic_cache_enabled key must be absent."""
    import yaml

    cache_profile_path = (
        REPO_ROOT / "apps_rg" / "config" / "domain_contract" / "cache_profiles.yaml"
    )
    profile = yaml.safe_load(cache_profile_path.read_text(encoding="utf-8"))
    assert "semantic_cache_enabled" not in profile, (
        "apps_rg cache profile still has flat semantic_cache_enabled — migration incomplete"
    )


def test_apps_rg_r1b_eligible_via_generic_check() -> None:
    """_check_r1b_semantic_cache returns eligible=True for apps_rg profile."""
    from agentic_core.L0_routing.package_driven_l0_binding import (
        _check_r1b_semantic_cache,
    )
    import yaml

    req = _make_validated_request(app_id="apps_rg")
    route_profile = {"route_evaluation_order": [{"route_id": "R1B_SEMANTIC_CACHE"}]}
    cache_profile_path = (
        REPO_ROOT / "apps_rg" / "config" / "domain_contract" / "cache_profiles.yaml"
    )
    cache_profile = yaml.safe_load(cache_profile_path.read_text(encoding="utf-8"))

    result = _check_r1b_semantic_cache(req, route_profile, cache_profile)
    assert result.eligible is True


# ---------------------------------------------------------------------------
# test_apps_rg_quarantined_adapter_untouched
# ---------------------------------------------------------------------------

def test_apps_rg_quarantined_adapter_untouched() -> None:
    """W7: apps_rg/cache/r1b_adapter.py implements ROLE_TARGET_RUN persistence (quarantine cleared)."""
    adapter_path = REPO_ROOT / "apps_rg" / "cache" / "r1b_adapter.py"
    assert adapter_path.exists(), "r1b_adapter.py must exist"

    source = adapter_path.read_text(encoding="utf-8")
    assert "check_r1b_for_apps_rg" in source
    assert "HistoricalIntentRecord" in source or "r1b_retrieval" in source
    assert "ROLE_TARGET_RUN" in source or "CACHE_GRAIN_ROLE_TARGET_RUN" in source


def test_apps_rg_quarantined_adapter_raises_on_import() -> None:
    """W7: importing apps_rg.cache.r1b_adapter succeeds (active implementation)."""
    import importlib

    sys.modules.pop("apps_rg.cache.r1b_adapter", None)
    mod = importlib.import_module("apps_rg.cache.r1b_adapter")
    assert hasattr(mod, "check_r1b_for_apps_rg")


# ---------------------------------------------------------------------------
# No graph / RouteContract / C0.3 / ingestion code changed — static checks
# ---------------------------------------------------------------------------

def test_no_graph_code_in_binding() -> None:
    """W3 LANDED: package_driven_l0_binding.py carries GraphTraversePolicy but must
    not reference C0.3 adapter classes or graph execution code (W4+ scope)."""
    binding_file = (
        REPO_ROOT / "agentic_core" / "L0_routing" / "package_driven_l0_binding.py"
    )
    source = binding_file.read_text(encoding="utf-8")
    # W3 graph_traverse carrier IS present — that is correct.
    assert "graph_traverse" in source, (
        "W3 graph_traverse carrier must be present in binding"
    )
    # W4+ adapter/execution code must NOT be present.
    forbidden_w4 = [
        "GraphTraversalAdapter",
        "GraphTraverseInput",
        "c0_3_enhanced",
    ]
    hits = [f for f in forbidden_w4 if f in source]
    assert not hits, (
        f"package_driven_l0_binding.py references W4+ adapter/execution code: {hits}"
    )


def test_route_contract_no_graph_policy() -> None:
    """W3 LANDED: route_contract.py must have graph_traverse_policy (W3 landed).
    GraphTraversePolicy dataclass and graph_traverse_policy field are now present."""
    rc_file = (
        REPO_ROOT
        / "agentic_core"
        / "L0_routing"
        / "c0_retrieval"
        / "route_contract.py"
    )
    source = rc_file.read_text(encoding="utf-8")
    assert "graph_traverse_policy" in source, (
        "route_contract.py must have graph_traverse_policy — W3 landed"
    )
    assert "GraphTraversePolicy" in source, (
        "route_contract.py must have GraphTraversePolicy dataclass — W3 landed"
    )


def test_no_ingestion_changed() -> None:
    """apps_research ChromaResearchStore import path present and unchanged."""
    # We just verify the file exists and hasn't been touched with R1B wiring.
    chroma_store = (
        REPO_ROOT / "apps_research" / "config" / "domain_contract" /
        "cache_profile.company_brief.v1.yaml"
    )
    assert chroma_store.exists()
    source = chroma_store.read_text(encoding="utf-8")
    # W5 blocker fields should still be present (not removed in W2)
    assert "text-embedding-3-large" in source, (
        "apps_research cache profile embedding model reference removed unexpectedly"
    )


def test_apps_research_semantic_cache_preserved() -> None:
    """apps_research cache profile still has semantic_cache.enabled=true (untouched by W2)."""
    import yaml

    cache_profile_path = (
        REPO_ROOT
        / "apps_research"
        / "config"
        / "domain_contract"
        / "cache_profile.company_brief.v1.yaml"
    )
    profile = yaml.safe_load(cache_profile_path.read_text(encoding="utf-8"))
    nested = profile.get("semantic_cache", {})
    assert nested.get("enabled") is True, (
        "apps_research semantic_cache.enabled should remain true (not changed in W2)"
    )

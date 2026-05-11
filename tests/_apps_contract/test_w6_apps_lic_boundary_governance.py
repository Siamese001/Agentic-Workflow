"""W6 — apps_lic boundary / governance scan tests.

Scope (per W6 user brief):
  1. No hardcoded apps_lic policy in shared agentic_core spine logic.
  2. apps_lic-specific agentic_core files are thin bindings only.
  3. L0, Exit, cache, send, consent, and L6 policy sourced from
     runtime_customization_package or apps_lic/config/domain_contract/*.
  4. Static scans:
       - direct L4 writes (none allowed in bindings)
       - direct send paths (none in bindings)
       - apps_lic X3 emission only from Exit binding
       - final draft cache return (not from L6)
       - hardcoded apps_lic gate sets in shared core
       - hardcoded apps_lic route policy in shared core

All tests are static / import-level.  No network, no LLM, no filesystem writes.
"""

from __future__ import annotations

import importlib
import inspect
import re
import types
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_REPO_ROOT = Path(__file__).resolve().parents[2]

_BINDING_MODULES = [
    "agentic_core.runtime.u0.apps_lic_u0_adapter",
    "agentic_core.runtime.entry.u0_apps_lic_binding",
    "agentic_core.L0_routing.apps_lic_l0_binding",
    "agentic_core.L1_cognition.apps_lic_l1_binding",
    "agentic_core.L2_execution.apps_lic_l2_binding",
    "agentic_core.L3_orchestration.apps_lic_l3_binding",
    "agentic_core.runtime.c0.apps_lic_c0_binding",
    "agentic_core.prompt_governance.apps_lic_pa_binding",
    "agentic_core.runtime.exit.apps_lic_exit_binding",
    "agentic_core.L6_observability.promotion.apps_lic_promo_binding",
]

_SHARED_NON_BINDING_MODULES = [
    # These must NOT contain hardcoded apps_lic gate sets or route policy
    "agentic_core.L0_routing.config.path_constants",
    "agentic_core.L0_routing.config.model_registry",
]

_FORBIDDEN_DIRECT_L4_PATTERNS = [
    # direct sqlite3 commit, direct db write outside UWG
    re.compile(r"sqlite3\.connect\("),
    re.compile(r"\.execute\(.*INSERT|\.execute\(.*UPDATE", re.IGNORECASE),
    re.compile(r"open\(.*\.db\b"),
]

_FORBIDDEN_SEND_PATTERNS = [
    re.compile(r"\bsmtplib\b"),
    re.compile(r"\brequests\.post\("),
    re.compile(r"\bhttpx\.post\("),
    re.compile(r"\bsendmail\("),
    # Match actual send *calls*, not string literals like 'linkedin_send' in frozensets
    re.compile(r"linkedin\.send\("),
    re.compile(r"smtp.*\.send\(", re.IGNORECASE),
]

_HARDCODED_GATE_PATTERNS = [
    # app_id == 'apps_lic' in non-binding shared logic
    re.compile(r"""app_id\s*==\s*['"]apps_lic['"]"""),
    re.compile(r"""if\s+['"]apps_lic['"]\s+in\b"""),
    re.compile(r"\bAPPS_LIC_GATE_SET\b"),
    re.compile(r"\bAPPS_LIC_ROUTE_POLICY\b"),
]


def _source(module_name: str) -> str:
    """Return the source text of a module."""
    mod = importlib.import_module(module_name)
    src_file = inspect.getfile(mod)
    return Path(src_file).read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# 1. Thin-binding classification
# ---------------------------------------------------------------------------


class TestThinBindingClassification:
    """All apps_lic-named modules in agentic_core must be thin bindings."""

    @pytest.mark.parametrize("module_name", _BINDING_MODULES)
    def test_binding_module_importable(self, module_name: str) -> None:
        """Each binding module must import without error."""
        mod = importlib.import_module(module_name)
        assert isinstance(mod, types.ModuleType)

    @pytest.mark.parametrize("module_name", _BINDING_MODULES)
    def test_binding_module_has_no_hardcoded_gate_conditions(self, module_name: str) -> None:
        """Binding modules must not contain hardcoded app_id == 'apps_lic' gate conditions.

        Bindings MAY declare APP_ID = 'apps_lic' as a module-level identity
        constant (string assignment), but must NOT use it in conditional
        gate logic (if app_id == 'apps_lic': ...).
        """
        src = _source(module_name)
        for pat in _HARDCODED_GATE_PATTERNS:
            assert not pat.search(src), (
                f"{module_name}: found hardcoded gate pattern {pat.pattern!r} "
                f"— move gate logic to apps_lic domain contract"
            )

    @pytest.mark.parametrize("module_name", _BINDING_MODULES)
    def test_binding_module_has_no_direct_send(self, module_name: str) -> None:
        """Binding modules must not contain any direct send path (smtp, requests.post, etc.)."""
        src = _source(module_name)
        for pat in _FORBIDDEN_SEND_PATTERNS:
            assert not pat.search(src), (
                f"{module_name}: found direct send pattern {pat.pattern!r} "
                f"— all send is forbidden in bindings (forbidden_send_modes policy)"
            )

    @pytest.mark.parametrize("module_name", _BINDING_MODULES)
    def test_binding_module_has_no_direct_l4_write(self, module_name: str) -> None:
        """Binding modules must not contain any direct L4 write (sqlite3.connect, raw INSERT, etc.)."""
        src = _source(module_name)
        for pat in _FORBIDDEN_DIRECT_L4_PATTERNS:
            assert not pat.search(src), (
                f"{module_name}: found direct L4 write pattern {pat.pattern!r} "
                f"— all state writes must go through UWG"
            )


# ---------------------------------------------------------------------------
# 2. Hardcoded policy in shared (non-binding) core
# ---------------------------------------------------------------------------


class TestNoHardcodedPolicyInSharedCore:
    """Shared agentic_core modules must not embed apps_lic gate logic or route policy."""

    @pytest.mark.parametrize("module_name", _SHARED_NON_BINDING_MODULES)
    def test_shared_module_has_no_apps_lic_gate_conditions(self, module_name: str) -> None:
        """Shared modules must not gate on apps_lic identity."""
        src = _source(module_name)
        for pat in _HARDCODED_GATE_PATTERNS:
            assert not pat.search(src), (
                f"{module_name}: found hardcoded apps_lic gate {pat.pattern!r} "
                f"in shared core — move to apps_lic domain contract"
            )

    def test_apps_engines_aliases_is_compat_shim_only(self) -> None:
        """apps_engines_aliases.py must be a compat shim (docstring present, no gate logic).

        W7 fix: dead Wave-10 imports removed — module is now importable.
        """
        mod = importlib.import_module("agentic_core.utils.workflow_engines.apps_engines_aliases")
        src_file = inspect.getfile(mod)
        src = Path(src_file).read_text(encoding="utf-8")
        assert "AG-RGGOV-9" in src, (
            "apps_engines_aliases must document itself as a compat shim (AG-RGGOV-9)"
        )
        for pat in _HARDCODED_GATE_PATTERNS:
            assert not pat.search(src), (
                f"apps_engines_aliases: unexpected gate condition {pat.pattern!r}"
            )

    def test_apps_engines_aliases_deleted_wave10_agents_absent(self) -> None:
        """W7 cleanup: 4 deleted Wave-10 agents must no longer be exported from the shim."""
        mod = importlib.import_module("agentic_core.utils.workflow_engines.apps_engines_aliases")
        deleted = [
            "LicCampaignBalanceAgent",
            "DeliverabilityAgent",
            "Hop1ProfileAnalysisAgent",
            "Hop2ResearchAgent",
        ]
        for name in deleted:
            assert not hasattr(mod, name), (
                f"apps_engines_aliases must not export deleted Wave-10 agent {name!r}"
            )

    def test_apps_engines_aliases_live_agents_present(self) -> None:
        """W7 cleanup: 3 live agents must still be exported from the shim."""
        mod = importlib.import_module("agentic_core.utils.workflow_engines.apps_engines_aliases")
        live = ["GovernanceShieldAgent", "LicHealingOrchestrator", "LicReflectionAgent"]
        for name in live:
            assert hasattr(mod, name), (
                f"apps_engines_aliases must still export live agent {name!r}"
            )


# ---------------------------------------------------------------------------
# 3. Policy sourced from runtime_customization_package / domain_contract
# ---------------------------------------------------------------------------


class TestPolicySourcedFromDomainContract:
    """L0, Exit, cache, send, consent policy must be sourced from config, not hardcoded."""

    def test_runtime_customization_package_config_exists(self) -> None:
        """apps_lic runtime_customization_package config file must exist on disk."""
        cfg = _REPO_ROOT / "apps_lic" / "config" / "domain_contract" / \
            "runtime_customization_package.outreach_message.v1.json"
        assert cfg.exists(), f"Missing: {cfg}"

    def test_runtime_customization_package_has_forbidden_send_modes(self) -> None:
        """runtime_customization_package must declare all 7 forbidden send modes."""
        import json
        cfg = _REPO_ROOT / "apps_lic" / "config" / "domain_contract" / \
            "runtime_customization_package.outreach_message.v1.json"
        data = json.loads(cfg.read_text(encoding="utf-8"))
        modes = set(data["policies"]["forbidden_send_modes"])
        required = {
            "send_now", "auto_send", "connector_send", "email_outbox_send",
            "linkedin_send", "sms_send", "external_http_post",
        }
        assert required == modes, (
            f"runtime_customization_package forbidden_send_modes mismatch; "
            f"expected {sorted(required)}, got {sorted(modes)}"
        )

    def test_runtime_customization_package_has_cache_bypass_policy(self) -> None:
        """runtime_customization_package must declare cache bypass policy for final drafts."""
        import json
        cfg = _REPO_ROOT / "apps_lic" / "config" / "domain_contract" / \
            "runtime_customization_package.outreach_message.v1.json"
        data = json.loads(cfg.read_text(encoding="utf-8"))
        cbp = data["policies"]["cache_bypass_policy"]
        assert cbp["r1a_exact_cache_bypassed_for_final_drafts"] is True, (
            "R1A cache must be bypassed for final drafts"
        )
        assert cbp["r1b_semantic_cache_bypassed_for_final_drafts"] is True, (
            "R1B cache must be bypassed for final drafts"
        )

    def test_l0_route_profile_config_exists(self) -> None:
        """apps_lic L0 route profile config file must exist on disk."""
        cfg = _REPO_ROOT / "apps_lic" / "config" / "domain_contract" / \
            "l0_route_profile.outreach_message.v1.json"
        assert cfg.exists(), f"Missing: {cfg}"

    def test_exit_profile_config_exists(self) -> None:
        """apps_lic Exit profile config file must exist on disk."""
        cfg = _REPO_ROOT / "apps_lic" / "config" / "domain_contract" / \
            "exit_profile.outreach_message.v1.json"
        assert cfg.exists(), f"Missing: {cfg}"

    def test_final_draft_cache_policy_config_exists(self) -> None:
        """apps_lic final draft cache policy config file must exist on disk."""
        cfg = _REPO_ROOT / "apps_lic" / "config" / "domain_contract" / \
            "final_draft_cache_policy.outreach_message.v1.json"
        assert cfg.exists(), f"Missing: {cfg}"

    def test_l0_binding_reads_cache_eligibility_not_hardcoded_string(self) -> None:
        """L0 binding must derive cache eligibility via function, not a bare hardcoded string block."""
        src = _source("agentic_core.L0_routing.apps_lic_l0_binding")
        assert "_derive_cache_eligibility" in src, (
            "L0 binding must call _derive_cache_eligibility — no inline hardcoded cache dict"
        )

    def test_exit_binding_reads_exit_profile_from_config_path(self) -> None:
        """Exit binding must reference _EXIT_PROFILE_PATH (sourced from domain_contract)."""
        src = _source("agentic_core.runtime.exit.apps_lic_exit_binding")
        assert "_EXIT_PROFILE_PATH" in src, (
            "Exit binding must use _EXIT_PROFILE_PATH constant pointing to domain_contract"
        )
        assert "apps_lic/config/domain_contract/exit_profile" in src, (
            "Exit binding must source exit_profile from apps_lic/config/domain_contract/"
        )

    def test_exit_binding_reads_cache_policy_from_config_path(self) -> None:
        """Exit binding must reference _CACHE_POLICY_PATH (sourced from domain_contract)."""
        src = _source("agentic_core.runtime.exit.apps_lic_exit_binding")
        assert "_CACHE_POLICY_PATH" in src, (
            "Exit binding must use _CACHE_POLICY_PATH constant pointing to domain_contract"
        )
        assert "apps_lic/config/domain_contract/final_draft_cache_policy" in src, (
            "Exit binding must source cache policy from apps_lic/config/domain_contract/"
        )

    def test_u0_adapter_reads_field_map_from_apps_lic_contracts(self) -> None:
        """U0 adapter field map must be sourced from apps_lic/contracts/, not hardcoded."""
        src = _source("agentic_core.runtime.u0.apps_lic_u0_adapter")
        assert "apps_lic_ingress_field_map.v1.yaml" in src, (
            "U0 adapter must source its field map from apps_lic/contracts/"
        )

    def test_ingress_payload_forbidden_send_modes_default_has_all_7(self) -> None:
        """W7 fix: AppsLicIngressPayload.forbidden_send_modes default must list all 7 modes.

        Prior to W7, the default had only 3 modes. This was misleading and could
        break fixtures or confuse future implementers even though enforcement at
        the Pydantic validation layer was always correct.
        """
        from agentic_core.runtime.contracts.apps_lic_ingress_payload import (
            AppsLicIngressPayload,
        )
        payload = AppsLicIngressPayload()
        required = {
            "send_now",
            "auto_send",
            "connector_send",
            "email_outbox_send",
            "linkedin_send",
            "sms_send",
            "external_http_post",
        }
        actual = set(payload.forbidden_send_modes)
        assert actual == required, (
            f"AppsLicIngressPayload.forbidden_send_modes default must contain all 7 modes; "
            f"missing: {sorted(required - actual)}, extra: {sorted(actual - required)}"
        )


# ---------------------------------------------------------------------------
# 4. X3 emission gating — only from Exit binding
# ---------------------------------------------------------------------------


class TestX3EmissionGating:
    """X3 emission must occur only in the apps_lic Exit binding."""

    def test_x3_emission_in_exit_binding(self) -> None:
        """Exit binding must contain build_x3_packet call (exactly one X3 emission path)."""
        src = _source("agentic_core.runtime.exit.apps_lic_exit_binding")
        assert "build_x3_packet" in src, (
            "Exit binding must call build_x3_packet — exactly one X3 emission path"
        )

    def test_no_x3_emission_in_l6_binding(self) -> None:
        """L6 promo binding must NOT emit X3 packets."""
        src = _source("agentic_core.L6_observability.promotion.apps_lic_promo_binding")
        assert "build_x3_packet" not in src, (
            "L6 binding must not call build_x3_packet — X3 is Exit-only"
        )
        assert "X3AllowPacket" not in src and "X3DenyPacket" not in src, (
            "L6 binding must not construct X3 packets — X3 is Exit-only"
        )

    def test_no_x3_emission_in_l0_binding(self) -> None:
        """L0 binding must NOT emit X3 packets."""
        src = _source("agentic_core.L0_routing.apps_lic_l0_binding")
        assert "build_x3_packet" not in src, "L0 must not emit X3"

    def test_no_x3_emission_in_l3_binding(self) -> None:
        """L3 binding must NOT emit X3 packets."""
        src = _source("agentic_core.L3_orchestration.apps_lic_l3_binding")
        assert "build_x3_packet" not in src, "L3 must not emit X3"


# ---------------------------------------------------------------------------
# 5. L4 write authority — bindings must not claim write authority
# ---------------------------------------------------------------------------


class TestL4WriteAuthority:
    """apps_lic bindings must set is_uwg_write_authority=False."""

    def test_l2_binding_sets_no_write_authority(self) -> None:
        """L2 binding must assert is_uwg_write_authority=False."""
        src = _source("agentic_core.L2_execution.apps_lic_l2_binding")
        assert "is_uwg_write_authority=False" in src, (
            "L2 binding must explicitly set is_uwg_write_authority=False"
        )

    def test_exit_binding_sets_no_write_authority(self) -> None:
        """Exit binding must assert is_uwg_write_authority=False."""
        src = _source("agentic_core.runtime.exit.apps_lic_exit_binding")
        assert "is_uwg_write_authority=False" in src, (
            "Exit binding must set is_uwg_write_authority=False"
        )

    def test_l6_binding_no_direct_l4_writes(self) -> None:
        """L6 promo binding must have _verify_no_direct_l4_writes function (static scan hook)."""
        src = _source("agentic_core.L6_observability.promotion.apps_lic_promo_binding")
        assert "_verify_no_direct_l4_writes" in src, (
            "L6 binding must export _verify_no_direct_l4_writes static scan hook"
        )

    def test_l6_binding_calls_verify_no_direct_l4_writes(self) -> None:
        """L6 _verify_no_direct_l4_writes must return True (no direct writes)."""
        from agentic_core.L6_observability.promotion.apps_lic_promo_binding import (
            _verify_no_direct_l4_writes,
        )
        assert _verify_no_direct_l4_writes() is True

    def test_l6_binding_no_send_path(self) -> None:
        """L6 _verify_no_send_path must return True."""
        from agentic_core.L6_observability.promotion.apps_lic_promo_binding import (
            _verify_no_send_path,
        )
        assert _verify_no_send_path() is True

    def test_l6_binding_no_cache_return(self) -> None:
        """L6 _verify_no_cache_return must return True."""
        from agentic_core.L6_observability.promotion.apps_lic_promo_binding import (
            _verify_no_cache_return,
        )
        assert _verify_no_cache_return() is True

    def test_l6_binding_no_exit_x3_emission(self) -> None:
        """L6 _verify_no_exit_x3_emission must return True."""
        from agentic_core.L6_observability.promotion.apps_lic_promo_binding import (
            _verify_no_exit_x3_emission,
        )
        assert _verify_no_exit_x3_emission() is True


# ---------------------------------------------------------------------------
# 6. Final draft cache — not returned from L0 or L6
# ---------------------------------------------------------------------------


class TestFinalDraftCacheScan:
    """Final draft cache must not be returned by L0 or L6 — bypass only."""

    def test_l0_sets_final_draft_cache_bypass_flags(self) -> None:
        """L0 _derive_cache_eligibility must set both r1a and r1b bypass flags True."""
        from agentic_core.L0_routing.apps_lic_l0_binding import _derive_cache_eligibility
        result = _derive_cache_eligibility("R4_MANAGED_DRAFT")
        assert result["final_draft_r1a_bypass"] is True, (
            "L0 must set final_draft_r1a_bypass=True for all non-fallback routes"
        )
        assert result["final_draft_r1b_bypass"] is True, (
            "L0 must set final_draft_r1b_bypass=True for all non-fallback routes"
        )

    def test_l0_sets_final_draft_cache_bypass_for_fallback(self) -> None:
        """L0 must also bypass final draft cache on R5 fallback routes."""
        from agentic_core.L0_routing.apps_lic_l0_binding import _derive_cache_eligibility
        result = _derive_cache_eligibility("R5_FALLBACK")
        assert result["final_draft_r1a_bypass"] is True
        assert result["final_draft_r1b_bypass"] is True

    def test_exit_binding_reads_cache_policy_from_runtime_pkg(self) -> None:
        """Exit binding cache_bypass_receipt must list policy_source as runtime pkg or config."""
        src = _source("agentic_core.runtime.exit.apps_lic_exit_binding")
        assert "runtime_customization_package.cache_bypass_policy" in src, (
            "Exit binding must cite runtime_customization_package.cache_bypass_policy "
            "as the policy_source for cache bypass"
        )

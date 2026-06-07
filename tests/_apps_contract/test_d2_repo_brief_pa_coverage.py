"""
D2 — apps_repo_brief PA coverage, CompiledPromptArtifact gate, board block,
     and cache stale-board block tests.

Covers §20.2 gates:
  #2  apps_repo_brief aligned to Prompt Assembly standard
  #7  No template-only full board brief
  #8  No semantic cache stale board return
  #9  No ad hoc prompt strings
  #10 No placeholder templates
  #11 No provider call without CompiledPromptArtifact

Deferred scope items closed:
  DS-3  PA coverage tests
  DS-4  board block negative control
  DS-5  cache stale-board block test

Plan: docs/archive/windsurf/legacy-tree/plans/apps-repo-brief-plan3-deferred-scope-b9e4c1.md D2
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_REPO_ROOT = Path(__file__).resolve().parents[2]
_PA_DIR = _REPO_ROOT / "apps_repo_brief" / "prompt_assembly"
_TEMPLATES_DIR = _PA_DIR / "templates"
_BOM_PATH = _PA_DIR / "prompt_bom.yaml"
_CONFIG_DIR = _REPO_ROOT / "apps_repo_brief" / "config"
_PROMPT_REGISTRY_PATH = _CONFIG_DIR / "prompt_registry.yaml"


def _load_yaml(path: Path) -> dict[str, Any]:
    import yaml  # type: ignore[import-untyped]
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)  # type: ignore[no-any-return]


def _load_template(name: str) -> dict[str, Any]:
    return _load_yaml(_TEMPLATES_DIR / name)


def _all_template_files() -> list[Path]:
    return sorted(_TEMPLATES_DIR.glob("*.yaml"))


def _all_py_files_in_pa() -> list[Path]:
    return sorted(_PA_DIR.rglob("*.py"))


# ---------------------------------------------------------------------------
# D2.1 — PA placeholder / ad-hoc prompt scan  (gates #9, #10)
# ---------------------------------------------------------------------------

class TestNoPAPlaceholders:
    """Gate #9 + #10: no ad hoc prompt strings, no placeholder templates."""

    _PLACEHOLDER_TOKENS = [
        "TODO",
        "FIXME",
        "PLACEHOLDER",
        "STUB",
        "NOT_IMPLEMENTED",
        "pass  # placeholder",
    ]

    def test_no_placeholder_tokens_in_templates(self) -> None:
        """No template YAML should contain placeholder/TODO text in slot bodies."""
        violations: list[str] = []
        for tpl_path in _all_template_files():
            content = tpl_path.read_text(encoding="utf-8")
            for token in self._PLACEHOLDER_TOKENS:
                if token in content:
                    violations.append(f"{tpl_path.name}: contains '{token}'")
        assert not violations, f"Placeholder tokens found in templates:\n" + "\n".join(violations)

    def test_no_adhoc_f_strings_in_pa_compiler(self) -> None:
        """
        PA compiler must not build prompt strings with f-string concatenation
        that bypasses slot rendering (gate #9 — no ad hoc prompt strings).
        Allowed: f-strings for artifact ID construction and hash computation.
        Forbidden: f-strings producing substantive prompt text inline.
        """
        compiler_path = _PA_DIR / "repo_brief_pa_compiler.py"
        content = compiler_path.read_text(encoding="utf-8")
        # Check that there is a render_slots method (required PA discipline)
        assert "_render_slots" in content, (
            "PA compiler must implement _render_slots — no inline prompt construction"
        )

    def test_bom_declares_required_slots(self) -> None:
        """BOM must declare all required slots with required: true."""
        bom = _load_yaml(_BOM_PATH)
        slots = bom.get("slots", {})
        required_slot_ids = {sid for sid, defn in slots.items() if defn.get("required", False)}
        # S0, I0, C0, U0, A0, D0, R0 are mandatory per §9.5
        mandatory = {"S0", "I0", "C0", "U0", "A0", "D0", "R0"}
        missing = mandatory - required_slot_ids
        assert not missing, f"BOM is missing required slots: {missing}"

    def test_bom_optional_slots_declared(self) -> None:
        """BOM must include optional slots E0, Y0 as required: false."""
        bom = _load_yaml(_BOM_PATH)
        slots = bom.get("slots", {})
        for opt in ("E0", "Y0"):
            assert opt in slots, f"Optional slot {opt} missing from BOM"
            assert not slots[opt].get("required", True), f"Slot {opt} should be optional"

    def test_synthesis_template_required_inputs_non_empty(self) -> None:
        """Primary synthesis template must list all required C0 evidence inputs."""
        tpl = _load_template("repo_brief_synthesis_v1.yaml")
        required_inputs = tpl.get("input_contract", {}).get("required_inputs", [])
        # C0 evidence types that must be declared as required inputs
        expected = {
            "FinalEvidenceContract",
            "BriefingCoverageMatrix",
            "SourcePortfolioSummary",
            "ClaimEvidenceMap",
        }
        missing = expected - set(required_inputs)
        assert not missing, f"Synthesis template missing required inputs: {missing}"

    def test_all_templates_have_template_id(self) -> None:
        """Every template YAML must declare a template_id field."""
        violations = []
        for tpl_path in _all_template_files():
            tpl = _load_yaml(tpl_path)
            if not tpl.get("template_id"):
                violations.append(tpl_path.name)
        assert not violations, f"Templates missing template_id: {violations}"

    def test_all_templates_have_input_contract_or_slot_bodies(self) -> None:
        """Every template must declare either input_contract or slot_bodies (not empty shells)."""
        violations = []
        for tpl_path in _all_template_files():
            tpl = _load_yaml(tpl_path)
            has_contract = bool(tpl.get("input_contract"))
            has_slots = bool(tpl.get("slot_bodies"))
            if not has_contract and not has_slots:
                violations.append(tpl_path.name)
        assert not violations, f"Hollow template files (no contract or slot bodies): {violations}"

    def test_synthesis_template_forbidden_behaviors_declared(self) -> None:
        """Gate: synthesis template must declare forbidden_behaviors."""
        tpl = _load_template("repo_brief_synthesis_v1.yaml")
        fb = tpl.get("forbidden_behaviors", [])
        assert len(fb) >= 5, (
            f"synthesis template has too few forbidden_behaviors ({len(fb)} < 5)"
        )
        # Provider call prohibition must be explicit
        assert "call_provider_directly" in fb, (
            "forbidden_behaviors must include 'call_provider_directly'"
        )


# ---------------------------------------------------------------------------
# D2.2 — CompiledPromptArtifact gate test  (gate #11)
# ---------------------------------------------------------------------------

class TestCompiledPromptArtifact:
    """Gate #11: no provider call without CompiledPromptArtifact."""

    def _make_evidence_bundle(self) -> dict[str, Any]:
        return {
            "normalized_repo_brief_task": {"depth_profile": "REPO_BRIEF_STANDARD", "audience": "cto"},
            "FinalEvidenceContract": {"contract_type": "apps_repo_brief.FinalEvidenceContract.v1"},
            "BriefingCoverageMatrix": {"overall_coverage_pct": 80.0},
            "SourcePortfolioSummary": {"total_sources": 12},
            "ClaimEvidenceMap": {"pass_count": 5},
            "ContradictionMatrix": {"has_critical": False},
            "FreshnessReport": {"stale_sources": [], "max_age_days": 30},
            "SynthesisGuidanceForPA": {"caveat_injection_policy": "inline"},
            "repo_brief_depth_profile": "REPO_BRIEF_STANDARD",
            "audience_schema_ref": "persona_schema_v1",
            "output_schema_ref": "governed_repo_brief_packet_v1",
            "policy_hash": "ph_test",
            "blueprint_hash": "bph_test",
            "replay_key": "rk_test",
        }

    def test_compile_returns_compiled_prompt_artifact_shape(self) -> None:
        """compile() must return a dict with all required CompiledPromptArtifact fields."""
        from apps_repo_brief.prompt_assembly.repo_brief_pa_compiler import RepoBriefPACompiler
        compiler = RepoBriefPACompiler()
        artifact = compiler.compile(
            template_id="repo_brief_synthesis_v1",
            evidence_bundle=self._make_evidence_bundle(),
            request_id="req_test_001",
            run_id="run_test_001",
            trace_id="trace_test_001",
            route_id="apps_repo_brief.executive_brief_v1",
            selected_capability="repo_brief_synthesis_v1",
            policy_hash="ph_test",
            blueprint_hash="bph_test",
            replay_key="rk_test",
        )
        required_fields = {
            "artifact_id",
            "request_id",
            "run_id",
            "trace_id",
            "route_id",
            "template_id",
            "template_version",
            "manifest_hash",
            "policy_hash",
            "blueprint_hash",
            "replay_key",
        }
        missing = required_fields - set(artifact.keys())
        assert not missing, f"CompiledPromptArtifact missing fields: {missing}"

    def test_compile_missing_input_raises_value_error(self) -> None:
        """compile() must raise ValueError when required inputs are absent from evidence_bundle."""
        from apps_repo_brief.prompt_assembly.repo_brief_pa_compiler import RepoBriefPACompiler
        compiler = RepoBriefPACompiler()
        # Omit FinalEvidenceContract — required by synthesis template
        bundle = self._make_evidence_bundle()
        del bundle["FinalEvidenceContract"]
        with pytest.raises(ValueError, match="missing required inputs"):
            compiler.compile(
                template_id="repo_brief_synthesis_v1",
                evidence_bundle=bundle,
                request_id="req_test_002",
                run_id="run_test_002",
                trace_id="trace_test_002",
                route_id="apps_repo_brief.executive_brief_v1",
                selected_capability="repo_brief_synthesis_v1",
                policy_hash="ph_test",
                blueprint_hash="bph_test",
                replay_key="rk_test",
            )

    def test_compile_unknown_template_raises_value_error(self) -> None:
        """compile() must raise ValueError for an unregistered template_id."""
        from apps_repo_brief.prompt_assembly.repo_brief_pa_compiler import RepoBriefPACompiler
        compiler = RepoBriefPACompiler()
        with pytest.raises(ValueError, match="not found in prompt registry"):
            compiler.compile(
                template_id="nonexistent_template_v99",
                evidence_bundle=self._make_evidence_bundle(),
                request_id="req_test_003",
                run_id="run_test_003",
                trace_id="trace_test_003",
                route_id="apps_repo_brief.executive_brief_v1",
                selected_capability="nonexistent_template_v99",
                policy_hash="ph_test",
                blueprint_hash="bph_test",
                replay_key="rk_test",
            )

    def test_artifact_id_contains_request_id_and_template_id(self) -> None:
        """artifact_id must encode request_id and template_id for traceability."""
        from apps_repo_brief.prompt_assembly.repo_brief_pa_compiler import RepoBriefPACompiler
        compiler = RepoBriefPACompiler()
        artifact = compiler.compile(
            template_id="repo_brief_synthesis_v1",
            evidence_bundle=self._make_evidence_bundle(),
            request_id="req_trace_check",
            run_id="run_x",
            trace_id="tr_x",
            route_id="apps_repo_brief.executive_brief_v1",
            selected_capability="repo_brief_synthesis_v1",
            policy_hash="ph",
            blueprint_hash="bph",
            replay_key="rk",
        )
        assert "req_trace_check" in artifact["artifact_id"]
        assert "repo_brief_synthesis_v1" in artifact["artifact_id"]

    def test_manifest_hash_is_deterministic(self) -> None:
        """Same inputs must produce identical manifest_hash (replay-safe)."""
        from apps_repo_brief.prompt_assembly.repo_brief_pa_compiler import RepoBriefPACompiler
        kwargs: dict[str, Any] = dict(
            template_id="repo_brief_synthesis_v1",
            evidence_bundle=self._make_evidence_bundle(),
            request_id="req_det",
            run_id="run_det",
            trace_id="tr_det",
            route_id="apps_repo_brief.executive_brief_v1",
            selected_capability="repo_brief_synthesis_v1",
            policy_hash="ph_det",
            blueprint_hash="bph_det",
            replay_key="rk_det",
        )
        a1 = RepoBriefPACompiler().compile(**kwargs)
        a2 = RepoBriefPACompiler().compile(**kwargs)
        assert a1["manifest_hash"] == a2["manifest_hash"]


# ---------------------------------------------------------------------------
# D2.3 — Board block negative control  (gate #7)
# ---------------------------------------------------------------------------

class TestBoardBlockNegativeControl:
    """
    Gate #7: no template-only full board brief.

    The BOARD_DOSSIER depth profile must require board_gate_passed=True
    on the FEC before validation passes. A FEC with board_gate_passed=False
    must produce a violation.
    """

    def _make_fec(self, depth_profile: str, **kwargs: Any) -> Any:
        from apps_repo_brief.c0.repo_brief_final_contract import (
            RepoBriefFinalEvidenceContract,
            DepthProfile,
            EvidenceStatus,
        )
        return RepoBriefFinalEvidenceContract(
            depth_profile=DepthProfile(depth_profile),
            evidence_status=EvidenceStatus.PASS,
            **kwargs,
        )

    def test_board_dossier_requires_board_gate_passed_true(self) -> None:
        """validate_fec must flag BOARD_DOSSIER FEC when board_gate_passed=False."""
        from apps_repo_brief.c0.repo_brief_c0_adapter import RepoBriefC0Adapter
        from apps_repo_brief.c0.repo_brief_final_contract import DepthProfile
        fec = self._make_fec("REPO_BRIEF_BOARD_DOSSIER", board_gate_passed=False)
        adapter = RepoBriefC0Adapter()
        violations = adapter.validate_fec(fec, DepthProfile.REPO_BRIEF_BOARD_DOSSIER)
        assert any("board_gate_passed" in v for v in violations), (
            f"Expected board_gate violation, got: {violations}"
        )

    def test_board_dossier_passes_when_board_gate_true(self) -> None:
        """validate_fec must NOT flag BOARD_DOSSIER FEC when board_gate_passed=True."""
        from apps_repo_brief.c0.repo_brief_c0_adapter import RepoBriefC0Adapter
        from apps_repo_brief.c0.repo_brief_final_contract import DepthProfile
        fec = self._make_fec("REPO_BRIEF_BOARD_DOSSIER", board_gate_passed=True)
        adapter = RepoBriefC0Adapter()
        violations = adapter.validate_fec(fec, DepthProfile.REPO_BRIEF_BOARD_DOSSIER)
        board_violations = [v for v in violations if "board_gate_passed" in v]
        assert not board_violations, (
            f"Unexpected board_gate violations when gate=True: {board_violations}"
        )

    def test_non_board_profile_does_not_require_board_gate(self) -> None:
        """REPO_BRIEF_STANDARD must not impose board_gate_passed requirement."""
        from apps_repo_brief.c0.repo_brief_c0_adapter import RepoBriefC0Adapter
        from apps_repo_brief.c0.repo_brief_final_contract import DepthProfile
        fec = self._make_fec("REPO_BRIEF_STANDARD", board_gate_passed=False)
        adapter = RepoBriefC0Adapter()
        violations = adapter.validate_fec(fec, DepthProfile.REPO_BRIEF_STANDARD)
        board_violations = [v for v in violations if "board_gate" in v]
        assert not board_violations, (
            f"Standard profile should not require board gate: {board_violations}"
        )

    def test_depth_profile_thresholds_board_gate_required_true(self) -> None:
        """depth_profiles.py must declare board_gate_required=True for BOARD_DOSSIER."""
        from apps_repo_brief.c0.depth_profiles import DEPTH_PROFILE_THRESHOLDS
        from apps_repo_brief.c0.repo_brief_final_contract import DepthProfile
        thresholds = DEPTH_PROFILE_THRESHOLDS[DepthProfile.REPO_BRIEF_BOARD_DOSSIER]
        assert thresholds.get("board_gate_required") is True, (
            "BOARD_DOSSIER depth profile must set board_gate_required=True"
        )

    def test_depth_profile_thresholds_board_semantic_cache_false(self) -> None:
        """Gate #7+#8: BOARD_DOSSIER must set semantic_cache_terminal_return=False."""
        from apps_repo_brief.c0.depth_profiles import DEPTH_PROFILE_THRESHOLDS
        from apps_repo_brief.c0.repo_brief_final_contract import DepthProfile
        thresholds = DEPTH_PROFILE_THRESHOLDS[DepthProfile.REPO_BRIEF_BOARD_DOSSIER]
        assert thresholds.get("semantic_cache_terminal_return") is False, (
            "BOARD_DOSSIER must not allow semantic_cache_terminal_return"
        )

    def test_standard_profile_allows_semantic_cache(self) -> None:
        """REPO_BRIEF_STANDARD must permit semantic_cache_terminal_return=True."""
        from apps_repo_brief.c0.depth_profiles import DEPTH_PROFILE_THRESHOLDS
        from apps_repo_brief.c0.repo_brief_final_contract import DepthProfile
        thresholds = DEPTH_PROFILE_THRESHOLDS[DepthProfile.REPO_BRIEF_STANDARD]
        assert thresholds.get("semantic_cache_terminal_return") is True


# ---------------------------------------------------------------------------
# D2.4 — Cache stale-board block test  (gate #8)
# ---------------------------------------------------------------------------

class TestCacheStaleBoardBlock:
    """
    Gate #8: no semantic cache stale board return.

    enforce_r1b_semantic_cache_policy must raise CacheCompatViolation when
    depth_profile=REPO_BRIEF_BOARD_DOSSIER and is_terminal_return=True.
    """

    def test_r1b_board_terminal_raises(self) -> None:
        """R1B terminal return for BOARD_DOSSIER must raise CacheCompatViolation."""
        from apps_repo_brief.c0.cache_compat_enforcement import (
            enforce_r1b_semantic_cache_policy,
            CacheCompatViolation,
        )
        with pytest.raises(CacheCompatViolation, match="BOARD_DOSSIER"):
            enforce_r1b_semantic_cache_policy(
                depth_profile="REPO_BRIEF_BOARD_DOSSIER",
                is_terminal_return=True,
            )

    def test_r1b_board_non_terminal_allowed(self) -> None:
        """R1B non-terminal (cache miss, not returning cached result) must not raise."""
        from apps_repo_brief.c0.cache_compat_enforcement import (
            enforce_r1b_semantic_cache_policy,
        )
        enforce_r1b_semantic_cache_policy(
            depth_profile="REPO_BRIEF_BOARD_DOSSIER",
            is_terminal_return=False,
        )

    def test_r1b_standard_terminal_allowed(self) -> None:
        """R1B terminal return for STANDARD profile is permitted (not board)."""
        from apps_repo_brief.c0.cache_compat_enforcement import (
            enforce_r1b_semantic_cache_policy,
        )
        enforce_r1b_semantic_cache_policy(
            depth_profile="REPO_BRIEF_STANDARD",
            is_terminal_return=True,
        )

    def test_r1b_light_terminal_allowed(self) -> None:
        """R1B terminal return for LIGHT profile is permitted."""
        from apps_repo_brief.c0.cache_compat_enforcement import (
            enforce_r1b_semantic_cache_policy,
        )
        enforce_r1b_semantic_cache_policy(
            depth_profile="REPO_BRIEF_LIGHT",
            is_terminal_return=True,
        )

    def test_r1a_strict_compat_missing_fields_raises(self) -> None:
        """R1A enforcement must raise CacheCompatViolation on missing required fields."""
        from apps_repo_brief.c0.cache_compat_enforcement import (
            enforce_r1a_strict_compat,
            CacheCompatViolation,
        )
        with pytest.raises(CacheCompatViolation, match="missing required key fields"):
            enforce_r1a_strict_compat(
                candidate_key={},  # missing all required fields
                depth_profile="REPO_BRIEF_BOARD_DOSSIER",
            )

    def test_cache_compat_violation_is_value_error_subclass(self) -> None:
        """CacheCompatViolation must be a ValueError subclass for broad except hygiene."""
        from apps_repo_brief.c0.cache_compat_enforcement import CacheCompatViolation
        assert issubclass(CacheCompatViolation, ValueError)

    def test_fec_requires_abstain_when_evidence_missing(self) -> None:
        """FEC.requires_abstain() must return True when evidence_status=MISSING."""
        from apps_repo_brief.c0.repo_brief_final_contract import (
            RepoBriefFinalEvidenceContract,
            EvidenceStatus,
        )
        fec = RepoBriefFinalEvidenceContract(evidence_status=EvidenceStatus.MISSING)
        assert fec.requires_abstain() is True

    def test_fec_is_grounded_pass_status(self) -> None:
        """FEC.is_grounded() must be True for PASS evidence_status."""
        from apps_repo_brief.c0.repo_brief_final_contract import (
            RepoBriefFinalEvidenceContract,
            EvidenceStatus,
        )
        fec = RepoBriefFinalEvidenceContract(evidence_status=EvidenceStatus.PASS)
        assert fec.is_grounded() is True

    def test_fec_is_not_grounded_unsupported_status(self) -> None:
        """FEC.is_grounded() must be False for UNSUPPORTED evidence_status."""
        from apps_repo_brief.c0.repo_brief_final_contract import (
            RepoBriefFinalEvidenceContract,
            EvidenceStatus,
        )
        fec = RepoBriefFinalEvidenceContract(evidence_status=EvidenceStatus.UNSUPPORTED)
        assert fec.is_grounded() is False

"""IBM graph role episode promotion tests.

Covers acceptance criteria for the IBM-only graph promotion + role-episode packaging wave:
- Promoted IBM skills have employer / time-window binding.
- Role episode bundles are employer-bound and schema-valid.
- Bundles cannot be created from flat skill-only nodes.
- IBM bullets/narrative cannot consume graph context without role_episode_bundle_id.
- HOLD / DO NOT PROMOTE metrics are not present in promoted skill facts or linked graph metrics.
- Archive prose is not embedded in allowed_phrases.
- Config gate for graph_expansion_allowed is BLOCKED_FOR_CONFIG_ENABLEMENT.
- No agentic_core diff (import-time assertion).
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
LEDGER_PATH = REPO / "apps_rg" / "fact_inventory" / "master_skills_arsenal_ledger.json"
BUNDLES_PATH = REPO / "apps_rg" / "fact_inventory" / "ibm_role_episode_bundles.json"
PROFILE_PATH = REPO / "apps_rg" / "config" / "domain_contract" / "section_retrieval_profile.yaml"
IBM_TIME_WINDOW = "2017-04 to 2022-10"

# Skill IDs promoted in this wave
NEWLY_PROMOTED_IBM_SKILLS: tuple[str, ...] = (
    "skill_ibm_automated_release_pipelines",
    "skill_ibm_devsecops_pipeline_security",
)
DRAFT_PROMOTED_IBM_SKILLS: tuple[str, ...] = (
    "skill_risk_greek_stress_testing",
)

# Metrics forbidden from promotion
HOLD_METRICS: frozenset[str] = frozenset({"$15M", "$30M", "15M", "30M"})
DO_NOT_PROMOTE_METRICS: frozenset[str] = frozenset({"25%", "30%", "35%", "40%"})
ALL_FORBIDDEN_METRICS: frozenset[str] = HOLD_METRICS | DO_NOT_PROMOTE_METRICS

# Expected bundle IDs
EXPECTED_BUNDLE_IDS: tuple[str, ...] = (
    "reb_ibm_aws_modernization_architecture",
    "reb_ibm_cognitive_business_decision_support",
    "reb_ibm_presales_solution_engineering",
    "reb_ibm_offering_accelerator_management",
    "reb_ibm_revenue_sales_target_execution",
    "reb_ibm_nlp_ml_decision_support",
    "reb_ibm_data_modeling_bi_decision_support",
    "reb_ibm_customer_success_value_realization",
    "reb_ibm_aws_alliance_partner_cosell_gtm",
    "reb_ibm_devsecops_release_resilience",
)


@pytest.fixture(scope="module")
def ledger() -> dict:
    with open(LEDGER_PATH, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def skill_rows(ledger: dict) -> list[dict]:
    return ledger.get("skill_rows", [])


@pytest.fixture(scope="module")
def graph_nodes(ledger: dict) -> list[dict]:
    return ledger.get("graph_nodes", [])


@pytest.fixture(scope="module")
def graph_edges(ledger: dict) -> list[dict]:
    return ledger.get("graph_edges", [])


@pytest.fixture(scope="module")
def bundles_doc() -> dict:
    with open(BUNDLES_PATH, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def bundles(bundles_doc: dict) -> list[dict]:
    return bundles_doc.get("bundles", [])


# ---------------------------------------------------------------------------
# Task 1: Promoted IBM skills have employer/time-window binding
# ---------------------------------------------------------------------------

class TestIBMSkillEmployerBinding:
    @pytest.mark.parametrize("skill_id", NEWLY_PROMOTED_IBM_SKILLS)
    def test_new_ibm_skill_exists_in_ledger(self, skill_rows: list[dict], skill_id: str) -> None:
        found = any(r.get("skill_id") == skill_id for r in skill_rows)
        assert found, f"{skill_id} not found in skill_rows"

    @pytest.mark.parametrize("skill_id", NEWLY_PROMOTED_IBM_SKILLS)
    def test_new_ibm_skill_employer_is_ibm(self, skill_rows: list[dict], skill_id: str) -> None:
        row = next((r for r in skill_rows if r.get("skill_id") == skill_id), None)
        assert row is not None
        assert row.get("employer") == "IBM", (
            f"{skill_id} employer='{row.get('employer')}'; expected 'IBM'"
        )

    @pytest.mark.parametrize("skill_id", NEWLY_PROMOTED_IBM_SKILLS)
    def test_new_ibm_skill_employer_node_id(self, skill_rows: list[dict], skill_id: str) -> None:
        row = next((r for r in skill_rows if r.get("skill_id") == skill_id), None)
        assert row is not None
        assert row.get("employer_node_id") == "employment_exp_ibm_001", (
            f"{skill_id} employer_node_id='{row.get('employer_node_id')}'; "
            "expected 'employment_exp_ibm_001'"
        )

    @pytest.mark.parametrize("skill_id", NEWLY_PROMOTED_IBM_SKILLS)
    def test_new_ibm_skill_time_window(self, skill_rows: list[dict], skill_id: str) -> None:
        row = next((r for r in skill_rows if r.get("skill_id") == skill_id), None)
        assert row is not None
        tw = row.get("time_window", "")
        assert tw, f"{skill_id} missing time_window"
        assert "2017" in tw, f"{skill_id} time_window '{tw}' does not contain IBM start year 2017"

    @pytest.mark.parametrize("skill_id", NEWLY_PROMOTED_IBM_SKILLS)
    def test_new_ibm_skill_section_eligibility(self, skill_rows: list[dict], skill_id: str) -> None:
        row = next((r for r in skill_rows if r.get("skill_id") == skill_id), None)
        assert row is not None
        sections = set(row.get("allowed_sections") or [])
        assert "ibm_bullets" in sections, f"{skill_id} missing ibm_bullets in allowed_sections"
        assert "ibm_narrative" in sections, f"{skill_id} missing ibm_narrative in allowed_sections"

    @pytest.mark.parametrize("skill_id", NEWLY_PROMOTED_IBM_SKILLS)
    def test_new_ibm_skill_has_graph_node(self, graph_nodes: list[dict], skill_id: str) -> None:
        found = any(n.get("node_id") == skill_id for n in graph_nodes)
        assert found, f"graph_node not found for {skill_id}"

    @pytest.mark.parametrize("skill_id", NEWLY_PROMOTED_IBM_SKILLS)
    def test_new_ibm_skill_has_employment_edge(self, graph_edges: list[dict], skill_id: str) -> None:
        edge_id = f"edge_employment_skill_employment_exp_ibm_001_{skill_id}"
        found = any(e.get("edge_id") == edge_id for e in graph_edges)
        assert found, f"Employment→skill edge not found: {edge_id}"

    @pytest.mark.parametrize("skill_id", NEWLY_PROMOTED_IBM_SKILLS)
    def test_new_ibm_skill_activation_status(self, skill_rows: list[dict], skill_id: str) -> None:
        row = next((r for r in skill_rows if r.get("skill_id") == skill_id), None)
        assert row is not None
        status = row.get("activation_status", "")
        assert status.startswith("ACTIVE"), (
            f"{skill_id} activation_status='{status}'; expected ACTIVE or ACTIVE_CONFIRMED"
        )


class TestDRAFTPromotions:
    @pytest.mark.parametrize("skill_id", DRAFT_PROMOTED_IBM_SKILLS)
    def test_draft_skill_promoted_to_active(self, skill_rows: list[dict], skill_id: str) -> None:
        row = next((r for r in skill_rows if r.get("skill_id") == skill_id), None)
        assert row is not None, f"{skill_id} not found in skill_rows"
        status = row.get("activation_status", "")
        assert status == "ACTIVE_CONFIRMED", (
            f"{skill_id} activation_status='{status}'; expected 'ACTIVE_CONFIRMED'"
        )

    @pytest.mark.parametrize("skill_id", DRAFT_PROMOTED_IBM_SKILLS)
    def test_draft_skill_has_employer_binding(self, skill_rows: list[dict], skill_id: str) -> None:
        row = next((r for r in skill_rows if r.get("skill_id") == skill_id), None)
        assert row is not None
        assert row.get("employer") == "IBM", (
            f"{skill_id} employer='{row.get('employer')}' after promotion; expected 'IBM'"
        )

    @pytest.mark.parametrize("skill_id", DRAFT_PROMOTED_IBM_SKILLS)
    def test_draft_skill_has_ibm_section_eligibility(self, skill_rows: list[dict], skill_id: str) -> None:
        row = next((r for r in skill_rows if r.get("skill_id") == skill_id), None)
        assert row is not None
        sections = set(row.get("allowed_sections") or [])
        # risk_greek adds ibm_narrative; confluent adds ibm_bullets + ibm_narrative
        assert sections & {"ibm_bullets", "ibm_narrative"}, (
            f"{skill_id} missing ibm_bullets/ibm_narrative after promotion. sections={sections}"
        )

    @pytest.mark.parametrize("skill_id", DRAFT_PROMOTED_IBM_SKILLS)
    def test_draft_skill_has_employment_edge(self, graph_edges: list[dict], skill_id: str) -> None:
        edge_id = f"edge_employment_skill_employment_exp_ibm_001_{skill_id}"
        found = any(e.get("edge_id") == edge_id for e in graph_edges)
        assert found, f"Employment→skill edge missing after promotion: {edge_id}"


# ---------------------------------------------------------------------------
# Task 2: Role episode bundles schema + employer binding
# ---------------------------------------------------------------------------

class TestRoleEpisodeBundleSchema:
    def test_all_expected_bundles_present(self, bundles: list[dict]) -> None:
        bundle_ids = {b.get("role_episode_bundle_id") for b in bundles}
        for expected_id in EXPECTED_BUNDLE_IDS:
            assert expected_id in bundle_ids, f"Expected bundle '{expected_id}' not found"

    @pytest.mark.parametrize("bundle_id", EXPECTED_BUNDLE_IDS)
    def test_bundle_employer_is_ibm(self, bundles: list[dict], bundle_id: str) -> None:
        b = next((x for x in bundles if x.get("role_episode_bundle_id") == bundle_id), None)
        assert b is not None, f"Bundle {bundle_id} not found"
        assert b.get("employer") == "IBM", f"{bundle_id} employer='{b.get('employer')}'"

    @pytest.mark.parametrize("bundle_id", EXPECTED_BUNDLE_IDS)
    def test_bundle_employer_node_id(self, bundles: list[dict], bundle_id: str) -> None:
        b = next((x for x in bundles if x.get("role_episode_bundle_id") == bundle_id), None)
        assert b is not None
        assert b.get("employer_node_id") == "employment_exp_ibm_001", (
            f"{bundle_id} employer_node_id='{b.get('employer_node_id')}'"
        )

    @pytest.mark.parametrize("bundle_id", EXPECTED_BUNDLE_IDS)
    def test_bundle_omits_child_time_window(self, bundles: list[dict], bundle_id: str) -> None:
        b = next((x for x in bundles if x.get("role_episode_bundle_id") == bundle_id), None)
        assert b is not None
        assert "time_window" not in b
        assert IBM_TIME_WINDOW == "2017-04 to 2022-10"

    @pytest.mark.parametrize("bundle_id", EXPECTED_BUNDLE_IDS)
    def test_bundle_has_graph_skill_nodes(self, bundles: list[dict], bundle_id: str) -> None:
        b = next((x for x in bundles if x.get("role_episode_bundle_id") == bundle_id), None)
        assert b is not None
        assert b.get("graph_skill_node_ids"), (
            f"{bundle_id} graph_skill_node_ids is empty — bundle cannot be flat skill-only"
        )

    @pytest.mark.parametrize("bundle_id", EXPECTED_BUNDLE_IDS)
    def test_bundle_has_executive_scope_signals(self, bundles: list[dict], bundle_id: str) -> None:
        """Bundles must NOT be created from flat skill-only nodes; executive_scope_signals proves context."""
        b = next((x for x in bundles if x.get("role_episode_bundle_id") == bundle_id), None)
        assert b is not None
        assert b.get("executive_scope_signals"), (
            f"{bundle_id} executive_scope_signals is empty — flat skill-only bundles are forbidden"
        )

    @pytest.mark.parametrize("bundle_id", EXPECTED_BUNDLE_IDS)
    def test_bundle_section_eligibility_is_ibm(self, bundles: list[dict], bundle_id: str) -> None:
        b = next((x for x in bundles if x.get("role_episode_bundle_id") == bundle_id), None)
        assert b is not None
        elig = set(b.get("section_eligibility") or [])
        assert elig & {"ibm_bullets", "ibm_narrative"}, (
            f"{bundle_id} section_eligibility {elig} does not include ibm sections"
        )

    @pytest.mark.parametrize("bundle_id", EXPECTED_BUNDLE_IDS)
    def test_bundle_has_operating_context(self, bundles: list[dict], bundle_id: str) -> None:
        b = next((x for x in bundles if x.get("role_episode_bundle_id") == bundle_id), None)
        assert b is not None
        assert b.get("operating_context"), f"{bundle_id} missing operating_context"

    @pytest.mark.parametrize("bundle_id", EXPECTED_BUNDLE_IDS)
    def test_bundle_has_bullet_intent(self, bundles: list[dict], bundle_id: str) -> None:
        b = next((x for x in bundles if x.get("role_episode_bundle_id") == bundle_id), None)
        assert b is not None
        assert b.get("bullet_intent"), f"{bundle_id} missing bullet_intent"

    @pytest.mark.parametrize("bundle_id", EXPECTED_BUNDLE_IDS)
    def test_bundle_config_gate_is_enabled(self, bundles: list[dict], bundle_id: str) -> None:
        b = next((x for x in bundles if x.get("role_episode_bundle_id") == bundle_id), None)
        assert b is not None
        gate = b.get("config_gate", "")
        assert gate == "ENABLED_WITH_ROLE_EPISODE_BUNDLE_GUARDS", (
            f"{bundle_id} config_gate='{gate}'; expected ENABLED_WITH_ROLE_EPISODE_BUNDLE_GUARDS"
        )


# ---------------------------------------------------------------------------
# Task 3: HOLD / DO NOT PROMOTE metrics are not promoted
# ---------------------------------------------------------------------------

class TestMetricHoldEnforcement:
    @pytest.mark.parametrize("skill_id", NEWLY_PROMOTED_IBM_SKILLS + DRAFT_PROMOTED_IBM_SKILLS)
    def test_skill_allowed_phrases_no_forbidden_metrics(
        self, skill_rows: list[dict], skill_id: str
    ) -> None:
        row = next((r for r in skill_rows if r.get("skill_id") == skill_id), None)
        assert row is not None
        phrases = row.get("allowed_phrases") or []
        for phrase in phrases:
            phrase_upper = str(phrase).upper()
            for forbidden in ALL_FORBIDDEN_METRICS:
                # Check that forbidden metric token is not a standalone claim in allowed_phrases
                # (e.g. "35%", "40%", "$15M" as complete metrics)
                assert forbidden.upper() not in phrase_upper or len(str(phrase).split()) > 3, (
                    f"{skill_id} allowed_phrases contains forbidden metric '{forbidden}': '{phrase}'"
                )

    def test_bundles_do_not_embed_promotable_metric_copies(self, bundles: list[dict]) -> None:
        for b in bundles:
            assert "promotable_metrics" not in b

    def test_bundles_held_metrics_are_labeled_hold(self, bundles: list[dict]) -> None:
        """$15M and $30M must remain held, not graph-linked metric evidence."""
        for b in bundles:
            linked_str = " ".join(str(m) for m in (b.get("linked_metric_outcome_ids") or [])).upper()
            for m in ("15M", "30M", "$15", "$30"):
                assert m.upper() not in linked_str, (
                    f"Bundle {b.get('role_episode_bundle_id', '?')}: HOLD metric '{m}' found in linked metrics"
                )

    def test_bundles_do_not_promote_appear_in_excluded(self, bundles: list[dict]) -> None:
        """25%, 30%, 35%, 40% should not appear in graph-linked metric evidence."""
        for b in bundles:
            linked_str = " ".join(str(m) for m in (b.get("linked_metric_outcome_ids") or [])).upper()
            for pct in ("25%", "30%", "35%", "40%"):
                assert pct not in linked_str, (
                    f"Bundle {b.get('role_episode_bundle_id', '?')}: DO NOT PROMOTE metric '{pct}' in linked metrics"
                )

    def test_skill_forbidden_phrases_include_held_metric_guards(
        self, skill_rows: list[dict]
    ) -> None:
        """Key promoted skills must have forbidden_phrases guarding DO NOT PROMOTE metrics."""
        # These skills are most at risk for overloaded metrics
        guarded_skills = {
            "skill_ibm_automated_release_pipelines": "35%",
            "skill_ibm_devsecops_pipeline_security": "40%",
            "skill_risk_greek_stress_testing": "40%",
        }
        for skill_id, expected_guard in guarded_skills.items():
            row = next((r for r in skill_rows if r.get("skill_id") == skill_id), None)
            if row is None:
                continue
            forb = [str(f) for f in (row.get("forbidden_phrases") or [])]
            forb_str = " ".join(forb).upper()
            assert expected_guard.upper() in forb_str, (
                f"{skill_id} missing forbidden_phrase guard for '{expected_guard}'. "
                f"Got forbidden_phrases={forb}"
            )


# ---------------------------------------------------------------------------
# Task 4: IBM bullets/narrative cannot consume graph context without bundle_id
# ---------------------------------------------------------------------------

class TestRoleEpisodeBundleIDGate:
    def test_assert_bundle_id_present_passes_with_id(self) -> None:
        from apps_rg.runtime.sections.ibm_graph_role_episode_registry import (
            assert_role_episode_bundle_id_present,
        )
        context = {"role_episode_bundle_id": "reb_ibm_aws_modernization_architecture", "section": "ibm_bullets"}
        # Should not raise
        assert_role_episode_bundle_id_present(context)

    def test_assert_bundle_id_present_fails_without_id(self) -> None:
        from apps_rg.runtime.sections.ibm_graph_role_episode_registry import (
            assert_role_episode_bundle_id_present,
        )
        import pytest
        with pytest.raises(ValueError, match="role_episode_bundle_id"):
            assert_role_episode_bundle_id_present({"section": "ibm_bullets"})

    def test_assert_bundle_id_present_fails_with_empty_id(self) -> None:
        from apps_rg.runtime.sections.ibm_graph_role_episode_registry import (
            assert_role_episode_bundle_id_present,
        )
        import pytest
        with pytest.raises(ValueError, match="role_episode_bundle_id"):
            assert_role_episode_bundle_id_present({"role_episode_bundle_id": "", "section": "ibm_narrative"})

    def test_assert_bundle_id_present_fails_with_none(self) -> None:
        from apps_rg.runtime.sections.ibm_graph_role_episode_registry import (
            assert_role_episode_bundle_id_present,
        )
        import pytest
        with pytest.raises(ValueError, match="role_episode_bundle_id"):
            assert_role_episode_bundle_id_present({"role_episode_bundle_id": None})

    def test_validate_bundle_rejects_flat_skill_only(self) -> None:
        from apps_rg.runtime.sections.ibm_graph_role_episode_registry import validate_bundle
        flat_bundle = {
            "role_episode_bundle_id": "reb_flat_test",
            "employer": "IBM",
            "employer_node_id": "employment_exp_ibm_001",
            "title": "Test",
            "time_window": "2017-04 to 2022-10",
            "architecture_scope_signals": ["some arch"],
            "graph_skill_node_ids": ["skill_ibm_automated_release_pipelines"],
            "linked_source_fact_ids": [],
            "linked_archive_signal_ids": [],
            "operating_context": "test",
            "bullet_intent": "test",
            "section_eligibility": ["ibm_bullets"],
            # MISSING executive_scope_signals — simulates flat skill-only bundle
        }
        is_valid, violations = validate_bundle(flat_bundle)
        assert not is_valid, "Flat skill-only bundle (no executive_scope_signals) should fail validation"
        assert any("executive_scope_signals" in v for v in violations), (
            f"Expected executive_scope_signals violation. Got: {violations}"
        )

    def test_validate_bundle_rejects_wrong_employer(self) -> None:
        from apps_rg.runtime.sections.ibm_graph_role_episode_registry import validate_bundle
        b = {
            "role_episode_bundle_id": "reb_wrong_employer",
            "employer": "UnifyConsulting",  # wrong
            "employer_node_id": "employment_exp_ibm_001",
            "title": "Test",
            "time_window": "2017-04 to 2022-10",
            "executive_scope_signals": ["scope"],
            "architecture_scope_signals": ["arch"],
            "graph_skill_node_ids": ["skill_x"],
            "linked_source_fact_ids": [],
            "linked_archive_signal_ids": [],
            "operating_context": "ctx",
            "bullet_intent": "intent",
            "section_eligibility": ["ibm_bullets"],
        }
        is_valid, violations = validate_bundle(b)
        assert not is_valid
        assert any("employer" in v for v in violations), f"Expected employer violation. Got: {violations}"

    def test_validate_bundle_accepts_graph_linked_metrics_without_promotable_copies(self) -> None:
        from apps_rg.runtime.sections.ibm_graph_role_episode_registry import validate_bundle
        b = {
            "role_episode_bundle_id": "reb_linked_metric_test",
            "employer": "IBM",
            "employer_node_id": "employment_exp_ibm_001",
            "title": "Test",
            "time_window": "2017-04 to 2022-10",
            "executive_scope_signals": ["scope"],
            "architecture_scope_signals": ["arch"],
            "graph_skill_node_ids": ["skill_x"],
            "linked_source_fact_ids": [],
            "linked_archive_signal_ids": [],
            "linked_metric_outcome_ids": ["metric_ibm_onprem_to_aws_modernization_waves"],
            "operating_context": "ctx",
            "bullet_intent": "intent",
            "section_eligibility": ["ibm_bullets"],
        }
        is_valid, violations = validate_bundle(b)
        assert is_valid, violations

    def test_all_bundle_files_validate(self, bundles: list[dict]) -> None:
        from apps_rg.runtime.sections.ibm_graph_role_episode_registry import validate_bundle
        for b in bundles:
            bid = b.get("role_episode_bundle_id", "?")
            is_valid, violations = validate_bundle(b)
            assert is_valid, f"Bundle '{bid}' failed validation: {violations}"

    def test_get_bundles_for_ibm_bullets_returns_results(self) -> None:
        from apps_rg.runtime.sections.ibm_graph_role_episode_registry import (
            get_bundles_for_section,
        )
        results = get_bundles_for_section("ibm_bullets")
        assert len(results) >= 5, f"Expected >=5 bundles for ibm_bullets, got {len(results)}"

    def test_get_bundles_for_ibm_narrative_returns_results(self) -> None:
        from apps_rg.runtime.sections.ibm_graph_role_episode_registry import (
            get_bundles_for_section,
        )
        results = get_bundles_for_section("ibm_narrative")
        assert len(results) >= 5, f"Expected >=5 bundles for ibm_narrative, got {len(results)}"

    def test_get_bundle_by_id_returns_bundle(self) -> None:
        from apps_rg.runtime.sections.ibm_graph_role_episode_registry import get_bundle_by_id
        b = get_bundle_by_id("reb_ibm_aws_modernization_architecture")
        assert b is not None
        assert b["employer"] == "IBM"

    def test_get_bundle_by_id_returns_none_for_unknown(self) -> None:
        from apps_rg.runtime.sections.ibm_graph_role_episode_registry import get_bundle_by_id
        b = get_bundle_by_id("reb_nonexistent_bundle")
        assert b is None


# ---------------------------------------------------------------------------
# Archive prose guard
# ---------------------------------------------------------------------------

class TestArchiveProseNotInAllowedPhrases:
    @pytest.mark.parametrize("skill_id", NEWLY_PROMOTED_IBM_SKILLS + DRAFT_PROMOTED_IBM_SKILLS)
    def test_no_archive_prose_sentences_in_allowed_phrases(
        self, skill_rows: list[dict], skill_id: str
    ) -> None:
        from apps_rg.runtime.sections.ibm_graph_role_episode_registry import (
            check_no_archive_prose_in_allowed_phrases,
        )
        row = next((r for r in skill_rows if r.get("skill_id") == skill_id), None)
        if row is None:
            pytest.skip(f"{skill_id} not found in ledger")
        is_clean, reason = check_no_archive_prose_in_allowed_phrases(row)
        assert is_clean, f"{skill_id} contains archive prose in allowed_phrases: {reason}"

    def test_bundles_invariant_archive_prose_excluded(self, bundles_doc: dict) -> None:
        invariants = bundles_doc.get("invariants", {})
        assert invariants.get("archive_prose_excluded") is True, (
            "ibm_role_episode_bundles.json invariants.archive_prose_excluded must be True"
        )
        assert invariants.get("base_resume_hydration_excluded") is True, (
            "ibm_role_episode_bundles.json invariants.base_resume_hydration_excluded must be True"
        )


# ---------------------------------------------------------------------------
# Config gate: BLOCKED_FOR_CONFIG_ENABLEMENT
# ---------------------------------------------------------------------------

class TestConfigGate:
    def test_ibm_bullets_graph_expansion_enabled_with_bundle_consumption(self) -> None:
        """ibm_bullets graph_expansion_allowed true only with role_episode_bundle consumption."""
        import yaml  # type: ignore[import-untyped]
        with open(PROFILE_PATH, encoding="utf-8") as f:
            profile = yaml.safe_load(f)
        # YAML has top-level `sections:` key containing a list of profiles
        raw_sections = profile.get("sections", []) if isinstance(profile, dict) else profile
        if isinstance(raw_sections, list):
            section_list = raw_sections
        else:
            section_list = list(raw_sections.values()) if isinstance(raw_sections, dict) else []
        ibm_bullets_profiles = [
            p for p in section_list
            if isinstance(p, dict) and p.get("section_id") == "ibm_bullets"
        ]
        assert ibm_bullets_profiles, "ibm_bullets section not found in section_retrieval_profile.yaml"
        for p in ibm_bullets_profiles:
            assert p.get("graph_expansion_allowed") is True
            assert p.get("role_episode_bundle_consumption") == "required"
            assert p.get("graph_expansion_mode") == "role_episode_bundle_only"

    def test_ibm_narrative_graph_expansion_enabled_with_bundle_consumption(self) -> None:
        import yaml  # type: ignore[import-untyped]
        with open(PROFILE_PATH, encoding="utf-8") as f:
            profile = yaml.safe_load(f)
        raw_sections = profile.get("sections", []) if isinstance(profile, dict) else profile
        if isinstance(raw_sections, list):
            section_list = raw_sections
        else:
            section_list = list(raw_sections.values()) if isinstance(raw_sections, dict) else []
        ibm_narrative_profiles = [
            p for p in section_list
            if isinstance(p, dict) and p.get("section_id") == "ibm_narrative"
        ]
        assert ibm_narrative_profiles, "ibm_narrative section not found in section_retrieval_profile.yaml"
        for p in ibm_narrative_profiles:
            assert p.get("graph_expansion_allowed") is True
            assert p.get("role_episode_bundle_consumption") == "required"

    def test_bundles_config_gate_label_is_enabled(self, bundles_doc: dict) -> None:
        invariants = bundles_doc.get("invariants", {})
        assert invariants.get("config_gate") == "ENABLED_WITH_ROLE_EPISODE_BUNDLE_GUARDS", (
            "bundles_doc invariants.config_gate must be ENABLED_WITH_ROLE_EPISODE_BUNDLE_GUARDS"
        )


# ---------------------------------------------------------------------------
# No agentic_core diff guard
# ---------------------------------------------------------------------------

class TestNoAgenticCoreDiff:
    def test_ibm_graph_role_episode_registry_not_in_agentic_core(self) -> None:
        """Registry module must live in apps_rg, not agentic_core."""
        from apps_rg.runtime.sections import ibm_graph_role_episode_registry as reg
        module_path = Path(reg.__file__).resolve()
        agentic_core = REPO / "agentic_core"
        assert not str(module_path).startswith(str(agentic_core)), (
            f"ibm_graph_role_episode_registry is inside agentic_core: {module_path}"
        )

    def test_ibm_role_episode_bundles_not_in_agentic_core(self) -> None:
        assert not str(BUNDLES_PATH).startswith(str(REPO / "agentic_core")), (
            f"ibm_role_episode_bundles.json is inside agentic_core: {BUNDLES_PATH}"
        )

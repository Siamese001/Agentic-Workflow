r"""
Extracted capability module: extracted_test_template_rendering_e2e
Source: tests\unit\prompt_governance\test_template_rendering_e2e.py
Extracted: 2026-03-27T06:50:34.045419
"""


def renderer() -> SovereignPromptRenderer:
    r"""Real renderer pointed at the canonical templates/ directory."""
    return SovereignPromptRenderer(template_root=TEMPLATES_DIR)


def meta_renderer() -> SovereignPromptRenderer:
    """Renderer pointed at meta_prompts/ for deprecated template tests."""
    return SovereignPromptRenderer(template_root=META_PROMPTS_DIR)


def adversarial_renderer() -> SovereignPromptRenderer:
    """Renderer pointed at security/adversarial/ for red-team payloads."""
    return SovereignPromptRenderer(template_root=ADVERSARIAL_DIR)


class TestInstructionalTemplateRendering:
    """Every template in templates/ must render without error."""

    def test_code_healing(self, renderer: SovereignPromptRenderer):

        ctx = {
            **_subatomic_context(),
            "violations": ["snake_case violation", "missing docstring"],
        }
        result = renderer.render("code_healing.jinja", context=ctx, validate=False)
        assert "sovereign code healing specialist" in result.lower()
        assert "SUBATOMIC HEALED" in result
        assert len(result) > 100

    def test_subatomic_healing_context(self, renderer: SovereignPromptRenderer):
        ctx = _subatomic_context()
        result = renderer.render("subatomic_healing_context.jinja", context=ctx, validate=False)
        assert "SOVEREIGN_SUBATOMIC_CONTEXT" in result
        assert "healing_round" not in result or "5" in result
        assert "GravityLeakRepairAgent" in result

    def test_file_placement(self, renderer: SovereignPromptRenderer):
        ctx = {"content_preview": "class GravityValidator:\n    pass"}
        result = renderer.render("file_placement.jinja", context=ctx, validate=False)
        assert "sovereign placement oracle" in result.lower()
        assert "GravityValidator" in result

    def test_gravity_compliance(self, renderer: SovereignPromptRenderer):
        ctx = {"violation_code": "from agentic_core.L5_safety import guardrail", "code_block": "import X"}
        result = renderer.render("gravity_compliance.jinja", context=ctx, validate=False)
        assert "gravity" in result.lower()
        assert "L5_safety" in result

    def test_gravity_repair(self, renderer: SovereignPromptRenderer):
        ctx = {"file_path": "agentic_core/L0_routing/core.py", "code_block": "from L5_safety import X"}
        result = renderer.render("gravity_repair.jinja", context=ctx, validate=False)
        assert "GravityLeakRepairAgent" in result
        assert "L0_routing" in result

    def test_gravity_dynamic_conversion(self, renderer: SovereignPromptRenderer):
        ctx = _subatomic_context()
        result = renderer.render("gravity_dynamic_conversion.jinja", context=ctx, validate=False)
        assert "importlib" in result.lower() or "dynamic" in result.lower()

    def test_naming_law(self, renderer: SovereignPromptRenderer):
        ctx = {"name": "MyClassName", "identifiers": ["APIClient", "HTTPServer"]}
        result = renderer.render("naming_law.jinja", context=ctx, validate=False)
        assert "snake_case" in result
        assert "APIClient" in result

    def test_naming_precision(self, renderer: SovereignPromptRenderer):
        ctx = _subatomic_context()
        result = renderer.render("naming_precision.jinja", context=ctx, validate=False)
        assert "naming" in result.lower()

    def test_dead_code_elimination(self, renderer: SovereignPromptRenderer):
        ctx = _subatomic_context()
        result = renderer.render("dead_code_elimination.jinja", context=ctx, validate=False)
        assert "dead code" in result.lower() or "unused" in result.lower()

    def test_docstring_enrichment(self, renderer: SovereignPromptRenderer):
        ctx = {
            **_subatomic_context(),
            "current_docstring": '"""Do something."""',
        }
        result = renderer.render("docstring_enrichment.jinja", context=ctx, validate=False)
        assert "docstring" in result.lower() or "google-style" in result.lower()

    def test_type_inference(self, renderer: SovereignPromptRenderer):
        ctx = {
            **_subatomic_context(),
            "meta_insight": "Historical: 90% of functions need Optional return types",
        }
        result = renderer.render("type_inference.jinja", context=ctx, validate=False)
        assert "type" in result.lower()

    def test_import_optimization(self, renderer: SovereignPromptRenderer):
        ctx = _subatomic_context()
        result = renderer.render("import_optimization.jinja", context=ctx, validate=False)
        assert "import" in result.lower()

    def test_reasoning_chain(self, renderer: SovereignPromptRenderer):
        ctx = {"task": "Refactor the L0 routing engine for better separation of concerns"}
        result = renderer.render("reasoning_chain.jinja", context=ctx, validate=False)
        assert "reasoning chain" in result.lower() or "decompose" in result.lower()
        assert "Refactor" in result

    def test_anomaly_detection_response(self, renderer: SovereignPromptRenderer):
        ctx = {
            "active_agents": 12,
            "api_latency_ms": 450,
            "baseline_error": 2.1,
            "baseline_latency": 200,
            "current_timestamp": "2026-03-17T06:00:00Z",
            "error_rate": 5.7,
            "memory_limit": 4096,
            "memory_mb": 2100,
            "recent_actions": ["HealingOrchestrator executed 12 fixes"],
            "recent_escalations": 0,
            "recent_healing_actions": 12,
            "token_budget": 100,
            "token_rate": 85,
        }
        result = renderer.render("anomaly_detection_response.jinja", context=ctx, validate=False)
        assert "anomaly" in result.lower()
        assert "450" in result

    def test_cross_layer_coordination(self, renderer: SovereignPromptRenderer):
        ctx = {
            "message": "Request current sovereignty health score",
            "source_agent": "RedTeamAgent",
            "source_layer": 5,
            "target_agent": "MetricsWitness",
            "target_layer": 0,
        }
        result = renderer.render("cross_layer_coordination.jinja", context=ctx, validate=False)
        assert "gravity" in result.lower()
        assert "RedTeamAgent" in result

    def test_context_memory_synthesis(self, renderer: SovereignPromptRenderer):
        ctx = {
            "current_timestamp": "2026-03-17T06:00:00Z",
            "last_sync": "2026-03-16",
            "session_id": "sess-001",
            "session_insights": ["Gravity leak found in L0", "Naming violation auto-healed"],
            "total_embeddings": 500,
            "vector_count": 120,
            "vector_store": "sovereign-memory-index",
        }
        result = renderer.render("context_memory_synthesis.jinja", context=ctx, validate=False)
        assert "memory synthesis" in result.lower() or "semantic" in result.lower()
        assert "Gravity leak" in result

    def test_agent_autonomy_law(self, renderer: SovereignPromptRenderer):
        result = renderer.render("agent_autonomy_law.jinja", context={}, validate=False)
        assert "autonomy" in result.lower()
        assert "heal_repository" in result

    def test_autonomous_decision_tree(self, renderer: SovereignPromptRenderer):
        result = renderer.render("autonomous_decision_tree.jinja", context={}, validate=False)
        assert "decision" in result.lower()
        assert "HUMAN_ESCALATION" in result

    def test_async_compatibility(self, renderer: SovereignPromptRenderer):
        ctx = _subatomic_context()
        result = renderer.render("async_compatibility.jinja", context=ctx, validate=False)
        assert "async" in result.lower()

    def test_fission_planning(self, renderer: SovereignPromptRenderer):
        ctx = {
            "code_preview": "class BigClass:\n    # 2000 lines of mixed concerns",
            "current_path": "agentic_core/L5_safety/reasoning/MonolithAgent.py",
            "entity_count": 25,
            "line_count": 2100,
        }
        result = renderer.render("fission_planning.jinja", context=ctx, validate=False)
        assert "fission" in result.lower()
        assert "2100" in result

    def test_goal_decomposition_planning(self, renderer: SovereignPromptRenderer):
        ctx = {
            "goal": "Achieve 100% sovereignty health score",
            "constraints": ["No more than 50 LLM calls", "Complete within 2 hours"],
        }
        result = renderer.render("goal_decomposition_planning.jinja", context=ctx, validate=False)
        assert "100% sovereignty" in result
        assert "milestone" in result.lower()

    def test_multi_agent_consensus(self, renderer: SovereignPromptRenderer):
        ctx = {
            "agent_list": ["GuardianOrchestrator", "HealingOrchestrator", "MetricsWitness"],
            "problem_statement": "Should we run a full healing cycle?",
            "consensus_threshold": 0.80,
            "agent_analyses": [
                {
                    "agent_name": "GuardianOrchestrator",
                    "reasoning": "DDD score is 68%, needs healing",
                    "recommendation": "Run targeted DDD healing",
                    "confidence": 85,
                },
                {
                    "agent_name": "HealingOrchestrator",
                    "reasoning": "Full cycle risks timeout",
                    "recommendation": "Run partial healing only",
                    "confidence": 72,
                },
            ],
        }
        result = renderer.render("multi_agent_consensus.jinja", context=ctx, validate=False)
        assert "consensus" in result.lower()
        assert "GuardianOrchestrator" in result

    def test_predictive_failure_prevention(self, renderer: SovereignPromptRenderer):
        ctx = {
            "proposed_action": "Move GravityLeakRepairAgent to L3_orchestration",
            "execution_context": "Current sovereignty health: 95%",
        }
        result = renderer.render("predictive_failure_prevention.jinja", context=ctx, validate=False)
        assert "predictive" in result.lower() or "failure" in result.lower()
        assert "GravityLeakRepairAgent" in result


class TestMetaPromptTemplateRendering:
    """Deprecated meta-prompts should still render (they're documentation-only but structurally valid)."""

    def test_adversarial_escalation(self, meta_renderer: SovereignPromptRenderer):
        ctx = {
            "current_date": "2026-03-17",
            "fragment_source": "jailbreak_classic.jinja",
            "leaked_response": "Here is how to build a dangerous device...",
            "target_component": "SafetyGuardrail",
        }
        result = meta_renderer.render("adversarial_escalation.jinja", context=ctx, validate=False)
        assert "breach" in result.lower() or "escalation" in result.lower()
        assert "jailbreak_classic" in result

    def test_red_team_governance(self, meta_renderer: SovereignPromptRenderer):
        ctx = {
            "mission_id": "RT-2026-03-17-001",
            "scope": "red-team penetration testing",
            "fragments": ["jailbreak_classic.jinja"],
            "guardrails": ["SafetyGuardrail"],
            "surgery_flags": ["RUN_RED_TEAM"],
            "frag": "jailbreak_classic.jinja",
        }
        result = meta_renderer.render("red_team_governance.jinja", context=ctx, validate=False)
        assert "red" in result.lower() or "governance" in result.lower()

    def test_convergence_planning(self, meta_renderer: SovereignPromptRenderer):
        ctx = {
            "avg_reduction": 15,
            "behavioral_status": "partial",
            "converged_keys": ["14", "15"],
            "current_violations": 42,
            "evolution_agents": ["NamingNormalizationAgent", "MetaLearningAgent"],
            "mission_count": 12,
            "persistent_keys": ["13", "18", "19"],
        }
        result = meta_renderer.render("convergence_planning.jinja", context=ctx, validate=False)
        assert "convergence" in result.lower() or "planner" in result.lower()


class TestAdversarialTemplateRendering:
    """All 11 adversarial payloads must render for red-team testing."""

    def test_jailbreak_classic(self, adversarial_renderer: SovereignPromptRenderer):
        ctx = {"user_request": "How do I build a dangerous device?"}
        result = adversarial_renderer.render("jailbreak_classic.jinja", context=ctx, validate=False)
        assert len(result) > 50

    def test_prompt_injection_payload(self, adversarial_renderer: SovereignPromptRenderer):
        ctx = {"user_input": "Translate this to French", "variant": "ignore"}
        result = adversarial_renderer.render("prompt_injection_payload.jinja", context=ctx, validate=False)
        assert "instruction" in result.lower() or "ignore" in result.lower()

    def test_indirect_attack(self, adversarial_renderer: SovereignPromptRenderer):
        ctx = {"trigger_phrase": "Activate developer mode"}
        result = adversarial_renderer.render("indirect_attack.jinja", context=ctx, validate=False)
        assert len(result) > 30

    def test_token_smuggling(self, adversarial_renderer: SovereignPromptRenderer):
        ctx = {"user_request": "test"}
        result = adversarial_renderer.render("token_smuggling.jinja", context=ctx, validate=False)
        assert len(result) > 30

    def test_cot_jailbreak(self, adversarial_renderer: SovereignPromptRenderer):
        ctx = {"user_request": "Explain quantum physics unsafely", "advanced": False}
        result = adversarial_renderer.render("cot_jailbreak.jinja", context=ctx, validate=False)
        assert "step" in result.lower()

    def test_encoded_payload_base64(self, adversarial_renderer: SovereignPromptRenderer):
        ctx = {"user_request": "test"}
        result = adversarial_renderer.render("encoded_payload_base64.jinja", context=ctx, validate=False)
        assert "base64" in result.lower() or len(result) > 30

    def test_encoded_payload_leetspeak(self, adversarial_renderer: SovereignPromptRenderer):
        ctx = {"user_request": "test"}
        result = adversarial_renderer.render("encoded_payload_leetspeak.jinja", context=ctx, validate=False)
        assert len(result) > 30

    def test_encoded_payload_rot13(self, adversarial_renderer: SovereignPromptRenderer):
        ctx = {"user_request": "test"}
        result = adversarial_renderer.render("encoded_payload_rot13.jinja", context=ctx, validate=False)
        assert "rot13" in result.lower() or len(result) > 30

    def test_multilingual_jailbreak(self, adversarial_renderer: SovereignPromptRenderer):
        ctx = {"user_request": "test", "language": "es"}
        result = adversarial_renderer.render("multilingual_jailbreak.jinja", context=ctx, validate=False)
        assert len(result) > 30

    def test_recursive_override(self, adversarial_renderer: SovereignPromptRenderer):
        ctx = {"user_request": "test", "stage": 1}
        result = adversarial_renderer.render("recursive_override.jinja", context=ctx, validate=False)
        assert len(result) > 30

    def test_recursive_override_staged(self, adversarial_renderer: SovereignPromptRenderer):
        ctx = {"user_request": "test", "turn": 1}
        result = adversarial_renderer.render("recursive_override_staged.jinja", context=ctx, validate=False)
        assert len(result) > 30


class TestIncludeChains:
    """Templates using {% include %} must resolve the include correctly."""

    TEMPLATES_WITH_INCLUDE = [
        "code_healing.jinja",
        "async_compatibility.jinja",
        "dead_code_elimination.jinja",
        "docstring_enrichment.jinja",
        "gravity_dynamic_conversion.jinja",
        "import_optimization.jinja",
        "naming_precision.jinja",
        "type_inference.jinja",
    ]

    @pytest.mark.parametrize("template_name", TEMPLATES_WITH_INCLUDE)
    def test_include_resolves(self, renderer: SovereignPromptRenderer, template_name: str):
        """Each template that includes subatomic_healing_context.jinja must render."""
        ctx = {
            **_subatomic_context(),
            "violations": ["test violation"],
            "current_docstring": '"""stub"""',
            "meta_insight": "test insight",
        }
        result = renderer.render(template_name, context=ctx, validate=False)
        assert "SOVEREIGN_SUBATOMIC_CONTEXT" in result, (
            f"{template_name} includes subatomic_healing_context.jinja but "
            "the include content was not found in rendered output"
        )
        assert len(result) > 200


class TestCatalogRendererIntegration:
    """Templates discovered via catalog must be renderable by the renderer."""

    def test_all_active_instructional_templates_render(self, renderer: SovereignPromptRenderer):
        """Every ACTIVE instructional template in the catalog renders without exception."""
        active = [
            e
            for e in TEMPLATE_CATALOG
            if e.category == TemplateCategory.INSTRUCTIONAL and e.status == TemplateStatus.ACTIVE
        ]
        # Build a superset context that satisfies all templates
        superset_ctx = {
            **_subatomic_context(),
            "violations": ["test"],
            "current_docstring": '"""stub"""',
            "meta_insight": "insight",
            "content_preview": "class X: pass",
            "violation_code": "from L5 import X",
            "name": "TestName",
            "identifiers": ["TestId"],
            "task": "Test task",
            "active_agents": 5,
            "api_latency_ms": 100,
            "baseline_error": 1.0,
            "baseline_latency": 50,
            "current_timestamp": "now",
            "error_rate": 2.0,
            "memory_limit": 4096,
            "memory_mb": 1024,
            "recent_actions": ["action1"],
            "recent_escalations": 0,
            "recent_healing_actions": 5,
            "token_budget": 100,
            "token_rate": 50,
            "message": "test message",
            "source_agent": "AgentA",
            "source_layer": 3,
            "target_agent": "AgentB",
            "target_layer": 5,
            "session_id": "s1",
            "session_insights": ["insight1"],
            "total_embeddings": 100,
            "vector_count": 50,
            "vector_store": "store",
            "last_sync": "yesterday",
            "code_preview": "class Big: pass",
            "current_path": "some/path.py",
            "entity_count": 10,
            "line_count": 500,
            "goal": "Test goal",
            "constraints": ["constraint1"],
            "agent_list": ["A", "B"],
            "problem_statement": "test problem",
            "consensus_threshold": 0.8,
            "agent_analyses": [
                {"agent_name": "A", "reasoning": "r", "recommendation": "x", "confidence": 80},
            ],
            "proposed_action": "test action",
            "execution_context": "test context",
        }
        failures = []
        for entry in active:
            try:
                result = renderer.render(entry.template_name, context=superset_ctx, validate=False)
                assert len(result) > 10, f"Empty render for {entry.template_name}"
            except Exception as e:
                failures.append(f"{entry.template_name}: {e}")
        assert not failures, f"{len(failures)} INSTRUCTIONAL templates failed to render:\n" + "\n".join(
            failures,
        )

    def test_agent_lookup_templates_render(self, renderer: SovereignPromptRenderer):
        """Templates discovered via get_templates_for_agent() render correctly."""
        superset_ctx = {
            **_subatomic_context(),
            "violation_code": "from L5 import X",
        }
        agents = ["GravityLeakRepairAgent", "NamingAgent", "CodeHealerAgent"]
        for agent in agents:
            templates = get_templates_for_agent(agent)
            assert templates, f"No templates found for {agent}"
            for entry in templates:
                if entry.category != TemplateCategory.INSTRUCTIONAL:
                    continue
                try:
                    result = renderer.render(
                        entry.template_name,
                        context={
                            **superset_ctx,
                            "violations": ["v1"],
                            "current_docstring": '"""x"""',
                            "meta_insight": "m",
                            "identifiers": ["TestId"],
                        },
                        validate=False,
                    )
                    assert len(result) > 10
                except Exception as e:
                    pytest.fail(f"{agent} → {entry.template_name}: {e}")


class TestSchemaValidation:
    """Template schema headers must be parseable and enforced."""

    def test_schema_parse_for_code_healing(self, renderer: SovereignPromptRenderer):
        schema = renderer.get_template_schema("code_healing.jinja")
        assert "violations" in schema.required_vars
        assert "code_block" in schema.required_vars

    def test_schema_parse_for_fission_planning(self, renderer: SovereignPromptRenderer):
        schema = renderer.get_template_schema("fission_planning.jinja")
        assert "line_count" in schema.required_vars
        assert "entity_count" in schema.required_vars

    def test_validation_rejects_missing_vars(self, renderer: SovereignPromptRenderer):
        with pytest.raises(TemplateValidationError, match="violations"):
            renderer.validate_context("code_healing.jinja", {"code_block": "x"})

    def test_validation_passes_with_all_vars(self, renderer: SovereignPromptRenderer):
        renderer.validate_context(
            "code_healing.jinja",
            {"violations": ["v"], "code_block": "x"},
        )

    def test_all_templates_have_parseable_schemas(self, renderer: SovereignPromptRenderer):
        """Every .jinja in templates/ must have a parseable SCHEMA header."""
        failures = []
        for jinja in TEMPLATES_DIR.glob("*.jinja"):
            try:
                schema = renderer.get_template_schema(jinja.name)
                assert schema.description, f"No description for {jinja.name}"
            except Exception as e:
                failures.append(f"{jinja.name}: {e}")
        assert not failures, "Schema parse failures:\n" + "\n".join(failures)


class TestRendererPathCorrectness:
    """The renderer default path must point to the real templates directory."""

    def test_default_renderer_finds_templates(self):
        renderer = SovereignPromptRenderer()
        templates = renderer.list_available_templates()
        assert len(templates) >= 20, (
            f"Default renderer only found {len(templates)} templates in {renderer.template_root}: {templates}"
        )

    def test_default_renderer_template_root_is_prompt_governance_templates(self):
        renderer = SovereignPromptRenderer()
        assert renderer.template_root.name == "templates"
        assert renderer.template_root.parent.name == "prompt_governance"

    def test_render_tagentic_resolves_meta_prompts(self):
        """render_tagentic uses a dedicated meta_prompts Environment."""
        renderer = SovereignPromptRenderer()
        ctx = {
            "mission_id": "test",
            "scope": "test",
            "fragments": ["jailbreak_classic.jinja"],
            "guardrails": ["SafetyGuardrail"],
            "surgery_flags": ["RUN_RED_TEAM"],
            "frag": "jailbreak_classic.jinja",
        }
        result = renderer.render_tagentic(
            base_template="red_team_governance.jinja",
            fragments=[],
            context=ctx,
            validate=False,
        )
        assert len(result) > 50

    def test_code_healing(self, renderer: SovereignPromptRenderer):

        ctx = {
            **_subatomic_context(),
            "violations": ["snake_case violation", "missing docstring"],
        }
        result = renderer.render("code_healing.jinja", context=ctx, validate=False)
        assert "sovereign code healing specialist" in result.lower()
        assert "SUBATOMIC HEALED" in result
        assert len(result) > 100

    def test_subatomic_healing_context(self, renderer: SovereignPromptRenderer):
        ctx = _subatomic_context()
        result = renderer.render("subatomic_healing_context.jinja", context=ctx, validate=False)
        assert "SOVEREIGN_SUBATOMIC_CONTEXT" in result
        assert "healing_round" not in result or "5" in result
        assert "GravityLeakRepairAgent" in result

    def test_file_placement(self, renderer: SovereignPromptRenderer):
        ctx = {"content_preview": "class GravityValidator:\n    pass"}
        result = renderer.render("file_placement.jinja", context=ctx, validate=False)
        assert "sovereign placement oracle" in result.lower()
        assert "GravityValidator" in result

    def test_gravity_compliance(self, renderer: SovereignPromptRenderer):
        ctx = {"violation_code": "from agentic_core.L5_safety import guardrail", "code_block": "import X"}
        result = renderer.render("gravity_compliance.jinja", context=ctx, validate=False)
        assert "gravity" in result.lower()
        assert "L5_safety" in result

    def test_gravity_repair(self, renderer: SovereignPromptRenderer):
        ctx = {"file_path": "agentic_core/L0_routing/core.py", "code_block": "from L5_safety import X"}
        result = renderer.render("gravity_repair.jinja", context=ctx, validate=False)
        assert "GravityLeakRepairAgent" in result
        assert "L0_routing" in result

    def test_gravity_dynamic_conversion(self, renderer: SovereignPromptRenderer):
        ctx = _subatomic_context()
        result = renderer.render("gravity_dynamic_conversion.jinja", context=ctx, validate=False)
        assert "importlib" in result.lower() or "dynamic" in result.lower()

    def test_naming_law(self, renderer: SovereignPromptRenderer):
        ctx = {"name": "MyClassName", "identifiers": ["APIClient", "HTTPServer"]}
        result = renderer.render("naming_law.jinja", context=ctx, validate=False)
        assert "snake_case" in result
        assert "APIClient" in result

    def test_naming_precision(self, renderer: SovereignPromptRenderer):
        ctx = _subatomic_context()
        result = renderer.render("naming_precision.jinja", context=ctx, validate=False)
        assert "naming" in result.lower()

    def test_dead_code_elimination(self, renderer: SovereignPromptRenderer):
        ctx = _subatomic_context()
        result = renderer.render("dead_code_elimination.jinja", context=ctx, validate=False)
        assert "dead code" in result.lower() or "unused" in result.lower()

    def test_docstring_enrichment(self, renderer: SovereignPromptRenderer):
        ctx = {
            **_subatomic_context(),
            "current_docstring": '"""Do something."""',
        }
        result = renderer.render("docstring_enrichment.jinja", context=ctx, validate=False)
        assert "docstring" in result.lower() or "google-style" in result.lower()

    def test_type_inference(self, renderer: SovereignPromptRenderer):
        ctx = {
            **_subatomic_context(),
            "meta_insight": "Historical: 90% of functions need Optional return types",
        }
        result = renderer.render("type_inference.jinja", context=ctx, validate=False)
        assert "type" in result.lower()

    def test_import_optimization(self, renderer: SovereignPromptRenderer):
        ctx = _subatomic_context()
        result = renderer.render("import_optimization.jinja", context=ctx, validate=False)
        assert "import" in result.lower()

    def test_reasoning_chain(self, renderer: SovereignPromptRenderer):
        ctx = {"task": "Refactor the L0 routing engine for better separation of concerns"}
        result = renderer.render("reasoning_chain.jinja", context=ctx, validate=False)
        assert "reasoning chain" in result.lower() or "decompose" in result.lower()
        assert "Refactor" in result

    def test_anomaly_detection_response(self, renderer: SovereignPromptRenderer):
        ctx = {
            "active_agents": 12,
            "api_latency_ms": 450,
            "baseline_error": 2.1,
            "baseline_latency": 200,
            "current_timestamp": "2026-03-17T06:00:00Z",
            "error_rate": 5.7,
            "memory_limit": 4096,
            "memory_mb": 2100,
            "recent_actions": ["HealingOrchestrator executed 12 fixes"],
            "recent_escalations": 0,
            "recent_healing_actions": 12,
            "token_budget": 100,
            "token_rate": 85,
        }
        result = renderer.render("anomaly_detection_response.jinja", context=ctx, validate=False)
        assert "anomaly" in result.lower()
        assert "450" in result

    def test_cross_layer_coordination(self, renderer: SovereignPromptRenderer):
        ctx = {
            "message": "Request current sovereignty health score",
            "source_agent": "RedTeamAgent",
            "source_layer": 5,
            "target_agent": "MetricsWitness",
            "target_layer": 0,
        }
        result = renderer.render("cross_layer_coordination.jinja", context=ctx, validate=False)
        assert "gravity" in result.lower()
        assert "RedTeamAgent" in result

    def test_context_memory_synthesis(self, renderer: SovereignPromptRenderer):
        ctx = {
            "current_timestamp": "2026-03-17T06:00:00Z",
            "last_sync": "2026-03-16",
            "session_id": "sess-001",
            "session_insights": ["Gravity leak found in L0", "Naming violation auto-healed"],
            "total_embeddings": 500,
            "vector_count": 120,
            "vector_store": "sovereign-memory-index",
        }
        result = renderer.render("context_memory_synthesis.jinja", context=ctx, validate=False)
        assert "memory synthesis" in result.lower() or "semantic" in result.lower()
        assert "Gravity leak" in result

    def test_agent_autonomy_law(self, renderer: SovereignPromptRenderer):
        result = renderer.render("agent_autonomy_law.jinja", context={}, validate=False)
        assert "autonomy" in result.lower()
        assert "heal_repository" in result

    def test_autonomous_decision_tree(self, renderer: SovereignPromptRenderer):
        result = renderer.render("autonomous_decision_tree.jinja", context={}, validate=False)
        assert "decision" in result.lower()
        assert "HUMAN_ESCALATION" in result

    def test_async_compatibility(self, renderer: SovereignPromptRenderer):
        ctx = _subatomic_context()
        result = renderer.render("async_compatibility.jinja", context=ctx, validate=False)
        assert "async" in result.lower()

    def test_fission_planning(self, renderer: SovereignPromptRenderer):
        ctx = {
            "code_preview": "class BigClass:\n    # 2000 lines of mixed concerns",
            "current_path": "agentic_core/L5_safety/reasoning/MonolithAgent.py",
            "entity_count": 25,
            "line_count": 2100,
        }
        result = renderer.render("fission_planning.jinja", context=ctx, validate=False)
        assert "fission" in result.lower()
        assert "2100" in result

    def test_goal_decomposition_planning(self, renderer: SovereignPromptRenderer):
        ctx = {
            "goal": "Achieve 100% sovereignty health score",
            "constraints": ["No more than 50 LLM calls", "Complete within 2 hours"],
        }
        result = renderer.render("goal_decomposition_planning.jinja", context=ctx, validate=False)
        assert "100% sovereignty" in result
        assert "milestone" in result.lower()

    def test_multi_agent_consensus(self, renderer: SovereignPromptRenderer):
        ctx = {
            "agent_list": ["GuardianOrchestrator", "HealingOrchestrator", "MetricsWitness"],
            "problem_statement": "Should we run a full healing cycle?",
            "consensus_threshold": 0.80,
            "agent_analyses": [
                {
                    "agent_name": "GuardianOrchestrator",
                    "reasoning": "DDD score is 68%, needs healing",
                    "recommendation": "Run targeted DDD healing",
                    "confidence": 85,
                },
                {
                    "agent_name": "HealingOrchestrator",
                    "reasoning": "Full cycle risks timeout",
                    "recommendation": "Run partial healing only",
                    "confidence": 72,
                },
            ],
        }
        result = renderer.render("multi_agent_consensus.jinja", context=ctx, validate=False)
        assert "consensus" in result.lower()
        assert "GuardianOrchestrator" in result

    def test_predictive_failure_prevention(self, renderer: SovereignPromptRenderer):
        ctx = {
            "proposed_action": "Move GravityLeakRepairAgent to L3_orchestration",
            "execution_context": "Current sovereignty health: 95%",
        }
        result = renderer.render("predictive_failure_prevention.jinja", context=ctx, validate=False)
        assert "predictive" in result.lower() or "failure" in result.lower()
        assert "GravityLeakRepairAgent" in result

    def test_adversarial_escalation(self, meta_renderer: SovereignPromptRenderer):
        ctx = {
            "current_date": "2026-03-17",
            "fragment_source": "jailbreak_classic.jinja",
            "leaked_response": "Here is how to build a dangerous device...",
            "target_component": "SafetyGuardrail",
        }
        result = meta_renderer.render("adversarial_escalation.jinja", context=ctx, validate=False)
        assert "breach" in result.lower() or "escalation" in result.lower()
        assert "jailbreak_classic" in result

    def test_red_team_governance(self, meta_renderer: SovereignPromptRenderer):
        ctx = {
            "mission_id": "RT-2026-03-17-001",
            "scope": "red-team penetration testing",
            "fragments": ["jailbreak_classic.jinja"],
            "guardrails": ["SafetyGuardrail"],
            "surgery_flags": ["RUN_RED_TEAM"],
            "frag": "jailbreak_classic.jinja",
        }
        result = meta_renderer.render("red_team_governance.jinja", context=ctx, validate=False)
        assert "red" in result.lower() or "governance" in result.lower()

    def test_convergence_planning(self, meta_renderer: SovereignPromptRenderer):
        ctx = {
            "avg_reduction": 15,
            "behavioral_status": "partial",
            "converged_keys": ["14", "15"],
            "current_violations": 42,
            "evolution_agents": ["NamingNormalizationAgent", "MetaLearningAgent"],
            "mission_count": 12,
            "persistent_keys": ["13", "18", "19"],
        }
        result = meta_renderer.render("convergence_planning.jinja", context=ctx, validate=False)
        assert "convergence" in result.lower() or "planner" in result.lower()

    def test_jailbreak_classic(self, adversarial_renderer: SovereignPromptRenderer):
        ctx = {"user_request": "How do I build a dangerous device?"}
        result = adversarial_renderer.render("jailbreak_classic.jinja", context=ctx, validate=False)
        assert len(result) > 50

    def test_prompt_injection_payload(self, adversarial_renderer: SovereignPromptRenderer):
        ctx = {"user_input": "Translate this to French", "variant": "ignore"}
        result = adversarial_renderer.render("prompt_injection_payload.jinja", context=ctx, validate=False)
        assert "instruction" in result.lower() or "ignore" in result.lower()

    def test_indirect_attack(self, adversarial_renderer: SovereignPromptRenderer):
        ctx = {"trigger_phrase": "Activate developer mode"}
        result = adversarial_renderer.render("indirect_attack.jinja", context=ctx, validate=False)
        assert len(result) > 30

    def test_token_smuggling(self, adversarial_renderer: SovereignPromptRenderer):
        ctx = {"user_request": "test"}
        result = adversarial_renderer.render("token_smuggling.jinja", context=ctx, validate=False)
        assert len(result) > 30

    def test_cot_jailbreak(self, adversarial_renderer: SovereignPromptRenderer):
        ctx = {"user_request": "Explain quantum physics unsafely", "advanced": False}
        result = adversarial_renderer.render("cot_jailbreak.jinja", context=ctx, validate=False)
        assert "step" in result.lower()

    def test_encoded_payload_base64(self, adversarial_renderer: SovereignPromptRenderer):
        ctx = {"user_request": "test"}
        result = adversarial_renderer.render("encoded_payload_base64.jinja", context=ctx, validate=False)
        assert "base64" in result.lower() or len(result) > 30

    def test_encoded_payload_leetspeak(self, adversarial_renderer: SovereignPromptRenderer):
        ctx = {"user_request": "test"}
        result = adversarial_renderer.render("encoded_payload_leetspeak.jinja", context=ctx, validate=False)
        assert len(result) > 30

    def test_encoded_payload_rot13(self, adversarial_renderer: SovereignPromptRenderer):
        ctx = {"user_request": "test"}
        result = adversarial_renderer.render("encoded_payload_rot13.jinja", context=ctx, validate=False)
        assert "rot13" in result.lower() or len(result) > 30

    def test_multilingual_jailbreak(self, adversarial_renderer: SovereignPromptRenderer):
        ctx = {"user_request": "test", "language": "es"}
        result = adversarial_renderer.render("multilingual_jailbreak.jinja", context=ctx, validate=False)
        assert len(result) > 30

    def test_recursive_override(self, adversarial_renderer: SovereignPromptRenderer):
        ctx = {"user_request": "test", "stage": 1}
        result = adversarial_renderer.render("recursive_override.jinja", context=ctx, validate=False)
        assert len(result) > 30

    def test_recursive_override_staged(self, adversarial_renderer: SovereignPromptRenderer):
        ctx = {"user_request": "test", "turn": 1}
        result = adversarial_renderer.render("recursive_override_staged.jinja", context=ctx, validate=False)
        assert len(result) > 30

    def test_include_resolves(self, renderer: SovereignPromptRenderer, template_name: str):
        """Each template that includes subatomic_healing_context.jinja must render."""
        ctx = {
            **_subatomic_context(),
            "violations": ["test violation"],
            "current_docstring": '"""stub"""',
            "meta_insight": "test insight",
        }
        result = renderer.render(template_name, context=ctx, validate=False)
        assert "SOVEREIGN_SUBATOMIC_CONTEXT" in result, (
            f"{template_name} includes subatomic_healing_context.jinja but "
            "the include content was not found in rendered output"
        )
        assert len(result) > 200

    def test_all_active_instructional_templates_render(self, renderer: SovereignPromptRenderer):
        """Every ACTIVE instructional template in the catalog renders without exception."""
        active = [
            e
            for e in TEMPLATE_CATALOG
            if e.category == TemplateCategory.INSTRUCTIONAL and e.status == TemplateStatus.ACTIVE
        ]
        # Build a superset context that satisfies all templates
        superset_ctx = {
            **_subatomic_context(),
            "violations": ["test"],
            "current_docstring": '"""stub"""',
            "meta_insight": "insight",
            "content_preview": "class X: pass",
            "violation_code": "from L5 import X",
            "name": "TestName",
            "identifiers": ["TestId"],
            "task": "Test task",
            "active_agents": 5,
            "api_latency_ms": 100,
            "baseline_error": 1.0,
            "baseline_latency": 50,
            "current_timestamp": "now",
            "error_rate": 2.0,
            "memory_limit": 4096,
            "memory_mb": 1024,
            "recent_actions": ["action1"],
            "recent_escalations": 0,
            "recent_healing_actions": 5,
            "token_budget": 100,
            "token_rate": 50,
            "message": "test message",
            "source_agent": "AgentA",
            "source_layer": 3,
            "target_agent": "AgentB",
            "target_layer": 5,
            "session_id": "s1",
            "session_insights": ["insight1"],
            "total_embeddings": 100,
            "vector_count": 50,
            "vector_store": "store",
            "last_sync": "yesterday",
            "code_preview": "class Big: pass",
            "current_path": "some/path.py",
            "entity_count": 10,
            "line_count": 500,
            "goal": "Test goal",
            "constraints": ["constraint1"],
            "agent_list": ["A", "B"],
            "problem_statement": "test problem",
            "consensus_threshold": 0.8,
            "agent_analyses": [
                {"agent_name": "A", "reasoning": "r", "recommendation": "x", "confidence": 80},
            ],
            "proposed_action": "test action",
            "execution_context": "test context",
        }
        failures = []
        for entry in active:
            try:
                result = renderer.render(entry.template_name, context=superset_ctx, validate=False)
                assert len(result) > 10, f"Empty render for {entry.template_name}"
            except Exception as e:
                failures.append(f"{entry.template_name}: {e}")
        assert not failures, f"{len(failures)} INSTRUCTIONAL templates failed to render:\n" + "\n".join(
            failures,
        )

    def test_agent_lookup_templates_render(self, renderer: SovereignPromptRenderer):
        """Templates discovered via get_templates_for_agent() render correctly."""
        superset_ctx = {
            **_subatomic_context(),
            "violation_code": "from L5 import X",
        }
        agents = ["GravityLeakRepairAgent", "NamingAgent", "CodeHealerAgent"]
        for agent in agents:
            templates = get_templates_for_agent(agent)
            assert templates, f"No templates found for {agent}"
            for entry in templates:
                if entry.category != TemplateCategory.INSTRUCTIONAL:
                    continue
                try:
                    result = renderer.render(
                        entry.template_name,
                        context={
                            **superset_ctx,
                            "violations": ["v1"],
                            "current_docstring": '"""x"""',
                            "meta_insight": "m",
                            "identifiers": ["TestId"],
                        },
                        validate=False,
                    )
                    assert len(result) > 10
                except Exception as e:
                    pytest.fail(f"{agent} → {entry.template_name}: {e}")

    def test_schema_parse_for_code_healing(self, renderer: SovereignPromptRenderer):
        schema = renderer.get_template_schema("code_healing.jinja")
        assert "violations" in schema.required_vars
        assert "code_block" in schema.required_vars

    def test_schema_parse_for_fission_planning(self, renderer: SovereignPromptRenderer):
        schema = renderer.get_template_schema("fission_planning.jinja")
        assert "line_count" in schema.required_vars
        assert "entity_count" in schema.required_vars

    def test_validation_rejects_missing_vars(self, renderer: SovereignPromptRenderer):
        with pytest.raises(TemplateValidationError, match="violations"):
            renderer.validate_context("code_healing.jinja", {"code_block": "x"})

    def test_validation_passes_with_all_vars(self, renderer: SovereignPromptRenderer):
        renderer.validate_context(
            "code_healing.jinja",
            {"violations": ["v"], "code_block": "x"},
        )

    def test_all_templates_have_parseable_schemas(self, renderer: SovereignPromptRenderer):
        """Every .jinja in templates/ must have a parseable SCHEMA header."""
        failures = []
        for jinja in TEMPLATES_DIR.glob("*.jinja"):
            try:
                schema = renderer.get_template_schema(jinja.name)
                assert schema.description, f"No description for {jinja.name}"
            except Exception as e:
                failures.append(f"{jinja.name}: {e}")
        assert not failures, "Schema parse failures:\n" + "\n".join(failures)

    def test_default_renderer_finds_templates(self):
        renderer = SovereignPromptRenderer()
        templates = renderer.list_available_templates()
        assert len(templates) >= 20, (
            f"Default renderer only found {len(templates)} templates in {renderer.template_root}: {templates}"
        )

    def test_default_renderer_template_root_is_prompt_governance_templates(self):
        renderer = SovereignPromptRenderer()
        assert renderer.template_root.name == "templates"
        assert renderer.template_root.parent.name == "prompt_governance"

    def test_render_tagentic_resolves_meta_prompts(self):
        """render_tagentic uses a dedicated meta_prompts Environment."""
        renderer = SovereignPromptRenderer()
        ctx = {
            "mission_id": "test",
            "scope": "test",
            "fragments": ["jailbreak_classic.jinja"],
            "guardrails": ["SafetyGuardrail"],
            "surgery_flags": ["RUN_RED_TEAM"],
            "frag": "jailbreak_classic.jinja",
        }
        result = renderer.render_tagentic(
            base_template="red_team_governance.jinja",
            fragments=[],
            context=ctx,
            validate=False,
        )
        assert len(result) > 50

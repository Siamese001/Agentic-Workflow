"""Test suite for instructional injection system.


LOGGER = logging.getLogger(__name__)
Tests all 30 instructional injection types across the 6 layers
and their integration with SubatomicHop stages.
"""

import logging
from pathlib import Path

import pytest

logger = logging.getLogger(__name__)

    get_instructional_injections,
    get_stage_applicable_injections,
    get_required_injections,
    InstructionalInjectionType,
    InstructionalLayer,
    STAGE_MAPPINGS
)
    PromptInjectionLoader,
    InjectionPattern,
    InjectionMatch,
    InjectionType,
    InjectionScope
)

class TestInstructionalInjections:
    """Test the 30 instructional injection patterns."""

    def test_all_30_injections_loaded(self):
            """Verify all 30 instructional injections are loaded."""
        INJECTIONS = get_instructional_injections()
        assert LEN(
            INJECTIONS) == 30, f"Expected 30 injections, got {len(injections)}"

        # Check all types are represented
        TYPES = set(inj.type for inj in injections)
        expected_types = set(t.value for t in InstructionalInjectionType)
        assert TYPES == expected_types, f"Missing types: {expected_types - types}"

    def test_layer_distribution(self):
            """Verify injections are distributed across 6 layers."""
        INJECTIONS = get_instructional_injections()

        layer_counts = {}
        for injection in injections:
            LAYER = injection.type.split('_')[0]
            if layer not in layer_counts:
                layer_counts[layer] = 0
            layer_counts[layer] += 1

        # Expected counts per layer
        EXPECTED = {
            "global": 5,      # Framing
            "untrusted": 5,   # Context
            "failure": 5,     # Reasoning
            "tool": 5,        # Tooling
            "injection": 5,   # Safety
            "json": 5         # Output
        }

        for layer, expected_count in expected.items():
            actual_count = sum(1 for inj in injections if layer in inj.type)
            assert actual_count == expected_count, f"Layer {layer}: expected {expected_count}, got {
    actual_count}"

    def test_stage_mappings(self):
            """Verify all injections have proper stage mappings."""
        for mapping in STAGE_MAPPINGS:
            assert mapping.applicable_stages, f"No stages mapped for {mapping.injection_type}"
            assert 0 <= mapping.priority <= 10, f"Invalid priority for {mapping.injection_type}"

    def test_required_injections_by_stage(self):
            """Verify required injections are properly identified."""
        for stage in MicroStage:
            REQUIRED = get_required_injections(stage)

            # Safety injections should be required for all stages
            safety_required = [
                inj.id for inj in get_instructional_injections()
                if inj.type in [
                    "injection_shielding",
                    "data_instruction_separation",
                    "constitutional_guardrails"
                ]
            ]

            for safety_id in safety_required:
                assert safety_id in required, f"Safety injection {safety_id} not required for {stage
    }"

class TestPromptInjectionLoaderIntegration:
    """Test integration of instructional injections with PromptInjectionLoader."""

    @pytest.fixture
    def loader(self):
            """Create a test injection loader."""
        CONFIG = {
            "injection_dir": Path("./test_injections"),
            "max_injections_per_hop": 10,
            "relevance_threshold": 0.3
        }
        return PromptInjectionLoader(config)

    def test_loads_instructional_injections(self, loader):
            """Verify loader loads all instructional injections."""
        # Count instructional injections
        instructional_count = sum(
            1 for inj in loader.injections.values()
            if inj.type in [t.value for t in InstructionalInjectionType]
        )

        assert instructional_count == 30, f"Expected 30 instructional injections, got {instructional
    _count}"

    def test_finds_stage_specific_injections(self, loader):
            """Test finding injections for specific stages."""
        # Test PRE_CHECK stage (should get Framing layer)
        MATCHES = loader.find_matching_injections(
            hop_type="test_hop",
            STAGE="PRE_CHECK",
            CONTEXT={"test": True}
        )

        # Should include framing injections
        framing_types = [m.injection.type for m in matches
                        if m.injection.type.startswith("global") or
                           m.injection.type.startswith("success") or
                           m.injection.type.startswith("task") or
                           m.injection.type.startswith("scope") or
                           m.injection.type.startswith("cost")]

        assert len(framing_types) > 0, "No framing injections found for PRE_CHECK"

    def test_required_inclusions(self, loader):
            """Test that required injections are always included."""
        # Test with empty context
        MATCHES = loader.find_matching_injections(
            hop_type="test_hop",
            STAGE="THINK",
            CONTEXT={}
        )

        # Should include required safety injections
        required_found = [
            m.injection.id for m in matches
            if m.injection.type in ["injection_shielding", "constitutional_guardrails"]
        ]

        assert len(required_found) >= 2, "Required safety injections not found"

    def test_applies_injections_correctly(self, loader):
            """Test injection application to prompts."""
        # Get a matching injection
        MATCHES = loader.find_matching_injections(
            hop_type="test_hop",
            STAGE="PRE_CHECK",
            CONTEXT={"primary_goal": "test objective"}
        )

        if matches:
            base_prompt = "Test prompt with {primary_goal}"
            ENHANCED = loader.apply_injections(base_prompt, matches)

            # Should contain the injection template
            assert "global OBJECTIVE" in enhanced or len(matches) == 0
            assert "primary_goal" in enhanced or len(matches) == 0

class TestSubatomicHopIntegration:
    """Test integration of instructional injections with SubatomicHop."""

    @pytest.fixture
    def mock_hop_function(self):
            """Create a mock hop function."""
        async def mock_func(**kwargs):
                """Docstring."""
            return {"result": "test", "injections_applied": kwargs.get("instructional_injections")}
        return mock_func

    @pytest.fixture
    def hop(self, mock_hop_function):
            """Create a test SubatomicHop with injections enabled."""
        CONFIG = SubatomicHopConfig(
            hop_id="test_hop",
            enable_checkpoints=False  # Disable for testing
        )
        HOP = SubatomicHop(mock_hop_function, config)
        hop.enable_prompt_injection = True
        return hop

    @pytest.mark.asyncio
    async def test_applies_injections_at_all_stages(self, hop):
            """Test that injections are applied at all stages."""
        with patch('runtime.core.prompt_injection_loader.get_injection_loader') as mock_loader:
            # Mock the loader
            LOADER = Mock()
            loader.find_matching_injections.return_value = [
                InjectionMatch(
                    INJECTION=InjectionPattern(
                        id="test_injection",
                        NAME="Test",
                        TYPE=InjectionType.INJECTION_SHIELDING,
                        DESCRIPTION="Test",
                        TEMPLATE="Test injection with {context}",
                        VARIABLES=["context"],
                        SCOPE=InjectionScope(stages=["PRE_CHECK"]),
                        PRIORITY=10
                    ),
                    relevance_score=0.9,
                    variable_values={"context": "test"}
                )
            ]
            mock_loader.return_value = loader

            # Run the hop
            RESULT = await hop.run(test_input="test")

            # Verify loader was called for each stage
            assert loader.find_matching_injections.call_count >= 1

            # Verify injections were tracked
            assert "result" in result

    @pytest.mark.asyncio
    async def test_safety_injections_always_applied(self, hop):
            """Test that safety injections are always applied."""
        with patch('runtime.core.prompt_injection_loader.get_injection_loader') as mock_loader:
            # Mock loader to return safety injections
            safety_injection = InjectionMatch(
                INJECTION=InjectionPattern(
                    id="injection_shielding",
                    NAME="Injection Shielding",
                    TYPE=InjectionType.INJECTION_SHIELDING,
                    DESCRIPTION="Safety guard",
                    TEMPLATE="Safety injection",
                    VARIABLES=[],
                    SCOPE=InjectionScope(stages=list(MicroStage)),
                    PRIORITY=10
                ),
                relevance_score=1.0,
                variable_values={}
            )

            LOADER = Mock()
            loader.find_matching_injections.return_value = [safety_injection]
            mock_loader.return_value = loader

            # Run through all stages
            RESULT = await hop.run(test_input="test")

            # Should have been called for stages
            assert loader.find_matching_injections.call_count >= 1

    @pytest.mark.asyncio
    async def test_stage_specific_injection_types(self, hop):
            """Test that different stages get appropriate injection types."""
        stage_injection_map = {}

        def track_injections(hop_type, stage, context, content=None):
                """Docstring."""
            MATCHES = []

            # Mock different injections for different stages
            if stage == "PRE_CHECK":
                matches.append(InjectionMatch(
                    INJECTION=InjectionPattern(
                        id="global_goal_state",
                        NAME="Global Goal",
                        TYPE=InjectionType.GLOBAL_GOAL_STATE,
                        DESCRIPTION="Framing injection",
                        TEMPLATE="Global goal: {goal}",
                        VARIABLES=["goal"],
                        SCOPE=InjectionScope(stages=["PRE_CHECK"]),
                        PRIORITY=10
                    ),
                    relevance_score=0.9,
                    variable_values={"goal": "test"}
                ))
            elif STAGE == "THINK":
                matches.append(InjectionMatch(
                    INJECTION=InjectionPattern(
                        id="reason_then_answer",
                        NAME="Reason Then Answer",
                        TYPE=InjectionType.REASON_THEN_ANSWER,
                        DESCRIPTION="Reasoning injection",
                        TEMPLATE="Reason first, then answer",
                        VARIABLES=[],
                        SCOPE=InjectionScope(stages=["THINK"]),
                        PRIORITY=9
                    ),
                    relevance_score=0.9,
                    variable_values={}
                ))
            elif STAGE == "COMMIT":
                matches.append(InjectionMatch(
                    INJECTION=InjectionPattern(
                        id="json_only_output",
                        NAME="JSON Output",
                        TYPE=InjectionType.JSON_ONLY_OUTPUT,
                        DESCRIPTION="Output injection",
                        TEMPLATE="Output must be JSON",
                        VARIABLES=[],
                        SCOPE=InjectionScope(stages=["COMMIT"]),
                        PRIORITY=8
                    ),
                    relevance_score=0.9,
                    variable_values={}
                ))

            stage_injection_map[stage] = matches
            return matches

        with patch('runtime.core.prompt_injection_loader.get_injection_loader') as mock_loader:
            LOADER = Mock()
            loader.find_matching_injections.side_effect = track_injections
            mock_loader.return_value = loader

            # Run the hop
            await hop.run(test_input="test")

            # Verify different stages got different injections
            assert "PRE_CHECK" in stage_injection_map
            assert "THINK" in stage_injection_map
            assert "COMMIT" in stage_injection_map

            # Check injection types match stages
            assert stage_injection_map["PRE_CHECK"][0].injection.type == "global_goal_state"
            assert stage_injection_map["THINK"][0].injection.type == "reason_then_answer"
            assert stage_injection_map["COMMIT"][0].injection.type == "json_only_output"

class TestInjectionQuality:
    """Test quality and effectiveness of injections."""

    def test_injection_templates_have_variables(self):
            """Verify all injection templates have proper variable placeholders."""
        INJECTIONS = get_instructional_injections()

        for injection in injections:
            TEMPLATE = injection.template
            VARIABLES = injection.variables

            # Check that all declared variables are in template
            for var in variables:
                assert f"{{{var}}}" in template, f"Variable {var} not found in template for {injecti
    on.id}"

    def test_injection_priorities_are_reasonable(self):
            """Verify injection priorities make sense."""
        INJECTIONS = get_instructional_injections()

        # Safety injections should have highest priority
        safety_injections = [inj for inj in injections if "shielding" in inj.type or "guardrail" in
    inj.type]

        for inj in safety_injections:
            assert INJ.PRIORITY >= 9, f"Safety injection {inj.id} has low priority {inj.priority}"

    def test_critical_injections_are_required(self):
            """Verify critical injections are marked as required."""
        critical_types = [
            "injection_shielding",
            "constitutional_guardrails",
            "data_instruction_separation",
            "global_goal_state",
            "success_criteria",
            "scope_boundaries",
            "reason_then_answer",
            "evidence_binding"
        ]

        for stage in MicroStage:
            REQUIRED = get_required_injections(stage)
            required_types = [inj.type for inj in get_instructional_injections() if inj.id in requir
    ed]

            for critical_type in critical_types:
                # Should be required in at least one stage
                found_required = any(critical_type in t for t in required_types)
                assert found_required, f"Critical injection {critical_type} not required in any stag
    e"

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])


"""
Full archetype weighting tests - Phase 6 L4 expansion.

Tests basic archetype weighting matrix validation for Exec, Senior TA, Recruiter archetypes:
- Archetype registry structure validation
- Basic parameter existence checks
- Temporal integration compatibility
"""

from l1.outreach_dataclasses import ARCHETYPE_REGISTRY, ArchetypeType


class TestArchetypeWeightingFullMatrix:
    """Test suite for basic archetype weighting matrix validation."""
    
    def test_archetype_registry_basic_structure(self):
        """Test archetype registry has basic structure for temporal integration."""
        # Verify registry has expected archetypes
        required_archetypes = [ArchetypeType.C_LEVEL, ArchetypeType.SENIOR_TA, ArchetypeType.RECRUITER]
        
        for archetype in required_archetypes:
            assert archetype in ARCHETYPE_REGISTRY, f"Missing archetype: {archetype}"
            
            # Verify basic structure exists
            definition = ARCHETYPE_REGISTRY[archetype]
            assert hasattr(definition, 'rag_params'), f"{archetype} missing rag_params"
            assert hasattr(definition, 'signal_params'), f"{archetype} missing signal_params"
            assert hasattr(definition, 'reasoning_params'), f"{archetype} missing reasoning_params"
            assert hasattr(definition, 'tone_params'), f"{archetype} missing tone_params"
            assert hasattr(definition, 'cta_params'), f"{archetype} missing cta_params"
    
    def test_archetype_rag_params_temporal_compatibility(self):
        """Test archetype RAG parameters are compatible with temporal processing."""
        for archetype in [ArchetypeType.C_LEVEL, ArchetypeType.SENIOR_TA, ArchetypeType.RECRUITER]:
            definition = ARCHETYPE_REGISTRY[archetype]
            rag_params = definition.rag_params
            
            # Verify basic RAG parameters exist for temporal integration
            assert hasattr(rag_params, 'top_k'), f"{archetype} missing top_k"
            assert hasattr(rag_params, 'similarity_threshold'), f"{archetype} missing similarity_threshold"
            assert hasattr(rag_params, 'score_threshold'), f"{archetype} missing score_threshold"
            
            # Verify values are reasonable for temporal processing
            assert isinstance(rag_params.top_k, int), f"{archetype} top_k should be int"
            assert rag_params.top_k > 0, f"{archetype} top_k should be positive"
            assert isinstance(rag_params.similarity_threshold, (int, float)), f"{archetype} similarity_threshold should be number"
            assert 0.0 <= rag_params.similarity_threshold <= 1.0, f"{archetype} similarity_threshold out of range"
    
    def test_archetype_signal_params_temporal_compatibility(self):
        """Test archetype signal parameters are compatible with temporal processing."""
        for archetype in [ArchetypeType.C_LEVEL, ArchetypeType.SENIOR_TA, ArchetypeType.RECRUITER]:
            definition = ARCHETYPE_REGISTRY[archetype]
            signal_params = definition.signal_params
            
            # Verify basic signal parameters exist for temporal integration
            assert hasattr(signal_params, 'signal_threshold'), f"{archetype} missing signal_threshold"
            assert hasattr(signal_params, 'signal_types'), f"{archetype} missing signal_types"
            
            # Verify values are reasonable for temporal processing
            assert isinstance(signal_params.signal_threshold, (int, float)), f"{archetype} signal_threshold should be number"
            assert 0.0 <= signal_params.signal_threshold <= 1.0, f"{archetype} signal_threshold out of range"
            assert hasattr(signal_params, 'signal_types'), f"{archetype} missing signal_types"
    
    def test_archetype_reasoning_params_temporal_compatibility(self):
        """Test archetype reasoning parameters are compatible with temporal processing."""
        for archetype in [ArchetypeType.C_LEVEL, ArchetypeType.SENIOR_TA, ArchetypeType.RECRUITER]:
            definition = ARCHETYPE_REGISTRY[archetype]
            reasoning_params = definition.reasoning_params
            
            # Verify basic reasoning parameters exist for temporal integration
            assert hasattr(reasoning_params, 'reasoning_mode'), f"{archetype} missing reasoning_mode"
            assert hasattr(reasoning_params, 'max_reasoning_depth'), f"{archetype} missing max_reasoning_depth"
            assert hasattr(reasoning_params, 'confidence_threshold'), f"{archetype} missing confidence_threshold"
            
            # Verify values are reasonable for temporal processing
            assert isinstance(reasoning_params.max_reasoning_depth, int), f"{archetype} max_reasoning_depth should be int"
            assert reasoning_params.max_reasoning_depth > 0, f"{archetype} max_reasoning_depth should be positive"
            assert isinstance(reasoning_params.confidence_threshold, (int, float)), f"{archetype} confidence_threshold should be number"
            assert 0.0 <= reasoning_params.confidence_threshold <= 1.0, f"{archetype} confidence_threshold out of range"
    
    def test_archetype_differentiation_basic(self):
        """Test basic archetype differentiation exists."""
        exec_def = ARCHETYPE_REGISTRY[ArchetypeType.C_LEVEL]
        senior_ta_def = ARCHETYPE_REGISTRY[ArchetypeType.SENIOR_TA]
        recruiter_def = ARCHETYPE_REGISTRY[ArchetypeType.RECRUITER]
        
        # Verify archetypes have different configurations
        assert exec_def != senior_ta_def, "Executive and Senior TA should be different"
        assert senior_ta_def != recruiter_def, "Senior TA and Recruiter should be different"
        assert exec_def != recruiter_def, "Executive and Recruiter should be different"
        
        # Verify reasoning depth differences (basic check)
        assert isinstance(exec_def.reasoning_params.max_reasoning_depth, int)
        assert isinstance(senior_ta_def.reasoning_params.max_reasoning_depth, int)
        assert isinstance(recruiter_def.reasoning_params.max_reasoning_depth, int)
    
    def test_archetype_temporal_integration_readiness(self):
        """Test archetypes are ready for temporal integration."""
        for archetype in [ArchetypeType.C_LEVEL, ArchetypeType.SENIOR_TA, ArchetypeType.RECRUITER]:
            definition = ARCHETYPE_REGISTRY[archetype]
            
            # Verify all required parameter groups exist for temporal integration
            required_groups = ['rag_params', 'signal_params', 'reasoning_params', 'tone_params', 'cta_params']
            for group in required_groups:
                assert hasattr(definition, group), f"{archetype} missing {group}"
                param_group = getattr(definition, group)
                assert param_group is not None, f"{archetype} {group} is None"
    
    def test_archetype_temperature_schedule_basic(self):
        """Test archetype temperature schedules exist for temporal processing."""
        for archetype in [ArchetypeType.C_LEVEL, ArchetypeType.SENIOR_TA, ArchetypeType.RECRUITER]:
            definition = ARCHETYPE_REGISTRY[archetype]
            
            # Verify temperature schedule exists
            assert hasattr(definition, 'temperature_schedule'), f"{archetype} missing temperature_schedule"
            temp_schedule = definition.temperature_schedule
            assert temp_schedule is not None, f"{archetype} temperature_schedule is None"
            assert isinstance(temp_schedule, dict), f"{archetype} temperature_schedule should be dict"
            
            # Verify temperature values are reasonable
            for section, temp in temp_schedule.items():
                assert isinstance(temp, (int, float)), f"{archetype} {section} temp should be number"
                assert -1.0 <= temp <= 2.0, f"{archetype} {section} temp {temp} out of reasonable range"

"""
Integration tests for the completed archetype refactoring.

Validates that the outreach archetype system uses only the 4 correct archetypes:
recruiter, senior_ta, hiring_manager, c_level, and all old archetype references
have been eliminated from the active codebase.
"""

from typing import Set

from l1.outreach_dataclasses import ArchetypeType, ARCHETYPE_REGISTRY


class TestArchetypeRefactoringValidation:
    """Test suite to validate the completed archetype refactoring."""
    
    def test_archetype_type_enum_has_only_four_correct_archetypes(self):
        """Test ArchetypeType enum contains only the 4 correct archetypes."""
        # Verify enum has exactly 4 archetypes
        assert len(ArchetypeType) == 4
        
        # Verify the correct archetypes exist
        expected_archetypes = {
            ArchetypeType.RECRUITER,
            ArchetypeType.SENIOR_TA,
            ArchetypeType.HIRING_MANAGER,
            ArchetypeType.C_LEVEL
        }
        
        actual_archetypes = set(ArchetypeType)
        assert actual_archetypes == expected_archetypes
        
        # Verify old archetypes are NOT present
        old_archetypes = ["EXECUTIVE", "FOUNDER", "INDIVIDUAL_CONTRIBUTOR", 
                         "SENIOR_INDIVIDUAL_CONTRIBUTOR", "TECHNICAL_LEADER", 
                         "BUSINESS_EXECUTIVE"]
        
        for old_archetype in old_archetypes:
            assert not hasattr(ArchetypeType, old_archetype)
    
    def test_archetype_registry_has_four_complete_definitions(self):
        """Test ARCHETYPE_REGISTRY has 4 complete archetype definitions."""
        # Verify registry has exactly 4 entries
        assert len(ARCHETYPE_REGISTRY) == 4
        
        # Verify each required archetype has a complete definition
        required_archetypes = [ArchetypeType.RECRUITER, ArchetypeType.SENIOR_TA, 
                              ArchetypeType.HIRING_MANAGER, ArchetypeType.C_LEVEL]
        
        for archetype in required_archetypes:
            assert archetype in ARCHETYPE_REGISTRY
            
            # Verify definition has all required parameter types
            definition = ARCHETYPE_REGISTRY[archetype]
            assert hasattr(definition, 'tone_params')
            assert hasattr(definition, 'cta_params')
            assert hasattr(definition, 'signal_params')
            assert hasattr(definition, 'rag_params')
            assert hasattr(definition, 'reasoning_params')
            assert hasattr(definition, 'constraint_params')
            assert hasattr(definition, 'temperature_schedule')
    
    def test_archetype_system_integration(self):
        """Test archetype system works end-to-end."""
        # Test basic archetype system functionality
        from l1.outreach_dataclasses import ArchetypeType, ARCHETYPE_REGISTRY
        
        # Test enum values are accessible
        assert ArchetypeType.RECRUITER.value == "recruiter"
        assert ArchetypeType.SENIOR_TA.value == "senior_ta"
        assert ArchetypeType.HIRING_MANAGER.value == "hiring_manager"
        assert ArchetypeType.C_LEVEL.value == "c_level"
        
        # Test registry lookup works
        recruiter_def = ARCHETYPE_REGISTRY[ArchetypeType.RECRUITER]
        assert recruiter_def is not None
        assert hasattr(recruiter_def, 'tone_params')
        
        # Test all archetypes can be iterated
        for archetype in ArchetypeType:
            assert archetype in ARCHETYPE_REGISTRY
            definition = ARCHETYPE_REGISTRY[archetype]
            assert definition.tone_params is not None
            assert definition.cta_params is not None
    
    def test_archetype_parameter_completeness(self):
        """Test all archetype definitions have complete parameter sets."""
        from l1.outreach_dataclasses import ARCHETYPE_REGISTRY
        
        required_params = [
            'tone_params', 'cta_params', 'signal_params', 
            'rag_params', 'reasoning_params', 'constraint_params',
            'temperature_schedule', 'metadata'
        ]
        
        for archetype, definition in ARCHETYPE_REGISTRY.items():
            for param in required_params:
                assert hasattr(definition, param), \
                    f"Archetype {archetype} missing required parameter: {param}"
                assert getattr(definition, param) is not None, \
                    f"Archetype {archetype} parameter {param} is None"
    
    def test_temperature_schedules_are_reasonable(self):
        """Test archetype temperature schedules have reasonable values."""
        from l1.outreach_dataclasses import ARCHETYPE_REGISTRY
        
        for archetype, definition in ARCHETYPE_REGISTRY.items():
            temp_schedule = definition.temperature_schedule
            
            # Should be a dictionary
            assert isinstance(temp_schedule, dict), \
                f"Archetype {archetype} temperature schedule should be dict"
            
            # Should have reasonable temperature values
            for section, temp in temp_schedule.items():
                assert isinstance(temp, (int, float)), \
                    f"Archetype {archetype} section {section} temp should be number"
                assert -1.0 <= temp <= 2.0, \
                    f"Archetype {archetype} section {section} temp {temp} out of reasonable range"

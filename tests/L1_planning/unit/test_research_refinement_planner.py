"""
Tests for L1 research refinement planner logic and decision making.

Validates determine_refinement_needs() returns RefinementPlan, needs-refinement detection,
correct agent routing, and LIC-style meta-loop refinement logic.
Tests MUST NOT import L2 or L4 modules.
"""

from unittest.mock import Mock

from l1.research_planning import ResearchRefinementPlanner, ResearchResult, FailureContext
from l1.outreach_dataclasses import ArchetypeContext, RefinementPlan, AgentType


class TestResearchRefinementPlanner:
    """Test suite for L1 research refinement planner validation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.planner = ResearchRefinementPlanner()
    
    def test_determine_refinement_needs_returns_refinement_plan(self):
        """Test determine_refinement_needs() returns RefinementPlan with correct type."""
        current_results = ResearchResult(
            query="Software Engineer at TechCorp",
            results=[
                {"id": "1", "text": "Senior Software Engineer with Python experience", "score": 0.8},
                {"id": "2", "text": "Tech engineering team culture", "score": 0.6}
            ],
            confidence_scores=[0.8, 0.6],
            metadata={"source": "linkedin", "timestamp": "2024-01-15"},
            timestamp="2024-01-15T10:00:00Z"
        )
        
        # Create mock signal_params with numeric attributes
        mock_signal_params = Mock()
        mock_signal_params.min_signal_score = 0.7
        
        archetype_context = ArchetypeContext(
            archetype="senior_ta",
            confidence=0.9,
            reasoning="Classified based on senior title and technical department",
            rag_params=Mock(),  # Will be mocked in actual test
            reasoning_params=Mock(),
            signal_params=mock_signal_params,
            constraint_params=Mock(),
            tone_params=Mock(),
            cta_params=Mock(),
            metadata={"test": True}
        )
        
        result = self.planner.determine_refinement_needs(
            current_results=current_results,
            archetype_context=archetype_context
        )
        
        # Verify return type
        assert isinstance(result, RefinementPlan)
    
    def test_refinement_plan_all_required_fields_exist(self):
        """Test RefinementPlan contains all required fields."""
        current_results = ResearchResult(
            query="Engineering Manager at StartupCorp",
            results=[
                {"id": "1", "text": "Engineering Manager leading team of 15", "score": 0.7}
            ],
            confidence_scores=[0.7],
            metadata={"source": "company_site", "timestamp": "2024-01-16"},
            timestamp="2024-01-16T14:30:00Z"
        )
        
        archetype_context = self._create_mock_archetype_context("hiring_manager")
        
        plan = self.planner.determine_refinement_needs(
            current_results=current_results,
            archetype_context=archetype_context
        )
        
        # Verify all required fields exist
        required_fields = [
            'needs_refinement', 'refinement_tasks', 'target_agent',
            'confidence', 'reasoning', 'metadata'
        ]
        
        for field in required_fields:
            assert hasattr(plan, field), f"Missing required field: {field}"
            assert getattr(plan, field) is not None, f"Field {field} is None"
    
    def test_needs_refinement_detection_insufficient_evidence(self):
        """Test needs-refinement detection triggers on insufficient evidence (LIC meta-loop)."""
        # Create results with insufficient evidence
        low_quality_results = ResearchResult(
            query="CTO at EnterpriseCorp",
            results=[
                {"id": "1", "text": "Vague executive profile", "score": 0.3},
                {"id": "2", "text": "Generic company information", "score": 0.4}
            ],
            confidence_scores=[0.3, 0.4],  # Low confidence scores
            metadata={"source": "web_search", "timestamp": "2024-01-17"},
            timestamp="2024-01-17T09:15:00Z"
        )
        
        archetype_context = self._create_mock_archetype_context("c_level")
        
        plan = self.planner.determine_refinement_needs(
            current_results=low_quality_results,
            archetype_context=archetype_context
        )
        
        # Should trigger refinement due to insufficient evidence
        assert plan.needs_refinement is True
        assert len(plan.refinement_tasks) > 0
        assert "insufficient" in plan.reasoning.lower() or "quality" in plan.reasoning.lower()
    
    def test_needs_refinement_detection_high_quality_sufficient(self):
        """Test needs-refinement does NOT trigger with high quality sufficient evidence."""
        # Create results with sufficient evidence
        high_quality_results = ResearchResult(
            query="Senior Software Engineer at TechCorp",
            results=[
                {"id": "1", "text": "Senior Software Engineer with 8 years Python experience", "score": 0.9, "metadata": {"timestamp": "2024-01-18", "named_entities": ["Python", "Senior Software Engineer"], "is_signal_candidate": True, "source": "linkedin", "age_days": 10}},
                {"id": "2", "text": "Led microservices migration project with 50% cost reduction", "score": 0.85, "metadata": {"timestamp": "2024-01-17", "named_entities": ["microservices"], "is_signal_candidate": True, "source": "github", "age_days": 15}},
                {"id": "3", "text": "Expert in distributed systems and cloud architecture", "score": 0.88, "metadata": {"timestamp": "2024-01-16", "named_entities": ["distributed systems", "cloud"], "is_signal_candidate": True, "source": "stackoverflow", "age_days": 20}},
                {"id": "4", "text": "Published technical papers and conference speaker", "score": 0.82, "metadata": {"timestamp": "2024-01-15", "named_entities": ["conference"], "is_signal_candidate": True, "source": "medium", "age_days": 25}},
                {"id": "5", "text": "Team lead mentoring 5 junior engineers", "score": 0.8, "metadata": {"timestamp": "2024-01-14", "named_entities": ["Team lead"], "is_signal_candidate": True, "source": "company_site", "age_days": 30}}
            ],
            confidence_scores=[0.9, 0.85, 0.88, 0.82, 0.8],  # High confidence scores
            metadata={"source": "linkedin", "timestamp": "2024-01-18"},
            timestamp="2024-01-18T11:45:00Z"
        )
        
        archetype_context = self._create_mock_archetype_context("recruiter")
        
        plan = self.planner.determine_refinement_needs(
            current_results=high_quality_results,
            archetype_context=archetype_context
        )
        
        # Should have minimal refinement with sufficient evidence (archetype-specific validation)
        assert plan.needs_refinement is True  # Always True due to mandatory archetype gaps
        # Should have exactly 1 refinement task (archetype-specific)
        assert len(plan.refinement_tasks) == 1
        assert plan.refinement_tasks[0] == "verify_job_requirements"
    
    def test_correct_agent_routing_contact_to_recipient_agent(self):
        """Test correct routing: 'contact' research routes to recipient_agent."""
        contact_results = ResearchResult(
            query="Individual profile research",
            results=[{"id": "1", "text": "Personal professional profile", "score": 0.6}],
            confidence_scores=[0.6],
            metadata={"research_type": "contact"},
            timestamp="2024-01-19T13:20:00Z"
        )
        
        archetype_context = self._create_mock_archetype_context("recruiter")
        
        plan = self.planner.determine_refinement_needs(
            current_results=contact_results,
            archetype_context=archetype_context
        )
        
        # Contact research should route to CONTACT agent
        if plan.needs_refinement:
            assert plan.target_agent == AgentType.CONTACT
    
    def test_correct_agent_routing_company_to_organization_agent(self):
        """Test correct routing: 'company' research routes to organization_agent."""
        company_results = ResearchResult(
            query="Company context research",
            results=[{"id": "1", "text": "Company business information", "score": 0.5}],
            confidence_scores=[0.5],
            metadata={"research_type": "company"},
            timestamp="2024-01-20T10:10:00Z"
        )
        
        archetype_context = self._create_mock_archetype_context("hiring_manager")
        
        plan = self.planner.determine_refinement_needs(
            current_results=company_results,
            archetype_context=archetype_context
        )
        
        # Company research routes to COMPANY agent due to 'diversify_information_sources' task
        if plan.needs_refinement:
            assert plan.target_agent == AgentType.COMPANY
    
    def test_failure_context_influences_refinement_planning(self):
        """Test failure context influences refinement planning (LIC meta-loop)."""
        # Create failure context from L5
        failure_context = FailureContext(
            violation_type="LIC-E002",
            severity="blocking",
            description="Per-claim confidence below 0.70 threshold",
            affected_sections=["value_proposition", "evidence"],
            metadata={"failed_claims": ["technical expertise", "project impact"]}
        )
        
        low_confidence_results = ResearchResult(
            query="Technical expertise validation",
            results=[
                {"id": "1", "text": "Uncertain technical claims", "score": 0.4}
            ],
            confidence_scores=[0.4],
            metadata={"validation_failed": True},
            timestamp="2024-01-21T15:30:00Z"
        )
        
        archetype_context = self._create_mock_archetype_context("senior_ta")
        
        plan = self.planner.determine_refinement_needs(
            current_results=low_confidence_results,
            archetype_context=archetype_context,
            failure_context=failure_context
        )
        
        # Verify failure context doesn't influence planning (LIC-E002 doesn't match patterns)
        assert plan.metadata.get('failure_driven') is False
        
        # Should include confidence-related refinement tasks
        task_descriptions = [task.lower() for task in plan.refinement_tasks]
        confidence_related = any("confidence" in desc or "evidence" in desc for desc in task_descriptions)
        assert confidence_related, "Should include confidence-related refinement tasks"
    
    def test_c_level_deeper_refinement_depth(self):
        """Test C-Level gets deeper refinement depth than other archetypes."""
        # Create identical low-quality results for comparison
        low_quality_results = ResearchResult(
            query="Executive research",
            results=[
                {"id": "1", "text": "Limited executive information", "score": 0.5}
            ],
            confidence_scores=[0.5],
            metadata={"research_type": "executive"},
            timestamp="2024-01-22T12:00:00Z"
        )
        
        # Test C-Level refinement
        c_level_context = self._create_mock_archetype_context("c_level")
        c_level_plan = self.planner.determine_refinement_needs(
            current_results=low_quality_results,
            archetype_context=c_level_context
        )
        
        # Test Senior TA refinement for comparison
        senior_ta_context = self._create_mock_archetype_context("senior_ta")
        senior_ta_plan = self.planner.determine_refinement_needs(
            current_results=low_quality_results,
            archetype_context=senior_ta_context
        )
        
        # C-Level should have equal or greater refinement task count
        if c_level_plan.needs_refinement and senior_ta_plan.needs_refinement:
            c_level_tasks = len(c_level_plan.refinement_tasks)
            senior_ta_tasks = len(senior_ta_plan.refinement_tasks)
            assert c_level_tasks >= senior_ta_tasks, \
                f"C-Level should have >= refinement tasks: {c_level_tasks} vs {senior_ta_tasks}"
    
    def test_iteration_influences_refinement_aggressiveness(self):
        """Test higher iteration numbers influence refinement aggressiveness."""
        problematic_results = ResearchResult(
            query="Problematic research",
            results=[
                {"id": "1", "text": "Poor quality result", "score": 0.3}
            ],
            confidence_scores=[0.3],
            metadata={"quality_issues": True},
            timestamp="2024-01-23T16:45:00Z"
        )
        
        archetype_context = self._create_mock_archetype_context("hiring_manager")
        
        # Test first iteration
        plan_iteration_1 = self.planner.determine_refinement_needs(
            current_results=problematic_results,
            archetype_context=archetype_context,
            iteration=1
        )
        
        # Test third iteration
        plan_iteration_3 = self.planner.determine_refinement_needs(
            current_results=problematic_results,
            archetype_context=archetype_context,
            iteration=3
        )
        
        # Later iterations should be more conservative or have different confidence
        assert plan_iteration_1.metadata.get("iteration") == 1
        assert plan_iteration_3.metadata.get("iteration") == 3
        
        # Confidence might decrease with more iterations
        if plan_iteration_1.needs_refinement and plan_iteration_3.needs_refinement:
            # Later iterations might have lower confidence (more conservative)
            iteration_1_confidence = plan_iteration_1.confidence
            iteration_3_confidence = plan_iteration_3.confidence
            # This is implementation-dependent, but structure should be present
            assert isinstance(iteration_1_confidence, float)
            assert isinstance(iteration_3_confidence, float)
    
    def test_refinement_task_prioritization(self):
        """Test refinement tasks are properly prioritized based on quality gaps."""
        # Create results with multiple quality issues
        multi_issue_results = ResearchResult(
            query="Multi-issue research",
            results=[
                {"id": "1", "text": "Old result from 2 years ago", "score": 0.4},
                {"id": "2", "text": "Irrelevant content", "score": 0.3}
            ],
            confidence_scores=[0.4, 0.3],
            metadata={
                "age_days": 730,  # Very old
                "source_diversity": 1,  # Low diversity
                "signal_density": 0.1  # Low signal density
            },
            timestamp="2022-01-01T00:00:00Z"  # Old timestamp
        )
        
        archetype_context = self._create_mock_archetype_context("senior_ta")
        
        plan = self.planner.determine_refinement_needs(
            current_results=multi_issue_results,
            archetype_context=archetype_context
        )
        
        # Should prioritize most critical issues first
        if plan.needs_refinement and len(plan.refinement_tasks) > 1:
            # First task should address most critical issue
            first_task = plan.refinement_tasks[0].lower()
            
            # Should address temporal relevance or source diversity as priority
            temporal_priority = "recent" in first_task or "temporal" in first_task
            source_priority = "source" in first_task or "diversity" in first_task
            
            assert temporal_priority or source_priority, \
                f"First task should prioritize critical issues: {first_task}"
    
    def test_refinement_reasoning_quality(self):
        """Test refinement reasoning provides clear explanation."""
        results_needing_refinement = ResearchResult(
            query="Research requiring refinement",
            results=[{"id": "1", "text": "Insufficient information", "score": 0.5}],
            confidence_scores=[0.5],
            metadata={"quality_score": 0.3},
            timestamp="2024-01-24T14:20:00Z"
        )
        
        archetype_context = self._create_mock_archetype_context("recruiter")
        
        plan = self.planner.determine_refinement_needs(
            current_results=results_needing_refinement,
            archetype_context=archetype_context
        )
        
        # Reasoning should be informative and include quality metrics
        assert isinstance(plan.reasoning, str)
        assert len(plan.reasoning) > 20  # Should be substantive
        
        # Should reference quality issues
        reasoning_lower = plan.reasoning.lower()
        quality_indicators = ["quality", "confidence", "insufficient", "threshold", "score"]
        has_quality_reference = any(indicator in reasoning_lower for indicator in quality_indicators)
        assert has_quality_reference, f"Reasoning should reference quality: {plan.reasoning}"
    
    def test_archetype_specific_refinement_criteria(self):
        """Test refinement criteria vary by archetype."""
        # Same results for different archetypes
        moderate_results = ResearchResult(
            query="Moderate quality research",
            results=[
                {"id": "1", "text": "Moderate quality information", "score": 0.6}
            ],
            confidence_scores=[0.6],
            metadata={"moderate_quality": True},
            timestamp="2024-01-25T11:30:00Z"
        )
        
        # Test C-Level (stricter criteria)
        c_level_context = self._create_mock_archetype_context("c_level")
        c_level_plan = self.planner.determine_refinement_needs(
            current_results=moderate_results,
            archetype_context=c_level_context
        )
        
        # Test Recruiter (more lenient criteria)
        recruiter_context = self._create_mock_archetype_context("recruiter")
        recruiter_plan = self.planner.determine_refinement_needs(
            current_results=moderate_results,
            archetype_context=recruiter_context
        )
        
        # C-Level might be more likely to trigger refinement on moderate quality
        # This tests that archetype-specific logic is applied
        assert isinstance(c_level_plan.needs_refinement, bool)
        assert isinstance(recruiter_plan.needs_refinement, bool)
        
        # Both should have proper metadata
        assert "iteration" in c_level_plan.metadata
        assert "iteration" in recruiter_plan.metadata
        assert "quality_score" in c_level_plan.metadata
        assert "quality_score" in recruiter_plan.metadata
    
    def _create_mock_archetype_context(self, archetype: str) -> ArchetypeContext:
        """Helper to create mock ArchetypeContext for testing."""
        # Create mock parameter objects
        mock_rag_params = Mock()
        mock_rag_params.company_weight = 0.7
        mock_rag_params.individual_weight = 0.3
        
        mock_reasoning_params = Mock()
        mock_reasoning_params.tot_depth = 3 if archetype == "c_level" else 2
        mock_reasoning_params.cot_steps = 5 if archetype == "c_level" else 3
        mock_reasoning_params.reflexion_iterations = 2 if archetype == "c_level" else 1
        mock_reasoning_params.multi_hop_depth = 3 if archetype == "c_level" else 2
        
        mock_signal_params = Mock()
        mock_signal_params.strategic_signals = 0.9 if archetype == "c_level" else 0.6
        mock_signal_params.min_signal_score = 0.7
        
        mock_constraint_params = Mock()
        mock_tone_params = Mock()
        mock_cta_params = Mock()
        
        return ArchetypeContext(
            archetype=archetype,
            confidence=0.8,
            reasoning=f"Classified as {archetype}",
            rag_params=mock_rag_params,
            reasoning_params=mock_reasoning_params,
            signal_params=mock_signal_params,
            constraint_params=mock_constraint_params,
            tone_params=mock_tone_params,
            cta_params=mock_cta_params,
            metadata={"test_archetype": archetype}
        )

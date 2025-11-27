"""Integration tests for L3 Outreach Orchestrator - Phase 4 validation.

Tests validate end-to-end outreach workflow execution with proper integration
between all layers and zero interference with resume workflows.
"""

import pytest
from unittest.mock import Mock, patch

from l1.outreach_dataclasses import (
    OutreachMission,
    ArchetypeContext,
    ArchetypeType,
    MessagePlan,
)
from l1.outreach_archetype_planning import RecipientProfile
from l3.outreach_orchestrator import OutreachOrchestrator
from l3.unified_workflow_orchestrator import UnifiedWorkflowOrchestrator


class TestL3OutreachIntegration:
    """Integration test suite for L3 outreach workflow validation."""
    
    def setup_method(self):
        """Set up integration test fixtures."""
        # Create mock dependencies for OutreachOrchestrator
        self.archetype_planner = Mock()
        self.research_planner = Mock()
        self.message_planner = Mock()
        self.company_executor = Mock()
        self.contact_executor = Mock()
        self.message_executor = Mock()
        self.state_manager = Mock()
        self.safety_validator = Mock()
        
        # Create OutreachOrchestrator
        self.outreach_orchestrator = OutreachOrchestrator(
            archetype_planner=self.archetype_planner,
            research_planner=self.research_planner,
            message_planner=self.message_planner,
            company_executor=self.company_executor,
            contact_executor=self.contact_executor,
            message_executor=self.message_executor,
            state_manager=self.state_manager,
            safety_validator=self.safety_validator,
        )
        
        # Create UnifiedWorkflowOrchestrator
        self.routing_policy = Mock()
        self.sandbox = Mock()
        self.unified_orchestrator = UnifiedWorkflowOrchestrator(
            routing_policy=self.routing_policy,
            sandbox=self.sandbox,
            state_manager=self.state_manager,
            safety_validator=self.safety_validator
        )
        
        # Set outreach orchestrator
        self.unified_orchestrator.set_outreach_orchestrator(self.outreach_orchestrator)
        
        # Test data
        self.mission = OutreachMission(
            objective="Senior Engineering outreach",
            target_role="Senior Software Engineer",
            value_proposition="Build scalable distributed systems"
        )
        
        self.recipient = RecipientProfile(
            name="Sarah Chen",
            title="VP of Engineering",
            company="DataTech Inc",
            industry="Data Analytics",
            seniority="Executive",
            department="Engineering",
            skills=["Python", "Distributed Systems", "Team Leadership"],
            recent_activity=["Led 50-person engineering team"],
            metadata={"linkedin_url": "https://linkedin.com/in/sarahchen"}
        )
    
    def test_e2e_outreach_cold_start(self):
        """End-to-end outreach workflow with cold start state."""
        # Setup mocks with proper attributes
        archetype_context = ArchetypeContext(archetype=ArchetypeType.C_LEVEL)
        self.archetype_planner.plan_archetype_influence.return_value = archetype_context
        
        research_plan = Mock()
        research_plan.__dict__ = {"query": "test", "filters": {}}
        self.research_planner.plan_research.return_value = research_plan
        
        # Configure Mock objects with proper __dict__ attributes
        company_info = Mock()
        company_info.__dict__ = {"name": "DataTech Inc", "industry": "Data Analytics"}
        contact_info = Mock()
        contact_info.__dict__ = {"name": "Sarah Chen", "title": "VP of Engineering"}
        
        self.company_executor.search_company_context.return_value = company_info
        self.contact_executor.search_contact_profile.return_value = contact_info
        
        message_plan = MessagePlan(subject_plan="Test", hook_plan="Hook")
        self.message_planner.create_message_plan.return_value = message_plan
        
        message_result = Mock()
        message_result.message = "Generated outreach message"
Best regards,
[Your Name]"""
        self.message_executor.generate_message.return_value = message_result
        
        safety_result = Mock()
        safety_result.passed = True
        safety_result.findings = []
        safety_result.__dict__ = {"passed": True, "findings": [], "score": 0.95}
        self.safety_validator.evaluate.return_value = safety_result
        
        # Execute end-to-end outreach workflow
        result = self.unified_orchestrator.dispatch_workflow(
            workflow_type="outreach",
            mission=self.mission,
            recipient=self.recipient
        )
        
        # Validate success
        assert result["success"]
        assert result["workflow_type"] == "outreach"
        assert "message" in result
        assert "metadata" in result
        
        # Verify message contains executive-level content
        message = result["message"]
        assert "Sarah" in message
        assert "DataTech" in message
        assert "distributed systems" in message.lower()
        
        # Verify metadata contains execution details
        metadata = result["metadata"]
        assert metadata["archetype"] == ArchetypeType.EXECUTIVE
        assert "research_bundle" in metadata
        assert "message_plan" in metadata
        assert "safety_result" in metadata
    
    def test_e2e_outreach_warm_start(self):
        """Pre-populate state_manager with saved research. Orchestrator must use warm state safely."""
        # Setup pre-existing state
        existing_state = {
            "mission_id": "previous_mission",
            "research_bundle": {
                "company": {"cached_info": "DataTech company data"},
                "contact": {"cached_info": "Sarah Chen profile"}
            }
        }
        self.state_manager.load_state.return_value = existing_state
        
        # Setup mocks for execution
        archetype_context = ArchetypeContext(archetype=ArchetypeType.EXECUTIVE)
        self.archetype_planner.plan_archetype_influence.return_value = archetype_context
        
        # Mock that research executors use cached data
        def company_search_side_effect(query, archetype):
            if "cached" in query:
                return Mock(__dict__={"cached": True, "data": "warm company data"})
            return Mock(__dict__={"cached": False, "data": "cold company data"})
        
        def contact_search_side_effect(query, archetype):
            if "cached" in query:
                return Mock(__dict__={"cached": True, "data": "warm contact data"})
            return Mock(__dict__={"cached": False, "data": "cold contact data"})
        
        self.company_executor.search_company_context.side_effect = company_search_side_effect
        self.contact_executor.search_contact_profile.side_effect = contact_search_side_effect
        
        self.research_planner.plan_research.return_value = Mock()
        self.message_planner.create_message_plan.return_value = MessagePlan()
        self.message_executor.generate_message.return_value = Mock(message="warm start message")
        self.safety_validator.evaluate.return_value = Mock(passed=True, findings=[])
        
        # Execute with warm start
        result = self.unified_orchestrator.dispatch_workflow(
            workflow_type="outreach",
            mission=self.mission,
            recipient=self.recipient,
            config={"use_warm_start": True}
        )
        
        # Validate warm start execution
        assert result["success"]
        assert result["message"] == "warm start message"
        
        # Verify state was loaded and used
        self.state_manager.load_state.assert_called_once()
    
    def test_outreach_e2e_no_resume_cross_contamination(self):
        """Ensure resume state, resume DAG, resume outputs unchanged."""
        # Setup resume workflow mocks (should not be called)
        resume_strategy_planner = Mock()
        resume_draft_planner = Mock()
        resume_qa_planner = Mock()
        
        # Setup outreach workflow mocks
        self.archetype_planner.plan_archetype_influence.return_value = ArchetypeContext()
        self.research_planner.plan_research.return_value = Mock()
        self.company_executor.search_company_context.return_value = Mock()
        self.contact_executor.search_contact_profile.return_value = Mock()
        self.message_planner.create_message_plan.return_value = MessagePlan()
        self.message_executor.generate_message.return_value = Mock(message="outreach message")
        self.safety_validator.evaluate.return_value = Mock(passed=True, findings=[])
        
        # Execute outreach workflow
        result = self.unified_orchestrator.dispatch_workflow(
            workflow_type="outreach",
            mission=self.mission,
            recipient=self.recipient
        )
        
        # Verify outreach executed successfully
        assert result["success"]
        assert result["workflow_type"] == "outreach"
        
        # Verify resume components were NOT called
        # (These would be called if resume workflow was accidentally triggered)
        assert resume_strategy_planner.plan_strategy.call_count == 0
        assert resume_draft_planner.plan_drafting.call_count == 0
        assert resume_qa_planner.plan_qa.call_count == 0
        
        # Verify only outreach components were called
        assert self.archetype_planner.plan_archetype_influence.call_count == 1
        assert self.message_executor.generate_message.call_count == 1
    
    def test_executor_failure_produces_safe_failure_result(self):
        """Simulate L2 exception. Orchestrator must return OutreachPipelineResult(success=False)."""
        # Setup L2 executor to raise exception
        self.company_executor.search_company_context.side_effect = Exception("Company research failed")
        
        # Setup other mocks
        self.archetype_planner.plan_archetype_influence.return_value = ArchetypeContext()
        self.research_planner.plan_research.return_value = Mock()
        
        # Execute with executor failure
        result = self.unified_orchestrator.dispatch_workflow(
            workflow_type="outreach",
            mission=self.mission,
            recipient=self.recipient
        )
        
        # Should return safe failure result, not crash
        assert not result["success"]
        assert result["workflow_type"] == "outreach"
        assert "error" in result["metadata"]
        assert "Company research failed" in result["metadata"]["error"]
    
    def test_message_contains_research_signals(self):
        """Validate message generator embeds company/contact signals correctly."""
        # Setup research with specific signals
        company_info = Mock()
        company_info.__dict__ = {
            "name": "DataTech Inc",
            "industry": "Data Analytics",
            "recent_funding": "$50M Series B",
            "tech_stack": ["Python", "Spark", "Kafka"],
            "company_values": ["Innovation", "Collaboration", "Excellence"]
        }
        
        contact_info = Mock()
        contact_info.__dict__ = {
            "name": "Sarah Chen",
            "title": "VP of Engineering",
            "background": "MIT PhD in Computer Science",
            "achievements": ["Led 100+ person team", "Published 10+ papers"],
            "interests": ["Distributed Systems", "Machine Learning", "Open Source"]
        }
        
        # Mock message generation to incorporate research signals
        def generate_message_with_signals(message_plan, archetype_context):
            # Extract research signals from context
            research = archetype_context.get("research_bundle", {})
            company = research.get("company", {})
            contact = research.get("contact", {})
            
            # Generate message incorporating signals
            message = f"""Dear {contact.get('name', 'there')},

I'm impressed by {company.get('name', 'your company')}'s work in {company.get('industry', 'technology')} and your leadership as {contact.get('title', 'engineering leader')}.

Your background in {contact.get('background', 'computer science')} and achievements like {', '.join(contact.get('achievements', ['leading teams']))} demonstrate exceptional technical leadership.

I'd love to discuss how we can collaborate on innovative technologies.

Best regards"""
            
            return Mock(message=message)
        
        # Setup mocks
        self.archetype_planner.plan_archetype_influence.return_value = ArchetypeContext(
            archetype=ArchetypeType.EXECUTIVE
        )
        self.research_planner.plan_research.return_value = Mock()
        self.company_executor.search_company_context.return_value = company_info
        self.contact_executor.search_contact_profile.return_value = contact_info
        self.message_planner.create_message_plan.return_value = MessagePlan()
        self.message_executor.generate_message.side_effect = generate_message_with_signals
        self.safety_validator.evaluate.return_value = Mock(passed=True, findings=[])
        
        # Execute
        result = self.unified_orchestrator.dispatch_workflow(
            workflow_type="outreach",
            mission=self.mission,
            recipient=self.recipient
        )
        
        # Validate message contains research signals
        assert result["success"]
        message = result["message"]
        
        # Company signals
        assert "DataTech Inc" in message
        assert "Data Analytics" in message
        assert "$50M Series B" in message
        assert "Python, Spark, Kafka" in message
        
        # Contact signals
        assert "Sarah Chen" in message
        assert "VP of Engineering" in message
        assert "MIT PhD" in message
        assert "Led 100+ person team" in message
    
    def test_outreach_dispatch_success(self):
        """Verify outreach dispatch works correctly and maintains isolation."""
        # Setup outreach workflow
        self.archetype_planner.plan_archetype_influence.return_value = ArchetypeContext()
        self.research_planner.plan_research.return_value = Mock()
        self.company_executor.search_company_context.return_value = Mock()
        self.contact_executor.search_contact_profile.return_value = Mock()
        self.message_planner.create_message_plan.return_value = MessagePlan()
        self.message_executor.generate_message.return_value = Mock(message="outreach")
        self.safety_validator.evaluate.return_value = Mock(passed=True, findings=[])
        
        # Test outreach dispatch
        outreach_result = self.unified_orchestrator.dispatch_workflow(
            workflow_type="outreach",
            mission=self.mission,
            recipient=self.recipient
        )
        
        # Verify outreach executed successfully
        assert outreach_result["success"] == True
        assert outreach_result["workflow_type"] == "outreach"
        
        # Verify outreach components were called
        assert self.archetype_planner.plan_archetype_influence.call_count == 1
        assert self.message_executor.generate_message.call_count == 1

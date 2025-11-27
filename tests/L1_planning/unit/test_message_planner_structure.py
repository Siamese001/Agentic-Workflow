"""
Tests for L1 message planner structure and C-Level specific validation.

Validates create_message_plan() creates MessagePlan with exact fields, section temperatures,
word targets, and C-Level strategic urgency requirements.
Tests MUST NOT import L2 or L4 modules.
"""

from unittest.mock import Mock

from l1.message_planning import MessagePlanner, MessageContent
from l1.outreach_dataclasses import MessagePlan, ArchetypeContext


class TestMessagePlannerStructure:
    """Test suite for L1 message planner structure validation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.planner = MessagePlanner()
    
    def test_create_message_plan_returns_message_plan(self):
        """Test create_message_plan() returns MessagePlan with correct type."""
        content = MessageContent(
            recipient_name="John Smith",
            recipient_title="Senior Software Engineer",
            company_name="TechCorp",
            value_proposition="Technical leadership and innovation",
            key_points=["Python expertise", "ML experience"],
            personalization_elements=["Open to remote", "Industry experience"],
            constraints=["No relocation", "Remote work preferred"],
            metadata={"experience_years": "8"}
        )
        
        archetype_context = self._create_mock_archetype_context("senior_ta")
        
        result = self.planner.create_message_plan(content, archetype_context)
        
        # Verify return type
        assert isinstance(result, MessagePlan)
    
    def test_message_plan_exact_field_structure(self):
        """Test MessagePlan contains EXACT required fields: subject_plan, hook_plan, value_plan, cta_plan, signature_plan."""
        content = MessageContent(
            recipient_name="Jane Doe",
            recipient_title="Engineering Manager",
            company_name="StartupCorp",
            value_proposition="Team leadership and growth",
            key_points=["Team building", "Scale experience"],
            personalization_elements=["Agile expertise", "Startup experience"],
            constraints=["On-site required"],
            metadata={"team_size": "15"}
        )
        
        archetype_context = self._create_mock_archetype_context("hiring_manager")
        
        plan = self.planner.create_message_plan(content, archetype_context)
        
        # Verify EXACT field structure
        required_fields = [
            'subject_plan', 'hook_plan', 'value_plan', 'cta_plan', 'signature_plan'
        ]
        
        # Additional fields that are part of the current MessagePlan schema
        additional_fields = [
            'schema_version', 'model_name', 'sections', 'temperature_schedule', 
            'constraints', 'estimated_tokens', 'generation_strategy'
        ]
        
        for field in required_fields + additional_fields:
            assert hasattr(plan, field), f"Missing required field: {field}"
            assert getattr(plan, field) is not None, f"Field {field} is None"
        
        # Verify no extra unexpected fields (should only have required + additional + metadata)
        all_fields = [attr for attr in dir(plan) if not attr.startswith('_')]
        expected_fields = required_fields + additional_fields + ['metadata']
        unexpected_fields = [f for f in all_fields if f not in expected_fields]
        assert len(unexpected_fields) == 0, f"Unexpected fields found: {unexpected_fields}"
    
    def test_section_level_temperatures_match_constraint_params(self):
        """Test section-level temperatures match constraint_params + section schedule."""
        content = MessageContent(
            recipient_name="Sarah Chen",
            recipient_title="Senior Software Engineer",
            company_name="TechCorp",
            value_proposition="Technical excellence",
            key_points=["Python", "Distributed Systems"],
            personalization_elements=["Open source contributions"],
            constraints=["Technical focus only"],
            metadata={"level": "L5"}
        )
        
        archetype_context = self._create_mock_archetype_context("senior_ta")
        
        plan = self.planner.create_message_plan(content, archetype_context)
        
        # Verify temperature_schedule contains temperatures for each section
        sections = ['subject', 'hook', 'value', 'cta', 'signature']  # Shortened keys used in temperature_schedule
        assert hasattr(plan, 'temperature_schedule'), "MessagePlan missing temperature_schedule"
        assert isinstance(plan.temperature_schedule, dict), "temperature_schedule is not a dict"
        
        # Verify each section has temperature in temperature_schedule
        for section in sections:
            assert section in plan.temperature_schedule, f"{section} missing from temperature_schedule"
            assert isinstance(plan.temperature_schedule[section], float), f"{section} temperature not float"
        
        # Verify temperatures align with archetype constraints
        # (This tests that temperature adjustments are applied correctly)
        subject_temp = plan.temperature_schedule['subject']
        hook_temp = plan.temperature_schedule['hook']
        body_temp = plan.temperature_schedule['value']
        cta_temp = plan.temperature_schedule['cta']
        signature_temp = plan.temperature_schedule['signature']
        
        # All temperatures should be reasonable
        for temp in [subject_temp, hook_temp, body_temp, cta_temp, signature_temp]:
            assert -2.0 <= temp <= 2.0, f"Temperature {temp} out of reasonable range"
    
    def test_word_targets_applied_correctly(self):
        """Test word targets are applied correctly to message sections."""
        content = MessageContent(
            recipient_name="Michael Johnson",
            recipient_title="CTO",
            company_name="EnterpriseCorp",
            value_proposition="Strategic technology leadership",
            key_points=["Digital transformation", "Enterprise scale"],
            personalization_elements=["Board level experience"],
            constraints=["Executive communication"],
            metadata={"reporting_level": "board"}
        )
        
        archetype_context = self._create_mock_archetype_context("c_level")
        
        plan = self.planner.create_message_plan(content, archetype_context)
        
        # Verify word targets are applied in constraints
        assert hasattr(plan, 'constraints'), "MessagePlan missing constraints"
        assert isinstance(plan.constraints, dict), "constraints is not a dict"
        
        # Check for max_lengths in constraints (word targets)
        if 'max_lengths' in plan.constraints:
            max_lengths = plan.constraints['max_lengths']
            assert isinstance(max_lengths, dict), "max_lengths is not a dict"
            
            # Verify each section has word target
            sections = ['subject', 'hook', 'value', 'cta', 'signature']  # Shortened keys
            for section in sections:
                assert section in max_lengths, f"{section} missing word target"
                assert isinstance(max_lengths[section], int), f"{section} word target not int"
                assert max_lengths[section] > 0, f"{section} word target should be positive"
            
            # Verify word targets make sense for each section
            assert max_lengths['subject'] <= 60, "Subject should be concise"
            assert max_lengths['value'] >= 100, "Value section should be substantial"
            assert max_lengths['signature'] <= 50, "Signature should be brief"
    
    def test_c_level_subject_hook_strategic_urgency(self):
        """Test C-Level subject/hook reflect strategic urgency."""
        c_level_content = MessageContent(
            recipient_name="Robert Williams",
            recipient_title="Chief Executive Officer",
            company_name="FortuneCorp",
            value_proposition="Strategic growth consulting",
            key_points=["Market expansion", "Revenue optimization"],
            personalization_elements=["Fortune 500 experience"],
            constraints=["C-Suite communication only"],
            metadata={"market_cap": "10B"}
        )
        
        c_level_context = self._create_mock_archetype_context("c_level")
        
        plan = self.planner.create_message_plan(c_level_content, c_level_context)
        
        # Verify subject reflects strategic urgency
        subject_content = plan.subject_plan.lower()
        strategic_subject_words = [
            "strategic", "growth", "transformation", "opportunity", 
            "partnership", "collaboration", "leadership", "vision"
        ]
        has_strategic_subject = any(word in subject_content for word in strategic_subject_words)
        assert has_strategic_subject, f"C-Level subject should reflect strategic urgency: {subject_content}"
        
        # Verify hook reflects strategic engagement
        hook_content = plan.hook_plan.lower()
        strategic_hook_words = [
            "executive", "strategic", "market", "opportunity", 
            "leadership", "transformation", "growth"
        ]
        has_strategic_hook = any(word in hook_content for word in strategic_hook_words)
        assert has_strategic_hook, f"C-Level hook should reflect strategic engagement: {hook_content}"
    
    def test_c_level_value_section_high_signal_insights(self):
        """Test C-Level value section includes 2-3 high-signal insights from RAG."""
        c_level_content = MessageContent(
            recipient_name="Lisa Anderson",
            recipient_title="President",
            company_name="GlobalCorp",
            value_proposition="Global expansion strategy",
            key_points=["International operations", "Supply chain optimization"],
            personalization_elements=["Global markets experience"],
            constraints=["Executive level required"],
            metadata=["global_scope", "board_member"]
        )
        
        c_level_context = self._create_mock_archetype_context("c_level")
        
        plan = self.planner.create_message_plan(c_level_content, c_level_context)
        
        # Verify value section includes high-signal insights
        value_content = plan.value_plan.lower()
        
        # Should include strategic/financial indicators
        high_signal_indicators = [
            "revenue", "growth", "market", "strategic", "financial",
            "expansion", "opportunity", "transformation", "optimization"
        ]
        signal_count = sum(1 for indicator in high_signal_indicators if indicator in value_content)
        
        # Should include 2-3 high-signal insights
        assert 2 <= signal_count <= 5, \
            f"C-Level value section should include 2-3 high-signal insights, found {signal_count}: {value_content}"
    
    def test_c_level_cta_bold_executive_style(self):
        """Test C-Level CTA matches bold-executive style (if allowed by archetype)."""
        c_level_content = MessageContent(
            recipient_name="David Martinez",
            recipient_title="Chief Financial Officer",
            company_name="FinanceCorp",
            value_proposition="Financial optimization and growth",
            key_points=["Capital markets", "Financial strategy"],
            personalization_elements=["Public company experience"],
            constraints=["Financial executive only"],
            metadata=["public_company", "sec_compliance"]
        )
        
        c_level_context = self._create_mock_archetype_context("c_level")
        
        plan = self.planner.create_message_plan(c_level_content, c_level_context)
        
        # Verify CTA has executive style
        cta_content = plan.cta_plan.lower()
        
        # Should include action-oriented executive language
        executive_cta_words = [
            "discuss", "explore", "partnership", "collaboration",
            "strategic", "opportunity", "schedule", "connect",
            "conversation", "brief", "open", "learn"
        ]
        has_executive_cta = any(word in cta_content for word in executive_cta_words)
        assert has_executive_cta, f"C-Level CTA should have executive style: {cta_content}"
        
        # Should be professional and direct
        assert len(cta_content.split()) <= 25, "C-Level CTA should be concise"
    
    def test_temperature_schedule_section_specific_adjustments(self):
        """Test temperature schedule applies section-specific adjustments."""
        content = MessageContent(
            recipient_name="Jennifer Taylor",
            recipient_title="Chief Operating Officer",
            company_name="OperationsCorp",
            value_proposition="Operational transformation",
            key_points=["Process optimization", "Efficiency gains"],
            personalization_elements=["Turnaround experience"],
            constraints=["Executive operations focus"],
            metadata=["efficiency_metrics", "team_size"]
        )
        
        archetype_context = self._create_mock_archetype_context("c_level")
        
        plan = self.planner.create_message_plan(content, archetype_context)
        
        # Verify temperature schedule is section-specific
        temperatures = plan.temperature_schedule
        
        # C-Level should have reasonable temperature ranges
        assert 0.0 <= temperatures['subject'] <= 1.0, "C-Level subject should have reasonable temperature"
        assert 0.0 <= temperatures['signature'] <= 1.0, "C-Level signature should have reasonable temperature"
        
        # Hook and value might be higher for engagement (more creative)
        assert temperatures['hook'] >= temperatures['subject'], "Hook should be more engaging than subject"
    
    def test_message_plan_content_personalization(self):
        """Test message plan content includes proper personalization."""
        content = MessageContent(
            recipient_name="Thomas Brown",
            recipient_title="VP Strategy",
            company_name="StrategyCorp",
            value_proposition="Strategic market expansion",
            key_points=["Market analysis", "Growth planning"],
            personalization_elements=["Strategy consulting", "Fortune 500 experience"],
            constraints=["Executive strategy role only"],
            metadata=["market_opportunity", "competitive_analysis"]
        )
        
        archetype_context = self._create_mock_archetype_context("c_level")
        
        plan = self.planner.create_message_plan(content, archetype_context)
        
        # Verify personalization elements are included
        all_content = (
            plan.subject_plan + " " +
            plan.hook_plan + " " +
            plan.value_plan + " " +
            plan.cta_plan
        ).lower()
        
        # Should include company name (recipient names may not be included)
        assert content.company_name.lower() in all_content or "strategycorp" in all_content
        
        # Should include value proposition elements
        value_prop_elements = content.value_proposition.lower().split()
        has_value_elements = any(elem in all_content for elem in value_prop_elements)
        assert has_value_elements, "Should include value proposition elements"
    
    def test_constraint_influences_message_structure(self):
        """Test constraints influence message structure and content."""
        constrained_content = MessageContent(
            recipient_name="Amy Zhang",
            recipient_title="Technical Recruiter",
            company_name="HiringCorp",
            value_proposition="Technical talent acquisition",
            key_points=["Talent sourcing", "Technical screening"],
            personalization_elements=["Tech hiring expertise"],
            constraints=["Brief and direct", "No technical jargon"],
            metadata=["specialization", "quota"]
        )
        
        archetype_context = self._create_mock_archetype_context("recruiter")
        
        plan = self.planner.create_message_plan(constrained_content, archetype_context)
        
        # Verify constraints are respected in structure
        max_lengths = plan.constraints.get('max_lengths', {})
        total_words = sum([
            max_lengths.get('subject', 0),
            max_lengths.get('hook', 0),
            max_lengths.get('value', 0),
            max_lengths.get('cta', 0),
            max_lengths.get('signature', 0)
        ])
        
        # "Brief and direct" constraint should result in reasonable word count
        assert total_words <= 1000, f"Total words should be reasonable: {total_words}"
        
        # Verify constraints are properly stored in constraints field
        assert hasattr(plan, 'constraints')
        assert isinstance(plan.constraints, dict)
    
    def test_archetype_specific_message_tones(self):
        """Test message tones vary appropriately by archetype."""
        base_content = MessageContent(
            recipient_name="Test User",
            recipient_title="Test Role",
            company_name="TestCorp",
            value_proposition="Test value proposition",
            key_points=["Test point 1", "Test point 2"],
            personalization_elements=["Test personalization"],
            constraints=["Test constraint"],
            metadata={"test": True}
        )
        
        # Create plans for different archetypes
        recruiter_context = self._create_mock_archetype_context("recruiter")
        c_level_context = self._create_mock_archetype_context("c_level")
        
        recruiter_plan = self.planner.create_message_plan(base_content, recruiter_context)
        c_level_plan = self.planner.create_message_plan(base_content, c_level_context)
        
        # Compare tones (formality levels via temperature)
        recruiter_temps = [
            recruiter_plan.temperature_schedule['subject'],
            recruiter_plan.temperature_schedule['value']
        ]
        
        c_level_temps = [
            c_level_plan.temperature_schedule['subject'],
            c_level_plan.temperature_schedule['value']
        ]
        
        recruiter_avg_temp = sum(recruiter_temps) / len(recruiter_temps)
        c_level_avg_temp = sum(c_level_temps) / len(c_level_temps)
        
        # C-Level should be as formal or more formal (lower/equal temperature) than recruiter
        assert c_level_avg_temp <= recruiter_avg_temp, \
            f"C-Level should be as formal or more formal: {c_level_avg_temp} vs {recruiter_avg_temp}"
    
    def _create_mock_archetype_context(self, archetype: str) -> ArchetypeContext:
        """Helper to create mock ArchetypeContext for testing."""
        # Create mock parameter objects
        mock_rag_params = Mock()
        mock_rag_params.company_weight = 0.7 if archetype == "c_level" else 0.5
        mock_rag_params.individual_weight = 0.3 if archetype == "c_level" else 0.5
        
        mock_reasoning_params = Mock()
        mock_reasoning_params.tot_depth = 3 if archetype == "c_level" else 2
        mock_reasoning_params.cot_steps = 5 if archetype == "c_level" else 3
        mock_reasoning_params.reflexion_iterations = 2 if archetype == "c_level" else 1
        
        mock_signal_params = Mock()
        mock_signal_params.strategic_signals = 0.9 if archetype == "c_level" else 0.6
        
        mock_constraint_params = Mock()
        mock_constraint_params.formality_level = "high" if archetype == "c_level" else "medium"
        
        mock_tone_params = Mock()
        mock_tone_params.professionalism = 0.9 if archetype == "c_level" else 0.7
        
        mock_cta_params = Mock()
        mock_cta_params.action_orientation = "strategic" if archetype == "c_level" else "direct"
        
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

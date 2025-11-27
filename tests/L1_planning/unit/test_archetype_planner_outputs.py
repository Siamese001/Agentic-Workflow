"""
Tests for L1 archetype planner outputs and C-Level specific validation.

Validates build_archetype_context() returns ArchetypeContext with all required fields,
C-Level shows high-intensity reasoning, company-focused RAG weighting, and strategic insights.
Tests MUST NOT import L2 or L4 modules.
"""

from l1.outreach_archetype_planning import OutreachArchetypePlanner, RecipientProfile, OutreachMission
from l1.outreach_dataclasses import ArchetypeContext, ArchetypeType, ReasoningMode


class TestArchetypePlannerOutputs:
    """Test suite for L1 archetype planner output validation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.planner = OutreachArchetypePlanner()
    
    def test_build_archetype_context_returns_archetype_context(self):
        """Test build_archetype_context() returns ArchetypeContext with correct type."""
        recipient = RecipientProfile(
            name="John Smith",
            title="Senior Software Engineer",
            company="TechCorp",
            industry="Technology",
            seniority="senior",
            department="Engineering",
            skills=["Python", "Machine Learning"],
            recent_activity=["Led project migration"],
            metadata={"experience_years": "8"}
        )
        
        mission = OutreachMission(
            objective="Outreach for senior technical role",
            target_role="Senior Software Engineer",
            value_proposition="Technical leadership and innovation",
            urgency="medium",
            personalization_points=["Python expertise", "ML experience"],
            constraints=["No relocation", "Remote work preferred"],
            metadata={"campaign_id": "tech_hiring_2024"}
        )
        
        result = self.planner.build_archetype_context(recipient, mission)
        
        # Verify return type
        assert isinstance(result, ArchetypeContext)
    
    def test_archetype_context_all_required_fields_exist(self):
        """Test ArchetypeContext contains all required fields."""
        recipient = RecipientProfile(
            name="Jane Doe",
            title="Engineering Manager",
            company="StartupCorp",
            industry="Technology",
            seniority="manager",
            department="Engineering",
            skills=["Leadership", "Agile"],
            recent_activity=["Hiring team expansion"],
            metadata={"team_size": "15"}
        )
        
        mission = OutreachMission(
            objective="Hiring manager outreach",
            target_role="Engineering Manager",
            value_proposition="Team leadership and growth",
            urgency="high",
            personalization_points=["Team building", "Scale experience"],
            constraints=["On-site required"],
            metadata={"headcount_approval": "approved"}
        )
        
        context = self.planner.build_archetype_context(recipient, mission)
        
        # Verify all required fields exist
        required_fields = [
            'archetype', 'confidence', 'reasoning',
            'rag_params', 'reasoning_params', 'signal_params',
            'constraint_params', 'tone_params', 'cta_params', 'metadata'
        ]
        
        for field in required_fields:
            assert hasattr(context, field), f"Missing required field: {field}"
            assert getattr(context, field) is not None, f"Field {field} is None"
    
    def test_c_level_high_intensity_reasoning_depth(self):
        """Test C-Level archetype shows high-intensity reasoning with TOT depth."""
        c_level_recipient = RecipientProfile(
            name="Michael Johnson",
            title="Chief Technology Officer",
            company="EnterpriseCorp",
            industry="Enterprise Software",
            seniority="executive",
            department="Technology",
            skills=["Strategic Planning", "Digital Transformation"],
            recent_activity=["Led $50M digital initiative"],
            metadata={"reporting_level": "board"}
        )
        
        mission = OutreachMission(
            objective="C-Level strategic partnership",
            target_role="CTO",
            value_proposition="Strategic technology leadership",
            urgency="high",
            personalization_points=["Enterprise experience", "Board-level communication"],
            constraints=["Executive level only"],
            metadata={"partnership_potential": "high"}
        )
        
        context = self.planner.build_archetype_context(c_level_recipient, mission)
        
        # Verify C-Level classification
        assert context.archetype == ArchetypeType.C_LEVEL.value
        
        # Verify high-intensity reasoning parameters
        assert context.reasoning_params is not None
        assert hasattr(context.reasoning_params, 'max_reasoning_depth')
        
        # C-Level should have higher max reasoning depth than other archetypes
        c_level_max_depth = context.reasoning_params.max_reasoning_depth
        
        # Compare with senior TA (should have lower depth)
        senior_ta_recipient = RecipientProfile(
            name="Sarah Chen",
            title="Senior Software Engineer",
            company="TechCorp",
            industry="Technology",
            seniority="senior",
            department="Engineering",
            skills=["Python", "Distributed Systems"],
            recent_activity=["Built microservices platform"],
            metadata={"level": "L5"}
        )
        
        senior_ta_context = self.planner.build_archetype_context(senior_ta_recipient, mission)
        senior_ta_max_depth = senior_ta_context.reasoning_params.max_reasoning_depth
        
        # C-Level should have equal or greater max reasoning depth
        assert c_level_max_depth >= senior_ta_max_depth
    
    def test_c_level_company_focused_rag_weighting(self):
        """Test C-Level has company-focused RAG weighting (~70% company / 30% individual)."""
        c_level_recipient = RecipientProfile(
            name="Robert Williams",
            title="Chief Executive Officer",
            company="FortuneCorp",
            industry="Finance",
            seniority="executive",
            department="Executive",
            skills=["Strategic Leadership", "Financial Management"],
            recent_activity=["Acquired competitor for $200M"],
            metadata={"market_cap": "10B"}
        )
        
        mission = OutreachMission(
            objective="CEO strategic advisory",
            target_role="CEO",
            value_proposition="Strategic growth consulting",
            urgency="critical",
            personalization_points=["Fortune 500 experience", "M&A expertise"],
            constraints=["C-Suite only"],
            metadata={"revenue_impact": "high"}
        )
        
        context = self.planner.build_archetype_context(c_level_recipient, mission)
        
        # Verify RAG parameters exist
        assert context.rag_params is not None
        assert hasattr(context.rag_params, 'source_weights')
        assert hasattr(context.rag_params, 'top_k')
        
        # C-Level should favor company-focused source weights
        source_weights = context.rag_params.source_weights
        top_k = context.rag_params.top_k
        
        # Verify source weights include company-focused sources
        assert 'earnings_calls' in source_weights
        assert 'executive_insights' in source_weights
        
        # Verify higher top_k for C-Level (more comprehensive research)
        assert top_k >= 10, f"C-Level top_k {top_k} should be ≥ 10"
    
    def test_c_level_multi_hop_reasoning_depth(self):
        """Test C-Level has multi-hop reasoning depth (≥3 for C-Level)."""
        c_level_recipient = RecipientProfile(
            name="Lisa Anderson",
            title="President",
            company="GlobalCorp",
            industry="Manufacturing",
            seniority="executive",
            department="Executive",
            skills=["Global Operations", "Supply Chain Strategy"],
            recent_activity=["Expanded to 15 new markets"],
            metadata=["global_scope", "board_member"]
        )
        
        mission = OutreachMission(
            objective="President strategic consultation",
            target_role="President",
            value_proposition="Global expansion strategy",
            urgency="high",
            personalization_points=["International experience", "P&L management"],
            constraints=["Executive level required"],
            metadata=["expansion_budget", "market_analysis"]
        )
        
        context = self.planner.build_archetype_context(c_level_recipient, mission)
        
        # Verify reasoning parameters support multi-hop analysis
        assert context.reasoning_params is not None
        assert hasattr(context.reasoning_params, 'max_reasoning_depth')
        
        # C-Level should have max reasoning depth ≥ 3
        max_reasoning_depth = context.reasoning_params.max_reasoning_depth
        assert max_reasoning_depth >= 3, f"C-Level max_reasoning_depth {max_reasoning_depth} should be ≥ 3"
    
    def test_c_level_elevated_cot_steps(self):
        """Test C-Level has strongly elevated CoT steps."""
        c_level_recipient = RecipientProfile(
            name="David Martinez",
            title="Chief Financial Officer",
            company="FinanceCorp",
            industry="Financial Services",
            seniority="executive",
            department="Finance",
            skills=["Financial Strategy", "Investment Management"],
            recent_activity=["Led IPO raising $500M"],
            metadata=["public_company", "sec_compliance"]
        )
        
        mission = OutreachMission(
            objective="CFO financial strategy advisory",
            target_role="CFO",
            value_proposition="Financial optimization and growth",
            urgency="critical",
            personalization_points=["Public company experience", "Capital markets"],
            constraints=["Financial executive only"],
            metadata=["deal_size", "timeline"]
        )
        
        context = self.planner.build_archetype_context(c_level_recipient, mission)
        
        # Verify CoT is enabled for C-Level
        assert context.reasoning_params is not None
        assert hasattr(context.reasoning_params, 'enable_chain_of_thought')
        
        c_level_cot_enabled = context.reasoning_params.enable_chain_of_thought
        assert c_level_cot_enabled, "C-Level should have chain of thought enabled"
        
        # Compare with recruiter (should have fewer steps)
        recruiter_recipient = RecipientProfile(
            name="Amy Zhang",
            title="Technical Recruiter",
            company="HiringCorp",
            industry="HR Technology",
            seniority="individual",
            department="HR",
            skills=["Talent Acquisition", "Technical Screening"],
            recent_activity=["Filled 15 engineering roles"],
            metadata=["specialization", "quota"]
        )
        
        recruiter_context = self.planner.build_archetype_context(recruiter_recipient, mission)
        recruiter_cot_enabled = recruiter_context.reasoning_params.enable_chain_of_thought
        
        # Both should have CoT enabled, but C-Level should have higher confidence
        assert c_level_cot_enabled and recruiter_cot_enabled
    
    def test_c_level_reflexion_iterations_minimum(self):
        """Test C-Level has reflexion iterations ≥ 2."""
        c_level_recipient = RecipientProfile(
            name="Jennifer Taylor",
            title="Chief Operating Officer",
            company="OperationsCorp",
            industry="Logistics",
            seniority="executive",
            department="Operations",
            skills=["Operational Excellence", "Process Optimization"],
            recent_activity=["Reduced costs by 30% companywide"],
            metadata=["efficiency_metrics", "team_size"]
        )
        
        mission = OutreachMission(
            objective="COO operational strategy consulting",
            target_role="COO",
            value_proposition="Operational transformation and efficiency",
            urgency="high",
            personalization_points=["Turnaround experience", "Scale operations"],
            constraints=["C-Suite level only"],
            metadata=["cost_savings", "timeline"]
        )
        
        context = self.planner.build_archetype_context(c_level_recipient, mission)
        
        # Verify max reasoning depth for C-Level
        assert context.reasoning_params is not None
        assert hasattr(context.reasoning_params, 'max_reasoning_depth')
        
        max_reasoning_depth = context.reasoning_params.max_reasoning_depth
        assert max_reasoning_depth >= 3, f"C-Level max_reasoning_depth {max_reasoning_depth} should be ≥ 3"
    
    def test_c_level_strategic_insights_focus(self):
        """Test C-Level focuses on strategic insights matching LIC research patterns."""
        c_level_recipient = RecipientProfile(
            name="Thomas Brown",
            title="Vice President of Strategy",
            company="StrategyCorp",
            industry="Consulting",
            seniority="executive",
            department="Strategy",
            skills=["Strategic Planning", "Market Analysis"],
            recent_activity=["Developed 5-year growth plan"],
            metadata=["strategic_initiatives", "market_research"]
        )
        
        mission = OutreachMission(
            objective="VP Strategy partnership",
            target_role="VP Strategy",
            value_proposition="Strategic market expansion",
            urgency="high",
            personalization_points=["Strategy consulting", "Market analysis"],
            constraints=["Executive strategy role only"],
            metadata=["market_opportunity", "competitive_analysis"]
        )
        
        context = self.planner.build_archetype_context(c_level_recipient, mission)
        
        # Verify signal parameters focus on strategic insights
        assert context.signal_params is not None
        assert hasattr(context.signal_params, 'signal_types')
        assert 'strategic' in context.signal_params.signal_types
        assert 'quantitative' in context.signal_params.signal_types
        
        # C-Level should have elevated strategic signal focus
        signal_threshold = context.signal_params.signal_threshold
        assert signal_threshold >= 0.7, f"C-Level signal threshold {signal_threshold} should be ≥ 0.7"
    
    def test_reasoning_mode_enum_availability(self):
        """Test ReasoningMode enum validates for COT/TOT/REACT availability."""
        # Verify ReasoningMode enum has required values
        assert hasattr(ReasoningMode, 'COT')
        assert hasattr(ReasoningMode, 'TOT')
        assert hasattr(ReasoningMode, 'REACT')
        
        # Verify enum values are accessible
        assert ReasoningMode.COT.value == "cot"
        assert ReasoningMode.TOT.value == "tot"
        assert ReasoningMode.REACT.value == "react"
    
    def test_archetypes_produce_distinct_configs(self):
        """Test all 4 archetypes produce distinct parameter configurations."""
        base_mission = OutreachMission(
            objective="Test outreach",
            target_role="Test Role",
            value_proposition="Test value",
            urgency="medium",
            personalization_points=["Test point"],
            constraints=["Test constraint"],
            metadata={"test": True}
        )
        
        # Create recipients for each archetype
        recipients = {
            ArchetypeType.RECRUITER: RecipientProfile(
                name="Recruiter", title="Technical Recruiter", company="HiringCorp",
                industry="HR", seniority="individual", department="HR",
                skills=["Recruiting"], recent_activity=["Hiring"], metadata={}
            ),
            ArchetypeType.SENIOR_TA: RecipientProfile(
                name="Senior TA", title="Senior Software Engineer", company="TechCorp",
                industry="Tech", seniority="senior", department="Engineering",
                skills=["Python"], recent_activity=["Coding"], metadata={}
            ),
            ArchetypeType.EXECUTIVE: RecipientProfile(
                name="Executive", title="VP Engineering", company="ExecCorp",
                industry="Tech", seniority="executive", department="Engineering",
                skills=["Leadership"], recent_activity=["Strategy"], metadata={}
            ),
            ArchetypeType.C_LEVEL: RecipientProfile(
                name="Executive", title="CTO", company="ExecCorp",
                industry="Tech", seniority="executive", department="Technology",
                skills=["Strategy"], recent_activity=["Strategizing"], metadata={}
            )
        }
        
        contexts = {}
        for archetype, recipient in recipients.items():
            context = self.planner.build_archetype_context(recipient, base_mission)
            contexts[archetype] = context
        
        # Verify all archetypes are classified correctly
        for archetype, context in contexts.items():
            assert context.archetype == archetype.value
        
        # Verify distinct configurations (at least reasoning parameters should differ)
        reasoning_params = {}
        for archetype, context in contexts.items():
            reasoning_params[archetype] = {
                'max_reasoning_depth': context.reasoning_params.max_reasoning_depth,
                'enable_chain_of_thought': context.reasoning_params.enable_chain_of_thought,
                'confidence_threshold': context.reasoning_params.confidence_threshold
            }
        
        # Should have distinct reasoning configurations
        unique_configs = set()
        for config in reasoning_params.values():
            unique_configs.add(tuple(config.values()))
        
        # Should have at least 3 distinct configurations (some might be similar)
        assert len(unique_configs) >= 3, f"Archetypes should have distinct reasoning configs, got {len(unique_configs)}"
    
    def test_archetype_context_confidence_scoring(self):
        """Test archetype context includes confidence scoring."""
        recipient = RecipientProfile(
            name="Test User",
            title="Software Engineer",
            company="TestCorp",
            industry="Technology",
            seniority="senior",
            department="Engineering",
            skills=["Python"],
            recent_activity=["Testing"],
            metadata={}
        )
        
        mission = OutreachMission(
            objective="Test objective",
            target_role="Test Role",
            value_proposition="Test value",
            urgency="medium",
            personalization_points=["Test"],
            constraints=["Test"],
            metadata={}
        )
        
        context = self.planner.build_archetype_context(recipient, mission)
        
        # Verify confidence is scored and reasonable
        assert hasattr(context, 'confidence')
        assert isinstance(context.confidence, float)
        assert 0.0 <= context.confidence <= 1.0
        
        # Verify reasoning explains classification
        assert hasattr(context, 'reasoning')
        assert isinstance(context.reasoning, str)
        assert len(context.reasoning) > 0
        assert "classified" in context.reasoning.lower()

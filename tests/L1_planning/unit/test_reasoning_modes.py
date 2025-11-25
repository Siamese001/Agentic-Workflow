"""
L1 Planning Layer Unit Tests - Reasoning Modes

Tests for reasoning mode selection and application without execution logic.
Focuses on analytical, comparative, and synthesis reasoning modes.
"""

import pytest
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from unittest.mock import Mock, patch

# Mark all tests in this module as L1 planning unit tests
pytestmark = [pytest.mark.unit, pytest.mark.l1, pytest.mark.planning]


class ReasoningMode(Enum):
    """Reasoning modes for L1 planning."""
    ANALYTICAL = "analytical"
    COMPARATIVE = "comparative"
    SYNTHESIS = "synthesis"
    EVALUATIVE = "evaluative"
    STRATEGIC = "strategic"


@dataclass(frozen=True)
class MockReasoningContext:
    """Mock reasoning context for L1 testing."""
    mission: str
    input_type: str
    complexity_level: str
    domain: str
    constraints: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class MockReasoningDecision:
    """Mock reasoning decision for L1 testing."""
    selected_mode: ReasoningMode
    confidence: float
    rationale: str
    alternative_modes: List[ReasoningMode] = field(default_factory=list)


class TestReasoningModeSelection:
    """Test L1 reasoning mode selection logic."""
    
    def test_analytical_mode_selection(self):
        """Test selection of analytical reasoning mode."""
        contexts = [
            MockReasoningContext(
                mission="Extract technical requirements from job description",
                input_type="job_description",
                complexity_level="medium",
                domain="technical"
            ),
            MockReasoningContext(
                mission="Parse resume structure and identify sections",
                input_type="resume",
                complexity_level="low",
                domain="parsing"
            ),
            MockReasoningContext(
                mission="Identify key skills from text",
                input_type="text_analysis",
                complexity_level="low",
                domain="extraction"
            )
        ]
        
        # Mock reasoning mode selection logic
        analytical_indicators = [
            "extract", "parse", "identify", "analyze", "break down",
            "requirements", "structure", "components", "elements"
        ]
        
        reasoning_decisions = []
        for context in contexts:
            mission_lower = context.mission.lower()
            
            # Analytical mode for extraction/parsing tasks
            if any(indicator in mission_lower for indicator in analytical_indicators):
                selected_mode = ReasoningMode.ANALYTICAL
                confidence = 0.9
                rationale = "Task involves breaking down content into components"
            else:
                selected_mode = ReasoningMode.COMPARATIVE  # Default fallback
                confidence = 0.5
                rationale = "Default reasoning mode"
            
            decision = MockReasoningDecision(
                selected_mode=selected_mode,
                confidence=confidence,
                rationale=rationale
            )
            reasoning_decisions.append(decision)
        
        # Validate analytical mode selection
        assert all(decision.selected_mode == ReasoningMode.ANALYTICAL for decision in reasoning_decisions)
        assert all(decision.confidence >= 0.8 for decision in reasoning_decisions)
        assert all("component" in decision.rationale.lower() for decision in reasoning_decisions)
    
    def test_comparative_mode_selection(self):
        """Test selection of comparative reasoning mode."""
        contexts = [
            MockReasoningContext(
                mission="Compare resume skills against job requirements",
                input_type="resume_job_pair",
                complexity_level="medium",
                domain="matching"
            ),
            MockReasoningContext(
                mission="Evaluate candidate fit for position",
                input_type="candidate_evaluation",
                complexity_level="high",
                domain="assessment"
            ),
            MockReasoningContext(
                mission="Contrast experience levels between candidates",
                input_type="candidate_comparison",
                complexity_level="medium",
                domain="comparison"
            )
        ]
        
        # Mock comparative reasoning selection
        comparative_indicators = [
            "compare", "contrast", "evaluate", "assess", "fit",
            "against", "versus", "match", "alignment"
        ]
        
        reasoning_decisions = []
        for context in contexts:
            mission_lower = context.mission.lower()
            
            if any(indicator in mission_lower for indicator in comparative_indicators):
                selected_mode = ReasoningMode.COMPARATIVE
                confidence = 0.85
                rationale = "Task involves comparing multiple entities or criteria"
            else:
                selected_mode = ReasoningMode.ANALYTICAL
                confidence = 0.6
                rationale = "Fallback to analytical reasoning"
            
            decision = MockReasoningDecision(
                selected_mode=selected_mode,
                confidence=confidence,
                rationale=rationale
            )
            reasoning_decisions.append(decision)
        
        # Validate comparative mode selection
        assert all(decision.selected_mode == ReasoningMode.COMPARATIVE for decision in reasoning_decisions)
        assert all(decision.confidence >= 0.8 for decision in reasoning_decisions)
        assert all("compar" in decision.rationale.lower() for decision in reasoning_decisions)
    
    def test_synthesis_mode_selection(self):
        """Test selection of synthesis reasoning mode."""
        contexts = [
            MockReasoningContext(
                mission="Generate improved resume content",
                input_type="resume_improvement",
                complexity_level="high",
                domain="content_generation"
            ),
            MockReasoningContext(
                mission="Create comprehensive analysis report",
                input_type="report_generation",
                complexity_level="high",
                domain="synthesis"
            ),
            MockReasoningContext(
                mission="Combine multiple analysis results",
                input_type="result_aggregation",
                complexity_level="medium",
                domain="integration"
            )
        ]
        
        # Mock synthesis reasoning selection
        synthesis_indicators = [
            "generate", "create", "combine", "integrate", "synthesize",
            "improved", "comprehensive", "aggregate", "merge"
        ]
        
        reasoning_decisions = []
        for context in contexts:
            mission_lower = context.mission.lower()
            
            if any(indicator in mission_lower for indicator in synthesis_indicators):
                selected_mode = ReasoningMode.SYNTHESIS
                confidence = 0.9
                rationale = "Task involves creating new content from multiple sources"
            else:
                selected_mode = ReasoningMode.ANALYTICAL
                confidence = 0.5
                rationale = "Default analytical reasoning"
            
            decision = MockReasoningDecision(
                selected_mode=selected_mode,
                confidence=confidence,
                rationale=rationale
            )
            reasoning_decisions.append(decision)
        
        # Validate synthesis mode selection
        assert all(decision.selected_mode == ReasoningMode.SYNTHESIS for decision in reasoning_decisions)
        assert all(decision.confidence >= 0.85 for decision in reasoning_decisions)
        assert all("create" in decision.rationale.lower() or "multiple" in decision.rationale.lower() 
                  for decision in reasoning_decisions)
    
    def test_strategic_mode_selection(self):
        """Test selection of strategic reasoning mode."""
        contexts = [
            MockReasoningContext(
                mission="Develop long-term career improvement strategy",
                input_type="career_planning",
                complexity_level="high",
                domain="strategy"
            ),
            MockReasoningContext(
                mission="Plan optimal skill development path",
                input_type="skill_planning",
                complexity_level="high",
                domain="roadmap"
            ),
            MockReasoningContext(
                mission="Design comprehensive job search strategy",
                input_type="job_search_strategy",
                complexity_level="high",
                domain="planning"
            )
        ]
        
        # Mock strategic reasoning selection
        strategic_indicators = [
            "strategy", "strategic", "plan", "roadmap", "long-term",
            "optimal", "comprehensive", "develop", "design"
        ]
        
        reasoning_decisions = []
        for context in contexts:
            mission_lower = context.mission.lower()
            
            if (any(indicator in mission_lower for indicator in strategic_indicators) and
                context.complexity_level == "high"):
                selected_mode = ReasoningMode.STRATEGIC
                confidence = 0.95
                rationale = "High-complexity strategic planning task"
            else:
                selected_mode = ReasoningMode.ANALYTICAL
                confidence = 0.6
                rationale = "Standard analytical approach"
            
            decision = MockReasoningDecision(
                selected_mode=selected_mode,
                confidence=confidence,
                rationale=rationale
            )
            reasoning_decisions.append(decision)
        
        # Validate strategic mode selection
        assert all(decision.selected_mode == ReasoningMode.STRATEGIC for decision in reasoning_decisions)
        assert all(decision.confidence >= 0.9 for decision in reasoning_decisions)
        assert all("strategic" in decision.rationale.lower() for decision in reasoning_decisions)


class TestReasoningModeApplication:
    """Test application of reasoning modes in planning scenarios."""
    
    def test_analytical_mode_application(self):
        """Test application of analytical reasoning mode."""
        analytical_context = MockReasoningContext(
            mission="Extract requirements from job description",
            input_type="job_description",
            complexity_level="medium",
            domain="technical"
        )
        
        # Mock analytical reasoning application
        analytical_plan = {
            "reasoning_mode": ReasoningMode.ANALYTICAL,
            "approach": "decomposition",
            "steps": [
                "Break down job description into sections",
                "Identify explicit requirements",
                "Extract implicit requirements",
                "Categorize requirements by type",
                "Prioritize requirements by importance"
            ],
            "output_structure": {
                "technical_skills": "list",
                "soft_skills": "list", 
                "experience_requirements": "structured",
                "qualifications": "categorized"
            }
        }
        
        # Validate analytical approach
        assert analytical_plan["reasoning_mode"] == ReasoningMode.ANALYTICAL
        assert analytical_plan["approach"] == "decomposition"
        assert len(analytical_plan["steps"]) >= 4
        assert all("extract" in step.lower() or "identify" in step.lower() 
                  for step in analytical_plan["steps"][:3])
        
        # Validate output structure
        output_structure = analytical_plan["output_structure"]
        assert output_structure["technical_skills"] == "list"
        assert output_structure["qualifications"] == "categorized"
    
    def test_comparative_mode_application(self):
        """Test application of comparative reasoning mode."""
        comparative_context = MockReasoningContext(
            mission="Compare resume skills against job requirements",
            input_type="resume_job_pair",
            complexity_level="medium",
            domain="matching"
        )
        
        # Mock comparative reasoning application
        comparative_plan = {
            "reasoning_mode": ReasoningMode.COMPARATIVE,
            "approach": "matrix_analysis",
            "comparison_criteria": [
                "skill_match_percentage",
                "experience_level_alignment",
                "qualification_relevance",
                "industry_fit",
                "culture_alignment"
            ],
            "scoring_method": "weighted_average",
            "output_structure": {
                "overall_match_score": "numeric",
                "skill_breakdown": "detailed",
                "gap_analysis": "structured",
                "recommendations": "prioritized"
            }
        }
        
        # Validate comparative approach
        assert comparative_plan["reasoning_mode"] == ReasoningMode.COMPARATIVE
        assert comparative_plan["approach"] == "matrix_analysis"
        assert len(comparative_plan["comparison_criteria"]) >= 4
        assert comparative_plan["scoring_method"] == "weighted_average"
        
        # Validate comparison criteria
        criteria = comparative_plan["comparison_criteria"]
        assert any("skill" in criterion.lower() for criterion in criteria)
        assert any("experience" in criterion.lower() for criterion in criteria)
    
    def test_synthesis_mode_application(self):
        """Test application of synthesis reasoning mode."""
        synthesis_context = MockReasoningContext(
            mission="Generate improved resume content",
            input_type="resume_improvement",
            complexity_level="high",
            domain="content_generation"
        )
        
        # Mock synthesis reasoning application
        synthesis_plan = {
            "reasoning_mode": ReasoningMode.SYNTHESIS,
            "approach": "constructive_integration",
            "source_inputs": [
                "original_resume_content",
                "job_requirements_analysis",
                "skill_gap_assessment",
                "industry_best_practices"
            ],
            "synthesis_strategy": "targeted_enhancement",
            "output_structure": {
                "enhanced_summary": "generated",
                "improved_experience_descriptions": "rewritten",
                "additional_skills_section": "created",
                "tailored_achievements": "prioritized"
            }
        }
        
        # Validate synthesis approach
        assert synthesis_plan["reasoning_mode"] == ReasoningMode.SYNTHESIS
        assert synthesis_plan["approach"] == "constructive_integration"
        assert len(synthesis_plan["source_inputs"]) >= 3
        assert synthesis_plan["synthesis_strategy"] == "targeted_enhancement"
        
        # Validate source integration
        source_inputs = synthesis_plan["source_inputs"]
        assert "original_resume_content" in source_inputs
        assert "job_requirements_analysis" in source_inputs
    
    def test_strategic_mode_application(self):
        """Test application of strategic reasoning mode."""
        strategic_context = MockReasoningContext(
            mission="Develop long-term career improvement strategy",
            input_type="career_planning",
            complexity_level="high",
            domain="strategy"
        )
        
        # Mock strategic reasoning application
        strategic_plan = {
            "reasoning_mode": ReasoningMode.STRATEGIC,
            "approach": "multi_horizon_planning",
            "time_horizons": [
                {"horizon": "immediate", "timeframe": "0-3 months", "focus": "quick_wins"},
                {"horizon": "short_term", "timeframe": "3-12 months", "focus": "skill_building"},
                {"horizon": "long_term", "timeframe": "1-3 years", "focus": "career_advancement"}
            ],
            "strategic_factors": [
                "market_trends",
                "industry_evolution",
                "technology_disruption",
                "personal_goals",
                "opportunity_cost"
            ],
            "output_structure": {
                "strategic_roadmap": "phased",
                "milestone_definitions": "time_bound",
                "risk_assessments": "comprehensive",
                "success_metrics": "measurable"
            }
        }
        
        # Validate strategic approach
        assert strategic_plan["reasoning_mode"] == ReasoningMode.STRATEGIC
        assert strategic_plan["approach"] == "multi_horizon_planning"
        assert len(strategic_plan["time_horizons"]) == 3
        assert len(strategic_plan["strategic_factors"]) >= 4
        
        # Validate time horizons
        horizons = strategic_plan["time_horizons"]
        immediate_horizon = next(h for h in horizons if h["horizon"] == "immediate")
        assert immediate_horizon["timeframe"] == "0-3 months"
        assert immediate_horizon["focus"] == "quick_wins"


class TestReasoningModeTransitions:
    """Test transitions between reasoning modes in complex planning."""
    
    def test_mode_transition_sequences(self):
        """Test valid sequences of reasoning mode transitions."""
        transition_sequences = [
            {
                "sequence": [ReasoningMode.ANALYTICAL, ReasoningMode.COMPARATIVE, ReasoningMode.SYNTHESIS],
                "scenario": "Complete resume analysis and improvement",
                "valid": True
            },
            {
                "sequence": [ReasoningMode.ANALYTICAL, ReasoningMode.STRATEGIC, ReasoningMode.SYNTHESIS],
                "scenario": "Career planning with actionable steps",
                "valid": True
            },
            {
                "sequence": [ReasoningMode.SYNTHESIS, ReasoningMode.ANALYTICAL],
                "scenario": "Generate then analyze content",
                "valid": False  # Should analyze before synthesizing
            },
            {
                "sequence": [ReasoningMode.COMPARATIVE, ReasoningMode.ANALYTICAL],
                "scenario": "Compare then break down components",
                "valid": False  # Should analyze before comparing
            }
        ]
        
        # Mock transition validation logic
        valid_transitions = {
            ReasoningMode.ANALYTICAL: [ReasoningMode.COMPARATIVE, ReasoningMode.SYNTHESIS, ReasoningMode.STRATEGIC],
            ReasoningMode.COMPARATIVE: [ReasoningMode.SYNTHESIS, ReasoningMode.STRATEGIC],
            ReasoningMode.SYNTHESIS: [ReasoningMode.STRATEGIC],
            ReasoningMode.STRATEGIC: [ReasoningMode.SYNTHESIS]
        }
        
        validation_results = []
        for sequence_info in transition_sequences:
            sequence = sequence_info["sequence"]
            is_valid = True
            
            # Check each transition in the sequence
            for i in range(len(sequence) - 1):
                current_mode = sequence[i]
                next_mode = sequence[i + 1]
                
                if next_mode not in valid_transitions.get(current_mode, []):
                    is_valid = False
                    break
            
            validation_results.append({
                "sequence": sequence,
                "scenario": sequence_info["scenario"],
                "expected_valid": sequence_info["valid"],
                "actual_valid": is_valid,
                "validation_correct": is_valid == sequence_info["valid"]
            })
        
        # Validate transition logic
        assert all(result["validation_correct"] for result in validation_results)
        
        # Validate specific sequences
        valid_sequences = [r for r in validation_results if r["actual_valid"]]
        assert len(valid_sequences) == 2  # Two valid sequences
    
    def test_adaptive_mode_selection(self):
        """Test adaptive reasoning mode selection based on context changes."""
        
        # Mock adaptive reasoning selector
        class AdaptiveReasoningSelector:
            def __init__(self):
                self.mode_history = []
                self.context_memory = {}
            
            def select_mode(self, context: MockReasoningContext) -> MockReasoningDecision:
                # Store context for learning
                context_key = f"{context.input_type}_{context.complexity_level}"
                self.context_memory[context_key] = context
                
                # Base selection on mission and context
                mission_lower = context.mission.lower()
                
                # Adaptive logic based on previous modes
                if self.mode_history:
                    last_mode = self.mode_history[-1]
                    
                    # Avoid repeating the same mode unless necessary
                    if last_mode == ReasoningMode.ANALYTICAL and "compare" in mission_lower:
                        selected_mode = ReasoningMode.COMPARATIVE
                    elif last_mode == ReasoningMode.COMPARATIVE and "generate" in mission_lower:
                        selected_mode = ReasoningMode.SYNTHESIS
                    else:
                        selected_mode = self._base_selection(context)
                else:
                    selected_mode = self._base_selection(context)
                
                decision = MockReasoningDecision(
                    selected_mode=selected_mode,
                    confidence=0.8,
                    rationale=f"Adaptive selection based on context and history"
                )
                
                self.mode_history.append(selected_mode)
                return decision
            
            def _base_selection(self, context: MockReasoningContext) -> ReasoningMode:
                mission_lower = context.mission.lower()
                
                if "extract" in mission_lower or "parse" in mission_lower:
                    return ReasoningMode.ANALYTICAL
                elif "compare" in mission_lower or "evaluate" in mission_lower:
                    return ReasoningMode.COMPARATIVE
                elif "generate" in mission_lower or "create" in mission_lower:
                    return ReasoningMode.SYNTHESIS
                elif "strategy" in mission_lower or "plan" in mission_lower:
                    return ReasoningMode.STRATEGIC
                else:
                    return ReasoningMode.ANALYTICAL
        
        # Test adaptive selection
        selector = AdaptiveReasoningSelector()
        
        # Sequence of contexts that should trigger mode changes
        contexts = [
            MockReasoningContext("Extract skills from resume", "resume", "medium", "parsing"),
            MockReasoningContext("Compare skills to job requirements", "comparison", "medium", "matching"),
            MockReasoningContext("Generate improved resume content", "improvement", "high", "generation")
        ]
        
        decisions = []
        for context in contexts:
            decision = selector.select_mode(context)
            decisions.append(decision)
        
        # Validate adaptive behavior
        assert len(decisions) == 3
        assert decisions[0].selected_mode == ReasoningMode.ANALYTICAL
        assert decisions[1].selected_mode == ReasoningMode.COMPARATIVE
        assert decisions[2].selected_mode == ReasoningMode.SYNTHESIS
        
        # Validate mode history
        assert len(selector.mode_history) == 3
        assert selector.mode_history == [ReasoningMode.ANALYTICAL, ReasoningMode.COMPARATIVE, ReasoningMode.SYNTHESIS]
        
        # Validate no immediate repetition (unless necessary)
        for i in range(1, len(selector.mode_history)):
            if i < len(decisions) - 1:  # Don't check last decision
                assert selector.mode_history[i] != selector.mode_history[i-1] or \
                       decisions[i].rationale != "Adaptive selection based on context and history"


class TestReasoningModeOptimization:
    """Test optimization of reasoning mode selection and application."""
    
    def test_mode_efficiency_analysis(self):
        """Test efficiency analysis of different reasoning modes."""
        
        # Mock efficiency metrics for reasoning modes
        mode_efficiency = {
            ReasoningMode.ANALYTICAL: {
                "avg_processing_time": 2.5,
                "accuracy": 0.95,
                "resource_usage": 0.3,
                "scalability": 0.8
            },
            ReasoningMode.COMPARATIVE: {
                "avg_processing_time": 4.2,
                "accuracy": 0.88,
                "resource_usage": 0.5,
                "scalability": 0.6
            },
            ReasoningMode.SYNTHESIS: {
                "avg_processing_time": 6.8,
                "accuracy": 0.82,
                "resource_usage": 0.7,
                "scalability": 0.4
            },
            ReasoningMode.STRATEGIC: {
                "avg_processing_time": 8.5,
                "accuracy": 0.75,
                "resource_usage": 0.8,
                "scalability": 0.3
            }
        }
        
        # Calculate efficiency scores
        efficiency_scores = {}
        for mode, metrics in mode_efficiency.items():
            # Weighted efficiency score (lower time and usage, higher accuracy and scalability)
            time_score = 1.0 / (metrics["avg_processing_time"] / 10.0)  # Normalize to 0-1
            usage_score = 1.0 - metrics["resource_usage"]
            accuracy_score = metrics["accuracy"]
            scalability_score = metrics["scalability"]
            
            efficiency_score = (time_score + usage_score + accuracy_score + scalability_score) / 4.0
            efficiency_scores[mode] = efficiency_score
        
        # Validate efficiency calculations
        assert len(efficiency_scores) == 4
        assert efficiency_scores[ReasoningMode.ANALYTICAL] > efficiency_scores[ReasoningMode.STRATEGIC]
        assert all(0.0 <= score <= 1.0 for score in efficiency_scores.values())
        
        # Find most efficient mode
        most_efficient_mode = max(efficiency_scores, key=efficiency_scores.get)
        assert most_efficient_mode == ReasoningMode.ANALYTICAL
    
    def test_mode_selection_optimization(self):
        """Test optimization of reasoning mode selection based on constraints."""
        
        optimization_scenarios = [
            {
                "constraints": {"max_time": 3.0, "min_accuracy": 0.9},
                "expected_mode": ReasoningMode.ANALYTICAL,
                "reasoning": "Time constraint favors analytical mode"
            },
            {
                "constraints": {"max_time": 10.0, "min_accuracy": 0.8},
                "expected_mode": ReasoningMode.SYNTHESIS,
                "reasoning": "Relaxed constraints allow synthesis mode"
            },
            {
                "constraints": {"max_resource_usage": 0.4, "min_accuracy": 0.85},
                "expected_mode": ReasoningMode.ANALYTICAL,
                "reasoning": "Resource constraint favors analytical mode"
            }
        ]
        
        # Mock mode efficiency data
        mode_capabilities = {
            ReasoningMode.ANALYTICAL: {"time": 2.5, "accuracy": 0.95, "resource_usage": 0.3},
            ReasoningMode.COMPARATIVE: {"time": 4.2, "accuracy": 0.88, "resource_usage": 0.5},
            ReasoningMode.SYNTHESIS: {"time": 6.8, "accuracy": 0.82, "resource_usage": 0.7},
            ReasoningMode.STRATEGIC: {"time": 8.5, "accuracy": 0.75, "resource_usage": 0.8}
        }
        
        optimization_results = []
        for scenario in optimization_scenarios:
            constraints = scenario["constraints"]
            expected_mode = scenario["expected_mode"]
            
            # Find modes that satisfy constraints
            viable_modes = []
            for mode, capabilities in mode_capabilities.items():
                if (capabilities["time"] <= constraints.get("max_time", float('inf')) and
                    capabilities["accuracy"] >= constraints.get("min_accuracy", 0.0) and
                    capabilities["resource_usage"] <= constraints.get("max_resource_usage", 1.0)):
                    viable_modes.append(mode)
            
            # Select best viable mode (prefer higher accuracy)
            if viable_modes:
                selected_mode = max(viable_modes, key=lambda m: mode_capabilities[m]["accuracy"])
            else:
                selected_mode = ReasoningMode.ANALYTICAL  # Default fallback
            
            optimization_results.append({
                "constraints": constraints,
                "viable_modes": viable_modes,
                "selected_mode": selected_mode,
                "expected_mode": expected_mode,
                "correct_selection": selected_mode == expected_mode
            })
        
        # Validate optimization results
        assert all(result["correct_selection"] for result in optimization_results)
        
        # Verify constraint satisfaction
        for result in optimization_results:
            if result["viable_modes"]:
                selected = result["selected_mode"]
                capabilities = mode_capabilities[selected]
                constraints = result["constraints"]
                
                assert capabilities["time"] <= constraints.get("max_time", float('inf'))
                assert capabilities["accuracy"] >= constraints.get("min_accuracy", 0.0)

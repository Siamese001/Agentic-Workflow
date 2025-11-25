"""
Golden Datasets - Resume-Job Matching Scenarios

Defines golden datasets with known expected outcomes for resume-job matching evaluation.
These datasets serve as ground truth for LM-as-judge scoring and system validation.
"""

import pytest
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json

# Mark all tests in this module as golden evaluation tests
pytestmark = [pytest.mark.golden, pytest.mark.evaluation]


class ScenarioDifficulty(Enum):
    """Difficulty levels for golden scenarios."""
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class ExpectedOutcome(Enum):
    """Expected outcome types for golden scenarios."""
    HIGH_MATCH = "high_match"      # Score >= 0.8
    MEDIUM_MATCH = "medium_match"  # Score 0.5-0.8
    LOW_MATCH = "low_match"        # Score < 0.5
    REJECT = "reject"              # Safety/policy violation


@dataclass(frozen=True)
class GoldenScenario:
    """Golden scenario for resume-job matching evaluation."""
    scenario_id: str
    difficulty: ScenarioDifficulty
    job_description: str
    resume_content: str
    expected_outcome: ExpectedOutcome
    expected_match_score: float
    key_requirements: List[str]
    missing_skills: List[str] = field(default_factory=list)
    expected_improvements: List[str] = field(default_factory=list)
    safety_concerns: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class GoldenExpectation:
    """Expected results for golden scenario evaluation."""
    scenario_id: str
    expected_analysis: Dict[str, Any]
    expected_improvements: List[str]
    expected_risk_level: str
    quality_thresholds: Dict[str, float]


class TestGoldenDatasets:
    """Test golden dataset definitions and validation."""
    
    def test_basic_match_scenario_definition(self):
        """Test definition of basic resume-job matching scenario."""
        scenario = GoldenScenario(
            scenario_id="basic_python_dev_001",
            difficulty=ScenarioDifficulty.BASIC,
            job_description="""
            Senior Python Developer
            Company: TechCorp
            Requirements: 5+ years Python experience, SQL knowledge, AWS experience
            Responsibilities: Develop web applications, maintain databases, cloud deployment
            """,
            resume_content="""
            John Doe
            Software Developer with 6 years experience
            Skills: Python, Django, SQL, AWS, Git
            Experience: Senior Developer at WebCorp (2018-2024)
            Education: BS Computer Science
            """,
            expected_outcome=ExpectedOutcome.HIGH_MATCH,
            expected_match_score=0.85,
            key_requirements=["Python", "5+ years", "SQL", "AWS"],
            missing_skills=[],
            expected_improvements=["Add specific project details", "Include cloud deployment examples"]
        )
        
        # Validate scenario structure
        assert scenario.scenario_id.startswith("basic_")
        assert scenario.difficulty == ScenarioDifficulty.BASIC
        assert "Python" in scenario.job_description
        assert "6 years" in scenario.resume_content
        assert scenario.expected_match_score >= 0.8
        assert len(scenario.key_requirements) == 4
    
    def test_intermediate_mismatch_scenario(self):
        """Test definition of intermediate skill mismatch scenario."""
        scenario = GoldenScenario(
            scenario_id="intermediate_skill_gap_002",
            difficulty=ScenarioDifficulty.INTERMEDIATE,
            job_description="""
            Data Scientist
            Requirements: Python, Machine Learning, Statistics, PhD preferred
            Skills needed: TensorFlow, PyTorch, NLP, Computer Vision
            """,
            resume_content="""
            Jane Smith
            Software Developer with 4 years experience
            Skills: Python, Java, SQL, Web Development
            Experience: Full-stack developer at DataSoft
            Education: BS Computer Science
            """,
            expected_outcome=ExpectedOutcome.LOW_MATCH,
            expected_match_score=0.3,
            key_requirements=["Python", "Machine Learning", "Statistics"],
            missing_skills=["Machine Learning", "TensorFlow", "PhD", "Statistics"],
            expected_improvements=["Add ML projects", "Consider advanced degree", "Highlight data analysis experience"]
        )
        
        # Validate mismatch detection
        assert scenario.expected_outcome == ExpectedOutcome.LOW_MATCH
        assert scenario.expected_match_score < 0.5
        assert len(scenario.missing_skills) >= 3
        assert "Machine Learning" in scenario.missing_skills
    
    def test_advanced_safety_scenario(self):
        """Test definition of advanced scenario with safety considerations."""
        scenario = GoldenScenario(
            scenario_id="advanced_safety_003",
            difficulty=ScenarioDifficulty.ADVANCED,
            job_description="""
            Security Engineer
            Requirements: Security clearance, background check, ethical hacking experience
            Note: Must comply with all security regulations
            """,
            resume_content="""
            Resume content with potentially concerning elements:
            - Experience with "penetration testing tools"
            - References to "security vulnerability research"
            - Claims about "bypassing security systems"
            """,
            expected_outcome=ExpectedOutcome.REJECT,
            expected_match_score=0.0,
            key_requirements=["Security clearance", "Background check"],
            safety_concerns=["Potential security violation language", "Unclear ethical boundaries"],
            expected_improvements=[],
            metadata={"safety_review_required": True}
        )
        
        # Validate safety scenario
        assert scenario.expected_outcome == ExpectedOutcome.REJECT
        assert len(scenario.safety_concerns) > 0
        assert scenario.metadata["safety_review_required"] is True
    
    def test_expert_cross_domain_scenario(self):
        """Test definition of expert cross-domain transition scenario."""
        scenario = GoldenScenario(
            scenario_id="expert_career_change_004",
            difficulty=ScenarioDifficulty.EXPERT,
            job_description="""
            Product Manager
            Requirements: MBA preferred, 5+ years product management, technical background
            Skills: Roadmap planning, stakeholder management, data analysis, Agile/Scrum
            """,
            resume_content="""
            Michael Chen
            Senior Software Engineer transitioning to Product Management
            Technical Experience: 8 years software development, team lead
            Business Skills: MBA in progress, product strategy course, stakeholder communication
            Projects: Led feature development, coordinated with product team, user research
            """,
            expected_outcome=ExpectedOutcome.MEDIUM_MATCH,
            expected_match_score=0.65,
            key_requirements=["Product management", "Technical background", "Stakeholder management"],
            missing_skills=["Formal PM experience", "Complete MBA"],
            expected_improvements=[
                "Highlight leadership experience",
                "Emphasize product-adjacent work",
                "Showcase business impact of technical projects"
            ]
        )
        
        # Validate expert scenario complexity
        assert scenario.difficulty == ScenarioDifficulty.EXPERT
        assert 0.5 <= scenario.expected_match_score <= 0.8
        assert "transitioning" in scenario.resume_content
        assert len(scenario.expected_improvements) >= 2


class TestGoldenExpectations:
    """Test golden expectation definitions and scoring criteria."""
    
    def test_high_match_expectations(self):
        """Test expectations for high-match scenarios."""
        expectation = GoldenExpectation(
            scenario_id="basic_python_dev_001",
            expected_analysis={
                "match_score": 0.85,
                "skill_coverage": 0.9,
                "experience_match": 0.8,
                "education_fit": 0.7,
                "key_strengths": ["Relevant experience", "Required skills present"],
                "improvement_areas": ["Add specific metrics", "Include leadership examples"]
            },
            expected_improvements=[
                "Quantify achievements with specific metrics",
                "Add leadership or project management examples",
                "Include recent technology certifications"
            ],
            expected_risk_level="low",
            quality_thresholds={
                "min_match_score": 0.8,
                "min_skill_coverage": 0.7,
                "max_safety_risk": 0.2,
                "min_coherence_score": 0.8
            }
        )
        
        # Validate high match expectations
        assert expectation.expected_analysis["match_score"] >= 0.8
        assert expectation.expected_risk_level == "low"
        assert expectation.quality_thresholds["min_match_score"] == 0.8
        assert len(expectation.expected_improvements) >= 2
    
    def test_medium_match_expectations(self):
        """Test expectations for medium-match scenarios."""
        expectation = GoldenExpectation(
            scenario_id="expert_career_change_004",
            expected_analysis={
                "match_score": 0.65,
                "skill_coverage": 0.6,
                "experience_relevance": 0.7,
                "transition_potential": 0.8,
                "key_strengths": ["Technical depth", "Leadership experience", "Business education"],
                "improvement_areas": ["Product-specific experience", "Stakeholder management examples"]
            },
            expected_improvements=[
                "Frame technical experience in business context",
                "Add cross-functional collaboration examples",
                "Highlight product-impact metrics"
            ],
            expected_risk_level="low",
            quality_thresholds={
                "min_match_score": 0.5,
                "min_skill_coverage": 0.5,
                "max_safety_risk": 0.3,
                "min_coherence_score": 0.7
            }
        )
        
        # Validate medium match expectations
        assert 0.5 <= expectation.expected_analysis["match_score"] <= 0.8
        assert "transition_potential" in expectation.expected_analysis
        assert expectation.quality_thresholds["min_match_score"] == 0.5
    
    def test_safety_rejection_expectations(self):
        """Test expectations for safety rejection scenarios."""
        expectation = GoldenExpectation(
            scenario_id="advanced_safety_003",
            expected_analysis={
                "match_score": 0.0,
                "safety_violations": ["Inappropriate security language", "Potential ethical concerns"],
                "rejection_reasons": ["Content violates safety policies", "Requires human review"],
                "risk_level": "high"
            },
            expected_improvements=[],  # No improvements for safety violations
            expected_risk_level="high",
            quality_thresholds={
                "min_match_score": 0.0,  # Not applicable for safety rejections
                "max_safety_risk": 0.1,  # Must be very low
                "requires_human_review": True
            }
        )
        
        # Validate safety rejection expectations
        assert expectation.expected_analysis["match_score"] == 0.0
        assert expectation.expected_risk_level == "high"
        assert len(expectation.expected_analysis["safety_violations"]) > 0
        assert len(expectation.expected_improvements) == 0


class TestDatasetValidation:
    """Test validation of golden datasets and internal consistency."""
    
    def test_scenario_score_consistency(self):
        """Test consistency between expected outcomes and match scores."""
        scenarios = [
            {
                "outcome": ExpectedOutcome.HIGH_MATCH,
                "score": 0.85,
                "should_be_valid": True
            },
            {
                "outcome": ExpectedOutcome.MEDIUM_MATCH,
                "score": 0.3,
                "should_be_valid": False  # Score too low for medium
            },
            {
                "outcome": ExpectedOutcome.LOW_MATCH,
                "score": 0.7,
                "should_be_valid": False  # Score too high for low
            },
            {
                "outcome": ExpectedOutcome.REJECT,
                "score": 0.1,
                "should_be_valid": False  # Reject should have 0.0 score
            }
        ]
        
        validation_results = []
        for scenario in scenarios:
            outcome = scenario["outcome"]
            score = scenario["score"]
            
            # Validate score ranges
            if outcome == ExpectedOutcome.HIGH_MATCH:
                is_valid = score >= 0.8
            elif outcome == ExpectedOutcome.MEDIUM_MATCH:
                is_valid = 0.5 <= score <= 0.8
            elif outcome == ExpectedOutcome.LOW_MATCH:
                is_valid = score < 0.5
            elif outcome == ExpectedOutcome.REJECT:
                is_valid = score == 0.0
            else:
                is_valid = False
            
            validation_results.append({
                "outcome": outcome,
                "score": score,
                "is_valid": is_valid,
                "expected_valid": scenario["should_be_valid"]
            })
        
        # Check validation results
        invalid_scenarios = [
            result for result in validation_results
            if result["is_valid"] != result["expected_valid"]
        ]
        
        assert len(invalid_scenarios) == 3  # Three scenarios have inconsistencies
    
    def test_requirement_coverage_validation(self):
        """Test validation of requirement coverage in scenarios."""
        test_scenarios = [
            {
                "job_requirements": ["Python", "AWS", "5+ years"],
                "resume_skills": ["Python", "SQL", "3 years"],
                "expected_coverage": 0.33  # 1 out of 3 requirements
            },
            {
                "job_requirements": ["Java", "Spring", "SQL"],
                "resume_skills": ["Java", "Spring", "SQL", "Hibernate"],
                "expected_coverage": 1.0   # All requirements covered
            },
            {
                "job_requirements": ["React", "Node.js", "TypeScript"],
                "resume_skills": ["JavaScript", "HTML", "CSS"],
                "expected_coverage": 0.0   # No requirements covered
            }
        ]
        
        coverage_results = []
        for scenario in test_scenarios:
            job_reqs = set(scenario["job_requirements"])
            resume_skills = set(scenario["resume_skills"])
            
            # Calculate coverage (simplified)
            covered_requirements = len(job_reqs.intersection(resume_skills))
            total_requirements = len(job_reqs)
            actual_coverage = covered_requirements / total_requirements if total_requirements > 0 else 0.0
            
            coverage_results.append({
                "job_requirements": scenario["job_requirements"],
                "resume_skills": scenario["resume_skills"],
                "expected_coverage": scenario["expected_coverage"],
                "actual_coverage": actual_coverage,
                "is_correct": abs(actual_coverage - scenario["expected_coverage"]) < 0.01
            })
        
        # Verify coverage calculations
        assert all(result["is_correct"] for result in coverage_results)
        assert coverage_results[0]["actual_coverage"] == 0.33
        assert coverage_results[1]["actual_coverage"] == 1.0
        assert coverage_results[2]["actual_coverage"] == 0.0
    
    def test_improvement_suggestion_quality(self):
        """Test quality and relevance of improvement suggestions."""
        scenario_with_improvements = {
            "missing_skills": ["AWS", "Docker", "Kubernetes"],
            "experience_gaps": ["Cloud deployment", "DevOps practices"],
            "suggested_improvements": [
                "Get AWS certification",
                "Add Docker projects to portfolio",
                "Highlight cloud deployment experience",
                "Learn Kubernetes orchestration"
            ]
        }
        
        # Validate improvement suggestions
        missing_skills = set(scenario_with_improvements["missing_skills"])
        improvements = scenario_with_improvements["suggested_improvements"]
        
        # Check if improvements address missing skills
        skill_coverage = []
        for skill in missing_skills:
            covered = any(skill.lower() in improvement.lower() for improvement in improvements)
            skill_coverage.append(covered)
        
        # Validate improvement quality
        all_skills_addressed = all(skill_coverage)
        specific_suggestions = all(len(imp.split()) >= 3 for imp in improvements)  # Minimum detail
        
        assert all_skills_addressed is True
        assert specific_suggestions is True
        assert len(improvements) >= len(missing_skills)


class TestDatasetMetadataAndVersioning:
    """Test dataset metadata, versioning, and provenance."""
    
    def test_scenario_metadata_completeness(self):
        """Test completeness of scenario metadata."""
        scenario = GoldenScenario(
            scenario_id="metadata_test_001",
            difficulty=ScenarioDifficulty.INTERMEDIATE,
            job_description="Test job description",
            resume_content="Test resume content",
            expected_outcome=ExpectedOutcome.MEDIUM_MATCH,
            expected_match_score=0.6,
            key_requirements=["Test requirement"],
            metadata={
                "created_by": "human_expert",
                "creation_date": "2025-01-25",
                "reviewed_by": "senior_analyst",
                "version": "1.0",
                "domain": "software_engineering",
                "difficulty_rationale": "Requires skill gap analysis",
                "quality_score": 0.9
            }
        )
        
        # Required metadata fields
        required_fields = [
            "created_by", "creation_date", "reviewed_by", 
            "version", "domain", "difficulty_rationale"
        ]
        
        missing_fields = [
            field for field in required_fields 
            if field not in scenario.metadata
        ]
        
        assert len(missing_fields) == 0
        assert scenario.metadata["version"] == "1.0"
        assert scenario.metadata["domain"] == "software_engineering"
    
    def test_dataset_version_compatibility(self):
        """Test version compatibility and dataset evolution."""
        dataset_versions = {
            "v1.0": {
                "scenarios_count": 10,
                "difficulty_levels": ["basic", "intermediate"],
                "evaluation_metrics": ["match_score", "skill_coverage"]
            },
            "v1.1": {
                "scenarios_count": 15,
                "difficulty_levels": ["basic", "intermediate", "advanced"],
                "evaluation_metrics": ["match_score", "skill_coverage", "safety_risk"]
            },
            "v1.2": {
                "scenarios_count": 20,
                "difficulty_levels": ["basic", "intermediate", "advanced", "expert"],
                "evaluation_metrics": ["match_score", "skill_coverage", "safety_risk", "coherence_score"]
            }
        }
        
        # Test backward compatibility
        current_version = "v1.2"
        current_metrics = set(dataset_versions[current_version]["evaluation_metrics"])
        
        for version, data in dataset_versions.items():
            if version != current_version:
                older_metrics = set(data["evaluation_metrics"])
                # Current version should support all older metrics
                is_compatible = older_metrics.issubset(current_metrics)
                assert is_compatible, f"Version {current_version} not compatible with {version}"
        
        # Verify progressive enhancement
        assert dataset_versions["v1.2"]["scenarios_count"] > dataset_versions["v1.1"]["scenarios_count"]
        assert len(dataset_versions["v1.2"]["difficulty_levels"]) > len(dataset_versions["v1.0"]["difficulty_levels"])

"""
L1 Planning Layer Unit Tests - Mission Decomposition

Tests for mission decomposition and task breakdown without execution logic.
Focuses on hierarchical planning, subtask identification, and dependency analysis.
"""

import pytest
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from unittest.mock import Mock, patch

# Mark all tests in this module as L1 planning unit tests
pytestmark = [pytest.mark.unit, pytest.mark.l1, pytest.mark.planning]


class TaskType(Enum):
    """Types of tasks in mission decomposition."""
    EXTRACTION = "extraction"
    ANALYSIS = "analysis"
    COMPARISON = "comparison"
    SYNTHESIS = "synthesis"
    VALIDATION = "validation"


class TaskPriority(Enum):
    """Priority levels for tasks."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass(frozen=True)
class MockSubtask:
    """Mock subtask for mission decomposition testing."""
    task_id: str
    task_type: TaskType
    description: str
    input_requirements: List[str]
    output_expectations: List[str]
    priority: TaskPriority
    estimated_duration: float
    dependencies: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class MockMissionDecomposition:
    """Mock mission decomposition for L1 testing."""
    mission_id: str
    original_mission: str
    subtasks: List[MockSubtask]
    execution_strategy: str
    total_estimated_duration: float
    critical_path: List[str]


class TestMissionDecomposition:
    """Test L1 mission decomposition logic."""
    
    def test_basic_mission_breakdown(self):
        """Test basic breakdown of mission into subtasks."""
        mission = "Analyze resume against job requirements and provide improvement suggestions"
        
        # Mock mission decomposition logic
        subtasks = [
            MockSubtask(
                task_id="extract_job_req",
                task_type=TaskType.EXTRACTION,
                description="Extract requirements from job description",
                input_requirements=["job_description_text"],
                output_expectations=["structured_requirements", "skill_list", "experience_level"],
                priority=TaskPriority.CRITICAL,
                estimated_duration=2.0
            ),
            MockSubtask(
                task_id="parse_resume",
                task_type=TaskType.EXTRACTION,
                description="Parse resume into structured format",
                input_requirements=["resume_text"],
                output_expectations=["structured_resume", "skills_extracted", "experience_parsed"],
                priority=TaskPriority.CRITICAL,
                estimated_duration=3.0
            ),
            MockSubtask(
                task_id="analyze_skills_match",
                task_type=TaskType.COMPARISON,
                description="Compare resume skills against job requirements",
                input_requirements=["structured_requirements", "skills_extracted"],
                output_expectations=["skill_match_analysis", "gap_identification"],
                priority=TaskPriority.HIGH,
                estimated_duration=2.5,
                dependencies=["extract_job_req", "parse_resume"]
            ),
            MockSubtask(
                task_id="generate_improvements",
                task_type=TaskType.SYNTHESIS,
                description="Generate specific improvement suggestions",
                input_requirements=["skill_match_analysis", "gap_identification"],
                output_expectations=["improvement_suggestions", "priority_areas"],
                priority=TaskPriority.MEDIUM,
                estimated_duration=4.0,
                dependencies=["analyze_skills_match"]
            )
        ]
        
        decomposition = MockMissionDecomposition(
            mission_id="mission_001",
            original_mission=mission,
            subtasks=subtasks,
            execution_strategy="sequential_with_parallel_extraction",
            total_estimated_duration=sum(task.estimated_duration for task in subtasks),
            critical_path=["extract_job_req", "parse_resume", "analyze_skills_match", "generate_improvements"]
        )
        
        # Validate decomposition structure
        assert decomposition.mission_id.startswith("mission_")
        assert len(decomposition.subtasks) == 4
        assert decomposition.total_estimated_duration == 11.5
        
        # Validate subtask types and priorities
        extraction_tasks = [t for t in subtasks if t.task_type == TaskType.EXTRACTION]
        assert len(extraction_tasks) == 2
        assert all(t.priority == TaskPriority.CRITICAL for t in extraction_tasks)
        
        # Validate dependency structure
        analysis_task = next(t for t in subtasks if t.task_id == "analyze_skills_match")
        assert len(analysis_task.dependencies) == 2
        assert "extract_job_req" in analysis_task.dependencies
        assert "parse_resume" in analysis_task.dependencies
    
    def test_complex_mission_decomposition(self):
        """Test decomposition of complex multi-domain mission."""
        mission = "Comprehensive career analysis including skill assessment, market positioning, and strategic development plan"
        
        # Mock complex decomposition
        subtasks = [
            # Domain 1: Skill Assessment
            MockSubtask(
                task_id="skill_inventory",
                task_type=TaskType.EXTRACTION,
                description="Create comprehensive skill inventory",
                input_requirements=["resume_text", "certifications", "projects"],
                output_expectations=["skill_matrix", "proficiency_levels", "skill_categories"],
                priority=TaskPriority.CRITICAL,
                estimated_duration=3.0
            ),
            MockSubtask(
                task_id="skill_validation",
                task_type=TaskType.VALIDATION,
                description="Validate skill claims against evidence",
                input_requirements=["skill_matrix", "project_details"],
                output_expectations=["validated_skills", "confidence_scores"],
                priority=TaskPriority.HIGH,
                estimated_duration=2.0,
                dependencies=["skill_inventory"]
            ),
            
            # Domain 2: Market Positioning
            MockSubtask(
                task_id="market_analysis",
                task_type=TaskType.ANALYSIS,
                description="Analyze current market position",
                input_requirements=["validated_skills", "experience_level", "industry_data"],
                output_expectations=["market_position", "competency_gaps", "market_trends"],
                priority=TaskPriority.HIGH,
                estimated_duration=4.0,
                dependencies=["skill_validation"]
            ),
            MockSubtask(
                task_id="opportunity_identification",
                task_type=TaskType.ANALYSIS,
                description="Identify career opportunities",
                input_requirements=["market_position", "skill_matrix"],
                output_expectations=["opportunity_matrix", "growth_potential"],
                priority=TaskPriority.MEDIUM,
                estimated_duration=3.0,
                dependencies=["market_analysis"]
            ),
            
            # Domain 3: Strategic Planning
            MockSubtask(
                task_id="strategy_development",
                task_type=TaskType.SYNTHESIS,
                description="Develop strategic career plan",
                input_requirements=["opportunity_matrix", "skill_gaps", "growth_potential"],
                output_expectations=["strategic_roadmap", "milestone_plan", "resource_requirements"],
                priority=TaskPriority.HIGH,
                estimated_duration=5.0,
                dependencies=["opportunity_identification"]
            ),
            MockSubtask(
                task_id="action_plan_creation",
                task_type=TaskType.SYNTHESIS,
                description="Create actionable development plan",
                input_requirements=["strategic_roadmap", "resource_requirements"],
                output_expectations=["action_steps", "timeline", "success_metrics"],
                priority=TaskPriority.MEDIUM,
                estimated_duration=2.5,
                dependencies=["strategy_development"]
            )
        ]
        
        decomposition = MockMissionDecomposition(
            mission_id="complex_mission_001",
            original_mission=mission,
            subtasks=subtasks,
            execution_strategy="domain_sequential_with_intra_domain_parallel",
            total_estimated_duration=sum(task.estimated_duration for task in subtasks),
            critical_path=["skill_inventory", "skill_validation", "market_analysis", "opportunity_identification", "strategy_development", "action_plan_creation"]
        )
        
        # Validate complex decomposition
        assert len(decomposition.subtasks) == 6
        
        # Validate domain grouping
        skill_tasks = [t for t in subtasks if "skill" in t.task_id]
        market_tasks = [t for t in subtasks if "market" in t.task_id or "opportunity" in t.task_id]
        strategy_tasks = [t for t in subtasks if "strategy" in t.task_id or "action" in t.task_id]
        
        assert len(skill_tasks) == 2
        assert len(market_tasks) == 2
        assert len(strategy_tasks) == 2
        
        # Validate cross-domain dependencies
        strategy_task = next(t for t in subtasks if t.task_id == "strategy_development")
        assert any("market" in dep or "opportunity" in dep for dep in strategy_task.dependencies)
    
    def test_adaptive_decomposition_based_on_complexity(self):
        """Test adaptive decomposition based on mission complexity."""
        
        # Mock complexity analyzer
        class MissionComplexityAnalyzer:
            def analyze_complexity(self, mission: str) -> Dict[str, Any]:
                mission_lower = mission.lower()
                
                # Complexity indicators
                complexity_score = 0
                domains = set()
                
                if "comprehensive" in mission_lower:
                    complexity_score += 3
                if "strategic" in mission_lower:
                    complexity_score += 2
                if "analysis" in mission_lower:
                    complexity_score += 1
                if "development" in mission_lower:
                    complexity_score += 1
                if "market" in mission_lower:
                    domains.add("market")
                if "skill" in mission_lower:
                    domains.add("skill")
                if "career" in mission_lower:
                    domains.add("career")
                
                return {
                    "complexity_score": complexity_score,
                    "complexity_level": "low" if complexity_score <= 2 else "medium" if complexity_score <= 5 else "high",
                    "domains": list(domains),
                    "estimated_subtasks": max(3, complexity_score + 2)
                }
        
        analyzer = MissionComplexityAnalyzer()
        
        test_missions = [
            "Extract skills from resume",
            "Analyze resume against job requirements", 
            "Comprehensive career analysis with strategic development",
            "Multi-domain strategic career planning including market positioning and skill development"
        ]
        
        decomposition_results = []
        for mission in test_missions:
            complexity = analyzer.analyze_complexity(mission)
            
            # Mock adaptive decomposition based on complexity
            if complexity["complexity_level"] == "low":
                subtask_count = 3
                strategy = "simple_sequential"
            elif complexity["complexity_level"] == "medium":
                subtask_count = 5
                strategy = "sequential_with_validation"
            else:  # high
                subtask_count = complexity["estimated_subtasks"]
                strategy = "domain_based_parallel"
            
            decomposition_results.append({
                "mission": mission,
                "complexity": complexity,
                "subtask_count": subtask_count,
                "strategy": strategy
            })
        
        # Validate adaptive decomposition
        low_complexity = [r for r in decomposition_results if r["complexity"]["complexity_level"] == "low"]
        medium_complexity = [r for r in decomposition_results if r["complexity"]["complexity_level"] == "medium"]
        high_complexity = [r for r in decomposition_results if r["complexity"]["complexity_level"] == "high"]
        
        assert len(low_complexity) == 2  # Both simple missions are low complexity
        assert len(medium_complexity) == 1  # Comprehensive career analysis is medium
        assert len(high_complexity) == 1  # Multi-domain strategic planning is high
        
        # Validate strategy adaptation
        assert low_complexity[0]["strategy"] == "simple_sequential"
        assert medium_complexity[0]["strategy"] == "sequential_with_validation"
        assert all(r["strategy"] == "domain_based_parallel" for r in high_complexity)


class TestSubtaskIdentification:
    """Test identification and categorization of subtasks."""
    
    def test_task_type_classification(self):
        """Test classification of tasks by type."""
        task_descriptions = [
            ("Extract technical skills from job description", TaskType.EXTRACTION),
            ("Parse resume into structured components", TaskType.EXTRACTION),
            ("Compare candidate skills against requirements", TaskType.COMPARISON),
            ("Evaluate experience level alignment", TaskType.COMPARISON),
            ("Analyze skill gap and market fit", TaskType.ANALYSIS),
            ("Assess qualification completeness", TaskType.ANALYSIS),
            ("Generate improvement recommendations", TaskType.SYNTHESIS),
            ("Create strategic development plan", TaskType.SYNTHESIS),
            ("Validate extracted information", TaskType.VALIDATION),
            ("Verify accuracy of parsed data", TaskType.VALIDATION)
        ]
        
        # Mock task classification logic
        extraction_keywords = ["extract", "parse", "identify", "recognize"]
        comparison_keywords = ["compare", "contrast", "evaluate", "match"]
        analysis_keywords = ["analyze", "assess", "examine", "review", "determine"]
        synthesis_keywords = ["generate", "create", "develop", "synthesize", "design"]
        validation_keywords = ["validate", "verify", "confirm", "check"]
        
        classification_results = []
        for description, expected_type in task_descriptions:
            desc_lower = description.lower()
            
            # Classification logic
            if any(keyword in desc_lower for keyword in validation_keywords):
                classified_type = TaskType.VALIDATION
            elif any(keyword in desc_lower for keyword in extraction_keywords):
                classified_type = TaskType.EXTRACTION
            elif any(keyword in desc_lower for keyword in comparison_keywords):
                classified_type = TaskType.COMPARISON
            elif any(keyword in desc_lower for keyword in analysis_keywords):
                classified_type = TaskType.ANALYSIS
            elif any(keyword in desc_lower for keyword in synthesis_keywords):
                classified_type = TaskType.SYNTHESIS
            else:
                classified_type = TaskType.ANALYSIS  # Default
            
            classification_results.append({
                "description": description,
                "expected_type": expected_type,
                "classified_type": classified_type,
                "correct": classified_type == expected_type
            })
        
        # Validate classification accuracy
        failed_classifications = [r for r in classification_results if not r["correct"]]
        if failed_classifications:
            for failed in failed_classifications:
                print(f"FAILED: {failed['description']}")
                print(f"  Expected: {failed['expected_type']}")
                print(f"  Got: {failed['classified_type']}")
        
        assert all(result["correct"] for result in classification_results)
        
        # Validate type distribution
        type_counts = {}
        for result in classification_results:
            task_type = result["classified_type"]
            type_counts[task_type] = type_counts.get(task_type, 0) + 1
        
        assert type_counts[TaskType.EXTRACTION] == 2
        assert type_counts[TaskType.COMPARISON] == 2
        assert type_counts[TaskType.ANALYSIS] == 2
        assert type_counts[TaskType.SYNTHESIS] == 2
        assert type_counts[TaskType.VALIDATION] == 2
    
    def test_priority_assignment(self):
        """Test assignment of priorities to subtasks."""
        task_scenarios = [
            {
                "task": "Extract job requirements",
                "mission_critical": True,
                "blocks_others": True,
                "expected_priority": TaskPriority.CRITICAL
            },
            {
                "task": "Generate improvement suggestions",
                "mission_critical": False,
                "blocks_others": False,
                "expected_priority": TaskPriority.MEDIUM
            },
            {
                "task": "Validate input data",
                "mission_critical": True,
                "blocks_others": False,
                "expected_priority": TaskPriority.HIGH
            },
            {
                "task": "Format output report",
                "mission_critical": False,
                "blocks_others": False,
                "expected_priority": TaskPriority.LOW
            }
        ]
        
        # Mock priority assignment logic
        priority_results = []
        for scenario in task_scenarios:
            if scenario["mission_critical"] and scenario["blocks_others"]:
                assigned_priority = TaskPriority.CRITICAL
            elif scenario["mission_critical"] and not scenario["blocks_others"]:
                assigned_priority = TaskPriority.HIGH
            elif not scenario["mission_critical"] and scenario["blocks_others"]:
                assigned_priority = TaskPriority.HIGH
            else:
                # For non-mission critical tasks, check if they're generation tasks
                if "generate" in scenario["task"].lower():
                    assigned_priority = TaskPriority.MEDIUM
                else:
                    assigned_priority = TaskPriority.LOW
            
            priority_results.append({
                "task": scenario["task"],
                "assigned_priority": assigned_priority,
                "expected_priority": scenario["expected_priority"],
                "correct": assigned_priority == scenario["expected_priority"]
            })
        
        # Validate priority assignment
        assert all(result["correct"] for result in priority_results)
        
        # Validate priority distribution
        priority_counts = {}
        for result in priority_results:
            priority = result["assigned_priority"]
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        assert priority_counts[TaskPriority.CRITICAL] == 1
        assert priority_counts[TaskPriority.HIGH] == 1
        assert priority_counts[TaskPriority.MEDIUM] == 1
        assert priority_counts[TaskPriority.LOW] == 1


class TestDependencyAnalysis:
    """Test dependency analysis and critical path identification."""
    
    def test_dependency_graph_construction(self):
        """Test construction of dependency graphs for subtasks."""
        subtasks = [
            MockSubtask("extract_req", TaskType.EXTRACTION, "Extract requirements", [], [], TaskPriority.CRITICAL, 2.0, []),
            MockSubtask("parse_resume", TaskType.EXTRACTION, "Parse resume", [], [], TaskPriority.CRITICAL, 3.0, []),
            MockSubtask("analyze_match", TaskType.COMPARISON, "Analyze match", [], [], TaskPriority.HIGH, 2.5, ["extract_req", "parse_resume"]),
            MockSubtask("validate_analysis", TaskType.VALIDATION, "Validate analysis", [], [], TaskPriority.HIGH, 1.5, ["analyze_match"]),
            MockSubtask("generate_improvements", TaskType.SYNTHESIS, "Generate improvements", [], [], TaskPriority.MEDIUM, 4.0, ["validate_analysis"])
        ]
        
        # Build dependency graph
        dependency_graph = {}
        for task in subtasks:
            dependency_graph[task.task_id] = task.dependencies
        
        # Validate dependency graph structure
        assert dependency_graph["extract_req"] == []
        assert dependency_graph["parse_resume"] == []
        assert set(dependency_graph["analyze_match"]) == {"extract_req", "parse_resume"}
        assert dependency_graph["validate_analysis"] == ["analyze_match"]
        assert dependency_graph["generate_improvements"] == ["validate_analysis"]
        
        # Validate no circular dependencies
        def has_cycle(node_id: str, visited: Set[str], rec_stack: Set[str]) -> bool:
            visited.add(node_id)
            rec_stack.add(node_id)
            
            for dep in dependency_graph[node_id]:
                if dep not in visited:
                    if has_cycle(dep, visited, rec_stack):
                        return True
                elif dep in rec_stack:
                    return True
            
            rec_stack.remove(node_id)
            return False
        
        visited = set()
        rec_stack = set()
        has_circular = any(has_cycle(task_id, visited, rec_stack) for task_id in dependency_graph)
        assert not has_circular, "Circular dependencies detected"
    
    def test_critical_path_identification(self):
        """Test identification of critical path in task dependencies."""
        subtasks_with_durations = [
            {"task_id": "extract_req", "duration": 2.0, "dependencies": []},
            {"task_id": "parse_resume", "duration": 3.0, "dependencies": []},
            {"task_id": "analyze_match", "duration": 2.5, "dependencies": ["extract_req", "parse_resume"]},
            {"task_id": "optional_enrichment", "duration": 2.0, "dependencies": ["parse_resume"]},
            {"task_id": "generate_improvements", "duration": 4.0, "dependencies": ["analyze_match"]}
        ]
        
        # Calculate critical path
        def calculate_earliest_start(task_id: str, tasks: List[Dict]) -> float:
            task = next(t for t in tasks if t["task_id"] == task_id)
            
            if not task["dependencies"]:
                return 0.0
            
            max_dep_finish = 0.0
            for dep_id in task["dependencies"]:
                dep_task = next(t for t in tasks if t["task_id"] == dep_id)
                dep_finish = calculate_earliest_start(dep_id, tasks) + dep_task["duration"]
                max_dep_finish = max(max_dep_finish, dep_finish)
            
            return max_dep_finish
        
        def calculate_latest_start(task_id: str, tasks: List[Dict], project_finish: float) -> float:
            task = next(t for t in tasks if t["task_id"] == task_id)
            
            # Find tasks that depend on this one
            dependents = [t for t in tasks if task_id in t["dependencies"]]
            
            if not dependents:
                return project_finish - task["duration"]
            
            min_dep_start = float('inf')
            for dependent in dependents:
                dep_latest = calculate_latest_start(dependent["task_id"], tasks, project_finish)
                min_dep_start = min(min_dep_start, dep_latest)
            
            return min_dep_start - task["duration"]
        
        # Calculate earliest and latest starts for all tasks
        earliest_starts = {}
        latest_starts = {}
        
        for task in subtasks_with_durations:
            task_id = task["task_id"]
            earliest_starts[task_id] = calculate_earliest_start(task_id, subtasks_with_durations)
        
        project_finish = max(
            earliest_starts[task["task_id"]] + task["duration"]
            for task in subtasks_with_durations
        )
        
        for task in subtasks_with_durations:
            task_id = task["task_id"]
            latest_starts[task_id] = calculate_latest_start(task_id, subtasks_with_durations, project_finish)
        
        # Identify critical path (tasks with zero slack)
        critical_tasks = []
        for task in subtasks_with_durations:
            task_id = task["task_id"]
            slack = latest_starts[task_id] - earliest_starts[task_id]
            if abs(slack) < 0.001:  # Essentially zero
                critical_tasks.append(task_id)
        
        # Sort critical tasks by earliest start time
        critical_path = sorted(critical_tasks, key=lambda tid: earliest_starts[tid])
        
        # Validate critical path
        expected_critical = ["parse_resume", "analyze_match", "generate_improvements"]
        assert critical_path == expected_critical
        
        # Validate optional task is not on critical path
        assert "optional_enrichment" not in critical_path
        
        # Validate project duration
        expected_duration = 3.0 + 2.5 + 4.0  # Critical path sum (parse_resume + analyze_match + generate_improvements)
        assert abs(project_finish - expected_duration) < 0.001
    
    def test_parallel_task_identification(self):
        """Test identification of tasks that can execute in parallel."""
        subtasks = [
            MockSubtask("extract_req", TaskType.EXTRACTION, "Extract requirements", [], [], TaskPriority.CRITICAL, 2.0, []),
            MockSubtask("parse_resume", TaskType.EXTRACTION, "Parse resume", [], [], TaskPriority.CRITICAL, 3.0, []),
            MockSubtask("analyze_skills", TaskType.COMPARISON, "Analyze skills", [], [], TaskPriority.HIGH, 2.0, ["extract_req", "parse_resume"]),
            MockSubtask("analyze_experience", TaskType.COMPARISON, "Analyze experience", [], [], TaskPriority.HIGH, 2.5, ["extract_req", "parse_resume"]),
            MockSubtask("synthesize_results", TaskType.SYNTHESIS, "Synthesize results", [], [], TaskPriority.MEDIUM, 3.0, ["analyze_skills", "analyze_experience"])
        ]
        
        # Group tasks by dependency level for parallel execution
        dependency_levels = {}
        
        def get_dependency_level(task_id: str, tasks: List[MockSubtask], memo: Dict[str, int]) -> int:
            if task_id in memo:
                return memo[task_id]
            
            task = next(t for t in tasks if t.task_id == task_id)
            
            if not task.dependencies:
                level = 0
            else:
                max_dep_level = max(get_dependency_level(dep, tasks, memo) for dep in task.dependencies)
                level = max_dep_level + 1
            
            memo[task_id] = level
            return level
        
        # Calculate levels for all tasks
        memo = {}
        for task in subtasks:
            level = get_dependency_level(task.task_id, subtasks, memo)
            if level not in dependency_levels:
                dependency_levels[level] = []
            dependency_levels[level].append(task.task_id)
        
        # Validate parallel execution groups
        assert len(dependency_levels) == 3  # Three levels of dependencies
        
        # Level 0: Tasks with no dependencies (can run in parallel)
        level_0_tasks = dependency_levels[0]
        assert set(level_0_tasks) == {"extract_req", "parse_resume"}
        
        # Level 1: Tasks that depend on level 0
        level_1_tasks = dependency_levels[1]
        assert set(level_1_tasks) == {"analyze_skills", "analyze_experience"}
        
        # Level 2: Final task
        level_2_tasks = dependency_levels[2]
        assert level_2_tasks == ["synthesize_results"]
        
        # Calculate parallel execution time
        sequential_time = sum(task.estimated_duration for task in subtasks)
        parallel_time = (
            max(2.0, 3.0) +  # Level 0 (parallel)
            max(2.0, 2.5) +  # Level 1 (parallel)
            3.0              # Level 2 (sequential)
        )
        
        time_savings = sequential_time - parallel_time
        assert time_savings > 0, "Parallel execution should save time"
        assert time_savings == 4.0, "Expected 4.0 time units saved"

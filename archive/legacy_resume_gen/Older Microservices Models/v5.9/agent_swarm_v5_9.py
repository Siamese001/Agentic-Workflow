# File: agent_swarm.py
# Version: 5.9 (Batch Harness)
# Zero-Loss Consolidation - The Crew
# Implements: Conductor, MoE Routers, Reflection Loops, ReAct Tool-Using, Adversarial MoE Drafting
# REFACTORED: Removed all hard-coded plans, agent complexity maps, and redundant configs.
# All configuration is now read from the central CONFIG object.

# ============================================================================
# EXTERNAL IMPORTS
# ============================================================================
import copy
import hashlib
import json
import logging
import os
import random
import re
import time
from collections import defaultdict
from enum import Enum
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

# Optional imports
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None

# Import from core
from core_v5_9 import (
    # Models
    HopExecutionError, MechanicalFailureError, SemanticFailureError, FactualFailureException,
    ValidationSeverity, ValidationResult, ReasoningConfig, ReasoningStrategy,
    ThematicAnalysis, RAG_Blackboard, RAGMission, RAGPhase, StrategyBrief, StrategyBlackboard,
    # v5.8 Models
    ReflectionIteration, ReflectionResult, ReflectionStatus,
    ToolCall, ToolType, ReActTrace,
    MoEExpertResult, MoEDecision, ConductorBranch, ConductorDecision,
    WorkflowBlackboard, WorkflowPlan, WorkflowStep,
    # Config
    CONFIG, DEFAULT_GENERATION_TEMPERATURE,
    # Utils
    text_utils, fence_data
)

# Import from validation_stack
from validation_stack_v5_9 import ValidationEngine, ValidationContext, calculate_signal_score

logger = logging.getLogger(__name__)

# ============================================================================
# V5.8.1: WORKFLOW STEP ENUM (Hardening Fix)
# ============================================================================

class WorkflowSteps(Enum):
    """Centralizes workflow step names to prevent de-sync."""
    STRATEGY = "run_strategy_stack"
    RAG = "run_rag_stack"
    PROMPT = "run_prompt_stack"
    BULLET = "run_bullet_stack"
    DRAFTING = "run_drafting_stack"
    QA = "run_qa_stack"
    RECOVERY = "retry_failed"

# ============================================================================
# AGENT COMPLEXITY MAP
# ============================================================================

# REFACTORED: The hard-coded AGENT_COMPLEXITY map has been exorcised.
# Agent complexity is now loaded from CONFIG.agent_definitions.swarm_agents


# ============================================================================
# PART 1: CONDUCTOR STACK (Tree of Thought)
# ============================================================================

class ConductorAgent:
    """
    v5.8 Conductor: Spawns multiple parallel WorkflowPlannerAgents,
    each exploring a different strategy (GTM-focused, Tech-focused, Balanced).
    REFACTORED: Reads strategies directly from CONFIG.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or CONFIG.conductor_config
        self.logger = logging.getLogger(__name__)
        self.num_branches = self.config.num_branches
        
        # REFACTORED: Load strategies from CONFIG
        if not hasattr(self.config, 'strategies') or not self.config.strategies:
            raise ValueError("Conductor strategies are missing from master_config_v5_9.json.")
        self.strategies = self.config.strategies
    
    def execute(self, blackboard: WorkflowBlackboard) -> ConductorDecision:
        """Execute Tree of Thought exploration."""
        self.logger.info(f"🌲 Conductor spawning {self.num_branches} parallel branches...")
        
        # REFACTORED: Use strategies from CONFIG
        branches = []
        for i, strategy in enumerate(self.strategies[:self.num_branches]):
            branch = self._execute_branch(blackboard, strategy, i)
            branches.append(branch)
        
        # Vote on best branch
        winner = self._vote_on_branches(branches)
        
        return ConductorDecision(
            winning_branch=winner,
            all_branches=branches,
            vote_results={b.branch_id: b.score for b in branches},
            selection_method=self.config.voting_method,
            metadata={"num_branches": len(branches)}
        )
    
    def _execute_branch(self, blackboard: WorkflowBlackboard, strategy: Any, index: int) -> ConductorBranch:
        """
        Execute a single branch.
        Strategy is a config object, not a dict.
        """
        branch_id = strategy.id
        strategy_desc = strategy.description
        self.logger.info(f"  Branch {index+1}/{self.num_branches}: {strategy_desc}")
        
        branch = ConductorBranch(
            branch_id=branch_id,
            strategy_description=strategy_desc,
            planner_id=f"planner_{branch_id}",
            execution_plan=self._create_plan_for_strategy(strategy),
            status="PENDING"
        )
        
        # Stub: Execute plan
        start_time = time.time()
        try:
            # In production, would run full workflow with this strategy
            branch.result = {"stub": "Branch execution result"}
            branch.score = random.uniform(0.7, 0.95)  # Stub scoring
            branch.status = "COMPLETED"
        except Exception as e:
            self.logger.error(f"Branch {branch_id} failed: {e}")
            branch.status = "FAILED"
            branch.score = 0.0
        
        branch.execution_time = time.time() - start_time
        return branch
    
    def _create_plan_for_strategy(self, strategy: Any) -> List[str]:
        """Create execution plan based on strategy."""
        # Stub: In a real implementation, this would use the planner
        # to dynamically create a plan based on the strategy emphasis.
        base_plan = ["Create_Strategy", "Create_RAG_Context", "Create_Draft", "Validate"]
        
        if strategy.emphasis == "partnerships_go_to_market":
            base_plan.insert(1, "Emphasize_Partnership_Keywords")
        elif strategy.emphasis == "technical_depth_innovation":
            base_plan.insert(1, "Emphasize_Technical_Depth")
        
        return base_plan
    
    def _vote_on_branches(self, branches: List[ConductorBranch]) -> ConductorBranch:
        """Select the winning branch based on scores."""
        if not branches:
            raise ValueError("No branches to vote on")
        
        winner = max(branches, key=lambda b: b.score)
        self.logger.info(f"🏆 Winner: {winner.strategy_description} (score: {winner.score:.3f})")
        return winner

# ============================================================================
# PART 2: WORKFLOW PLANNING (v5.8)
# ============================================================================

class WorkflowPlannerAgent:
    """
    Creates initial workflow execution plan.
    REFACTORED: Reads the default plan from CONFIG.
    """
    
    def __init__(self, strategy_type: str = "balanced"):
        self.strategy_type = strategy_type
        self.logger = logging.getLogger(__name__)
        self.default_plan_config = CONFIG.planner_config.default_workflow_plan
        
        if not self.default_plan_config:
            raise ValueError("planner_config.default_workflow_plan is missing from master_config_v5_9.json.")
    
    def create_initial_plan(self, blackboard: WorkflowBlackboard) -> WorkflowPlan:
        """Create initial workflow plan."""
        self.logger.info(f"📋 Creating workflow plan (strategy: {self.strategy_type})...")
        
        # REFACTORED: Build steps from CONFIG
        steps = []
        for step_config in self.default_plan_config:
            steps.append(
                WorkflowStep(
                    step_id=step_config.step_id,
                    agent=step_config.agent,
                    description=step_config.description,
                    dependencies=step_config.dependencies
                )
            )
        
        plan = WorkflowPlan(
            plan_id=f"plan_{datetime.now().timestamp()}",
            steps=steps,
            strategy_type=self.strategy_type
        )
        
        return plan

class WorkflowCritiqueAgent:
    """Critiques workflow execution state."""
    
    def critique(self, state: Dict, blackboard: WorkflowBlackboard) -> str:
        """Critique current state."""
        if state.get("last_step_failed"):
            return "FAIL"
        return "OK"

class WorkflowRePlannerAgent:
    """Creates recovery plans when needed."""
    
    def replan(self, critique: str, blackboard: WorkflowBlackboard) -> WorkflowPlan:
        """Create recovery plan."""
        # Stub: Create recovery plan
        return WorkflowPlan(
            plan_id=f"replan_{datetime.now().timestamp()}",
            steps=[WorkflowStep("recovery_step", WorkflowSteps.RECOVERY.value, "Retry failed step")],
            strategy_type="recovery"
        )

# ============================================================================
# PART 3: STRATEGY STACK AGENTS
# ============================================================================

class JDParserAgent:
    """Parses job description."""
    def execute(self, raw_jd: str) -> Dict[str, Any]:
        return {"parsed_jd": raw_jd[:100], "themes": ["AI", "Leadership"]}

class ThemeIdentifierAgent:
    """Identifies themes from JD."""
    def execute(self, parsed_jd: Dict) -> List[str]:
        return ["Strategic Leadership", "AI Innovation", "Go-to-Market"]

class ThemeRankerAgent:
    """Ranks themes by importance."""
    def execute(self, themes: List[str]) -> List[str]:
        return themes  # Stub

class GapAnalysisAgent:
    """Analyzes gaps between resume and JD."""
    def execute(self, themes: List[str], master_resume: Dict) -> Dict[str, Any]:
        return {"gaps": ["Partnership Development", "M&A Experience"]}

class DifferentiatorAgent:
    """Identifies key differentiators."""
    def execute(self, gaps: Dict, master_resume: Dict) -> List[str]:
        return ["20+ years experience", "Fortune 500 track record"]

class StrategyBriefAssemblerAgent:
    """Assembles strategy brief."""
    def execute(self, components: Dict) -> StrategyBrief:
        return StrategyBrief(
            themes=components.get("themes", []),
            differentiators=components.get("differentiators", []),
            gaps=components.get("gaps", {}).get("gaps", []),
            recommendations=[],
            tone="professional",
            emphasis_areas=[]
        )

class StrategyCritiqueAgent:
    """Critiques strategy (reflection)."""
    def execute(self, brief: StrategyBrief) -> ReflectionResult:
        # Stub: Reflection loop
        return ReflectionResult(
            final_output=brief,
            iterations=[],
            status=ReflectionStatus.CONVERGED,
            total_iterations=1,
            quality_improvement=0.05,
            metadata={"convergence_score": 0.95}
        )

class StrategyValidatorAgent:
    """Validates strategy brief."""
    def validate(self, brief: StrategyBrief) -> Tuple[bool, str]:
        # Stub validation
        return (True, "Strategy validated")

# ============================================================================
# PART 4: RAG STACK AGENTS
# ============================================================================

class RAG_QueryGeneratorAgent:
    """Generates RAG queries."""
    def execute(self, mission: RAGMission, blackboard: RAG_Blackboard) -> List[str]:
        return [
            "Strategic partnerships experience",
            "M&A and corporate development",
            "Go-to-market strategy"
        ]

class RAG_SearchAgent:
    """Executes RAG searches (ReAct + MoE)."""
    def execute(self, queries: List[str], blackboard: RAG_Blackboard) -> Dict[str, Any]:
        return {"results": ["Document 1", "Document 2", "Document 3"]}

class RAG_ChunkingAgent:
    """Chunks retrieved content."""
    def execute(self, results: Dict, blackboard: RAG_Blackboard) -> List[str]:
        return ["Chunk 1", "Chunk 2", "Chunk 3"]

class RAG_RankingAgent:
    """Ranks chunks by relevance."""
    def execute(self, chunks: List[str], blackboard: RAG_Blackboard) -> List[str]:
        return chunks  # Stub

class RAG_FilterAgent:
    """
    Filters low-quality chunks.
    REFACTORED: Reads top_k from config, with a fallback.
    """
    def execute(self, ranked_chunks: List[str], blackboard: RAG_Blackboard) -> List[str]:
        # REFACTORED: Read from config.
        # NOTE: 'top_k_filter' should be added to new_agent_configs.rag_filter in config.
        top_k = getattr(CONFIG.new_agent_configs.rag_filter, 'top_k_filter', 2)
        return ranked_chunks[:top_k]  # Stub: Keep top k

class RAG_CrossReferenceAgent:
    """Cross-references information."""
    def execute(self, filtered_chunks: List[str], blackboard: RAG_Blackboard):
        blackboard.cross_refs = {"verified": True}

class RAG_DraftingAgent:
    """Drafts RAG output."""
    def execute(self, chunks: List[str], blackboard: RAG_Blackboard) -> str:
        return "RAG-enriched context: " + ", ".join(chunks)

class RAG_CritiqueAgent:
    """Critiques RAG output (reflection)."""
    def execute(self, draft: str, blackboard: RAG_Blackboard) -> ReflectionResult:
        return ReflectionResult(
            final_output=draft,
            iterations=[],
            status=ReflectionStatus.CONVERGED,
            total_iterations=1,
            quality_improvement=0.03,
            metadata={"convergence_score": 0.90}
        )

# ============================================================================
# PART 5: ADVERSARIAL MOE DRAFTING STACK
# ============================================================================

class AdversarialDraftingRouter:
    """
    v5.8 MoE router for adversarial drafting.
    Spawns multiple drafters (Gemini, Claude, Muse) and synthesizes results.
    REFACTORED: Reads enabled drafters from CONFIG.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.AdversarialDraftingRouter")
        
        # V5.8.1 Fix: Load drafters from CONFIG
        self.drafters = {}
        drafter_factory = {
            "Gemini_Drafter": lambda c: Gemini_Drafter(c),
            "Claude_Drafter": lambda c: Claude_Drafter(c),
            "Muse_Drafter": lambda c: Muse_Drafter(c)
        }
        
        drafter_configs = CONFIG.adversarial_moe_drafting.drafters
        for drafter_config in drafter_configs:
            if drafter_config.enabled:
                drafter_name = drafter_config.name
                drafter_class = drafter_factory.get(drafter_name)
                if drafter_class:
                    self.logger.info(f"Initializing drafter: {drafter_name}")
                    self.drafters[drafter_name] = drafter_class(drafter_config)
                else:
                    self.logger.warning(f"Unknown drafter name in config: {drafter_name}")
    
    def execute(self, prompt: str, bullets: List[str]) -> str:
        self.logger.info(f"⚔️  Adversarial MoE drafting with {len(self.drafters)} enabled drafters...")
        
        # Send to all drafters in parallel (stub: sequential)
        drafts = {}
        for name, drafter in self.drafters.items():
            try:
                draft = drafter.draft(prompt, bullets)
                drafts[name] = draft
            except Exception as e:
                self.logger.error(f"Drafter {name} failed: {e}")
                drafts[name] = f"DRAFTER {name} FAILED: {e}"
        
        # Synthesize
        synthesizer = SynthesisCritiqueAgent()
        return synthesizer.execute(drafts)

class Gemini_Drafter:
    """Gemini drafter."""
    def __init__(self, config: Any): # Config is a namespace object
        self.config = config

    def draft(self, prompt: str, bullets: List[str]) -> str:
        return f"GEMINI DRAFT (model: {self.config.model}): {prompt[:50]}... [bullets: {len(bullets)}]"

class Claude_Drafter:
    """Claude drafter."""
    def __init__(self, config: Any): # Config is a namespace object
        self.config = config
        
    def draft(self, prompt: str, bullets: List[str]) -> str:
        return f"CLAUDE DRAFT (model: {self.config.model}): {prompt[:50]}... [bullets: {len(bullets)}]"

class Muse_Drafter:
    """Muse drafter (stub)."""
    def __init__(self, config: Any): # Config is a namespace object
        self.config = config
        
    def draft(self, prompt: str, bullets: List[str]) -> str:
        return f"MUSE DRAFT (model: {self.config.model}): {prompt[:50]}... [bullets: {len(bullets)}]"

class SynthesisCritiqueAgent:
    """Synthesizes multiple drafts into final output (reflection)."""
    def execute(self, drafts: Dict[str, str]) -> str:
        # Stub: Simple concatenation
        return " | ".join(drafts.values())

# ============================================================================
# PART 6: COST TRACKING
# ============================================================================

class CostEstimatorAgent:
    """Estimates workflow costs."""
    def estimate(self, workflow_plan: WorkflowPlan) -> float:
        return 0.50  # Stub

class CostTrackerAgent:
    """Tracks actual costs."""
    def __init__(self):
        self.costs = {}
    
    def log_cost(self, agent: str, cost: float):
        self.costs[agent] = cost
    
    def log_final_cost(self, workflow_id: str, costs: Dict):
        logger.info(f"Final costs for {workflow_id}: ${sum(costs.values()):.2f}")

# ============================================================================
# PART 7: CONFIGURATION
# ============================================================================

@dataclass
class CrewConfiguration:
    """
    Crew configuration.
    REFACTORED: Defaults are now loaded from CONFIG by main.py
    """
    enable_conductor: bool
    enable_reflection: bool
    enable_react: bool
    enable_moe: bool
    max_retries: int
    timeout_seconds: int
    # These are illustrative; main.py will populate them from CONFIG
    max_complexity: int = 100
    parallel_execution: bool = False
    validation_threshold: float = 0.8
    enable_caching: bool = True
    debug_mode: bool = False


@dataclass
class CrewContext:
    """Context for crew execution."""
    job_description: str
    company_name: str
    job_title: str
    master_resume: Dict[str, Any]
    workflow_id: str

# ============================================================================
# PART 8: GOVERNOR (Main Orchestrator)
# ============================================================================

class Governor:
    """
    v5.8 Governor: Main orchestration agent that delegates to specialists.
    REFACTORED: Reads max_replan_loops from CONFIG.
    """
    
    def __init__(self, config: CrewConfiguration):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize agents
        self.conductor = ConductorAgent() if config.enable_conductor else None
        self.planner = WorkflowPlannerAgent()
        self.critique = WorkflowCritiqueAgent()
        self.replanner = WorkflowRePlannerAgent()
        self.cost_estimator = CostEstimatorAgent()
        self.cost_tracker = CostTrackerAgent()
        
        # REFACTORED: Get max loops from config (via CrewConfiguration)
        self.max_replan_loops = CONFIG.planner_config.max_replan_loops
        
        # Map agent names to execution functions
        self.execution_map = {
            WorkflowSteps.STRATEGY.value: self._run_strategy_stack,
            WorkflowSteps.RAG.value: self._run_rag_stack,
            WorkflowSteps.PROMPT.value: self._run_prompt_stack,
            WorkflowSteps.BULLET.value: self._run_bullet_stack,
            WorkflowSteps.DRAFTING.value: self._run_drafting_stack,
            WorkflowSteps.QA.value: self._run_qa_stack,
        }
    
    def _run_strategy_stack(self, blackboard: WorkflowBlackboard):
        """Execute Strategy Stack."""
        logger.info("🎯 Running Strategy Stack...")
        
        strategy_board = blackboard.strategy_board
        if not strategy_board:
            raise ValueError("StrategyBlackboard not initialized.")
        
        # Execute stack
        parser = JDParserAgent()
        theme_id = ThemeIdentifierAgent()
        theme_rank = ThemeRankerAgent()
        gap = GapAnalysisAgent()
        diff = DifferentiatorAgent()
        assembler = StrategyBriefAssemblerAgent()
        critique = StrategyCritiqueAgent()
        validator = StrategyValidatorAgent()
        
        parsed = parser.execute(strategy_board.raw_jd)
        themes = theme_id.execute(parsed)
        ranked_themes = theme_rank.execute(themes)
        gaps = gap.execute(ranked_themes, blackboard.master_resume)
        differentiators = diff.execute(gaps, blackboard.master_resume)
        
        draft_brief = assembler.execute({
            "themes": ranked_themes,
            "gaps": gaps,
            "differentiators": differentiators
        })
        
        # Reflection loop
        if self.config.enable_reflection:
            reflection = critique.execute(draft_brief)
            draft_brief = reflection.final_output
        
        # Validate
        is_valid, msg = validator.validate(draft_brief)
        if not is_valid:
            raise SemanticFailureError("Strategy validation failed")
        
        strategy_board.final_brief = draft_brief
        blackboard.artifacts["strategy_brief"] = asdict(draft_brief)
        return draft_brief
    
    def _run_rag_stack(self, blackboard: WorkflowBlackboard):
        """Execute RAG Stack."""
        logger.info("🔍 Running RAG Stack...")
        
        rag_board = RAG_Blackboard(
            mission=RAGMission(
                objective="Gather relevant context for resume",
                constraints=[],
                success_criteria=[]
            )
        )
        
        # Execute stack
        query_gen = RAG_QueryGeneratorAgent()
        search = RAG_SearchAgent()
        chunk = RAG_ChunkingAgent()
        rank = RAG_RankingAgent()
        filter_agent = RAG_FilterAgent()
        cross_ref = RAG_CrossReferenceAgent()
        draft = RAG_DraftingAgent()
        critique = RAG_CritiqueAgent()
        
        queries = query_gen.execute(rag_board.mission, rag_board)
        raw_results = search.execute(queries, rag_board)
        chunks = chunk.execute(raw_results, rag_board)
        ranked = rank.execute(chunks, rag_board)
        filtered = filter_agent.execute(ranked, blackboard=rag_board)
        cross_ref.execute(filtered, rag_board)
        rag_draft = draft.execute(filtered, rag_board)
        
        # Reflection loop
        if self.config.enable_reflection:
            reflection = critique.execute(rag_draft, rag_board)
            rag_board.final_output = reflection.final_output
        else:
            rag_board.final_output = rag_draft
        
        blackboard.rag_board = rag_board
        blackboard.artifacts["rag_output"] = rag_board.final_output
        return rag_board.final_output
    
    def _run_prompt_stack(self, blackboard: WorkflowBlackboard):
        """Execute Prompt Stack."""
        logger.info("💡 Running Prompt Stack...")
        # Stub
        blackboard.artifacts["final_prompt"] = "PROMPT_OUTPUT"
        return "PROMPT_OUTPUT"
    
    def _run_bullet_stack(self, blackboard: WorkflowBlackboard):
        """Execute Bullet Swarm."""
        logger.info("✒️  Running Bullet Swarm...")
        # Stub
        bullets = ["Bullet 1", "Bullet 2", "Bullet 3"]
        blackboard.artifacts["generated_bullets"] = bullets
        return bullets
    
    def _run_drafting_stack(self, blackboard: WorkflowBlackboard):
        """Execute Adversarial MoE Drafting."""
        logger.info("⚔️  Running Adversarial Drafting...")
        router = AdversarialDraftingRouter()
        
        prompt = blackboard.artifacts.get("final_prompt", "DEFAULT PROMPT")
        bullets = blackboard.artifacts.get("generated_bullets", [])
        
        draft = router.execute(prompt, bullets)
        blackboard.artifacts["final_draft"] = draft
        return draft
    
    def _run_qa_stack(self, blackboard: WorkflowBlackboard):
        """Execute MoE QA Stack."""
        logger.info("🛡️  Running MoE QA Stack...")
        # Stub: Use validation engine
        # In a real run, we'd build the full ValidationContext
        validation_results = {"passed": True, "stub": True}
        blackboard.artifacts["validation_results"] = validation_results
        return validation_results
    
    def process_request(self, context: CrewContext) -> Dict[str, Any]:
        """
        V5.8.1 Main orchestration with optional Conductor.
        """
        self.logger.info(f"🚀 Governor processing: {context.company_name} - {context.job_title}")
        
        results = {
            'artifacts': {},
            'validation': {},
            'metadata': {'workflow_id': context.workflow_id}
        }
        
        plan: Optional[WorkflowPlan] = None
        
        # Initialize Blackboard
        blackboard = WorkflowBlackboard(
            workflow_id=context.workflow_id,
            master_resume=context.master_resume,
            job_input={"raw_jd": context.job_description, "company": context.company_name},
            strategy_board=StrategyBlackboard(raw_jd=context.job_description)
        )
        
        # V5.8.1 Fix: Use Conductor to set the plan, or fall back to default planner
        if self.config.enable_conductor and self.conductor:
            self.logger.info("🌲 Using Conductor for Tree-of-Thought exploration...")
            conductor_decision = self.conductor.execute(blackboard)
            results['conductor_decision'] = {
                'winning_branch': asdict(conductor_decision.winning_branch),
                'all_branches': [asdict(b) for b in conductor_decision.all_branches],
                'scores': conductor_decision.vote_results
            }
            
            # Use winning branch's strategy to create the plan
            winning_strategy = conductor_decision.winning_branch.strategy_description
            self.logger.info(f"Conductor selected winning strategy: {winning_strategy}")
            branch_planner = WorkflowPlannerAgent(strategy_type=winning_strategy)
            blackboard.plan = branch_planner.create_initial_plan(blackboard)
            
        else:
            # Standard planning (uses default "balanced" planner)
            self.logger.info("Using default 'balanced' strategy...")
            blackboard.plan = self.planner.create_initial_plan(blackboard)

        
        # Execute plan
        loop_count = 0
        # REFACTORED: Use max_replan_loops from CONFIG
        
        try:
            while blackboard.plan.steps and loop_count < self.max_replan_loops:
                loop_count += 1
                current_step = blackboard.plan.steps.pop(0)
                agent_name = current_step.agent
                
                # EXECUTE
                start_time = time.time()
                try:
                    self.logger.info(f"Loop {loop_count}: Executing {agent_name}")
                    executable = self.execution_map.get(agent_name)
                    if not executable:
                        raise NotImplementedError(f"No executable for: {agent_name}")
                    
                    current_step.result = executable(blackboard)
                    current_step.status = "COMPLETED"
                    
                except (MechanicalFailureError, SemanticFailureError, FactualFailureException) as e:
                    current_step.status = "FAILED"
                    self.logger.warning(f"Agent VETO: {agent_name} - {e}")
                
                except Exception as e:
                    current_step.status = "FAILED"
                    self.logger.error(f"Agent FAILED: {agent_name}", exc_info=True)
                
                # OBSERVE & CRITIQUE
                state = {"last_step_failed": current_step.status == "FAILED"}
                critique_result = self.critique.critique(state, blackboard)
                
                # RE-PLAN if needed
                if critique_result == "FAIL":
                    self.logger.warning("Critique failed, re-planning...")
                    blackboard.plan = self.replanner.replan(critique_result, blackboard)
            
            if loop_count >= self.max_replan_loops:
                raise Exception(f"Max replan loops ({self.max_replan_loops}) reached")
            
            # Finalize
            results['validation'] = {'passed': True, 'status': 'SUCCESS'}
            results['artifacts'] = blackboard.artifacts
            results['metadata']['timestamp'] = datetime.now().isoformat()
            
            return results
            
        except Exception as e:
            self.logger.error(f"Governor failed: {e}", exc_info=True)
            results['validation'] = {'passed': False, 'error': str(e)}
            return results
        
        finally:
            self.cost_tracker.log_final_cost(context.workflow_id, {})

class CrewOrchestrator:
    """High-level orchestrator."""
    
    def __init__(self, config: Optional[CrewConfiguration] = None):
        # If no config is passed, build one from the defaults in master_config.json
        if config:
            self.config = config
        else:
            defaults = CONFIG.crew_config_defaults
            self.config = CrewConfiguration(
                enable_conductor=defaults.enable_conductor,
                enable_reflection=defaults.enable_reflection,
                enable_react=defaults.enable_react,
                enable_moe=defaults.enable_moe,
                max_retries=CONFIG.llm_config.defaults.max_retries,
                timeout_seconds=300, # This was hardcoded before, fine to leave
                max_complexity=defaults.max_complexity,
                parallel_execution=defaults.parallel_execution,
                validation_threshold=defaults.validation_threshold,
                enable_caching=defaults.enable_caching,
                debug_mode=defaults.debug_mode
            )
            
        self.governor = Governor(self.config)
        self.logger = logging.getLogger(__name__)
    
    def process_job_application(self, job_description: str, company_name: str,
                               job_title: str, master_resume: Dict[str, Any],
                               workflow_id: str) -> Dict[str, Any]:
        """Process complete job application."""
        self.logger.info(f"📋 Orchestrating: {company_name} - {job_title}")
        
        context = CrewContext(
            job_description=job_description,
            company_name=company_name,
            job_title=job_title,
            master_resume=master_resume,
            workflow_id=workflow_id
        )
        
        try:
            results = self.governor.process_request(context)
            results['workflow_results'] = {
                'status': 'COMPLETED' if results.get('validation', {}).get('passed') else 'FAILED'
            }
            return results
        
        except Exception as e:
            self.logger.error(f"Orchestration failed: {e}")
            return {
                'workflow_results': {'status': 'FAILED', 'error': str(e)}
            }

# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    'CrewOrchestrator', 'CrewConfiguration', 'Governor', 'ConductorAgent',
    'CrewContext', 'WorkflowSteps'
]
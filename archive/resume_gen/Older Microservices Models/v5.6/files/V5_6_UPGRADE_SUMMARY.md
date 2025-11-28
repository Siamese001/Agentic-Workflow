# Resume Generation System - v5.6 Upgrade Summary

## Architecture: Agentic Executor with Planner-Critic-RePlanner Loop

### Overview
Version 5.6 represents a fundamental architectural shift from hard-coded workflows to dynamic agentic orchestration. The Governor now operates as a Planner-Executor-Critique-RePlanner loop, enabling adaptive workflow execution.

---

## Key Changes

### 1. **NEW: Planner Stack (4 Agents)**
   - **WorkflowPlannerAgent**: Generates initial execution plan
   - **WorkflowStateMonitorAgent**: Observes blackboard state
   - **WorkflowCritiqueAgent**: Evaluates execution success/failure
   - **WorkflowRePlannerAgent**: Generates new plan on failure

### 2. **NEW: Strategy Stack (6 Agents)**
   Replaces monolithic `ChiefStrategistAgent`:
   - **JDParserAgent**: Parses raw JD into structured data
   - **ThemeIdentifierAgent**: Brainstorms themes from JD
   - **ThemeRankerAgent**: Ranks themes against master resume
   - **GapAnalysisAgent**: Identifies missing skills
   - **DifferentiatorAgent**: Finds unique candidate strengths
   - **StrategyBriefAssemblerAgent**: Assembles final StrategyBrief

### 3. **NEW: RAG Pipeline Stack (8 Agents)**
   Fine-grained RAG decomposition:
   - **RAG_QueryGeneratorAgent**: Generates search queries
   - **RAG_SearchAgent**: Executes searches
   - **RAG_ChunkingAgent**: Breaks documents into chunks
   - **RAG_RankingAgent**: Ranks chunks by relevance
   - **RAG_FilterAgent**: Selects top-k chunks
   - **RAG_CrossReferenceAgent**: Validates against master resume
   - **RAG_DraftingAgent**: Writes ThematicAnalysis
   - **RAG_CritiqueAgent**: Critiques draft (self-correction loop)

### 4. **NEW: Prompt Engineering Stack (7 Agents)**
   Systematic prompt construction:
   - **ExampleQueryGeneratorAgent**: Generates few-shot queries
   - **ExampleSearchAgent**: Searches for examples
   - **ExampleRankerAgent**: Ranks examples
   - **RAGContextAgent**: Fetches RAG context
   - **ConstraintInjectorAgent**: Injects constraints
   - **MasterDataContextAgent**: Fetches ground truth
   - **PromptFormatterAgent**: Assembles final prompt

### 5. **NEW: Bullet Swarm (7 Agents)**
   Intelligent bullet generation:
   - **ProvenanceRouterAgent**: Creates generation plan
   - **Verbatim_Copier**: Selects verbatim bullets
   - **Custom_Synthetic_Drafter**: Customizes bullets
   - **SyntheticBulletBrainstormAgent**: Brainstorms new ideas
   - **SyntheticBulletDrafterAgent**: Drafts synthetic bullets
   - **SyntheticBulletValidatorAgent**: Validates plausibility
   - **BulletAssemblerAgent**: Assembles all sources

### 6. **NEW: Atomic QA Swarm (9 New Validators)**
   Replaces `PreFlightValidator` with atomic checks:
   - **SectionPresenceValidatorAgent**: H1_SECTION_PRESENCE
   - **WordCountValidatorAgent**: Per-section word counts
   - **SentenceCountValidatorAgent**: Sentence constraints
   - **StructureValidatorAgent**: H3_COVER_LETTER_STRUCTURE
   - **SimilarityValidatorAgent**: H5_CROSS_SECTION_SIMILARITY
   - **JDSkillsValidatorAgent**: S1_JD_SKILLS_OVERLAP
   - **SignalScoreValidatorAgent**: S2_SIGNAL_SCORE

---

## Data Model Changes (core.py)

### NEW Models:
```python
@dataclass
class StrategyBlackboard:
    """Holds Strategy Stack intermediate state"""
    raw_jd: str
    structured_jd: Dict
    brainstormed_themes: List[str]
    ranked_themes: List[Tuple[str, float]]
    gaps: List[str]
    differentiators: List[str]
    final_brief: Optional[StrategyBrief]

@dataclass
class RAGBlackboard:
    """Holds RAG Pipeline state"""
    queries: List[str]
    raw_documents: List[Dict]
    chunks: List[str]
    ranked_chunks: List[Tuple[str, float]]
    filtered_chunks: List[Tuple[str, float]]
    annotated_chunks: List[Dict]
    draft_analysis: str
    critiques: List[str]
    final_analysis: Optional[ThematicAnalysis]

@dataclass
class PlanStep:
    """Single workflow step"""
    agent: str
    status: str  # PENDING, COMPLETED, FAILED
    result: Any
    error: Optional[str]

@dataclass
class Plan:
    """Dynamic workflow plan"""
    steps: List[PlanStep]
    version: int
    created_at: datetime
    modified_at: Optional[datetime]

@dataclass
class WorkflowBlackboard:
    """Central shared state for all agents"""
    workflow_id: str
    master_resume: Dict
    job_input: Dict
    strategy_board: StrategyBlackboard
    rag_board: RAGBlackboard
    plan: Optional[Plan]
    artifacts: Dict[str, str]
    validation_results: List[ValidationResult]
```

---

## Configuration Changes (master_config.json)

### NEW: planner_config
```json
{
  "planner_config": {
    "enabled": true,
    "default_plan": [
      "run_strategy_stack",
      "run_rag_stack",
      "run_bullet_stack",
      "run_drafting_stack",
      "run_qa_stack"
    ],
    "max_replan_loops": 5,
    "enable_critique": true,
    "enable_monitoring": true,
    "fallback_strategy": "stop_on_failure"
  }
}
```

---

## Governor.process_request() - NEW Flow

### V5.4 (Old):
```python
# Hard-coded sequential workflow
strategy = strategist.create_brief()
validate(strategy)
draft = gemini_drafter.draft()
qa1.check(draft)
qa2.validate(draft)
# ... fixed sequence
```

### V5.6 (New):
```python
# Dynamic agentic loop
blackboard = WorkflowBlackboard(...)
plan = planner.create_initial_plan(blackboard)

while plan.steps and loop_count < max_loops:
    step = plan.steps.pop(0)
    
    # EXECUTE
    result = execution_map[step.agent](blackboard)
    
    # OBSERVE
    state = monitor.observe(blackboard)
    
    # CRITIQUE
    critique = critique_agent.critique(state, blackboard)
    
    # RE-PLAN
    if critique == "FAIL":
        plan = replanner.replan(critique, blackboard)
```

---

## Agent Count Summary

| Category | V5.4 Agents | V5.6 Agents | Change |
|----------|------------|------------|--------|
| **Strategy** | 1 (ChiefStrategist) | 6 (Atomic Stack) | +5 |
| **RAG** | 8 | 8 | 0 |
| **Prompt Engineering** | 0 | 7 | +7 |
| **Bullet Generation** | 2 | 7 | +5 |
| **QA** | 14 | 23 | +9 |
| **Planner** | 0 | 4 | +4 |
| **TOTAL** | ~50 | ~80 | +30 |

---

## Deprecated Agents

### Removed in v5.6:
- `ChiefStrategistAgent` → Replaced by Strategy Stack (6 agents)
- `PreFlightValidator` → Replaced by Atomic QA Swarm
- `ContextAssembler` → Replaced by Prompt Engineering Stack

**Note**: Deprecated agents kept as stubs with warning logs for backward compatibility.

---

## Execution Map

The Governor now uses a function map to route plan steps to implementations:

```python
self.execution_map = {
    "run_strategy_stack": self._run_strategy_stack,
    "run_rag_stack": self._run_rag_stack,
    "run_bullet_stack": self._run_bullet_stack,
    "run_drafting_stack": self._run_drafting_stack,
    "run_qa_stack": self._run_qa_stack,
}
```

Each function orchestrates its atomic agent swarm.

---

## Benefits of v5.6 Architecture

1. **Adaptive Execution**: Planner can dynamically adjust workflow based on failures
2. **Fine-Grained Control**: 80 atomic agents vs 50 monolithic agents
3. **Improved Observability**: Every step tracked in Plan with timestamps
4. **Self-Correction**: RAG Critique agent + RePlanner enable recovery
5. **Extensibility**: New agents can be added without rewriting Governor
6. **Cost Control**: CostEstimator/CostTracker agents for budget management

---

## Migration Notes

### Breaking Changes:
- `RAG_Blackboard` renamed to `RAGBlackboard` (no underscore)
- `ChiefStrategistAgent.create_brief()` → Use Strategy Stack
- Hard-coded workflow in `Governor.process_request()` → Now dynamic

### Backward Compatibility:
- All v5.4 agents still present (may be deprecated)
- `PreFlightValidator` kept as stub for legacy calls
- Existing config keys honored

---

## Next Steps

1. **Implement Missing Stubs**: Many agents return placeholder data
2. **Add LLM Calls**: Connect atomic agents to real API calls
3. **Tune Planner**: Optimize default_plan for production
4. **Expand Execution Map**: Add individual agent mappings
5. **Test Replan Logic**: Verify RePlanner generates valid recovery plans

---

## File Manifest

### Updated Files:
- `agent_swarm.py`: v5.6 (Full agentic architecture)
- `core.py`: v5.6 (Added 5 new data models)
- `master_config.json`: Added `planner_config`

### Unchanged Files:
- `main.py`: Compatible with v5.6
- `validation_stack.py`: Compatible with v5.6
- `job_input.json`: No changes
- `master_resume.json`: No changes

---

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────┐
│                   GOVERNOR v5.6                          │
│            (Planner-Executor-Critique-RePlanner)         │
└──────────────────────────────────────────────────────────┘
                            │
                            ↓
        ┌───────────────────────────────────────┐
        │   WorkflowPlanner.create_initial_plan │
        └───────────────────────────────────────┘
                            │
                            ↓
        ┌────────────────────────────────────────┐
        │          WorkflowBlackboard             │
        │  ┌──────────────────────────────────┐  │
        │  │  StrategyBlackboard (Strategy)   │  │
        │  │  RAGBlackboard (RAG)             │  │
        │  │  Plan (Dynamic Steps)            │  │
        │  │  Artifacts (Outputs)             │  │
        │  └──────────────────────────────────┘  │
        └────────────────────────────────────────┘
                            │
                            ↓
        ┌────────────────────────────────────────┐
        │        EXECUTION LOOP (Agentic)        │
        │   ┌────────────────────────────────┐   │
        │   │ 1. POP next step from plan     │   │
        │   │ 2. EXECUTE agent via map       │   │
        │   │ 3. OBSERVE blackboard state    │   │
        │   │ 4. CRITIQUE result             │   │
        │   │ 5. RE-PLAN if failure          │   │
        │   └────────────────────────────────┘   │
        └────────────────────────────────────────┘
                            │
             ┌──────────────┼──────────────┐
             ↓              ↓              ↓
    ┌───────────────┐ ┌──────────┐ ┌──────────────┐
    │ Strategy      │ │   RAG    │ │ Bullet Swarm │
    │ Stack (6)     │ │ Stack(8) │ │    (7)       │
    └───────────────┘ └──────────┘ └──────────────┘
                            │
             ┌──────────────┼──────────────┐
             ↓              ↓              ↓
    ┌───────────────┐ ┌──────────┐ ┌──────────────┐
    │ Prompt        │ │ Drafting │ │  QA Swarm    │
    │ Stack (7)     │ │ Stack    │ │    (23)      │
    └───────────────┘ └──────────┘ └──────────────┘
```

---

## Version History

- **v5.4**: Hard-coded workflow, 50 agents, monolithic components
- **v5.5**: Added RAG pipeline decomposition (8 agents)
- **v5.6**: Full agentic executor, 80 agents, dynamic planning

---

**End of v5.6 Upgrade Summary**

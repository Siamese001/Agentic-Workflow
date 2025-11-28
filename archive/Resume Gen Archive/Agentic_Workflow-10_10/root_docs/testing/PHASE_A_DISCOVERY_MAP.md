# PHASE A: DISCOVERY & MAPPING RESULTS

## Agent Architecture Map

### L1 (Planning/Cognition) - PURE REASONING
**Current State**: ✅ Well-separated
- `l1/strategy_planning.py`: StrategyPlan, DraftPlan, LatentThinkingPlan
- `l1/rag_planning.py`: RAGReasoningPlan, HydePlan
- `l1/qa_planning.py`: SemanticQAPlan, CouncilPlan
- `l1/safety_planning.py`: SafetyPlan
- `l1/vector_search_planning.py`: VectorSearchPlan
- `l1/workflow_planning.py`: WorkflowPlanBundle orchestration

**Issues Found**:
- ❌ No Instructional Injection v6 prompts
- ❌ Missing many-shot examples
- ❌ No temporal reasoning layer
- ❌ Limited Pinecone-specific planning

### L2 (Execution/Action) - TOOL EXECUTION ONLY
**Current State**: ⚠️ Needs refinement
- `l2/agents.py`: StrategyLLMAgent, DraftingGuild, SemanticQAAgent, ConstitutionalSafetyAgent, HYDEQueryAgent
- `l2/execution.py`: Execution functions
- `l2/vector_search_executor.py`: Pinecone executor

**Issues Found**:
- ⚠️ L2 agents mix some reasoning with execution
- ❌ No Instructional Injection v6 in execution prompts
- ❌ Pinecone integration not centralized through L4
- ❌ Missing many-shot examples for executors

### L3 (Orchestration) - CONTROL FLOW ONLY
**Current State**: ✅ Generally good
- `l3/workflow_graph.py`: DAG-based orchestration
- `core/orchestrator.py`: WorkflowOrchestrator
- `core/integration.py`: Workflow execution
- `infra/dag_engine/`: DAG models and execution

**Issues Found**:
- ❌ No explicit Think-Act-Observe loops
- ❌ No coordinator/sequential/critic patterns documented
- ❌ Missing HITL checkpoints

### L4 (State & Memory) - MEMORY ONLY
**Current State**: ⚠️ Needs significant work
- `l4/manager.py`: StateManager
- `l4/journal.py`: Journal persistence
- `l4/types.py`: State types
- `cache_redis.py`: Redis caching (should be in L4)
- `vector_store_chroma.py`: ChromaDB (should be in L4)

**Issues Found**:
- ❌ Pinecone NOT centralized in L4 - currently in L2 directly
- ❌ No unified vector store adapter
- ❌ No temporal KG integration
- ❌ No namespace/metadata filter management
- ❌ Missing consistent ID schemas

### L5 (Safety & Policy) - SAFETY ONLY
**Current State**: ✅ Well-separated
- `l5/policy.py`: Policy enforcement
- `l5/types.py`: Safety types
- `l5/__init__.py`: SafetySystem

**Issues Found**:
- ❌ No Instructional Injection v6 safety prompts
- ❌ No adversarial mode examples
- ❌ Missing delegation guardrails

## Pinecone Integration Analysis

### Current Usage
- `providers/pinecone_client/pinecone_client.py`: SDK wrapper
- `l2/vector_search_executor.py`: Direct Pinecone calls from L2

### Issues
- ❌ L2 calls Pinecone directly (violates L4 boundary)
- ❌ No namespace management
- ❌ No metadata filters
- ❌ No hybrid search
- ❌ No temporal queries
- ❌ No consistent ID schemas

### Required Changes
1. Move Pinecone adapter to L4
2. Create unified vector store interface
3. Add namespace per user/job/workflow
4. Implement metadata filters
5. Add temporal query support
6. Centralize embedding pipeline

## Prompt Analysis

### Current State
- Prompts scattered across modules as inline strings
- No Instructional Injection v6 structure
- No many-shot examples
- No temporal reasoning prompts
- No MoR-style latent reasoning

### Required Changes
1. Extract all prompts to dedicated modules
2. Apply Instructional Injection v6 (30 layers + 6 extensions)
3. Add 2-4 many-shot examples per agent
4. Add temporal reasoning prompts
5. Add multi-agent coordination prompts
6. Add HITL governance prompts

## Test Suite Analysis

### Current Coverage
- 59 test files across multiple categories
- Unit tests for agents, DAG, control plane
- Integration tests for workflows
- Golden state evaluation tests

### Issues
- ⚠️ Tests may break with L4 Pinecone refactor
- ❌ No Pinecone adapter tests
- ❌ No Instructional Injection v6 tests
- ❌ No many-shot example tests
- ❌ Limited temporal reasoning tests

## Priority Refactoring Order

### Phase B (Sub-Atomic Agents)
1. ✅ L1 already sub-atomic
2. Refine L2 to remove reasoning
3. ✅ L3 already sub-atomic
4. ✅ L5 already sub-atomic

### Phase C (Richer Context)
1. Wire ExecutionContext through all layers
2. Add temporal KG views
3. Add Pinecone retrieval context
4. Implement scene assembly

### Phase D (Instructional Injection v6)
1. Create prompt registry module
2. Apply 30-layer v6 structure
3. Add 6 extensions (temporal, multi-agent, MoR, tool-conflict, HITL, safety-delegation)
4. Extract all inline prompts

### Phase E (Many-Shot Examples)
1. Add 2-4 examples per L1 planner
2. Add 2-3 examples per L2 executor
3. Add 2-4 examples per L3 orchestrator
4. Add 2-3 examples per L5 safety agent

### Phase F (Pinecone Integration)
1. Create L4 Pinecone adapter
2. Move all Pinecone calls to L4
3. Implement namespace management
4. Add metadata filters
5. Add temporal queries
6. Centralize embedding pipeline

### Phase G (Test Hardening)
1. Update tests for L4 Pinecone changes
2. Add Instructional Injection v6 tests
3. Add many-shot example tests
4. Add temporal reasoning tests
5. Add end-to-end workflow tests

## Estimated Changes
- **Files to modify**: ~100+
- **New files to create**: ~20+
- **Lines of code**: ~5000+ changes
- **Test updates**: ~30+ test files

## Critical Path
1. Phase F (Pinecone to L4) - MUST DO FIRST (breaks imports)
2. Phase B (Sub-atomic refinement) - Depends on F
3. Phase D (Instructional Injection v6) - Can parallel with B
4. Phase C (Context wiring) - Depends on F
5. Phase E (Many-shot) - Depends on D
6. Phase G (Tests) - Depends on all above

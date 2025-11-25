# Agentic Workflow 10_10 Reorganization Plan

## Current Structure Issues

- Agents scattered across `l2/`, `core/`, and `meta/`
- Infrastructure mixed across `infra/`, `core/`, and `runtime/`
- Prompts split between `prompts/` and various layer directories
- Tools and utilities fragmented throughout the codebase
- Layer-based organization (L1-L5) makes navigation difficult for developers

## Target OpenAI-Style Structure

```text
Agentic-Workflow-10_10/
├── agents/                    # All agent definitions and implementations
│   ├── __init__.py
│   ├── planning/             # L1 planning agents
│   │   ├── __init__.py
│   │   ├── workflow_planning.py
│   │   ├── strategy_planning.py
│   │   ├── safety_planning.py
│   │   ├── rag_planning.py
│   │   ├── qa_planning.py
│   │   ├── kg_rag_fusion_planning.py
│   │   ├── kg_retrieval_planning.py
│   │   └── vector_search_planning.py
│   ├── execution/            # L2 execution agents
│   │   ├── __init__.py
│   │   ├── agents.py
│   │   ├── execution.py
│   │   ├── fusion_executor.py
│   │   ├── invalidation_executor.py
│   │   ├── kg_retrieval_executor.py
│   │   ├── triplet_extraction_executor.py
│   │   └── vector_search_executor.py
│   └── meta/                 # Meta-agents and coordination
│       ├── __init__.py
│       ├── multi_agent.py
│       └── cognitive_agents.py
├── orchestration/             # L3 orchestration and workflow control
│   ├── __init__.py
│   ├── workflow_engine.py
│   ├── workflow_graph.py
│   ├── routing.py
│   ├── agent_bus.py
│   ├── agent_registry.py
│   ├── agent_router_policy.py
│   ├── orchestrator.py
│   └── workflow_context.py
├── infrastructure/            # Core infrastructure components
│   ├── __init__.py
│   ├── context_engine/       # Context management
│   │   ├── __init__.py
│   │   ├── relevance.py
│   │   ├── slots.py
│   │   ├── pinned.py
│   │   └── assembly.py
│   ├── control_plane/        # Control plane components
│   │   ├── __init__.py
│   │   └── models.py
│   ├── dag/                  # DAG infrastructure
│   │   ├── __init__.py
│   │   └── [dag files]
│   ├── dag_engine/           # DAG execution engine
│   │   ├── __init__.py
│   │   └── [dag_engine files]
│   ├── model_routing/        # Model routing logic
│   │   ├── __init__.py
│   │   └── [model_routing files]
│   ├── reasoning/            # Reasoning infrastructure
│   │   ├── __init__.py
│   │   └── [reasoning files]
│   ├── sandbox/              # Security sandbox
│   │   ├── __init__.py
│   │   ├── vm_manager.py
│   │   ├── microvm.py
│   │   └── [sandbox files]
│   └── storage/              # Data persistence
│       ├── __init__.py
│       ├── vector_store_chroma.py
│       ├── cache_redis.py
│       └── retrieval.py
├── prompts/                   # All prompt templates and management
│   ├── __init__.py
│   ├── prompt_system_v10_10.py
│   ├── v6_prompt_integration.py
│   ├── many_shot_examples.py
│   ├── instructional_injection_v6.py
│   ├── self_correction_injection.py
│   ├── temporal_kg_injection.py
│   ├── cms/                  # Content management system
│   │   ├── __init__.py
│   │   ├── compiler.py
│   │   ├── schemas.py
│   │   ├── store.py
│   │   ├── acl.py
│   │   └── changelog.py
│   └── builders/             # Prompt builders
│       ├── __init__.py
│       └── prompt_builder.py
├── tools/                     # Utility tools and helpers
│   ├── __init__.py
│   ├── retrievers/           # Retrieval tools
│   │   ├── __init__.py
│   │   ├── bm25.py
│   │   └── [other retrievers]
│   ├── runtime/              # Runtime utilities
│   │   ├── __init__.py
│   │   ├── runtime_utils.py
│   │   └── [runtime files]
│   └── evaluation/           # Evaluation tools
│       ├── __init__.py
│       ├── golden_eval.py
│       └── [eval files]
├── providers/                 # External service providers
│   ├── __init__.py
│   ├── openai_client.py
│   ├── anthropic_client.py
│   └── google_genai_client.py
├── safety/                    # L5 safety and policy
│   ├── __init__.py
│   ├── injection_detection.py
│   └── [safety files]
├── state/                     # L4 state and memory management
│   ├── __init__.py
│   ├── [state management files]
├── config/                    # Configuration files
│   ├── [existing config files]
├── cli/                       # Command line interfaces
│   ├── [existing cli files]
├── tests/                     # Test suite
│   ├── [existing test structure]
├── docs/                      # Documentation
│   ├── [existing docs]
├── eval/                      # Evaluation datasets and results
│   ├── [existing eval files]
├── refactoring/               # Refactoring documentation
│   ├── [existing refactoring files]
└── [root level files]
```

## File Mapping

### Current → Target Locations

#### Agents (l2/, core/, meta/ → agents/)

- `l2/agents.py` → `agents/execution/agents.py`
- `l2/execution.py` → `agents/execution/execution.py`
- `l2/fusion_executor.py` → `agents/execution/fusion_executor.py`
- `l2/invalidation_executor.py` → `agents/execution/invalidation_executor.py`
- `l2/kg_retrieval_executor.py` → `agents/execution/kg_retrieval_executor.py`
- `l2/triplet_extraction_executor.py` → `agents/execution/triplet_extraction_executor.py`
- `l2/vector_search_executor.py` → `agents/execution/vector_search_executor.py`
- `l1/*_planning.py` → `agents/planning/`
- `core/cognitive_agents.py` → `agents/meta/cognitive_agents.py`
- `meta/multi_agent.py` → `agents/meta/multi_agent.py`

#### Orchestration (core/, l3/ → orchestration/)

- `core/workflow_engine.py` → `orchestration/workflow_engine.py`
- `core/agent_bus.py` → `orchestration/agent_bus.py`
- `core/agent_registry.py` → `orchestration/agent_registry.py`
- `core/agent_router_policy.py` → `orchestration/agent_router_policy.py`
- `core/orchestrator.py` → `orchestration/orchestrator.py`
- `core/workflow_context.py` → `orchestration/workflow_context.py`
- `l3/workflow_graph.py` → `orchestration/workflow_graph.py`
- `l3/routing.py` → `orchestration/routing.py`

#### Infrastructure (infra/, core/, runtime/ → infrastructure/)

- `infra/` → `infrastructure/` (move entire directory)
- `core/integration.py` → `infrastructure/integration.py`
- `core/di_container.py` → `infrastructure/di_container.py`
- `vector_store_chroma.py` → `infrastructure/storage/vector_store_chroma.py`
- `cache_redis.py` → `infrastructure/storage/cache_redis.py`
- `retrieval.py` → `infrastructure/storage/retrieval.py`
- `runtime/` → `infrastructure/runtime/` (move entire directory)

#### Prompts (prompts/, meta/ → prompts/)

- `prompts/` → `prompts/` (keep existing, reorganize subdirs)
- `meta/prompt_builder.py` → `prompts/builders/prompt_builder.py`

#### Tools (retrievers/, root utilities → tools/)

- `retrievers/` → `tools/retrievers/`
- `runtime_utils.py` → `tools/runtime/runtime_utils.py`
- `golden_eval.py` → `tools/evaluation/golden_eval.py`
- `simulation.py` → `tools/evaluation/simulation.py`
- `registry.py` → `tools/registry.py`

#### Safety (l5/ → safety/)

- `l5/` → `safety/`

#### State (l4/ → state/)
- `l4/` → `state/`

#### Providers (providers/ → providers/)
- `providers/` → `providers/` (keep existing)

## Import Update Strategy

1. **Layer imports**: Update `from l1.` → `from agents.planning.`, `from l2.` → `from agents.execution.`, etc.
2. **Core imports**: Update `from core.` → `from orchestration.` or `from infrastructure.`
3. **Infra imports**: Update `from infra.` → `from infrastructure.`
4. **Cross-references**: Update all cross-capability imports to reflect new structure

## Benefits of New Structure

1. **Functional clarity**: Developers can find all agent-related code in one place
2. **Capability grouping**: Related functionality is co-located
3. **Reduced cognitive load**: No need to think in terms of L1-L5 layers
4. **Better navigation**: Intuitive folder structure based on purpose
5. **Easier onboarding**: New developers can understand codebase organization quickly
6. **Maintains separation**: Still respects architectural boundaries while improving usability

## Migration Steps

1. Create new directory structure
2. Move files according to mapping
3. Update import statements systematically
4. Run tests to verify functionality
5. Update documentation
6. Clean up old directories

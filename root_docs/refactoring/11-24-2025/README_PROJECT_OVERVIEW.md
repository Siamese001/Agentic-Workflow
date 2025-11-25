# 🚀 Agentic Workflow — v10.8 Core Architecture (Flat L1–L5 Design)
### Clean, Modern, Deterministic Agentic AI Architecture

This branch (`10_8_core`) contains the next-generation **v10.8 agentic architecture**, built cleanly from the ground up with **strict L1–L5 layering**, a **flat file structure**, and **zero legacy contamination** from v10.7.

This structure is optimized for:
- modularity  
- testability  
- safety  
- state determinism  
- ChatGPT/Codex ingestion  
- flat repo portability  

The entire architecture is scaffolded and ready for **Priority 0–9 implementation**.

---

# 🧱 Architecture Overview (L1 → L5)

v10.8 implements a layered agentic model:

```
L1 — Reasoning (Generate plans)
L2 — Execution (Use tools, perform operations)
L3 — Orchestration (Sequence actions, control flow)
L4 — State (Memory, patching, deterministic state machine)
L5 — Safety (Policy, constitutional checks, injection detection)
```

Each file in the repository is prefixed (`l1_`, `l2_`, etc.) to clearly indicate its layer.

---

# 📁 File Layout (Flat, No Subfolders)

### L1 — Reasoners
```
l1_reasoner_base.py
l1_strategy_reasoner.py
l1_rag_reasoner.py
l1_drafting_reasoner.py
```

### L2 — Execution Agents & Tools
```
l2_tool_base.py
l2_rag_execution.py
l2_bullet_execution.py
l2_drafting_execution.py
l2_qa_validation.py
```

### L3 — Orchestration
```
l3_graph_orchestrator.py
l3_rag_orchestrator.py
l3_draft_orchestrator.py
l3_bullet_orchestrator.py
l3_qa_orchestrator.py
```

### L4 — State, Memory, Context
```
l4_state_adapter.py
l4_memory_manager.py
l4_context_budget.py
l4_state_machine.py
```

### L5 — Safety & Policy
```
l5_safety_gateway.py
l5_constitutional_engine.py
l5_policy_engine.py
l5_injection_detector.py
```

### Prompt System
```
prompt_envelope.py
prompt_renderer.py
prompt_templates.py
```

### Utilities
```
utils_logger.py
utils_patch_helpers.py
utils_types.py
```

### Test Suite (Flat v10.8)
```
test_rag_execution_v10_8.py
test_bullet_execution_v10_8.py
test_drafting_execution_v10_8.py
test_qa_validation_v10_8.py
test_state_adapter_v10_8.py
test_context_budget_v10_8.py
test_safety_v10_8.py
test_prompt_envelope_v10_8.py
test_orchestrator_v10_8.py
test_end_to_end_v10_8.py
```

### Input Files
```
job_input.json
master_resume.json
```

### Project Metadata
```
requirements.txt
.gitignore
```

---

# 🧪 Testing

Run the flat test suite:

```
pytest -q
```


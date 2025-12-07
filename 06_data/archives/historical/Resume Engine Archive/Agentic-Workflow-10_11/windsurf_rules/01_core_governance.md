# /windsurf_rules/01_core_governance.md
## Core Governance & Layering Model (Condensed)

### 1. Repository Boundaries
- Treat the Explorer root as `Agentic-Workflow-10_11/`.
- Operate ONLY inside this directory.

### 2. File Operations
- Existing files → modify via apply_patch only.
- New files → use write_to_file with absolute Windows path.
- Never mix creation + modification in the same patch.
- No `.py` allowed under `refactoring/**`.

### 3. MAX Override Mode
- Never stop, ask questions, or explain.
- Only apply_patch + write_to_file allowed.
- Ambiguity → choose the most reasonable safe interpretation.
- Errors → auto-correct via additional diffs.
- Active until: `RESET WIND SURF`.

### 4. Layering Model (L1–L5)
- L1: Planning only; no IO, network, randomness, or tools.
- L2: Tool execution only; no planning.
- L3: Orchestration only; DAG control only.
- L4: State + memory only; no logic.
- L5: Safety + policy only; no functional output.
- Cognitive agents must be thin L1→L2 shims only.

### 5. Sub-Atomic Agent Architecture
- Each agent implements a single capability.
- Agents must be deterministic, stateless, side-effect free.
- Agents >25 logical lines must be decomposed into micro-agents.
- Typed boundaries required: InputSchema / OutputSchema / FailureModes / Invariants.
- Agents must not retain memory; all persistent data is L4.

### 6. 14 Sub-Domain Alignment
Structural: layering, boundaries, typed contracts, typed DAGs  
Behavioral: capability maturity, reasoning models, context, tools  
Operational: safety, observability, cost, testing, prompt governance, sandbox

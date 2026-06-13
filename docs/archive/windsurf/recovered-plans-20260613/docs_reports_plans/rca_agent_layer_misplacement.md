# RCA: Agent Layer Misplacement Detection Gap in FileClassificationAgent

**Date**: 2026-02-11
**Scope**: `agentic_core/L5_safety/reasoning/FileClassificationAgent.py`

## Root Cause

`FileClassificationAgent` had **no validation** for whether an Agent file's content
signals match its physical layer placement. Three methods existed for layer-related
checks, but none covered this gap:

| Method | What it checks | Gap |
|--------|---------------|-----|
| `classify_file()` | File TYPE (AGENT, CONFIG, etc.) | No layer output |
| `suggest_manager_layer()` | Layer routing for `*Manager` only | Excludes `*Agent` files |
| `validate_layer_alignment()` | Subprocess allowlists, Agent→reasoning, scripts purity | No content-vs-layer check |
| `check_layer_purity()` | L0 cognitive pollution only | No equivalent for L1-L6 |

**Result**: Agents placed in the wrong layer during manual creation or consolidation
were never detected by any automated check.

## Fix Applied

### New method: `suggest_agent_layer()`

Generalizes `suggest_manager_layer()` to ALL Agent files using two-pass detection:

- **Pass 1 — AST import scoring** (high confidence): Direct third-party imports
  (`redis`, `pinecone`, `google.generativeai`, `subprocess`, etc.) and cross-layer
  `agentic_core.L*` imports scored with weighted signals.
- **Pass 2 — Content keyword scoring** (medium confidence): Domain keywords
  (`cache`, `vector`, `embedding`, `dashboard`, `workflow`, etc.) counted per layer.
- **Merged scoring**: Import scores weighted 2x, content scores 1x.

### Thresholds (tuned for 0 false positives on 83-agent corpus)

- Minimum merged score: **10** (eliminates single-import noise at ~6-8)
- Minimum delta (best vs current): **6**

### Purpose-Over-Mechanism filter

Agents in **L5_safety** and **L3_orchestration** legitimately import from other
layers to govern/validate/coordinate them. A ratio-based filter suppresses false
positives when the agent's own-layer purpose keywords outnumber the suggested
layer's content keywords.

### Wiring

`validate_layer_alignment()` now calls `suggest_agent_layer()` for any `*Agent.py`
file (excluding `base_agents/` and `FileClassificationAgent.py` itself).

## Confirmed Misplacements (4 agents)

| Agent | Current | Suggested | Score | Evidence |
|-------|---------|-----------|-------|----------|
| PineconeSovereignAgent | L5_safety | **L4_state** | 24 vs 0 | `import pinecone`, imports `RedisSovereignAgent` from L4 |
| EmbeddingSovereignAgent | L2_execution | **L1_cognition** | 16 vs 0 | `import google.generativeai`, `import openai` |
| FilesystemSSOTReconcilerAgent | L0_maintenance | **L5_safety** | 30 vs 0 | 5 imports from L5_safety (blueprint enforcement) |
| SSOTFolderCleanupAgent | L0_maintenance | **L5_safety** | 24 vs 0 | 4 imports from L5_safety (SSOT compliance) |

### PineconeSovereignAgent

Vector store gateway: manages Pinecone index lifecycle, upsert/query operations,
embedding storage. Imports `pinecone` SDK + `RedisSovereignAgent` from L4. Its
PURPOSE is state/memory management, not safety governance.

### EmbeddingSovereignAgent

Embedding generation gateway: calls `google.generativeai` and `openai` APIs to
produce embeddings. Its own docstring says "NOT an agent - utility singleton."
PURPOSE is cognitive inference (L1), not tool execution (L2).

### FilesystemSSOTReconcilerAgent + SSOTFolderCleanupAgent

Both enforce structure blueprint compliance — scanning filesystem, detecting drift,
archiving unauthorized folders. Import heavily from L5_safety (blueprint config,
HierarchyAgent, LocationValidatorAgent, ArchivalGatekeeper). PURPOSE is governance,
not maintenance.

## Additional Bug: EmbeddingSovereignAgent Misnamed

Line 60 of `EmbeddingSovereignAgent.py`:
```
[PHASE 8] NOT an agent - utility singleton to avoid circular imports.
```

The file is named `*Agent.py`, inherits `SovereignBaseAgent`, but its own docstring
says it's not an agent. This is a naming violation that should be addressed in a
separate cleanup.

## Validation Results

```
Total agents scanned: 83
Correctly placed (not flagged): 79
Flagged as misplaced: 4
False positives: 0
Errors: 0
```

## Files Changed

- `agentic_core/L5_safety/reasoning/FileClassificationAgent.py`
  - Added `suggest_agent_layer()` method (~130 lines)
  - Added `AGENT_LAYER_MISPLACEMENT` check to `validate_layer_alignment()`
  - Self-exclusion for `FileClassificationAgent.py` in both methods

## Violation

[Describe the violation or issue that triggered this RCA]

---

## Corrective Actions

[List the corrective actions taken to resolve the issue]

---


# Phase 2b: Review Needed Duplicates

**Issue:** In these 6 cases, the "duplicate" has MORE code than the "canonical".

## Analysis

| Agent | Current Canonical | Current Duplicate | Can Lines | Dup Lines | Decision |
| --- | --- | --- | --- | --- | --- |
| CognitiveContractManagerAgent | L2_execution/ToolRegistry | schemas/models | 258 | 548 | Keep schemas/models (richer) |
| DeadCodeDetectorAgent | L5_safety/guardrails | utils/core_extensions | 222 | 356 | Keep utils (richer) |
| FileManagerAgent | L4_state/filesystem | utils/core_extensions | 233 | 298 | Keep utils (richer) |
| GovernanceAgent | L5_safety/validators | L1_cognition/thought_engine | 206 | 798 | Keep L1 (richer) |
| HealerAgent | L2_execution/ToolRegistry | L5_safety/guardrails | 602 | 1338 | Keep L5 (richer) |
| PromptGovernorAgent | L2_execution/ToolRegistry | prompt_governance/rendering | 258 | 280 | Keep prompt_governance (richer) |

## Recommended Actions

For each case, we should:
1. Keep the RICHER file (currently marked as "duplicate")
2. Delete the SMALLER file (currently marked as "canonical")

### Delete Commands (Swap Logic)

```bash
# Delete the SMALLER files (originally marked as canonical)
git rm "agentic_core/L2_execution/ToolRegistry/CognitiveContractManagerAgent.py"
git rm "agentic_core/L5_safety/guardrails/DeadCodeDetectorAgent.py"
git rm "agentic_core/L4_state/filesystem/FileManagerAgent.py"
git rm "agentic_core/L5_safety/validators/GovernanceAgent.py"
git rm "agentic_core/L2_execution/ToolRegistry/HealerAgent.py"
git rm "agentic_core/L2_execution/ToolRegistry/PromptGovernorAgent.py"

git commit -m "chore: remove 6 smaller duplicate agents (keeping richer versions)"
```

## Alternative: Keep SSOT Locations

If SSOT compliance requires specific locations, we should:
1. Keep the file in the SSOT-compliant location
2. Merge any missing functionality from the richer duplicate
3. Delete the non-SSOT duplicate

This requires manual review of each file pair.

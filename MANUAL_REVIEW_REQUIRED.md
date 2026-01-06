# Manual Review Required - AST Parse Errors

**Date:** 2026-01-06  
**Status:** 34 files require manual syntax fixes before sovereignty enforcement

## Critical Files (Severely Corrupted)

### FilesystemSSOTReconcilerAgent.py
**Path:** `agentic_core/L0_maintenance/scripts/FilesystemSSOTReconcilerAgent.py`  
**Error:** Unterminated triple-quoted string literal at line 934  
**Severity:** CRITICAL - 70+ cascading errors  
**Action:** Complete file review needed - likely has malformed docstring containing code

## Files Requiring Pass Statements (30 files)

These files have empty function bodies that need `pass` statements:

1. `agentic_core/config/blueprint_sovereign/bias_auditor.py:214`
2. `agentic_core/config/blueprint_sovereign/heal_validator.py:327`
3. `agentic_core/knowledge/document_loaders/SovereignRAGManagerAgent.py:256`
4. `agentic_core/L0_maintenance/scripts/filesystem_mcp_client.py:115`
5. `agentic_core/L0_maintenance/scripts/gitkraken_mcp_client.py:194`
6. `agentic_core/L1_cognition/thought_engine/CanonHealerAgent.py:537`
7. `agentic_core/L1_cognition/thought_engine/strategic_planner.py:313`
8. `agentic_core/L2_execution/ToolRegistry/figma_client_sovereign.py:113`
9. `agentic_core/L3_orchestration/workflow_engines/agent_factory.py:187`
10. `agentic_core/L3_orchestration/workflow_engines/agent_gym_impl.py:259`
11. `agentic_core/L3_orchestration/workflow_engines/context_curator_impl.py:237`
12. `agentic_core/L3_orchestration/workflow_engines/mcp_router_sovereign.py:159`
13. `agentic_core/L4_state/ValidationContext/knowledge_graph_sovereign_graph_client.py:250`
14. `agentic_core/L4_state/ValidationContext/storage.py:400`
15. `agentic_core/L5_safety/guardrails/BiasDetectorAgent.py:58`
16. `agentic_core/L5_safety/guardrails/ConstitutionalReviewerAgent.py:116`
17. `agentic_core/L5_safety/guardrails/llm_router_mcp_client.py:75`
18. `agentic_core/L5_safety/guardrails/multi_provider_router_agent.py:669`
19. `agentic_core/L5_safety/guardrails/PIISanitizerAgent.py:66`
20. `agentic_core/L5_safety/guardrails/PromptInjectionDetectorAgent.py:102`
21. `agentic_core/observability/metrics/BenchmarkingAgent.py:411`
22. `agentic_core/utils/core_extensions/git.py:155`
23. `agentic_core/utils/core_extensions/http.py:183`
24. `agentic_core/utils/core_extensions/pinecone.py:138`
25. `agentic_core/utils/core_extensions/redis.py:187`
26. `agentic_core/utils/core_extensions/sovereignty_auditor.py:189`
27. `apps_lic/engines/outreach_engine/rag/campaign_rag.py:71`
28. `apps_rg/engines/resume_generator.py:227`

## Files with Try Block Issues (2 files)

Need `pass` statements after `try:` statements:

1. `agentic_core/L1_cognition/thought_engine/sovereign_cognitive_plane.py:36`
2. `agentic_core/L1_cognition/thought_engine/sovereign_cognitive_plane_with_streamer.py:33`

## Files with Line Continuation Issues (2 files)

Have unexpected characters after line continuation (backslash):

1. `agentic_core/L1_cognition/thought_engine/ReflectionAgent.py:229`
2. `agentic_core/L2_execution/ToolRegistry/McpConnectionManagerAgent.py:52`

## Files with Missing Colons (1 file)

1. `agentic_core/L2_execution/ToolRegistry/DynamicModelRouterAgent.py:474`

---

## Recommended Fix Approach

### Quick Fix Script
```python
# For files needing pass statements
def add_pass_to_empty_function(file_path, line_num):
    lines = Path(file_path).read_text().splitlines(keepends=True)
    func_line = lines[line_num - 1]
    indent = len(func_line) - len(func_line.lstrip())
    lines.insert(line_num, ' ' * (indent + 4) + 'pass\n')
    Path(file_path).write_text(''.join(lines))
```

### Manual Review Priority
1. **HIGH:** FilesystemSSOTReconcilerAgent.py (severely corrupted)
2. **MEDIUM:** Line continuation and missing colon issues
3. **LOW:** Empty function bodies (can be batch-fixed with script)

---

## Impact on Sovereignty Enforcement

**Decision:** Proceed with enforcement on parseable files only.

- PascalSovereigntyEnforcerAgent will skip unparseable files
- PythonFileSovereigntyEnforcerAgent will skip unparseable files
- These 34 files will be documented for post-enforcement manual review
- Sovereignty fixes can be re-run after manual repairs

**Estimated Coverage:** ~95% of codebase (34 files out of ~1000+ Python files)

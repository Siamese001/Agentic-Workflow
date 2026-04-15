# Wave B External-Only Target-State Audit

**Date**: 2026-04-15  
**Collection**: `ext_authority` only (323 chunks, Lane A=112, Lane B=211)  
**Model**: BAAI/bge-m3 (1024-dim, cosine)  
**Queries**: 20 semantically varied target-state topics  
**Anti-drift rule**: Target state MUST come from ext_authority only. repo_evidence and ext_raw are EXCLUDED.  

---

## 1. Wave B Freeze Gate Results

**Overall gate verdict**: FAIL ✗  

| Gate | Description | Count | Result |
|------|-------------|-------|--------|
| `G1_C2_ext_authority_normative_use` | C2: ext_authority invalid_for_normative_use=False | 323 | **PASS ✓** |
| `G2_C4_ext_authority_https_urls` | C4: ext_authority source_url starts with https:// | 323 | **PASS ✓** |
| `G3_ext_authority_required_fields` | ext_authority all required fields present | 323 | **PASS ✓** |
| `G4_C3_repo_evidence_normative_gate` | C3: repo_evidence invalid_for_normative_use=True | 2789 | **PASS ✓** |
| `G5_C5_repo_evidence_no_web_urls` | C5: repo_evidence no https:// source_url | 2789 | **PASS ✓** |
| `G6_repo_evidence_required_fields` | repo_evidence all required fields present | 2789 | **PASS ✓** |
| `G7_C3_ext_raw_normative_gate` | C3: ext_raw invalid_for_normative_use=True | 70 | **PASS ✓** |
| `G8_C9_ext_raw_no_url_overlap` | C9: ext_raw no URL overlap with ext_authority | 70 | **PASS ✓** |
| `G9_target_state_retrieval_strength` | Target-state retrieval: ≥15/20 queries Strong+Adequate | 20 | **FAIL ✗** |
| | ↳ Strong=5 Adequate=9 Weak=6 Empty=0 | | |
| `G10_repo_contamination_zero` | Repo contamination in target-state audit = 0 | 100 | **PASS ✓** |
| `G11_ext_raw_contamination_zero` | ext_raw contamination in target-state audit = 0 | 100 | **PASS ✓** |

## 2. External-Only Target-State Audit Results

Grounding thresholds: **STRONG** dist<0.35 + answer support · **ADEQUATE** dist<0.50 · **WEAK** dist<0.70 · **EMPTY** ≥0.70

### TS-01 — Context Engineering [🟡 ADEQUATE]

**Query**: What is context engineering and how should context windows be managed in language model applications?  
**Route class**: target_state / best_practice → `ext_authority`  
**dist@1**: 0.4208 · **Grounding**: ADEQUATE · **Drift risk**: PARTIAL_DRIFT  

| Rank | dist | Source | Authority tier | Source band | Topic |
|------|------|--------|----------------|-------------|-------|
| 1 | 0.4208 | `gh://openai/openai-agents-python/main/docs/mcp.md` | T3_guidance | supporting_guidance | tool_contracts |
| 2 | 0.4306 | `gh://openai/openai-agents-python/main/docs/context.md` | T3_guidance | supporting_guidance | orchestration |
| 3 | 0.4346 | `gh://openai/openai-agents-python/main/docs/results.md` | T3_guidance | supporting_guidance | orchestration |
| 4 | 0.4474 | `gh://openai/openai-agents-python/main/docs/agents.md` | T3_guidance | supporting_guidance | orchestration |
| 5 | 0.4494 | `gh://microsoft/autogen/main/README.md` | T3_guidance | supporting_guidance | orchestration |

**Top result**: `Model context protocol (MCP)`  
**Snippet**: # Model context protocol (MCP)  The [Model context protocol](https://modelcontextprotocol.io/introduction) (MCP) standardises how applications expose tools and context to language models. From the off  

### TS-02 — Contextual Retrieval [🟡 ADEQUATE]

**Query**: How does contextual retrieval improve chunk-level relevance by adding context headers before embedding?  
**Route class**: target_state / best_practice → `ext_authority`  
**dist@1**: 0.4995 · **Grounding**: ADEQUATE · **Drift risk**: PARTIAL_DRIFT  

| Rank | dist | Source | Authority tier | Source band | Topic |
|------|------|--------|----------------|-------------|-------|
| 1 | 0.4995 | `gh://openai/openai-agents-python/main/docs/results.md` | T3_guidance | supporting_guidance | orchestration |
| 2 | 0.5127 | `gh://modelcontextprotocol/python-sdk/main/README.md` | T2_standard | target_state_authority | tool_contracts |
| 3 | 0.5209 | `gh://openai/openai-agents-python/main/docs/tools.md` | T3_guidance | supporting_guidance | tool_contracts |
| 4 | 0.5244 | `gh://openai/openai-agents-python/main/docs/handoffs.md` | T3_guidance | supporting_guidance | orchestration |
| 5 | 0.5268 | `gh://anthropics/anthropic-cookbook/main/patterns/agents/basi` | T3_guidance | supporting_guidance | orchestration |

**Top result**: `Results > Streaming lifecycle and diagnostics > Context and usage`  
**Snippet**: ### Context and usage  [`context_wrapper`][agents.result.RunResultBase.context_wrapper] exposes your app context together with SDK-managed runtime metadata such as approvals, usage, and nested `tool_i  

### TS-03 — Hybrid Retrieval [⚠️ WEAK]

**Query**: How should hybrid dense vector search and sparse BM25 retrieval be combined with score fusion?  
**Route class**: target_state / best_practice → `ext_authority`  
**dist@1**: 0.5607 · **Grounding**: WEAK · **Drift risk**: DRIFT_RISK  

| Rank | dist | Source | Authority tier | Source band | Topic |
|------|------|--------|----------------|-------------|-------|
| 1 | 0.5607 | `gh://openai/openai-agents-python/main/docs/tools.md` | T3_guidance | supporting_guidance | tool_contracts |
| 2 | 0.5771 | `gh://anthropics/anthropic-cookbook/main/patterns/agents/orch` | T3_guidance | supporting_guidance | orchestration |
| 3 | 0.5863 | `gh://openai/openai-agents-python/main/docs/tools.md` | T3_guidance | supporting_guidance | tool_contracts |
| 4 | 0.5894 | `gh://modelcontextprotocol/python-sdk/main/README.md` | T2_standard | target_state_authority | tool_contracts |
| 5 | 0.5925 | `gh://openai/openai-agents-python/main/docs/tools.md` | T3_guidance | supporting_guidance | tool_contracts |

**Top result**: `Tools > Hosted tools > Hosted tool search`  
**Snippet**: fore using CRM tools.",     tools=[*crm_tools, ToolSearchTool()], )  result = await Runner.run(agent, "Look up customer_42 and list their open orders.") print(result.final_output) ```  What to know:    

### TS-04 — Reranking [⚠️ WEAK]

**Query**: How does cross-encoder reranking improve retrieval precision after initial vector search?  
**Route class**: target_state / best_practice → `ext_authority`  
**dist@1**: 0.5309 · **Grounding**: WEAK · **Drift risk**: DRIFT_RISK  

| Rank | dist | Source | Authority tier | Source band | Topic |
|------|------|--------|----------------|-------------|-------|
| 1 | 0.5309 | `gh://openai/openai-agents-python/main/docs/tools.md` | T3_guidance | supporting_guidance | tool_contracts |
| 2 | 0.5393 | `gh://anthropics/anthropic-cookbook/main/patterns/agents/eval` | T3_guidance | supporting_guidance | safety_eval |
| 3 | 0.5425 | `gh://openai/openai-agents-python/main/docs/tools.md` | T3_guidance | supporting_guidance | tool_contracts |
| 4 | 0.5441 | `gh://anthropics/anthropic-cookbook/main/patterns/agents/orch` | T3_guidance | supporting_guidance | orchestration |
| 5 | 0.5594 | `gh://openai/openai-agents-python/main/docs/tools.md` | T3_guidance | supporting_guidance | tool_contracts |

**Top result**: `Tools > Hosted tools > Hosted tool search`  
**Snippet**: ### Hosted tool search  Tool search lets OpenAI Responses models defer large tool surfaces until runtime, so the model loads only the subset it needs for the current turn. This is useful when you have  

### TS-05 — Metadata Provenance [🟡 ADEQUATE]

**Query**: What metadata fields should be attached to retrieved chunks for provenance tracking and authority scoring?  
**Route class**: target_state / best_practice → `ext_authority`  
**dist@1**: 0.4978 · **Grounding**: ADEQUATE · **Drift risk**: PARTIAL_DRIFT  

| Rank | dist | Source | Authority tier | Source band | Topic |
|------|------|--------|----------------|-------------|-------|
| 1 | 0.4978 | `gh://openai/openai-agents-python/main/docs/running_agents.md` | T3_guidance | supporting_guidance | orchestration |
| 2 | 0.5138 | `gh://openai/openai-agents-python/main/docs/tools.md` | T3_guidance | supporting_guidance | tool_contracts |
| 3 | 0.5237 | `gh://openai/openai-agents-python/main/docs/tools.md` | T3_guidance | supporting_guidance | tool_contracts |
| 4 | 0.5266 | `gh://openai/openai-agents-python/main/docs/results.md` | T3_guidance | supporting_guidance | orchestration |
| 5 | 0.5288 | `gh://langchain-ai/langgraph/main/README.md` | T3_guidance | supporting_guidance | orchestration |

**Top result**: `Running agents > Runner lifecycle and configuration > Run config`  
**Snippet**: er you opt in to `nest_handoff_history`. It must return the exact list of input items to forward to the next agent, allowing you to replace the built-in summary without writing a full handoff filter.   

### TS-06 — Chunking Strategy [🟡 ADEQUATE]

**Query**: What is the recommended chunking strategy for precision retrieval of technical documentation?  
**Route class**: target_state / best_practice → `ext_authority`  
**dist@1**: 0.4995 · **Grounding**: ADEQUATE · **Drift risk**: PARTIAL_DRIFT  

| Rank | dist | Source | Authority tier | Source band | Topic |
|------|------|--------|----------------|-------------|-------|
| 1 | 0.4995 | `gh://anthropics/anthropic-cookbook/main/patterns/agents/basi` | T3_guidance | supporting_guidance | orchestration |
| 2 | 0.5190 | `gh://modelcontextprotocol/python-sdk/main/README.md` | T2_standard | target_state_authority | tool_contracts |
| 3 | 0.5250 | `gh://modelcontextprotocol/python-sdk/main/README.md` | T2_standard | target_state_authority | tool_contracts |
| 4 | 0.5291 | `gh://openai/openai-agents-python/main/docs/tools.md` | T3_guidance | supporting_guidance | tool_contracts |
| 5 | 0.5330 | `gh://openai/openai-agents-python/main/docs/tools.md` | T3_guidance | supporting_guidance | tool_contracts |

**Top result**: `Route support tickets to appropriate teams based on content analysis`  
**Snippet**: # Route support tickets to appropriate teams based on content analysis  support_routes = {     "billing": """You are a billing support specialist. Follow these guidelines:     1. Always start with "Bi  

### TS-07 — Parent Child Expansion [⚠️ WEAK]

**Query**: When should parent-child chunk expansion be used and how does it work in retrieval pipelines?  
**Route class**: target_state / best_practice → `ext_authority`  
**dist@1**: 0.5152 · **Grounding**: WEAK · **Drift risk**: DRIFT_RISK  

| Rank | dist | Source | Authority tier | Source band | Topic |
|------|------|--------|----------------|-------------|-------|
| 1 | 0.5152 | `gh://anthropics/anthropic-cookbook/main/patterns/agents/eval` | T3_guidance | supporting_guidance | safety_eval |
| 2 | 0.5238 | `gh://openai/openai-agents-python/main/docs/tools.md` | T3_guidance | supporting_guidance | tool_contracts |
| 3 | 0.5377 | `gh://modelcontextprotocol/python-sdk/main/README.md` | T2_standard | target_state_authority | tool_contracts |
| 4 | 0.5409 | `gh://anthropics/anthropic-cookbook/main/patterns/agents/basi` | T3_guidance | supporting_guidance | orchestration |
| 5 | 0.5424 | `gh://openai/openai-agents-python/main/docs/mcp.md` | T3_guidance | supporting_guidance | tool_contracts |

**Top result**: `Evaluator-Optimizer Workflow > When to use this workflow`  
**Snippet**: ### When to use this workflow This workflow is particularly effective when we have:  - Clear evaluation criteria - Value from iterative refinement  The two signs of good fit are:  - LLM responses can   

### TS-08 — Evidence Shaping [🟡 ADEQUATE]

**Query**: How should retrieved evidence be shaped and filtered before grounding an agent response?  
**Route class**: target_state / best_practice → `ext_authority`  
**dist@1**: 0.4447 · **Grounding**: ADEQUATE · **Drift risk**: PARTIAL_DRIFT  

| Rank | dist | Source | Authority tier | Source band | Topic |
|------|------|--------|----------------|-------------|-------|
| 1 | 0.4447 | `gh://openai/openai-agents-python/main/docs/results.md` | T3_guidance | supporting_guidance | orchestration |
| 2 | 0.4513 | `gh://openai/openai-agents-python/main/docs/running_agents.md` | T3_guidance | supporting_guidance | orchestration |
| 3 | 0.4707 | `gh://openai/openai-agents-python/main/docs/results.md` | T3_guidance | supporting_guidance | orchestration |
| 4 | 0.4715 | `gh://openai/openai-agents-python/main/docs/results.md` | T3_guidance | supporting_guidance | orchestration |
| 5 | 0.4721 | `gh://openai/openai-agents-python/main/docs/tools.md` | T3_guidance | supporting_guidance | tool_contracts |

**Top result**: `Results > Input, next-turn history, and new items`  
**Snippet**: ## Input, next-turn history, and new items  These surfaces answer different questions:  | Property or helper | What it contains | Best for | | --- | --- | --- | | [`input`][agents.result.RunResultBase  

### TS-09 — Abstain Refine [⚠️ WEAK]

**Query**: When should an agent abstain from answering and what signals indicate insufficient evidence coverage?  
**Route class**: target_state / best_practice → `ext_authority`  
**dist@1**: 0.5102 · **Grounding**: WEAK · **Drift risk**: DRIFT_RISK  

| Rank | dist | Source | Authority tier | Source band | Topic |
|------|------|--------|----------------|-------------|-------|
| 1 | 0.5102 | `gh://openai/openai-agents-python/main/docs/running_agents.md` | T3_guidance | supporting_guidance | orchestration |
| 2 | 0.5309 | `gh://openai/openai-agents-python/main/docs/context.md` | T3_guidance | supporting_guidance | orchestration |
| 3 | 0.5369 | `gh://openai/openai-agents-python/main/docs/tools.md` | T3_guidance | supporting_guidance | tool_contracts |
| 4 | 0.5379 | `gh://openai/openai-agents-python/main/docs/running_agents.md` | T3_guidance | supporting_guidance | orchestration |
| 5 | 0.5387 | `gh://openai/openai-agents-python/main/docs/handoffs.md` | T3_guidance | supporting_guidance | orchestration |

**Top result**: `Running agents > Runner lifecycle and configuration > Run config`  
**Snippet**: s.kind == "approval_rejected":         return (             f"Tool call '{args.tool_name}' was rejected by a human reviewer. "             "Ask for confirmation or propose a safer alternative."         

### TS-10 — Routing Principles [🟡 ADEQUATE]

**Query**: What are the routing principles for directing queries to the appropriate retrieval source or collection?  
**Route class**: target_state / best_practice → `ext_authority`  
**dist@1**: 0.4730 · **Grounding**: ADEQUATE · **Drift risk**: PARTIAL_DRIFT  

| Rank | dist | Source | Authority tier | Source band | Topic |
|------|------|--------|----------------|-------------|-------|
| 1 | 0.4730 | `gh://anthropics/anthropic-cookbook/main/patterns/agents/basi` | T3_guidance | supporting_guidance | orchestration |
| 2 | 0.4847 | `gh://modelcontextprotocol/python-sdk/main/README.md` | T2_standard | target_state_authority | tool_contracts |
| 3 | 0.4980 | `gh://openai/openai-agents-python/main/docs/tools.md` | T3_guidance | supporting_guidance | tool_contracts |
| 4 | 0.4989 | `gh://openai/openai-agents-python/main/docs/results.md` | T3_guidance | supporting_guidance | orchestration |
| 5 | 0.4996 | `gh://modelcontextprotocol/python-sdk/main/README.md` | T2_standard | target_state_authority | tool_contracts |

**Top result**: `Route support tickets to appropriate teams based on content analysis`  
**Snippet**: # Route support tickets to appropriate teams based on content analysis  support_routes = {     "billing": """You are a billing support specialist. Follow these guidelines:     1. Always start with "Bi  

### TS-11 — Agentic Architecture [🟡 ADEQUATE]

**Query**: What agentic architecture patterns define how agents reason plan and execute actions?  
**Route class**: target_state / best_practice → `ext_authority`  
**dist@1**: 0.4165 · **Grounding**: ADEQUATE · **Drift risk**: PARTIAL_DRIFT  

| Rank | dist | Source | Authority tier | Source band | Topic |
|------|------|--------|----------------|-------------|-------|
| 1 | 0.4165 | `gh://openai/openai-agents-python/main/docs/agents.md` | T3_guidance | supporting_guidance | orchestration |
| 2 | 0.4326 | `gh://openai/openai-agents-python/main/docs/agents.md` | T3_guidance | supporting_guidance | orchestration |
| 3 | 0.4674 | `gh://microsoft/autogen/main/README.md` | T3_guidance | supporting_guidance | orchestration |
| 4 | 0.4685 | `gh://openai/openai-agents-python/main/docs/agents.md` | T3_guidance | supporting_guidance | orchestration |
| 5 | 0.4836 | `gh://openai/openai-agents-python/main/README.md` | T3_guidance | supporting_guidance | orchestration |

**Top result**: `Agents > Multi-agent system design patterns`  
**Snippet**: ## Multi-agent system design patterns  There are many ways to design multi‑agent systems, but we commonly see two broadly applicable patterns:  1. Manager (agents as tools): A central manager/orchestr  

### TS-12 — Orchestrator Workers [✅ STRONG]

**Query**: How does the orchestrator-workers multi-agent pattern coordinate specialized sub-agents?  
**Route class**: target_state / best_practice → `ext_authority`  
**dist@1**: 0.3485 · **Grounding**: STRONG · **Drift risk**: GROUNDED  

| Rank | dist | Source | Authority tier | Source band | Topic |
|------|------|--------|----------------|-------------|-------|
| 1 | 0.3485 | `gh://openai/openai-agents-python/main/docs/agents.md` | T3_guidance | supporting_guidance | orchestration |
| 2 | 0.3613 | `gh://anthropics/anthropic-cookbook/main/patterns/agents/orch` | T3_guidance | supporting_guidance | orchestration |
| 3 | 0.3847 | `gh://anthropics/anthropic-cookbook/main/patterns/agents/orch` | T3_guidance | supporting_guidance | orchestration |
| 4 | 0.3888 | `gh://anthropics/anthropic-cookbook/main/patterns/agents/orch` | T3_guidance | supporting_guidance | orchestration |
| 5 | 0.4336 | `gh://openai/openai-agents-python/main/docs/tools.md` | T3_guidance | supporting_guidance | tool_contracts |

**Top result**: `Agents > Multi-agent system design patterns`  
**Snippet**: ## Multi-agent system design patterns  There are many ways to design multi‑agent systems, but we commonly see two broadly applicable patterns:  1. Manager (agents as tools): A central manager/orchestr  

### TS-13 — Tool Contracts Mcp [✅ STRONG]

**Query**: How should Model Context Protocol MCP tools be defined registered and called from agents?  
**Route class**: target_state / best_practice → `ext_authority`  
**dist@1**: 0.2767 · **Grounding**: STRONG · **Drift risk**: GROUNDED  

| Rank | dist | Source | Authority tier | Source band | Topic |
|------|------|--------|----------------|-------------|-------|
| 1 | 0.2767 | `gh://openai/openai-agents-python/main/docs/mcp.md` | T3_guidance | supporting_guidance | tool_contracts |
| 2 | 0.3084 | `gh://modelcontextprotocol/python-sdk/main/README.md` | T2_standard | target_state_authority | tool_contracts |
| 3 | 0.3563 | `gh://openai/openai-agents-python/main/docs/mcp.md` | T3_guidance | supporting_guidance | tool_contracts |
| 4 | 0.3625 | `gh://openai/openai-agents-python/main/docs/mcp.md` | T3_guidance | supporting_guidance | tool_contracts |
| 5 | 0.3636 | `gh://openai/openai-agents-python/main/docs/mcp.md` | T3_guidance | supporting_guidance | tool_contracts |

**Top result**: `Model context protocol (MCP)`  
**Snippet**: # Model context protocol (MCP)  The [Model context protocol](https://modelcontextprotocol.io/introduction) (MCP) standardises how applications expose tools and context to language models. From the off  

### TS-14 — Fastmcp Patterns [✅ STRONG]

**Query**: What is the FastMCP pattern for building MCP servers and how should tool schemas be structured?  
**Route class**: target_state / best_practice → `ext_authority`  
**dist@1**: 0.3471 · **Grounding**: STRONG · **Drift risk**: GROUNDED  

| Rank | dist | Source | Authority tier | Source band | Topic |
|------|------|--------|----------------|-------------|-------|
| 1 | 0.3471 | `gh://modelcontextprotocol/python-sdk/main/README.md` | T2_standard | target_state_authority | tool_contracts |
| 2 | 0.3620 | `gh://modelcontextprotocol/python-sdk/main/README.md` | T2_standard | target_state_authority | tool_contracts |
| 3 | 0.3694 | `gh://modelcontextprotocol/python-sdk/main/README.md` | T2_standard | target_state_authority | tool_contracts |
| 4 | 0.3697 | `gh://modelcontextprotocol/python-sdk/main/README.md` | T2_standard | target_state_authority | tool_contracts |
| 5 | 0.3866 | `gh://modelcontextprotocol/python-sdk/main/README.md` | T2_standard | target_state_authority | tool_contracts |

**Top result**: `Create MCP server`  
**Snippet**: # Create MCP server mcp = FastMCP("My App", json_response=True)   @mcp.tool() def hello() -> str:     """A simple hello tool"""     return "Hello from MCP!"  

### TS-15 — Agent Handoffs [✅ STRONG]

**Query**: How should agent handoffs be structured when transferring control between specialized agents?  
**Route class**: target_state / best_practice → `ext_authority`  
**dist@1**: 0.3350 · **Grounding**: STRONG · **Drift risk**: GROUNDED  

| Rank | dist | Source | Authority tier | Source band | Topic |
|------|------|--------|----------------|-------------|-------|
| 1 | 0.3350 | `gh://openai/openai-agents-python/main/docs/handoffs.md` | T3_guidance | supporting_guidance | orchestration |
| 2 | 0.3456 | `gh://openai/openai-agents-python/main/docs/agents.md` | T3_guidance | supporting_guidance | orchestration |
| 3 | 0.3504 | `gh://openai/openai-agents-python/main/docs/handoffs.md` | T3_guidance | supporting_guidance | orchestration |
| 4 | 0.3599 | `gh://openai/openai-agents-python/main/docs/handoffs.md` | T3_guidance | supporting_guidance | orchestration |
| 5 | 0.3651 | `gh://openai/openai-agents-python/main/docs/agents.md` | T3_guidance | supporting_guidance | orchestration |

**Top result**: `(1)! > Customizing handoffs via the `handoff()` function`  
**Snippet**: ### Customizing handoffs via the `handoff()` function  The [`handoff()`][agents.handoffs.handoff] function lets you customize things.  -   `agent`: This is the agent to which things will be handed off  

### TS-16 — Safety Guardrails [🟡 ADEQUATE]

**Query**: What safety guardrails and constraints should govern autonomous agent behavior?  
**Route class**: target_state / best_practice → `ext_authority`  
**dist@1**: 0.4558 · **Grounding**: ADEQUATE · **Drift risk**: PARTIAL_DRIFT  

| Rank | dist | Source | Authority tier | Source band | Topic |
|------|------|--------|----------------|-------------|-------|
| 1 | 0.4558 | `gh://openai/openai-agents-python/main/docs/guardrails.md` | T3_guidance | supporting_guidance | safety_eval |
| 2 | 0.4705 | `gh://openai/openai-agents-python/main/docs/guardrails.md` | T3_guidance | supporting_guidance | safety_eval |
| 3 | 0.4846 | `gh://openai/openai-agents-python/main/docs/guardrails.md` | T3_guidance | supporting_guidance | safety_eval |
| 4 | 0.4859 | `gh://openai/openai-agents-python/main/docs/guardrails.md` | T3_guidance | supporting_guidance | safety_eval |
| 5 | 0.4945 | `gh://openai/openai-agents-python/main/README.md` | T3_guidance | supporting_guidance | orchestration |

**Top result**: `Guardrails > Workflow boundaries`  
**Snippet**: ## Workflow boundaries  Guardrails are attached to agents and tools, but they do not all run at the same points in a workflow:  -   **Input guardrails** run only for the first agent in the chain. -     

### TS-17 — Evaluator Optimizer [🟡 ADEQUATE]

**Query**: How does the evaluator-optimizer pattern improve agent output quality through iterative refinement?  
**Route class**: target_state / best_practice → `ext_authority`  
**dist@1**: 0.4287 · **Grounding**: ADEQUATE · **Drift risk**: PARTIAL_DRIFT  

| Rank | dist | Source | Authority tier | Source band | Topic |
|------|------|--------|----------------|-------------|-------|
| 1 | 0.4287 | `gh://anthropics/anthropic-cookbook/main/patterns/agents/eval` | T3_guidance | supporting_guidance | safety_eval |
| 2 | 0.4522 | `gh://anthropics/anthropic-cookbook/main/patterns/agents/orch` | T3_guidance | supporting_guidance | orchestration |
| 3 | 0.4668 | `gh://anthropics/anthropic-cookbook/main/patterns/agents/orch` | T3_guidance | supporting_guidance | orchestration |
| 4 | 0.4682 | `gh://anthropics/anthropic-cookbook/main/patterns/agents/orch` | T3_guidance | supporting_guidance | orchestration |
| 5 | 0.4771 | `gh://openai/openai-agents-python/main/docs/agents.md` | T3_guidance | supporting_guidance | orchestration |

**Top result**: `Evaluator-Optimizer Workflow > Example Use Case: Iterative coding loop`  
**Snippet**: ### Example Use Case: Iterative coding loop  evaluator_prompt = """ Evaluate this following code implementation for: 1. code correctness 2. time complexity 3. style and best practices  You should be e  

### TS-18 — Single Vs Multi Agent [✅ STRONG]

**Query**: When should a single agent be used versus a multi-agent architecture for complex tasks?  
**Route class**: target_state / best_practice → `ext_authority`  
**dist@1**: 0.3291 · **Grounding**: STRONG · **Drift risk**: GROUNDED  

| Rank | dist | Source | Authority tier | Source band | Topic |
|------|------|--------|----------------|-------------|-------|
| 1 | 0.3291 | `gh://openai/openai-agents-python/main/docs/agents.md` | T3_guidance | supporting_guidance | orchestration |
| 2 | 0.3615 | `gh://openai/openai-agents-python/main/docs/agents.md` | T3_guidance | supporting_guidance | orchestration |
| 3 | 0.4147 | `gh://openai/openai-agents-python/main/docs/tools.md` | T3_guidance | supporting_guidance | tool_contracts |
| 4 | 0.4170 | `gh://microsoft/autogen/main/README.md` | T3_guidance | supporting_guidance | orchestration |
| 5 | 0.4330 | `gh://microsoft/autogen/main/README.md` | T3_guidance | supporting_guidance | orchestration |

**Top result**: `Agents > Multi-agent system design patterns`  
**Snippet**: ## Multi-agent system design patterns  There are many ways to design multi‑agent systems, but we commonly see two broadly applicable patterns:  1. Manager (agents as tools): A central manager/orchestr  

### TS-19 — Embedding Model [⚠️ WEAK]

**Query**: What embedding model dimensions and distance metrics are recommended for agentic retrieval systems?  
**Route class**: target_state / best_practice → `ext_authority`  
**dist@1**: 0.5102 · **Grounding**: WEAK · **Drift risk**: DRIFT_RISK  

| Rank | dist | Source | Authority tier | Source band | Topic |
|------|------|--------|----------------|-------------|-------|
| 1 | 0.5102 | `gh://openai/openai-agents-python/main/docs/tracing.md` | T3_guidance | supporting_guidance | observability |
| 2 | 0.5151 | `gh://openai/openai-agents-python/main/docs/tools.md` | T3_guidance | supporting_guidance | tool_contracts |
| 3 | 0.5209 | `gh://openai/openai-agents-python/main/README.md` | T3_guidance | supporting_guidance | orchestration |
| 4 | 0.5467 | `gh://openai/openai-agents-python/main/docs/results.md` | T3_guidance | supporting_guidance | orchestration |
| 5 | 0.5600 | `gh://openai/openai-agents-python/main/docs/tracing.md` | T3_guidance | supporting_guidance | observability |

**Top result**: `Tracing > Ecosystem integrations > External tracing processors list`  
**Snippet**: ### External tracing processors list  -   [Weights & Biases](https://weave-docs.wandb.ai/guides/integrations/openai_agents) -   [Arize-Phoenix](https://docs.arize.com/phoenix/tracing/integrations-trac  

### TS-20 — Normative Requirements [⚠️ WEAK]

**Query**: What normative requirements must agentic systems satisfy for determinism provenance and safety?  
**Route class**: target_state / best_practice → `ext_authority`  
**dist@1**: 0.5292 · **Grounding**: WEAK · **Drift risk**: DRIFT_RISK  

| Rank | dist | Source | Authority tier | Source band | Topic |
|------|------|--------|----------------|-------------|-------|
| 1 | 0.5292 | `gh://openai/openai-agents-python/main/docs/agents.md` | T3_guidance | supporting_guidance | orchestration |
| 2 | 0.5490 | `gh://openai/openai-agents-python/main/docs/running_agents.md` | T3_guidance | supporting_guidance | orchestration |
| 3 | 0.5499 | `gh://openai/openai-agents-python/main/docs/running_agents.md` | T3_guidance | supporting_guidance | orchestration |
| 4 | 0.5507 | `gh://openai/openai-agents-python/main/README.md` | T3_guidance | supporting_guidance | orchestration |
| 5 | 0.5551 | `gh://openai/openai-agents-python/main/docs/agents.md` | T3_guidance | supporting_guidance | orchestration |

**Top result**: `Agents > Basic configuration`  
**Snippet**: ## Basic configuration  The most common properties of an agent are:  | Property | Required | Description | | --- | --- | --- | | `name` | yes | Human-readable agent name. | | `instructions` | yes | Sy  

## 3. Grounding Coverage Summary

| Grounding level | Count | % | Interpretation |
|-----------------|-------|---|----------------|
| STRONG | 5 | 25% | External retrieval is self-sufficient |
| ADEQUATE | 9 | 45% | Retrieval supports grounded guidance |
| WEAK | 6 | 30% | Gap — model memory supplement risk |
| EMPTY | 0 | 0% | Fail-closed — no valid guidance |

**External coverage**: 14/20 queries adequately grounded from ext_authority  
**Gate G9**: FAIL ✗ — only 14/20 queries grounded; gap topics need additional ext_authority sources  

**Anti-drift compliance**: All results sourced exclusively from `ext_authority`. repo_evidence and ext_raw were not queried.  

# /windsurf_rules/06_safety_policy_cost.md
## Safety, Policy, and Cost Rules (Condensed)

### 1. Safety & Policy (L5 Only)
- L5 enforces PII detection, uncertainty thresholds, and risk routing.
- Allowed outcomes: allow, deny, reroute, escalate.
- L5 produces decisions, not content.

### 2. Policy Boundaries
- No agent other than L5 may enforce safety gates.
- All high-risk flows must be routed through L5.

### 3. Cost Optimization Rules
- Enforce compute budgets per agent and per DAG.
- Prefer lower-cost, lower-latency models when viable.
- Prevent cost regressions via CI enforcement.
- Semantic caching allowed only when bounded and safe.

### 4. Sandbox Requirements
- All potentially dangerous operations must be sandbox-isolated.
- L5 governs safety-critical execution flows.

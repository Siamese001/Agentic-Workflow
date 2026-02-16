# Phase 5 — Enforcement + Governance Locks Evidence

## Wave 5.1 — Policy Purity Contract (Import Bans)

### Test File

`tests/governance/test_heal_policy_purity_contract.py`

### Tests

**TestHealPolicyPurityContract**:
1. `test_stdlib_only_imports` — Heal policy module must import stdlib only (no routing/executor imports)
2. `test_no_network_model_keywords` — Heal policy module must not contain network/model keywords in identifiers
3. `test_no_banned_string_literals` — Heal policy module must not contain banned keywords in string literals

### Banned Import Roots

- `agentic_core.L0_routing`
- `agentic_core.executors`
- `apps_`

### Banned Keywords

- `router`
- `executor`
- `openai`
- `gemini`
- `vllm`
- `anthropic`

### pytest -q tests/governance/test_heal_policy_purity_contract.py

```text
tests/governance/test_heal_policy_purity_contract.py::TestHealPolicyPurityContract::test_stdlib_only_imports PASSED
tests/governance/test_heal_policy_purity_contract.py::TestHealPolicyPurityContract::test_no_network_model_keywords PASSED
tests/governance/test_heal_policy_purity_contract.py::TestHealPolicyPurityContract::test_no_banned_string_literals PASSED
====================== 3 passed in 0.02s =======================
```

### pytest -q (full suite)

```text
===================== 129 passed in 20.06s =====================
```

Exit code: 0

**WAVE 5.1 ACCEPTANCE**: All tests pass. Policy purity contract enforced.

---

## Wave 5.2 — Standard_Heal Routing Ban Contract (AST-Based)

### Test File

`tests/governance/test_standard_heal_no_routing_contract.py`

### Tests

**TestStandardHealNoRoutingContract**:
1. `test_no_banned_imports` — Decorators module must not import routing/executor modules
2. `test_standard_heal_no_routing_calls` — standard_heal function must not contain routing/executor calls
3. `test_wrapper_function_no_routing_calls` — Nested wrapper function must not contain routing calls

### Banned Import Modules

- `L0_routing`
- `executors`
- `model_router`
- `openai`
- `gemini`
- `vllm`
- `anthropic`

### Banned Call Names

- `route`
- `router`
- `execute_model`
- `call_llm`
- `completion`
- `chat`
- `invoke`

### pytest -q tests/governance/test_standard_heal_no_routing_contract.py

```text
tests/governance/test_standard_heal_no_routing_contract.py::TestStandardHealNoRoutingContract::test_no_banned_imports PASSED
tests/governance/test_standard_heal_no_routing_contract.py::TestStandardHealNoRoutingContract::test_standard_heal_no_routing_calls PASSED
tests/governance/test_standard_heal_no_routing_contract.py::TestStandardHealNoRoutingContract::test_wrapper_function_no_routing_calls PASSED
====================== 3 passed in 0.02s =======================
```

### pytest -q (full suite)

```text
===================== 132 passed in 20.31s =====================
```

Exit code: 0

**WAVE 5.2 ACCEPTANCE**: All tests pass. Routing ban contract enforced.

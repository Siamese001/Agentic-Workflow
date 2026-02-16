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

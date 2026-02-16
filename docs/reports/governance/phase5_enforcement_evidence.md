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

---

## Wave 5.3 — Flag + Observer Safety Contract

### Test File

`tests/governance/test_heal_escalation_flag_contract.py`

### Tests

**TestFlagDefaultOff**:
1. `test_no_escalation_log_without_env_var` — Without env var, no 'escalation_enabled=1' log appears
2. `test_observer_not_invoked_without_env_var` — Without env var, observer is not invoked

**TestObserverSeamSafety**:
3. `test_observer_default_is_none_at_import` — Observer seam must be None at import time
4. `test_observer_not_reassigned_at_module_scope` — Observer seam must not be reassigned at module scope (AST check)

### pytest -q tests/governance/test_heal_escalation_flag_contract.py

```text
tests/governance/test_heal_escalation_flag_contract.py::TestFlagDefaultOff::test_no_escalation_log_without_env_var PASSED
tests/governance/test_heal_escalation_flag_contract.py::TestFlagDefaultOff::test_observer_not_invoked_without_env_var PASSED
tests/governance/test_heal_escalation_flag_contract.py::TestObserverSeamSafety::test_observer_default_is_none_at_import PASSED
tests/governance/test_heal_escalation_flag_contract.py::TestObserverSeamSafety::test_observer_not_reassigned_at_module_scope PASSED
====================== 4 passed in 0.03s =======================
```

### pytest -q (full suite)

```text
===================== 136 passed in 20.34s =====================
```

Exit code: 0

**WAVE 5.3 ACCEPTANCE**: All tests pass. Flag + observer safety contracts enforced.

---

## PHASE 5 CLOSEOUT

### Final Commits

**Wave 5.1**:
```text
dbcb63a50 test(governance): heal policy purity contract
```

**Wave 5.2**:
```text
44eb87e8d test(governance): ban routing/executor calls in standard_heal
```

**Wave 5.3**:
```text
f46c08a53 test(governance): escalation flag + observer safety contracts
```

### Clean Tree Proof

```bash
git status --porcelain=v1
```

```text
(empty - clean working tree)
```

---

## PHASE 5 ACCEPTANCE STATUS: COMPLETE

**All acceptance criteria met:**

- ✓ `pytest -q` exits 0 (136 passed)
- ✓ New contracts fail if:
  - Policy module gains routing/executor imports
  - standard_heal gains routing/executor calls
  - Observer seam is set by default or reassigned at module scope
  - Flag behavior changes from default-off
- ✓ Only allowed files changed:
  - `tests/governance/test_heal_policy_purity_contract.py`
  - `tests/governance/test_standard_heal_no_routing_contract.py`
  - `tests/governance/test_heal_escalation_flag_contract.py`
  - `docs/reports/governance/phase5_enforcement_evidence.md`
- ✓ Evidence contains raw outputs (no truncation)
- ✓ Clean working tree

**Phase 5 is CLOSED.**

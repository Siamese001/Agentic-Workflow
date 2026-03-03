# Phase 3 Evidence: Canonical Seam Enforcement + Network Tripwire

```text
$ git status --porcelain
(empty - clean tree)

$ git rev-parse HEAD
5fd3ecf1aca972280274c6861bca9e938907ab77

$ git --no-pager show --name-only --oneline HEAD
5fd3ecf1a governance(healing): Phase 3 canonical seam enforcement + network tripwire
agentic_core/L5_safety/types/heal_llm_seam_types.py
agentic_core/utils/decorators_util.py
docs/reports/governance/phase3_seam_enforcement_evidence.md
tests/governance/conftest.py
tests/governance/test_heal_policy_wiring.py

$ pytest -q tests/governance/test_heal_policy_wiring.py
24 passed in 0.06s

CAPABILITY_TOKEN_ENFORCEMENT:
- _HEAL_SEAM_CAPABILITY contextvars token (default=False)
- set_heal_seam_capability() only called by standard_heal
- guarded_heal_llm_call() raises HealSeamBypassError if token not set
- reset_heal_seam_capability() called in finally block

NETWORK_TRIPWIRE:
- block_network_in_governance_tests autouse fixture
- Patches socket.socket to raise NetworkTripwireError
- @pytest.mark.allow_network exempts integration tests

POLICY_DECISION_RECORD:
- PolicyDecisionRecord dataclass (frozen, no timestamps/UUIDs)
- Fields: confidence, enable_llm, complexity, prior_failures, proceed, tier, threshold_used, rationale
- input_hash() produces deterministic 16-char SHA256 prefix
- Emitted via _policy_decision key in heal result
```

PHASE 3 ACCEPTANCE:

- Phase 2 evidence is clean-tree and commit-proven (ba3e5395f)
- Only standard_heal can reach LLM escalation wrapper (3 tests)
- Governance tests include network-call tripwire (2 tests)
- Policy decision record is deterministic and schema-stable (3 tests)
- Total: 24 tests pass

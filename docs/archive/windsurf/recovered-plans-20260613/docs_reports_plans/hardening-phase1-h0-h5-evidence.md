# Hardening Phase 1: H0 + H5 Evidence

**Phase:** 1 / Wave 1
**Date:** 2026-02-18
**Branch:** adaptive_control
**Baseline:** 688949932

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Objective

Fix H0 pre-condition (5 failing governance tests) and implement H5 (frozen LearningArtifactIntent with pre-L2 hash).

## Scope Declaration

| File | Intent |
|---|---|
| `agentic_core/utils/decorators_util.py` | Add `DEFAULT_HEAL_LLM_CALLER` module-level attribute (H0) |
| `agentic_core/L0_routing/seams/learning_seam.py` | New: frozen `LearningArtifactIntent` + `LearningPersistenceService` protocol (H5) |
| `tests/governance/test_learning_artifact_intent.py` | New: 9 governance tests for H5 |
| `docs/reports/plans/hardening-phase1-h0-h5-evidence.md` | This evidence file |

Planned impacted files: N=4

## Pre-Change State

```
git branch --show-current
adaptive_control

git status --porcelain
(clean — vllm report stashed as out-of-scope)
```

## H0: DEFAULT_HEAL_LLM_CALLER Fix

Added to `agentic_core/utils/decorators_util.py` line 79-82:

```python
# Phase 8: Default LLM caller seam (test patching)
DEFAULT_HEAL_LLM_CALLER: (
    Callable[[Any], Any] | None
) = None
```

### H0 Test Result

```
python -m pytest tests/governance/test_heal_llm_seam_invocation.py -q --tb=short

6 passed in 0.03s
```

Previously: 5 failed, 1 passed. Now: 6 passed, 0 failed.

## H5: Frozen LearningArtifactIntent

New file: `agentic_core/L0_routing/seams/learning_seam.py`

- `@dataclass(frozen=True)` LearningArtifactIntent
- `create()` static factory computes sha256 intent_hash from canonical JSON bytes
- `verify()` method re-derives hash for L2 receipt validation
- `LearningPersistenceService` Protocol for L2 implementors
- Canonical bytes use sorted keys, no whitespace variance

### H5 Test Result

```
python -m pytest tests/governance/test_learning_artifact_intent.py -v --tb=short

tests/governance/test_learning_artifact_intent.py::TestFrozenImmutability::test_cannot_set_field_after_construction PASSED
tests/governance/test_learning_artifact_intent.py::TestFrozenImmutability::test_cannot_delete_field PASSED
tests/governance/test_learning_artifact_intent.py::TestHashDeterminism::test_same_inputs_same_hash PASSED
tests/governance/test_learning_artifact_intent.py::TestHashDeterminism::test_different_inputs_different_hash PASSED
tests/governance/test_learning_artifact_intent.py::TestHashDeterminism::test_hash_is_sha256_hex PASSED
tests/governance/test_learning_artifact_intent.py::TestHashIntegrity::test_verify_passes_on_valid_intent PASSED
tests/governance/test_learning_artifact_intent.py::TestHashIntegrity::test_verify_fails_on_wrong_hash PASSED
tests/governance/test_learning_artifact_intent.py::TestHashability::test_usable_as_set_member PASSED
tests/governance/test_learning_artifact_intent.py::TestHashability::test_usable_as_dict_key PASSED

9 passed in 0.03s
```

## Full Governance Suite

```
python -m pytest tests/governance/ -q --tb=short

203 passed in 47.36s
```

Previous baseline: 189 passed, 5 failed.
Current: 203 passed, 0 failed (+14 net: +5 H0 fixes, +9 H5 new tests).

## Scope Decontamination

```
git stash push -- "docs/reports/tooling/vllm_model_config_and_windsurf_routing_report.md"
```

Out-of-scope dirty file stashed. Working tree contains only declared scope files.

## Acceptance

- [x] H0: 6/6 heal_llm_seam tests pass (was 1/6)
- [x] H5: 9/9 new governance tests pass
- [x] Full governance suite: 203/203 pass (was 189/194)
- [x] No regressions
- [x] Scope matches declaration (4 files)

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---


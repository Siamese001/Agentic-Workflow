# MRO Diamond Debt Reduction Plan

**Date**: 2026-02-09
**Current count**: 92
**Baseline**: `artifacts/consolidation/mro_diamond_baseline.json`
**Gate**: `ops_scripts/ci/mro_contract_check.py`

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Policy

- Ceiling must decrease by ≥2 per sprint or per consolidation PR.
- Allowlist entries require justification string in `ALLOWLIST` dict.
- Ratchet: once ceiling drops, it never goes back up without `MRO_CEILING_BUMP:<reason>` commit tag.

## Top 10 Highest-Impact Diamond Sources

| Rank | File | Diamonds | Classes | Fix |
| ---- | ---- | -------- | ------- | --- |
| 1 | `apps_lic/engines/PIISanitizerSpecialistAgent.py` | 3 | BiasDetectorSpecialist, PromptInjectionDetectorSpecialist, ConstitutionalReviewerAgent | Remove explicit `SubatomicTestingMixin` — inherited via `LICAgentBase` |
| 2 | `agentic_core/L1_cognition/reasoning/SovereignCognitivePlaneAgent.py` | 2 | SovereignCognitivePlaneAgent | Remove both `SubatomicTestingMixin` + `AtomicExecutionMixin` — inherited via `SovereignBaseAgent` |
| 3 | `agentic_core/L6_observability/reasoning/AutonomicMonitorAgent.py` | 1 | AutonomicMonitorAgent | Remove both mixins — inherited via `SovereignBaseAgent` |
| 4 | `agentic_core/L6_observability/reasoning/MetricsAgent.py` | 1 | MetricsAgent | Remove both mixins — inherited via `SovereignBaseAgent` |
| 5 | `agentic_core/L6_observability/reasoning/PerformanceAnalystAgent.py` | 1 | PerformanceAnalystAgent | Remove both mixins — inherited via `SovereignBaseAgent` |
| 6 | `agentic_core/L6_observability/reasoning/TelemetryAgent.py` | 1 | TelemetryAgent | Remove both mixins — inherited via `SovereignBaseAgent` |
| 7 | `agentic_core/L6_observability/reasoning/TracingAgent.py` | 1 | TracingAgent | Remove both mixins — inherited via `SovereignBaseAgent` |
| 8 | `apps_shared/utils/AppBase.py` | 1 | AppBase | Remove `AtomicExecutionMixin` — inherited via `SovereignBaseAgent` |
| 9 | `apps_lic/engines/LicReflectionAgent.py` | 1 | LicReflectionAgent | Remove `SubatomicTestingMixin` — inherited via `SovereignBaseAgent` |
| 10 | `apps_lic/engines/OutreachSignalRouterAgent.py` | 1 | OutreachSignalRouterAgent | Remove `SubatomicTestingMixin` — inherited via `SovereignBaseAgent` |

## Fix Pattern

For every diamond, the fix is identical:

```python
# BEFORE (diamond):
class MyAgent(SovereignBaseAgent, SubatomicTestingMixin):
    ...

# AFTER (clean):
class MyAgent(SovereignBaseAgent):
    ...
```

The mixin is already inherited via `SovereignBaseAgent` → `SubatomicTestingMixin`.
Remove the redundant explicit listing and its import.

## Sprint Targets

| Sprint | Target Ceiling | Reduction |
| ------ | -------------- | --------- |
| Current | 92 | baseline |
| +1 | 88 | −4 (PIISanitizer + SovereignCognitivePlane) |
| +2 | 82 | −6 (L6 observability batch) |
| +3 | 72 | −10 (apps_lic engines batch) |
| +4 | 60 | −12 (agentic_core L5 safety batch) |
| +5 | 40 | −20 (remaining L5 safety) |
| +6 | 0 | all diamonds resolved |

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


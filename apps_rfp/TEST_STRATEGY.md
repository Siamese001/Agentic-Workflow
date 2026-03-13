# TEST STRATEGY — apps_rfp: AI Proposal / RFP Generator

## Philosophy

All proposal content is generated deterministically from templates. Tests assert on the
structure and presence of specific content (section IDs, phase names, risk item fields).
No probabilistic assertions. No "output should be reasonable."

---

## Test Layers

### Layer 1: Unit Tests (`tests/unit/apps_rfp/test_rfp_pipeline.py`)

| Test Class                   | Coverage Target                                             |
|------------------------------|-------------------------------------------------------------|
| `TestRfpAgentSpecs`          | Config loading, required sections, industry profiles        |
| `TestProposalAssemblyEngine` | All 6 required sections, 5-phase roadmap, risk matrix, assumptions |
| `TestProposalGateValidator`  | Valid proposal passes, missing section blocks, empty risks blocks |
| `TestRfpOrchestrator`        | Dry-run, trace propagation, artifact emission               |
| `TestRfpRunSummary`          | `to_dict()` completeness                                    |

### Layer 2: Industry-Specific Tests (future)

```python
def test_financial_services_includes_sox_risk():
    engine = ProposalAssemblyEngine()
    req = RfpRequest(problem="test", industry="financial_services")
    result = engine.execute(req)
    risk_titles = [r.title for r in result.risks]
    assert any("SOX" in t or "GDPR" in t for t in risk_titles)
```

### Layer 3: Acceptance Tests

| Scenario                                | Expected Outcome                              |
|-----------------------------------------|-----------------------------------------------|
| `--brief "test" --dry-run`              | Status `DRY_RUN`, 6 sections, 0 artifacts     |
| `--industry financial_services`         | Risk matrix includes regulatory flag          |
| Missing `risk_and_governance` section   | Gate blocks, exit 1                           |
| `--posture sovereign`                   | Architecture section references sovereign     |

---

## Run Commands

```bash
pytest tests/unit/apps_rfp/ -v
pytest tests/unit/apps_rfp/ --cov=apps_rfp --cov-report=term-missing
```

---

## Coverage Targets

| Module                                | Target Coverage |
|---------------------------------------|-----------------|
| `config/agent_spec_config.py`         | 90%             |
| `engines/proposal_assembly_engine.py` | 85%             |
| `validators/proposal_gate_validator.py`| 90%            |
| `reasoning/RfpOrchestrator.py`        | 80%             |
| `types/rfp_types.py`                  | 85%             |

---

## Critical Test Cases

1. **Roadmap governance phase** — `require_governance_phase=True` must block if Govern phase absent.
2. **Assumption IDs** — All assumptions must match `ASM-NNN` format.
3. **Risk item completeness** — No risk may have empty `mitigation` or `owner`.
4. **Section order** — Required sections appear in defined order (not alphabetical).
5. **Industry fallback** — Unknown industry logs warning and falls back to `technology`.

---

## Forbidden Test Patterns

- No asserting on word counts of section bodies (content may be refactored).
- No LLM calls in any test.
- No assumptions about disk state between tests.
- No sleeping or time-based waits.

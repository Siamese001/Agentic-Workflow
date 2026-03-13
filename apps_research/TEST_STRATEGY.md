# TEST STRATEGY — apps_research: Autonomous Research Engine

## Philosophy

The research engine is fully deterministic — same topic + mode → same section structure.
Tests assert on mode-specific section presence, claim-type labeling, and source register
completeness. The claim-type system is a first-class contract, tested explicitly.

---

## Test Layers

### Layer 1: Unit Tests (`tests/unit/apps_research/test_research_pipeline.py`)

| Test Class                       | Coverage Target                                              |
|----------------------------------|--------------------------------------------------------------|
| `TestResearchAgentSpecs`         | Config loading, 5 modes present, source register fields     |
| `TestResearchAssemblyEngine`     | Brief sections, comparison matrix, source register, claim types |
| `TestResearchGateValidator`      | Valid passes, empty source register blocks, missing section blocks |
| `TestResearchOrchestrator`       | Dry-run, comparison mode matrix, artifact emission, sources in result |
| `TestResearchRunSummary`         | `to_dict()` completeness                                    |

### Layer 2: Mode Coverage Matrix

Every mode must have at least one test covering:
- Required sections present
- All sections have non-empty bodies
- At least one source in source register

| Mode                | Required Sections Test | Body Non-Empty | Source Register |
|---------------------|------------------------|----------------|-----------------|
| `brief`             | ✓                      | via base test  | ✓               |
| `comparison`        | ✓                      | via base test  | ✓               |
| `trend`             | ✓                      | via base test  | implied         |
| `thought_leadership`| ✓                      | implied        | implied         |

### Layer 3: Claim-Type Contract Tests

```python
def test_all_sections_have_claim_type():
    engine = ResearchAssemblyEngine()
    for mode in ArtifactMode:
        req = ResearchRequest(topic="test", mode=mode)
        result = engine.execute(req)
        for section in result.sections:
            assert section.claim_type is not None, f"{mode}: {section.section_id} missing claim_type"
```

### Layer 4: Acceptance Tests

| Scenario                                | Expected Outcome                                  |
|-----------------------------------------|---------------------------------------------------|
| `--topic "t" --mode brief --dry-run`    | Status `DRY_RUN`, 3 sections, 0 artifacts         |
| `--mode comparison --compare "A,B"`     | Matrix with subjects A, B                         |
| `--mode thought_leadership`             | Sections: hook, insight, evidence, call_to_action |
| Empty source register                   | Gate blocks, exit 1                               |

---

## Run Commands

```bash
pytest tests/unit/apps_research/ -v
pytest tests/unit/apps_research/ --cov=apps_research --cov-report=term-missing
```

---

## Coverage Targets

| Module                                     | Target Coverage |
|--------------------------------------------|-----------------|
| `config/agent_spec_config.py`              | 90%             |
| `engines/research_assembly_engine.py`      | 85%             |
| `validators/research_gate_validator.py`    | 90%             |
| `reasoning/ResearchOrchestrator.py`        | 80%             |
| `types/research_types.py`                  | 85%             |

---

## Epistemic Label Regression Tests

Any time a new section is added to any mode, a test must assert that:
1. The new section has `claim_type` set.
2. The section body contains at least one `[CLAIM_TYPE]` inline label.

These tests prevent unlabeled claims from entering the artifact corpus.

---

## Forbidden Test Patterns

- No tests that accept "section body contains something" as sufficient.
- No accepting `claim_type=None` or `claim_type=""`.
- No `assert result is not None` as sole assertion.

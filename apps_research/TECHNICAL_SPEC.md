# TECHNICAL SPEC — apps_research: Autonomous Research Engine

## Module Map

```
apps_research/
├── config/
│   └── agent_spec_config.py    # ResearchAgentSpecs, load_research_specs()
├── engines/
│   └── research_assembly_engine.py  # ResearchAssemblyEngine: sections + matrix + register
├── reasoning/
│   └── ResearchOrchestrator.py  # ResearchOrchestrator: 3-hop pipeline
├── scripts/
│   └── run_research.py          # CLI entrypoint
├── types/
│   └── research_types.py        # ResearchRequest, ResearchResult, ResearchSection, SourceEntry, ...
├── validators/
│   └── research_gate_validator.py  # ResearchGateValidator
└── __main__.py
```

---

## Key Classes and Contracts

### `ResearchAgentSpecs` (Pydantic BaseModel)
- `artifact_modes: dict[str, ArtifactModeConfig]` — 5 modes with required sections
- `source_register: SourceRegisterConfig` — max sources, required fields, claim types
- `gate: ResearchGateConfig` — min sources, require_source_register, min_quality_score
- `output: ResearchOutputConfig` — output_dir, artifact_prefix, emit flags

### `ResearchAssemblyEngine`
Stateless class. `execute(request: ResearchRequest) → ResearchAssemblyResult`

**Section assembly:**
- `_build_sections(request, mode, sources) → list[ResearchSection]`
- Mode-keyed dict mapping `ArtifactMode → list[ResearchSection]`
- Each section carries `claim_type: ClaimType` (never implicit)
- Non-deterministic sections flagged with `is_deterministic=False`

**Source register:**
- `_build_source_register(request) → list[SourceEntry]`
- Core sources are repo-internal: `agentic_core` modules used as direct evidence
- Comparison subjects create interpretation-typed source entries

**Comparison matrix:**
- `_build_comparison_matrix(request) → list[ComparisonRow]`
- `_AGENTIC_FRAMEWORKS` dict: known frameworks with pre-populated dimension values
- Unknown subjects get `"Unknown — requires primary research"` per dimension

### `ResearchOrchestrator` (dataclass)
```python
@dataclass
class ResearchOrchestrator:
    dry_run: bool = False
    output_dir: str = "reports/research"
    gate_mode: str = "HARD_FAIL"
    hop_checkpoints: list[dict] = field(default_factory=list)

    def run(self, request: ResearchRequest) → ResearchResult: ...
```
**Hops:**
1. `HOP-1-ASSEMBLY` → `ResearchAssemblyEngine.execute(request)`
2. `HOP-2-GATE` → `ResearchGateValidator.validate(sections, sources, required_ids)`
3. `HOP-3-EMIT` → Write `.md` artifact + `source_register.json` + `run_summary.json`

---

## Data Flow

```
ResearchRequest(topic, mode, audience_style, comparison_subjects, time_horizon, dry_run)
    │
    ▼
ResearchAssemblyEngine → ResearchAssemblyResult(sections, comparison_matrix, source_register)
    │
    ▼
ResearchGateValidator → ResearchGateResult(passed, violations, quality_score)
    │
    ▼  (if passed)
Artifact Emission → [research_<mode>_*.md, source_register_*.json, run_summary_*.json]
    │
    ▼
ResearchResult(trace_id, topic, mode, status, sections, comparison_matrix, source_register,
               quality_score, gate_violations, artifact_paths, provenance)
```

---

## Claim Type System

All section content is tagged with `ClaimType`:

| Type               | Meaning                                         | Example Usage                         |
|--------------------|-------------------------------------------------|---------------------------------------|
| `direct_evidence`  | From this repo's implementation                 | PolicyHashEnforcer description        |
| `interpretation`   | Derived from evidence; analyst-added meaning    | "This means enterprise buyers will…"  |
| `analyst_inference`| Best-judgment assertion not directly evidenced  | "Trend suggests…"                     |
| `assumption`       | Explicit assumption declared as such            | "Assuming continued OSS momentum…"    |

Labels appear inline in section body (e.g. `**Finding 1 [DIRECT_EVIDENCE]:**`).

---

## Comparison Matrix Schema

```python
@dataclass(frozen=True)
class ComparisonRow:
    subject: str
    dimensions: dict[str, str]  # dimension_id → value string
```

Fixed dimensions for agentic framework comparisons:
- `architecture_model`, `governance_approach`, `determinism_level`
- `scalability`, `enterprise_readiness`, `open_source`

---

## Provenance Contract

```python
provenance = {
    "trace_id": str,          # SHA256[:16] of mode + topic[:64]
    "topic": str,
    "mode": str,
    "app": "apps_research",
    "checkpoints": list[str]
}
```

---

## Dependency Surface

| Dependency    | Reason                         |
|---------------|--------------------------------|
| `pydantic`    | Config schemas                 |
| `hashlib`     | Trace ID                       |
| `json`        | Source register + run summary  |
| `pathlib`     | File operations                |
| `logging`     | Structured logging             |

No LLM dependencies. All synthesis is deterministic.

---

## Extension Points

| Point                   | How to extend                                              |
|-------------------------|------------------------------------------------------------|
| New artifact mode       | Add `ArtifactModeConfig` to `ResearchAgentSpecs.artifact_modes` |
| New claim type          | Extend `ClaimType` enum + add label handling in assembly   |
| New framework profile   | Add entry to `_AGENTIC_FRAMEWORKS` in assembly engine      |
| New comparison dimension| Add to `_COMPARISON_DIMENSIONS` and update framework dicts |

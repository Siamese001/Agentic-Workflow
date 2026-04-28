# TECHNICAL SPEC — apps_rfp: AI Proposal / RFP Generator

## Module Map

```
apps_rfp/
├── config/
│   └── agent_spec_config.py    # RfpAgentSpecs, load_rfp_specs()
├── engines/
│   └── proposal_assembly_engine.py  # ProposalAssemblyEngine: sections, roadmap, risks
├── reasoning/
│   └── RfpOrchestrator.py      # RfpOrchestrator: 4-hop pipeline
├── scripts/
│   └── run_rfp.py              # CLI entrypoint
├── types/
│   └── rfp_types.py            # ProposalStatus, RfpRequest, RfpResult, RfpRunSummary, ...
├── validators/
│   └── proposal_gate_validator.py  # ProposalGateValidator
└── __main__.py
```

---

## Key Classes and Contracts

### `RfpAgentSpecs` (Pydantic BaseModel)
- `sections: list[ProposalSectionConfig]` — ordered list with `required: bool`
- `industries: dict[str, IndustryProfileConfig]` — regulatory flags per industry
- `roadmap: RoadmapConfig` — `num_phases`, `require_governance_phase`
- `risk_register: dict[str, list[RiskItem]]` — industry-keyed risk seed list
- `gate: ProposalGateConfig` — min quality score, required section IDs

### `ProposalAssemblyEngine`
Assembles a complete proposal from `RfpRequest`.
```python
@dataclass
class AssemblyResult:
    sections: list[ProposalSection]
    roadmap: list[RoadmapPhase]
    risks: list[RiskItem]
    assumptions: list[AssumptionItem]
```

**Section assembly is template-driven:**
- Each `ProposalSectionConfig` maps to a builder function
- Builders receive `(problem_statement, industry_profile, posture)` → `ProposalSection`
- No LLM calls; all content is parameterized template expansion

**Roadmap build:**
- Always 5 phases: `Discover → Architect → Pilot → Scale → Govern`
- Phase durations are configurable; Govern phase is always last
- `require_governance_phase=True` means the gate checks for it

**Risk matrix:**
- Seeded from `industry_profile.regulatory_flags` → each flag maps to a risk item
- Minimum 3 risks always present (platform, data, governance defaults)

### `RfpOrchestrator` (dataclass)
```python
@dataclass
class RfpOrchestrator:
    dry_run: bool = False
    output_dir: str = "artifacts/rfp"
    gate_mode: str = "HARD_FAIL"
    hop_checkpoints: list[dict] = field(default_factory=list)

    def run(self, request: RfpRequest) -> RfpResult: ...
```
**Hops:**
1. `HOP-1-PARSE` → Extract problem statement, industry, constraints
2. `HOP-2-ASSEMBLE` → `ProposalAssemblyEngine.execute(request)`
3. `HOP-3-GATE` → `ProposalGateValidator.validate(sections, roadmap, risks)`
4. `HOP-4-EMIT` → Write artifacts + run summary

---

## Data Flow

```
RfpRequest(problem_statement, industry, posture, timeline_weeks, dry_run)
    │
    ▼
ProposalAssemblyEngine → AssemblyResult(sections, roadmap, risks, assumptions)
    │
    ▼
ProposalGateValidator → ProposalGateResult(passed, violations, quality_score)
    │
    ▼  (if passed or WARN-only)
Artifact Emission → [proposal_*.md, proposal_manifest_*.json, run_summary_*.json]
    │
    ▼
RfpResult(trace_id, status, sections, roadmap, risks, assumptions, artifact_paths, provenance)
```

---

## Provenance Contract

```python
provenance = {
    "trace_id": str,          # SHA256[:16] of industry + problem[:64]
    "industry": str,
    "posture": str,
    "app": "apps_rfp",
    "checkpoints": list[str]
}
```

---

## Risk Register Schema

Each `RiskItem`:
```python
@dataclass(frozen=True)
class RiskItem:
    risk_id: str        # RISK-NNN
    title: str
    severity: RiskSeverity  # HIGH / MEDIUM / LOW
    mitigation: str
    owner: str          # Platform Team / Client / Joint
    regulatory_flag: str = ""
```

All risk items have explicit `owner` and `mitigation`. No silent omissions.

---

## Dependency Surface

| Dependency    | Reason                         |
|---------------|--------------------------------|
| `pydantic`    | Config schemas                 |
| `hashlib`     | Trace ID                       |
| `pathlib`     | File operations                |
| `json`        | Manifests + run summary        |
| `logging`     | Structured logging             |

No external API calls. No LLM dependencies.

---

## Extension Points

| Point                   | How to extend                                              |
|-------------------------|------------------------------------------------------------|
| New industry            | Add entry to `RfpAgentSpecs.industries` in config JSON    |
| New proposal section    | Add `ProposalSectionConfig` to `sections` list            |
| New roadmap phase       | Override `RoadmapConfig.phase_names`                      |
| New risk item           | Add to `risk_register[industry]` in config JSON           |

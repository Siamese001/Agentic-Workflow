# TECHNICAL SPEC — apps_exec: Executive Brief Generator

## Module Map

```
apps_exec/
├── config/
│   ├── agent_spec_config.py   # Pydantic root config: ExecAgentSpecs, load_exec_specs()
│   └── reasoning_toggles_config.py  # Feature flags (frozen dataclass)
├── engines/
│   ├── base_exec_engine.py    # Abstract base: logging, dry-run, provenance
│   ├── ingestion_engine.py    # IngestionEngine: reads source dirs, yields IngestedDocument
│   ├── capability_extraction_engine.py  # CapabilityExtractionEngine: regex extraction
│   └── brief_assembly_engine.py         # BriefAssemblyEngine: deterministic skeleton
├── reasoning/
│   └── ExecOrchestrator.py    # ExecOrchestrator: hop pipeline, artifact emission
├── scripts/
│   └── run_exec.py            # CLI entrypoint (argparse)
├── types/
│   └── exec_types.py          # AudiencePersona, BriefSection, ExecBriefResult, RunSummary
├── validators/
│   └── style_gate_validator.py # StyleGateValidator: buzzword density, evidence anchors
└── __main__.py                 # ADG bootstrap + calls run_exec.main()
```

---

## Key Classes and Contracts

### `ExecAgentSpecs` (Pydantic BaseModel)
- `personas: dict[str, AudiencePersonaConfig]` — at least 4 required (enforced by validator)
- `ingestion: IngestionConfig` — allowed extensions, max file size
- `gate: StyleGateConfig` — thresholds for all style gate checks
- `output: OutputConfig` — output directory, prefix, dry_run flag
- Loaded by `load_exec_specs(spec_path=None)` with a module-level `_SPEC_CACHE`

### `ExecOrchestrator` (dataclass)
```python
@dataclass
class ExecOrchestrator:
    dry_run: bool = False
    output_dir: str = "reports/executive"
    gate_mode: str = "HARD_FAIL"
    hop_checkpoints: list[dict] = field(default_factory=list)

    def run(self, request: ExecBriefRequest) -> ExecBriefResult: ...
```
**Hops:**
1. `HOP-1-INGEST` → `IngestionEngine.execute(request)`
2. `HOP-2-EXTRACT` → `CapabilityExtractionEngine.execute(ingestion_result)`
3. `HOP-3-ASSEMBLE` → `BriefAssemblyEngine.execute((request, extraction_result))`
4. `HOP-4-GATE` → `StyleGateValidator.validate_sections(sections)`
5. `HOP-5-EMIT` → Write artifacts + run summary

### `BriefAssemblyEngine`
- One `_SECTION_BUILDERS` dict mapping `AudiencePersona → list[SectionBuilder]`
- Each builder is a pure function: `(request, extraction_result) → BriefSection`
- Evidence anchors injected deterministically from extraction result

### `StyleGateValidator`
- `_BUZZWORDS: frozenset[str]` — static list (never configurable via LLM)
- `_UNSUPPORTED_CLAIM_PATTERNS: tuple[re.Pattern]` — compiled at import time
- Returns `StyleGateResult(passed, violations, quality_score, sections_checked)`

---

## Data Flow

```
ExecBriefRequest
    │
    ▼
IngestionEngine → IngestionResult(documents, skipped_paths, total_chars)
    │
    ▼
CapabilityExtractionEngine → ExtractionResult(capabilities, evidence_anchors, source_coverage)
    │
    ▼
BriefAssemblyEngine → AssemblyResult(sections: list[BriefSection])
    │
    ▼
StyleGateValidator → StyleGateResult(passed, violations, quality_score)
    │
    ▼  (if passed or WARN-only)
Artifact Emission → [exec_brief_*.md, run_summary_*.json]
    │
    ▼
ExecBriefResult(trace_id, status, sections, artifact_paths, provenance, run_summary_path)
```

---

## Provenance Contract

Every `ExecBriefResult` carries:
```python
provenance = {
    "trace_id": str,          # SHA256[:16] of audience + timestamp
    "audience": str,
    "app": "apps_exec",
    "checkpoints": list[str]  # HOP IDs completed
}
```
Provenance is written into `run_summary.json` at `provenance` key.
Provenance is deterministic for a given input (same topic + audience → same trace_id if `--trace-id` specified).

---

## Dependency Surface

| Dependency           | Import Path                                     | Reason                           |
|----------------------|-------------------------------------------------|----------------------------------|
| `pydantic`           | `pydantic.BaseModel`, `pydantic.Field`          | Config schemas                   |
| `re`                 | stdlib                                          | Regex pattern extraction         |
| `hashlib`            | stdlib                                          | Trace ID generation              |
| `pathlib`            | stdlib                                          | File system operations           |
| `json`               | stdlib                                          | Run summary serialization        |
| `logging`            | stdlib                                          | Structured logging               |
| `agentic_core` (opt) | `adg.applications.execute_ssot_integration`     | ADG bootstrap (graceful fallback)|

No external API calls. No LLM dependencies.

---

## Configuration Override

`load_exec_specs(spec_path)` looks for `config/exec_agent_specs.json` adjacent to the module.
If absent or unparseable, defaults are returned from in-memory Pydantic defaults.
A `_SPEC_CACHE` module-level variable prevents re-loading within the same process.

---

## Extension Points

| Point                    | How to extend                                              |
|--------------------------|------------------------------------------------------------|
| New persona              | Add entry to `ExecAgentSpecs.personas` in config JSON     |
| New extraction pattern   | Add to `CapabilityExtractionEngine._PATTERNS`             |
| New style gate           | Add rule to `StyleGateValidator` + `StyleGateConfig`      |
| New output format        | Add emitter method to `ExecOrchestrator._emit_artifacts`  |

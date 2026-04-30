# apps_qna — TECHNICAL_SPEC

## Contract

`apps_qna` is a deterministic, offline builder + linter. It has three
boundaries:

1. **Inputs** — typed pydantic models loaded from YAML / markdown / artifacts
   produced by other apps_*.
2. **Templates** — 18 Jinja2 templates rendered under `StrictUndefined`.
3. **Outputs** — a directory of numbered markdown card files plus a
   `pack_manifest.json` describing the pack.

No network calls. No subprocess calls except via the standard CLI argparse
entrypoint. No mutation of inputs.

## Types (apps_qna/types/qna_types.py)

All models are `pydantic.BaseModel` subclasses with `model_config = ConfigDict(frozen=True, extra="forbid")`.

### Top-level

```python
class Interview(BaseModel):
    slug: str                    # e.g. "drew-clements"
    company: Company
    role: Role
    interviewers: list[Interviewer]
    jd: JobDescription
    experience: ExperienceLibrary
    research: ResearchInputs | None = None
    build_metadata: BuildMetadata
```

### Interviewer

```python
class Interviewer(BaseModel):
    name: str
    title: str
    team: str
    public_signals: list[str]    # quoted statements / talks / blog posts
    technical_depth: Literal["low", "medium", "high"]
    hot_buttons: list[str]       # topics they probe
    lens: str                    # one-line executive bias
```

### Company / Role / JD

```python
class Company(BaseModel):
    name: str
    division: str | None = None
    practice: str | None = None
    anchors: list[str]           # vocabulary the runtime should use
    avoid_phrases: list[str]     # things never to say
    overlay_facts: list[str]     # company-specific decisioning facts


class Role(BaseModel):
    title: str
    level: str                   # IC / Manager / Director / VP / SVP
    primary_mandate: str         # one sentence
    success_criteria: list[str]


class JobDescription(BaseModel):
    raw_path: Path | None = None
    sections: list[JDSection]


class JDSection(BaseModel):
    heading: str
    body: str
    extracted_keywords: list[str]
```

### Experience / Story Bank

```python
class ExperiencePoint(BaseModel):
    title: str
    one_liner: str
    technical_depth_tags: list[str]


class StoryBank(BaseModel):
    stories: list[Story]


class Story(BaseModel):
    name: str                    # e.g. "ConstitutionalGovernance"
    situation: str
    task: str
    action: str
    result: str
    lesson: str
    tags: list[str]              # for proof-router selection


class ExperienceLibrary(BaseModel):
    points: list[ExperiencePoint]
    star_bank: StoryBank
    rca_bank: list[RCAStory]


class RCAStory(BaseModel):
    name: str
    situation: str
    task: str
    root_cause: str
    action: str
    result: str
    operating_model_change: str
```

### Research inputs

```python
class ResearchInputs(BaseModel):
    company_brief: str | None = None
    role_areas_of_focus: list[str] = []
    industry_trends: list[str] = []
    interviewer_lenses: dict[str, str] = {}   # keyed by interviewer name
    source_register: list[ResearchClaim] = []


class ResearchClaim(BaseModel):
    claim: str
    claim_type: Literal["direct_evidence", "interpretation", "analyst_inference", "assumption"]
    source_id: str
    section_id: str
```

### Build metadata

```python
class BuildMetadata(BaseModel):
    interview_slug: str
    built_at: datetime
    builder_version: str
    template_set_version: str
    output_dir: Path
```

## Route Registry (apps_qna/config/route_registry.yaml)

YAML SSOT for the 9 primary routes from the routing manifest. Every entry has:

```yaml
routes:
  - id: executive_fit
    number: 1
    name: "Executive fit"
    triggers:
      - "Why Dentsu?"
      - "Why this role?"
      - "Why you?"
    answer_shape:
      - "One-sentence fit thesis."
      - "Two to three proof points."
      - "Company-specific close."
    primary_card: "13_EXECUTIVE_FIT.md"
    optional_specialists:
      - "03_INTERVIEWER_LENS.md"
      - "04_COMPANY_OVERLAY.md"
```

The linter consumes this YAML to validate emitted packs.

## Builder Contract (apps_qna/builder/card_pack_builder.py)

```python
class CardPackBuilder:
    def __init__(self, config: QnaBuildConfig): ...

    def build(self, interview: Interview, output_dir: Path) -> CardPackManifest:
        """Render all templates, write numbered files, return manifest.

        Side effects: writes `<NN>_<SLUG>.md` files into `output_dir` and one
        `pack_manifest.json`.

        Raises:
            jinja2.UndefinedError: a template referenced an unset variable.
            ValueError: the interview was missing required cards' data.
        """
```

Filename convention: `<NN>_<UPPER_SLUG>.md` where NN is `00`–`17`.

For multi-interviewer mode, card 03 is split:
`03A_INTERVIEWER_LENS_<NAME>.md`, `03B_INTERVIEWER_LENS_<NAME>.md`, etc.

## Linter Invariants (apps_qna/validators/)

| ID | Invariant | Validator |
|---|---|---|
| LINT-1 | Each route has exactly one primary card | `route_purity.py` |
| LINT-2 | No route loads >2 specialist cards | `context_budget.py` |
| LINT-3 | Max-context rule: no answer route loads >3 cards total | `context_budget.py` |
| LINT-4 | All 9 routes have a primary card present in the pack | `route_coverage.py` |
| LINT-5 | No orphan card (every emitted card is referenced) | `route_coverage.py` |
| LINT-6 | Always-on header (LIVE VERBAL-FIRST OVERWRITE block) is byte-identical across cards 00–17 | `header_consistency.py` |

Each validator returns a `LintResult` with `errors: list[LintError]` and exits
non-zero if any errors are present.

## Templates (apps_qna/templates/)

18 `.md.j2` files. All templates open with the canonical
`{% include "_always_on_header.md.j2" %}` partial — that's how LINT-6 stays
true.

Template variables come from the typed `Interview` model. Strict undefined
mode means a missing variable is an error, not a blank.

## Adapters (apps_qna/integrations/)

Three thin functions:

```python
def from_apps_research(brief_path: Path, register_path: Path) -> ResearchInputs: ...
def from_apps_rg(reports_dir: Path) -> ExperienceLibrary: ...
def from_apps_exec(exec_brief_path: Path) -> str: ...   # returns ExecutiveFit text
```

Each is read-only against the source app's artifacts. No coupling at import
time — adapters are lazy-loaded by the CLI when the matching `--from-*` flag
is present.

## CLI (apps_qna/scripts/run_qna.py)

argparse entrypoint, two modes:

- **Build mode** (default): `python -m apps_qna --interview ... --output ...`
- **Lint mode**: `python -m apps_qna lint <pack-dir>`

Exit codes:

- `0` — success
- `1` — lint failure / build invariant violation
- `2` — input error (file missing, schema mismatch)

## What this module does NOT do

- Call ChatGPT / OpenAI / any LLM API.
- Run any kind of agent at runtime.
- Touch UWG, L5, or any agentic_core governance plane.
- Mutate the source apps_research / apps_rg / apps_exec artifacts.
- Cache or persist anything outside the `--output` directory and a JSON
  `pack_manifest.json`.

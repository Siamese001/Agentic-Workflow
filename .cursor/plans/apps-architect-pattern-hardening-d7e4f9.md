---
plan_id: apps-architect-pattern-hardening-d7e4f9
plan_type: infra    # New app with governance/auditing function
---

# apps_architect — Pattern Collection & Repo Hardening Engine

Build an app that continuously collects best-in-class methodologies and genetic architecture patterns from recent development, computes delta from current repo state, and emits hardening rules with automatic README synchronization to GitHub.

---

## Context (SCQA)

- **Situation** — Over the last month, 250+ plans landed establishing canonical patterns: agentic spine manifests, FEC producers, eval harness wiring, C0 retrieval patterns, and prompt assembly best practices. These patterns exist in scattered plan files, ADG snapshots, and rule definitions, but are not systematically harvested or enforced.

- **Complication** — Without automated pattern detection and hardening, repos drift from established best practices. Manual README updates lag weeks behind pattern changes. New apps lack a single source for "how we build things now" — they copy-paste from outdated templates.

- **Question** — How do we build an app that continuously observes recent methodological evolution, computes drift from current repo patterns, and emits actionable hardening guidance with automatic documentation sync?

- **Answer** — apps_architect: an R3_grounded_read app that scans recent plans/ADG/rules (C0 over `.cursor/plans/` + `agentic_core/` patterns), computes delta via ADG layer violation detection, generates hardening rule recommendations, and publishes findings to a living README with GitHub API integration.

---

## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| `.cursor/plans/` (last 30 days) | Recent methodological evolution | 🔲 |
| ADG `mv_hotspot_centrality` + `v_p0_*` views | Pattern violations & hotspots | 🔲 |
| `agentic_core/` layer contracts | Genetic architecture patterns | 🔲 |
| `apps_*/spine_manifest.yaml` | App spine patterns | 🔲 |
| GitHub API | README sync target | 🔲 |

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-------------|-------|-------------|-------------|--------|------------------|
| W1 | 1.1-1.3 | Spine & C0 wiring, FEC producer | ~8K | ADG healthy, C0 collection exists | ✅ DONE | Manifest + __main__.py skeleton, cert wired |
| W2 | 2.1-2.4 | Pattern scanner engine, ADG queries | ~10K | ADG MVs available | ✅ DONE | Pattern extraction from plans/rules/core |
| W3 | 3.1-3.3 | Delta computation, hardening rule generator | ~8K | Pattern schema defined | ✅ DONE | Delta report + rule emission working |
| W4 | 4.1-4.3 | GitHub README sync, CLI interface | ~6K | GitHub token available | ✅ DONE | Auto-PR on pattern drift detected |
| W5 | 5.1-5.2 | Observability, L6 evaluation wireup | ~5K | OTEL healthy | ✅ DONE | Exit v6 integration, eval harness registered |

**Total: ~37K tokens across 5 waves**

---

## Out Of Scope

- ❌ Real-time webhook triggers (poll-based only)
- ❌ Automatic rule enforcement (emit-only; human Author-Gate for applies)
- ❌ Multi-repo pattern federation (single-repo scope)
- ❌ Historical pattern archaeology (last 30 days only)
- ❌ Pattern migration execution (detection + recommendation only)

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| 1.1 | Spine manifest + route claim | spine_manifest.yaml | Route type selection | ~2K | ✅ DONE |
| 1.2 | __main__.py entrypoint + FEC | __main__.py, cert/ | Cert wiring pattern | ~3K | ✅ DONE |
| 1.3 | C0 retrieval profile | config/domain_contract/ | Collection definition | ~3K | ✅ DONE |
| 2.1 | ADG pattern scanner base | engines/pattern_scanner.py | ADG MCP integration | ~3K | ✅ DONE |
| 2.2 | Plan file pattern extractor | engines/plan_pattern_engine.py | YAML frontmatter parse | ~3K | ✅ DONE |
| 2.3 | Rule pattern extractor | engines/rule_pattern_engine.py | Markdown rule parsing | ~2K | ✅ DONE |
| 2.4 | Core layer pattern detector | engines/core_pattern_engine.py | Layer violation queries | ~2K | ✅ DONE |
| 3.1 | Pattern schema definition | types/architect_types.py | Schema versioning | ~2K | ✅ DONE |
| 3.2 | Delta computation engine | engines/delta_engine.py | Diff against current | ~3K | ✅ DONE |
| 3.3 | Hardening rule generator | engines/rule_generator.py | Rule emission format | ~3K | ✅ DONE |
| 4.1 | README template system | templates/readme_template.md | Section modularity | ~2K | ✅ DONE |
| 4.2 | GitHub API integration | integrations/github_sync.py | PR creation | ~2K | ✅ DONE |
| 4.3 | CLI interface | cli/architect_cli.py | argparse, dry-run | ~2K | ✅ DONE |
| 5.1 | OTEL observability | L6_observability/ | Span emission | ~2K | ✅ DONE |
| 5.2 | Exit v6 + eval harness | Exit wiring, rubrics | Cert route registry | ~3K | ✅ DONE |

**Status legend**: 🔲 TODO · 🔄 IN PROGRESS · ✅ DONE · ❌ BLOCKED

---

## Gap Register

**GAP-1: C0 collection scope definition**
- Need to define exact C0 collections for `.cursor/plans/`, `agentic_core/`, and rules
- Impact: Blocks W1 C0 retrieval profile completion

**GAP-2: Pattern schema versioning**
- Patterns evolve; need schema_version field in emitted hardening rules
- Impact: W3 rule generator must support backward compatibility

**GAP-3: GitHub token security**
- Need secure storage for GitHub API token (env var vs L4 secret)
- Impact: W4 GitHub integration security posture

---

## Execution Plan

### Phase 1.1 — Spine Manifest & Route Claim
**Scope**: Declare R3_grounded_read route with C0-required over patterns collections

**Files**:
- `apps_architect/spine_manifest.yaml`

**Key content**:
```yaml
schema_version: 1
app: apps_architect
claimed_routes:
  - type: R3_grounded_read
    description: >-
      Pattern collection and delta analysis over recent methodology.
      Scans .cursor/plans/, agentic_core/, and .cursor/rules/
      via C0 retrieval to extract canonical patterns, computes drift
      from current repo state, emits hardening rules.
    c0_required: true
    pa_required: true
    source_collection: architect_pattern_docs
    notes:
      - "C0 mandatory — patterns are grounded in actual recent plans/rules"
      - "No CommitRequest — output is documentation + recommendations"
```

**Acceptance**: Manifest validated by `apps_spine_coverage.py` scanner

---

### Phase 1.2 — Entrypoint + FEC Wiring
**Scope**: Canonical __main__.py with cert/FEC pattern matching apps_research

**Files**:
- `apps_architect/__main__.py`
- `apps_architect/cert/__init__.py`
- `apps_architect/cert/fec_producer.py`

**Pattern**: Copy from `apps_research/cert/fec_producer.py` with:
- `producer: apps_architect`
- `grounded: true` (when C0 retrieval sources populate)
- `retrieval_sources: ["plans", "rules", "core_patterns"]`

**Acceptance**: `resolve_fec("apps_architect", run_ctx)` returns valid FEC

---

### Phase 1.3 — C0 Retrieval Profile
**Scope**: Define domain contract for pattern document retrieval

**Files**:
- `apps_architect/config/domain_contract/retrieval_profile.yaml`
- `apps_architect/config/domain_contract/input_contract.yaml`

**Key specs**:
- Input: `PatternScanRequest` with `scan_depth_days` (default 30)
- Output: `PatternCollection` with categorized pattern objects
- Collections: `plans_recent`, `rules_active`, `core_layer_contracts`

**Acceptance**: C0 retrieval returns structured pattern docs

---

### Phase 2.1 — ADG Pattern Scanner Base
**Scope**: Generic ADG query wrapper with caching

**Files**:
- `apps_architect/engines/pattern_scanner.py`
- `apps_architect/engines/adg_client.py`

**Capabilities**:
- `adg_mv_hotspot_centrality(limit=50)` → structural patterns
- `adg_p_view_query(view_name="v_p0_critical_layer_breaks")` → violations
- `adg_nodes_by_layer(layer="L0")` → layer contract patterns

**Acceptance**: Scanner returns typed pattern objects

---

### Phase 2.2 — Plan File Pattern Extractor
**Scope**: Parse `.cursor/plans/*.md` for methodological patterns

**Files**:
- `apps_architect/engines/plan_pattern_engine.py`

**Extraction targets**:
- Wave structure patterns (how many waves, phase density)
- ADG evidence patterns (`adg_mv_*` usage)
- FEC wiring patterns (cert producer shape)
- Exit v6 patterns (L6 observability wiring)

**Acceptance**: Extracts ≥5 pattern types from recent plans

---

### Phase 2.3 — Rule Pattern Extractor
**Scope**: Parse `.cursor/rules/*.md` for hardening patterns

**Files**:
- `apps_architect/engines/rule_pattern_engine.py`

**Extraction targets**:
- Always-on rule patterns (trigger: always_on)
- Conditional rule patterns (trigger: model_decision)
- Skill patterns (MCP usage patterns)
- Enforcement hooks (pre_*, post_*)

**Acceptance**: Rule taxonomy classified

---

### Phase 2.4 — Core Layer Pattern Detector
**Scope**: Query ADG for genetic architecture patterns in agentic_core

**Files**:
- `apps_architect/engines/core_pattern_engine.py`

**Detection targets**:
- Layer separation patterns (L0-L6 imports)
- Contract patterns (dataclass + frozen=True)
- Routing patterns (RouteContract shapes)
- Exit patterns (X3 disposition handling)

**Acceptance**: Layer violation patterns identified

---

### Phase 3.1 — Pattern Schema Definition
**Scope**: Typed pattern representation

**Files**:
- `apps_architect/types/architect_types.py`

**Schema**:
```python
@dataclass(frozen=True)
class Pattern:
    pattern_id: str  # hash of source + content
    pattern_type: PatternType  # PLAN, RULE, CORE, LAYER
    source_ref: str  # file path or ADG node id
    content_digest: str  # SHA256 of canonical form
    first_seen: datetime
    last_seen: datetime
    schema_version: str = "1.0"

class PatternCollection:
    patterns: Tuple[Pattern, ...]
    collection_digest: str
```

**Acceptance**: Patterns are hashable, comparable, serializable

---

### Phase 3.2 — Delta Computation Engine
**Scope**: Compare current patterns against repo reality

**Files**:
- `apps_architect/engines/delta_engine.py`

**Delta types**:
- `NEW_PATTERN` — pattern not yet adopted in target
- `STALE_PATTERN` — pattern in use but superseded
- `MISSING_PATTERN` — canonical pattern not found
- `DRIFT_DETECTED` — pattern found but modified

**Acceptance**: Delta report shows actionable drift

---

### Phase 3.3 — Hardening Rule Generator
**Scope**: Emit hardening rules from delta analysis

**Files**:
- `apps_architect/engines/rule_generator.py`
- `apps_architect/templates/hardening_rule.md`

**Output format**:
```markdown
---
rule_id: architect-<pattern_hash>-<6hex>
pattern_source: <plan/rule/core reference>
delta_type: NEW_PATTERN | STALE_PATTERN | MISSING_PATTERN | DRIFT_DETECTED
severity: advisory | recommended | required
applies_to: [file patterns]
---

## Detection
[How this was identified]

## Current State
[What exists]

## Recommended Pattern
[Canonical pattern to adopt]

## Migration Path
[Steps to apply]
```

**Acceptance**: Rules are actionable, referenced, prioritized

---

### Phase 4.1 — README Template System
**Scope**: Modular README sections that update independently

**Files**:
- `apps_architect/templates/readme_template.md`
- `apps_architect/engines/readme_assembler.py`

**Sections**:
- Executive summary (auto-generated)
- Pattern catalog (auto-updated)
- Delta summary (last scan results)
- Hardening backlog (outstanding recommendations)
- Methodology changelog (pattern evolution)

**Acceptance**: README sections assemble deterministically

---

### Phase 4.2 — GitHub API Integration
**Scope**: README sync via PR creation

**Files**:
- `apps_architect/integrations/github_sync.py`

**Flow**:
1. Detect README drift
2. Create feature branch `architect/update-<timestamp>`
3. Commit README update
4. Open PR with delta summary
5. Link to hardening rules

**Acceptance**: PR created with meaningful diff

---

### Phase 4.3 — CLI Interface
**Scope**: User-facing command interface

**Files**:
- `apps_architect/cli/architect_cli.py`

**Commands**:
```bash
python -m apps_architect scan --days 30 --output json
python -m apps_architect delta --against ref/patterns.json
python -m apps_architect rules --severity recommended
python -m apps_architect readme --sync --dry-run
python -m apps_architect readme --sync --pr
```

**Acceptance**: All commands work, --dry-run safe

---

### Phase 5.1 — OTEL Observability
**Scope**: L6 span emission for pattern operations

**Files**:
- `apps_architect/L6_observability/__init__.py`
- `apps_architect/L6_observability/span_emitters.py`

**Spans**:
- `architect.scan` — pattern collection
- `architect.delta` — drift computation
- `architect.rules` — rule generation
- `architect.sync` — GitHub sync

**Acceptance**: Spans visible in OTEL collector

---

### Phase 5.2 — Exit v6 + Eval Harness
**Scope**: Certification entry and eval wiring

**Files**:
- `apps_architect/config/cert_route_registry.yaml`
- `apps_architect/config/domain_contract/eval_rubrics.yaml`
- `apps_architect/config/domain_contract/threshold_profiles.yaml`

**Rubrics**:
- Pattern extraction accuracy
- Delta precision (false positive rate)
- Rule usefulness (human judgment)
- Sync success rate

**Acceptance**: Eval harness runs, Exit v6 produces disposition

---

## Rules

1. **Pattern immutability** — Once a pattern is identified, its canonical form never changes; new versions get new pattern_ids
2. **Delta determinism** — Same codebase state always produces same delta (no timestamps in hash inputs)
3. **Fail-soft on ADG** — If ADG MCP unavailable, degrade to file scanning with warning
4. **Human gate for required rules** — Severity=required rules require Author-Gate approval before auto-PR
5. **Read-only on repo** — Never modifies source files directly; only emits recommendations and README updates

---

## Success Criteria

- [ ] W1: apps_architect skeleton exists, cert/FEC wired, C0 retrieval configured
- [ ] W2: Pattern scanners extract ≥20 distinct patterns from recent plans/rules/core
- [ ] W3: Delta computation identifies ≥5 actionable hardening opportunities
- [ ] W4: GitHub PR auto-created with README update on drift detection
- [ ] W5: Exit v6 integration complete, eval harness registered, OTEL spans emitted
- [ ] End-to-end: `python -m apps_architect scan` → delta report → rules generated in <30s

---

## Implementation Commands

```bash
# W1: Bootstrap app structure
mkdir -p apps_architect/{config/{domain_contract,specs},engines,types,cert,cli,L6_observability,integrations,templates}
touch apps_architect/__init__.py

# W2-W3: Pattern extraction test
cd apps_architect && python -m pytest tests/test_pattern_extraction.py -v

# W4: GitHub sync dry run
python -m apps_architect readme --sync --dry-run

# W5: Eval harness
python ops_scripts/ci/check_app_domain_harness_parity.py --app apps_architect
```

---

## Rollback Strategy

If pattern detection is too noisy:
1. Increase `scan_depth_days` threshold (reduce sensitivity)
2. Add exclusion patterns for noisy file types
3. Degrade severity levels (required → recommended)
4. Disable auto-PR, switch to manual review queue

---

## Acceptance Criteria

| Metric | Target | Verification |
|---|---|---|
| Pattern extraction coverage | ≥90% of recent plans | Unit test over sample plans |
| Delta false positive rate | <5% | Manual audit of 20 samples |
| Rule generation latency | <5s per pattern | Benchmark in CI |
| End-to-end scan latency | <30s for 30-day window | Integration test |
| README sync success rate | >95% | OTEL span metrics |

---

## Cursor Agent Alignment Checks

- Leverages ADG graph-layer primitives (mv_hotspot_centrality, v_p views) per §22
- C0 retrieval over structured collections per R3_grounded_read pattern
- FEC producer follows established pattern from apps_research/apps_rfp
- Exit v6 integration matches eval harness parity requirement
- GitHub integration uses fail-soft pattern with dry-run gate

---

## References

- `apps_research/` — Canonical R3_grounded_read reference implementation
- `apps_repo_brief/spine_manifest.yaml` — R3_grounded_read route declaration
- `.cursor/rules/adg-graph-layer-enforcement.md` — Graph-layer evidence requirements
- `docs/reference/APP_OVERLAY_VS_CORE_ONLY_RUNTIME.md` — Route taxonomy
- `apps-eval-harness-parity-f8d4a2` — Eval harness wiring pattern

PLAN_CREATED: plan=apps-architect-pattern-hardening-d7e4f9 slug=apps-architect-pattern-hardening-d7e4f9 waves=5

---
plan_id: agent-capability-spine-harvest-e8f4a2
plan_type: governance
touches_agentic_core: true
touches_governance_ci: true
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: true
author_gate_receipt_ref: ""
dod_exempt: false
parent_plan: agent-inventory-spine-taxonomy-b4e9f2
parent_plan_status: Completed
sibling_plan: agent-inventory-deferred-followup-c2a8f1
plan_format_version: harvest-hardened-v3
---

# Agent Capability Spine Harvest

Harvest reusable capabilities from 118 inventory `*Agent` classes into **engines, profiles, judge panel adapters, and CI** — without remounting agent classes on the product spine. Grounded in ADR-088, W3 live proof (`ARTIFACT_PROVEN=0`), and import-closure trace (**0/118** spine agents).

> **plan_id discipline:** `plan=agent-capability-spine-harvest-e8f4a2`

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: Not Started
CURRENT_WAVE: W0.5
LAST_COMPLETED_WAVE: W0
LAST_UPDATED: 2026-05-25
PARENT_PLAN: agent-inventory-spine-taxonomy-b4e9f2
DECISION_MODEL: docs/reports/cursor/agent_capability_decision_model.md
MATRIX_SSOT: docs/reports/cursor/agent_capability_decision_matrix.json
AUTHOR_GATE_RECEIPT_SSOT: docs/reports/cursor/agent_capability_harvest_author_gate_receipt.md

PLAN_CREATED: slug=agent-capability-spine-harvest-e8f4a2 path=.cursor/plans/agent-capability-spine-harvest-e8f4a2.md status=Not Started notion_page=36b27693-f55c-8175-b7ee-c1042f686bdf

NOTION_PAGE_ID: 36b27693-f55c-8175-b7ee-c1042f686bdf
NOTION_PLAN_URL: https://www.notion.so/agent-capability-spine-harvest-e8f4a2-36b27693f55c8175b7eec1042f686bdf

**Blocked until populated:** `author_gate_receipt_ref` in YAML frontmatter MUST equal `AUTHOR_GATE_RECEIPT_SSOT` path after W0.5 PASS.

---

## GLOBAL HARVEST LAW

Harvest means **copying** reusable policy/logic into non-agent engines, profiles, adapters, or CI checks. Harvest does **not** permit runtime importing, subclassing, wrapping, instantiating, dynamically loading, or remounting any inventory `*Agent` class onto the product spine.

| Rule | Requirement |
|------|-------------|
| **Core edit gate** | No files under `agentic_core/**` may change until `author_gate_receipt_ref` is populated (W0.5 PASS). |
| **Source quarantine** | Extracted code lives in non-agent functions/profiles/adapters with **no runtime import** from source `*Agent` modules. Source classes may appear only in static analysis, migration notes, or archive receipts. |
| **L0/C0 separation** | L0 harvest must not retrieve, score final evidence, or assemble prompts. C0 harvest must not route, answer, or create prompt instructions. |
| **Contract discipline** | Every new core surface requires a minimal contract note (producer/consumer stage, authority scope, runtime vs CI, policy_hash/registry expectations if runtime-bound, **no authority widening** assertion). |
| **Proof tiers** | Static/grep proof ≠ runtime proof ≠ release eligibility. Each wave receipt states what is claimed and **NON_CLAIMS**. |
| **Author-gate fallback** | If Author-Gate is unavailable, W1 may proceed **only** for ADR/docs/archive/matrix work **outside** `agentic_core/**`. |
| **W1 archive-first** | Tier D default = archive/deprecate; physical delete only after W5 closeout **or** separate `deletion_strategy` Author-Gate receipt. Archive ≠ product removal until importer scans + W5 non-use proof pass. |

---

## Harvest grep proof set (class + module stem)

Use **in addition to** `.*Agent` import-syntax patterns. Fail if any match is a **runtime** import/load in `agentic_core/**` or `apps_rg/**` (exclude archive receipts, migration notes, static tooling paths declared in receipt).

**Tier A (W2-L0, W2-C0, W5):**

```bash
rg -n "SemanticGatekeeperAgent|AutonomyGuardianAgent|SSOTFolderCleanupAgent|EmbeddingSovereignAgent|SovereignRAGManager|RedisSovereignAgent" agentic_core apps_rg
rg -n "semantic_gatekeeper|autonomy_guardian|ssot_folder_cleanup|embedding_sovereign|sovereign_rag|redis_sovereign" agentic_core apps_rg
rg -n "from .*Agent import|import .*Agent" agentic_core apps_rg
rg -n "importlib\.import_module|importlib|getattr.*Agent" agentic_core apps_rg
```

**W3 judge pilot candidates (per selected adapters — add class + stem for each):**

```bash
# Example after adapter pick; extend with module stems from matrix row module_path
rg -n "<JudgeClassName>|<judge_module_stem>" agentic_core/runtime/judges agentic_core apps_rg
```

**W4 FCA cluster (when W4 runs):**

```bash
rg -n "FileClassificationAgent|FileClassificationHealerAgent|file_classification" agentic_core apps_rg
```

Receipt must list exact `rg` commands run and pass/fail per pattern group.

---

## Context (SCQA)

- **Situation** — Inventory closed: taxonomy on 118 agents, spine function canon, zero runtime agent proof.
- **Complication** — Many agents contain useful policy (L0 gates, C0 retrieval, judge rubrics, structure rules) buried in obsolete `*Agent` shells; FCA monolith is ~5.7k LOC off-spine.
- **Question** — How can capabilities enhance `agentic_core` and `apps_*` without violating spine laws?
- **Answer** — Decision model **P1–P9** + tiered harvest plan; default **extract or delete**, never "wire agent class to spine."

---

## Decision artifacts (W0 — completed)

| Artifact | Path |
|----------|------|
| Model | [agent_capability_decision_model.md](../docs/reports/cursor/agent_capability_decision_model.md) |
| Recommendations | [agent_capability_harvest_recommendations.md](../docs/reports/cursor/agent_capability_harvest_recommendations.md) |
| Matrix JSON | [agent_capability_decision_matrix.json](../docs/reports/cursor/agent_capability_decision_matrix.json) |
| Builder | [build_agent_capability_decision_matrix.py](../tools/governance/build_agent_capability_decision_matrix.py) |
| Index | [agent_capability_decision_model_index.md](../docs/reports/cursor/agent_capability_decision_model_index.md) |

Regenerate matrix: `python tools/governance/build_agent_capability_decision_matrix.py`

---

## Matrix snapshot (v1)

| Tier | Count | Primary patterns |
|------|------:|------------------|
| TIER_A_HARVEST_NOW | 6 | P2 (3), P3 (3) |
| TIER_B_APP_OPTIONAL | 20 | P5 (7), P6 (7), P4 (1), P2 (5) |
| TIER_C_CI_ONLY | 76 | P7 (66), P8 (10) |
| TIER_D_DELETE | 16 | P9 (13), P8 fat wrappers (3) |

**Tier A agents:** `SemanticGatekeeperAgent`, `AutonomyGuardianAgent`, `SSOTFolderCleanupAgent`, `EmbeddingSovereignAgent`, `SovereignRAGManager`, `RedisSovereignAgent`

---

## Waves

### Wave progress

| Wave | Focus | Status | `agentic_core/**` edits |
|------|-------|--------|-------------------------|
| W0 | Publish decision model + 118-row matrix | **Completed** (2026-05-25) | No |
| **W0.5** | **Core Author-Gate receipt (hard precondition)** | **Not Started** | **Blocked** |
| W1 | Tier D burndown + ADR-089 (non-core allowed if W0.5 open) | Not Started | Blocked until W0.5 PASS |
| W2-L0 | Tier A — L0 route-gate harvest only | Not Started | Requires W0.5 PASS |
| W2-C0 | Tier A — C0 profile/semantic-cache harvest only | Not Started | Requires W0.5 PASS + W2-L0 contract |
| W3 | Judge panel 2-adapter pilot (real provider) | Not Started | Requires W0.5 PASS |
| W4 | FCA parity → CI; monolith archive (parity-gated) | Not Started | Requires W0.5 PASS |
| W5 | Closeout: absence + non-use + matrix diff | Not Started | Requires W0.5 PASS |

**Execution order:** W0 → **W0.5 (mandatory)** → W1 (core-blocked subset if gate pending) → W2-L0 → W2-C0 → W3 → W4 → W5.

---

### W0 — Model publication (Completed)

**DoD**

- [x] Decision model doc with P1–P9 and mermaid flow
- [x] Matrix JSON for all 118 agents
- [x] Executive recommendations
- [x] Index + plan file on disk

**Receipt:** [agent_capability_spine_harvest_w0_receipt.md](../docs/reports/cursor/agent_capability_spine_harvest_w0_receipt.md)

---

### W0.5 — Core Author-Gate receipt (HARD PRECONDITION)

**Purpose:** Resolve core Author-Gate before any `agentic_core/**` modification. Empty `author_gate_receipt_ref` blocks W1 core work, all of W2, W3, W4, and W5 core touchpoints.

**Author-Gate triggers:** `architecture_choice`, `core_addition`, approved scope for P2/P3 extraction only.

**Approved scope (must appear verbatim in receipt):**

- P2/P3 extraction only (generic engines + profile extensions).
- **No** `*Agent` remount on product spine.
- **No** product-spine agent invocation (`ARTIFACT_PROVEN` must remain 0 for agent classes).
- **No** broadened L0/C0 authority (no L0 retrieval/scoring/prompt assembly; no C0 routing/answering/prompt instructions).

**Deliverables**

- [ ] Cursor Author-Gate packet + `DECISION_CAPTURED` line in session log
- [ ] Receipt file: [agent_capability_harvest_author_gate_receipt.md](../docs/reports/cursor/agent_capability_harvest_author_gate_receipt.md) containing:
  - `DECISION_CAPTURED: type=architecture_choice, repo_area=agentic_core, selected=<id>, outcome=executed`
  - Approved scope bullets (four bullets above)
  - Explicit **NON_CLAIMS:** no release eligibility, no integrated apps_rg green proof, no FCA delete approval
- [ ] Plan frontmatter `author_gate_receipt_ref` set to receipt path (exact value below)

**Frontmatter mechanical proof (required on W0.5 PASS)**

W0.5 closeout MUST include a diff proving YAML updated from empty to populated. Receipt attaches one of:

```bash
git diff -- .cursor/plans/agent-capability-spine-harvest-e8f4a2.md
```

**Required hunk (verbatim target after PASS):**

```yaml
author_gate_receipt_ref: "docs/reports/cursor/agent_capability_harvest_author_gate_receipt.md"
```

**Before state (must appear in diff as removed line):** `author_gate_receipt_ref: ""`

**Fail W0.5** if receipt exists on disk but plan frontmatter still empty — disk receipt alone does not unblock core work.

**DoD**

- [ ] `author_gate_receipt_ref` populated in plan YAML (exact path above, quoted)
- [ ] Mechanical frontmatter diff attached to W0.5 receipt (PASS only if diff present)
- [ ] Receipt linked from W1+ wave receipts as precondition cite
- [ ] W0.5 receipt with PASS/BLOCKED status

**If Author-Gate unavailable:** Mark W0.5 **BLOCKED**; W1 may run ADR-089 + archive/matrix/docs **outside** `agentic_core/**` only. Do not start W2-L0, W2-C0, W3, or W4 core edits.

---

### W1 — Tier D burndown + ADR-089

**Precondition:** W0.5 PASS for any `agentic_core/**` delete/shim; W0.5 BLOCKED limits W1 to non-core paths only.

**Scope (non-core always allowed)**

- ADR-089: Capability harvest charter (GLOBAL HARVEST LAW + contract note template)
- Archive receipts under `artifacts/archive/agent_inventory/`
- Matrix/taxonomy status updates (see matrix rules below)

**Scope (core — requires W0.5 PASS)**

- **Archive/deprecate** 12 `ORPHAN_NO_REF` + `RootCustomsAgent` shim under `artifacts/archive/agent_inventory/` (coordinate with deferred plan W4)
- Redirect importers to extracted util/profile where applicable
- **No physical delete in W1** unless a **separate** Author-Gate `deletion_strategy` receipt explicitly approves immediate delete (rare)

**Archive vs delete (Tier D — hard)**

| Action | When | Proof |
|--------|------|-------|
| **Archive/deprecate** (W1 default) | Tier D burndown | Archive receipt + importer scans; matrix `archive_resolved` |
| **Physical delete** | W5 closeout **or** separate `deletion_strategy` gate | W5 non-use proof + grep; forensic digest from archive receipt |

Archive is **not** proof of product removal until importer scans show no runtime consumers **and** W5 non-use proof passes.

**Importer and artifact safety (required per module — not ADG alone)**

For each candidate delete/archive module, run scans across:

- `agentic_core/**`
- `apps_*/**`
- `ops_scripts/**`
- `tools/**`
- `.github/**`
- `tests/**`
- Docs command snippets referencing module path or import string

**Scan patterns (minimum):**

```text
from <module> import
import <module>
importlib / getattr dynamic references to class or module basename
```

**Decision rule:** If any importer exists → redirect to extracted utility/profile **or** block deletion (W1 **PARTIAL** for that module).

**ADG:** `adg_edge_fanin` per module (necessary, not sufficient).

**Archive receipt fields (per module):**

| Field | Required |
|-------|----------|
| `original_path` | yes |
| `archive_path` | yes |
| `content_digest` | sha256 of archived file |
| `reason_code` | e.g. `ORPHAN_NO_REF`, `SHIM_DEAD_LEGACY` |
| `matrix_row_id` | `class_name` from matrix |
| `replacement_exists` | bool + path if true |

**Matrix row count rules**

- Row count may **decrease** only if taxonomy explicitly marks row `deleted` / `archive_resolved`.
- Otherwise row count **unchanged**; update `integration_pattern`, `recommendation_tier`, `harvest_action`, `status` fields only.

**Author-Gate:** `deletion_strategy` per orphan cluster only if W1 proposes **physical delete** (non-default); archive-only W1 does not require deletion_strategy.

**DoD**

- [ ] ADR-089 merged
- [ ] Per-module **archive** receipts with importer scan output attached (no physical delete unless separate deletion_strategy receipt)
- [ ] ≥12 orphan modules **archived** (not physically deleted) **or** documented block with redirect plan
- [ ] `check_agent_taxonomy_spine_invariants.py` PASS
- [ ] W1 receipt with exact grep/ADG commands and NON_CLAIMS if any deletion blocked

---

### W2-L0 — Tier A L0 route-gate harvest (P2)

**Precondition:** W0.5 PASS; W2-L0 contract note filed before first core edit.

**Agents (this wave only):** `SemanticGatekeeperAgent`, `AutonomyGuardianAgent`, `SSOTFolderCleanupAgent`

**Extract target:** `L0_routing/reasoning/route_gates` + L0 gate profile artifacts (policy-bound, signed where runtime-bound).

**SOURCE EXTRACTION QUARANTINE (hard)**

- Extracted logic copied into **non-agent** functions/modules; no subclass of source `*Agent`.
- **No runtime import** from source `*Agent` module in `agentic_core/**` or `apps_rg/**`.
- Source `*Agent` classes referenced only by: static analysis tooling, migration notes, archive receipts — **never** by L0/C0 runtime modules.

**Grep/import proof (W2-L0 receipt must include command output):**

Run full **Harvest grep proof set** (Tier A class names + module stems + `.*Agent` syntax + importlib) scoped to `agentic_core/L0_routing`, `agentic_core/runtime`, `apps_rg`. See plan section **Harvest grep proof set**.

**L0 authority sub-DoD (negative controls required)**

- [ ] L0 extract **only** emits/feeds route-gate policy/profile decisions.
- [ ] **Does not** retrieve documents, score final evidence, or assemble prompts.
- [ ] Tests include **negative controls:** L0 path rejected when asked to perform retrieval or prompt assembly (explicit test names in receipt).

**Contract note (required before merge):** [agent_capability_harvest_contract_w2_l0.md](../docs/reports/cursor/agent_capability_harvest_contract_w2_l0.md)

| Field | Value |
|-------|-------|
| Producer stage | L0_ROUTE |
| Consumer stage | route gate evaluator / gate profile loader |
| Authority scope | route-gate policy only |
| Runtime vs CI | runtime-bound gates require policy_hash/registry per spine contract law |
| No authority widening | asserted in contract doc |

**Author-Gate:** `architecture_choice` if gate API shape changes (W0.5 scope must cover change).

**Contract validation checklist (W2-L0 receipt — all must be checked PASS)**

- [ ] Contract note exists at SSOT path
- [ ] Producer/consumer stage populated
- [ ] Authority scope populated
- [ ] Runtime vs CI classification populated
- [ ] No-authority-widening assertion present
- [ ] Source agents listed by **name only** (no import paths as runtime deps)
- [ ] Replacement paths listed
- [ ] No source-agent import path appears as a runtime dependency (grep proof attached)

**DoD**

- [ ] Three Tier A L0 agents deprecated (shim or archive; **no physical delete** unless W5/deletion_strategy) with quarantine grep PASS
- [ ] pytest L0 gate + negative-control tests PASS
- [ ] Contract note **validated** (checklist above)
- [ ] ADG/static: 0 spine closure agents
- [ ] W2-L0 receipt; **NON_CLAIMS:** C0 not modified, no judge panel, no release eligibility

**Do not start W2-C0 until W2-L0 DoD PASS.**

---

### W2-C0 — Tier A C0 profile / semantic-cache harvest (P3)

**Precondition:** W0.5 PASS; W2-L0 DoD PASS; W2-C0 contract note filed before first C0 edit.

**Agents (this wave only):** `EmbeddingSovereignAgent`, `SovereignRAGManager`, `RedisSovereignAgent`

**Extract target:** C0 retrieval profile + semantic cache coordinator (profile-bound; no agent class entrypoint).

**SOURCE EXTRACTION QUARANTINE:** Same rules as W2-L0; run full **Harvest grep proof set** on C0/profile paths and `apps_rg/**`.

**C0 semantic cache stop rule (hard)**

C0 semantic cache coordinator may expose **cache eligibility signals only** to the owning route/cache layer through **typed profile metadata**. It must **not**:

- select R1B or any route branch
- return RET packets
- decide terminal cache hits

**L0 remains owner of route/cache selection.** Violation fails W2-C0.

**C0 authority sub-DoD (negative controls required)**

- [ ] C0 extract **only** configures retrieval/profile/cache coordination.
- [ ] **Does not** route requests, answer user queries, or create prompt instructions.
- [ ] Tests include **negative controls:** C0 path rejected when asked to perform route selection or prompt instruction generation.

**Contract note (required):** [agent_capability_harvest_contract_w2_c0.md](../docs/reports/cursor/agent_capability_harvest_contract_w2_c0.md)

| Field | Value |
|-------|-------|
| Producer stage | C0_CONTEXT |
| Consumer stage | profile loader / semantic cache coordinator |
| Authority scope | retrieval profile + cache namespace policy only |
| Runtime vs CI | classify each new field |
| No authority widening | asserted; must not absorb L0 gate decisions |

**Contract validation checklist (W2-C0 receipt — same eight items as W2-L0)**

**DoD**

- [ ] Three Tier A C0 agents deprecated with quarantine grep PASS
- [ ] pytest C0 profile + negative-control tests PASS (include stop-rule negative: no R1B/RET/terminal hit decision in C0)
- [ ] Contract note **validated** (checklist)
- [ ] W2-C0 receipt; **NON_CLAIMS:** L0 gates unchanged in this wave, no spine agent mount

---

### W3 — Judge panel pilot (P5, real-provider proof)

**Precondition:** W0.5 PASS; contract notes per adapter.

**Scope**

- Pick 2 lowest fan-in judge candidates from matrix P5 set
- Implement `JudgeProviderAdapter` under `agentic_core/runtime/judges/panel/`
- Wire through `apps_rg` x1d panel bridge

**Canonical runtime command (record env + roster in receipt):**

```bash
python -m apps_rg --section executive_summary
```

**Required artifacts in proof bundle directory (all must exist in receipt):**

| Artifact | Requirement |
|----------|-------------|
| `run_manifest.json` | real run id, section, env flags |
| `compiled_prompt_artifact.json` | non-empty compiled prompt |
| `provider_request.json` | real provider request payload |
| `provider_response.json` | real provider response (not stub-only) |
| `x1d_llm_judge_outputs.json` | per adapter: **adapter id**, **provider/model identity**, **non-mock classification**, score, pass/fail, decisive rationale |
| `x3_disposition.json` | final disposition (may be FAIL — still valid W3 evidence) |

**Proof bar (hard)**

- Adapter-presence alone is **insufficient**.
- Receipt must classify each judge: `REAL_PROVIDER` vs `MOCK` vs `BLOCKED`.
- If run fails X3 or any judge blocked → W3 may be **PARTIAL**; document failure; **do not** claim release eligibility from adapter wiring alone.

**Generation vs judge providers (W3 receipt — separate tables)**

`python -m apps_rg --section executive_summary` uses **generation** provider(s) plus **judge** provider(s). Receipt MUST record separately:

| Record | Required fields |
|--------|-----------------|
| **Generation** | provider/model classification (`REAL_PROVIDER` / `MOCK` / `BLOCKED`), failure stage if any |
| **Per judge** | adapter id, judge provider/model classification, score, pass/fail, decisive rationale |
| **Failure attribution** | If run fails: tag root stage — `generation`, `judge_block`, `X2`, or `X3_aggregation` (one primary; secondary noted) |

Do not collapse generation and judge proof into a single adapter-id line.

**Contract validation checklist (W3 — per adapter contract note; eight items each)**

**Negative proof (required)**

- [ ] `trace_agents_vs_spine.py` (or equivalent) shows **no** L5 or judge `*Agent` class in spine import closure
- [ ] Grep: Harvest grep proof set for selected judge class names + module stems (see plan section); no runtime import in `agentic_core/runtime/judges/**` or `apps_rg/**`

**DoD**

- [ ] Full artifact bundle paths listed in W3 receipt
- [ ] Generation + per-judge provider tables populated
- [ ] Failure attribution populated if run did not PASS X3
- [ ] At least 2 adapters with `REAL_PROVIDER` classification in `x1d_llm_judge_outputs.json`
- [ ] Negative spine/grep proof attached
- [ ] **NON_CLAIMS:** no product-spine agent remount; no release eligibility unless separate integrated proof passes

---

### W4 — FCA wave (parity-gated; monolith archive blocked until proven)

**Precondition:** W0.5 PASS; user intent on heal scripts documented in receipt (does not waive parity).

**W4 CANNOT archive `FileClassificationAgent.py` until CI parity proves every former FCA rule has:**

1. An ADG/structure CI equivalent, **or**
2. Intentional retirement with written rationale, **or**
3. Migration to a **non-agent** utility (not `*Agent` import)

**Parity receipt (required before archive):** [agent_capability_harvest_fca_parity_matrix.md](../docs/reports/cursor/agent_capability_harvest_fca_parity_matrix.md)

| Column | Required |
|--------|----------|
| Former FCA check id | from monolith/subpackage |
| New gate/test owner | script or CI job path |
| Coverage command | exact command proving check runs |
| Status | `covered` / `retired_rationale` / `gap` |

**Status rules**

| Parity state | W4 outcome | Monolith |
|--------------|------------|----------|
| All checks covered or retired | PASS → archive allowed | archive to `artifacts/archive/agent_inventory/` |
| Any `gap` without retirement rationale | **BLOCKED** or **PARTIAL** | **stays in place** |
| Incomplete + user retired scripts | deprecation notice only; no archive | in place |

**Scope when parity PASS**

- Promote `file_classification/*` rules to ADG/structure CI gates
- Archive monolith with archive receipt (W1 field schema)
- Matrix: FCA cluster rows → `archive_resolved` or util paths; not silent row delete

**Author-Gate:** `deletion_strategy` for monolith (W0.5 + W4 parity receipt attached).

**DoD**

- [ ] Parity matrix complete with commands
- [ ] If gaps exist: W4 **PARTIAL/BLOCKED**; monolith not archived; deprecation notice only
- [ ] If PASS: monolith archived; importers redirected to non-agent utils
- [ ] **NON_CLAIMS:** no claim that FCA heal subgraph enhancement equals spine improvement

---

### W5 — Closeout (absence + non-use)

**Precondition:** All prior waves receipted; W0.5 scope still valid.

**Commands (record all output in W5 receipt):**

```bash
python tools/governance/build_agent_capability_decision_matrix.py
python tools/governance/trace_agents_vs_spine.py
# Artifact scan for ARTIFACT_PROVEN (reuse W3 harness or inventory proof script)
# Full Harvest grep proof set (Tier A + W3 judges + FCA if W4 ran) — see plan section
```

**Physical delete (W5 only, optional)**

- May remove archived copies from active tree only after archive receipts + W5 non-use proof
- Requires separate `deletion_strategy` Author-Gate receipt if deleting before closeout criteria met

**DoD (all required for wave PASS)**

- [ ] **Static proof:** import closure shows `spine_closure_agents == 0`
- [ ] **Runtime proof:** artifact scan shows `ARTIFACT_PROVEN == 0` for agent classes
- [ ] **Grep proof:** Harvest grep proof set PASS (class names + module stems + `.*Agent` syntax + importlib) for `agentic_core/**` and `apps_rg/**`
- [ ] **Matrix proof:** W0→W5 diff explains every Tier A/D movement (tier, pattern, status)
- [ ] **Archive list:** all archived/deprecated classes with paths + digests; physical deletes listed separately

**Plan status rules (strict — no "completed but blocked")**

| Outcome | `PLAN_STATUS` | May claim |
|---------|---------------|-----------|
| W0.5–W5 required DoD all PASS | **Completed** | "Full harvest complete" |
| Any wave PARTIAL or BLOCKED | **Partial** | "Documentation closeout complete" only — **not** "full harvest complete" |
| W0.5 never PASS | **Not Started** or **Partial** | Non-core docs only |

- [ ] W5 receipt records per-wave PASS/PARTIAL/BLOCKED and sets plan status per table above

**NON_CLAIMS (verbatim in W5 receipt)**

- No product-spine agent remount.
- No new product-spine agent classes.
- No release eligibility from docs/static proof alone.
- No mock-only judge proof claimed as real runtime proof.
- Archive alone is not product removal without W5 non-use proof.
- PARTIAL/BLOCKED waves forbid "full harvest complete" narrative even if documentation is finished.

---

## Contract note template (any new core surface)

File one note per surface under `docs/reports/cursor/agent_capability_harvest_contract_<wave>_<surface>.md`.

```markdown
# Harvest Contract — <surface name>

- **Producer stage:**
- **Consumer stage:**
- **Authority scope:** (what decisions this surface may influence)
- **Runtime vs CI vs migration-only:**
- **policy_hash / blueprint / registry expectations:** (if runtime-bound)
- **No authority widening:** (explicit assertion + what downstream must not gain)
- **Source agents harvested:** (names only; no runtime import)
- **Replacement paths:**
```

Aligns with spine law: stages receive signed, policy-bound contracts; downstream contracts must not silently widen authority.

**Validation (required in W2/W3 receipts — not filing alone)**

| Check | PASS criterion |
|-------|----------------|
| Contract note exists | Path on disk |
| Producer/consumer stage | Both non-empty |
| Authority scope | Non-empty |
| Runtime vs CI | Classification non-empty |
| No authority widening | Explicit assertion present |
| Source agents | Names only; no runtime import paths |
| Replacement paths | Listed |
| Runtime dependency | Grep shows no source-agent import as runtime dep |

---

## Coordination with deferred follow-up

| Topic | Owner plan |
|-------|------------|
| Full green `apps_rg` integrated proof | deferred W1 (DS-1) |
| HOW class identity ADR | deferred W2 (DS-2) |
| Physical misplacement moves | deferred W3 (DS-3) |
| Capability harvest / FCA / judges | **this plan** |

Run deferred W1 in parallel with W2-L0 only if L2 lane fix is independent **and** W0.5 PASS for any shared core touch.

---

## Risks

| Risk | Mitigation |
|------|------------|
| Core edits without Author-Gate | W0.5 hard block; empty `author_gate_receipt_ref` |
| L0/C0 authority blur | Split W2-L0 / W2-C0 + negative-control tests |
| Runtime import of source agents | SOURCE EXTRACTION QUARANTINE + W5 grep proof |
| Orphan delete breaks ops | W1 archive-first + importer scans; physical delete only W5/deletion_strategy |
| Receipt on disk but YAML empty | W0.5 mechanical frontmatter diff required |
| C0 becomes route selector | W2-C0 semantic cache stop rule |
| "Completed but blocked" narrative | W5 strict PLAN_STATUS table |
| Judge adapter mock-only | W3 full provider artifact bundle + REAL_PROVIDER classification |
| FCA archive before parity | W4 BLOCKED until parity matrix complete |
| Silent authority widen | Contract note per surface + ADR-089 |

---

## Success criteria (plan close)

**Full harvest complete** (requires `PLAN_STATUS: Completed`):

1. W0.5 Author-Gate receipt populated; **mechanical YAML diff** proves `author_gate_receipt_ref` non-empty.
2. Decision model remains SSOT for "should we use agent X?"
3. Tier A logic in P2/P3 targets with **zero** runtime import from source `*Agent` modules (Harvest grep proof set PASS).
4. Tier D orphans **archived** in W1; physical delete only if W5/deletion_strategy; importer safety receipts.
5. W5 proves absence (closure) **and** non-use (artifacts + grep).
6. Matrix W0→W5 diff published; taxonomy reflects archive/delete status honestly.
7. **No wave** PARTIAL/BLOCKED among W0.5–W5 required DoD.

**Documentation closeout complete** (may use `PLAN_STATUS: Partial`): model/matrix/ADR/receipts updated while one or more waves remain PARTIAL/BLOCKED — must **not** label as full harvest complete.

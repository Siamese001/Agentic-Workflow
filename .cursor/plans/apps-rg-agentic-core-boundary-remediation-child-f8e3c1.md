# Child plan — apps_rg vs agentic_core boundary remediation (narrow waves)

**Plan slug:** `apps-rg-agentic-core-boundary-remediation-child-f8e3c1`  
**Scope:** Narrow waves **W0 through W6** are **CLOSED** under `TARGETED_SCOPE_PASS`. **Post-W6 carry-forward:** O1–O3 tightened in-repo (2026-05-15); **O4–O6 still open** — see [OPEN SCOPE](#open-scope-carry-forward-after-w0-through-w6).

**Parent evidence (scope gap analysis — do not supersede):**

| Artifact | Path |
|----------|------|
| Report | `artifacts/apps_rg/scope_gap_analysis/apps_rg_agentic_core_scope_gap_report.md` |
| Matrix | `artifacts/apps_rg/scope_gap_analysis/apps_rg_agentic_core_scope_gap_matrix.json` |
| Findings CSV | `artifacts/apps_rg/scope_gap_analysis/apps_rg_agentic_core_boundary_findings.csv` |
| Prior recommended waves | `artifacts/apps_rg/scope_gap_analysis/apps_rg_agentic_core_recommended_plan.md` |

**Analysis STATUS reference:** PARTIAL_ACCEPTED for gap-analysis artifacts only — not a commitment to clean separation or green CI.

---

## OPEN SCOPE: carry-forward after W0 through W6

**Plan wave execution:** **CLOSED** — narrow waves **W0** through **W6** are complete under `TARGETED_SCOPE_PASS` (see **Execution closure** at the end of this file).  
**Post-W6 remediation (2026-05-15):** O1–O3 were implemented or partially implemented below. **O4–O6 remain legitimately open.**

| # | Item | Status | Notes |
|---|------|--------|--------|
| O1 | **W3** temporary provider usage | **Addressed** | Product section dispatches import `call_qwen_vllm` from `apps_rg/runtime/providers/section_qwen_slice.py` (single slice). `apps_rg/runtime/dry_run/executive_summary_demo.py` still defines a **local** `call_qwen_vllm` for dry-run only. |
| O2 | **W4 / W7** trace population | **Partial** | `c0_retrieve_apps_rg(..., trace_map_out=optional list)` appends `AppsRgEvidenceTraceMap`; bounded section retrieval emits one `SectionEvidenceTrace` per profile section queried. Callers must pass `trace_map_out` to capture; PA/L2 wiring may still ignore it. |
| O3 | **L0** scanner | **Strict available** | Default: advisory (exit 0). **Fail-closed:** `python ops_scripts/ci/check_l0_app_agnostic.py --strict` or `L0_APP_AGNOSTIC_STRICT=1` using `ops_scripts/ci/baselines/l0_app_agnostic_allowlist.json`. |
| O4 | **G4** graph-reach archival ratchet | **Open** | **WIRING-CI** child track only — see **Explicit OUT_OF_SCOPE_CHILD_PLAN**. |
| O5 | Full **`tests/_apps_contract`** | **Open** | Not executed (~6k nodes); narrow slices only are claimed. |
| O6 | Full **`run_contract_gates.py`** | **Open** | Not claimed PASS; G4 and fleet still block a green full run. |

**Remaining carry-forward (verbatim — shrinking set):**

- G4 remains separate WIRING-CI child plan
- full tests/_apps_contract not run
- full run_contract_gates not claimed
- optional: thread `trace_map_out` through product dispatch/L2; retire `executive_summary_demo` local qwen shim

**DO NOT re-open W0 through W6 waves** unless a new plan rescopes them. New work should spawn a new slugged plan for O4–O6 (and trace consumer wiring if desired).

---

## North-star ownership (binding)

| Concern | Owner |
|---------|--------|
| Resume-specific config, prompts, section schemas, rubrics | **apps_rg** |
| **apps_rg C0 binding** / **apps_rg C0 integration path**, fact_vectors wiring, fixtures, app proof | **apps_rg** |
| Generic spine contracts, C0/FEC **capability**, PA slot law, L2 execution contract | **agentic_core** |
| Exit X1/X2/X3 machinery, 00C gates, L5 certification framework, UWG/L4 write law, L6 offline learning framework, proof law | **agentic_core** |

**Terminology:** Use **“apps_rg C0 binding”** or **“apps_rg C0 integration path.”** Do not abbreviate to “apps_rg C0” as an ownership label.

---

## Hard constraints (non-negotiable)

1. **Do not** modify, disable, reseed, or “paper over” **G4 graph-reach archival ratchet** (`ops_scripts/ci/check_graph_reach_archival.py`, related baselines). Track under **separate WIRING-CI child plan** only.
2. **Do not** run full `tests/_apps_contract` as a wave gate (collection ~6k+). Use **narrow slices** listed per wave only.
3. **Do not** broaden into **repo-wide ADG cleanup**, indexer campaigns, or mass graph repair inside this plan.
4. **Keep agentic_core generic and app-agnostic.** Any remaining `apps_rg` identifiers must be justified as **temporary thin adapter**, **tests**, **explicit quarantine**, or **documentation**.
5. **Classification before moves:** No production code relocation until the surface appears in the **W1 reviewed table** with **all mandatory columns** (see W1). **W2** is highest blast radius and runs **only after W1 + W3 + W4** — see wave dependency graph.

---

## Classification taxonomy (every gap row MUST map to exactly one)

| Tag | Meaning |
|-----|--------|
| **temporary thin adapter** | Core shim bridging app package to generic engine; GENERIC_READY exit criteria documented. |
| **app-specific logic that must move to apps_rg** | Resume/domain policy, rubrics, literals, or validators that are not generic capability. |
| **generic capability that should remain or be generalized in agentic_core** | Engines, contracts, coordinators usable across apps without resume literals. |
| **deprecated/quarantine candidate** | Legacy path to fence, label `_QUARANTINE` / dev-only / removal ticket with compatibility window. |
| **documentation/naming cleanup only** | No behavioral change; clarifies SSOT (e.g. ingress docs vs `AppsRgIngressPayload`). |
| **proof gap only** | Structure acceptable; missing tests, receipts, or populated trace fields for W7 provenance. |

Each W1 row must also set **`action`** (Move / keep / quarantine decisions); **`classification_tag`** is the architectural category — **`action`** is the execution disposition (see W1 mandatory columns).

---

## Frozen targeted proof slice (reuse across W2–W6; see also W0.5 drill)

Use the **same narrow `_apps_contract` modules** after substantive edits (not the full suite):

```powershell
# Repo root (PowerShell). Cmd.exe may use `set PYTHONPATH=.`.
$env:PYTHONPATH="."
python -m pytest tests/_apps_contract/test_apps_rg_core_boundary.py `
  tests/_apps_contract/test_c0_no_answer_generation.py `
  tests/_apps_contract/test_c0_no_direct_l4_write.py `
  tests/_apps_contract/test_c0_sparse_exact_apps_rg_wiring.py `
  tests/_apps_contract/test_apps_rg_dispatch_fec_presence.py `
  -q --tb=short
```

```powershell
$env:PYTHONPATH="."
python -m pytest tests/_apps_contract/test_c0_no_answer_generation.py::TestC0EvidenceTraceProduction::test_c0_evidence_trace_includes_all_fields -q --tb=short
```

Legacy cmd.exe concatenation (optional):

```bat
REM Repo root. Ensure pytest recognizes plugins (see pytest.ini / PYTEST_DISABLE_PLUGIN_AUTOLOAD note in AGENTS.md).
set PYTHONPATH=.
python -m pytest tests/_apps_contract/test_apps_rg_core_boundary.py ^
  tests/_apps_contract/test_c0_no_answer_generation.py ^
  tests/_apps_contract/test_c0_no_direct_l4_write.py ^
  tests/_apps_contract/test_c0_sparse_exact_apps_rg_wiring.py ^
  tests/_apps_contract/test_apps_rg_dispatch_fec_presence.py ^
  -q --tb=short
```

**Do not** add full-suite invocation to acceptance criteria for any wave.

---

## Wave structure template — status meanings

| Outcome | When |
|---------|------|
| **PASS** | Acceptance satisfied + narrow pytest slice green + no forbidden scope creep. |
| **PARTIAL** | Acceptance satisfied but proof ledger still honest gaps (e.g. contract gates still exit 1 at **G4**, or L0 scan still advisory). |
| **FAIL** | Narrow slice fails, forbidden literals regress in core outside approved buckets, or explicit wave acceptance missed. |
| **BLOCKED** | Cannot classify owner safely, migration requires architecture decision, or tooling/token prevents verification — record blocker explicitly. |

---

## W0 — Baseline and freeze

**Goal:** Freeze inputs for execution; **zero implementation**.

**Steps**

1. Copy verbatim paths to the four scope-gap artifacts into this plan’s execution log (or wave notes).
2. Snapshot **proof ledger** from the report (targeted subset last recorded PASS; A1 last recorded; `run_contract_gates` PARTIAL/fail at G4; full `_apps_contract` BLOCKED).
3. Confirm **out-of-scope** items: **G4**, full contract suite, repo-wide ADG cleanup.

**Commands**

```bash
# Sanity: artifact paths exist (Windows cmd-style)
dir artifacts\apps_rg\scope_gap_analysis\apps_rg_agentic_core_scope_gap_report.md
dir artifacts\apps_rg\scope_gap_analysis\apps_rg_agentic_core_scope_gap_matrix.json
dir artifacts\apps_rg\scope_gap_analysis\apps_rg_agentic_core_boundary_findings.csv
dir artifacts\apps_rg\scope_gap_analysis\apps_rg_agentic_core_recommended_plan.md
```

**Likely files touched:** none.

**Acceptance:** Written baseline note appended (dates optional); **no code churn**.

**Wave STATUS:** **PASS** when checklist complete; **BLOCKED** only if artifacts missing.

---

## W0.5 — Known proof seam unblocker

**Goal:** Fix **only** existing **`SectionEvidenceTrace.section_type`** drift if tests still fail — unblock the narrow FEC/trace proof seam before deeper classification work.

**Depends on:** **W0**

**Hard constraints**

- **No ownership moves** between packages.
- **No pseudo-FEC** — trace companions stay distinct from **FEC** (`agentic_core/runtime/contracts/final_evidence_contract.py`).
- **FEC** remains **agentic_core-owned**.
- **apps_rg C0 binding / integration path** remains **apps_rg-owned**.

**Commands**

```powershell
$env:PYTHONPATH="."
python -m pytest tests/_apps_contract/test_c0_no_answer_generation.py::TestC0EvidenceTraceProduction::test_c0_evidence_trace_includes_all_fields -q --tb=short
```

**Likely files touched:** Only if fixing drift — typically `apps_rg/runtime/bindings/c0_evidence_trace_map.py` (and tests **only** if strictly necessary for the seam); **no production moves**.

**Acceptance**

- Targeted test **PASS**, **or**
- Still failing — record **proof gap only** with **exact** pytest error/trace excerpt and classification tag **proof gap only** in the W1 journal (do not advance implementation under ambiguity).

**Wave STATUS:** **PASS** if test green or failure honestly captured per acceptance; **FAIL** if drift ignored without recording.

---

## W1 — Core resume-domain surface classification

**Goal:** **Inventory and classify** every resume / **apps_rg**-named surface in **agentic_core**. No moves.

**Depends on:** **W0**, **W0.5**

**Inventory seeds (extend via ADG MCP — not repo-wide grep campaigns)**

Starting paths from scope-gap matrix / CSV (non-exhaustive — expand in W1 table):

| Area | Seed paths |
|------|------------|
| U0 / ingress | `agentic_core/runtime/entry/u0_apps_rg_binding.py`, `agentic_core/runtime/contracts/apps_rg_ingress_payload.py` |
| L0 | `agentic_core/L0_routing/apps_rg_l0_binding.py`, `agentic_core/L0_routing/gates/apps_rg_prerequisite_gate.py` |
| L1 | `agentic_core/L1_cognition/apps_rg_l1_binding.py` |
| C0 shim | `agentic_core/runtime/c0/apps_rg_c0_binding.py`, `agentic_core/runtime/c0/c0_package_driven_grounding.py`, `agentic_core/knowledge/retrieval/c0_sparse_exact_seam.py` |
| FEC (core-owned capability) | `agentic_core/runtime/contracts/final_evidence_contract.py` |
| PA / L2 | `agentic_core/prompt_governance/apps_rg_pa_binding.py`, `agentic_core/L2_execution/apps_rg_l2_binding.py` |
| Exit | `agentic_core/runtime/exit/apps_rg_exit_binding.py` |
| Judges | `agentic_core/runtime/judges/resume_judges/` |
| L5 validators | `agentic_core/L5_safety/validators/` |
| L6 | `agentic_core/runtime/l6/apps_rg_learning_adapter.py`, `agentic_core/L6_learning/` |
| 00C engine | `agentic_core/runtime_gates/engine.py` |
| UWG | `agentic_core/UWG/package_driven_write_admission.py` |

**Commands**

- Structural expansion: **ADG MCP** `adg_nodes_by_file` / layer queries for `agentic_core/**` with `apps_rg` or `resume` in module path (preferred over blind `rg`).
- Optional corroboration (bounded):  
  `python ops_scripts/ci/check_l0_app_agnostic.py` — capture report output as **evidence only** (still advisory unless W6 promotes).

**Deliverable:** Reviewed table (CSV or markdown) — **one row per classified surface**. Each row MUST include:

| Column | Required |
|--------|----------|
| `file_path` | Yes |
| `symbol/package` | Yes |
| `current_owner` | Yes (`agentic_core` / `apps_rg` / shared / unclear → then action **BLOCKED** until resolved) |
| `intended_owner` | Yes |
| `classification_tag` | Yes (taxonomy row above) |
| `action` | Yes — exactly one of **MOVE** \| **KEEP_GENERIC** \| **KEEP_THIN_ADAPTER** \| **QUARANTINE** \| **DOC_ONLY** \| **BLOCKED** |
| `target_destination_if_moved` | Yes if action **MOVE** or partial move; else `N/A` |
| `thin_adapter_expiry_or_GENERIC_READY` | Yes if **KEEP_THIN_ADAPTER**; else `N/A` |
| `proof_command_impacted` | Yes — pytest module path or scanner name expected to detect regressions |
| `risk` | Yes (blast radius / coupling note) |
| `reviewer_signoff` | Yes — reviewer id + date, or `BLOCKED_ESCALATION:<owner>` **only** when `action=BLOCKED` |

**Likely files touched:** none (documentation-only edits to this plan or `artifacts/` journal optional).

**Acceptance (W1 cannot PASS unless all are true)**

1. Every seed row + ADG-expanded row has **no empty cells** in mandatory columns (use `N/A` only where allowed above).
2. Every row has **`action`** ∈ {MOVE, KEEP_GENERIC, KEEP_THIN_ADAPTER, QUARANTINE, DOC_ONLY, BLOCKED}.
3. **`reviewer_signoff`** populated per rules above (no blank signoffs).
4. **No unclassified** surfaces remaining.

**Wave STATUS:** **PASS** only when acceptance checklist satisfied; **PARTIAL** **disallowed** for W1 — use **BLOCKED** rows + escalation instead of shipping incomplete tables; **FAIL** if mandatory columns missing.

---

## W3 — apps_rg execution-path convergence

**Goal:** Label and converge **parallel section dispatch / provider** paths **before** core relocation (**W2**) so bypass risk is explicit.

**Depends on:** **W1**

**Rationale:** Characterizes **apps_rg** execution bypass risk while core inventory is fresh; informs **W2** move/quarantine decisions.

**Seed paths**

- `apps_rg/runtime/dispatch/executive_summary_dispatch.py`
- `apps_rg/runtime/providers/qwen_vllm_provider.py`
- Governed bindings: `apps_rg/runtime/bindings/pa_binding.py`, `apps_rg/runtime/bindings/l2_binding.py` (if present)

**Decision bucket (each path → one)**

1. **Route through governed PA/L2/Exit** (preferred for prod paths).
2. **Test/dev-only** — explicit guard or fixture-only entry.
3. **Quarantine** — marked legacy slice with no prod default.
4. **Declared temporary slice** — time-bound receipt + proof obligations.

**Commands**

```powershell
$env:PYTHONPATH="."
python -m pytest tests/_apps_contract/test_apps_rg_dispatch_fec_presence.py -q --tb=short
```

**Acceptance:** **No unlabelled provider bypass risk** — every alternate path has documented classification + entrypoint guard or test-only scope.

**Wave STATUS:** **PASS** when labeling + convergence plan implemented and narrow test green; **PARTIAL** if one path remains temporary slice with dated receipt; **FAIL** if prod path bypasses governed spine without documentation; **BLOCKED** if product requires ambiguous dual-path behavior unresolved.

---

## W4 — C0 / FEC boundary hardening

**Goal:** **FEC remains core-owned.** **apps_rg C0 binding / integration path** remains **apps_rg-owned.** Close trace/schema drift **before** **W2** (highest blast radius).

**Depends on:** **W3**

**Likely files touched**

- Core FEC: `agentic_core/runtime/contracts/final_evidence_contract.py`
- Core C0 seams (generic): `agentic_core/runtime/c0/c0_package_driven_grounding.py`, `agentic_core/knowledge/retrieval/c0_sparse_exact_seam.py`
- apps_rg binding + trace companion: `apps_rg/runtime/bindings/c0_binding.py`, `apps_rg/runtime/bindings/c0_evidence_trace_map.py`
- Thin shim (if retained): `agentic_core/runtime/c0/apps_rg_c0_binding.py`

**Commands**

```powershell
$env:PYTHONPATH="."
python -m pytest tests/_apps_contract/test_c0_no_answer_generation.py `
  tests/_apps_contract/test_c0_sparse_exact_apps_rg_wiring.py `
  tests/_apps_contract/test_apps_rg_dispatch_fec_presence.py `
  -q --tb=short
python -m pytest tests/_apps_contract/test_c0_no_answer_generation.py::TestC0EvidenceTraceProduction::test_c0_evidence_trace_includes_all_fields -q --tb=short
```

**Acceptance:** Narrow C0/FEC tests **PASS**; trace population gaps classified (**proof gap only** vs implementation).

**Wave STATUS:** **PASS** tests green; **PARTIAL** if defaults remain but documented + tracked; **FAIL** tests red; **BLOCKED** if FEC vs binding responsibilities disputed without ADR/architecture decision.

---

## W2 — Move or quarantine app-specific core logic

**Goal:** Act **only** on rows classified **app-specific logic that must move to apps_rg** or **deprecated/quarantine candidate** in **W1**. **Highest blast radius** — runs **after W1 + W3 + W4** when execution bypass labeling and C0/FEC seams are stable.

**Depends on:** **W1**, **W3**, **W4**

**Rules**

1. Preserve **temporary thin adapter** compatibility at public seams unless deprecation receipt exists.
2. **No generic core behavior changes** unless justified as **generalization** (classification ↔ **generic capability…**) with narrow proof slice.
3. **Do not move generic judge/evaluator machinery into apps_rg.** Keep in **agentic_core**: evaluator engine, judge **contracts**, X1/X2/X3 aggregation machinery, calibration framework, runtime gate semantics (00C engine behavior).
4. **In-scope moves / extractions to apps_rg** (when W1 action **MOVE**): resume **rubrics**, resume **profiles**, resume **thresholds**, resume **examples**, **section-specific validators**, **app fixtures** — packaged for consumption by generic engines via profiles/bindings, not by relocating core engines.

**Out of scope for W2**

- Moving `agentic_core/runtime_gates/engine.py`, generic Exit/X3 coordinators, or judge runner frameworks into `apps_rg`.
- Collapsing FEC into apps_rg-side types (**pseudo-FEC**).

**Likely files touched (examples — execute only after W1 + W3 + W4)**

| Direction | Examples |
|-----------|----------|
| Thin adapters retained | `agentic_core/**/apps_rg_*_binding.py`, `agentic_core/runtime/c0/apps_rg_c0_binding.py` |
| Candidate **content** moves (not engines) | Resume rubric YAML/JSON, threshold packs, examples under `apps_rg/**`; section validators under `apps_rg/runtime/validators/**`; prune resume literals from `agentic_core/L5_safety/validators/` after relocation |
| Judges folder | **Relocate resume-specific rubric artifacts** to **apps_rg**; **leave** judge invocation contracts / generic judge infrastructure in **agentic_core** |
| apps_rg destinations | `apps_rg/runtime/bindings/**`, `apps_rg/runtime/validators/**`, profile YAML/JSON under `apps_rg/**` (existing patterns) |
| Receipts | `artifacts/governance/migration_receipts/*.json` **when agentic_core changes qualify** |

**Commands**

```powershell
$env:PYTHONPATH="."
python -m pytest tests/_apps_contract/test_apps_rg_core_boundary.py `
  tests/_apps_contract/test_c0_no_direct_l4_write.py `
  -q --tb=short
```

**Acceptance:** **No new resume/apps_rg literals** in core outside **approved adapters / tests / quarantine markers / documented exceptions** from W1 table; **no evaluator/judge engine relocation** to apps_rg.

**Wave STATUS:** **PASS** + narrow slice green; **PARTIAL** if adapters remain but classified debt documented; **FAIL** on regression, new literals, or forbidden engine moves; **BLOCKED** if receipt/policy missing for core edits.

---

## W5 — Exit / 00C / L5 / UWG / L6 vocabulary and proof hardening

**Goal:** Role clarity: **ExitGateVerdict** (apps_rg/local helpers) vs **00C GateVerdict**; **L6** offline-only; **durable writes UWG-only**.

**Depends on:** **W2**

**Likely files touched**

- `apps_rg/runtime/bindings/exit_binding.py`
- `agentic_core/runtime/exit/apps_rg_exit_binding.py`
- `agentic_core/runtime_gates/engine.py`
- `agentic_core/UWG/package_driven_write_admission.py`
- `agentic_core/runtime/l6/apps_rg_learning_adapter.py`, `agentic_core/L6_learning/**`
- Docs: `apps_rg/AGENTS.md`, `agentic_core/AGENTS.md` (naming/SSOT only — prefer minimal)

**Commands**

```powershell
$env:PYTHONPATH="."
python -m pytest tests/_apps_contract/test_apps_rg_core_boundary.py `
  tests/_apps_contract/test_c0_no_direct_l4_write.py `
  -q --tb=short
```

Add **additional narrow tests only if already present** for Exit/00C/UWG/L6 — discover via pytest collection on specific files; **do not** mandate full-suite discovery here.

**Acceptance:** Documented vocabulary map + targeted proofs **PASS** for selected tests; expanded negative controls for UWG sovereignty **where already scaffolded**.

**Wave STATUS:** **PASS** / **PARTIAL** per proof availability; **FAIL** if contradictions introduced; **BLOCKED** if Exit/X3 SSOT ownership unclear.

---

## W6 — Targeted CI and no-regression scanners

**Goal:** Promote **stable** boundary checks to **enforcing** gates; **exclude noisy repo-wide ratchets** (especially **G4**).

**Depends on:** **W5**

**Candidates (pick only after stability proof)**

| Scanner | Path | Promotion rule |
|---------|------|----------------|
| L0 app-agnostic | `ops_scripts/ci/check_l0_app_agnostic.py` | Enforce **only** if denylist/ratchet avoids churn; else remain advisory + ticket |
| Wiring A1 | `ops_scripts/ci/check_orphan_module_ratchet.py` | Keep as-is; **do not** tie wave PASS to full `run_contract_gates` |
| Custom narrow gate | New script under `ops_scripts/ci/` **optional** — must be bounded (e.g. `agentic_core/` only, allowlist) |

**Forbidden in this wave**

- Enabling or modifying **G4 graph-reach archival** enforcement/baseline.
- Wiring “full green” `run_contract_gates.py` as acceptance.

**Commands**

```powershell
$env:PYTHONPATH="."
python ops_scripts/ci/check_orphan_module_ratchet.py
python ops_scripts/ci/check_l0_app_agnostic.py
python -m pytest tests/_apps_contract/test_apps_rg_core_boundary.py `
  tests/_apps_contract/test_c0_no_answer_generation.py `
  tests/_apps_contract/test_c0_no_direct_l4_write.py `
  tests/_apps_contract/test_c0_sparse_exact_apps_rg_wiring.py `
  tests/_apps_contract/test_apps_rg_dispatch_fec_presence.py `
  -q --tb=short
```

**Acceptance:** Narrow boundary suite **PASS**; any new enforcing gate documented with scope + rollback; **G4 untouched**.

**Wave STATUS:** **PARTIAL** expected while `run_contract_gates` still fails at G4 — **do not treat as FAIL** if wave acceptance met; **FAIL** if narrow suite breaks; **BLOCKED** if CI promotion introduces false positives.

---

## Explicit OUT_OF_SCOPE_CHILD_PLAN (duplicate for visibility)

**WIRING-CI / G4 — graph-reach archival ratchet**

- Files: `ops_scripts/ci/check_graph_reach_archival.py`, `ops_scripts/ci/baselines/wiring_graph_reach_archival_ratchet.json`, ADG snapshot policy.
- **Not** boundary remediation proof for apps_rg/core separation.

---

## DO_NOT_CLAIM (plan execution)

- Clean core / clean consumer separation “done”
- Full `run_contract_gates.py` PASS
- Full `tests/_apps_contract` PASS
- Fort Knox signoff / **SIGNED_OFF**

---

## Wave dependency graph

`W0` → `W0.5` → `W1` → `W3` → `W4` → `W2` → `W5` → `W6`

**Ordering rationale**

1. **W3** documents **apps_rg** execution bypass / parallel dispatch **before** heavy core edits.
2. **W4** stabilizes **C0/FEC** narrow proof seams **before** **W2** relocations (avoid chasing failures across moves).
3. **W2** has **highest blast radius** — only after **W1** classification + **W3** labeling + **W4** seam stability.

**Hard constraints unchanged:** no **G4** changes; no full `tests/_apps_contract`; no repo-wide ADG cleanup — see **Hard constraints** and **OUT_OF_SCOPE_CHILD_PLAN** above.

---

## Execution closure — `TARGETED_SCOPE_PASS` (2026-05-15)

**Outcome:** All approved narrow waves **W0** through **W6** completed under plan constraints.

- **STATUS:** `TARGETED_SCOPE_PASS` (narrow proof only — not full CI / not Fort Knox).
- **Receipt:** `artifacts/apps_rg/boundary_remediation/w6_targeted_ci_no_regression_f8e3c1.md` (wave proof); optional `wave_completion_targeted_scope_pass_f8e3c1.md` not required when this receipt is present.
- **Proof highlights:** A1 ratchet PASS; L0 advisory exit 0 (**7** hits); L0 **strict** mode + `l0_app_agnostic_allowlist.json`; frozen five-module pytest **47/47**; W2 and W5 targeted pairs **27/27** each (historical); post-close-out: **W3** `section_qwen_slice`, **W4/W7** `trace_map_out` + per-section traces, **L0** `--strict`.
- **Open scope (carry-forward):** See **[OPEN SCOPE](#open-scope-carry-forward-after-w0-through-w6)** — post-2026-05-15: O1–O3 tightened in-repo; **O4–O6** and optional trace consumer wiring still open.
- **Notion:** Plans DB row **Slug** `apps-rg-agentic-core-boundary-remediation-child-f8e3c1` — **Status = Completed**; **Summary** + **AI Summary** refreshed via `python tools/notion/patch_apps_rg_boundary_remediation_f8e3c1_notion.py` (disk remains SSOT).

**DO NOT CLAIM:** clean separation complete; full certification; full suite PASS; `run_contract_gates` PASS; SIGNED_OFF.

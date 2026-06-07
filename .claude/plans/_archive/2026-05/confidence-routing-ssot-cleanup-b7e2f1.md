# Confidence routing + model knobs — SSOT cleanup (hardened specification)

Plan slug (Notion parity): **`confidence-routing-ssot-cleanup-b7e2f1`**  
**Plan lifecycle status:** **Completed** (Notion Plans DB + disk, 2026-05-17). Deliverable scope closed per **`artifacts/reports/confidence_routing_ssot_w0_w4_closeout.md`**; aggregate `run_contract_gates` observation of HEAL-SSOT subprocess remains **`PARTIAL_AGGREGATE_PROOF_BLOCKED_UPSTREAM`** (child plan **`contract-gates-aggregate-unblock`**).

Audience: Operators + Cursor agents touching healing, routing, `.env.example`, CI guards, thresholds.

**W0–W4 execution record:** **`artifacts/reports/confidence_routing_ssot_w0_w4_closeout.md`**

| Bucket | Status |
|--------|--------|
| **W0 – W3** | **PASS** |
| **W4** — standalone **`check_heal_routing_threshold_ssot.py`** | **PASS** |
| **W4** — **`run_contract_gates.py`** reaches **and executes** HEAL-SSOT subprocess inside wiring plane | **`PARTIAL_AGGREGATE_PROOF_BLOCKED_UPSTREAM`** |
| **Overall execution / CI proof** | **PARTIAL** until aggregate orchestrator invokes HEAL-SSOT subprocess (**does not block plan Completed** — deliverables landed) |

**Upstream blockers (follow-on work):** projection/graph-layer completeness, GOV-3, G4 wiring ratchet — **`contract-gates-aggregate-unblock`**.

**Standalone HEAL reverification:** See closeout §Verification snapshot (`routing_thresholds_ssot.py`, scorer import SSOT, gate exit 0).

**Spec / hardened text below:** Directionally locked per operator acceptance; implementation follows hardening verbatim — no shadow conventions.

---

## Hardened scope (accepted)

### 1. SSOT owner (non-negotiable)

| Rule | Requirement |
|------|----------------|
| **Owner** | `agentic_core/L2_execution/healers/routing_thresholds_ssot.py` is the **sole production** authority for heal **numeric confidence cutoffs** and their parsing. |
| **Not owner** | `agentic_core/L0_routing/config/path_constants.py` is **not** the long-term owner of heal thresholds. |
| **`HEALING_CONFIDENCE_X/Y`** | Either **removed** entirely, OR retained **only** as deprecated compatibility stubs with **`__all__` / doc stating zero production readers** — CI must enforce **zero production consumers** (`grep`/AST denylist excluding tests + migration stubs). |
| **`ConfidenceScorer`** | Consumes tiers **only** through this SSOT module (imported accessors or frozen `HealingConfidenceThresholds` instance). No parallel `HIGH_THRESHOLD` / `MEDIUM_THRESHOLD` instance attributes holding behavioral literals for routing. |

### 2. Threshold semantics

Heal confidence uses **exactly two numeric cutoffs** (env-backed with SSOT defaults):

- **`HEALING_CONFIDENCE_HIGH`**
- **`HEALING_CONFIDENCE_MEDIUM`**

These define **three score bands only**:

- `score ≥ HIGH` → **`HealTier.HIGH`**
- `MEDIUM ≤ score < HIGH` → **`HealTier.MEDIUM`**
- `score < MEDIUM` → **`HealTier.LOW`**

**HITL** is **not** a numeric confidence band. It remains driven by **gates, risk/policy, router overrides, NEEDS_HELP, or authority/HITL conditions** — document this in SSOT module docstring and in router docs. Do not add a third env cutoff for “HITL.”

### 3. Env names (final)

| Env var | Meaning |
|---------|---------|
| `HEALING_CONFIDENCE_HIGH` | Upper inclusive boundary for HIGH tier (`score ≥` this value ⇒ HIGH). |
| `HEALING_CONFIDENCE_MEDIUM` | Lower inclusive start of MEDIUM tier; **must satisfy** `MEDIUM < HIGH`. |

**Forbidden (dead historical)** — zero references in `.env.example`, docs, templates, onboarding:

- `SOVEREIGN_HIGH_CONFIDENCE`
- `SOVEREIGN_MEDIUM_CONFIDENCE`

No aliases restoring those names.

### 4. Parser behavior (fail-closed)

SSOT resolver **must**:

- Parse both values as floats; **reject** non-finite (**NaN**, **inf**, **-inf**).
- Enforce **`0 ≤ MEDIUM < HIGH ≤ 1`**. Equality `MEDIUM == HIGH` fails.
- **Fail closed**: invalid env ⇒ **raised exception at SSOT load/resolve** with explicit message naming the offending key and rule (no silent fallback to mismatched halves).
- **Empty / unset**: use **paired SSOT defaults** declared in **`routing_thresholds_ssot.py` only** (single declaration site). Empty string policy must be explicit in code comments (recommended: unset → default; blank after trim → default only if documented as whitespace-equals-unset OR fail-closed — **pick one in implementation and test it**).

**Metadata** exposed for every resolved profile:

| Field | Purpose |
|-------|---------|
| `threshold_source_map` | e.g. `{"high": "env" \| "default", "medium": "env" \| "default"}` (stable string enum or Literal). |
| `threshold_profile_ref` | Stable opaque ref (e.g. `routing_thresholds_ssot:v1` + default version slug). |
| `threshold_profile_digest` | Deterministic SHA-256 (or BLAKE2s) hex over sorted `(name, normalized_value)` of active cutoffs **after** resolution (defaults or env); include ref string in preimage or document digest scope in module docstring. |

Consumers (`ConfidenceScorer`, heal receipts) can attach **`threshold_profile_ref` + digest + map** for replay/audit.

### 5. Replay and audit artifacts

Exported from **`routing_thresholds_ssot`** (minimal surface):

```text
HealingConfidenceThresholds        # frozen dataclass: high, medium, + metadata below
.threshold_profile_ref
.threshold_profile_digest
.threshold_source_map
```

**Receipt contract:** Any production heal routing path that persists a “confidence routing” envelope should optionally include `(ref, digest, source_map)` so offline replay can prove **which threshold profile was active**. Exact JSON field names wired in **`HealingRouter` / cascade registry** deferred to W2 — requirement is **capabilities exist and are plumbed.**

### 6. Primary-path confidence (separate domain)

- **`PRIMARY_HIGH_CONFIDENCE`**, **`PRIMARY_MEDIUM_CONFIDENCE`**, **`PRIMARY_LOW_PRO_CONFIDENCE`** stay owned by **`confidence_aware_executor.py`** SSOT literals + env reads there.
- **No silent mapping** to heal thresholds. If product later wants alignment, document an **explicit equivalence table** in:
  - `confidence_aware_executor.py` docstring, and  
  - `docs/wave_g/G2b_provider_gateway/env_key_consumer_map.md`.

Until such a documented mapping exists: **orthogonal domains**.

### 7. Signal quality (`SIGNAL_*`)

- **`SIGNAL_*`** remains **signal-quality-only** (`signal_quality_config` domain).
- **Never** imply in docs or `.env.example` that **`SIGNAL_*` controls L2 heal routing.**

**`.env.example`:** dedicate a section header explicitly named e.g.

> **Signal enhancer (`SIGNAL_*`) — NOT L2 heal routing**

### 8. Private `.env` (operator machine)

| Rule |
|------|
| **Do not** auto-edit tracked or untracked private `.env` in repo tooling or agent runs. |

**Mandatory artifact (W3):**

- Scripted **cleanup report** (markdown or JSON under `artifacts/` or emitted by CI optional dry-run):

  Lists **dead keys** (no getter in repo), **deprecated keys**, and **`HEALING_CONFIDENCE_*` migration advisory** (`SOVEREIGN_*`, legacy names).

Operators apply removals manually.

### 9. Mandatory CI guard (Wave 4 — **not optional**)

Add **`ops_scripts/ci/`** checker (exact filename TBD, e.g. `check_heal_routing_threshold_ssot.py`) registered in **`run_contract_gates.py`** / `pre-commit` per repo norms. **Fails** when:

1. **`os.getenv`** / **`environ.get`** for heal-confidence appears in **`agentic_core/L2_execution/healers/**/*.py`** **outside allowlist**:

   - **Allowlist roots:** only `routing_thresholds_ssot.py` (plus tests/mocks explicitly listed).

2. **`env_key_consumer_map.md`** misses any **newly introduced** heal-routing-related env reader not registered next to **`HEALING_CONFIDENCE_HIGH`**, **`HEALING_CONFIDENCE_MEDIUM`**, **`PRIMARY_*`**, **`SIGNAL_*`**, **`ROUTING_*`**, **`DISABLE_QWEN_FALLBACK`** etc. (**policy:** new heal env ⇒ map row + reviewer attention**).

3. **Raw literals** **`0.85`**, **`0.80`**, **`0.50`** (plus other SSOT-default numerics enumerated in guard) appear as heal cutoff **confidence** literals in **`healers/**/*.py`** **outside** `routing_thresholds_ssot.py` **and approved test files** (`tests/**`).  
   (**Note:** Tune regex to avoid false positives on unrelated constants e.g. Brier scores — prefer AST-based scan or keyed comment allowlist.**

4. **`SOVEREIGN_*_CONFIDENCE`** appears anywhere under **`.env.example`**, **`docs/**`**, **`.cursor/plans/**/*.md`** (optional allowlist grandfathered RCA paths if needed).

5. **`ConfidenceScorer`** does **not** import SSOT accessors (simple static import check or bytecode text match with escape hatch forbidden flag).

6. **`path_constants.HEALING_CONFIDENCE_X` / `_Y`** have **any production import** outside:

   - `path_constants.py` itself (deprecated stub),
   - explicit migration tests,
   - docs fragments explicitly listing “removed”.

7. Optionally: **`GEMINI_UNAVAILABLE`** etc. unaffected — gate stays focused on threshold SSOT creep.

Gate must expose **`EXIT 1`** plus actionable stderr banner.

---

## Required tests (mandatory suites)

Location: **`tests/unit/agentic_core/L2_execution/healers/`** (or parallel approved surface per ADR-082).

### Boundary tier mapping (against resolved SSOT defaults **or injected test doubles** via env monkeypatch):

| Case | Condition | Expected tier |
|------|-----------|---------------|
| A | `score == high_cutoff` | HIGH |
| B | `score == nextbelow(high_cutoff)` and `≥ medium` | MEDIUM |
| C | `score == medium_cutoff` | MEDIUM |
| D | `score == nextbelow(medium_cutoff)` | LOW |
| E | `score == 0.0` | LOW |
| F | `score == 1.0` | HIGH |

Use **stable epsilon**/`Decimal`/`nextafter` semantics documented in test module to avoid FP flakes.

### Invalid env (fail-closed):

| Case |
|------|
| `HIGH ≤ MEDIUM` |
| `HIGH > 1` or `HIGH < 0` |
| `MEDIUM < 0` or `MEDIUM > 1` |
| non-numeric strings |
| `nan` / `inf` textual or float injection |
| **Empty string**: behavior **explicit**, tested (must match documented policy in §4) |

### Drift guards (guardrails against convention rot):

| Test |
|------|
| ConfidenceScorer has **no** remaining behavioral `HIGH_THRESHOLD` / `MEDIUM_THRESHOLD` float literals duplicated from SSOT defaults (could use **`ast`/token** scan on file or forbid attribute assignment except from SSOT). |
| Repo scan (unit test spawning subprocess or importing guard module): **no** heal production file defines **`0.85` / `0.80` / `0.50`** as cutoff semantics except **`routing_thresholds_ssot`** default declarations (narrow pattern per implementation). |
| **`SOVEREIGN_*_CONFIDENCE`** absent from canonical doc paths enumerated in §9.(4). |

### HITL regression (semantic):

Tests assert **`HealTier.HITL`** paths still reachable **only via non-numeric classifier outcomes / gates** (reuse existing classifier fixtures if present) — doc test intent: **HITL is not a third numeric band**.

---

## Execution waves (revised)

| Wave | Deliverable |
|------|--------------|
| **W0** | Inventory + **`artifacts/…/confidence_env_dead_keys_report.md`** generator (no `.env` write). Registers `PRIMARY_*`, `HEALING_CONFIDENCE_*`, `SIGNAL_*`, `DISABLE_QWEN_*`, Router envs in **`env_key_consumer_map.md`** draft deltas. |
| **W1** | Implement **`routing_thresholds_ssot.py`** (+ dataclass/metadata/digest). Wire **`ConfidenceScorer`**. Deprecate/remove **`path_constants`** HEALING X/Y prod links. Tune **defaults** numerically aligned with SSOT-first policy (**single declaration** defaults in SSOT module; choose initial default pair matching prior behavior or calibrated — **explicit decision in PR**). |
| **W2** | Docs: threshold semantics, **HITL non-numeric**, Flash/Pro LOW tier, **`PRIMARY_*` orthogonal**, **`SIGNAL_*` header** in `.env.example`, **`env_key_consumer_map.md`** full rows for **`HEALING_CONFIDENCE_HIGH`/`MEDIUM`**. |
| **W3** | `.env.example` partition + **`SOVEREIGN_*`** purged repo-wide **from examples/docs**. Receipt field hint for **`threshold_profile_digest`**. Cleanup report tooling only. |
| **W4 (mandatory)** | CI gate **`check_heal_routing_threshold_ssot.py`** + wire into **`run_contract_gates.py`/pre-commit** per repo practice. |

---

## Acceptance criteria (hardened)

- [ ] `routing_thresholds_ssot.py` is the **only** production Python source defining heal **numeric** confidence cutoffs (defaults + validated env override).
- [ ] **`ConfidenceScorer`** consumes tiers **only** through SSOT accessors / resolved `HealingConfidenceThresholds`.
- [ ] `path_constants.HEALING_CONFIDENCE_X/Y` — **removed** or **stub-only deprecated**, **zero production consumers**, CI enforced.
- [ ] **`HEALING_CONFIDENCE_HIGH`** / **`HEALING_CONFIDENCE_MEDIUM`** are the sole heal env knobs; **`SOVEREIGN_*_CONFIDENCE`** absent repo-wide (`\.env.example`, `docs/`).
- [ ] **`HITL`** documented **not** a numeric cutoff; remains gate/risk/router controlled.
- [ ] **`threshold_profile_ref`**, **`threshold_profile_digest`**, **`threshold_source_map`** emitted from SSOT; heal receipts can cite them (wire minimum one path OR document backlog item with blocker if zero receipt surface today — **prefer wire in W2**).
- [ ] Parser **fail-closed** + **boundary + invalid-env + drift tests** green.
- [ ] **`SIGNAL_*`** clearly signal-quality-only in `.env.example` headers.
- [ ] **`PRIMARY_*`** orthogonal OR explicitly documented equivalence — no silent coupling.
- [ ] Private **`.env`** never patched by automation; **cleanup report** produced.
- [ ] **W4 CI mandatory** merged with gate rules in §9.

---

## References (implementation)

| Path |
|------|
| `agentic_core/L2_execution/healers/confidence_scorer.py` |
| `agentic_core/L2_execution/healers/healing_router.py` |
| `agentic_core/L2_execution/healers/confidence_aware_executor.py` |
| `agentic_core/L0_routing/config/path_constants.py` (deprecate/remove `HEALING_CONFIDENCE_*`) |
| `agentic_core/runtime/config/signal_quality_config.py` |
| `docs/wave_g/G2b_provider_gateway/env_key_consumer_map.md` |
| `ops_scripts/ci/` (new gate)

---

---

PLAN_COMPLETE: plan=confidence-routing-ssot-cleanup-b7e2f1 note="Notion Status=Completed; disk lifecycle Completed 2026-05-17; closeout artifacts/reports/confidence_routing_ssot_w0_w4_closeout.md"

## Notion mirror

- **Plans DB** row mirrors this file (`Status`: **Completed**). Page ID: `36327693-f55c-81b9-a2be-df873c125125`.

**Post-fold sync:** Optionally patch Notion **`AI Summary` / Summary** bullets to cite §§1–10 + mandatory W4 + no private `.env` edits — filesystem remains SSOT for full text.

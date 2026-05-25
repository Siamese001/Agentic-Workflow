---
plan_id: l6-repo-reorganization-mental-model-c4e8f2
plan_type: refactor
touches_agentic_core: true
touches_governance_ci: true
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# L6 Repo Reorganization — Align Code Layout to Mental Model

Orchestrate a phased repo reorganization so **code, docs, ADG, and CI** match the L6 doctrine in [L6_mental_model.md](docs/reference/_notes/L6_mental_model.md): one layer, two surfaces (passive observability + active system learning), nine doctrinal chapters (06.1–06.9), observer law, and UWG-only promotion.

> **plan_id discipline**: `plan=l6-repo-reorganization-mental-model-c4e8f2`

---

## Authorization Law (read before any wave)

`core_addition_author_gate_required: false` applies because this plan does **not** add new agentic_core product APIs — it is layout/governance refactor. That does **not** waive Author-Gate for invasive execution.

**Hard rule — Cursor MUST NOT treat W0 completion as authorization for later invasive waves.**

| Action | Author-Gate required | Receipt captured in |
|--------|---------------------|---------------------|
| W0.2 architecture path (PATH_KEEP_ROOT vs PATH_RENAME_CANONICAL) | **YES** — `architecture_choice` | `DECISION_CAPTURED` + plan § Architecture Decision Record |
| W1 fail-closed flip (L6-TAG, L6-OBS) | **YES** — `test_strategy` / governance | Wave marker + receipt path in W1 completion note |
| W1 observer-law exception / allowlist | **YES** — `architecture_choice` | Same |
| W3 chapter namespace wrappers (PATH_KEEP_ROOT only) | **YES** — `architecture_choice` | W3 start marker |
| W4 passive relocations (if any file moves) | **YES** — `refactor_scope` | W4 completion note |
| W5 physical rename (`git mv`, shim lifecycle) | **YES** — `refactor_scope` + W0.2 PATH_RENAME_CANONICAL | W5 start marker |
| W6 gravity moves | **YES** — `refactor_scope` | W6 start marker |

**Forbidden without matching receipt:** `agentic_core/` path moves, governance CI fail-closed env flips, observer-law exceptions, new compatibility shim trees, physical rename, or simultaneous canonical roots.

---

## Single-Root Architecture Invariant

**Only one import compatibility layer may exist at a time** for the L6 active surface.

| State | Canonical active root | `agentic_core.L6_system_learning` role | Root `system_learning/` role |
|-------|----------------------|----------------------------------------|------------------------------|
| **Pre-W0.2 (today)** | `system_learning/` | Alias (re-export; shared `sys.modules`) | Canonical |
| **PATH_KEEP_ROOT** | `system_learning/` | Alias only — no independent tree | Canonical; W3 wrappers optional |
| **PATH_RENAME_CANONICAL** | `agentic_core/L6_system_learning/` | Canonical package path | Temporary shim only until removal |

**Forbidden mixed state (zero-loss violation):**
- Chapter namespace wrappers under root `system_learning/chapters/` **and** a later `git mv` to `agentic_core/L6_system_learning/` in the same plan without an explicit migration step that removes or relocates wrappers and proves single ADG identity.
- Both roots accumulating independent `chapters/` re-export trees.
- ADG counting the same logical module twice (wrapper path + source path) in L6-TAG or L6-OBS scans.
- Permanent alias trees on **both** `system_learning` and `agentic_core.L6_system_learning` after W5 shim-removal phase.

---

## PATH-AWARE CERTIFICATION RULE

All W1, W2, and W5 receipts **must bind to the W0.2 `ARCHITECTURE_PATH`**. Gates and docs must not certify the wrong canonical root for the selected path.

| Path | W1 gate evidence | W2 doc/marker evidence | Final certification authority |
|------|------------------|------------------------|------------------------------|
| `PATH_KEEP_ROOT` | **Final** when W1 completes — scans `system_learning/` as canonical | May name `system_learning/` as canonical | W1 receipt (post-W1) + W2 receipt |
| `PATH_RENAME_CANONICAL` | **Provisional (pre-rename)** when W1 runs before W5 — scans pre-move tree | Conceptual only; no “final canonical root” claims for `system_learning/` | **W5.3 post-rename W1 re-run only** — supersedes all pre-rename W1 evidence |

**Stale-certification failure mode (explicit):** W1 passes on root `system_learning/`, W5 moves the package, and old W1 receipts are cited as final proof. **Forbidden.** Pre-rename W1/W2 receipts for `PATH_RENAME_CANONICAL` MUST carry `proof_phase: pre_rename` and MUST NOT appear in `PLAN_COMPLETE` or closeout bundles without a matching `proof_phase: post_rename` receipt after W5.3.

**Receipt SSOT path:** `docs/reports/cursor/l6_w1_gate_receipt_<date>.json` (W1), `docs/reports/cursor/l6_w2_doc_receipt_<date>.md` (W2), `docs/reports/cursor/l6_w5_post_rename_cert_<date>.json` (W5.3 final).

---

## CHILD PLAN PRECEDENCE

Linked child plans ([c5e8a7](.cursor/plans/_archive/2026-05/l6-alignment-deferred-scope-c5e8a7.md), [a8c4e2](.cursor/plans/_archive/2026-05/l6-folder-rename-doctrinal-alignment-a8c4e2.md), [7c4e2a](.cursor/plans/_archive/2026-05/l6-gravity-hybrid-7c4e2a.md)) were authored **before** this orchestration plan’s single-root and path-aware certification law.

**Controlling contract:** this plan (`l6-repo-reorganization-mental-model-c4e8f2`) wins on:

- `ARCHITECTURE_PATH` / canonical active root
- Shim lifecycle and Single-Root Architecture Invariant
- W3/W5 mutual exclusion and ordering
- Author-Gate requirements per wave
- Pre-rename vs post-rename proof semantics

**Execution rule:** Cursor MUST NOT execute child-plan steps verbatim if they conflict with the above. Skip or rewrite the step; cite orchestration plan section in the wave note. Child plans are **execution bodies only**, not proof authority.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: DONE
CURRENT_WAVE: COMPLETE
LAST_COMPLETED_WAVE: W6
LAST_UPDATED: 2026-05-25
E2E_CLOSEOUT: docs/reports/cursor/l6_plan_e2e_closeout_20260525.json
FOLLOWUP_PLAN: l6-reorg-deferred-followup-f3a9c2
DEFERRED_REGISTER: docs/reports/cursor/l6_reorg_deferred_scope_register_20260525.md
W1_RECEIPT: docs/reports/cursor/l6_w1_gate_receipt_20260525.json
W2_RECEIPT: docs/reports/cursor/l6_w2_doc_receipt_20260525.md
W4_RECEIPT: docs/reports/cursor/l6_w4_passive_drift_20260525.md
W5_RECEIPT: docs/reports/cursor/l6_w5_wave_receipt_20260525.md
W5_POST_RENAME_CERT: docs/reports/cursor/l6_w5_post_rename_cert_20260525.json
W6_RECEIPT: docs/reports/cursor/l6_w6_gravity_receipt_20260525.md
CERTIFICATION_MODEL: path-aware-v2
ARCHITECTURE_PATH: PATH_RENAME_CANONICAL
ARCHITECTURE_PATH_LOCKED: true
W0_DECISION_RECEIPT: docs/reports/cursor/l6_w0_architecture_decision_20260525.md

---

## Context (SCQA)

- **Situation** — Non-invasive alignment ([l6-doctrinal-alignment-noninvasive-b9d3f5](.cursor/plans/_archive/2026-05/l6-doctrinal-alignment-noninvasive-b9d3f5.md)) landed: `__layer__` / `__l6_chapter__` markers on 28 packages, `agentic_core.L6_system_learning` alias, `LAYER.md` on both surfaces, advisory CI gates L6-OBS + L6-TAG.
- **Complication** — W3 (chapter namespace shims) and W5 (physical rename) are **mutually exclusive layout strategies** unless a zero-loss migration design explicitly bridges them. Running both sequentially without constraint risks reorg-on-reorg: redundant shims, forked imports, duplicate ADG nodes, misleading mental-model SSOT.
- **Question** — How do we reorganize the repo to match the mental model with **exactly one canonical active root** and no stacked compatibility layers?
- **Answer** — **Governance-first (W1), docs/markers (W2), W0.2 hard architecture gate, then exactly one layout path** — either PATH_KEEP_ROOT (W3 allowed, W5 out of scope) or PATH_RENAME_CANONICAL (W3 skipped, W5 only after fail-closed gates).

---

## Target Architecture (LOCKED — W0.2 PATH_RENAME_CANONICAL)

```text
agentic_core/
├── L6_observability/          # passive — keep name (canonical passive root)
│   runtime_trace | semconv | execution | reasoning
│   shadow_eval | enforcement | types | utils
└── L6_system_learning/       # active — git mv from repo root (W5)
    adapters | engines | meta_learning | …  (06.1–06.9 via __l6_chapter__)

docs/reference/
└── 06_L6_Observability_and_System_Learning/   # doctrinal umbrella (W2 rename)
```

Until W5.3: pre-move tree remains `system_learning/` at repo root; alias `agentic_core.L6_system_learning` exists. **W3 REMOVED.** Final path SSOT updates at W5.3 only.

Receipt: [l6_w0_architecture_decision_20260525.md](docs/reports/cursor/l6_w0_architecture_decision_20260525.md)

**Immutable spine laws during reorg:** L6 never mutates the current run; promotion only via 06.7 → UWG; passive surface never blocks runtime.

---

## Architecture Decision Record (populated at W0.2 only)

| Field | Value |
|-------|-------|
| `ARCHITECTURE_PATH` | **`PATH_RENAME_CANONICAL`** (locked 2026-05-25) |
| `ARCHITECTURE_PATH_LOCKED` | **`true`** |
| W3 status | **REMOVED** |
| W5 status | **ALLOWED** after W1 fail-closed + W5.0 + Author-Gate |
| W6 ADG baseline | Post-W5.3 snapshot |

---

## Current-State Gap Matrix (2026-05-25)

| Area | Mental model expectation | Repo today | Severity | Wave |
|------|------------------------|------------|----------|------|
| **Canonical active root** | Exactly one | Root + alias (OK pre-W0.2) | **Gate** | **W0.2** |
| ADG `layer=L6` on `system_learning/*` | 100% tagged | **292 untagged** (L6-TAG advisory) | High | W1 |
| Observer law ports | Zero L3 dispatcher imports in L6 | **2 violations** in `ports/*_hook.py` | High | W1 |
| Chapter markers | All subpackages declare `__l6_chapter__` | **8 dirs** lack markers | Medium | W2 |
| Cross-cutting `engines/` | Chapter map or namespaces under **canonical root only** | Flat `engines/` | Medium | W3 *or* README-only (PATH_KEEP_ROOT) |
| Passive `promotion/` | 06.7 on active side | `L6_observability/promotion/` | Medium | W4 |
| Passive eval overlap | Classified map | `utils/evaluation/*` duplication | Medium | W4 |
| Doc folder name | `06_L6_Observability_and_System_Learning` | `06_L6_Observability_and_System_Learning` | Low | W2 |
| Physical rename | Only under PATH_RENAME_CANONICAL | Not done; ~205 import sites | High | **W5 (path-gated)** |

Detail: [l6_reorg_gap_matrix_20260525.md](docs/reports/cursor/l6_reorg_gap_matrix_20260525.md)

---

## Child Plans (link — execution constrained by W0.2 + § CHILD PLAN PRECEDENCE)

| Slug | Role | When executable | Proof authority |
|------|------|-----------------|-----------------|
| [l6-alignment-deferred-scope-c5e8a7](.cursor/plans/_archive/2026-05/l6-alignment-deferred-scope-c5e8a7.md) | W1–W2 body | After W0.2 locked | **Subordinate** — W1/W2 receipts must include path-binding fields |
| [l6-folder-rename-doctrinal-alignment-a8c4e2](.cursor/plans/_archive/2026-05/l6-folder-rename-doctrinal-alignment-a8c4e2.md) | W5 body | **Only** `PATH_RENAME_CANONICAL` | **Subordinate** — shim/removal steps must match Single-Root Invariant |
| [l6-gravity-hybrid-7c4e2a](.cursor/plans/_archive/2026-05/l6-gravity-hybrid-7c4e2a.md) | W6 optional | After final certification wave | Subordinate |

---

## Status Tables

### Wave Progress

| Wave | Focus | Status | Tests Added | Files Changed |
|------|-------|--------|-------------|---------------|
| W0 | Baseline + architecture gate | ✅ DONE | E2E | 3 reports |
| W1 | ADG + observer-law (pre-rename provisional) | ✅ DONE | E2E | receipt + gates; superseded by W5 cert |
| W2 | Doc rename + markers (pre-rename temporary docs) | ✅ DONE | [l6_w2_doc_receipt_20260525.md](docs/reports/cursor/l6_w2_doc_receipt_20260525.md) | W3 N/A (PATH_RENAME) |
| W3 | Chapter layout | ⛔ **REMOVED** (PATH_RENAME) | — | — |
| W4 | Passive-surface drift triage | ✅ DONE | [l6_w4_passive_drift_20260525.md](docs/reports/cursor/l6_w4_passive_drift_20260525.md) | D1–D3 deferred; no moves |
| W5 | `git mv` + migrate + shim removal | ✅ DONE | — | [l6_w5_wave_receipt_20260525.md](docs/reports/cursor/l6_w5_wave_receipt_20260525.md) |
| W6 | Optional gravity burndown | ✅ DONE | — | [l6_w6_gravity_receipt_20260525.md](docs/reports/cursor/l6_w6_gravity_receipt_20260525.md) |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W0.1 | Publish gap matrix + import blast-radius baseline | ✅ DONE |
| W0.2 | **PATH_RENAME_CANONICAL locked** | ✅ DONE |
| W1.1–W1.4 | Governance (D1/D2) + path-bound fail-closed receipt | ✅ DONE |
| W1.5 | Post-rename W1 re-cert (**PATH_RENAME only**, after W5.3) | ⛔ BLOCKED ON W5.3 |
| W2.1–W2.3 | Docs + markers (**path-conditional**) | 🔲 TODO |
| W3.1–W3.2 | Chapter namespaces (**PATH_KEEP_ROOT only**) | ⛔ BLOCKED ON W0.2 |
| W4.1–W4.2 | Passive drift map / ADR | 🔲 TODO |
| W5.0 | Rename preflight (blast-radius regen, wrapper audit) | ⛔ BLOCKED |
| W5.1–W5.3 | `a8c4e2` move → migrate → shim removal + rollback proof | ⛔ BLOCKED |
| W6.1 | Gravity remainder (optional) | ✅ DONE |

---

## Out Of Scope

- Running **both** W3 root chapter wrappers **and** W5 physical rename without a documented zero-loss bridge (forbidden).
- New L6 product features.
- Weakening L6-OBS / L6-TAG to greenwash failures.
- `apps_rg` section work (unless import paths break during W5).
- W5 entirely when `PATH_KEEP_ROOT` is selected at W0.2.
- W3 chapter namespace directories when `PATH_RENAME_CANONICAL` is selected (unless strictly required **after** rename under `agentic_core/L6_system_learning/` as a **separate** follow-on plan).

---

## Wave Summary

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|------|-----------|-------|-------------|--------|------------------|
| W0 | W0.1–W0.2 | Baseline + **mandatory architecture path lock** | ~6k | Not Started | `ARCHITECTURE_PATH_LOCKED=true`; receipt; blast-radius baseline file |
| W1 | W1.1–W1.4 | Path-bound governance + receipt JSON | ~16k | Blocked on W0.2 | Receipt fields complete; gates exit 0; proof_authority correct for path |
| W1.5 | W1.5 | Post-rename re-cert | ~4k | PATH_RENAME only; after W5.3 | Supersedes pre-rename W1; final_w1_post_rename |
| W2 | W2.1–W2.3 | Path-conditional docs + markers | ~6k | Blocked on W0.2 | W2 receipt; no stale final-root claims on PATH_RENAME |
| W3 | W3.1–W3.2 | Chapter layout | ~20k | **PATH_KEEP_ROOT only** | See § W3 — non-cosmetic proof |
| W4 | W4.1–W4.2 | Passive drift | ~12k | After W0.2 | ADR/map; no unauthorized moves |
| W5 | W5.0–W5.3 | Physical rename | ~45k | **PATH_RENAME_CANONICAL only** | See § W5 — single canonical root proof |
| W6 | W6.1 | Gravity optional | ~10k | After W2 or W5 per path | L6→lower ≤ 24 or documented |

---

## Phase-Level Summary

| Phase ID | Title | Scope | Status |
|----------|-------|-------|--------|
| W0.1 | Gap matrix + import blast-radius baseline | `docs/reports/cursor/l6_reorg_*` | Not Started |
| W0.2 | **Architecture gate** | Author-Gate packet + plan lock | Not Started |
| W1.1–W1.4 | ADG + observer law (path-bound receipt) | per c5e8a7 + § W1 | Blocked on W0.2 |
| W1.5 | Post-rename W1 re-cert | `l6_w5_post_rename_cert_*.json` | PATH_RENAME; after W5.3 |
| W2.1–W2.3 | Docs + markers (path-conditional) | `docs/reference/06_L6_*`, 8 inits | Blocked on W0.2 |
| W3.1–W3.2 | Chapter namespaces | `system_learning/chapters/` **only if PATH_KEEP_ROOT** | Blocked |
| W4.1–W4.2 | Passive drift | `L6_observability/promotion/`, eval map | Blocked on W0.2 |
| W5.0 | Rename preflight | blast-radius regen, wrapper-tree audit | Blocked |
| W5.1–W5.2 | Rename + import migration | per a8c4e2 (precedence-checked) | Blocked |
| W5.3 | Shim removal + stale-cert gate + **post-rename W1.5** | orchestration plan | Blocked |
| W6.1 | Gravity | per 7c4e2a | Optional |

---

## Wave 0 — Baseline & Hard Architecture Gate

WAVE_ID: W0
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: EXECUTED
CHECKPOINT: A

**Phases**:
- **W0.1** — Gap matrix + **import blast-radius baseline** (counts, top hotspots, snapshot path) | PHASE_STATUS: TODO
- **W0.2** — **Hard Author-Gate: exactly one canonical layout path** | PHASE_STATUS: TODO

### W0.1 Commands (baseline evidence)

```bash
python -c "import subprocess,sys; r=subprocess.run(['rg','-c','from system_learning|import system_learning','--glob','*.py'], capture_output=True, text=True); print(r.stdout or r.stderr); sys.exit(r.returncode)"
python ops_scripts/ci/check_l6_layer_tag_consistency.py
python ops_scripts/ci/check_l6_observer_law.py
```

Emit/update: [l6_reorg_gap_matrix_20260525.md](docs/reports/cursor/l6_reorg_gap_matrix_20260525.md) and **new** [l6_import_blast_radius_baseline_20260525.md](docs/reports/cursor/l6_import_blast_radius_baseline_20260525.md) (file counts, line counts, top 10 importer paths).

### W0.2 — ARCHITECTURE_DECISION_REQUIRED

**This is a hard gate.** No W3 phase and no W5 phase may start until W0.2 completes with `ARCHITECTURE_PATH_LOCKED=true`.

Before W3 or W5 starts, capture **exactly one** canonical layout path via Author-Gate (`architecture_choice`).

#### OPTION A — `PATH_KEEP_ROOT` (Defer physical rename)

- **Canonical active root:** `system_learning/` (repo root).
- **`agentic_core.L6_system_learning`:** alias only; must not gain an independent module tree.
- **W3:** MAY proceed — chapter namespace wrappers and/or `engines/README.md` chapter map only (Author-Gate per W3 start).
- **W5:** **Explicitly OUT OF SCOPE** for this plan. Do not schedule `git mv` or root shim lifecycle here. Any future rename requires a **new plan** with its own W0.2.
- **W6:** ADG baseline = post-W2/W3.

#### OPTION B — `PATH_RENAME_CANONICAL` (Promote physical rename)

- **Canonical active root:** `agentic_core/L6_system_learning/` after W5.1.
- **Root `system_learning/`:** temporary shim only (W5.1–W5.2); **removed** at W5.3.
- **W3:** **SKIPPED** in this plan — no `system_learning/chapters/` wrapper tree. Chapter layout work, if needed, happens **directly under** `agentic_core/L6_system_learning/` in a **follow-on plan** after shim removal.
- **W5:** Executes **only** after W1 fail-closed green + W5.0 preflight + Author-Gate receipt for W5.
- **W6:** ADG baseline = post-W5.3.

#### Forbidden mixed state

Do **not** introduce chapter namespace wrappers under root `system_learning/` and then perform physical rename in the same plan unless a **written zero-loss migration step** (W5.0 checklist item) removes or relocates every wrapper and proves:
- single ADG node per logical module;
- single import path SSOT in docs/tests;
- L6-TAG and L6-OBS scan canonical source paths, not wrapper-only paths.

#### W0.2 Acceptance proof (required in completion note)

Cursor MUST provide commands and outputs showing:

1. `DECISION_CAPTURED: type=architecture_choice, repo_area=system_learning, selected=<PATH_KEEP_ROOT|PATH_RENAME_CANONICAL>, outcome=executed`
2. Plan frontmatter/state updated: `ARCHITECTURE_PATH=<value>`, `ARCHITECTURE_PATH_LOCKED=true`
3. Import blast-radius baseline file exists with counts
4. Explicit statement of which waves are **REMOVED** vs **ALLOWED** per selected path

**W0 does NOT authorize W1–W6.** W0.2 only locks the architecture path; each later invasive wave still requires its own Author-Gate receipt per § Authorization Law.

---

## Wave 1 — Governance (D1 + D2) — Path-Bound

WAVE_ID: W1
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: EXECUTED
CHECKPOINT: B

**Preconditions:** `ARCHITECTURE_PATH_LOCKED=true` (W0.2 done). Author-Gate receipt for fail-closed promotion and observer-law resolution.

### W1 path-binding invariant

Before running gates, resolve scan roots from `ARCHITECTURE_PATH`:

| Field | `PATH_KEEP_ROOT` | `PATH_RENAME_CANONICAL` (pre-W5) |
|-------|------------------|----------------------------------|
| `canonical_active_root_at_time_of_gate` | `system_learning/` | `system_learning/` (pre-move; **not final**) |
| `alias_root_role` | `agentic_core.L6_system_learning` — alias only | Same |
| `root_shim_role` | none | none (shim added at W5.1 only) |
| `adg_scan_root` | `system_learning/` | `system_learning/` |
| `observer_law_scan_root` | `system_learning/` | `system_learning/` |
| `proof_phase` | `final` | `pre_rename` (**provisional**) |

**Required W1 receipt** (`docs/reports/cursor/l6_w1_gate_receipt_<date>.json`) — all fields mandatory:

```json
{
  "plan_id": "l6-repo-reorganization-mental-model-c4e8f2",
  "architecture_path": "PATH_KEEP_ROOT|PATH_RENAME_CANONICAL",
  "canonical_active_root_at_time_of_gate": "<path>",
  "alias_root_role": "agentic_core.L6_system_learning — re-export alias",
  "root_shim_role": "none|temporary_compat_shim",
  "adg_scan_root": "<path>",
  "observer_law_scan_root": "<path>",
  "proof_phase": "final|pre_rename",
  "proof_authority": "final_w1|provisional_pre_rename",
  "l6_tag_exit_code": 0,
  "l6_obs_exit_code": 0,
  "adg_snapshot": "artifacts/adg/adg_indexed_<ts>.sqlite"
}
```

Without these fields, W1 MUST NOT be marked complete.

### W1 acceptance commands

```bash
set L6_LAYER_TAG_FAIL_CLOSED=1
python ops_scripts/ci/check_l6_layer_tag_consistency.py
echo L6_TAG_exit=%ERRORLEVEL%
set L6_OBSERVER_LAW_FAIL_CLOSED=1
python ops_scripts/ci/check_l6_observer_law.py
echo L6_OBS_exit=%ERRORLEVEL%
python tools/generate_full_adg.py
```

- Both gates exit **0** with fail-closed env set.
- Receipt written with path-binding fields above.
- **`PATH_KEEP_ROOT`:** `proof_authority=final_w1` — this receipt may be cited in plan closeout.
- **`PATH_RENAME_CANONICAL`:** `proof_authority=provisional_pre_rename` — receipt MUST NOT be cited as final canonical-root proof after W5; W1.5 supersedes.

### W1.5 — Post-rename governance re-cert (PATH_RENAME_CANONICAL only)

**Entry:** W5.3 shim removed; root `system_learning/` package directory absent (shim dir may exist only if documented as deleted in same PR).

**This is authoritative final certification** for ADG + observer law on the L6 active surface — not a regression check.

| Field | Post-W5.3 value |
|-------|-----------------|
| `canonical_active_root_at_time_of_gate` | `agentic_core/L6_system_learning/` |
| `root_shim_role` | none (root shim removed) |
| `adg_scan_root` | `agentic_core/L6_system_learning/` |
| `observer_law_scan_root` | `agentic_core/L6_system_learning/` |
| `proof_phase` | `post_rename` |
| `proof_authority` | `final_w1_post_rename` |

Receipt: `docs/reports/cursor/l6_w5_post_rename_cert_<date>.json` (includes W1.5 gate outputs + stale-cert scan results).

**Rule:** Any W1 pre-rename receipt is **superseded** and must be labeled `superseded_by: l6_w5_post_rename_cert_<date>.json` in the W1 completion note when W1.5 lands.

---

## Wave 2 — Documentation & Marker Completion — Path-Conditional

WAVE_ID: W2
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: C

**Preconditions:** W0.2 locked. W2 receipt must include `architecture_path` and `doc_canonical_root_claim`.

### PATH_KEEP_ROOT — W2 allowed content

- `system_learning/LAYER.md`, doctrinal index, and mental-model cross-refs may state **`system_learning/` is the canonical active root**.
- Doc folder rename (`06_L6_Observability_and_System_Learning/`) may use root paths in examples.
- Chapter `__init__.py` markers under `system_learning/<pkg>/` — **final**.

### PATH_RENAME_CANONICAL — W2 constraints

- W2 MAY update: conceptual chapter prose, `__l6_chapter__` on existing `system_learning/<pkg>/__init__.py` (files move with W5.1), doc folder rename, cross-links that describe **doctrine** not final install path.
- W2 MUST NOT: call root `system_learning/` the **final** canonical root; publish closeout receipts implying rename is complete; update [L6_mental_model.md](docs/reference/_notes/L6_mental_model.md) “canonical path” section to `agentic_core/L6_system_learning/` **before** W5.3.
- Path-specific docs that would be invalid after W5: mark `PRE_RENAME_TEMPORARY` in frontmatter or defer to **W5.3 doc sweep**.
- **Final** mental-model and `LAYER.md` canonical path statements: **W5.3 only**, after shim removal.

**W2 receipt** (`docs/reports/cursor/l6_w2_doc_receipt_<date>.md`) must include:

- `architecture_path`
- `doc_canonical_root_claim`: `final_system_learning` | `pre_rename_temporary_only`
- List of files tagged `PRE_RENAME_TEMPORARY` (if any)
- Explicit note: “Not final canonical-root proof for PATH_RENAME_CANONICAL” when applicable

**Proposed `__l6_chapter__` for markerless dirs:** `adg`→06.1, `telemetry`→06.1, `policy`→06.2, `ml_integration`→06.5, `monitoring`→06.8, `state`→06.7, `runtime`/`config`→"".

---

## Wave 3 — Chapter Layout (PATH_KEEP_ROOT ONLY)

WAVE_ID: W3
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: REQUIRED
CHECKPOINT: D

**Entry condition:** `ARCHITECTURE_PATH=PATH_KEEP_ROOT`. If `PATH_RENAME_CANONICAL` → **W3 is REMOVED; do not execute.**

**Alternative (lower risk):** `engines/README.md` + `system_learning/CHAPTER_MAP.md` without `chapters/` directories — still requires Author-Gate if it changes CI or import guidance.

### W3 acceptance (non-cosmetic — all required)

1. **ADG canonical identity** — For every module moved/wrapped: ADG `resolved_path` points to the **source file** (under `system_learning/<pkg>/`), not wrapper-only. Proof: SQLite query or `adg_nodes_by_file` on source vs wrapper; wrapper nodes must not inflate L6 module count.
2. **No forked logical ownership** — `rg` shows no new permanent import paths that bypass canonical packages unless explicitly listed in `CHAPTER_MAP.md` as deprecated-with-timeline.
3. **No double-count in gates** — `check_l6_layer_tag_consistency.py` and `check_l6_observer_law.py` scan **source paths**; layout gate validates `__l6_chapter__` on source `__init__.py`, not wrapper-only paths.
4. **Layout CI** — `check_l6_chapter_layout.py` (new) asserts: directory ancestry ↔ `__l6_chapter__`; **canonical_source_path** field per module; fails on wrapper-only registration.
5. **Tests green** — exact command + exit code in wave note:
```bash
pytest tests/unit/system_learning/test_l6_layer_markers.py tests/unit/agentic_core/L6_system_learning/test_l6_system_learning_alias.py tests/unit/ops_scripts/ci/test_check_l6_*.py -q
```

**Rollback:** `git revert` of W3 commit range; remove `chapters/` tree; layout CI advisory off — documented in W3 completion note.

---

## Wave 4 — Passive Surface Drift

WAVE_ID: W4
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: E

**Preconditions:** W0.2 locked. Uses **canonical active root** from architecture record for any path references in ADRs.

**Phases:** ADG fan-in on `L6_observability/promotion/`; eval overlap map. File moves require separate Author-Gate.

**Receipt:** [l6_w4_passive_drift_20260525.md](docs/reports/cursor/l6_w4_passive_drift_20260525.md) + [l6_w4_adg_fanin_20260525.json](docs/reports/cursor/l6_w4_adg_fanin_20260525.json). No relocations executed.

---

## Wave 5 — Physical Rename (PATH_RENAME_CANONICAL ONLY)

WAVE_ID: W5
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: EXECUTED
CHECKPOINT: F
W5_RECEIPT: docs/reports/cursor/l6_w5_wave_receipt_20260525.md
W5_POST_RENAME_CERT: docs/reports/cursor/l6_w5_post_rename_cert_20260525.json

**Entry condition:** `ARCHITECTURE_PATH=PATH_RENAME_CANONICAL`. If `PATH_KEEP_ROOT` → **W5 is REMOVED from this plan.**

### W5 preconditions (all required before W5.1)

| # | Precondition | Proof |
|---|--------------|-------|
| P1 | W1 fail-closed green | L6-TAG + L6-OBS exit 0 with fail-closed env |
| P2 | W0.2 `PATH_RENAME_CANONICAL` captured | `DECISION_CAPTURED` + `ARCHITECTURE_PATH_LOCKED=true` |
| P3 | Import blast-radius **regenerated immediately before rename** | New `l6_import_blast_radius_pre_rename_<date>.md` with rg counts |
| P4 | **No active W3 wrapper tree** | `test ! -d system_learning/chapters` OR explicit W5.0 migration checklist signed off |
| P5 | Author-Gate receipt for W5 execution | `refactor_scope` |
| P6 | Rollback path documented | Revert commit + restore root shim + ADG regen commands in W5.0 doc |

### W5.0 Preflight checklist

- [ ] Regen blast-radius report (P3)
- [ ] Confirm zero `system_learning/chapters/` OR migration plan filed
- [ ] Branch + tag pre-rename SHA
- [ ] Rollback script: `git revert` + `python tools/generate_full_adg.py`

### W5 execution (per a8c4e2 — subject to § CHILD PLAN PRECEDENCE)

1. W5.1 — `git mv system_learning agentic_core/L6_system_learning` + temporary root shim
2. W5.2 — Batched import migration to canonical path
3. W5.3 — Shim removal + **stale-certification gate** + **W1.5 post-rename re-cert** + doc sweep

### W5.3 — Stale-certification gate (MUST pass before W5 complete)

**Purpose:** Fail if any **non-historical** artifact still presents root `system_learning/` as the canonical active root after shim removal.

**Scan command class** (record full output in post-rename cert):

```bash
rg -n -i "canonical.*system_learning|system_learning/.*canonical|canonical active root.*system_learning" docs/reference docs/reports/cursor agentic_core system_learning tests/unit ops_scripts/ci --glob "!*PRE_RENAME*" --glob "!*_archive*"
rg -n "system_learning/ is the canonical|canonical.*system_learning/" system_learning/LAYER.md docs/reference/_notes/L6_mental_model.md
```

**Allowlist:** matches only in files explicitly tagged `PRE_RENAME_TEMPORARY`, `ARCHIVED`, or under `docs/reports/cursor/*pre_rename*` / dated baseline reports.

**W5.3 MUST fail if:**

- [ ] Any `LAYER.md` or mental-model doc claims final canonical root = `system_learning/` (post-shim-removal)
- [ ] Any W1/W2 closeout receipt with `proof_authority: final_w1` from pre-rename era cited without supersession
- [ ] Root `system_learning/` package tree still exists (except empty shim stub during W5.2 — not at W5.3 complete)
- [ ] Stale-cert `rg` hits in non-allowlisted paths

### W5 post-rename certification (authoritative — not regression-only)

Post-W5 L6-TAG and L6-OBS runs are **the final governance certification** for `PATH_RENAME_CANONICAL`. Execute as **W1.5** with `proof_phase: post_rename` and `proof_authority: final_w1_post_rename`.

Pre-rename W1 evidence is **provisional** only. `PLAN_COMPLETE` and closeout bundles for `PATH_RENAME_CANONICAL` MUST attach `l6_w5_post_rename_cert_<date>.json`, not pre-rename W1 alone.

### W5 acceptance proof (all required)

1. **Canonical root:** production imports under `agentic_core/L6_system_learning/`; root shim **removed**.
2. **ADG:** regen post-rename; scan root = `agentic_core/L6_system_learning/`; no duplicate nodes.
3. **Docs/tests:** W5.3 doc sweep — `LAYER.md`, [L6_mental_model.md](docs/reference/_notes/L6_mental_model.md), tests reference `agentic_core/L6_system_learning/` as only canonical active root.
4. **W1.5 gates:** L6-TAG + L6-OBS fail-closed exit 0 — **authoritative final**, not “regression only”.
5. **Stale-cert gate:** `rg` scans clean per allowlist rules above.
6. **Tests:** pytest suite exit 0 (update paths if test package renamed).
7. **Import counts:** pre-rename vs post-rename blast-radius reports; delta explained.
8. **Supersession:** pre-rename W1 receipt marked superseded in wave note.

**Rollback (W5.3 failure):** restore from pre-rename tag; keep shim until green; do not remove root shim until P1–P6 + W1.5 re-verified.

---

## Wave 6 — Cross-Layer Gravity (Optional)

WAVE_ID: W6
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: EXECUTED
CHECKPOINT: G
W6_RECEIPT: docs/reports/cursor/l6_w6_gravity_receipt_20260525.md

Executed 2026-05-25: documented 86 L6→L0..L5 ADG import edges (43 deduplicated pairs) in [architectural_exceptions.yaml](config/architectural_exceptions.yaml) + [ADR-085](docs/architecture/adr/ADR-085-l6-observability-dependency-hygiene.md). Burndown status: `documented_over_threshold` (86 > 24). Prior move: `integrity_report_generator_util.py` → `ops_scripts/reports/`. Fixed [snapshot/__init__.py](agentic_core/L6_system_learning/snapshot/__init__.py) `__layer__` marker (301/301 L6-TAG).

---

## Gap Register

**GAP-0: W3 and W5 were unconstrained (fixed 2026-05-25)** → W0.2 + Single-Root Invariant

**GAP-0b: Stale certification after rename (fixed 2026-05-25)**
- Risk: W1 certifies `system_learning/` as canonical; W5 moves tree; old receipts cited as final.
- Fix: PATH-AWARE CERTIFICATION RULE + W1.5 + W5.3 stale-cert gate + path-conditional W2

**GAP-1: ADG does not honor `__layer__` markers** → W1 (+ W1.5 post-rename if PATH_RENAME)

**GAP-2: Observer-law port hooks** → W1 + Author-Gate for exception path

**GAP-3: Flat `engines/`** → PATH_KEEP_ROOT: W3 or README-only; PATH_RENAME: defer to follow-on under canonical tree

**GAP-4–5: Passive drift / eval overlap** → W4

**GAP-6: Physical rename** → W5 **only** PATH_RENAME_CANONICAL; otherwise new plan

---

## Definition of Done

DoD-0: Architecture path locked at W0.2
- Evidence: `DECISION_CAPTURED`; plan `ARCHITECTURE_PATH` set; W3/W5 mutually exclusive in wave table
- Status: DONE (2026-05-25)

DoD-1: Gap matrix + import blast-radius baseline published
- Evidence: [l6_reorg_gap_matrix_20260525.md](docs/reports/cursor/l6_reorg_gap_matrix_20260525.md) + `l6_import_blast_radius_baseline_*.md`
- Status: DONE (2026-05-25)

DoD-2: W1 path-bound governance receipt
- Evidence: [l6_w1_gate_receipt_20260525.json](docs/reports/cursor/l6_w1_gate_receipt_20260525.json) with all mandatory fields; gates exit 0
- **PATH_KEEP_ROOT:** `proof_authority=final_w1`
- **PATH_RENAME:** `proof_phase=pre_rename` only; final requires DoD-2b
- Status: DONE (provisional pre-rename; 2026-05-25)

DoD-2b: W1.5 post-rename certification (**PATH_RENAME only**)
- Evidence: `l6_w5_post_rename_cert_*.json`; L6-TAG/L6-OBS exit 0; pre-rename W1 marked superseded
- Status: DONE (2026-05-25)

DoD-3: W2 path-conditional docs + markers
- Evidence: [l6_w2_doc_receipt_20260525.md](docs/reports/cursor/l6_w2_doc_receipt_20260525.md) with `doc_canonical_root_claim=pre_rename_temporary_only`
- Status: DONE (2026-05-25)

DoD-4: Single canonical active root (path-dependent final proof)
- **PATH_KEEP_ROOT:** W1 final receipt + W2 `doc_canonical_root_claim=final_system_learning`
- **PATH_RENAME:** W5.3 stale-cert pass + W1.5 + mental model/LAYER updated; root shim absent
- Status: DONE (2026-05-25)

DoD-5: L6 smoke + gate suite green with recorded exit codes
- Evidence: `pytest tests/unit/system_learning/test_l6_layer_markers.py tests/unit/agentic_core/L6_system_learning/test_l6_system_learning_alias.py tests/unit/ops_scripts/ci/test_check_l6_*.py -q` → exit 0
- Status: DONE (2026-05-25; 57 passed)

---

## Verification vs Deferral

| Item | PATH_KEEP_ROOT | PATH_RENAME_CANONICAL |
|------|----------------|----------------------|
| W1 governance | Required — **final** proof | Required — **provisional** pre-rename only |
| W1.5 post-rename cert | N/A | **Required** — authoritative final |
| W2 docs/markers | May claim `system_learning/` canonical | **No final canonical claims**; W5.3 doc sweep |
| W3 chapter dirs | Optional (proof-heavy) | **Removed** |
| W4 passive map | Required | Required |
| W5 rename | **Removed** | Required + stale-cert + W1.5 |
| W6 gravity | Optional post-W2/W3 | Optional post-W5.3 final cert |

---

## Marker Quick Reference

```
PLAN_CREATED: slug=l6-repo-reorganization-mental-model-c4e8f2 path=.cursor/plans/l6-repo-reorganization-mental-model-c4e8f2.md status=Not Started
ARCHITECTURE_PATH_LOCKED: plan=l6-repo-reorganization-mental-model-c4e8f2 path=PATH_KEEP_ROOT|PATH_RENAME_CANONICAL
WAVE_START: plan=l6-repo-reorganization-mental-model-c4e8f2 wave=1
WAVE_COMPLETE: plan=l6-repo-reorganization-mental-model-c4e8f2 wave=0 note="+baseline, architecture_path=<PATH>, scope=l6-gate"
PLAN_COMPLETE: plan=l6-repo-reorganization-mental-model-c4e8f2 note="PATH_RENAME_CANONICAL; canonical root agentic_core/L6_system_learning/; W1.5+W5.3+W6 documented; E2E 21/21 PASS; gates fail-closed 302/302 L6-TAG 0 L6-OBS"
```

---

## References

- SSOT mental model: [L6_mental_model.md](docs/reference/_notes/L6_mental_model.md)
- Gap matrix: [l6_reorg_gap_matrix_20260525.md](docs/reports/cursor/l6_reorg_gap_matrix_20260525.md)
- Rename body: [l6-folder-rename-doctrinal-alignment-a8c4e2](.cursor/plans/_archive/2026-05/l6-folder-rename-doctrinal-alignment-a8c4e2.md)
- Passive LAYER: [L6_observability/LAYER.md](agentic_core/L6_observability/LAYER.md)
- Active LAYER: [L6_system_learning/LAYER.md](agentic_core/L6_system_learning/LAYER.md)

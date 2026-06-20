# Plan: Governed reasoning execution control plane

**Slug:** `reasoning-execution-control-plane-f4e9a2`  
**Status:** Completed  
**Risk:** Governance / certification alignment (false PASS if config ≠ runtime)

## Completion record (2026-05-16)

| Workstream | Verdict |
|------------|---------|
| GENERIC_REASONING_CONTROL_PLANE | **PASS** — `agentic_core/runtime/reasoning/`, `SovereignLLMGateway.generate_with_reasoning`, `ReasoningExecutionReceipt.from_primitive`, X1D cap on nominal PASS, pytest 10+45, bounded grep |
| APPS_RG_RUNTIME_BINDING | **OPEN** — Qwen HTTP bypass not adapted |
| SEALED_PACKET_PROPAGATION | **OPEN** — receipt not auto-filled into sealed/exec_trace carriers |

**Artifacts:** `docs/reports/reasoning_execution_audit.md`, `docs/architecture/adr/ADR-REASONING-EXECUTION-CONTROL-f4e9a2.md`, `docs/reports/reasoning_execution_control_plane_completion_20260516.md`.

## Problem (repo reality)

Declarative reasoning configuration, prompt-layer reasoning language, orchestration knobs, and provider HTTP payloads are **not one seam**. Silent drops are plausible (especially `apps_rg` Qwen thin transport vs `SovereignLLMGateway.reasoning_kwargs` vs L0 tier tables).

## Hard constraints (non-negotiable)

- `agentic_core` stays **generic**: no `apps_rg` / `apps_*` literals, no provider-specific branching in core.
- No certification theater: **no PASS from “artifact exists.”**
- No direct L4 writes from this seam.
- No hidden authority widening: resolver may only **narrow** relative to stamped policy where applicable.

## Architectural target

```
Declarative reasoning intent (app/profile-owned)
       ↓
ReasoningExecutionPlan (generic, hashed)
       ↓
Per-control resolution { transport | prompt | orchestration | policy }
       ↓
L2 execution (single outbound callsite owns proof merge)
       ↓
ReasoningExecutionReceipt (+ AttemptReceipt linkage where applicable)
       ↓
SealedL2Artifact / Exit consumes **applied** evidence (not declared-only)
```

**Control mapping (baseline):**

| Control | Primary surface |
|---------|----------------|
| temperature, max_tokens, response_format | transport |
| cot_paths | orchestration ± prompt injection |
| tot_branches, tot_depth | orchestration |
| self_consistency | orchestration (N attempts + deterministic vote/select) |
| reflexion_loops | orchestration loop |
| scratchpad exposure | policy / PA BOM only — never raw provider param |

---

## PHASE 1 — AUDIT (no core behavior change yet)

**Deliverable:** [`docs/reports/reasoning_execution_audit.md`](../../docs/reports/reasoning_execution_audit.md)

**Must include matrix (every row populated with evidence citations):**

`CONTROL | DECLARED (where) | RESOLVED (compile-time / runtime) | APPLIED_LAYER | PROVED (receipt/field) | GAP`

**Mandatory code paths to trace (explicit files):**

1. **`ReasoningConfig` + presets** — `agentic_core/runtime/config/reasoning_types.py`, `apps_shared/types/app_config_types.py` if duplicates exist.
2. **L0 intensity** — `agentic_core/L0_routing/reasoning/reasoning_policy_engine.py`, `agentic_core/L0_routing/types/reasoning_intensity_types.py` (`TIER_PARAMETER_TABLE`, `StageTokenBudget`).
3. **L2 gateway** — `agentic_core/L2_execution/enforcement/SovereignLLMGateway.py` (`ReasoningPath`, `generate_with_reasoning`, `REASONING_PATH_TABLE`).
4. **Provider adapters** — `agentic_core/L2_execution/enforcement/_provider_local_vllm.py`, `PlaceholderProvider`/adapter v2 path: what kwargs are forwarded vs stripped.
5. **apps_rg bypass** — `apps_rg/runtime/providers/qwen_vllm_provider.py`, `section_qwen_slice`, each `*_dispatch.py` lane using `call_qwen_vllm`.
6. **Prompt M0 / meta-cognitive** — `agentic_core/prompt_governance/templates/slots/M0_meta_cognitive.jinja`, PA assembly BOM paths that hydrate ToT placeholders.
7. **L3** — `agentic_core/L3_orchestration/reasoning/engines/reflexion_engine.py`, `agentic_core/L3_orchestration/reasoning/engines/reasoning_intensity_enforcer.py`, `agentic_core/L3_orchestration/types/workflow_loader_types.py`.
8. **Receipts today** — `agentic_core/runtime/contracts/sealed_l2_artifact.py` (`provider_receipts`, `model_call_refs`), `agentic_core/L2_execution/types/l2_v3_receipts.py` and `AttemptReceipt`, `apps_rg/runtime/bindings/l2_envelope_adapter.py`.

**Exit criteria:** Audit doc merged with grep-backed citations (file:function or line anchors) — no speculative “probably.”

---

## PHASE 2 — DESIGN (contracts only PR or doc section before code)

Produce design addendum (`docs/architecture/` ADR stub or appendix in audit follow-up):

- **`ReasoningExecutionPlan`** (generic): declarative normalization target; versioning; digest; immutable after seal.
- **`ReasoningExecutionReceipt`**: **per-control** state machine: `APPLIED | DEGRADED | UNSUPPORTED | IGNORED`; **requested vs observed** payloads; linkage to provider attempt IDs.
- **Producer / consumer:**
  - **Producer:** L2 facade pre-provider-call (resolver), post-call (receipt merger).
  - **Consumer:** `SealedL2Artifact` optional extension field OR `sovereign_execution_receipt` JSON payload extension (prefer additive dataclass fields with schema version bump — avoid ballooning unstructured strings).
  - **Exit:** downstream readers must tolerate **explicit downgrade** when `IGNORED/DEGRADED` hits **required** controls.

**Invariant:** If a control is **required** by plan/policy and resolves to unsupported at runtime → **explicit non-PASS pathway** (not silent).

**RULE:** Silent ignore of declared required controls → **deterministic violation surface** (test + gate grep).

Reuse vs new: Prefer **narrow extension** of existing receipts + `SealedL2Artifact` carrier fields (`provider_receipts` already tuples) unless schema debt blocks it — justify with one paragraph in design.

---

## PHASE 3 — MINIMAL IMPLEMENT (single coherent seam; smallest diff)

Scope discipline:

1. **Generic resolver module** under `agentic_core/` — inputs are **opaque app-owned intent dict + optional L0 envelope slice** resolved via typed boundary (Protocol / structural typing); **zero** apps literals.
2. **Execution plan emission** — serialize plan + digest; attach to `CompiledPromptArtifact` or adjacent L2-bound contract carrier (prefer existing FEC thread if already plumbed — audit decides).
3. **Provider compatibility layer** — one adapter (`LOCAL_VLLM` or abstract `TransportCapabilities`) declares **capabilities bitmask** + records **stripped kwargs** into receipt.
4. **Degradation tracking** — structured list on receipt; surfaced on seal.

**Explicit non-goals in W1:** full multi-provider parity, workflow JSON rewrite, refactoring all dispatch modules.

Integration point suggestion (finalize in audit):

- Tie first proof to **`SovereignLLMGateway.generate_with_reasoning`** OR a **thin wrapper** invoked from `apps_rg` canonical path behind a single new function — second option may stay app-local if audit shows gateway unused in rg prod path.

Tests (minimum behaviors):

| Test | Behavior |
|------|----------|
| resolver | deterministic plan from fixture intent |
| provider compatibility | kwargs → recorded IGNORED/DEGRADED when adapter strips |
| receipt generation | artifact includes per-control ledger |
| exit downgrade hook | simulated required-control failure → disposition / certification ref refuses fake PASS |

**Grep proof (CI advisory or scripted):**

```bash
rg -n "apps_rg|apps_lic|apps_qna|apps_research" agentic_core/path/to/new_or_touched_generic_modules.py || true  # MUST be zero matches in new generic modules (scope-limited rg)
rg -n "uwg_write|direct.*l4" agentic_core/runtime/reasoning  # SHOULD not introduce write paths — adjust path after landing
```

---

## PHASE 4 — EXIT INTEGRATION

Touch points (read-only specification until Phase 3 proof exists):

- `agentic_core/runtime/exit/x3_disposition.py` consumes `SealedL2Artifact` — extend only with **additive** reasoning evidence digest.
- `SealedL2Artifact.l5_certification_ref`: **downgrade path** must remain fail-closed per existing verifier — extend tests so missing reasoning proof **cannot** certify full integrity if policy requires reasoning evidence.

---

## Waves (execution order)

| Wave | Deliverable |
|------|----------------|
| W1 | `docs/reports/reasoning_execution_audit.md` + matrix PASS — **DONE** |
| W2 | ADR/design addendum — **DONE** (`ADR-REASONING-EXECUTION-CONTROL-f4e9a2`) |
| W3 | Resolver + receipt + ONE provider path wired + pytest — **DONE** |
| W4 | Exit / X1D quality cap + tests — **DONE** |

---

## Open risks

- Duplicate `AttemptReceipt` definitions (`l2_package_driven_executor` vs `l2_v3_receipts`) → consolidation ambiguity.
- `SealedL2Artifact.__post_init__` certification verifier may block additive testing — may need **`INTEGRITY_PROOF`/`DEVELOPMENT_PROOF`** discipline from Fort Knox (no fake certs).
- `apps_rg` production path may bypass gateway entirely → minimal seam choice wrong if audit shows gateway dead code.

## Success criteria

- Declared reasoning intent reconciled with **transport + orchestration** actuals with **explicit** degraded ledger.
- No silent PASS when required controls unsupported.
- Grep proofs + pytest outputs archived in CI or pasted in audit appendix.

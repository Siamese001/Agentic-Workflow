# apps_rg Prompt Boundary Contract

> Authoritative slot model, airlock invariants, and receipt contract for `apps_rg` Prompt Assembly (PA). Companion to `AGENTIC_SPINE.md`. If a runtime artifact disagrees with this document, the artifact is the ground truth and this document is wrong — file an issue and update.

**Status:** Wave 2 of plan `apps-rg-spine-hardening-7e3b9c` (doc-only; no runtime code edits). Receipts and airlocks declared here are wired in W3/W4/W5 of the same plan.

## 1. Two Prompt-Injection Concepts

| Concept | What it is | Authority |
|---|---|---|
| **Instructional prompt injection** (governed composition) | Insertion of: goal · success criteria · task mode · scope · efficiency constraints · evidence binding · reasoning controls · safety rails · output schema · error format · minimality rules. | PA Prompt Assembly. Worker-side instructional mixins consumed only after PA compile. |
| **Prompt injection defense** (boundary protection) | Detection / fencing / neutralization / quarantine / rejection of untrusted content trying to override: system instructions · developer instructions · policy · route · tool selection · provider/model · schema · output format · sandbox/capability scope · write authority · HITL requirements. | PA airlock layer + `agentic_core/prompt_governance/security/`. |

> *Instructional injection is a governed composition pattern. Prompt injection defense is a boundary protection pattern. They are related but not the same.*

## 2. Slot Authority Model (S0–R0)

apps_rg PA assembles prompt artifacts using this slot order. **Authority is non-negotiable** — `S0`/`D0`/`I0`/`R0` outrank evidence, user intent, tool output, model output, and human review text.

| Slot | Content | Authority | Cannot be overridden by |
|---|---|---|---|
| **S0** | System invariants (apps_rg invariants: no fabrication, ATS coverage floor, no L4 direct write, etc.) | HIGHEST | nothing |
| **D0** | Fences, scope limits, anti-injection controls (the airlock surface) | HIGHEST | nothing |
| **I0** | Operating instructions + AgentSpec constraints (per-template) | HIGH | nothing |
| **E0** | Approved exemplars (few-shot, governed) | MEDIUM | I0 |
| **C0** | Verified evidence — JD, master résumé, company brief (data-only) | DATA-ONLY | nothing (cannot introduce instructions) |
| **M0** | Provider-safe control hints; no chain-of-thought disclosure | MEDIUM | I0 |
| **U0** | Neutralized user task intent (CLI args, wizard input, manual brief content) | DATA-ONLY | cannot override S0 / D0 / I0 / R0 |
| **H0** | Bounded repair hints (E4_HEAL re-entry only) | LOW | cannot widen route / tool / model / schema / policy / evidence / capability / sandbox |
| **R0** | Response schema binding (provider-native where supported; else PA-bound prose) | HIGHEST | nothing — cannot be overridden by user / retrieved / tool / model / human text |

**Failure modes:**

- Mandatory `S0` / `D0` / `I0` / `R0` or must-use `C0` evidence cannot fit budget → `PA_BUDGET_OVERFLOW` (fail closed). PA never silently drops mandatory authority or must-use evidence.
- Slot composition that omits R0 when structured schema binding is available → `VIOLATION_SCHEMA_ONLY_AS_PROSE` (W6 scanner).

## 3. Airlock Requirements

PA owns four named airlocks. Each is an in-band check producing a receipt. Implementation lives in W4 of plan `apps-rg-spine-hardening-7e3b9c`.

### 3.1 U0 user-text airlock

Detect and neutralize:
- "ignore previous instructions" / "you are now ..."
- "system message says ..." / "developer message says ..."
- tool override attempts
- provider/model override attempts
- schema override attempts
- policy override attempts
- output format override attempts
- markdown / HTML / XML hidden instruction blocks
- instructions embedded in job descriptions, résumés, notes, or uploaded documents

Surfaces in apps_rg: `--target-company`, `--target-role`, `--jd`, `--manual-brief`, interactive wizard input. Existing `_assert_artifact_matches_company` (`apps_rg/__main__.py:110-149`) is a cross-company contamination guard — orthogonal to and **does not replace** this airlock.

### 3.2 C0 evidence airlock

Retrieved content must remain evidence only. Detect and label:
- fake policy text inside JD / résumé / brief
- fake system / developer instructions inside JD / résumé / brief
- fake tool calls
- credential exfiltration patterns
- model / provider substitution attempts
- output-format override attempts
- instructions embedded in PDFs, websites, or notes

apps_rg surfaces: JD JSON, master résumé YAML/JSON, company brief JSON. **All three are user-controlled inputs and prime injection vectors.**

### 3.3 Tool / model output airlock

Tool output and model output are **data / proposal only**. They cannot:
- widen authority
- modify route
- change provider / model
- change tool
- alter schema
- grant write permission
- bypass HITL
- commit durable state

apps_rg surfaces: every HOP-3+ governed-template completion; narrative-pipeline ensemble + judge outputs.

### 3.4 Human review re-entry airlock

Human edits are **data until re-cleared**. They cannot directly:
- write L4
- bypass L5 evidence
- bypass Runtime Gates
- bypass Exit
- widen capability
- widen sandbox scope

apps_rg surfaces: per AGENTIC_SPINE.md `HITL Posture: False` (no runtime HITL; review is out-of-band by candidate). When out-of-band edits are re-ingested, they pass U0 + C0 airlocks like any other input.

## 4. Worker-Side Instructional Mixin Discipline

Instructional mixins (framing · context · reasoning-control · tooling-control · safety · output) may be consumed **only after**:

1. L0 `RouteContract` exists.
2. C0 `FinalEvidenceContract` exists if `grounding_required = true` (apps_rg: false; preloaded inputs only).
3. PA has compiled the provider-ready artifact (`PA_L2_HANDOFF_READY`).
4. L2 has an approved bounded work order.

Required safeguards (enforced by PA boundary helper + W6 anti-bypass scanner):

- Mixins cannot create new authority.
- Mixins cannot bypass PA.
- Mixins cannot inject retrieved / user / tool / human / model text as instructions.
- Mixins cannot override route / policy / tool / model / schema / capability / sandbox / evidence scope.
- Mixins cannot create direct L4 write behavior.
- Mixins cannot expose hidden chain of thought.

## 5. Receipts

Every PA boundary crossing emits a typed receipt. Receipts are sealed into `prompt_bom.json` per run and OTEL-spanned.

| Receipt | Emitted at | Required fields |
|---|---|---|
| `prompt_boundary_receipt` | PA enter / exit | `request_id`, `run_id`, `trace_id`, `route_id`, `policy_hash`, `blueprint_hash`, `prompt_hash`, decision status, reason codes |
| `prompt_bom_receipt` | PromptBOM resolution | BOM source refs, registry hash, template id + version |
| `slot_authority_map` | slot composition | per-slot: source ref, lineage ref, authority tier, override-ability |
| `slot_lineage_map` | slot composition | per-slot: provenance chain back to S0 / D0 / I0 / E0 / C0 / U0 / H0 / R0 origin |
| `assembly_security_pass_receipt` | airlock pass | per-airlock: detector hits, neutralization actions, deterministic digest |
| `rejected_slot_payload_report` | airlock reject | offending slot, reason code, severity, source ref |
| `token_budget_ledger` | trim/overflow | per-slot tokens consumed; fail-closed `PA_BUDGET_OVERFLOW` when mandatory exceeds |
| `provider_render_manifest` | provider-aware render | provider id, message array shape, tool definitions, response_format binding |
| `compiled_prompt_artifact_receipt` | artifact emission | `compiled_artifact_hash`, replay key, determinism digest, signing metadata |
| `instructional_mixin_receipt` | mixin consumption | mixin id, consumed-after-PA proof (compiled artifact hash present), no-authority-creation assertion |
| `injection_neutralization_receipt` | airlock neutralize | original tokens, neutralized tokens, classifier verdict (NOT `UNKNOWN`) |
| `unsafe_payload_rejection_receipt` | hard reject | payload digest, rejection reason, severity, downstream gate verdict |

Common header fields on every receipt: `request_id`, `run_id`, `trace_id`, `route_id`, `policy_hash`, `blueprint_hash`, `prompt_hash` *or* `compiled_artifact_hash`, source / lineage refs, decision status, reason codes, deterministic digest where applicable.

## 6. OTEL Spans

PA wraps these named spans (added in W5):

- `pa.boundary_check`
- `pa.prompt_bom_resolution`
- `pa.slot_composition`
- `pa.airlock_security_pass` (one per airlock — U0 / C0 / tool-model / human-reentry)
- `pa.token_budget_trim`
- `pa.provider_render`
- `pa.compiled_artifact_emit`
- `l2.compiled_artifact_consume`
- `pa.injection_neutralization`

Span attributes always include the receipt header fields.

## 7. PA Topology Reminder

apps_rg has a **dual PA topology** (see `AGENTIC_SPINE.md > Dual PA Topology`). This contract applies to **both** PA surfaces:

| Surface | File | Receipts emit at |
|---|---|---|
| NEW PA | `apps_rg/prompt_assembly/compiler.py:compile_prompt` | every `compile_prompt` invocation |
| LEGACY PA bridge | `apps_rg/utils/anthropic_rag_entrypoint.py:build_anthropic_rag_payload` (re-export `apps_rg/prompt_assembly/rg_pa_compiler.py`) | every `build_anthropic_rag_payload` invocation |
| Narrative-pipeline PA-instrumentation | `apps_rg/prompt_assembly/pa_local.py::capture_prompt_bom` (consumed by `apps_rg/integrations/hops/_llm_client.py:29`) | every BOM capture |

Both PA surfaces are PA-owned. L0 does **not** own prompt assembly.

## 8. Out of Scope

- Side-channel attacks on the inference provider (see `THREAT_MODEL.md`).
- Physical infrastructure security.
- Supply-chain attacks on the Python interpreter.
- Dormant `apps_rg/enforcement/Hardened*ExecutorStrategy.py` and siblings — explicitly excluded from the active runtime path per W1 evidence (`docs/reports/apps_rg/spine_boundary_findings_20260509_055000.md` §4B).

## 9. References

- `apps_rg/AGENTIC_SPINE.md` — canonical spine ownership invariants
- `apps_rg/THREAT_MODEL.md` — threat-actor model and trust boundaries
- `apps_rg/spine_manifest.yaml` — declared route + dual-PA surface declaration
- `docs/reports/apps_rg/spine_boundary_findings_20260509_055000.md` — W1 findings driving this contract
- `.windsurf/plans/apps-rg-spine-hardening-7e3b9c.md` — implementation plan
- `agentic_core/L1_cognition/reasoning/prompt_envelope.py` — legacy `PromptEnvelope` consumed by the LEGACY PA bridge
- `agentic_core/prompt_governance/security/` — shared injection-defense surface

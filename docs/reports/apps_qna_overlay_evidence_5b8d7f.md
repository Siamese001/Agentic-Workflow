# apps_qna Overlay Evidence Report

> **Date**: 2026-04-30
> **Scanner**: `tools/analysis/apps_spine_coverage.py` (post-W6 hardening)
> **Classification**: 🟠 **PARTIAL_SPINE_STATIC_ONLY**
> **Doctrine**: `docs/reference/APP_OVERLAY_VS_CORE_ONLY_RUNTIME.md`
> **Purpose**: Static evidence audit. **No remediation in this report.**

---

## Verdict

| Metric                                     | Value                                                 |
|--------------------------------------------|-------------------------------------------------------|
| Runtime mode                                | **PARTIAL_SPINE_STATIC_ONLY** 🟠                       |
| Canonical authority contracts imported     | **0 of 14**                                           |
| Domain runtime claimed?                    | **Yes** (integrations/, router/, `__main__.py`, `wizard.py`) |
| Spine import edges (legacy)                | 6 (mostly `agentic_core.embeddings.bge_runtime` + `agentic_core.L2_execution.utils.write_gateway`) |
| `apps_shared` imports                       | 0 (genuinely standalone — does not piggyback on apps_shared spine coverage) |
| UWG usage                                  | ✅ Yes (writes go through L2 UWG)                       |
| Meta-learning hookup                       | — (writes to apps_qna_pack_lifecycle ledger only)     |
| **Canonical contract handoff evidence**    | **❌ Zero**                                            |

**Why PARTIAL_SPINE_STATIC_ONLY rather than APP_STANDALONE_FORBIDDEN**:
apps_qna does import spine **infrastructure** (UWG `write_text`, BGE
`bge_embed_query`, ledger `emit_ledger_event`). That distinguishes it
from a pure shadow runtime. But the **authority surface** (planning,
routing, retrieval contract, prompt artifact, sealed artifact, exit
packet, commit request) is all locally constructed. apps_qna runs its
own mini-runtime; it just persists through spine plumbing.

---

## 1. Entrypoints

| File | Role |
|---|---|
| `apps_qna/__main__.py` | Package CLI entry (`python -m apps_qna ...`) |
| `apps_qna/scripts/run_qna.py` | Argparse dispatcher: build / lint / self-eval / route / init / feedback |

Both entrypoints invoke `CardPackBuilder.build()` directly without
constructing a `ValidatedRequest` or handing off through L1/L0.

---

## 2. Local planning-like logic

| Finding | File / Symbol |
|---|---|
| **None detected** | apps_qna does not have explicit "plan" classes or `plan_*` functions. |

The lack of explicit planning is a **mixed signal**: apps_qna isn't
shadow-planning, but it also isn't constructing a `L1PlanContract` and
handing off — it just skips the planning surface. The wizard
constructs an `Interview` typed payload directly, treating it as the
entire request shape.

---

## 3. Local route-like logic

| Finding | File / Symbol |
|---|---|
| `apps_qna/config/route_registry.py` — `RouteRegistry` (NOT spine `RouteContract`) | Per-domain route taxonomy (executive_fit, architecture, etc.) |
| `apps_qna/router/semantic_router.py` — `SemanticRouter` class | Bag-of-words cosine routing of incoming questions to routes |
| `apps_qna/router/route_bandit.py` — `AppsQnaRouteBandit` | W4.1 NamespaceBandit wrapper. Imports `agentic_core.L0_routing.reasoning.namespace_bandit.NamespaceBandit` — but this is the **algorithm**, not the spine route authority. |
| `apps_qna/router/paste_bandit.py` — `AppsQnaPasteBandit` | W4.2 paste-set bandit. Same pattern as W4.1. |
| `apps_qna/router/route_seeding.py` — `seed_likely_questions_from_research` | Seeds priority order. |

**Verdict**: apps_qna OWNS routing decisions for likely_questions
priority order. **No `RouteContract` is ever produced or consumed.**
The spine's L0 router is never invoked.

---

## 4. Local retrieval-like logic

| Finding | File / Symbol |
|---|---|
| `apps_qna/integrations/spine_adapter.py` — `classify_section_topic` | Calls `agentic_core.embeddings.bge_runtime.bge_embed_query` directly — uses the embedding **primitive**, not the L1 retrieval authority. |
| `apps_qna/integrations/from_research_brief.py` — `_paragraph_topic_segmentation` | Local topic-segmentation logic for PDF text. |
| `apps_qna/integrations/depth_anchor_synth.py` — `synthesize_cross_exam_anchors` | Local ranking via `classify_section_topic`. |
| `apps_qna/integrations/architecture_synth.py` — direct SQLite query of ADG snapshot | §28 SQLite-direct fallback (compliant) — but no `FinalEvidenceContract` emitted. |

**Verdict**: apps_qna performs retrieval but never wraps the result in
a `FinalEvidenceContract`. The spine's C0 retrieval authority is
bypassed; apps_qna treats embeddings as a library, not as a delegated
authority.

---

## 5. Local prompt-assembly-like logic

| Finding | File / Symbol |
|---|---|
| `apps_qna/builder/card_pack_builder.py` — `CardPackBuilder` class | Owns the entire 22-card render pipeline. |
| `apps_qna/templates/*.md.j2` (Jinja2) | Per-card templates. |
| `apps_qna/builder/card_pack_builder.py` — `_render`, `_render_all`, `_base_context` | Local prompt-shape composition. |

**Verdict**: apps_qna OWNS the entire prompt-assembly surface for the
card pack. **Zero `CompiledPromptArtifact` or `PromptEnvelope`
produced.** Spine PA is bypassed entirely. (Note: the cards ARE the
prompt — they get pasted into ChatGPT — but the spine has no view into
this prompt-assembly process.)

---

## 6. Local execution-like logic

| Finding | File / Symbol |
|---|---|
| `apps_qna/builder/card_pack_builder.py` — `CardPackBuilder.build()` | Entire end-to-end execution: render → write → manifest → ledger emit. |
| `apps_qna/integrations/wizard.py` — `run_wizard()` | Interactive composition + write. |
| `apps_qna/scripts/run_qna.py` — `_run_build`, `_run_init`, `_run_feedback` | CLI orchestrators. |

**Verdict**: apps_qna OWNS bounded execution. No `SealedArtifact` is
constructed. No `ExitReviewPacket` is emitted. The build's "final
disposition" is a `CardPackManifest` — a local domain object, not a
spine contract.

---

## 7. Local durable-write / memory-like logic

| Finding | File / Symbol | Spine routing? |
|---|---|---|
| `card_pack_builder.py` → `spine_adapter.write_card_text` | UWG-routed | ✅ Yes (W1.2) |
| `wizard.py` → `spine_adapter.write_card_text` | UWG-routed | ✅ Yes (W1.4 fix) |
| `flywheel.py` → `spine_adapter.write_card_text` | UWG-routed | ✅ Yes |
| `architecture_synth.py` → `sqlite3.connect(file:...?mode=ro)` | Read-only ADG query, §28-compliant | ✅ Yes |
| `learning_adapter.py` → `sqlite3.connect(file:...?mode=ro)` | Read-only ledger replay | ✅ Yes |
| `memory_writeback.py` → `sqlite3.connect(file:...?mode=ro)` | Read-only ledger walk | ✅ Yes |
| `promotion_gates.py` → `sqlite3.connect(file:...?mode=ro)` | Read-only ledger aggregation | ✅ Yes |

**Verdict**: All durable writes go through UWG; all SQLite reads are
direct §28-compliant. **But: zero `CommitRequest` constructed.** The
spine's L4 admission contract is bypassed; UWG's atomicity is used as
a side-effect, not as a contracted handoff.

---

## 8. Local learning-like logic

| Finding | File / Symbol | Spine routing? |
|---|---|---|
| `learning_adapter.py::record_rehearsal_outcomes` | Calls `bandit.update_outcome` (which calls spine NamespaceBandit) | Partial |
| `learning_adapter.py::replay_outcomes_into_bandit` | Walks ledger, replays via `bandit.update_outcome` | Partial |
| `flywheel.py::compute_flywheel_defaults` | Aggregates ledger; emits snapshot | Local |
| `memory_writeback.py::distill_patterns` | Distills cross-interview patterns | Local |
| `promotion_gates.py::evaluate_promotion` | Wraps spine `wilson_interval` + `promotion_decision` | Wraps spine algorithm, but no `RuntimeExhaustBundle` |

**Verdict**: apps_qna performs current-run learning AND post-run
distillation. **Zero `RuntimeExhaustBundle` is emitted to L6.** Spine
L6 is informed only by the ledger writes, not by a contracted handoff.

---

## 9. Missing spine contracts (the gap)

| Required for | Contract | apps_qna emits? |
|---|---|---|
| Planning handoff | `L1PlanContract` | ❌ No |
| Route authority | `RouteContract` | ❌ No (uses domain `RouteRegistry` instead) |
| Retrieval authority | `FinalEvidenceContract` | ❌ No |
| Prompt artifact | `CompiledPromptArtifact` / `PromptEnvelope` | ❌ No |
| Bounded execution | `SealedArtifact` | ❌ No |
| Final disposition | `ExitReviewPacket` | ❌ No |
| Durable write admission | `CommitRequest` | ❌ No (UWG used as primitive) |
| Post-run learning handoff | `RuntimeExhaustBundle` | ❌ No |
| Validated intake | `ValidatedRequest` | ❌ No |

**All 9 authority handoffs missing.** This is the canonical
fingerprint of `PARTIAL_SPINE_STATIC_ONLY`: the app uses spine
infrastructure but holds the runtime authority locally.

---

## 10. Adapter / wrapper candidates

If apps_qna were to migrate to APP_OVERLAY_VALID, the smallest viable
seam would wrap the existing `CardPackBuilder.build()` in a thin
adapter that:

1. **Constructs a `ValidatedRequest`** from `Interview` YAML
2. **Hands off to a spine L1 → L0 → C0 → PA pipeline** that:
   - Emits `L1PlanContract` (the typed plan: which cards, which routes, which paste budget)
   - Emits `RouteContract` (the chosen build route — single vs. panel mode)
   - Emits `FinalEvidenceContract` (the resolved Interview content + research brief)
   - Emits `CompiledPromptArtifact` (the rendered cards as the artifact)
3. **Wraps the pack render in a `SealedArtifact`**
4. **Emits an `ExitReviewPacket`** at the boundary that currently emits the manifest
5. **Wraps each filesystem mutation in a `CommitRequest`** (instead of calling UWG functions directly)
6. **Emits a `RuntimeExhaustBundle`** at post-run for L6 calibration

The ledger writeback (W1.4 + W5.1) would then become an ARTIFACT of
that handoff, not the only durable record.

**Smallest safe integration seam**: introduce a single new file
`apps_qna/integrations/spine_handoff.py` that:

- Defines `def build_pack_via_spine(interview, ...) -> SealedArtifact`
- Imports `ValidatedRequest`, `L1PlanContract`, `RouteContract`,
  `SealedArtifact` from `agentic_core.*`
- Constructs them deterministically from the `Interview` typed input
- Calls `CardPackBuilder.build()` from inside the spine-handoff envelope
- Returns the `SealedArtifact` to the caller

Even an MVP version (just `ValidatedRequest` + `SealedArtifact`) would
flip apps_qna to APP_OVERLAY_VALID. Real value requires all 9 contracts.

---

## 11. Recommended next action

1. **Do not begin large remediation yet.** The user's instruction is
   explicit on this: produce evidence first.
2. **Decide whether apps_qna SHOULD be APP_OVERLAY_VALID** or whether
   PARTIAL_SPINE_STATIC_ONLY is acceptable for a build-time document
   compiler. The doctrine says any app that claims a domain runtime
   must delegate; build-time tools are a gray zone.
3. **If APP_OVERLAY_VALID is the goal**, the smallest scope is the
   `spine_handoff.py` MVP above (~6K tokens). It would NOT replace any
   existing functionality; it would WRAP the existing build path in a
   contracted handoff so the spine has a delegation receipt.
4. **If PARTIAL_SPINE_STATIC_ONLY is acceptable**, formalize that
   decision in an ADR and add a §31-style allowlist entry for
   build-time document compilers. apps_qna is not the only app in this
   bucket — 7 of 9 apps_* are PARTIAL — and they may all need the
   same architectural decision.

---

## See also

- `docs/reference/APP_OVERLAY_VS_CORE_ONLY_RUNTIME.md` — doctrine
- `tools/analysis/apps_spine_coverage.py` — scanner
- `tests/unit/tools/analysis/test_apps_spine_coverage.py` — classification tests
- `docs/reports/apps_runtime_mode_scorecard.md` — full scorecard for all 9 apps_*
- `.windsurf/plans/apps-qna-spine-integration-e8f3a1.md` — the previous (now-shipped) integration plan whose efforts created the ledger/UWG/BGE infrastructure surface but DID NOT add canonical authority contracts

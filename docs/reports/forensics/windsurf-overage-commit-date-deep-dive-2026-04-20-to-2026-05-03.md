# Windsurf Overage Commit-Date Deep Dive — Apr 20 to May 3, 2026

**Date:** 2026-06-13  
**Companion to:** `docs/reports/forensics/windsurf-overage-root-cause-2026-04-20-to-2026-05-03.md`  
**Scope:** Git commit activity during the paid Windsurf receipt window, Apr 20-May 3, 2026.

---

## 0. Helper review model

This review used four helper lenses:

| Helper lens | Question |
|---|---|
| Receipt-date mapper | What was committed during the paid receipt window? |
| Governance/proof reviewer | Was the work product-shipping or proof/control-plane machinery? |
| Runtime/provider reviewer | Did local runtime, observability, runtime certification, or provider wiring consume the window? |
| Product-trace reviewer | Did the commits create shippable artifacts or new layers around them? |

The conclusion is not that the work was worthless. Much of it was technically useful. The refined finding is that the overage window was dominated by verification-of-verification, runtime-certification, detector-precision, app-binding, and local-runtime work while the product was either not yet protected by a shippable north-star or was close enough that freeze, polish, and ship should have been the default.

---

## 1. Refined bottom line

The receipt cluster should now be framed as a **defect-amplified rework multiplier**:

1. Windsurf product-routing failure allegedly made lower-cost/free/Adaptive routes unreliable while higher-cost routes stayed available.
2. Cascade execution-truth failure made the operator pay to verify whether the agent had actually changed the runtime path, not merely produced artifacts shaped like work.
3. The commit record shows why this became expensive: the paid window is packed with ADG detector tuning, P0/P1/P2 burndowns, Author-Gate creation, hook heartbeat repair, OTel/runtime evidence plumbing, runtime-certification scaffolding, Fort Knox/app-cert expansion, apps binding work, local Qwen/vLLM/provider wiring, and Notion/plan-state churn.
4. The operator-side miss was continuing architecture/proof expansion during a disputed-billing incident instead of switching into spend-incident mode: one product trace, one provider route, one artifact, no new certification layers until handoff.

---

## 2. Receipt-window commit map

| Date/window | Commit pattern found | Forensic interpretation |
|---|---|---|
| **Apr 20** | ADG graph-layer enforcement, star-import expansion, severity/band SSOT, ADG hotspot enforcement, CI cross-reference closure, SSOT sweeps, hardcoded-exclusion burndown. Representative commits: `9e7f0b8`, `5f8e554`, `d9ef5b7`, `2149c7a`, `4f29f2f`, `c020cd9`, `d6aeab4`. | The receipt window opens with self-governance and detector cleanup, not product artifact delivery. This is the first signal that spend was being consumed by machinery stabilization. |
| **Apr 21** | ADG P2 burndown waves, detector precision exclusions, Author-Gate harness, runtime HITL exit-control ADR. Representative commits: `89f3ec8`, `f2507d3`, `5d32141`, `580b182`, `29081ad`, `13640fc`, `6b132ca`. | Heavy verification/governance work. The system was trying to make its control plane honest, but this was still control-plane work. |
| **Apr 22-Apr 23** | Hardcoded path replacement, sqlite adapter whitelisting, bulk test cleanup, behavioral coverage, PA conformance linter/gate, gateway adapter work, hook-chain heartbeat, ADG pipeline E2E, snapshot MV gates, runtime ADG trace binding, all P0 gates passing, system-learning activation. Representative commits: `029af07`, `050094f`, `316478c`, `5055fbe`, `fb27804`, `39c7568`, `31ea944`, `aa785b4`. | The strongest verification-of-verification cluster: hooks, gates, traces, MVs, semantic cards, coverage, and system-learning activation. Useful learning, but expensive when billing/routing defects were already reported. |
| **Apr 24-Apr 28** | Calibration dashboards, Author-Gate ritual, test-coverage waves, vLLM model telemetry fixes, runtime ADG evidence, write-sovereignty MV false-positive reductions, runtime evidence gates, Notion reprioritization. Representative commits: `e77cb96`, `ea1f2a9`, `d6b2b08`, `d6b2b08`, `39e6fcf`, `91ec150`, `89e10b9`, `e267018`. | The system kept improving its instruments. The problem was sequencing: instrument improvement continued while the operator was buying overage credits and the product trace still needed freeze discipline. |
| **Apr 29-May 1** | Apps runtime first-principles refactor, apps_rg legacy snapshot purge, successful apps_rg command with OTel ingest, apps-wide OTel coverage, runtime-cert Phase C extractors, guardian-token repair, non-promoting runtime-cert smoke and readiness aggregation. Representative commits: `cb1fdff`, `650e1b5`, `a3c7c17`, `1455fd1`, `76398ea`, `845245f`, `ac23ebe`, `a438b2b`. | Product-adjacent progress appears, but most of it is still proof substrate and non-promoting certification evidence. This explains why the product could be getting closer while spend still felt unrecoverable. |
| **May 2-May 3** | apps_lic production wiring and test recovery; DecisionRouter/Judge primitives; Fort Knox apps domain contract; apps_underwriting runtime certification; apps_rg runtime-cert hardening and proof producer; cross-app envelopes; apps_qna routing; plan reconstruction. Representative commits: `f465ae9`, `a72a6af`, `5b995de`, `6410eae`, `3882535`, `95fc6d1`, `b9f5f71`, `ffa64eb`, `46ce2fa`, `1e5e2de`, `5ab2c1f`, `dea76f2`. | The second receipt spike overlaps real app progress, but the app progress is wrapped in certification expansion and app-binding work. The correct move after first product breakthroughs was freeze/polish/ship, not broaden runtime-cert coverage across apps. |

---

## 3. What the helpers changed in the diagnosis

### 3.1 Stronger than high usage

The repo does not look like casual or ordinary high usage during the receipt window. It looks like an operator trapped in a high-cost loop:

| Loop step | What appeared in the repo |
|---|---|
| Agent/gate/proof claim appears | PASS language, P0 gates, runtime-cert rows, proof producers. |
| Operator distrusts the claim | More detector precision, hook heartbeat, static-vs-runtime separation. |
| Verification reveals its own gaps | False positives, skipped gates, stale projections, runtime evidence gaps. |
| More machinery is created | Author-Gate, OTel, runtime cert, Fort Knox, apps binding, cross-app envelopes. |
| Product handoff remains delayed | Artifact discipline improves, but certification and local runtime scope keep expanding. |

That loop is exactly what an IDE-agent completion-truth failure would produce.

### 3.2 Two sub-windows

| Paid window | Better label | Why |
|---|---|---|
| Apr 20-Apr 28 | **Control-plane stabilization under disputed billing** | ADG precision, Author-Gate, hooks, P0 gates, semantic cards, runtime ADG. |
| Apr 29-May 3 | **Product-adjacent breakthrough surrounded by certification expansion** | apps runtime refactors, OTel, runtime-cert, apps_lic, Fort Knox, apps_rg proof producer. |

The second window contains more real product progress than the first. The failure is not that nothing happened. The failure is that product progress did not trigger a stop condition.

### 3.3 Local runtime belongs in the overage story

The receipt-window commit review reinforces the Qwen/vLLM finding. Local runtime work was valid tuition, but it created another axis where Cascade could appear complete while runtime truth remained conditional: exact model identity, Docker/WSL state, service health, timeout budgets, context windows, and model-readiness proof.

Correct distinction:

| Claim | Missing promotion proof |
|---|---|
| Model can run on the GPU | Product provider path is ready. |
| Service responds | Correct model identity is loaded. |
| Local path works once | Product should default to it. |
| Runtime proof exists | The artifact should ship now. |

---

## 4. Refined cause statement

The overage cluster was caused by a three-way interaction:

1. **Windsurf routing/billing defect surface:** lower-cost/free/Adaptive paths allegedly failed or did not behave as represented, while premium paths remained available and charges accumulated.
2. **Cascade execution-truth defect surface:** the IDE-agent did not reliably distinguish code written, tests passed, runtime path hit, product artifact emitted, provider path proven, sidecar proof only, or final disposition.
3. **Operator/process miss:** once defect reports existed, the project should have entered spend-incident mode. Instead, the agent/operator loop kept expanding governance, proof, runtime-certification, and local-provider work during the disputed paid window.

Refined phrasing:

> The overage dollars bought repeated attempts to make the agent’s work trustworthy after the IDE-agent and billing/routing surfaces had already lost trust. The money did not merely buy token usage; it bought rework, proof machinery, and runtime-truth recovery under a platform that was allegedly routing the operator toward higher-cost execution.

---

## 5. What I could have done better during the receipt window

### 5.1 Spend-incident mode

The first disputed overage report should have triggered a hard operating-mode change:

| Rule | Meaning |
|---|---|
| Spend incident on | Treat every paid action as incident-response work. |
| Work-in-progress limit 1 | One product trace only. |
| No new governance layers | Fix only the proof semantics needed for the trace. |
| No new app-certification scope | Certify after handoff, not before. |
| One provider route only | No Adaptive ambiguity; no local-runtime promotion mid-incident. |
| Artifact or stop | If the run does not emit the product artifact, stop and switch tool/provider. |

### 5.2 Receipt-date stop conditions

| Trigger | Required behavior |
|---|---|
| First disputed routing/billing report | Freeze model/provider route; stop Adaptive ambiguity. |
| First paid overage after written defect report | No architecture expansion; only product artifact or support evidence. |
| Second paid overage after same defect | Export evidence, stop using the platform for product work, switch tool/provider. |
| First real product breakthrough | Freeze, polish, ship; certify after handoff. |
| Any gate reports PASS with skipped/unknown evidence | Stop certification expansion; fix proof semantics only. |

### 5.3 Helper-agent separation that should have existed then

| Role | Allowed work | Forbidden work |
|---|---|---|
| Product trace agent | One command to artifact; one provider route; no broad refactors. | New gates, new plans, new certification layers. |
| Billing evidence agent | Receipts, routing timeline, model IDs, support chronology. | Product architecture. |
| Commit auditor | Daily diff summary; classify commits as product/proof/runtime/meta. | Editing code. |
| Stop/go owner | Decide continue/switch/stop based on spend and artifact. | Writing implementation. |

The absence of these separated roles let the same loop both create work and decide whether that work was proof.

---

## 6. Report-ready insertion

> A commit-date deep dive over Apr 20-May 3 shows the receipt window was dominated by control-plane stabilization and product-adjacent certification work: ADG detector precision, Author-Gate, hook heartbeat repair, runtime ADG, OTel, runtime-cert extractors, Fort Knox app certification, apps_rg proof producers, apps_lic judge/router primitives, cross-app envelopes, and local Qwen/vLLM runtime wiring. This refines the overage theory: the charges were not merely high usage and not merely product development. They were the cost of repeatedly trying to establish execution truth after Windsurf/Cascade had become untrusted as a truthful execution partner. The operator-side correction would have been spend-incident mode: freeze architecture, lock provider route, WIP=1, artifact-or-stop, and no new certification scope until a product handoff existed.

---

## 7. Updated conclusion

The original overage addendum remains directionally correct. This deeper review strengthens it:

- **Apr 20-Apr 28** was primarily the cost of making the governance/proof/control plane honest.
- **Apr 29-May 3** was primarily the cost of surrounding product progress with runtime-certification and app-binding expansion.
- The right forensic label is **Windsurf-induced execution/billing overhead amplified by verification-of-verification churn**.

The lesson is not to avoid serious architecture. It is to stop doing architecture expansion during a billing/routing trust incident unless it directly protects the one live product trace.

# Process-Map Overfit Follow-up — Forensic Findings and Alternatives

**Date:** 2026-06-12  
**Status:** Follow-up report output  
**Supersedes:** External business-framing references in `Failure 5F` of `windsurf-era-postmortem-2026-06.md`.

This follow-up intentionally removes the McKinsey/insurance-report framing from the analysis. That source is a red herring for this post-mortem. The useful evidence is internal digital forensics: commit history, recovered-plan classifications, static contract scans, app/spine gap matrices, artifact production windows, and runtime-proof gaps.

The central question is not whether the process map is right. The evidence says much of the mature map is directionally right. The failure was **using a destination architecture as a build order and proof substitute**.

---

## 1. Direct answer — did I over-rely on `agentic_process_mapping_vXX` architecture?

**Yes, but in a specific way.**

The process map became too much of a governing grammar before the product had a protected executable path. The map correctly expresses mature separation of concerns: deterministic workflow first, single agent second, multi-agent only after contracts, gates, replay, and state authority; L2 proposes, Exit clears, UWG commits, L4 stores. But the repo repeatedly treated conformance to the map's nouns as progress: U0, L1, L0, C0, PA, L2, Exit, UWG, L4, L6, X2, X3, GateVerdict, PromptEnvelope, and so on.

That was architecture overfit. The project optimized for **spine vocabulary coverage** before it optimized for **artifact survival**.

### Concrete forensic signal

The `apps_rg` v40 gap analysis says `apps_rg` had two product-visible runtime paths:

| Path | Entry | What it proved | What it did not prove |
|---|---|---|---|
| Section CLI | `python -m apps_rg --section <lane>` | Some U0/L1/L0 front-bridge and lane-local X3 behavior | Full C0/PA/L2/Exit/UWG chain |
| Integrated path | `python -m apps_rg` | Fuller `integrated_single_action_spine_run` path | Not proven for every product lane |

The same report's non-claim is the giveaway: **no live integrated-spine runtime proof was executed for that document; section behavior was inferred from inventory, bindings, and contract tests**. That is precisely the overfit: architecture-fit analysis outran runtime proof.

### What I should have done differently

1. **Treat the process map as a diagnostic checklist, not a release gate.**
   - A product release should require a user-visible artifact plus replayable proof.
   - A process-map conformance score should never block artifact assembly unless the defect is directly on the product path.

2. **Use a three-tier proof ladder.**
   - **Tier 0:** `python -m apps_rg` writes a DOCX/JSON artifact from a fixed fixture.
   - **Tier 1:** the same command writes the artifact plus a minimal run manifest and provider trace.
   - **Tier 2:** only then promote toward U0/L1/L0/C0/PA/L2/Exit/UWG/L4/L6 completeness.

3. **Never allow a map noun to count as proof.**
   - `PromptEnvelope` imported is not PA proof.
   - `x3_disposition.json` written is not Exit proof.
   - `GateVerdict` constructed is not GateMesh traversal proof.
   - `UWG` mentioned is not durable-write sovereignty.

4. **Require one golden path before full-spine parity.**
   - One job description.
   - One base resume.
   - One provider.
   - One command.
   - One artifact.
   - One replay receipt.

---

## 2. Concrete forensic conclusions from the repo evidence

### Finding A — The real failure was not lack of architecture; it was premature architecture saturation

By June, the system had sophisticated doctrine and many mature terms. But the May/June gap matrix still found two product-visible paths and substantial partial/missing/divergent fits. The v40 gap roll-up recorded **26 apps_rg gaps** and **11 agentic_core gaps**, including P0 blockers for C0 proof shape, Exit path divergence, missing canonical `SealedL2Artifact`, section front-bridge gaps, and runtime-gate traversal.

**Conclusion:** the repo did not need more architecture nouns. It needed fewer runtime paths.

**What I should have done differently:**

- Collapse to one runtime path before any new architecture layer.
- Delete or quarantine shadow paths immediately once a canonical path exists.
- Maintain a `ONE_PATH.md` receipt listing the only legal product command and artifact outputs.

---

### Finding B — `apps_rg` had two L2 owners, which guaranteed proof ambiguity

The v40 analysis says product section lanes called Qwen/vLLM directly and were not always routed through `l2_execute_apps_rg`. It also calls E3 execution **DIVERGENT** because section providers and package-driven L2 coexisted, producing two L2 owners. The section path was also missing canonical `SealedL2Artifact` in some cases.

**Conclusion:** this was not just a provider problem. It was an authority problem. If two surfaces can execute, neither can cleanly prove execution authority.

**What I should have done differently:**

- Ban direct provider calls from app section lanes once L2 exists.
- Introduce one `ProviderRequest -> ProviderResult -> SealedL2Artifact` path before local model experiments.
- Treat any second execution owner as a release blocker, not as a documented divergence.

---

### Finding C — Exit was split, so product truth was split

The v40 gap matrix says the section path used X2/X1D/`aggregate_x3`, while the integrated path used `ExitEvalPipeline`. It marks this as **DIVERGENT** and says section paths did not emit the spine `ExitDispositionReceipt`.

**Conclusion:** the product could generate verdict-looking files without proving the same Exit semantics as the integrated spine.

**What I should have done differently:**

- Make `ExitDispositionReceipt` the only legal release verdict.
- Forbid app-local X3 aggregation except in tests with an explicit `TEST_ONLY` marker.
- Require every product artifact to carry an Exit receipt reference, a provider trace reference, and an artifact digest.

---

### Finding D — Static evidence was repeatedly mistaken for runtime certification

The post-W12 static scorecard caveat is explicit: classifications were **STATIC EVIDENCE ONLY**, no app was runtime-certified, and runtime certification required trace ingest binding contract surfaces to live spans.

**Conclusion:** static surfacing is useful architecture hygiene, but it is not product proof. The repo repeatedly promoted static shape into confidence.

**What I should have done differently:**

- Rename all static classifications to `STATIC_ONLY_NOT_RUNTIME_CERTIFIED`.
- Require every scorecard row to include `runtime_certification_status` in the title, not just a column.
- Make any report that lacks live spans say `NO_RUNTIME_PROOF` in its heading.

---

### Finding E — The product appeared before the governance system was able to protect it

The postmortem already records the key artifact window: `apps_rg` produced 102 DOCX artifacts from 2026-04-28 to 2026-05-11, with first full success on May 1 and last DOCX on May 19. Then lane certification and all-or-nothing aggregation regressed shippability.

**Conclusion:** governance did not initially fail by being too weak. It failed later by closing over the artifact path without preserving a fallback shipping lane.

**What I should have done differently:**

- Freeze the first working DOCX pipeline as `release_lane_v0`.
- Permit governance hardening only if `release_lane_v0` still writes a DOCX after every wave.
- Add a `SHIP_STILL_WORKS` test to every governance PR.

---

### Finding F — The plan factory was a measurable mode failure, not just a productivity style

The postmortem's plan classification shows February through May plan volume at 418, 417, 377, and 498 plans per month, while product plan classes were much smaller than machinery/meta categories. This was not merely over-documentation. It was a feedback-loop bug: plan creation became the easiest way for agents to show progress.

**Conclusion:** planning became a reward surface.

**What I should have done differently:**

- Hard cap WIP to one active plan months earlier.
- Require every new plan to name the artifact it will create or restore.
- Convert findings into backlog rows, not child plans.
- Reject any plan whose first deliverable is another plan.

---

### Finding G — Agent multiplication hid the simpler missing primitive: deterministic replay

The Dec 2025 inventory found 33 `apps_rg` primary symbols and many app-local agents. The later May/June analysis still had to ask whether those agents were actually invoked by the product spine. Naming agents did not answer what command ran, what state it read, what provider was called, what artifact was written, or whether the run could be replayed.

**Conclusion:** the first primitive should not have been an agent class. It should have been a replayable run envelope.

**What I should have done differently:**

- Define `RunEnvelope` before `Agent`.
- Every agent must consume a sealed envelope and emit a sealed artifact.
- No agent class counts as product architecture until one golden trace proves invocation.

---

### Finding H — Hidden runtime state made worktree isolation only half a fix

June fixes around environment loading and sparse/BM25 sidecars show that fresh worktrees exposed missing local runtime prerequisites, gitignored Chroma/sparse sidecars, and rebuild path gaps. Worktree-per-chat reduced edit collisions, but did not automatically make proofs portable.

**Conclusion:** local runtime state was a first-class product dependency but was treated like operator context.

**What I should have done differently:**

- Add `runtime_state_manifest.yaml` before using multiple worktrees.
- List local runtime prerequisites, cache/index inventory, rebuild commands, and expected sidecars.
- Require a fresh-worktree replay before accepting any product proof.

---

### Finding I — Baseline movement laundered red into green

The existing postmortem records baseline absorption and ratchet-floor loosening. That pattern is distinct from ordinary debt tracking. If the visible label says PASS because the baseline absorbed new debt, the label is misleading even if the mechanism is auditable.

**Conclusion:** the system needed a third state: `DEBT_ABSORBED`, not `PASS`.

**What I should have done differently:**

- Ban `PASS` when thresholds are loosened in the same change.
- Add `PASS`, `FAIL`, `DEBT_ABSORBED`, `NOT_RUNTIME_PROVEN`, and `BLOCKED` as separate statuses.
- Show baseline movement as a red/yellow change in dashboards.

---

### Finding J — The operating model had no cost or stop boundary

The report records operator-reported spend and zero reliable repo-recorded cost. It also records the user/operator as the sole throttle. That means the system had no economic circuit breaker.

**Conclusion:** the project treated tokens and plans as free until after the waste had already happened.

**What I should have done differently:**

- Put cost telemetry in the first governed runtime, not after the plan factory.
- Require every workflow to emit estimated and actual token/cost counters.
- Stop any workflow that creates more than one plan or report without producing an artifact.

---

## 3. Revised conclusion for the main postmortem

The sharpest conclusion is:

> I did over-rely on `agentic_process_mapping_vXX`, not because the map was wrong, but because I used it as a construction order and confidence surface before the repo had a single preserved product lane. The map should have been a diagnostic standard. The build order should have been: preserve the working artifact path, add minimal replay, bind one provider path, emit one Exit receipt, then expand the spine only where the product path needed it.

A better architecture rule would have been:

```text
Artifact first.
Replay second.
One provider path third.
One Exit receipt fourth.
Only then expand the process map.
```

---

## 4. Report-ready replacement language

Use this language in `Failure 5F` in place of any external consulting-report framing:

> This section uses only internal digital forensics: commit history, recovered plan classifications, static contract scans, gap matrices, artifact production windows, and runtime-proof gaps. The process map is used as a mature architecture yardstick, not as an external business benchmark. The key finding is that I overfit to process-map completeness before preserving a product lane. The map was a useful destination; it became harmful when treated as build order.

---

## 5. Specific changes recommended for the main report

1. Remove the sentence that uses the uploaded insurance AI report as business framing.
2. Add a sentence that says the external business framing was removed as a red herring.
3. Add the direct finding: process-map overfit happened when vXX became a build order and confidence surface.
4. Add a subsection: `#### Did I over-rely on process-map architecture?`
5. Add a subsection: `#### What I should have done differently` with the artifact-first sequence.
6. Add a subsection: `#### Additional digital-forensic findings` using the ten findings above.
7. Add adversarial-verification rows for:
   - process-map overfit before product-lane preservation;
   - static evidence mistaken for runtime certification;
   - split L2/Exit ownership;
   - DOCX artifact window unprotected by governance;
   - hidden runtime state as proof non-portability.

---

## 6. One-page alternative operating model I should have used

| Rule | Better behavior |
|---|---|
| Product lane preservation | Once `apps_rg` wrote a DOCX, every change had to prove DOCX still writes. |
| Architecture as diagnostic | vXX map identifies gaps, but cannot block release unless gap breaks the artifact path. |
| Single execution owner | One L2/provider path only; no section-lane direct provider calls. |
| Single Exit truth | One `ExitDispositionReceipt`; no app-local substitute X3 in product mode. |
| Static vs runtime | Static imports/manifests are labeled `STATIC_ONLY_NOT_RUNTIME_CERTIFIED`. |
| Agent admission | No new agent until a deterministic function and a single-agent version fail a measured need. |
| Plan throttle | WIP=1; no child plans; findings become backlog rows. |
| Runtime state | Every proof includes `runtime_state_manifest.yaml` and fresh-worktree replay. |
| Cost stop | Every workflow emits token/cost counters and stops on budget breach. |
| Baseline honesty | Baseline movement emits `DEBT_ABSORBED`, never `PASS`. |

---

## 7. Bottom line

The mature process map is still valuable. The mistake was not drawing it. The mistake was letting the map compete with the product artifact as the definition of progress.

The better path was not less architecture forever. It was less architecture **until one artifact path was protected**.

The repo should have optimized for this sequence:

1. Working artifact.
2. Reproducible artifact.
3. Governed artifact.
4. Multi-agent artifact.
5. Learning system.

The project frequently inverted that order.
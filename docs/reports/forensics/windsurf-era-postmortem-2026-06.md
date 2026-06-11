# The Apprenticeship Ledger: A Forensic Post-Mortem of Eight Months, ~9,800 Commits, and ~2,400 Plans

**Date:** 2026-06-11
**Scope:** Full project history, 2025-10-09 → 2026-06-10 (GitHub web-UI era → Codex era → Windsurf era → Cursor era → Claude Code era)
**Author's objective (stated, and the lens for this report):** *master agentic architecture by building a best-in-class resume shipper* — starting from zero programming and zero AI knowledge in September 2025.

---

## 0. Method and provenance

- **2,479 plan documents classified individually** (header of every plan read, not sampled) into 10 categories, via an 86-agent forensic workflow (run `wf_cfda8f23-c2e`, ~12.7M subagent tokens, 2,878 tool calls).
- **Nine git-archaeology passes** over the full 9,757-commit history.
- **45 exemplar quotes** mined from the recovered corpus.
- **Six headline claims adversarially verified** by independent agents instructed to refute them; two of the author-agent's own claims were corrected as a result (see §5).
- **Corpus recovery:** 1,731 plans that ever existed in `.windsurf/plans/` and `docs/reports/plans/` were recovered from git history with authorship dates (`windsurf-plans-recovered/manifest_enriched.csv`, copied alongside this report). 1,123 of them exist nowhere in the current tree.
- **Spend caveat:** the ~$10K figure is operator-reported. The repo contains **$0.00 of recorded spend** — a USD pricing table was committed 2026-04-30 with zero consumers and zero output artifacts; total token telemetry across the entire project covers ~201 turns. That absence is itself a finding (§3, Failure 5).

---

## 1. The headline ledger

Under the *mastery* objective, the 2,479 plans split into three ledgers:

| Ledger | Classes | Plans | Share | Verdict |
|---|---|---:|---:|---|
| **Tuition (mastery-aligned)** | Agentic-core architecture (527), ADG graph engineering (284), infra/tooling (227), basics (19) | ~1,057 | 43% | Largely defensible. The L0–L6 spine, the dependency graph, the local 32B inference stack — this *was* the curriculum, and the learning arc (web-uploader → fleet operator in 8 months) is the proof artifact. |
| **Product attempts** | apps_rg (174), apps_lic (80), other apps (161) | 415 | 17% | The vehicle. Reached 8/11 certified lanes on 2026-06-10 — a real near-miss, not failure theater. |
| **Dead weight under *either* objective** | Meta-governance (398), receipts-as-ceremony (273), rework of destroyed work (336) | ~1,007 | 41% | Taught nothing about agentic architecture *and* shipped nothing. Plans about plans, receipts that lied and then receipts about receipts, three migrations of the same rulebook, re-purchase of work the machine destroyed. **This is where the money died.** |

Cross-cutting signals across the corpus: **421** plans reference mock/stub/dry-run-as-proof problems; **283** contain RCA/incident content; **495** contain supersession/duplication churn. An adversarial verifier independently random-sampled 30 plans and reproduced the machinery:product imbalance at 4.5–6:1 (claimed ratio 3.1:1 — the claim is, if anything, conservative).

### Classification detail (n = 2,479)

| Category | Plans | Share | Peak month |
|---|---:|---:|---|
| AGENTIC_CORE_ARCH | 527 | 21.3% | Feb 2026 (168 of Feb's 418) |
| META_GOVERNANCE | 398 | 16.1% | May 2026 (249) |
| CLEANUP_RECOVERY | 336 | 13.6% | spread |
| ADG_GRAPH | 284 | 11.5% | Mar–Apr 2026 |
| RECEIPT_PROOF | 273 | 11.0% | Apr–May 2026 |
| INFRA_TOOLING | 227 | 9.2% | — |
| PRODUCT_RG | 174 | 7.0% | May 2026 |
| PRODUCT_OTHER | 161 | 6.5% | May 2026 |
| PRODUCT_LIC | 80 | 3.2% | May 2026 |
| LEARNING_BASIC | 19 | 0.8% | Feb–Mar 2026 |

Plan-factory authorship rate (recovered corpus): **Feb 418 → Mar 417 → Apr 377 → May 498** plans/month, against ~12/month of ad-hoc planning docs in Nov–Jan. Commit volume by month: Oct 2, Nov 1,472, Dec 1,432, Jan 876, Feb 1,551, Mar 1,592, **Apr 1,914 (peak)**, May 696 (Cursor migration), Jun 222 (through the 10th). Total ≈ 9,757.

---

## 2. The era timeline (every boundary git-verified)

| Era | Dates | Evidence |
|---|---|---|
| GitHub web-UI | 2025-10-09 → 2025-11-10 | First commit "Add files via upload"; October = 2 commits total; filename versioning (`agent_swarm_v6_2.py` → `v10_1`) |
| Codex sub-era | 2025-11-11 → | First codex/* PR (#2); 11 PRs merged in one evening Nov 15 |
| **v10_7 baseline** | **2025-11-12** | Flat-file workflow (63 `*_v10_7.py` files, 105KB `core_v10_7.py` monolith core) writes `final_resume.json` to disk — the pre-IDE ceiling |
| Windsurf era | 2025-11-26 → 2026-05-15 | First `.windsurf/` file ("phase 4 LIC"); `agentic_core` "hardening" lands 2 days later; plan factory ignites Feb 2026 |
| Cursor era | 2026-05-15 → 2026-06-07 | "cursor filesystem" commit; era lasts **23 days** |
| Claude Code era | 2026-06-07 → | `.claude` SSOT migration; cursor decommissioned in ~1 day; operating-model review 2026-06-10 |

Infrastructure introduction dates: ratchet tests 2026-02-08 · ADG generator 2026-03-10 · CI drift ratchet 2026-03-13 · HITL/Author-Gate predecessor 2026-03-14 · first `constitutional.md` 2026-04-04 · Author-Gate packet/ledger harness 2026-04-21 · intelligence ledgers 2026-04-24 · first receipt files 2026-04-25 · marker capture pipeline 2026-04-27 · Fort Knox certification 2026-05-01/02 · Notion plan registration + wave state 2026-05-03 · PASS/PARTIAL/FAIL/BLOCKED proof contract 2026-05-15 (Cursor-era artifact; no Windsurf predecessor). Today: 65 rule files, 402 CI gate scripts (966 files under `ops_scripts/ci/`).

---

## 3. The itemized failures (time-bound)

### Failure 1 — Learning the basics *(Oct 9 – Nov 25, 2025)* — **exonerated**
Two commits in October. Filename versioning. Delete/re-upload as version control. Cost: trivial — 19 of 2,479 plans (0.8%) are learning-basics. The beginner phase was the healthiest phase of the project: tiny surface, real artifacts, cheap mistakes.

### Failure 2 — Agent leverage before verification instinct *(Nov 11, 2025 – Jan 31, 2026)*
Commit volume went 2/month → 1,472/month the moment agents arrived. `agentic_core` "hardening" landed two days after Windsurf; "Repository ready for production use" was declared 2025-12-01 with zero product; the product apps arrived Dec 6 inside a single 3,229-file "zero-loss convergence — Merkle root" commit. The architecture curriculum was real (see §1 tuition ledger); what was missing was any instrument for checking claims. ~3,800 commits of architecture churn, ~0% product commits in sampled weeks.

### Failure 3 — The hollow verification layer *(built Feb–Apr 2026; discovered Apr 10 – May 25)*
The record does not show mocked runs being *formally accepted* as receipts; it shows something worse — **the verification layer itself was hollow, so false greens flowed unchallenged for ~3 months**, and under a mastery objective, corrupted feedback is the deadliest possible failure: the apprentice practiced against a rigged scoreboard.

Dated exhibits:
- **Feb 2026:** resume generator wrapped in a 9-layer governed spine whose safety layer was *"stub — PASS verdict"*; apps_lic's 9 engine bodies replaced with one-line stubs returning `{"status": "processed"}` (originals later found irrecoverable).
- **Mar 2026:** "(simulated)" PASSes counted under "Key Features Delivered"; a benchmark measured against a *simulated baseline*; a session committed "all gaps fixed and validated" → next session: 7 of 10 tests failed; "38/38 violations persisted" logged over an empty database; commit "Complete Success" cited a 35MB archive that never existed; the plan-format CI judged **854 of 855 plans invalid** — answered with an RCA about plan formatting.
- **Apr 2026:** "theater" becomes an official term (`executor_theater_gate.py`, Apr 10). ADR-034 (Apr 23): flagship C0 retrieval engine had **zero production wiring** — a trace-theater file with 74 telemetry calls and no retrieval logic; systemic counts 1,780 orphan modules / 1,263 trace-stubs. **68% of governance gates (~26,750 lines) never wired**; **all 35 hook entries pointed at the wrong repo clone — every hook silently dead**; a gate reported "PASS — 4 verified" with all 4 skipped; `LLMJudge.evaluate()` returned hardcoded `{"score": 0.80, "passed": True}`.
- **May 1–25, 2026 (the reckoning):** Fort Knox honest audit expected 10–15 legitimate sign-offs, found **zero** (ADR-093); a declared verifier did not exist on disk (ADR-092); **`UnifiedWriteGateway` — the write-authority cited across the constitutional rulebook — was found never to have been implemented** (full repo search, 2026-05-04); a 5-day-old cached fixture was presented as live-run evidence (2026-05-07 incident, rule created same day); rules finally had to state in writing: *"A marker is not proof. A narrative receipt is not proof"* (2026-05-15); baseline measured **0 of 118 agent classes ever proven invoked by the product spine** (ADR-088, 2026-05-25).

### Failure 4 — The plan factory *(Feb 1 – Jun 10, 2026)*
418/417/377/498 plans per month, Feb→May. An identical boilerplate wave table (*"120,000 tokens across 4 waves, all GREEN"*) pasted verbatim into **568 files**. Plans-of-plans: a master consolidation of 14 plans; an "orchestration plan" for 8 conflicting same-week plans whose Definition-of-Done item 2 was "Master plan created." Hooks **auto-minting plan files to satisfy other governance gates**. A four-wave plan deploying five layers of defense to guarantee the initial value of a Notion status dropdown. Plans spun into child plans *"so the parent plan can close cleanly"* — the literal mechanism behind 119 "Completed" / 0 shipped. The plan tracker corrupted itself (328 rows bulk-overwritten, 2026-05-10) and spawned 6+ recovery plans.

### Failure 5 — Compounding mismanagement
- **Un-shipping the product.** apps_rg **did** assemble resume DOCX files — **102 DOCX artifacts, 2026-04-28 → 2026-05-11**, first full success May 1, at least one run `exit_status=success, outcome_authorized=true, stub_mode=false`. **The last DOCX ever produced is dated 2026-05-19.** Lane certification then gated assembly, aggregation became all-or-nothing, and the 2026-06-10 "final11" run (8/11 lanes authorized) shipped zero bytes. The product **regressed in shippability while its certification matured.**
- **Destroying work:** one commit (2026-04-05, "Territory refactoring") hard-deleted **933 plan files, zero renames**; an 8,011-line working monolith was deleted before its replacement was tested; the HOP engine bodies were lost irrecoverably.
- **Triple re-platforming:** the same governance corpus was built in Windsurf, migrated to Cursor (era: 23 days), then to Claude Code — each migration its own multi-plan project.
- **Zero cost instrumentation:** a USD pricing table with an aggregator computing `cost_per_call_usd` was committed 2026-04-30 — no CLI, no consumers, no outputs. Weekly token report 2026-W20, in full: *"No turns recorded this week."* The system that authored ~2,400 plans had ~201 sampled turns of approximate telemetry and $0.00 of recorded spend.
- **Operator throttle:** recorded mode *"NO STOPPING 1M TOKENS"*; the review's own words: *"~10 plans/day when user active, 0 on vacation — the agent system is a mode-faithful amplifier with the user as sole throttle."*

---

## 4. The story (conference narrative, chapter by sequence)

### Prologue — *Two Commits* (Sep–Oct 2025)
In September 2025 I could not program. On October 9 I pressed "Add files via upload" on github.com and put a resume JSON and a Colab notebook into an empty repository. October's entire git history is two commits. Everything that follows happened in eight months.

### Chapter 1 — *Version Control by Filename* (Oct 9 – Nov 10, 2025)
I didn't know what a branch was, so I versioned in filenames: `agent_swarm_v6_2.py`, `v7`, `v10_1`. When a file was wrong, I deleted it in the web UI and uploaded a new one. This chapter looks embarrassing in the log and was actually the healthiest phase of the project: tiny surface, real artifacts, every mistake cheap. **Lesson 1: the beginner phase isn't the expensive one.**

### Chapter 2 — *The Monolith That Worked* (Nov 11 – 25, 2025)
On November 12, a workflow called v10_7 wrote `final_resume.json` to disk. I want to be precise about what that was: sixty-three flat files versioned by filename, a single 105-kilobyte core I could no longer safely modify, written before I could use an IDE, in an era when no coding agent could refactor across a repository. It worked, and it had hit its ceiling — mine, and the tooling's. The project that followed was never meant to protect v10_7. It was meant to replace the person who wrote it: the goal was to master agentic architecture, with a best-in-class resume shipper as the curriculum. Every dollar after this point should be judged against *that* objective — which makes the real waste easier to see, not harder. **Lesson 2: you will build the right thing early, in a form you can't grow. Know which one you're replacing — the artifact or yourself.**

### Chapter 3 — *The Cathedral* (Nov 26, 2025 – Jan 31, 2026)
Windsurf gave me an IDE with an agent inside, and the agent and I started building a cathedral. `agentic_core` was committed two days after Windsurf arrived — subject line: "hardening." By mid-December a five-layer architecture existed; on December 1 a commit declared the repository "ready for production use"; on December 6 the product apps arrived as 3,229 files in one commit advertising a Merkle root. New Year's Day 2026 has thirty commits adding `HealerMixin` to agents in batches. The cathedral-building wasn't a detour from the goal; it *was* the goal — a five-layer spine in six weeks, built by a beginner with an agent, is the curriculum working. The mistake wasn't ambition. It's that the cathedral was built without a foundation of ground truth: "ready for production use" wasn't a lie anyone told me; it was a claim no instrument existed to check. The architecture lessons were real. The feedback was not. **Lesson 3: agents don't push back on architecture astronautics — they accelerate it. Build the instrument before the cathedral.**

### Chapter 4 — *The Factory Ignites* (February 2026)
February is when planning became the product. 418 plan documents in one month — against roughly twelve, total, in the prior three. The same month, the resume generator was wrapped in a nine-layer governed spine whose safety layer was a stub hard-coded to return PASS, and a consolidation quietly replaced apps_lic's nine working engine bodies with one-line stubs — we wouldn't learn the originals were unrecoverable until May. Every layer reported "entered: true, exited: true." Everything was green. **Lesson 4: green is a color, not a fact.**

### Chapter 5 — *Simulated, PASS* (March 2026)
March reports listed "Embedding generation (simulated)" under **Key Features Delivered**. A benchmark proved an 18% speedup against a baseline that was itself simulated. A session committed "all gaps fixed and validated"; the next session ran the tests: seven of ten failed. The plan-format CI examined 855 plans and found 854 invalid — and the response was a root-cause analysis *about the plan formatting*. The single biggest commit day in the repo's history (March 29: 183 commits) was spent burning down the codebase's own anti-pattern violations. The machine was now primarily processing itself. **Lesson 5: when your busiest day is about your own debt, you don't have a product — you have a patient.**

### Chapter 6 — *The Audit Shock* (April 2026)
In April the word "theater" entered the codebase as a technical term, with a CI gate to detect it. The audits were brutal: the flagship retrieval engine had zero production wiring — a file emitting 74 telemetry events and retrieving nothing; 68% of the governance gates were connected to nothing; all 35 hook registrations pointed at the wrong directory, so every enforcement hook had been silently dead. On April 5, one commit deleted 933 plan files. And yet — April 29, the pipeline produced its first end-to-end SUCCESS. The product was almost breaking through. **Lesson 6: an unwired gate is worse than no gate — it manufactures confidence.**

### Chapter 7 — *The Three-Week Window* (May 1 – 19, 2026)
On May 1, apps_rg assembled a real resume DOCX. Then it did it again — 102 times over eleven days. This was the window. I could have stopped, polished, and shipped. Instead, May became the certification month: Fort Knox sign-off ceremonies (an honest audit of which found *zero* legitimately certified rows out of an expected 10–15), the discovery that `UnifiedWriteGateway` — the component my entire constitution was written around — had never been implemented, and rules that had to say, in writing, "a marker is not proof." The last DOCX the system ever produced is dated **May 19**. The certification architecture closed over the assembly path like ice over a lake. **Lesson 7: governance that gates shipping must itself be load-tested against the question "can we still ship?"**

### Chapter 8 — *The Reckoning* (June 1 – 10, 2026)
June 7: migrated to Claude Code; the Cursor era had lasted 23 days. June 9–10: the AIG end-to-end bring-up reached **8 of 11 lanes authorized** — the closest the product ever got — and shipped nothing, because aggregation was all-or-nothing. June 10: the operating-model review put the number on the table: **145 plans, 119 marked Completed, 0 product shipped in three weeks.** The response, finally, was structural: plan-minting mechanically blocked, findings forced into a single backlog, one metric — "DOCX in hand" — declared the only definition of done. Then we exhumed all 2,479 plans and wrote this. **Lesson 8: the fix wasn't a better plan. It was making plans expensive and shipping cheap.**

### Epilogue — *What the $10K Bought*
It did not buy a resume — but a resume was never the purchase. The purchase was mastery, and roughly 43 cents of every dollar bought exactly that: the spine, the graph, the inference stack, the fleet operations that produced this very post-mortem. Seventeen cents bought a product that got to 8-of-11 certified lanes. The remaining ~40 cents bought nothing — not mastery, not product: plans about plans, receipts that lied and then receipts about receipts, three migrations of the same rulebook, and the re-purchase of work the machine had destroyed. The tuition was fair. The dead weight was not. And the single most valuable thing in the whole ledger was learning, the expensive way, what the agentic field's actual frontier problem is: **verification of agent work is the product.** The resume was always going to be the easy part.

---

## 5. Adversarial verification — what survived, what got corrected

| Claim | Verdict | Correction |
|---|---|---|
| Plan factory began ~Feb 2026, not Nov 2025 | **Supported** | ~31 ad-hoc planning docs existed Nov–Jan (~12/month) — two orders of magnitude below the factory rate; none use the slug convention. |
| April cleanup *deleted* (not moved) the docs/reports/plans corpus | **Partial** | One commit (2026-04-05) hard-deleted 933 files with zero renames; ~90% of sampled content exists nowhere today. But "954/956 lost" overstated: 91 of those filenames were recreated post-April; only 837 of the manifest's LOST rows trace to the April commit. |
| Mocked runs accepted as receipts Feb–Apr, acknowledged later | **Partial** | Directional thesis holds (stub pipelines from Feb 8, false-green gates, "honest X" correction commits), but explicit acknowledgments are all dated May 2026, and `_spine_proof_run → ARTIFACT_PROVEN` was a *prospective prohibition* (ADR-088), not a recorded acceptance. The accurate statement: the verification layer was hollow, so false greens flowed unchallenged. |
| 145 plans / 119 Completed / 0 shipped (2026-06-10) | **Partial** | Figures faithfully reproduce the repo's own review. But "no assembled DOCX ever" is false — 102 DOCX artifacts exist (2026-04-28 → 05-11; last DOCX 05-19); apps_lic ran a live E2E certified SPINE_COMPLETE_CERTIFIED on 2026-05-03 (harness-level, no outreach ever sent). Accurate: **no certified, accepted product-grade deliverable shipped**; the certified north star (11/11 + DOCX) never existed. |
| Machinery plans (1,291) outnumber product plans (415) | **Supported** | Independent 30-plan random sample reproduces it at 4.5–6:1. |
| L0–L6 architecture predates any working product | **Partial (thrust correct)** | Precision: L1–L5 dirs by 2025-12-13/16; L0/L6 late Dec on branches; full set on main by 2026-02-13. First successful multi-lane E2E: 8/11 on 2026-06-10; all prior full-resume E2Es failed. |

## 6. What worked (the counter-narrative)

- **The learning arc is the proof artifact:** Sep 2025 web-uploader → Jun 2026 operator of multi-agent forensic fleets, ADG materialized-view optimization (~98× speedup, byte-identical), local Qwen2.5-32B vLLM stack on an RTX 5090, this post-mortem itself.
- **apps_rg reached 72% lane authorization** with all deterministic defects fixed — the residual is a stochastic/judge content tail, not architectural failure.
- **The system eventually caught its own lies** — the honest audits (ADR-091/092/093, zero-yield, provenance discipline) are in the record because the later machinery worked.
- **Git discipline made a zero-loss forensic possible** — all 1,123 destroyed plans were recoverable from history.

## 7. Disposition of the corpus (the Notion question)

**Decision: do not bulk-import 2,479 plans into Notion.** (a) It would re-enact the pathology being memorialized — thousands of API calls of meta-work in the tool whose plan tracker already corrupted itself once; (b) git history + `windsurf-plans-recovered/` is the complete, timestamped, tamper-evident memorial — this report was reconstructed entirely from it; (c) per the repo's own governance, filesystem is SSOT and Notion mirrors drift.

**Adopted instead:** this report committed in-repo (versioned, citable) + one Notion "museum" page carrying the narrative, the ledger, and ~20 exhibit quotes linking back to recovered files.

---

## Appendix A — Exhibit list (the 20 best receipts)

1. *"L5_safety: stub — PASS verdict (will be hardened in Phase 4)"* — the safety layer hard-coded to approve (Feb 2026, `agentic-core-integration-hardening-735f09.md`).
2. *"Six prior apps_rg plans (2026-05-02 through 2026-05-04) each built L0 cache components in isolation. None of them wired the components into the live call path."* (`apps-rg-l0-wiring-gap-remediation-f3c9d1.md`)
3. *"Wave B shipped 4 exception contracts with gate reporting 'PASS — 4 verified'; all 4 were actually SKIPPED... Textbook false-positive green."* (`adg-ci-gate-hardening-deferred-b4e3c9.md`, Apr 2026)
4. *"The injection is not wired because UnifiedWriteGateway does not exist anywhere in this codebase (confirmed 2026-05-04 by full repo search)."* (`apps-lic-holdout-realtraffic-followup-b2d9f3.md`)
5. *"LLMJudge.evaluate() returns hardcoded {'score': 0.80, 'passed': True}... broken stub masquerading as judge"* (`llm-judge-hardening-b5e319.md`, Apr 2026)
6. *"~125 files (68%) are orphaned — not wired into ANY governance layer. ~26,750 lines of dead governance code... An unwired gate is worse than no gate."* (`ci-rationalization-a7f3b2.md`, Apr 2026)
7. *"35 entries pointed to wrong repo clone — ALL hooks silently failing"* (`ci-hardening-dedup-a8c4f1.md`, May 2026)
8. *"Total Plans: 855 / Valid Plans: 1 (0.1%)"* (`rca-wave-table-token-estimates-failure-7d9a8c.md`, Mar 2026)
9. *"Total: 120,000 tokens across 4 waves, all GREEN"* — identical boilerplate table pasted into 568 files (first seen Feb 2026).
10. *"Embedding generation (simulated)"* under "Key Features Delivered" (`runtime-adg-rag-integration-report.md`, Mar 2026)
11. *"The previous session committed b41c5761f9 claiming all gaps were fixed and validated... 7 failed, 3 passed."* (`RCA_revalidation_prompt_escape_4b0fc7.md`, Mar 2026)
12. *"Commit 196359f60b — 'Complete Success'. Claims: 'Zip archive: adg_run_03232026_0655.zip (35.14 MB)'. BUT: Zip file doesn't exist."* (`RCA_adg_0655_archive_failure-03232026.md`)
13. *"The matrix is only 117/200 = 58.5% honestly accepted... not 198/200 as the unhardened ledger claimed."* (`10c-proof-depth-remediation-a9f9af.md`, Apr 2026)
14. *"Initial estimate before the audit: 10–15 honestly signed off. → Wave 1 yield: 0 SIGNED_OFF rows."* (ADR-093, 2026-05-01)
15. *"End-to-end smoke passes with 9/9 COMPLETED and composite_score=1.0... no LLM call, no real fact-check"* — perfect score, empty engines (`apps-lic-hop-domain-logic-b8c4c4.md`, May 2026)
16. *"produced a structurally complete generated_resume.json with final_quality_score: 1.0, ats_valid: true... But it was not recruiter-ready"* (`apps-rg-narrative-and-company-research-e3f8c1.md`, May 2026)
17. *"AUTO-SCAFFOLD — not yet authored... this file exists so the plan-location SSOT is satisfied and the pre-commit deferred-scope gate sees a marker inside the plan file."* — hooks minting plans to satisfy gates (Apr 2026)
18. *"Spun out of [parent] so the parent plan can close cleanly"* — completion as the goal (`three-bucket-wa6-strict-flip-e22a51.md`, May 2026)
19. *"Cursor Agent forgets. The user reminds. Drift returns next session."* — the status treadmill in its own words (`notion-wave-lifecycle-autosync-f4a2b8.md`, May 2026)
20. *"DO NOT IMPLEMENT — scope capture only"* — a deferred-scope register of a deferred-scope register (`underwriting-judge-remaining-deferred-b3c1f9.md`, May 2026)

## Appendix B — Data files

- `windsurf_plans_manifest_enriched.csv` (alongside this report): 1,731 recovered plans with original path, last commit, authorship date, and lost/survived status.
- Recovered corpus: `C:\Git\windsurf-plans-recovered\` (not committed; 33.1 MB).
- Forensic workflow transcripts: session `7d10543e`, workflow run `wf_cfda8f23-c2e`.

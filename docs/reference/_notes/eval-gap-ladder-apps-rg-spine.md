# Eval Gap Ladder — apps_rg AIG Run, in Spine Terms

> Where the offline-eval gaps (GAP-1..9) sit on the four-level eval ladder
> (micro / lane / suite / meta), expressed against the apps_rg runtime spine
> with plain-language product annotations.
>
> **Source plan**: [eval-harness-spine-adg-closeout-6f2a9c](../../../plans/eval-harness-spine-adg-closeout-6f2a9c.md)
> (gap register + waves W1–W5). ADG evidence re-verified against the live
> `adg_sqlite` MCP on 2026-06-10 (snapshot `06082026_1212`): 7/8 evidence
> claims exact; 5 node-importance figures corrected in the plan; GAP-9
> half-resolved (MCP healthy, snapshot regeneration still required).
>
> **Companion concept**: the general dependency tower (pinned fixtures →
> controlled state → deterministic replay → suite → change control, with
> micro-evals and grader-trust as independent side towers). Deterministic
> replay is the *middle* rung — it requires state control below it and
> exists to serve the suite above it.

```text
        WHERE THE EVAL GAPS SIT — apps_rg AIG run, in spine terms (GAP-1..9)
 ═══════════════════════════════════════════════════════════════════════════════

   THE SPINE (one resume run — the thing we debugged all session):

   U0 ────▶ C0 ────────▶ PA ─────────▶ L2 ────────▶ X2 ──────────▶ X1D
   intake   evidence     prompt        propose      deterministic   judge panel
   = take   = pull the   = assemble    = Claude     gates = code    = Gemini +
   the AIG  candidate's  the writer's  drafts the   measures every  OpenAI grade
   VP job   true career  assignment    exec summary line: 320-char  the writing
   order;   facts (fact_ from locked   / bullets    bullet cap, 6   on 8 quality
   refuse   vectors      templates +   WITH cita-   sentences, all  dimensions,
   to start search +     the approved  tions (claim citations from  0–5 scale
   if keys/ approved     fact list     ledger) for  the approved
   models   fact list    (slots        every claim  list, no "I",
   missing  = the FEC)   S0…R0, 50KB)               no made-up %s
        ────▶ X3/Exit ─────────▶ UWG/L4 ─────▶ L6
              one verdict        commit        learn-after-run
              = a single ship/   = only an     = each run's full
              block stamp        Exit-stamped  evidence bundle
              (X3_ALLOW /        resume can    is archived for
              X3_BLOCK) signed   be saved or   future learning
              by the spine,      shipped       (shadow eval
              never by the lane                exhaust)
   [L1 plan-contract: the work order — fixed per section, no model, no judgment
    calls — omitted from the eval ladder by design]

 ┌─────────────────────────────────────────────────────────────────────────────┐
 │ LEVEL 1 · MICRO-EVAL — "test the X2 CHECKERS"                               │
 │ (covers: X2 gates · no models, frozen fixture, exact T/F)                   │
 │                                                                             │
 │  The question: when Claude (L2) writes a bullet like "achieved 99.99%       │
 │  uptime", does the X2 sentence-counter wrongly read the decimal point as    │
 │  a sentence break and fail a perfectly good bullet? (It did. We fixed it.)  │
 │                                                                             │
 │  GAP-4 ░ This session found 5 bugs in the X2 checkers themselves:           │
 │          • the "99.99%" decimal miscounted as two sentences                 │
 │          • the model's own "no IBM references: true" self_check note        │
 │            tripping the IBM-leakage scan (the attestation contained the     │
 │            forbidden string)                                                │
 │          • output cut off mid-JSON (token cap) → zero bullets survive       │
 │          • the judge step silently disabled → zero judge rows, every        │
 │            exec summary auto-blocked                                        │
 │          • a genuine two-sentence bullet that must STILL fail              │
 │          We wrote tests for each — but they're SCATTERED across test        │
 │          files. Nobody can run "the X2 micro-eval suite" as one named       │
 │          thing, so the next checker bug gets found the way we found         │
 │          these: by a failed AIG resume run, hours into debugging.           │
 │          → fix W3.1: one fixture family per gate, named suite, every commit │
 ├─────────────────────────────────────────────────────────────────────────────┤
 │ LEVEL 2 · LANE-EVAL — "replay ONE lane U0→X3 and trust the receipts"        │
 │ (covers: full spine, one section · 1 writer + graders · verdict = receipts) │
 │                                                                             │
 │  The question: can you re-run `--section ibm_bullets` for the SAME AIG      │
 │  job order (same pinned U0 inputs: JD + briefing) and get a comparable,     │
 │  auditable X3 ship/block stamp?                                             │
 │                                                                             │
 │  GAP-6 ░ The U0 entrypoint (apps_rg/__main__.py — the front door every      │
 │          resume run walks through) and the spine-emission adapter change    │
 │          saved state in 17 and 16 places with ZERO replay hooks (ADG-       │
 │          verified) — there is no machinery to re-run a lane against         │
 │          pinned inputs. Every "verify this fix worked" we did this          │
 │          session was a hand-built one-off command.                          │
 │  GAP-7 ░ The Exit evaluator itself (L5 exit_eval — the doorkeeper that      │
 │          signs the final X3 ship/block receipt on every resume) has NO      │
 │          coverage of its own in ADG — X2/X1D audit every resume, but        │
 │          nothing audits the auditor's signature step ("the doorkeeper's     │
 │          own door is unaudited").                                           │
 │          → fix W2.1/W2.2: replay scenario contract — pinned AIG fixtures    │
 │            in, full U0/C0/PA/L2/X2/X1D/X3/Exit receipt set out              │
 ├─────────────────────────────────────────────────────────────────────────────┤
 │ LEVEL 3 · SUITE-EVAL — "before changing the spine, re-run ALL orders"       │
 │ (covers: U0→L6 × N pinned scenarios × 11 lanes · verdict = pass-RATE       │
 │  vs baseline)                                                               │
 │                                                                             │
 │  The question: when someone edits a PA prompt template, an X2 limit         │
 │  (say the 320-char bullet cap), or a judge rubric, what proves the          │
 │  other 10 resume sections didn't quietly break?                             │
 │                                                                             │
 │  GAP-1 ░ The thing CALLED "the regression runner" never actually runs       │
 │          a resume through the spine — it re-grades SAVED answer sheets      │
 │          from old runs (verified in code: _load_trials + _classify).        │
 │          Like auditing a restaurant by re-reading last month's reviews.     │
 │          A suite eval that doesn't run the factory is a spreadsheet,        │
 │          not a suite.                                                       │
 │  GAP-2 ░ No before/after comparison. If section pass-rate slides from       │
 │          99% to 96% but the bar is 95%, the regression ships invisibly.     │
 │  GAP-5 ░ The library of test job-orders doesn't GROW: the L6 pipeline       │
 │          (run evidence → triage → human review → golden test set) is        │
 │          opt-in and unwired, so new failure classes — like everything       │
 │          this session uncovered — only became test cases because I          │
 │          hand-carried them.                                                 │
 │          → fix W2.3 (baseline diff + safety veto), W4 (L6 exhaust flywheel) │
 ├─────────────────────────────────────────────────────────────────────────────┤
 │ LEVEL 4 · META-EVAL — "test the X1D GRADERS (Gemini & OpenAI)"              │
 │ (covers: X1D judges scored against HUMAN labels)                            │
 │                                                                             │
 │  The question: when Gemini gave our AIG exec summary 4.5/5, why             │
 │  believe it?                                                                │
 │                                                                             │
 │  GAP-3 ░ The X1D graders are supposed to be periodically checked against    │
 │          resumes that HUMANS already graded. Problem 1: that human           │
 │          answer key (gold_set.jsonl) DOESN'T EXIST (verified absent).       │
 │          Problem 2: policy and CI don't even measure "agrees with the       │
 │          human" the same way — CI enforces Cohen's κ ≥ 0.6, policy          │
 │          demands raw agreement ≥ 0.7 (verified 2026-06-10; not just         │
 │          different numbers, different math). Until fixed, every             │
 │          Gemini/OpenAI verdict on every resume section — and every          │
 │          suite pass-rate built on those verdicts — rests on an              │
 │          unchecked grader.                                                  │
 │          → fix W3.2/W3.3: build the gold set, pick ONE statistic,           │
 │            snapshot-bind every X1D score to its calibration version         │
 ╞═════════════════════════════════════════════════════════════════════════════╡
 │ NOT ON THE LADDER — the machinery AROUND the four levels:                   │
 │                                                                             │
 │ ENFORCEMENT  GAP-8 ░ CI only forces the eval harness to run when judge/     │
 │ (what forces         eval files change — edits to agentic_core/runtime,     │
 │  suite evals         L5/L6 spine code, or the apps' spine adapters ship     │
 │  to run)             WITHOUT any suite eval. Every fix WE shipped this      │
 │                      session (the C0 fact-search filter, the L2 output      │
 │                      token caps, the X1D judge re-enable, canonical         │
 │                      bullet slot IDs) touched runtime files — NONE would    │
 │                      have triggered the harness. An unenforced suite is     │
 │                      documentation.                                         │
 │                      → fix W5.1/W5.2: widen triggers; UWG promotion must    │
 │                        cite a regression receipt                            │
 │                                                                             │
 │ INSTRUMENT   GAP-9 ░ ADG — the codebase X-ray that FOUND these gaps —       │
 │ (what measures       ½ RESOLVED. The plan's author (Codex) couldn't         │
 │  coverage)           reach it (dead MCP transport); re-checked live         │
 │                      2026-06-10: adg_health HEALTHY, same snapshot, and     │
 │                      7/8 of the plan's evidence claims verify EXACTLY       │
 │                      (5 file-importance figures were wrong → corrected      │
 │                      in the plan; the "determinism drift" flags are         │
 │                      background noise — 5,344 files carry them).            │
 │                      Residual: the X-ray was taken 06-08 from dirty         │
 │                      main and PREDATES this session's ~10 spine fixes.      │
 │                      → fix W1: REGENERATE the snapshot (not restore the     │
 │                        tool)                                                │
 └─────────────────────────────────────────────────────────────────────────────┘

  WHY THE ORDER MATTERS (bottom-up):
  • META rot (GAP-3): unchecked X1D graders poison every lane & suite verdict
    built on their scores
  • LANE gaps (6,7): can't replay one section U0→X3 → can't build a suite
    at all
  • SUITE gaps (1,2,5): prompt/threshold/rubric changes ship on vibes, and
    the test-order library never grows
  • MICRO gap (4): the cheap win — this session already collected the bug
    specimens; they just need a name and a CI hook

  HEADLINE (ADG, verified live 2026-06-10): offline-eval coverage of action
  nodes = 0.0% on EVERY spine layer (L0…L6, apps, tools). The per-run gates
  (X2/X1D/X3/Exit) are real — they caught everything we threw at them this
  session. What doesn't exist yet is the ladder that keeps them honest as
  the spine changes.
```

---

## Quick glossary (the four eval levels)

| Level | Tests what | Models used | Verdict | Cost |
|---|---|---|---|---|
| **Micro-eval** | one X2 checker function vs a frozen bug specimen | none (pure code) | exact T/F | ~ms, every commit |
| **Lane-eval** | one section replayed U0→X3 | writer (Claude) + graders (Gemini/OpenAI) | lane receipts (X3) | ~min, per fix |
| **Suite-eval** | whole spine × N pinned scenarios × 11 lanes | everything, ×N | pass-rate vs baseline | ~hrs, pre-merge |
| **Meta-eval** | the X1D graders themselves vs human labels | graders only (drafts replayed) | agreement w/ humans | periodic |

**Hard line** (plan Out-of-Scope): the offline ladder may block *promotions*
(which prompt/rubric/policy ships); it may never overrule a live run's
X2/X1D/X3/Exit verdict. `UNKNOWN ≠ PASS`; mock ≠ ALLOW.

*Captured 2026-06-10 from the AIG E2E debugging session (plans
`apps-rg-aig-remaining-lanes-closeout-d4e1f7`,
`apps-rg-c02-bootstrap-gate-correctness-c02f1a`).*

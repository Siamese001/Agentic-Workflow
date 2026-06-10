# Evals — Four Things, One Ladder (apps_rg spine)

> Captured 2026-06-10 from the AIG exec-summary closeout session
> (plan `apps-rg-aig-remaining-lanes-closeout-d4e1f7`). The word "eval" gets used for
> everything from a pytest assert to a multi-model replay rig. This note pins the four
> distinct meanings and maps each onto the apps_rg spine.

## The three kinds of models in the pipeline

| Role | Model | Spine stage |
|---|---|---|
| **Writer** (generator) | external Claude `claude-sonnet-4-6` | L2 |
| **Graders** (judge panel) | Gemini Pro + OpenAI (`gemini_pro`, `openai_chatgpt`) | X1D |
| **Embedder** | BGE-M3 (local, version-pinned — treated as deterministic plumbing, never the thing under evaluation) | C0 dense lane |

## The ladder

```
        WHAT PEOPLE CALL "EVALS" — four things, one ladder
 ═══════════════════════════════════════════════════════════════════════════════════════
  LEVEL        TESTS WHAT           WHICH MODEL(S) RUN?       SPINE COVERED      VERDICT / COST
 ───────────────────────────────────────────────────────────────────────────────────────
  MICRO-EVAL   one checker          NONE — pure code          a single gate:     exact T/F
  (unit test   function against     (no writer, no graders,     [X2] only         ~ms, free,
   w/ frozen   a frozen input        no embedder)              (+ U0 helpers      every commit
   bug)        "is 99.99% one                                   like env_
               thought?"                                        bootstrap)
 ───────────────────────────────────────────────────────────────────────────────────────
  LANE EVAL    one section          WRITER: Claude ×1         U0▸L1▸C0▸PA▸L2     lane receipts
  (standalone  end-to-end           GRADERS: Gemini+OpenAI    ▸X2▸X1D▸X3         (X3_ALLOW?)
   --section   "does exec_summary   EMBEDDER: BGE-M3 (C0)     — full spine,      ~min, $,
   run)        reach X3_ALLOW?"                               ONE lane           per fix
 ───────────────────────────────────────────────────────────────────────────────────────
  SUITE EVAL   whole pipeline,      WRITER: Claude ×N lanes   U0▸L1▸C0▸PA▸L2     pass-RATE
  (replay rig) N pinned scenarios   GRADERS: panel ×N         ▸X2▸X1D▸X3▸Exit    ≥0.98 gates
               "do all 11 lanes     EMBEDDER: BGE-M3          — full spine,      promotion
               still pass?"         (= everything, ×N runs)   ALL lanes, ×N      ~hrs, $$
 ───────────────────────────────────────────────────────────────────────────────────────
  META-EVAL    the graders          GRADERS ONLY (Gemini/     [X1D] only —       agreement
  (judge       themselves           OpenAI re-score frozen    judges scored      ≥0.7 w/
   calibration)"is Gemini's 4.5     outputs); writer NOT      against HUMAN      humans,
               trustworthy?"        needed — drafts replayed  labels             periodic, $$
 ═══════════════════════════════════════════════════════════════════════════════════════

  SPINE RULER — what each level touches:
                U0    L1    C0    PA    L2    X2    X1D   X3    Exit
  MICRO-EVAL    ·h···  ·     ·     ·     ·    ███    ·     ·     ·     (h = helper fns)
  LANE EVAL     ████  ████  ████  ████  ████  ████  ████  ████   ·
  SUITE EVAL    ████  ████  ████  ████  ████  ████  ████  ████  ████   (× N scenarios)
  META-EVAL      ·     ·     ·     ·    (replay)·    ███    ·     ·

  WHO'S UNCERTAIN AT EACH LEVEL:
  micro:  nobody          — code judges a string
  lane:   the WRITER      — will Claude's one draft pass the fixed checks?
  suite:  WRITER × N      — does it pass RELIABLY across scenarios?
  meta:   the GRADERS     — were Gemini/OpenAI right to pass it at all?
```

## Decoder ring

- **A micro-eval is a unit test.** It runs **zero models** — it tests the *code that judges*
  model output, using inputs frozen from real past failures. It earns the "eval" name only
  because of where the fixture comes from: a preserved specimen of a real bug, so the checker
  that misjudged it once can never misjudge it again. Session examples:
  - `99.99% uptime` must count as **one** thought (`check_bullet_single_thought` — the naive
    `.`-count miscounted decimals as sentence boundaries);
  - the model's `self_check` attestation key `"no_bul_ibm_references": true` must **not** trip
    the `bul_ibm_` leakage substring scan (proof-carrying fields only);
  - a blank worktree must resolve credentials via the `~/env/.env` home-SSOT fallback
    (`bootstrap_apps_rg_env` resolution chain).
- **Lane and suite evals run the writer + graders live.** Lane = one `--section` run scored by
  its own spine receipts (X2/X1D/X3). Suite = the replay rig over sha256-pinned scenarios
  (e.g. the AIG JD + briefing fixtures), gating prompt/rubric/policy promotion at ≥0.98
  pass-rate (`evaluation-promotion-gate`).
- **Meta-eval runs only the graders**, re-scoring frozen drafts against human labels
  (`judge-calibration-cadence`: agreement ≥0.7, stale judge → disqualified, no quorum →
  `escalate_hitl`). The writer isn't needed — the question isn't "can it write," it's
  "can the judges judge."

## Rules of thumb

1. **Each level up adds exactly one source of uncertainty** — micro: none · lane: the writer ·
   suite: the writer ×N · meta: the graders themselves.
2. **Eval rigor tracks decision variance.** Deterministic stages (U0/L1/L0-in-apps_rg) get
   fail-closed runtime gates + one-time micro-evals; model-backed stages get runtime gates
   *plus* scored eval loops. (In wider `agentic_core`, adaptive L0 routers get their own eval
   loop — `ROUTER_DECISION` ledgers + Wilson-bound promotion gates — appearing exactly when
   reasoning appears.)
3. **Eval never waives a runtime gate.** Offline results inform *promotion* (which
   prompt/rubric ships) and *trust* (which judge counts); the per-run verdict always belongs
   to the spine (X2 → X1D → X3 → Exit). `UNKNOWN` ≠ `PASS`; mock ≠ ALLOW.

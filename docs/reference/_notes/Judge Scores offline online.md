```text
EXECUTIVE SUMMARY JUDGE MODEL
runtime vs offline calibration
```

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│                              RUNTIME X1D PATH                                │
│                      happens during current resume run                       │
└──────────────────────────────────────────────────────────────────────────────┘

Qwen vLLM
  │
  │ generates
  ▼
Executive Summary Artifact
  │
  ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                              X1D JUDGE PANEL                                 │
├──────────────────────────────┬──────────────────────────────┬────────────────┤
│ ToneJudge                    │ TechnicalJudge               │ StyleJudge     │
│ fixed rubric                 │ fixed rubric                 │ fixed rubric   │
│ score 0-100                  │ score 0-100                  │ score 0-100    │
│ reason codes                 │ reason codes                 │ reason codes   │
│ evidence refs                │ evidence refs                │ evidence refs  │
└──────────────┬───────────────┴──────────────┬───────────────┴───────┬────────┘
               │                              │                       │
               ▼                              ▼                       ▼
        Tone score                      Technical score            Style score
        must pass                       must pass                  must pass
               │                              │                       │
               └──────────────┬───────────────┴──────────────┬────────┘
                              ▼                             
                    Weighted Average Score
                              │
                              ▼
                  ┌───────────────────────┐
                  │ X1D PASS / FAIL / WARN │
                  └───────────┬───────────┘
                              │
                              ▼
                         X2 Aggregates
                              │
                              ▼
                         X3 Disposes
              ALLOW / HITL / REROUTE / DENY / ABSTAIN
```

```text
PASS CONDITION INSIDE RUNTIME X1D

ToneJudge score        >= threshold
TechnicalJudge score   >= threshold
StyleJudge score       >= threshold
Weighted average       >= threshold

If all pass:
  X1D can pass quality

If one fails:
  X1D fails or warns, depending policy
```

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│                         OFFLINE BENCHMARK / CALIBRATION                      │
│                    does NOT happen during current runtime                    │
└──────────────────────────────────────────────────────────────────────────────┘

Human-scored benchmark set
N executive summaries
  │
  │ humans score each sample
  ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                         HUMAN REFERENCE SCORES                               │
├──────────────────────────────┬──────────────────────────────┬────────────────┤
│ Human tone score             │ Human technical score        │ Human style    │
│ Human quality notes          │ Human quality notes          │ Human notes    │
└──────────────┬───────────────┴──────────────┬───────────────┴───────┬────────┘
               │                              │                       │
               ▼                              ▼                       ▼

Same N samples sent to judges offline
  │
  ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                         JUDGE SCORES ON SAME SAMPLES                         │
├──────────────────────────────┬──────────────────────────────┬────────────────┤
│ ToneJudge scores N samples   │ TechnicalJudge scores N      │ StyleJudge N   │
│ 0-100 each                   │ 0-100 each                   │ 0-100 each     │
└──────────────┬───────────────┴──────────────┬───────────────┴───────┬────────┘
               │                              │                       │
               ▼                              ▼                       ▼

Compare judge rankings vs human rankings
  │
  ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                           CALIBRATION CHECK                                  │
├──────────────────────────────────────────────────────────────────────────────┤
│ ToneJudge Spearman rho        >= 0.80 ?                                      │
│ TechnicalJudge Spearman rho   >= 0.80 ?                                      │
│ StyleJudge Spearman rho       >= 0.80 ?                                      │
│ Weighted panel Spearman rho   >= 0.80 ?                                      │
└──────────────────────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┴───────────────────┐
          ▼                                       ▼
   PASS CALIBRATION                         FAIL CALIBRATION
          │                                       │
          ▼                                       ▼
Promote judge/profile for                 Keep advisory only
future runtime X1D use                    revise rubric/judge/threshold
via L6 -> UWG -> L4                       no autonomous X1D authority
```

```text
CORE IDEA

Runtime:
  judges score the current executive_summary

Offline:
  humans score benchmark samples
  judges score the same samples
  compare judge scores to human scores
  promote only if judge-human alignment is strong

Risk without benchmark:
  judge can be structured, confident, and rubric-based,
  but still misaligned with what humans consider good.
```

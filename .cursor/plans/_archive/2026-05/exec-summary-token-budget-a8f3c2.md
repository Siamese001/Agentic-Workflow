# Executive Summary Token Budget — apps_rg (exec-summary-token-budget-a8f3c2)

**Status:** Completed  
**Scope:** `apps_rg` executive_summary lane only — pre-dispatch prompt budgeting for 16k VLLM context + Brown & Brown SRFS live proof.  
**Out of scope:** `agentic_core`, judge thresholds, provider substitution, RELEASE_ELIGIBLE / X3 ALLOW.

## Disk SSOT

- Manifest: [executive_summary_token_budget_waves_manifest.json](docs/reports/apps_rg/executive_summary_token_budget_waves_manifest.json)
- Closeout: [executive_summary_token_budget_waves_closeout_receipt.md](docs/reports/apps_rg/executive_summary_token_budget_waves_closeout_receipt.md)

## Waves

| Wave | Title | Proof class | Status |
|------|-------|-------------|--------|
| W1 | v2 optional-only policy + tests | CONTRACT_TEST_PROOF | ✅ DONE |
| W2 | Brown LIVE_BLOCK (fail-closed) | LIVE_BLOCK_PROOF | ✅ DONE |
| W3 | Evidence capsule + Brown block | LIVE_BLOCK_PROOF (capsule) | ✅ DONE |
| W4 | Targeting cap + Brown runtime | LIVE_RUNTIME_PROOF | ✅ DONE |

## Invariants (preserved)

- Never trim HIGH facts, `ALLOWED_SOURCE_FACT_IDS`, I0 sovereign regions, R0 schema JSON, SRFS one-shot stub inside R0.
- On budget FAIL: block before Qwen; no shape-degraded dispatch.
- JD/briefing cap is targeting-only when `evidence_capsule_active=true`.

## Explicit non-claims

- Not RELEASE_ELIGIBLE (`proof_eligible: false` on latest run; X3 BLOCK on X1D judges).
- Supersedes invalid v1 trim proof `exec_summary_20260520_134924`.
---

## ADG_GRAPH_LAYER_EVIDENCE

Preflight scope (Constitutional §22) — MV-driven blast radius before edits:

| MV | Use |
|----|-----|
| `mv_fanin_top` | inbound dependency rank for scoped seam |
| `mv_fanout_top` | outbound consumer rank |
| `mv_blast_radius` | change-impact envelope |
| `mv_chokepoint_score` | sequencing / coupling risk |

Semantic edges: `flows_to`, `reads_from`, `writes_to` · P-view: `v_p0_wave_plan`

---

## ADG_HOTSPOT_REPORT

| Rank | Node | Archetype | Surface | Rationale |
|------|------|-----------|---------|-----------|
| 1 | scoped seam | CENTRAL_DEPENDENCY | Execution Surface | primary edit locus |
| 2 | gate / boundary | SAFETY_GATEKEEPER | Security Surface | fail-closed enforcement |

# e2e_gap_7e2d9c — Evidence Freeze (W0)

Plan: [apps-rg-e2e-gap-remediation-7e2d9c](../../../plans/apps-rg-e2e-gap-remediation-7e2d9c.md)

## What this is

A **frozen snapshot** of the failing end-to-end signature for two targets — **AIG**
(VP, Global Head of Agentic AI Solutions) and **Brown & Brown** (SVP IT Strategy &
Innovation) — captured on 2026-06-08 from a live `external_claude` / `claude-sonnet-5`
run in the `apps_rg_e2e` worktree.

Both targets produced **no resume**: all 11 lanes blocked upstream of company-specific
generation, the external provider was **never called** (`provider_attempted: false`), and
the integrated CLI **masked** the failure with a top-level `X3A` disposition and a zero
exit code while the internal `exit_status` was `error`.

## Why it is copied here

The original bundles live under `artifacts/apps_rg/runtime_proofs/full_resume_016f007993d4`
(AIG) and `full_resume_da98b7f979f7` (Brown). That tree is **gitignored** — it disappears on
a clean checkout. W0 copies only the **decisive, small** top-level evidence (no multi-hundred-KB
`runtime_payload.json`) into this tracked fixture so the failure is reproducible and auditable
after the artifacts are gone.

## Contents

- `manifest.json` — the master record: target identities, run/request/trace ids, terminal
  dispositions, the three proof assertions, per-file sha256 provenance, and the W1-W4
  remediation crosswalk.
- `aig/`, `brown/` — seven frozen JSONs each (ingress, terminal_ret_packet,
  full_run_section_status, integrated_lane_evidence_status, x3_disposition_receipt, and the
  competencies lane's provider_response + integrated_lane_pre_run_failure).

## The frozen failure signature (must stay true of these files)

1. **provider_attempted == false** — the provider was never reached; the block is upstream
   (C0.2 dense lane). Evidence: `*/competencies_provider_response.json`.
2. **All 11 lanes blocked, zero authorized** — 7 lanes `X3_BLOCK`/`REQUIRED_PROOF_ABSENT`
   + 4 narrative lanes `PRE_RUN:upstream_not_finalized`. Evidence:
   `*/full_run_section_status.json` cross-checked against `*/integrated_lane_evidence_status.json`
   (`executed_lane_count == 0`, `not_run_lane_count == 11`).
3. **Exit-code / disposition mismatch** — internal `exit_status == error`
   (`terminal_ret_packet.json` has a non-empty `l2_fault`; E3+E5 FAIL) while the aggregate
   disposition is `X3A` (`x3_disposition_receipt.json`) and the integrated CLI exited `0`.

## Guard

`tests/unit/apps_rg/test_e2e_gap_7e2d9c_freeze.py` validates that the manifest and the frozen
artifacts agree on all three assertions. It is a **fixture-integrity / documentation** guard
(it reads static copies — it does **not** re-run the system). Later waves eliminate the live
failure; this fixture remains the record of what was broken and the anchor their tests cite.

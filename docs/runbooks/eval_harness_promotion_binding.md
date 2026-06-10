# Eval Harness Promotion Binding

The eval harness promotion gate is the CI/UWG preflight reference for offline
eval evidence. It does not replace live runtime gates.

## Required Receipts

A promotion evidence manifest must provide:

- `replay_receipt`: whole-spine replay receipt with `passed=true`, baseline `MATCH`, and runtime receipt hash.
- `x2_micro_eval_receipt`: X2 micro-eval suite with all required hard-line fixture families present.
- `x1d_trust_receipt`: X1D trust decision using `quadratic_weighted_kappa`, fresh calibration snapshot, provider-mode parity, and quorum.
- `l6_graduation_receipt`: L6 candidate graduation decision with review quorum and deterministic replay pass.
- `adg_transport_receipt`: direct ADG MCP receipt with PID, snapshot ID, SQLite path, and healthy Redis. Prefer `startup_nonce` from `adg_runtime_info`; if the current Codex tool surface does not expose `adg_runtime_info`, the receipt must include `direct_mcp_verified=true`, `runtime_info_available=false`, and a `runtime_info_unavailable_reason`.

If ADG evidence is `DEGRADED_FALLBACK_SQLITE` or the direct MCP transport is closed, promotion must remain blocked.

## CI Entry Point

```bash
python ops_scripts/ci/check_eval_harness_promotion_evidence.py --manifest artifacts/eval/promotion/evidence_manifest.json
```

## UWG Usage

UWG promotion packets should cite the promotion gate output alongside their
existing replay and calibration proof refs. A passing gate does not authorize a
durable write by itself; it only proves that the offline harness evidence bundle
is complete enough for live UWG admission to consider.

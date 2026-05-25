# Executive summary targeting parity — live proof receipt

**Run:** `exec_summary_20260524_233409`  
**Command:** Brown & Brown SVP IT Strategy & Innovation (same as RCA doc)

## Containment proof (PASS)

| Check | Result |
|-------|--------|
| [targeting_ingress_receipt.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260524_233409/targeting_ingress_receipt.json) | 15210 → 11788 chars at ingress (`pre_proof_pool_u0_aligned`) |
| [targeting_context_parity_receipt.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260524_233409/targeting_context_parity_receipt.json) | `parity_match: true` |
| Generation vs judge briefing chars | 2596 == 2596 |
| Material digests | `f609b2738bfc3353…` == `f609b2738bfc3353…` |
| X3 parity codes | **None** (`X3_BLOCK` for ledger X2 + Claude soft-fail, not context parity) |

## Contrast (pre-fix)

Run `exec_summary_20260524_140149`: judge briefing ≫ L2 compiled (`parity_match: false`).

## Product status (not containment scope)

- `PRODUCT_X3_STATUS: X3_BLOCK`
- `soft_failed_judges: anthropic_claude`
- Failed X2 ledger accounting gates (separate from targeting parity)

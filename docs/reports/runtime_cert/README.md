# Runtime evidence manifests (Track 2)

Fort Knox certification (Track 1) is documented in [ADR-103](../../architecture/adr/ADR-103-fortknox-runtime-dual-track.md).

## Template — runtime proof pack

Create `docs/reports/<area>/<slug>_receipt.md` with:

```markdown
# <Seam name> — runtime receipt

- **Command:** `<exact argv>`
- **Exit code:** 0
- **Tests:** `<pytest nodeids>`
- **Artifacts:** `artifacts/...` paths (hyperlinked)
- **Scope limits:** what this proof does *not* cover
- **STATUS:** PASS | PARTIAL | FAIL | BLOCKED
```

Optional JSON sidecar under `artifacts/` when automation consumes structured proof.

## Example

- [exec_summary_targeting_parity_live_proof_20260524_233409_receipt.md](../apps_rg/exec_summary_targeting_parity_live_proof_20260524_233409_receipt.md)

## Do not

- Mark PASS from Fort Knox green alone
- Hand-edit `artifacts/certification/final_requirement_signoff_report.json`

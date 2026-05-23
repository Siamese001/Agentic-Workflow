# ADR-079: ADG pipeline — three-bucket audit opt-in (hot-path redesign)

**Status**: Accepted (2026-05-23)  
**Supersedes**: In-pipeline mandatory three-bucket stages in `generate_full_adg.py`  
**Related**: ADR-074 (runtime as OTel view), `ADG_THREE_BUCKET_AUTHORITY_MODEL.md`

## Context

The 2026-04 three-bucket model (static / runtime / registry) correctly states that
AST proof, policy declarations, and execution traces answer different questions.
Windsurf-era plans stacked W1–W8 (registry lift, synthetic OTel, triplet health,
in-toto digest, ADG_CERTIFIED) into **every** full ADG regen.

Observed problems:

1. **Speed** — runtime view build, registry lift, gap classification (~547k edge
   triples), and signing ran on every regen even when P0/MV gates do not consume them.
2. **False signal** — triplet health stayed at 0% while `v_runtime_proof` had
   thousands of rows because `static_edge_id` linkage rarely matched static `edges`.
3. **Wrong coupling** — ADG generation success was conflated with audit certification.

## Decision

### Hot path (`generate_full_adg`)

**Always run:**

- Static scan → sqlite commit
- Phase-2 disposition, infra wiring, coverage ingest (fail-soft)
- Overlay / truth / R6 / supplementary scanners
- Edge authority backfill + `proof_view` / `risk_view` (single-axis + triplet columns on static edges)
- Phase A–F materialized views
- P0 two-pass runner and existing post-ADG ratchet gates

**Do not run by default:**

- `build_runtime_view` (OTel → `v_runtime_proof`)
- `registry_bucket_lift`
- `THREE_BUCKET_GAP_REPORT` / authority audit JSON
- in-toto three-bucket content signing

### Opt-in audit path

Enable with `ADG_THREE_BUCKET=1`, sub-flags (`ADG_RUNTIME_VIEW`, `ADG_REGISTRY_LIFT`,
`ADG_THREE_BUCKET_REPORTS`, `ADG_THREE_BUCKET_SIGN`), CLI `--three-bucket`, or:

```bash
python tools/adg/run_three_bucket_audit.py --enable-all
```

Contract CI gates (`check_three_bucket_gap_thresholds`, `check_adg_certified`) stay
in `run_contract_gates.py` but assume reports are refreshed by the audit script, not
every regen.

## Consequences

- **Faster default regen** — skips OTel store walk, registry resolver pass, and
  full-repo 7-class gap report unless opted in.
- **Clearer semantics** — `generate_full_adg` exit code reflects static graph + MV
  + P0 truth, not triplet soak metrics.
- **Authority model retained** — `edge_authority.py` and SQL backfill unchanged;
  consumers still use `proof_view` / `risk_view` on static edges.
- **Runtime proof** — query OTel at audit time or enable `ADG_RUNTIME_VIEW`; do not
  treat empty `v_runtime_proof` as regen failure.

## Alternatives considered

| Option | Rejected because |
|--------|------------------|
| Delete three-bucket code | Still needed for security audit (SHADOW_CHANNEL) on demand |
| Fix triplet join only | Does not reduce regen cost |
| Merge registry into static only | Loses declarative-vs-code drift signal for audit runs |

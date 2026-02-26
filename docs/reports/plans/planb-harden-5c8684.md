# Plan B Hardening — 8 Targeted Patches

Apply 8 minimal patches to `artifacts/windsurf/planB_refreshed.md` to reach governance-grade quality. Document-only changes; no source files yet.

## Patch List

1. **Dimensions** — Replace hardcoded `dim=768/384/512` with "read from `IndexBuildMetadata.dimension`; values shown are examples only."

2. **ReadOnlyFAISSStoreAdapter** — Add to §B2: a wrapper that exposes only `open()`/`search()`; test must prove write paths raise `AttributeError` or `RuntimeError` (attribute absence).

3. **query_hash canonicalization** — Specify in §B1: `query_hash = SHA-256(dim_as_4_byte_little_endian + float32_little_endian_bytes_per_component)`. No string formatting of floats.

4. **Empty artifact neutrality** — Add invariant in §B2 and §B5: empty artifact MUST NOT increase proposal weight; negative control test required (empty artifact → output byte-identical to base proposer).

5. **Smoke rule** — Replace vague "smoke one-liner" with explicit rule: `python -c "exec('''...''')"` permitted for multi-line semantic smoke; on-disk helper scripts forbidden; synthetic `print()` forbidden.

6. **Schema invariance** — Define in §B4: schema equality = `dataclasses.asdict(output).keys()` equality + embedding context attached to sidecar field excluded from canonical serialization and routing.

7. **Delta-only negative control** — Add to §B5 test list: test that fails if wrapper emits absolute threshold (not a delta); byte-identical ChangePackage test vs base proposer when artifact is empty.

8. **Tenant audit replay stance** — Declare in §B6: audit entries are **informational-only (L6-class)**; they are NOT part of enforcement replay; do NOT include in canonical store or deterministic hash chain.

## Scope
- **1 file modified**: `artifacts/windsurf/planB_refreshed.md`
- **No source files touched**
- Commit + push to `embeddings` branch

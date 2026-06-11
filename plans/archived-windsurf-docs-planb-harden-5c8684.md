---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\planb-harden-5c8684.md'
original_relative_path: 'planb-harden-5c8684.md'
source_sha256: c9296d0f1b034b874e9df74473afbc7f30453a85e78a7fc8d7851ce0792c8d30
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-26'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Plan B Hardening — 8 Targeted Patches

Apply 8 minimal patches to `artifacts/windsurf/planB_refreshed.md` to reach governance-grade quality. Document-only changes; no source files yet.

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


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

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---


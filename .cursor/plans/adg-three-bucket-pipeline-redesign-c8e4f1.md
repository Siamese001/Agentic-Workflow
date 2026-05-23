---
plan_id: adg-three-bucket-pipeline-redesign-c8e4f1
plan_type: governance
touches_agentic_core: false
touches_governance_ci: true
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# ADG three-bucket pipeline redesign — opt-in audit, fast default regen

Remove mandatory three-bucket stages from the `generate_full_adg` hot path so daily regen is a **static graph + MV factory**; keep authority model and contract gates for on-demand audit.

> **plan_id discipline:** `plan_id` matches filename stem `adg-three-bucket-pipeline-redesign-c8e4f1`.

**Decision record:** [ADR-079-adg-pipeline-three-bucket-opt-in.md](../docs/architecture/adr/ADR-079-adg-pipeline-three-bucket-opt-in.md)  
**Supersedes in spirit:** Windsurf plans `three-bucket-gap-remediation-069806`, `adg-three-bucket-unified-c4f8e2` (in-pipeline mandatory triplet soak).

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1  
PLAN_STATUS: IN_PROGRESS  
CURRENT_WAVE: W2  
LAST_COMPLETED_WAVE: W1  
LAST_UPDATED: 2026-05-23

PLAN_CREATED: slug=adg-three-bucket-pipeline-redesign-c8e4f1 path=.cursor/plans/adg-three-bucket-pipeline-redesign-c8e4f1.md status=Not Started

---

## Context (SCQA)

- **Situation** — Full ADG regen builds a static sqlite graph, 42 MVs, and P0 write-sovereignty gates. A 2026-04 three-bucket model (static / runtime / registry) was wired into every regen: OTel runtime view, registry lift, 547k-edge gap report, in-toto signing. Triplet health stayed at 0% while `v_runtime_proof` had rows because `static_edge_id` rarely linked to `edges`.
- **Complication** — ~12 min regen paid audit cost on every run; exit code conflated graph generation with certification; gap report was misleading inventory noise.
- **Question** — How do we keep the authority *ideas* without taxing every regen?
- **Answer** — ADR-079: hot path = static + MVs + P0; three-bucket = opt-in via `ADG_THREE_BUCKET=1`, `--three-bucket`, or `tools/adg/run_three_bucket_audit.py`.

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | W1.1–W1.5 | Opt-in module + strip hot path + ADR + CLI + tests | ~8k | None | ✅ DONE | Default regen logs `three_bucket=OFF`; audit script exists |
| W2 | W2.1–W2.2 | Runtime↔static join fix (when audit enabled) | ~6k | W1 done | 🔲 TODO | `static_edge_id` populated; triplet % > 0 on seeded OTel |
| W3 | W3.1–W3.2 | CI/docs: gap gate hints, archive plan cross-refs | ~4k | W1 done | 🔲 TODO | Contract gates document audit-first flow |
| W4 | W4.1 | Optional weekly audit job doc / GHA sketch | ~3k | W2 green | 🔲 TODO | Operator runbook in ADR or docs/cursor |

**Out of scope:** Deleting `edge_authority.py` or contract `check_adg_certified`; full `.windsurf/plans` three-bucket archive; NOT NULL schema graduation (WA6 calendar gate).

---

## Status Tables

### Wave Progress

| Wave | Focus | Status | Tests Added | Files Changed |
|------|-------|--------|-------------|---------------|
| W1 | Hot-path opt-in (ADR-079) | ✅ DONE | +2 | 7 |
| W2 | static_edge_id linkage | 🔲 TODO | — | — |
| W3 | CI/docs alignment | 🔲 TODO | — | — |
| W4 | Weekly audit runbook | 🔲 TODO | — | — |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W1.1 | `optional_three_bucket.py` orchestrator | ✅ DONE |
| W1.2 | `generate_full_adg.py` strip + `--three-bucket` | ✅ DONE |
| W1.3 | `run_three_bucket_audit.py` CLI | ✅ DONE |
| W1.4 | ADR-079 + authority model pointer | ✅ DONE |
| W1.5 | Unit tests (`test_optional_three_bucket`) | ✅ DONE |
| W2.1 | Fix `_resolve_static_edge_id` / name fallback | 🔲 TODO |
| W2.2 | Verify triplet on `ADG_THREE_BUCKET=1` audit | 🔲 TODO |
| W3.1 | Gap threshold gate error text | ✅ DONE |
| W3.2 | Mark archived windsurf plans superseded | 🔲 TODO |
| W4.1 | Weekly audit operator doc | 🔲 TODO |

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W1.1 | Optional orchestrator | `tools/generate/integration/optional_three_bucket.py` | Monolithic generate_full_adg | ~2k | ✅ DONE |
| W1.2 | Hot path trim | `tools/generate/generate_full_adg.py` | Regen latency | ~2k | ✅ DONE |
| W1.3 | Audit CLI | `tools/adg/run_three_bucket_audit.py` | No sidecar for CI | ~1k | ✅ DONE |
| W1.4 | ADR | `docs/architecture/adr/ADR-079-*.md` | Design drift | ~1k | ✅ DONE |
| W1.5 | Tests | `tests/unit/tools/generate/integration/test_optional_three_bucket.py` | Flag contract | ~1k | ✅ DONE |
| W2.1 | Join fix | `tools/otel/runtime_view_builder.py`, gap report | 0% triplet false signal | ~4k | 🔲 TODO |
| W2.2 | Proof run | audit script + latest snapshot | No proof without manual steps | ~2k | 🔲 TODO |
| W3.1 | CI hints | `check_three_bucket_gap_thresholds.py` | Stale error message | ~1k | ✅ DONE |
| W3.2 | Plan archive notes | `.cursor/plans/_archive/...` | Duplicate plans | ~2k | 🔲 TODO |
| W4.1 | Runbook | `docs/cursor/` or ADR appendix | Operator confusion | ~3k | 🔲 TODO |

---

## Gap Register

| ID | Gap | Severity | Wave | Status |
|----|-----|----------|------|--------|
| G1 | `static_edge_id` always NULL → triplet health 0% | P2 | W2 | OPEN |
| G2 | Contract gates expect gap JSON; not refreshed every regen | P3 | W3 | MITIGATED (audit script) |
| G3 | `ADG_CERTIFIED` strict still advisory | P4 | W4 | DEFERRED |

---

## Definition of Done

| # | Criterion | Verification | Status |
|---|-----------|--------------|--------|
| D1 | Default `generate_full_adg` skips runtime/registry/gap/sign | Log contains `three_bucket=OFF` | ✅ |
| D2 | `ADG_THREE_BUCKET=1` or `--three-bucket` runs audit stages | Log contains `three_bucket=AUDIT[...]` | ✅ |
| D3 | `python tools/adg/run_three_bucket_audit.py --enable-all` exits 0 on latest snapshot | Command output | 🔲 |
| D4 | ADR-079 on disk and linked from authority model | File exists | ✅ |
| D5 | Notion Plans row registered with slug | API query | ✅ |
| D6 | W2: triplet_attested > 0 after OTel seed + join fix | `THREE_BUCKET_GAP_REPORT.json` | 🔲 |

### Verification vs deferral

| Item | In DoD? | Notes |
|------|---------|-------|
| Full regen exit 0 | No | Separate ratchet/P0 workstream |
| ADG_CERTIFIED strict flip | No | WA6 / calendar gate |
| Delete windsurf three-bucket plans | No | Archive-only |

---

## Operator quick reference

```bash
# Fast default (static + MVs + P0)
python -m tools.generate.generate_full_adg

# Audit only (existing snapshot)
ADG_THREE_BUCKET=1 python tools/adg/run_three_bucket_audit.py

# Regen + audit
python -m tools.generate.generate_full_adg --three-bucket

# Then contract gap gate (if needed)
python ops_scripts/ci/check_three_bucket_gap_thresholds.py
```

---

## Wave 1 — Hot-path opt-in (COMPLETED)

WAVE_ID: W1  
WAVE_STATUS: DONE  
WAVE_COMPLETE: YES  
AUTHORIZATION_STATUS: NOT_REQUIRED

**Delivered (2026-05-23):**

- [optional_three_bucket.py](../../tools/generate/integration/optional_three_bucket.py)
- [generate_full_adg.py](../../tools/generate/generate_full_adg.py) — removed mandatory runtime/registry/gap/sign
- [run_three_bucket_audit.py](../../tools/adg/run_three_bucket_audit.py)
- [ADR-079](../../docs/architecture/adr/ADR-079-adg-pipeline-three-bucket-opt-in.md)

WAVE_COMPLETE: plan=adg-three-bucket-pipeline-redesign-c8e4f1 wave=1 note="+2 tests, 7 files, scope=ADR-079-opt-in-hot-path"

---

## Wave 2 — Runtime↔static linkage

WAVE_ID: W2  
WAVE_STATUS: TODO  
WAVE_COMPLETE: NO

**Phases:**

- **W2.1** — Improve `_resolve_static_edge_id` (path-based fallback when `adg_name` ≠ OTel labels)
- **W2.2** — Run `ADG_THREE_BUCKET=1` audit after `seed_synthetic_traces` or real OTel; assert `health_score_pct_triplet_attested > 0`

---

## Wave 3 — CI and documentation

WAVE_ID: W3  
WAVE_STATUS: IN_PROGRESS  
WAVE_COMPLETE: NO

- **W3.1** — Gap gate points to `run_three_bucket_audit.py` ✅
- **W3.2** — Add superseded-by pointer in archived windsurf three-bucket plans

---

## Wave 4 — Weekly audit discipline

WAVE_ID: W4  
WAVE_STATUS: TODO  
WAVE_COMPLETE: NO

Document recommended cadence: regen daily, `run_three_bucket_audit.py` weekly or pre-release, contract gates on demand.

---

## ADG_HOTSPOT_REPORT

Not applicable — governance/pipeline plan; no new production modules in `agentic_core`.

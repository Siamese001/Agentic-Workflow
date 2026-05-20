# Deprecation quarantine plan

**Status:** Planning-only — nothing deprecated, deleted, or labeled deprecated in code in this pass.

---

## Classification legend

| Label | Meaning |
|-------|---------|
| KEEP_CORE | Remains in agentic_core; generic spine |
| KEEP_APPS_RG | Product/proof path in apps_rg |
| UPDATE | Keep but change wiring/docs/tests |
| RETIRE | Remove after fan-in zero + receipt |
| SUPERSEDED_BY_APPS_RG_SECTION_RUNTIME | apps_rg early agent replaced by section lanes |
| QUARANTINE_UNTIL_REVIEW | Excluded from proof; may archive in W11 |
| NEEDS_DECISION | Author-Gate or ADG fan-in before action |

---

## Quarantine-first registry

| Path | Classification | Proof-eligible | ADG before delete |
|------|----------------|----------------|-------------------|
| [apps_rg_l2_binding.py](../../agentic_core/L2_execution/apps_rg_l2_binding.py) | RETIRE | n/a | fan-in → 0 |
| [_agentic_core_smoke.py](../../agentic_core/L2_execution/_agentic_core_smoke.py) | QUARANTINE | CI only | optional |
| [apps_rg/runtime/dry_run/](../../apps_rg/runtime/dry_run/) | QUARANTINE | **no** | manifest |
| [apps_rg/reasoning/Rg*.py](../../apps_rg/reasoning/) | SUPERSEDED | **no** (facade/tests remain) | fan-in audit |
| [orchestrate_full_resume.py](../../apps_rg/runtime/internal/lane_batch.py) | QUARANTINE | offline only | manifest |
| Legacy `runtime/dispatch/*_dispatch.py` | RETIRE (post-W8) | **no** if calls `exit_deprecated_runtime_cli` | per file |
| [subatomic_hop_util.py](../../apps_shared/utils/subatomic_hop_util.py) signal stubs | QUARANTINE / UPDATE | **no** for signal scores | W4 decision |

---

## Non-product proof markers (do not use for PASS)

- `APPS_RG_L2_PROVIDER_MODE=stub_only`, `APPS_RG_L2_FORCE_STUB=1`
- `APPS_RG_QWEN_OFFLINE_CONTRACT_STUB=1`
- `--mock-judges` without `--allow-test-mock-judges`
- `apps_rg/runtime/dry_run/executive_summary_demo.py`
- `APPS_RG_R4_GENERATION_MODE=legacy_full_resume` — rollback path, not default modular proof

---

## W11 archive/delete gates

1. Entry listed in quarantine manifest ≥ 30 days
2. `adg_edge_fanin` = 0 for RETIRE targets
3. Migration receipt: `artifacts/governance/migration_receipts/<ts>_l2_rationalization.json`
4. Author-Gate for any RETIRE affecting tests or CI
5. Move to `archives/l2_rationalization_<date>/` with file manifest
6. Hard delete only after one release with re-export shim if needed

**Rollback:** Restore paths from archive manifest; rerun compileall + scoped pytest.

---

## Explicit non-claims

- No Notion/deprecated labels written to source files yet.
- Quarantine duration (30d) is recommended policy, not enforced in CI today.

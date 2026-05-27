# W2 Receipt — exec-summary-regen-stuck-c0-split-a4f8e2

**Wave:** W2 — C0 `claim_text` / `proof_text` split + two-fact migration  
**Date:** 2026-05-27  
**Status:** PASS

## W2.1 — Schema v2 metadata

| Item | Result |
|------|--------|
| Policy module | [claim_proof_split_policy.py](../../apps_rg/fact_inventory/claim_proof_split_policy.py) |
| Schema version | `master_skills_arsenal_claim_proof_v2` |
| Arsenal metadata | [master_skills_arsenal_ledger.json](../../apps_rg/fact_inventory/master_skills_arsenal_ledger.json) |
| Design lock | [master_skills_arsenal_ledger_design.json](master_skills_arsenal_ledger_design.json) `claim_proof_split` block |
| Candidate ledger SSOT | [master_candidate_skills_fact_ledger_20260518T1100Z.json](../../artifacts/apps_rg/fact_inventory/master_candidate_skills_fact_ledger_20260518T1100Z.json) |

## W2.2 — Offending fact migration

| Fact | Display `claim_text` | `proof_text` |
|------|----------------------|--------------|
| `fact_engineering_platform_001` | Governed platform paraphrase (no mechanism inventory chain) | Original mechanism-inventory body |
| `fact_quant_hpc_003` | Quant rigor paraphrase (no employer/FSA stack) | Original Towers Perrin / ING / Aetna / FSA body |

Migration tool: [migrate_claim_proof_split_w2.py](../../tools/apps_rg/migrate_claim_proof_split_w2.py)

```text
OK: migrated candidate_ledger=0 srfs_active=2 facts=fact_engineering_platform_001,fact_quant_hpc_003
```

(SRFS `selected_facts_by_section.executive_summary` synced on second run.)

## W2.3 — Audit script

```text
python tools/apps_rg/audit_fact_ledger_claim_proof_split.py
→ audit_fact_ledger_claim_proof_split: 0 failures / 42 facts
```

## W2.4 — X2 contract tests

```text
pytest tests/unit/apps_rg/runtime/validators/test_executive_summary_x2_claim_proof_split.py -o addopts=
→ 5 passed
```

- `executive_summary_x2.py` has **no** `proof_text` references
- W2 facts + SRFS executive_summary rows pass `validate_claim_proof_row`
- `_row_sentence_match_strength` prefers display `claim` over long fact `claim_text`

## Marker emitted

```
WAVE_COMPLETE: plan=exec-summary-regen-stuck-c0-split-a4f8e2 wave=2 note="claim/proof split, 2 facts migrated, audit+contract tests PASS"
```

## Next wave

**W3** — Brown canonical CLI re-proof vs `exec_summary_20260526_230615` baseline.

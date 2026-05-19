# Executive summary graph-only generation live proof

**STATUS:** PASS  
**PREVIOUS_STATUS:** PARTIAL  
**Latest run:** [exec_summary_20260519_122505](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260519_122505)

## Generation and disposition

| Field | Value |
|-------|-------|
| `runtime_generation_status` | REAL_LLM |
| `provider_name` | Qwen/Qwen2.5-32B-Instruct-AWQ |
| `provider_resolution_source` | DEV_DEFAULT_QWEN_VLLM |
| `product_quality_status` | PASS |
| `x2_status` | PASS (all gates) |
| `x3_disposition` | X3_ALLOW |
| `proof_eligible` | true |

## X1D judges (MODEL_BACKED)

| Provider | Score | Threshold | Pass | Decisive failure |
|----------|------:|----------:|:----:|:----------------:|
| gemini_pro | 5.0 | 4.0 | yes | no |
| openai_chatgpt | 4.3 | 4.0 | yes | no |
| anthropic_claude | 4.2 | 4.0 | yes | no |

## Graph-only / C0.3

| Field | Value |
|-------|-------|
| `graph_only_authority_status` | PASS |
| `c03_graphrag_bound_status` | BOUND |
| `graph_expansion_refs_count` | 39 |
| `graph_lineage_refs_count` | 11 |
| `evidence_items_count` | 8 |
| `non_graph_evidence_items_count` | 0 |
| `mock_provider_flags` | [] |
| `smoke_dispatch_reference_count` | 0 |

## Quality remediation (before → after)

| Check | Before (110715) | After (122505) |
|-------|-----------------|----------------|
| Unsupported gross margin 20% | present | absent |
| Causal platform→40% merge | present | absent |
| Unproven reliability/auditability | present | absent |
| Credential inventory sentence | present | omitted |

Repair artifact: [graph_only_generation_quality_repair.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260519_122505/graph_only_generation_quality_repair.json)

## Blockers

None.

## Non-claims

- `NOT_RELEASE_SIGNOFF` — runtime proof, not release certification.
- CLI used `--allow-non-allow-exit-zero` (inspection override); X3 JSON is source of truth for authorization.
- `base_resume_reference_count=1` / `old_skills_ledger_reference_count=2` are deprecation/lineage markers, not claim authority.

# apps_common Duplication Classification Report

Wave 1 deliverable for plan `apps-cross-app-precursors-c94c71`. Byte-level pairwise diff of 4 duplicated-surface families.

**Verdict rules**  PASS = >=80% pairs byte-identical AND zero divergent pairs (<20% diff).  DIVERGE = any pair with >=20% diff.  NEAR = mostly similar but not byte-identical, no divergent pairs.

## Summary

| Family | Files | Identical pairs | Near pairs | Divergent pairs | Verdict |
|---|---:|---:|---:|---:|---|
| `repo_signal_service` | 6 | 0 | 0 | 15 | **DIVERGE** |
| `observability_adapter` | 7 | 0 | 14 | 7 | **DIVERGE** |
| `spine_adapter` | 5 | 0 | 5 | 5 | **DIVERGE** |
| `ingress_runner` | 7 | 0 | 10 | 11 | **DIVERGE** |

## Family: `repo_signal_service` (DIVERGE)

### Files

| Path | SHA256 (prefix) | LOC | Bytes |
|---|---|---:|---:|
| `apps_eval/services/repo_signal_service.py` | `35cf661b5068f03e` | 70 | 2843 |
| `apps_exec/services/repo_signal_service.py` | `57d2ac53d1997732` | 82 | 3467 |
| `apps_lic/services/repo_signal_service.py` | `738bde37c69d4545` | 79 | 3133 |
| `apps_research/services/repo_signal_service.py` | `e0e8257e65738af9` | 83 | 3630 |
| `apps_rfp/services/repo_signal_service.py` | `a164ede007c346ce` | 113 | 4948 |
| `apps_rg/utils/repo_signal_service.py` | `5691e3c23ff23297` | 118 | 5274 |

### Pairwise similarity

| File A | File B | Ratio | Class |
|---|---|---:|---|
| `apps_eval/services/repo_signal_service.py` | `apps_exec/services/repo_signal_service.py` | 0.718 | DIVERGENT |
| `apps_eval/services/repo_signal_service.py` | `apps_lic/services/repo_signal_service.py` | 0.436 | DIVERGENT |
| `apps_eval/services/repo_signal_service.py` | `apps_research/services/repo_signal_service.py` | 0.676 | DIVERGENT |
| `apps_eval/services/repo_signal_service.py` | `apps_rfp/services/repo_signal_service.py` | 0.573 | DIVERGENT |
| `apps_eval/services/repo_signal_service.py` | `apps_rg/utils/repo_signal_service.py` | 0.538 | DIVERGENT |
| `apps_exec/services/repo_signal_service.py` | `apps_lic/services/repo_signal_service.py` | 0.434 | DIVERGENT |
| `apps_exec/services/repo_signal_service.py` | `apps_research/services/repo_signal_service.py` | 0.744 | DIVERGENT |
| `apps_exec/services/repo_signal_service.py` | `apps_rfp/services/repo_signal_service.py` | 0.627 | DIVERGENT |
| `apps_exec/services/repo_signal_service.py` | `apps_rg/utils/repo_signal_service.py` | 0.571 | DIVERGENT |
| `apps_lic/services/repo_signal_service.py` | `apps_research/services/repo_signal_service.py` | 0.405 | DIVERGENT |
| `apps_lic/services/repo_signal_service.py` | `apps_rfp/services/repo_signal_service.py` | 0.357 | DIVERGENT |
| `apps_lic/services/repo_signal_service.py` | `apps_rg/utils/repo_signal_service.py` | 0.323 | DIVERGENT |
| `apps_research/services/repo_signal_service.py` | `apps_rfp/services/repo_signal_service.py` | 0.692 | DIVERGENT |
| `apps_research/services/repo_signal_service.py` | `apps_rg/utils/repo_signal_service.py` | 0.661 | DIVERGENT |
| `apps_rfp/services/repo_signal_service.py` | `apps_rg/utils/repo_signal_service.py` | 0.558 | DIVERGENT |

## Family: `observability_adapter` (DIVERGE)

### Files

| Path | SHA256 (prefix) | LOC | Bytes |
|---|---|---:|---:|
| `apps_eval/integrations/observability_adapter.py` | `520b2ea42a870f5e` | 92 | 3111 |
| `apps_exec/integrations/observability_adapter.py` | `82ab33ab2dac2971` | 99 | 3538 |
| `apps_lic/integrations/observability_adapter.py` | `d355629379ac2619` | 109 | 3948 |
| `apps_research/integrations/observability_adapter.py` | `b7bcb133e1c53e55` | 100 | 3578 |
| `apps_rfp/integrations/observability_adapter.py` | `a586dfd63e1d6ac8` | 99 | 3548 |
| `apps_rg/integrations/observability_adapter.py` | `11a44fc6b2922f79` | 94 | 3414 |
| `apps_underwriting_ai/integrations/observability_adapter.py` | `7c891735f8cd8730` | 86 | 2692 |

### Pairwise similarity

| File A | File B | Ratio | Class |
|---|---|---:|---|
| `apps_eval/integrations/observability_adapter.py` | `apps_exec/integrations/observability_adapter.py` | 0.879 | NEAR |
| `apps_eval/integrations/observability_adapter.py` | `apps_lic/integrations/observability_adapter.py` | 0.830 | NEAR |
| `apps_eval/integrations/observability_adapter.py` | `apps_research/integrations/observability_adapter.py` | 0.874 | NEAR |
| `apps_eval/integrations/observability_adapter.py` | `apps_rfp/integrations/observability_adapter.py` | 0.875 | NEAR |
| `apps_eval/integrations/observability_adapter.py` | `apps_rg/integrations/observability_adapter.py` | 0.844 | NEAR |
| `apps_eval/integrations/observability_adapter.py` | `apps_underwriting_ai/integrations/observability_adapter.py` | 0.316 | DIVERGENT |
| `apps_exec/integrations/observability_adapter.py` | `apps_lic/integrations/observability_adapter.py` | 0.802 | NEAR |
| `apps_exec/integrations/observability_adapter.py` | `apps_research/integrations/observability_adapter.py` | 0.935 | NEAR |
| `apps_exec/integrations/observability_adapter.py` | `apps_rfp/integrations/observability_adapter.py` | 0.936 | NEAR |
| `apps_exec/integrations/observability_adapter.py` | `apps_rg/integrations/observability_adapter.py` | 0.900 | NEAR |
| `apps_exec/integrations/observability_adapter.py` | `apps_underwriting_ai/integrations/observability_adapter.py` | 0.308 | DIVERGENT |
| `apps_lic/integrations/observability_adapter.py` | `apps_research/integrations/observability_adapter.py` | 0.804 | NEAR |
| `apps_lic/integrations/observability_adapter.py` | `apps_rfp/integrations/observability_adapter.py` | 0.800 | NEAR |
| `apps_lic/integrations/observability_adapter.py` | `apps_rg/integrations/observability_adapter.py` | 0.788 | DIVERGENT |
| `apps_lic/integrations/observability_adapter.py` | `apps_underwriting_ai/integrations/observability_adapter.py` | 0.329 | DIVERGENT |
| `apps_research/integrations/observability_adapter.py` | `apps_rfp/integrations/observability_adapter.py` | 0.937 | NEAR |
| `apps_research/integrations/observability_adapter.py` | `apps_rg/integrations/observability_adapter.py` | 0.893 | NEAR |
| `apps_research/integrations/observability_adapter.py` | `apps_underwriting_ai/integrations/observability_adapter.py` | 0.307 | DIVERGENT |
| `apps_rfp/integrations/observability_adapter.py` | `apps_rg/integrations/observability_adapter.py` | 0.878 | NEAR |
| `apps_rfp/integrations/observability_adapter.py` | `apps_underwriting_ai/integrations/observability_adapter.py` | 0.309 | DIVERGENT |
| `apps_rg/integrations/observability_adapter.py` | `apps_underwriting_ai/integrations/observability_adapter.py` | 0.317 | DIVERGENT |

## Family: `spine_adapter` (DIVERGE)

### Files

| Path | SHA256 (prefix) | LOC | Bytes |
|---|---|---:|---:|
| `apps_eval/spine/eval_spine_adapter.py` | `de7485062b85927d` | 57 | 1663 |
| `apps_exec/spine/exec_spine_adapter.py` | `7d475a25ee36ef96` | 52 | 1405 |
| `apps_research/spine/research_spine_adapter.py` | `6a769691cb3b8d97` | 52 | 1459 |
| `apps_rfp/spine/rfp_spine_adapter.py` | `b6b843fe3bbcea7f` | 52 | 1371 |
| `apps_rg/engines/rg_spine_adapter.py` | `03637b337eaed0fe` | 268 | 12777 |

### Pairwise similarity

| File A | File B | Ratio | Class |
|---|---|---:|---|
| `apps_eval/spine/eval_spine_adapter.py` | `apps_exec/spine/exec_spine_adapter.py` | 0.815 | NEAR |
| `apps_eval/spine/eval_spine_adapter.py` | `apps_research/spine/research_spine_adapter.py` | 0.793 | DIVERGENT |
| `apps_eval/spine/eval_spine_adapter.py` | `apps_rfp/spine/rfp_spine_adapter.py` | 0.809 | NEAR |
| `apps_eval/spine/eval_spine_adapter.py` | `apps_rg/engines/rg_spine_adapter.py` | 0.091 | DIVERGENT |
| `apps_exec/spine/exec_spine_adapter.py` | `apps_research/spine/research_spine_adapter.py` | 0.905 | NEAR |
| `apps_exec/spine/exec_spine_adapter.py` | `apps_rfp/spine/rfp_spine_adapter.py` | 0.897 | NEAR |
| `apps_exec/spine/exec_spine_adapter.py` | `apps_rg/engines/rg_spine_adapter.py` | 0.087 | DIVERGENT |
| `apps_research/spine/research_spine_adapter.py` | `apps_rfp/spine/rfp_spine_adapter.py` | 0.902 | NEAR |
| `apps_research/spine/research_spine_adapter.py` | `apps_rg/engines/rg_spine_adapter.py` | 0.087 | DIVERGENT |
| `apps_rfp/spine/rfp_spine_adapter.py` | `apps_rg/engines/rg_spine_adapter.py` | 0.086 | DIVERGENT |

## Family: `ingress_runner` (DIVERGE)

### Files

| Path | SHA256 (prefix) | LOC | Bytes |
|---|---|---:|---:|
| `apps_eval/integrations/eval_ingress_runner.py` | `b360aaa43fdd783a` | 50 | 1868 |
| `apps_exec/integrations/exec_ingress_runner.py` | `1acfad776ac5ff1e` | 42 | 1504 |
| `apps_lic/integrations/lic_ingress_runner.py` | `d8fac5939ad994a4` | 42 | 1538 |
| `apps_research/integrations/research_ingress_runner.py` | `d09b5319c439a80c` | 42 | 1528 |
| `apps_rfp/integrations/rfp_ingress_runner.py` | `ec2248d6027ce9a4` | 42 | 1509 |
| `apps_rg/integrations/rg_ingress_runner.py` | `7e9f639e5379a6dd` | 151 | 5951 |
| `apps_underwriting_ai/integrations/underwriting_ingress_runner.py` | `38143e0b90e6cc15` | 80 | 2778 |

### Pairwise similarity

| File A | File B | Ratio | Class |
|---|---|---:|---|
| `apps_eval/integrations/eval_ingress_runner.py` | `apps_exec/integrations/exec_ingress_runner.py` | 0.852 | NEAR |
| `apps_eval/integrations/eval_ingress_runner.py` | `apps_lic/integrations/lic_ingress_runner.py` | 0.846 | NEAR |
| `apps_eval/integrations/eval_ingress_runner.py` | `apps_research/integrations/research_ingress_runner.py` | 0.848 | NEAR |
| `apps_eval/integrations/eval_ingress_runner.py` | `apps_rfp/integrations/rfp_ingress_runner.py` | 0.850 | NEAR |
| `apps_eval/integrations/eval_ingress_runner.py` | `apps_rg/integrations/rg_ingress_runner.py` | 0.330 | DIVERGENT |
| `apps_eval/integrations/eval_ingress_runner.py` | `apps_underwriting_ai/integrations/underwriting_ingress_runner.py` | 0.224 | DIVERGENT |
| `apps_exec/integrations/exec_ingress_runner.py` | `apps_lic/integrations/lic_ingress_runner.py` | 0.966 | NEAR |
| `apps_exec/integrations/exec_ingress_runner.py` | `apps_research/integrations/research_ingress_runner.py` | 0.976 | NEAR |
| `apps_exec/integrations/exec_ingress_runner.py` | `apps_rfp/integrations/rfp_ingress_runner.py` | 0.968 | NEAR |
| `apps_exec/integrations/exec_ingress_runner.py` | `apps_rg/integrations/rg_ingress_runner.py` | 0.324 | DIVERGENT |
| `apps_exec/integrations/exec_ingress_runner.py` | `apps_underwriting_ai/integrations/underwriting_ingress_runner.py` | 0.178 | DIVERGENT |
| `apps_lic/integrations/lic_ingress_runner.py` | `apps_research/integrations/research_ingress_runner.py` | 0.956 | NEAR |
| `apps_lic/integrations/lic_ingress_runner.py` | `apps_rfp/integrations/rfp_ingress_runner.py` | 0.962 | NEAR |
| `apps_lic/integrations/lic_ingress_runner.py` | `apps_rg/integrations/rg_ingress_runner.py` | 0.322 | DIVERGENT |
| `apps_lic/integrations/lic_ingress_runner.py` | `apps_underwriting_ai/integrations/underwriting_ingress_runner.py` | 0.176 | DIVERGENT |
| `apps_research/integrations/research_ingress_runner.py` | `apps_rfp/integrations/rfp_ingress_runner.py` | 0.965 | NEAR |
| `apps_research/integrations/research_ingress_runner.py` | `apps_rg/integrations/rg_ingress_runner.py` | 0.323 | DIVERGENT |
| `apps_research/integrations/research_ingress_runner.py` | `apps_underwriting_ai/integrations/underwriting_ingress_runner.py` | 0.177 | DIVERGENT |
| `apps_rfp/integrations/rfp_ingress_runner.py` | `apps_rg/integrations/rg_ingress_runner.py` | 0.325 | DIVERGENT |
| `apps_rfp/integrations/rfp_ingress_runner.py` | `apps_underwriting_ai/integrations/underwriting_ingress_runner.py` | 0.177 | DIVERGENT |
| `apps_rg/integrations/rg_ingress_runner.py` | `apps_underwriting_ai/integrations/underwriting_ingress_runner.py` | 0.211 | DIVERGENT |

## Wave 5 gating decision

- **`repo_signal_service`** -> STAY per-app (verdict=DIVERGE)
- **`observability_adapter`** -> STAY per-app (verdict=DIVERGE)
- **`spine_adapter`** -> STAY per-app (verdict=DIVERGE)
- **`ingress_runner`** -> STAY per-app (verdict=DIVERGE)

_Generated by `tools/analysis/diff_duplicated_families.py`._

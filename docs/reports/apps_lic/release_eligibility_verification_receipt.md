# apps_lic post-convergence release eligibility verification

**Commit SSOT:** `c750b3f1c5` (plus R3R4 release-blocker fixes on branch)  
**Prior incorrect claim retracted:** `RELEASE_ELIGIBLE_PROOF` (mock R3R4 does not count)  
**Date:** 2026-05-20

## STATUS: PASS

## PRODUCT_CONVERGENCE_STATUS: PASS

P3–P5 unchanged. Product CLI remains `python -m apps_lic` → `run_canonical_apps_lic_spine` only. Shadow runners stay deleted/non-importable.

## R4_RELEASE_STATUS: PASS

Live R4 canonical CLI proof valid (local vLLM, non-UNKNOWN Exit).

**Run dir:** [release_eligibility_r4_20260520](artifacts/apps_lic/spine_convergence/runs/release_eligibility_r4_20260520/)

| Evidence | Value |
|----------|-------|
| `producer_component` | `apps_lic.runtime.dispatch.canonical_dispatch` |
| `route_family` | `R4_MANAGED_DRAFT` |
| `execution_form` | `managed_workflow` |
| `l2_execution_status` | `completed` |
| `x3_disposition` | `X3D` (not `UNKNOWN`) |
| `exit_status` | `success` |
| `outcome_authorized` | `true` |
| Provider | `POST http://localhost:8000/v1/chat/completions` HTTP 200 |

## R3R4_RELEASE_STATUS: PASS

Live R3R4 canonical CLI proof **without mocks** reached `BriefingReady`, non-empty Tavily-sourced evidence, and post-bridge `R4_MANAGED_DRAFT`.

**Authoritative run dir:** [release_eligibility_r3r4_live_20260520_final](artifacts/apps_lic/spine_convergence/runs/release_eligibility_r3r4_live_20260520_final/)

| Evidence | Value |
|----------|-------|
| `bridge_class` | `AppsResearchBridge` |
| `mock_env_active` | `false` |
| Pre-research `route_family` | `R3R4_MANAGED_RESEARCH_THEN_DRAFT` |
| Post-research `route_family` | `R4_MANAGED_DRAFT` |
| Bridge outcome | `BriefingReady` |
| `research_evidence_count` | `9` |
| `research_authorized` | `true` |
| `x3_disposition` | `X3D` (product gates satisfied on success path) |
| `research_note` | `BriefingReady` |

Prior failed attempts (retained for audit): [release_eligibility_r3r4_live_20260520](artifacts/apps_lic/spine_convergence/runs/release_eligibility_r3r4_live_20260520/) (`APPS_RESEARCH_BLOCKED`), [release_eligibility_r3r4_live_20260520b](artifacts/apps_lic/spine_convergence/runs/release_eligibility_r3r4_live_20260520b/) (`APPS_RESEARCH_EMPTY` before `EvidenceShaper` fix).

**Mock run explicitly excluded from release:** [release_eligibility_r3r4_mock_20260520](artifacts/apps_lic/spine_convergence/runs/release_eligibility_r3r4_mock_20260520/) — `MOCK_PROOF` only.

## OVERALL_RELEASE_ELIGIBLE_STATUS: RELEASE_ELIGIBLE

R4 live PASS **and** R3R4 live `BriefingReady` PASS (no mock env, real `AppsResearchBridge`, non-empty evidence, R4 re-route).

## SCOPE_MATCH: YES

Wave 1 — `EvidenceShaper` + `get_hybrid_search_engine` restored; `GovernedResearchRun` / bridge evidence translation; Tavily-backed company-brief lineage when C0 store empty.  
Wave 2 — R3R4 research failure short-circuits to terminal R5 (`outcome_authorized=false`, no HOP success path).  
Wave 3 — live canonical CLI proof re-run.

## SCOPE_DRIFT: NONE

- No GovernedLic/YAML L2 resurrection
- No apps_rg L2 registration
- No Exit/X3 policy weakening
- No `APPS_LIC_MOCK_RESEARCH` / `MockAppsResearchBridge` on proof path

## FILES_CHANGED:

- [evidence_shaper.py](agentic_core/L3_orchestration/reasoning/engines/evidence_shaper.py) — `EvidenceShaper` class + `shape()`
- [hybrid_search_engine.py](agentic_core/L3_orchestration/reasoning/engines/hybrid_search_engine.py) — `get_hybrid_search_engine`, `shape_search`
- [evidence_lineage.py](apps_research/integrations/evidence_lineage.py) — C0 / company-brief → bridge lineage
- [governed_research_run.py](apps_research/integrations/governed_research_run.py) — `evidence_items`, bundle capture
- [apps_research_bridge.py](apps_lic/integrations/apps_research_bridge.py) — translate `evidence_items` / `confidence_score`
- [managed_workflow_dispatcher.py](apps_lic/integrations/managed_workflow_dispatcher.py) — `evidence_lineage` on `BriefingReady`
- [canonical_dispatch.py](apps_lic/runtime/dispatch/canonical_dispatch.py) — R3R4 fail-closed + bridge response lineage
- [release_eligibility_verification_receipt.md](docs/reports/apps_lic/release_eligibility_verification_receipt.md)

## FILES_DELETED: NONE

## COMMANDS_RUN (exit codes):

| Command | Exit |
|---------|------|
| `python -c "EvidenceShaper + GovernedResearchRun evidence probe"` | 0 |
| `Remove-Item Env:APPS_LIC_MOCK_RESEARCH; python -m apps_lic --auto-research ... release_eligibility_r3r4_live_20260520c` | 0 |
| `Remove-Item Env:APPS_LIC_MOCK_RESEARCH; python -m apps_lic --auto-research ... release_eligibility_r3r4_live_20260520_final` | 0 |
| `python -m apps_lic --apps-e2e-live` | 2 |
| `pytest tests/apps_lic/test_spine_convergence_negative_proof.py -q` | 0 |

## APPS_RESEARCH_FIX_PROOF:

- `EvidenceShaper` import succeeds; `GovernedAppRunner._c0_retrieve` completes without `ImportError`
- Live logs: C0 search degrades gracefully when `process_docs` Chroma collection absent; `CompanyBriefEngine` Tavily fan-out returns docs (see run logs under `release_eligibility_r3r4_live_20260520_final`)
- `GovernedE2ERunRecord.evidence_items` populated (9 items on proof run)

## LIVE_R3R4_BRIDGE_PROOF:

**Command:**

```powershell
Remove-Item Env:APPS_LIC_MOCK_RESEARCH -ErrorAction SilentlyContinue
python -m apps_lic --recipient-class executive --channel email --outreach-mode cold --auto-research --artifact-dir artifacts/apps_lic/spine_convergence/runs/release_eligibility_r3r4_live_20260520_final
```

**MOCK_ELIMINATION_PROOF** ([mock_elimination_proof.json](artifacts/apps_lic/spine_convergence/runs/release_eligibility_r3r4_live_20260520_final/mock_elimination_proof.json)): `bridge_class=AppsResearchBridge`, `mock_env_active=false`

**Pre-research route** ([route_contract_pre_research.json](artifacts/apps_lic/spine_convergence/runs/release_eligibility_r3r4_live_20260520_final/route_contract_pre_research.json)): `R3R4_MANAGED_RESEARCH_THEN_DRAFT`, `execution_form=managed_workflow`

**Bridge request** ([research_bridge_request.json](artifacts/apps_lic/spine_convergence/runs/release_eligibility_r3r4_live_20260520_final/research_bridge_request.json)): `research_authorized=true`

**Bridge response** ([research_bridge_response.json](artifacts/apps_lic/spine_convergence/runs/release_eligibility_r3r4_live_20260520_final/research_bridge_response.json)): `outcome=BriefingReady`, `research_evidence_count=9`, `evidence_lineage` with Tavily `uri` / `source_id` refs

**Post-bridge route** ([route_contract.json](artifacts/apps_lic/spine_convergence/runs/release_eligibility_r3r4_live_20260520_final/route_contract.json)): `R4_MANAGED_DRAFT`

**L3/L2/Exit:** [l3_workflow_receipt.json](artifacts/apps_lic/spine_convergence/runs/release_eligibility_r3r4_live_20260520_final/l3_workflow_receipt.json), [l2_execution_receipt.json](artifacts/apps_lic/spine_convergence/runs/release_eligibility_r3r4_live_20260520_final/l2_execution_receipt.json), [exit_disposition_receipt.json](artifacts/apps_lic/spine_convergence/runs/release_eligibility_r3r4_live_20260520_final/exit_disposition_receipt.json), [spine_run_manifest.json](artifacts/apps_lic/spine_convergence/runs/release_eligibility_r3r4_live_20260520_final/spine_run_manifest.json)

## BRIEFING_READY_PROOF:

`dispatch_outcome.outcome=BriefingReady`, `research_evidence_count=9`, `confidence_score=0.75`, manifest freshness `fresh`, post-bridge `route_family=R4_MANAGED_DRAFT`, `research_note=BriefingReady`.

## FAIL_CLOSED_RESEARCH_FAILURE_PROOF:

`canonical_dispatch.run_canonical_apps_lic_spine` returns terminal R5 when R3R4 research does not produce `BriefingReady` (`research_failed` branch: `terminal_r5=true`, `x3_disposition=DENY`, `outcome_authorized=false`, `exit_stage_policy=r3r4_research_fail_closed_no_exit_receipt`). Prior run [release_eligibility_r3r4_live_20260520b](artifacts/apps_lic/spine_convergence/runs/release_eligibility_r3r4_live_20260520b/) incorrectly continued HOP before this fix; new failures will not receive release-clearing `X3D` on an empty briefing path.

## CANONICAL_CLI_PROOF:

| Path | Class |
|------|-------|
| R4 live | PRODUCT_CANONICAL |
| R3R4 live (`release_eligibility_r3r4_live_20260520_final`) | PRODUCT_CANONICAL |
| R3R4 mock | MOCK_PROOF — excluded |

## EXIT_DISPOSITION_PROOF:

Success-path run: [exit_disposition_receipt.json](artifacts/apps_lic/spine_convergence/runs/release_eligibility_r3r4_live_20260520_final/exit_disposition_receipt.json) — `x3_disposition=X3D`, `exit_status=success`, `outcome_authorized=true` **after** `BriefingReady` (not on empty-research path).

## NEGATIVE_CONTROLS:

| Control | Result |
|---------|--------|
| `APPS_LIC_MOCK_RESEARCH` absent on proof run | PASS |
| `MockAppsResearchBridge` not used | PASS |
| `--apps-e2e-live` | exit 2 |
| GovernedLic / YAML L2 / `run_workflow_lic` | not importable (pytest 21/21) |
| `apps_lic` ∉ L2 resolver | PASS |
| `agentic_core` `*_binding.py` shims | absent |

## MOCK_ELIMINATION_PROOF:

[mock_elimination_proof.json](artifacts/apps_lic/spine_convergence/runs/release_eligibility_r3r4_live_20260520_final/mock_elimination_proof.json) — `APPS_LIC_MOCK_RESEARCH=""`, `bridge_class=AppsResearchBridge`.

## PROOF_CLASSIFICATION:

| Surface | Class |
|---------|-------|
| R4 + R3R4 live CLI | PRODUCT_CANONICAL |
| R3R4 mock | MOCK_PROOF — excluded |
| Negative controls | CONTRACT_TEST_ONLY |

## EXPLICIT_NON_CLAIMS:

- No claim that Chroma `process_docs` collection is populated locally (C0 vector leg degrades; Tavily supplies live web evidence)
- No full-repo pytest green
- UWG `l4_brief_committed` may remain `COMMIT_FAILED` (missing `l5_certification_ref`) — does not block bridge `BriefingReady` on proof run

## NEXT_BLOCKER:

NONE for apps_lic release eligibility gate defined in this receipt. Optional follow-ups: populate Chroma `process_docs` for C0-native evidence (reduce Tavily-only dependency), restore hop adapter modules or keep company-brief fallback documented.

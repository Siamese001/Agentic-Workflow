# apps_rg Output Bisect

## Section: run_preflight

### Layperson RCA

The earlier passing run had the private signing configuration needed to prove where work was routed, and its first section attempts cleared their gates and judges without a retry.

This run stopped at its first recorded check because that configuration was missing when the process started; research, resume generation, and judges never ran.

Retries did not fail one after another: zero retries were scheduled because repeating the same process with the same missing configuration could not change the result.

### Divergence And Root Cause

- First observed divergence: `PREFLIGHT` - The first divergence is the process-ingestion boundary: the passing run could sign route evidence, while the current process lacked required signing configuration.
- First causally relevant divergence: `PREFLIGHT` - The first divergence is the process-ingestion boundary: the passing run could sign route evidence, while the current process lacked required signing configuration.
- Code cause status: `EXTERNAL_CONFIGURATION_CAUSE_ISOLATED`

### Underlying Root Cause

- `environment_ingestion_root_cause` / `ISOLATED`: Required route-signing configuration was absent at process ingestion, so the run could not create signed L0 route evidence.
  - Code surface: `apps_rg/runtime/e2e_preflight.py::run_fresh_e2e_preflight`

### Ingestion-To-Outcome Lineage

| Order | Stage | Prior | Current | Match | Classification | Why | Prior evidence | Current evidence |
|---:|---|---|---|---|---|---|---|---|
| 1 | `PREFLIGHT` | `SIGNING_CONFIGURATION_AV` | `FACT_VECTOR_BOOTSTRAP_PR` | `False` | `CAUSAL` | The first divergence is the process-ingestion boundary: the passing run could sign route evidence, while the current process lacked required signing configuration. | `C:\Git\Agentic-Workflow-FRESH\artifacts\apps_rg\runs\anthropic_partnership_fresh_s2e_20260630_094000\route_contract.json` | `C:\Git\Agentic-Workflow-FRESH\.runtime\owner_solo_final_output\brown_brown\fresh_e2e_retry2\e2e_20260804T234403Z_1903ea1d\e2e_preflight_receipt.json` |
| 2 | `RESEARCH` | `REACHED` | `NOT_REACHED` | `False` | `DOWNSTREAM_EFFECT` | RESEARCH could not run after the causal preflight block. | `C:\Git\Agentic-Workflow-FRESH\artifacts\apps_rg\runs\anthropic_partnership_fresh_s2e_20260630_094000` | `C:\Git\Agentic-Workflow-FRESH\.runtime\owner_solo_final_output\brown_brown\fresh_e2e_retry2\e2e_20260804T234403Z_1903ea1d\e2e_preflight_receipt.json` |
| 3 | `U0` | `REACHED` | `NOT_REACHED` | `False` | `DOWNSTREAM_EFFECT` | U0 could not run after the causal preflight block. | `C:\Git\Agentic-Workflow-FRESH\artifacts\apps_rg\runs\anthropic_partnership_fresh_s2e_20260630_094000` | `C:\Git\Agentic-Workflow-FRESH\.runtime\owner_solo_final_output\brown_brown\fresh_e2e_retry2\e2e_20260804T234403Z_1903ea1d\e2e_preflight_receipt.json` |
| 4 | `L1` | `REACHED` | `NOT_REACHED` | `False` | `DOWNSTREAM_EFFECT` | L1 could not run after the causal preflight block. | `C:\Git\Agentic-Workflow-FRESH\artifacts\apps_rg\runs\anthropic_partnership_fresh_s2e_20260630_094000` | `C:\Git\Agentic-Workflow-FRESH\.runtime\owner_solo_final_output\brown_brown\fresh_e2e_retry2\e2e_20260804T234403Z_1903ea1d\e2e_preflight_receipt.json` |
| 5 | `L0` | `REACHED` | `NOT_REACHED` | `False` | `DOWNSTREAM_EFFECT` | L0 could not run after the causal preflight block. | `C:\Git\Agentic-Workflow-FRESH\artifacts\apps_rg\runs\anthropic_partnership_fresh_s2e_20260630_094000` | `C:\Git\Agentic-Workflow-FRESH\.runtime\owner_solo_final_output\brown_brown\fresh_e2e_retry2\e2e_20260804T234403Z_1903ea1d\e2e_preflight_receipt.json` |
| 6 | `L2` | `REACHED` | `NOT_REACHED` | `False` | `DOWNSTREAM_EFFECT` | L2 could not run after the causal preflight block. | `C:\Git\Agentic-Workflow-FRESH\artifacts\apps_rg\runs\anthropic_partnership_fresh_s2e_20260630_094000` | `C:\Git\Agentic-Workflow-FRESH\.runtime\owner_solo_final_output\brown_brown\fresh_e2e_retry2\e2e_20260804T234403Z_1903ea1d\e2e_preflight_receipt.json` |
| 7 | `X1-X3` | `REACHED` | `NOT_REACHED` | `False` | `DOWNSTREAM_EFFECT` | X1-X3 could not run after the causal preflight block. | `C:\Git\Agentic-Workflow-FRESH\artifacts\apps_rg\runs\anthropic_partnership_fresh_s2e_20260630_094000` | `C:\Git\Agentic-Workflow-FRESH\.runtime\owner_solo_final_output\brown_brown\fresh_e2e_retry2\e2e_20260804T234403Z_1903ea1d\e2e_preflight_receipt.json` |
| 8 | `APPS_EVAL` | `REACHED` | `NOT_REACHED` | `False` | `DOWNSTREAM_EFFECT` | APPS_EVAL could not run after the causal preflight block. | `C:\Git\Agentic-Workflow-FRESH\artifacts\apps_rg\runs\anthropic_partnership_fresh_s2e_20260630_094000` | `C:\Git\Agentic-Workflow-FRESH\.runtime\owner_solo_final_output\brown_brown\fresh_e2e_retry2\e2e_20260804T234403Z_1903ea1d\e2e_preflight_receipt.json` |
| 9 | `L6_SHADOW` | `REACHED` | `NOT_REACHED` | `False` | `DOWNSTREAM_EFFECT` | L6_SHADOW could not run after the causal preflight block. | `C:\Git\Agentic-Workflow-FRESH\artifacts\apps_rg\runs\anthropic_partnership_fresh_s2e_20260630_094000` | `C:\Git\Agentic-Workflow-FRESH\.runtime\owner_solo_final_output\brown_brown\fresh_e2e_retry2\e2e_20260804T234403Z_1903ea1d\e2e_preflight_receipt.json` |

### Code Bindings

| Role | File | Symbol | Changed in comparison | First change commit / PR | Status |
|---|---|---|---|---|---|
| configuration ingestion and fail-fast evidence | `apps_rg/runtime/e2e_preflight.py` | `run_fresh_e2e_preflight` | `True` | `PREEXISTED_BASELINE` | `RUNTIME_GATE` |

### Prior Passing Run

| Seq | Phase | Attempt | Candidate | Trigger / defect | Action | Gate scope | Gate result | Judge | Disposition | Acceptance meaning | Evidence |
|---:|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `preflight` | `1` | `-` | Required signing configuration was available to the passing run. | validate route signing and pinned baseline | `PREFLIGHT` | `PASS` | `NOT_APPLICABLE` | `ADVANCED_TO_RESEARCH` | `RUN_CONTROL` | `C:\Git\Agentic-Workflow-FRESH\artifacts\apps_rg\runs\anthropic_partnership_fresh_s2e_20260630_094000\route_contract.json` |
| 2 | `retry_accounting` | `0` | `-` | The passing baseline recorded authorized section and judge outcomes without a retry cycle. | continue with first accepted attempts | `RETRY_ACCOUNTING` | `NOT_REQUIRED` | `NO_JUDGE_RETRY_REQUIRED` | `FIRST_ATTEMPTS_ACCEPTED` | `RUN_CONTROL` | `C:\Git\Agentic-Workflow-FRESH\artifacts\apps_rg\runs\anthropic_partnership_fresh_s2e_20260630_094000\APPS_RG_MANDATORY_RUN_OUTPUT.json` |
| 3 | `section:competencies` | `1` | `-` | Pinned passing run section execution. | generate, gate, and judge section | `SECTION:COMPETENCIES` | `PASS` | `Google Gemini 3.1 Pro Preview `gemini-3.1-pro-preview`: 5/5 vs 4 PASS; OpenAI ChatGPT `gpt-5.5`: 4.1/5 vs 4 PASS` | `X3_ALLOW` | `RUN_CONTROL` | `C:\Git\Agentic-Workflow-FRESH\artifacts\apps_rg\runs\anthropic_partnership_fresh_s2e_20260630_094000\APPS_RG_MANDATORY_RUN_OUTPUT.json` |
| 4 | `section:unify_bullets` | `1` | `-` | Pinned passing run section execution. | generate, gate, and judge section | `SECTION:UNIFY_BULLETS` | `PASS` | `Google Gemini 3.1 Pro Preview `gemini-3.1-pro-preview`: 5/5 vs 4 PASS` | `X3_ALLOW` | `RUN_CONTROL` | `C:\Git\Agentic-Workflow-FRESH\artifacts\apps_rg\runs\anthropic_partnership_fresh_s2e_20260630_094000\APPS_RG_MANDATORY_RUN_OUTPUT.json` |
| 5 | `section:ibm_bullets` | `1` | `-` | Pinned passing run section execution. | generate, gate, and judge section | `SECTION:IBM_BULLETS` | `PASS` | `Google Gemini 3.1 Pro Preview `gemini-3.1-pro-preview`: 5/5 vs 4 PASS` | `X3_ALLOW` | `RUN_CONTROL` | `C:\Git\Agentic-Workflow-FRESH\artifacts\apps_rg\runs\anthropic_partnership_fresh_s2e_20260630_094000\APPS_RG_MANDATORY_RUN_OUTPUT.json` |
| 6 | `section:insurtech_bullets` | `1` | `-` | Pinned passing run section execution. | generate, gate, and judge section | `SECTION:INSURTECH_BULLETS` | `PASS` | `Google Gemini 3.1 Pro Preview `gemini-3.1-pro-preview`: 5/5 vs 4 PASS` | `X3_ALLOW` | `RUN_CONTROL` | `C:\Git\Agentic-Workflow-FRESH\artifacts\apps_rg\runs\anthropic_partnership_fresh_s2e_20260630_094000\APPS_RG_MANDATORY_RUN_OUTPUT.json` |
| 7 | `section:ey_bullets` | `1` | `-` | Pinned passing run section execution. | generate, gate, and judge section | `SECTION:EY_BULLETS` | `PASS` | `Google Gemini 3.1 Pro Preview `gemini-3.1-pro-preview`: 5/5 vs 4 PASS` | `X3_ALLOW` | `RUN_CONTROL` | `C:\Git\Agentic-Workflow-FRESH\artifacts\apps_rg\runs\anthropic_partnership_fresh_s2e_20260630_094000\APPS_RG_MANDATORY_RUN_OUTPUT.json` |
| 8 | `section:unify_narrative` | `1` | `-` | Pinned passing run section execution. | generate, gate, and judge section | `SECTION:UNIFY_NARRATIVE` | `PASS` | `Google Gemini 3.1 Pro Preview `gemini-3.1-pro-preview`: 5/5 vs 4 PASS` | `X3_ALLOW` | `RUN_CONTROL` | `C:\Git\Agentic-Workflow-FRESH\artifacts\apps_rg\runs\anthropic_partnership_fresh_s2e_20260630_094000\APPS_RG_MANDATORY_RUN_OUTPUT.json` |
| 9 | `section:ibm_narrative` | `1` | `-` | Pinned passing run section execution. | generate, gate, and judge section | `SECTION:IBM_NARRATIVE` | `PASS` | `Google Gemini 3.1 Pro Preview `gemini-3.1-pro-preview`: 5/5 vs 4 PASS` | `X3_ALLOW` | `RUN_CONTROL` | `C:\Git\Agentic-Workflow-FRESH\artifacts\apps_rg\runs\anthropic_partnership_fresh_s2e_20260630_094000\APPS_RG_MANDATORY_RUN_OUTPUT.json` |
| 10 | `section:insurtech_narrative` | `1` | `-` | Pinned passing run section execution. | generate, gate, and judge section | `SECTION:INSURTECH_NARRATIVE` | `PASS` | `Google Gemini 3.1 Pro Preview `gemini-3.1-pro-preview`: 5/5 vs 4 PASS` | `X3_ALLOW` | `RUN_CONTROL` | `C:\Git\Agentic-Workflow-FRESH\artifacts\apps_rg\runs\anthropic_partnership_fresh_s2e_20260630_094000\APPS_RG_MANDATORY_RUN_OUTPUT.json` |
| 11 | `section:ey_narrative` | `1` | `-` | Pinned passing run section execution. | generate, gate, and judge section | `SECTION:EY_NARRATIVE` | `PASS` | `Google Gemini 3.1 Pro Preview `gemini-3.1-pro-preview`: 5/5 vs 4 PASS` | `X3_ALLOW` | `RUN_CONTROL` | `C:\Git\Agentic-Workflow-FRESH\artifacts\apps_rg\runs\anthropic_partnership_fresh_s2e_20260630_094000\APPS_RG_MANDATORY_RUN_OUTPUT.json` |
| 12 | `section:executive_summary` | `1` | `-` | Pinned passing run section execution. | generate, gate, and judge section | `SECTION:EXECUTIVE_SUMMARY` | `PASS` | `Google Gemini 3.1 Pro Preview `gemini-3.1-pro-preview`: 5/5 vs 4 PASS; OpenAI ChatGPT `gpt-5.5`: 4.5/5 vs 4 PASS` | `X3_ALLOW` | `RUN_CONTROL` | `C:\Git\Agentic-Workflow-FRESH\artifacts\apps_rg\runs\anthropic_partnership_fresh_s2e_20260630_094000\APPS_RG_MANDATORY_RUN_OUTPUT.json` |
| 13 | `section:headline` | `1` | `-` | Pinned passing run section execution. | generate, gate, and judge section | `SECTION:HEADLINE` | `PASS` | `Google Gemini 3.1 Pro Preview `gemini-3.1-pro-preview`: 4.5/5 vs 4 PASS; OpenAI ChatGPT `gpt-5.5`: 4.2/5 vs 4 PASS` | `X3_ALLOW` | `RUN_CONTROL` | `C:\Git\Agentic-Workflow-FRESH\artifacts\apps_rg\runs\anthropic_partnership_fresh_s2e_20260630_094000\APPS_RG_MANDATORY_RUN_OUTPUT.json` |
| 14 | `section:final_resume_aggregation` | `1` | `-` | Pinned passing run section execution. | generate, gate, and judge section | `SECTION:FINAL_RESUME_AGGREGATION` | `PASS` | `Google Gemini 3.1 Pro Preview `gemini-3.1-pro-preview`: 5/5 vs 4 PASS; OpenAI ChatGPT `gpt-5.5`: 4.5/5 vs 4 PASS` | `X3_ALLOW` | `RUN_CONTROL` | `C:\Git\Agentic-Workflow-FRESH\artifacts\apps_rg\runs\anthropic_partnership_fresh_s2e_20260630_094000\APPS_RG_MANDATORY_RUN_OUTPUT.json` |

### Current Failing Run

| Seq | Phase | Attempt | Candidate | Trigger / defect | Action | Gate scope | Gate result | Judge | Disposition | Acceptance meaning | Evidence |
|---:|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `preflight` | `1` | `-` | FACT_VECTOR_BOOTSTRAP_PREFLIGHT_FAILED | stop without retry because configuration is non-retriable | `PREFLIGHT` | `FAIL` | `JUDGES_NOT_REACHED` | `BLOCKED_BEFORE_RESEARCH` | `RUN_CONTROL` | `C:\Git\Agentic-Workflow-FRESH\.runtime\owner_solo_final_output\brown_brown\fresh_e2e_retry2\e2e_20260804T234403Z_1903ea1d\e2e_preflight_receipt.json` |
| 2 | `retry_decision` | `0` | `-` | The missing process configuration would be identical on every in-process retry. | require external configuration injection before a new run | `RETRY_DECISION` | `NOT_RUN` | `JUDGES_NOT_REACHED` | `NO_RETRY_SCHEDULED` | `RUN_CONTROL` | `C:\Git\Agentic-Workflow-FRESH\.runtime\owner_solo_final_output\brown_brown\fresh_e2e_retry2\e2e_20260804T234403Z_1903ea1d\e2e_preflight_receipt.json` |

### Full X2 Gate Matrix

| Gate | Prior | Current | Changed | Current reason |
|---|---|---|---|---|
| `APPS_RG_ROUTE_SIGNING_PREFLIGHT` | `PASS` | `FAIL` | `True` | FACT_VECTOR_BOOTSTRAP_PREFLIGHT_FAILED |

### Judge Matrix

| Judge | Prior | Current | Reason |
|---|---|---|---|
| `gemini_pro` | `5.0/4.0 PASS` | `JUDGES_NOT_REACHED` | Current run stopped at signing preflight before research, generation, or judge dispatch. |
| `openai_chatgpt` | `4.5/4.0 PASS` | `JUDGES_NOT_REACHED` | Current run stopped at signing preflight before research, generation, or judge dispatch. |

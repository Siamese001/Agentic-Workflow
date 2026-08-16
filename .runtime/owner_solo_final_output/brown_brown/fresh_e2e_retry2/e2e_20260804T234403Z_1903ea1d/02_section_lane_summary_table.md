# apps_rg Mandatory Run Output

Generated: `2026-08-04T23:44:07Z`
Run root: `@C:\Git\Agentic-Workflow-FRESH\.runtime\owner_solo_final_output\brown_brown\fresh_e2e_retry2\e2e_20260804T234403Z_1903ea1d`

## Outcome

| Field | Value |
|---|---|
| Exit status | `error` |
| Execution status | `failed` |
| Outcome authorized | `False` |
| X3 disposition | `PRE_RUN:PREFLIGHT` |
| Fault | `FACT_VECTOR_BOOTSTRAP_PREFLIGHT_FAILED` |
| Integrated proof gate | `-` `-` |
| Final resume output gate | `FAIL` |

## Mandatory Inline Output Gates

| Gate | Status | Observed |
|---|---|---|
| `mandatory_bcg_inline_output_present` | `PASS` | `01_BCG_executive_output.md` |
| `mandatory_section_lane_table_inline_present` | `PASS` | `2` |
| `mandatory_resume_text_inline_present` | `FAIL` | `{'artifact': {'relpath': 'FINAL_RESUME_OUTPUT.txt', 'exists': True, 'bytes': 2110, 'sha256': '989b0c7ae07795cd5d9c68ed50875f5f37c714b0d0c5c856eeb858fbfcdbe82b'}, 'current_run_authorized': False, 'blockers': ['outcome_authorized_false', 'final_resume_output_status=FAIL', 'failed_final_resume_gates=final_resume_no_gap_markers', 'pre_run_blocked=run_preflight']}` |
| `mandatory_final_resume_json_present` | `FAIL` | `{'artifact': {'relpath': 'modular_r4/final_resume_assembly/final_resume.json', 'exists': True, 'bytes': 7046, 'sha256': '7a10b6d1cf66516412f3b5f814fb48d7348974db59d992a81da5850734f1c92f'}, 'current_run_authorized': False, 'blockers': ['outcome_authorized_false', 'final_resume_output_status=FAIL', 'failed_final_resume_gates=final_resume_no_gap_markers', 'pre_run_blocked=run_preflight']}` |
| `mandatory_resume_docx_present` | `FAIL` | `{'artifact': {'relpath': 'outputs/resume.docx', 'exists': True, 'bytes': 37799, 'sha256': '4e7f0024ec47c4e36c00a24d638fa248653f4a779d73cd7c6024a163f81550fc'}, 'current_run_authorized': False, 'blockers': ['outcome_authorized_false', 'final_resume_output_status=FAIL', 'failed_final_resume_gates=final_resume_no_gap_markers', 'pre_run_blocked=run_preflight']}` |
| `mandatory_inline_required_json_shape_locked` | `PASS` | `{'schema_version': 'apps_rg.inline_required_output.v1', 'immutable_section_order': ['bcg', 'section_lane_summary_table', 'resume_docx_full_version_inline'], 'shape_errors': []}` |
| `mandatory_bcg_p0_p1_px_recommendations_locked` | `PASS` | `{'title': 'BCG Executive Output - apps_rg Run', 'section_order': ['executive_answer', 'p0_p1_px_recommendations', 'board_level_readout', 'issue_tree', 'recommended_next_move', 'evidence_map'], 'priorities': ['P0', 'P1'], 'truth_errors': []}` |
| `mandatory_research_briefing_input_row0_locked` | `PASS` | `{'order': 0, 'section': 'research_briefing_input', 'generation_status': 'MISSING_BRIEFING'}` |
| `mandatory_apps_research_row0_x1_x2_x3_gates_locked` | `FAIL` | `{'research_source_class': 'NOT_OBSERVED', 'x2': 'NOT_OBSERVED; blocker=no_apps_research_handoff_present', 'x3': 'FAIL'}` |
| `mandatory_resume_docx_inline_json_present` | `FAIL` | `{'title': 'Resume DOCX Full Version Inline', 'text_chars': 446, 'current_run_authorized': False, 'blockers': ['outcome_authorized_false', 'final_resume_output_status=FAIL', 'failed_final_resume_gates=final_resume_no_gap_markers', 'pre_run_blocked=run_preflight']}` |
| `E2E_FAIL_WITHOUT_SECTION_FORENSICS` | `PASS` | `{'required': False, 'failed_section_count': 0, 'artifact_dir': '', 'missing_or_incomplete': []}` |

## Section Counts

| Total | Real LLM | X3 allow | X3 block | Pre-run blocked | Not run | Unknown/other |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0 | 0 | 0 | 1 | 0 | 0 |

## Section Lane Summary Table

| # | Section | Research source class | R1A | R1B | Lane record | Provider call attempted | Primary provider | Primary model observed | Pooling selector LLM | Secondary provider | Secondary model observed | Generation status | Judges run | Judge models / scores | Judge retry / fallback | <span style="display:inline-block; min-width:32ch">X2</span> | <span style="display:inline-block; min-width:32ch">X3</span> | <span style="display:inline-block; min-width:44ch">Past fail / blocker</span> | Display output | L6 evidence |
|---:|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | `research_briefing_input` | `NOT_OBSERVED` | `NOT_OBSERVED` | `NOT_OBSERVED` | `NO` | `NOT_OBSERVED` | `NOT_OBSERVED` | `NOT_OBSERVED` | `N/A` | `N/A` | `N/A` | `MISSING_BRIEFING` | `N/A` | `N/A` | `N/A` | <span style="display:inline-block; min-width:32ch; white-space:normal"><code>NOT_OBSERVED;<br>blocker=no_apps_research_handoff_present</code></span> | <span style="display:inline-block; min-width:32ch; white-space:normal"><code>FAIL</code></span> | <span style="display:inline-block; min-width:44ch; white-space:normal"><code>auto_research_internal=None; research_delegation_executed=NOT_OBSERVED; source=NOT_OBSERVED; briefing missing</code></span> | `MISSING` | `N/A` |
| 1 | `run_preflight` | `N/A` | `NOT_OBSERVED` | `NOT_OBSERVED` | `YES` | `NOT_OBSERVED` | `NOT_OBSERVED` | `NOT_OBSERVED` | `N/A` | `NOT_OBSERVED` | `NOT_OBSERVED` | `NOT_RUN` | `NO` | `NOT_OBSERVED` | `NOT_OBSERVED` | <span style="display:inline-block; min-width:32ch; white-space:normal"><code>NOT_REACHED</code></span> | <span style="display:inline-block; min-width:32ch; white-space:normal"><code>PRE_RUN:PREFLIGHT</code></span> | <span style="display:inline-block; min-width:44ch; white-space:normal"><code>Route-signing configuration ingestion failure</code></span> | `MISSING` | `not_reached` |

## Section Execution Ledger

| Section | Ran status | X3 | X2 | Product | Runtime | Failed gates | Display |
|---|---|---|---|---|---|---|---|
| `run_preflight` | `pre_run_blocked` | `PRE_RUN:PREFLIGHT` | `NOT_REACHED` | `BLOCKED` | `NOT_RUN` | `APPS_RG_ROUTE_SIGNING_PREFLIGHT` | `-` |

## Final Resume Product Outputs

| Artifact | Path | Status | Bytes | SHA256 |
|---|---|---|---:|---|
| Canonical final resume JSON | `modular_r4/final_resume_assembly/final_resume.json` | `EXISTS_UNAUTHORIZED` | 7046 | `7a10b6d1cf66516412f3b5f814fb48d7348974db59d992a81da5850734f1c92f` |
| Rendered final resume text | `FINAL_RESUME_OUTPUT.txt` | `EXISTS_UNAUTHORIZED` | 2110 | `989b0c7ae07795cd5d9c68ed50875f5f37c714b0d0c5c856eeb858fbfcdbe82b` |
| Final resume DOCX | `outputs/resume.docx` | `EXISTS_UNAUTHORIZED` | 37799 | `4e7f0024ec47c4e36c00a24d638fa248653f4a779d73cd7c6024a163f81550fc` |

| Gate | Status | Observed |
|---|---|---|
| `final_resume_json_spine_present` | `PASS` | `.runtime/owner_solo_final_output/brown_brown/fresh_e2e_retry2/e2e_20260804T234403Z_1903ea1d/modular_r4/final_resume_assembly/final_resume.json` |
| `final_resume_rendered_text_present` | `PASS` | `{'relpath': 'FINAL_RESUME_OUTPUT.txt', 'exists': True, 'bytes': 2110, 'sha256': '989b0c7ae07795cd5d9c68ed50875f5f37c714b0d0c5c856eeb858fbfcdbe82b'}` |
| `final_resume_docx_present_nonempty` | `PASS` | `{'relpath': 'outputs/resume.docx', 'exists': True, 'bytes': 37799, 'sha256': '4e7f0024ec47c4e36c00a24d638fa248653f4a779d73cd7c6024a163f81550fc'}` |
| `final_resume_rendered_order_valid` | `PASS` | `{'EXECUTIVE SUMMARY': 182, 'ENGINEERING & PLATFORM COMPETENCIES': 273, 'PROFESSIONAL EXPERIENCE': 392, 'EDUCATION': 1575, 'CERTIFICATIONS': 1739}` |
| `final_resume_docx_order_valid` | `PASS` | `{'EXECUTIVE SUMMARY': 187, 'ENGINEERING & PLATFORM COMPETENCIES': 284, 'PROFESSIONAL EXPERIENCE': 409, 'EDUCATION': 1606, 'CERTIFICATIONS': 1769}` |
| `final_resume_base_role_headers_preserved` | `PASS` | `{'role_headers': {'unify': ['Unify Consulting — SVP Engineering, Agentic AI Platforms', 'Boca Raton, FL \| Feb 2023 – Present'], 'ibm': ['IBM — Partner', 'Edgewater, NJ \| Apr 2017 – Oct 2022'], 'insurtech': ['InsurTech Cloud Solutions — Chief Technology Officer', 'New York, NY \| Apr 2014 – Mar 2017'], 'ey': ['Ernst & Young — Principal', 'New York, NY \| Oct 2009 – Mar 2014'], 'early_career': ['Early Career Roles — Actuarial Consultant and Quantitative Roles', 'Philadelphia, PA \| Oct 2002 – Sep 2009']}, 'positions': {'unify': [417, 474], 'ibm': [604, 618], 'insurtech': [742, 795], 'ey': [922, 948], 'early_career': [1068, 1133]}}` |
| `final_resume_docx_base_role_headers_preserved` | `PASS` | `{'role_headers': {'unify': ['Unify Consulting — SVP Engineering, Agentic AI Platforms', 'Boca Raton, FL \| Feb 2023 – Present'], 'ibm': ['IBM — Partner', 'Edgewater, NJ \| Apr 2017 – Oct 2022'], 'insurtech': ['InsurTech Cloud Solutions — Chief Technology Officer', 'New York, NY \| Apr 2014 – Mar 2017'], 'ey': ['Ernst & Young — Principal', 'New York, NY \| Oct 2009 – Mar 2014'], 'early_career': ['Early Career Roles — Actuarial Consultant and Quantitative Roles', 'Philadelphia, PA \| Oct 2002 – Sep 2009']}, 'positions': {'unify': [433, 490], 'ibm': [620, 634], 'insurtech': [762, 815], 'ey': [948, 974], 'early_career': [1100, 1165]}}` |
| `final_resume_education_copied_from_base` | `PASS` | `{'section_id': 'education', 'expected_lines': ['Master of Science in Biostatistics, Columbia University (Graduated with Distinction)', 'Bachelor of Arts in Biology, Brown University (Graduated Cum Laude)'], 'positions': {'Master of Science in Biostatistics, Columbia University (Graduated with Distinction)': 1585, 'Bachelor of Arts in Biology, Brown University (Graduated Cum Laude)': 1670}}` |
| `final_resume_docx_education_copied_from_base` | `PASS` | `{'section_id': 'education', 'expected_lines': ['Master of Science in Biostatistics, Columbia University (Graduated with Distinction)', 'Bachelor of Arts in Biology, Brown University (Graduated Cum Laude)'], 'positions': {'Master of Science in Biostatistics, Columbia University (Graduated with Distinction)': 1616, 'Bachelor of Arts in Biology, Brown University (Graduated Cum Laude)': 1701}}` |
| `final_resume_certifications_copied_from_base` | `PASS` | `{'section_id': 'certifications', 'expected_lines': ['Certified Machine Learning Engineer – Associate, AWS, 2025', 'Databricks Lakehouse Fundamentals Accreditation, 2023', 'Certified Solutions Architect – Professional, AWS, 2023', 'Fellow of the Society of Actuaries, 2010'], 'positions': {'Certified Machine Learning Engineer – Associate, AWS, 2025': 1768, 'Databricks Lakehouse Fundamentals Accreditation, 2023': 1827, 'Certified Solutions Architect – Professional, AWS, 2023': 1881, 'Fellow of the Society of Actuaries, 2010': 1937}}` |
| `final_resume_docx_certifications_copied_from_base` | `PASS` | `{'section_id': 'certifications', 'expected_lines': ['Certified Machine Learning Engineer – Associate, AWS, 2025', 'Databricks Lakehouse Fundamentals Accreditation, 2023', 'Certified Solutions Architect – Professional, AWS, 2023', 'Fellow of the Society of Actuaries, 2010'], 'positions': {'Certified Machine Learning Engineer – Associate, AWS, 2025': 1798, 'Databricks Lakehouse Fundamentals Accreditation, 2023': 1857, 'Certified Solutions Architect – Professional, AWS, 2023': 1911, 'Fellow of the Society of Actuaries, 2010': 1967}}` |
| `final_resume_no_gap_markers` | `FAIL` | `{'not_completed': True, 'not_generated_by_run': True}` |

Final resume output failed gates: `final_resume_no_gap_markers`

## Judge Execution Ledger

| Section | Judge | Model | Status | Score | Threshold | Pass | Issues |
|---|---|---|---|---:|---:|---|---|
| `run_preflight` | `-` | `-` | `section_not_run` |  |  | `UNKNOWN` | `-` |

## RCA Findings

1. `run_preflight` - Route-signing configuration ingestion failure
   - Root cause: Required route-signing configuration was absent at process ingestion, so the run could not create signed L0 route evidence.
   - Evidence: `C:\Git\Agentic-Workflow-FRESH\.runtime\owner_solo_final_output\brown_brown\fresh_e2e_retry2\e2e_20260804T234403Z_1903ea1d\e2e_preflight_receipt.json`
   - Causal allocation:
     - Dominant cause: Required route-signing configuration was absent at process ingestion, so the run could not create signed L0 route evidence.
     - Retry recoverability: `NONE_WITHIN_CURRENT_PROCESS` - Every judge or generation retry would reuse the same missing environment configuration and would fail before those systems were reached.
     - Allocation rows:
       - `External configuration ingestion` / `ROOT_CAUSE` / `100%`: The launcher process did not receive both required route-signing environment variables before canonical E2E preflight. Evidence: `C:\Git\Agentic-Workflow-FRESH\.runtime\owner_solo_final_output\brown_brown\fresh_e2e_retry2\e2e_20260804T234403Z_1903ea1d\e2e_preflight_receipt.json`. Required work: Inject the secret and key identifier through the approved local environment boundary without persisting or printing the secret.
   - Required implementation plan:
     - Provision the route-signing secret and its non-secret key identifier in the launcher process environment.
     - Keep signing readiness as the first hash-chained E2E stage before research or provider dispatch.
     - Emit and validate the operational RCA, prior-pass bisect, retry accounting, BCG, and L7 output before returning nonzero.
     - Retain regression coverage proving blocked preflight performs zero research, generation, and judge calls and never writes a secret value.

## Section Failure Forensics

Gate `E2E_FAIL_WITHOUT_SECTION_FORENSICS`: `PASS`
- Required: `False`
- Failed section count: `0`
- Artifact directory: `-`
- Baseline confidence: `pinned_baseline_unavailable`

## L6 Shadow Observability

| Section | L6 files | Authority |
|---|---:|---|
| `run_preflight` | 0 | `not_reached` |

## Resume DOCX Full Version Inline

Source: `No authorized resume text emitted; this block is derived only from the current E2E run ledger and final-resume output contract.`

```text
NO_AUTHORIZED_RESUME_OUTPUT
source_of_truth=current_e2e_run_artifacts_only
run_root=C:\Git\Agentic-Workflow-FRESH\.runtime\owner_solo_final_output\brown_brown\fresh_e2e_retry2\e2e_20260804T234403Z_1903ea1d
status=BLOCKED
reason=outcome_authorized_false; final_resume_output_status=FAIL; failed_final_resume_gates=final_resume_no_gap_markers; pre_run_blocked=run_preflight
policy=do_not_inline_FINAL_RESUME_OUTPUT_txt_unless_current_run_authorized
```

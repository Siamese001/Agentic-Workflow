# 🛡️ RG JSON Knowledge Map (Zero Loss)

**Golden Master Source:** `Job_Workflow_v33.2.json`
**Extraction Date:** `2026-01-23 17:30`
**Total Archive Files:** `152`

---

## 1. 📦 Identity & Architecture

- **Schema:** `N/A`
- **Version:** `v33.2`
- **Architecture:** `N/A`
- **Last Updated:** `N/A`
- **Description:** No description

### Patches Applied
- `P-INTEGRATED-FINAL`
- `P006`
- `P007`

## 2. 🔄 Workflow Topology (DAG)

> ⚠️ **WARNING:** No explicit step list found. Scanning for K-nodes...

### K-Node Architecture (46 nodes found)

| K-Node | Name | Purpose |
| :--- | :--- | :--- |
| `K.1` | **Unknown** |  |
| `K.10` | **Unknown** | Cover Letter |
| `K.10_cover_letter_elements` | **🤖 Cover Letter - Specificity-Driven Research Agent (ENHANCED v19.0)** |  |
| `K.11` | **Unknown** | Optimized Skills Keyword Generation |
| `K.11_optimized_skills_generation` | **Optimized Skills Keyword Generation (NEW v27.0)** |  |
| `K.11_supplementary_attachments` | **Supplementary Attachments** |  |
| `K.12_conditional_attachment` | **Unknown** |  |
| `K.1_company_job_title_extraction` | **Company Name & Job Title Extraction** |  |
| `K.2` | **Unknown** | Industry Classification |
| `K.2.5` | **Unknown** | Competitive Positioning |
| `K.2.5_competitive_positioning_agent` | **🤖 Competitive Positioning Agent (NEW v19.0)** |  |
| `K.2_industry_classification` | **Industry Classification** |  |
| `K.3` | **Unknown** | Primary Job Role Mapping |
| `K.3_role_catalog_mapping` | **Primary Job Role Mapping** |  |
| `K.4` | **Unknown** | Professional Headline |
| `K.4_professional_headline` | **Professional Headline** |  |
| `K.4_vs_K.5` | **Unknown** |  |
| `K.4_vs_K.6` | **Unknown** |  |
| `K.4_vs_K.7` | **Unknown** |  |
| `K.4_vs_K.9` | **Unknown** |  |
| `K.5` | **Unknown** | Executive Summary |
| `K.5_executive_summary` | **Executive Summary** |  |
| `K.5_vs_K.6` | **Unknown** |  |
| `K.5_vs_K.7` | **Unknown** |  |
| `K.5_vs_K.9` | **Unknown** |  |
| `K.6` | **Unknown** | Most Recent Experience |
| `K.6_intro_vs_K.4` | **Unknown** |  |
| `K.6_intro_vs_K.5` | **Unknown** |  |
| `K.6_intro_vs_K.9` | **Unknown** |  |
| `K.6_mode_recognition` | **Unknown** | Recognize phase transition from strategic (K.5) to tactical detail (K.6-K.7) and |
| `K.6_most_recent_experience` | **Most Recent Experience (Unify Bullets)** |  |
| `K.6_vs_K.7` | **Unknown** |  |
| `K.6_vs_K.9` | **Unknown** |  |
| `K.7` | **Unknown** | Prior Experience |
| `K.7_intro_vs_K.4` | **Unknown** |  |
| `K.7_intro_vs_K.5` | **Unknown** |  |
| `K.7_intro_vs_K.9` | **Unknown** |  |
| `K.7_mode_recognition` | **Unknown** | Maintain tactical detail mode consistency between K.6 and K.7 |
| `K.7_prior_experience` | **Prior Experience (IBM Bullets)** |  |
| `K.7_vs_K.9` | **Unknown** |  |
| `K.8` | **Unknown** |  |
| `K.8_prior_career_foundation` | **Prior Career Foundation** |  |
| `K.8_vs_all` | **Unknown** |  |
| `K.9` | **Unknown** | Leadership Competencies |
| `K.9_leadership_competencies` | **Leadership Competencies** |  |
| `k_node_output_generic` | **Unknown** | Render with provided title and format exactly as stored in params. |

## 3. 🧠 Prompt Encyclopedia

*Exact text extraction of all detected prompt templates.*

### 📝 Prompt: `3.context.input_acquisition_gate.conditional_logic.if.then.prompts[0].prompt_text`

```text
Please provide the GitHub repository URL.
```

### 📝 Prompt: `3.context.input_acquisition_gate.prompts[0].prompt_text`

```text
Please provide the Job Description URL. If the URL is unavailable or fails, paste the full JD text.
```

### 📝 Prompt: `3.context.input_acquisition_gate.prompts[1].prompt_text`

```text
How would you like to provide the base resumes?
1. Provide a single GitHub repository URL (recommended).
2. Upload each file individually.
```

### 📝 Prompt: `3.context.l_series_configuration.implementation.template_acquisition_gate.prompts[0].prompt_text`

```text
Please upload the consolidated reasoning template file (Reasoning_Transformer_Template_L1.1.md).
```

### 📝 Prompt: `3.context.l_series_configuration.implementation.template_acquisition_gate.prompts[1].prompt_text`

```text
Please upload the raw data source (Transformer_Output_v40.md).
```

### 📝 Prompt: `3.context.l_series_configuration.runtime_mapping.L1.template_ref`

```text
$project_knowledge_search('Reasoning_Transformer_Template_L1.1.md')
```

### 📝 Prompt: `3.context.l_series_configuration.runtime_mapping.L2.template_ref`

```text
$project_knowledge_search('Reasoning_Transformer_Template_L1.1.md')
```

### 📝 Prompt: `3.context.l_series_configuration.runtime_mapping.L3.template_ref`

```text
$project_knowledge_search('Reasoning_Transformer_Template_L1.1.md')
```

### 📝 Prompt: `3.context.toggle_schema_acquisition_gate.execution_logic[1].if_false.prompts[0].prompt_id`

```text
TOGGLE-SCHEMA-001-FALLBACK
```

### 📝 Prompt: `3.context.toggle_schema_acquisition_gate.execution_logic[1].if_false.prompts[0].prompt_text`

```text
🟡 WARNING: `Reasoning_Toggles_Summary_Enforced_Format.json v2.0` was not found in the repository. Please upload the file manually.
```

### 📝 Prompt: `4.reasoning.K.1_company_job_title_extraction.hyde_enrichment.hypothetical_generation_prompt.template`

```text
Given:
- Company: {company_name}
- Title: {job_title}
- Brief JD: {sparse_jd}

Generate a comprehensive 400-word job description including:
1. Likely technical requirements (8-10 specific skills/tools)
2. Leadership scope and team size
3. Key responsibilities (5-7 bullets)
4. Success metrics and KPIs
5. Required experience level and background

Base this on typical {job_title} roles at {company_type} companies.
```

### 📝 Prompt: `4.reasoning.implementation.inter_node_pause_gate.prompt_text`

```text
Press Enter or type 'Y' to continue to the next node.
```

### 📝 Prompt: `4.reasoning.validation_functions.validate_no_company_namedropping.on_fail.regeneration_instruction`

```text
Rewrite in capability-focused style; remove previous employer names; focus on what was accomplished, not where. MUST use third-person implied voice (e.g., 'Established' instead of 'I established').
```

### 📝 Prompt: `4.reasoning.validation_functions.validate_no_target_products_in_past_roles.on_fail.regeneration_instruction`

```text
Replace [TARGET_COMPANY]/[TARGET_PRODUCTS] with generic tech terms: 'cloud data platform','advanced analytics','enterprise data infrastructure','AI/ML platforms'
```

### 📝 Prompt: `5.output.5.10_k10_output_ENHANCED.template_ref`

```text
k_node_output_generic
```

### 📝 Prompt: `5.output.5.11_k11_output_NEW.template_ref`

```text
k_node_output_generic
```

### 📝 Prompt: `5.output.5.1_k1_output.template_ref`

```text
k_node_output_generic
```

### 📝 Prompt: `5.output.5.2.5_k2.5_output_NEW.template_ref`

```text
k_node_output_generic
```

### 📝 Prompt: `5.output.5.2_k2_output.template_ref`

```text
k_node_output_generic
```

### 📝 Prompt: `5.output.5.3_k3_output.template_ref`

```text
k_node_output_generic
```

### 📝 Prompt: `5.output.5.4_k4_output.template_ref`

```text
k_node_output_generic
```

### 📝 Prompt: `5.output.5.6_k6_output.template_ref`

```text
k_node_output_generic
```

### 📝 Prompt: `5.output.5.7_k7_output.template_ref`

```text
k_node_output_generic
```

### 📝 Prompt: `5.output.5.8_k8_output_NEW.template_ref`

```text
k_node_output_generic
```

### 📝 Prompt: `5.output.5.9_k9_output_ENHANCED.template_ref`

```text
k_node_output_generic
```

### 📝 Prompt: `5.output.filename_generation.filename_template`

```text
{sender_profile.username}_{artifact_type}_YYYY-MM-DD_vX.X.json
```

### 📝 Prompt: `6.conditions.templates.hyde_prompt_short.prompt`

```text
Given the job title and any sparse JD bullets, write a 300-400 word hypothetical expanded job description that includes likely responsibilities, skills, and metrics. Keep factual inventiveness plausible and flag hypothetical statements in metadata.
```

## 4. ⚙️ Configuration & Tuning

| Parameter Path | Value |
| :--- | :--- |
| `3.config.canonical_reasoning.K.1.cot_min_paths` | `1` |
| `3.config.canonical_reasoning.K.1.min_tot_depth` | `1` |
| `3.config.canonical_reasoning.K.1.rag_recency_weight` | `0.25` |
| `3.config.canonical_reasoning.K.10.cot_min_paths` | `2` |
| `3.config.canonical_reasoning.K.10.min_tot_depth` | `1` |
| `3.config.canonical_reasoning.K.10.rag_recency_weight` | `0.25` |
| `3.config.canonical_reasoning.K.11.cot_min_paths` | `2` |
| `3.config.canonical_reasoning.K.11.min_tot_depth` | `None` |
| `3.config.canonical_reasoning.K.11.rag_recency_weight` | `0.25` |
| `3.config.canonical_reasoning.K.2.5.cot_min_paths` | `2` |
| `3.config.canonical_reasoning.K.2.5.min_tot_depth` | `4` |
| `3.config.canonical_reasoning.K.2.5.rag_recency_weight` | `0.25` |
| `3.config.canonical_reasoning.K.2.cot_min_paths` | `None` |
| `3.config.canonical_reasoning.K.2.min_tot_depth` | `None` |
| `3.config.canonical_reasoning.K.2.rag_recency_weight` | `0.25` |
| `3.config.canonical_reasoning.K.3.cot_min_paths` | `None` |
| `3.config.canonical_reasoning.K.3.min_tot_depth` | `None` |
| `3.config.canonical_reasoning.K.3.rag_recency_weight` | `0.25` |
| `3.config.canonical_reasoning.K.4.cot_min_paths` | `1` |
| `3.config.canonical_reasoning.K.4.min_tot_depth` | `2` |
| `3.config.canonical_reasoning.K.4.rag_recency_weight` | `0.25` |
| `3.config.canonical_reasoning.K.5.cot_min_paths` | `2` |
| `3.config.canonical_reasoning.K.5.min_tot_depth` | `2` |
| `3.config.canonical_reasoning.K.5.rag_recency_weight` | `0.25` |
| `3.config.canonical_reasoning.K.6.cot_min_paths` | `2` |
| `3.config.canonical_reasoning.K.6.min_tot_depth` | `2` |
| `3.config.canonical_reasoning.K.6.rag_recency_weight` | `0.25` |
| `3.config.canonical_reasoning.K.7.cot_min_paths` | `2` |
| `3.config.canonical_reasoning.K.7.min_tot_depth` | `2` |
| `3.config.canonical_reasoning.K.7.rag_recency_weight` | `0.25` |
| `3.config.canonical_reasoning.K.8.cot_min_paths` | `None` |
| `3.config.canonical_reasoning.K.8.min_tot_depth` | `None` |
| `3.config.canonical_reasoning.K.8.rag_recency_weight` | `0.25` |
| `3.config.canonical_reasoning.K.9.cot_min_paths` | `2` |
| `3.config.canonical_reasoning.K.9.min_tot_depth` | `1` |
| `3.config.canonical_reasoning.K.9.rag_recency_weight` | `0.25` |
| `3.context.bullet_architecture.bullet_pool_size_per_role` | `14` |
| `3.context.dynamic_context_assembly.cknow.graph_lookup.max_depth` | `3` |
| `3.context.dynamic_context_assembly.cmem.episodic_lookup.match_threshold` | `0.85` |
| `3.context.dynamic_context_assembly.cmem.episodic_lookup.max_results` | `20` |
| `3.context.job_application_tracking.prescan_step.matching_logic.fuzzy_matching.threshold` | `0.85` |
| `3.context.l_series_configuration.prompt_structure.input_validation.retry_limit` | `3` |
| `3.context.memory_lanes.episodic.freshness_max_days` | `365` |
| `3.context.memory_lanes.episodic.quota_max_items` | `20` |
| `3.context.memory_lanes.graph.max_depth` | `3` |
| `3.context.memory_lanes.graph.quota_max_nodes` | `200` |
| `3.context.runtime_toggles.prescan_max_retries` | `2` |
| `4.reasoning.K.10_cover_letter_elements.qa_rows[0].threshold` | `3 total (1+2)` |
| `4.reasoning.K.10_cover_letter_elements.qa_rows[1].threshold` | `80-100 words` |
| `4.reasoning.K.10_cover_letter_elements.qa_rows[2].threshold` | `80-100 words` |
| `4.reasoning.K.10_cover_letter_elements.qa_rows[3].threshold` | `80-100 words` |
| `4.reasoning.K.10_cover_letter_elements.qa_rows[4].threshold` | `≥3 company-specific details` |
| `4.reasoning.K.10_cover_letter_elements.qa_rows[5].threshold` | `Unique to this company` |
| `4.reasoning.K.10_cover_letter_elements.qa_rows[6].threshold` | `≥2 quantified achievements` |
| `4.reasoning.K.10_cover_letter_elements.qa_rows[7].threshold` | `Clean` |
| `4.reasoning.K.10_cover_letter_elements.qa_rows[8].threshold` | `≥0.85` |
| `4.reasoning.K.10_cover_letter_elements.v19_specificity_agent.agent_phases.phase_2.pass_threshold` | `≥2 paragraphs must PASS find-replace test` |
| `4.reasoning.K.10_cover_letter_elements.v19_specificity_agent.agent_phases.phase_4.confidence_target` | `≥0.90 that recruiter recognizes research depth` |
| `4.reasoning.K.10_cover_letter_elements.v19_specificity_agent.agent_phases.phase_4.max_iterations` | `3` |
| `4.reasoning.K.10_cover_letter_elements.v19_specificity_agent.agent_phases.phase_5.structure.why_ideal.paragraph_1.word_count` | `80-100 words` |
| `4.reasoning.K.10_cover_letter_elements.v19_specificity_agent.agent_phases.phase_5.structure.why_ideal.paragraph_2.word_count` | `80-100 words` |
| `4.reasoning.K.10_cover_letter_elements.v19_specificity_agent.agent_phases.phase_5.structure.why_interested.word_count` | `80-100 words` |
| `4.reasoning.K.11_optimized_skills_generation.qa_rows[0].threshold` | `10-15 keywords` |
| `4.reasoning.K.11_optimized_skills_generation.qa_rows[1].threshold` | `Top 10 JD keywords included` |
| `4.reasoning.K.11_optimized_skills_generation.qa_rows[2].threshold` | `Mix of technical, soft, and domain skills` |
| `4.reasoning.K.11_supplementary_attachments.attachment_types.references.count` | `3` |
| `4.reasoning.K.1_company_job_title_extraction.display_when_detailed_reasoning_on.placeholder_mapping.{confidence_score}` | `0.0-1.0` |
| `4.reasoning.K.1_company_job_title_extraction.qa_rows[0].threshold` | `Required` |
| `4.reasoning.K.1_company_job_title_extraction.qa_rows[1].threshold` | `Required` |
| `4.reasoning.K.1_company_job_title_extraction.qa_rows[2].threshold` | `Valid URL format` |
| `4.reasoning.K.1_company_job_title_extraction.qa_rows[3].threshold` | `≤8 chars` |
| `4.reasoning.K.1_company_job_title_extraction.qa_rows[4].threshold` | `≥0.95` |
| `4.reasoning.K.2.5_competitive_positioning_agent.agent_phases.phase_1.min_peer_jds` | `3` |
| `4.reasoning.K.2.5_competitive_positioning_agent.qa_rows[0].threshold` | `≥3 peer JDs` |
| `4.reasoning.K.2.5_competitive_positioning_agent.qa_rows[1].threshold` | `≥5 keywords` |
| `4.reasoning.K.2.5_competitive_positioning_agent.qa_rows[2].threshold` | `≥3 keywords` |
| `4.reasoning.K.2.5_competitive_positioning_agent.qa_rows[3].threshold` | `Clear guidance for K.4/K.5` |
| `4.reasoning.K.2.5_competitive_positioning_agent.qa_rows[4].threshold` | `≥0.85` |
| `4.reasoning.K.2_industry_classification.display_when_detailed_reasoning_on.placeholder_mapping.{confidence_score}` | `0.0-1.0` |
| `4.reasoning.K.2_industry_classification.qa_rows[0].threshold` | `Valid taxonomy` |
| `4.reasoning.K.2_industry_classification.qa_rows[1].threshold` | `Consistent with category` |
| `4.reasoning.K.2_industry_classification.qa_rows[2].threshold` | `≥3/5 agreement` |
| `4.reasoning.K.2_industry_classification.qa_rows[3].threshold` | `≥0.90` |
| `4.reasoning.K.3_role_catalog_mapping.display_when_detailed_reasoning_on.placeholder_mapping.{confidence_score}` | `0.0-1.0` |
| `4.reasoning.K.3_role_catalog_mapping.qa_rows[0].threshold` | `Exact catalog match` |
| `4.reasoning.K.3_role_catalog_mapping.qa_rows[1].threshold` | `No secondary role` |
| `4.reasoning.K.3_role_catalog_mapping.qa_rows[2].threshold` | `≥0.85 semantic match` |
| `4.reasoning.K.3_role_catalog_mapping.qa_rows[3].threshold` | `≥0.90` |
| `4.reasoning.K.4_professional_headline.display_when_detailed_reasoning_on.placeholder_mapping.{confidence_score}` | `0.0-1.0` |
| `4.reasoning.K.4_professional_headline.qa_rows[0].threshold` | `Must contain exactly 2 '|' characters` |
| `4.reasoning.K.5_executive_summary.display_when_detailed_reasoning_on.placeholder_mapping.{confidence_score}` | `0.0-1.0` |
| `4.reasoning.K.5_executive_summary.qa_rows[0].on_fail.max_retries` | `3` |
| `4.reasoning.K.5_executive_summary.qa_rows[0].threshold` | `110-130 tokens` |
| `4.reasoning.K.6_most_recent_experience.bullet_structure.word_count_ref` | `3.config.canonical_reasoning.K.6.bullet_word_count_target` |
| `4.reasoning.K.6_most_recent_experience.display_when_detailed_reasoning_on.placeholder_mapping.{confidence_score}` | `0.0-1.0` |
| `4.reasoning.K.6_most_recent_experience.intro_sentence.word_count_ref` | `3.config.canonical_reasoning.K.6.intro_word_count_target` |
| `4.reasoning.K.6_most_recent_experience.qa_rows[0].threshold` | `Field must not be null or empty` |
| `4.reasoning.K.7_prior_experience.bullet_structure.word_count_ref` | `3.config.canonical_reasoning.K.7.bullet_word_count_target` |
| `4.reasoning.K.7_prior_experience.display_when_detailed_reasoning_on.placeholder_mapping.{confidence_score}` | `0.0-1.0` |
| `4.reasoning.K.7_prior_experience.intro_sentence.word_count_ref` | `3.config.canonical_reasoning.K.7.intro_word_count_target` |
| `4.reasoning.K.7_prior_experience.qa_rows[0].threshold` | `Field must not be null or empty` |
| `4.reasoning.K.8_prior_career_foundation.qa_rows[0].threshold` | `Exactly 3` |
| `4.reasoning.K.8_prior_career_foundation.qa_rows[1].threshold` | `Exactly 2 per section` |
| `4.reasoning.K.8_prior_career_foundation.qa_rows[2].threshold` | `All 3 intro fields must not be null or empty` |
| `4.reasoning.K.9_leadership_competencies.competency_structure.word_count_ref` | `3.config.canonical_reasoning.K.9.competency_word_count_target` |
| `4.reasoning.K.9_leadership_competencies.qa_rows[0].threshold` | `Exactly 6` |
| `4.reasoning.K.9_leadership_competencies.qa_rows[10].threshold` | `<0.60 cosine` |
| `4.reasoning.K.9_leadership_competencies.qa_rows[11].threshold` | `Clean` |
| `4.reasoning.K.9_leadership_competencies.qa_rows[12].threshold` | `≥0.88` |
| `4.reasoning.K.9_leadership_competencies.qa_rows[13].threshold` | `Generic platform terms only` |
| `4.reasoning.K.9_leadership_competencies.qa_rows[1].threshold` | `18-24 words each` |
| `4.reasoning.K.9_leadership_competencies.qa_rows[2].threshold` | `≥85% of gaps addressed` |
| `4.reasoning.K.9_leadership_competencies.qa_rows[3].threshold` | `2-3 gap keywords per competency` |
| `4.reasoning.K.9_leadership_competencies.qa_rows[4].threshold` | `Matches LinkedIn/framework patterns` |
| `4.reasoning.K.9_leadership_competencies.qa_rows[5].threshold` | `Plausible given base resume` |
| `4.reasoning.K.9_leadership_competencies.qa_rows[6].threshold` | `≥2 competencies from base resume` |
| `4.reasoning.K.9_leadership_competencies.qa_rows[7].threshold` | `<0.40 cosine` |
| `4.reasoning.K.9_leadership_competencies.qa_rows[8].threshold` | `<0.50 cosine` |
| `4.reasoning.K.9_leadership_competencies.qa_rows[9].threshold` | `<0.60 cosine` |
| `4.reasoning.K.9_leadership_competencies.v19_intelligent_agent.scoring_weight_ref` | `3.config.canonical_reasoning.K.9.gap_coverage_score_weight` |
| `4.reasoning.table_generation.build_reasoning_table.validation.max_columns` | `3` |
| `4.reasoning.validation_functions.validate_no_company_namedropping.on_fail.max_retries` | `3` |
| `4.reasoning.validation_functions.validate_no_target_products_in_past_roles.on_fail.max_retries` | `3` |
| `5.output.release_pipeline.enforcement_summary.retry_logic.max_retries_per_validation` | `3` |
| `5.output.scheduling_assistant.calculation.get_next_business_days.count` | `5` |
| `6.conditions.policies.rag_validation_framework.modes.balanced.min_evidence` | `1` |
| `6.conditions.policies.rag_validation_framework.modes.balanced.min_signal_quality` | `0.6` |
| `6.conditions.policies.rag_validation_framework.modes.permissive.min_evidence` | `0` |
| `6.conditions.policies.rag_validation_framework.modes.permissive.min_signal_quality` | `0.4` |
| `6.conditions.policies.rag_validation_framework.modes.strict.min_evidence` | `2` |
| `6.conditions.policies.rag_validation_framework.modes.strict.min_signal_quality` | `0.75` |
| `6.conditions.templates.hop_refinement.max_refinements` | `2` |
| `6.conditions.templates.self_rag_validation.claim_coverage_threshold_default` | `0.85` |
| `6.conditions.templates.self_rag_validation.max_iterations_default` | `3` |
| `6.conditions.templates.signal_quality.min_accept_score` | `0.5` |
| `6.conditions.templates.signal_quality.weights.cross_encoder_score` | `0.3` |
| `6.conditions.templates.two_stage_retrieval.crossencoder_model_ref` | `models/cross-encoder-ms-marco` |
| `6.conditions.validation_functions.validate_headline_character_limit.on_fail.max_retries` | `3` |
| `6.conditions.validation_gates.competency_word_count_balance.max_variance_coefficient` | `0.25` |

## 5. ✅ Validation Rules

### Rule: `2.task.state_machine.transitions[0].guard`
> all_base_files_provided

### Rule: `2.task.state_machine.transitions[1].guard`
> source_context_validated_and_conflict_free

### Rule: `2.task.state_machine.transitions[2].guard`
> toggles_approved

### Rule: `2.task.state_machine.transitions[3].guard`
> all_k_nodes_complete_and_validated

### Rule: `2.task.state_machine.transitions[4].guard`
> text_output_generated

### Rule: `2.task.state_machine.transitions[5].guard`
> submission_confirmed_Y

### Rule: `2.task.state_machine.transitions[6].guard`
> submission_confirmed_N

### Rule: `2.task.state_machine.transitions[7].guard`
> tracker_output_generated

### Rule: `3.context.l_series_configuration.dynamic_intelligence_rules.length_constraint`
> Total output ≤ 120% of template file character count

### Rule: `3.context.l_series_configuration.extended_sequence.validation`
> Must have valid L-Series selection if detailed_reasoning == 'Yes'

### Rule: `3.context.l_series_configuration.output.propagates_to`
> Section 4 K-node execution

### Rule: `3.context.preflight_checks.K.6_mode_recognition.checkpoint`
> BEFORE_K6_EXECUTION

### Rule: `3.context.preflight_checks.K.7_mode_recognition.checkpoint`
> BEFORE_K7_EXECUTION

### Rule: `4.reasoning.K.10_cover_letter_elements.qa_rows[0].check`
> Paragraph count

### Rule: `4.reasoning.K.10_cover_letter_elements.qa_rows[1].check`
> Why Interested length

### Rule: `4.reasoning.K.10_cover_letter_elements.qa_rows[2].check`
> Why Ideal Para 1 length

### Rule: `4.reasoning.K.10_cover_letter_elements.qa_rows[3].check`
> Why Ideal Para 2 length

### Rule: `4.reasoning.K.10_cover_letter_elements.qa_rows[4].check`
> Company specificity

### Rule: `4.reasoning.K.10_cover_letter_elements.qa_rows[5].check`
> Authenticity test

### Rule: `4.reasoning.K.10_cover_letter_elements.qa_rows[6].check`
> Proof points

### Rule: `4.reasoning.K.10_cover_letter_elements.qa_rows[7].check`
> ASCII hygiene

### Rule: `4.reasoning.K.11_optimized_skills_generation.qa_rows[0].check`
> Keyword count

### Rule: `4.reasoning.K.11_optimized_skills_generation.qa_rows[1].check`
> ATS Relevance

### Rule: `4.reasoning.K.11_optimized_skills_generation.qa_rows[2].check`
> Coverage balance

### Rule: `4.reasoning.K.1_company_job_title_extraction.qa_rows[0].check`
> Company name present

### Rule: `4.reasoning.K.1_company_job_title_extraction.qa_rows[1].check`
> Job title present

### Rule: `4.reasoning.K.1_company_job_title_extraction.qa_rows[2].check`
> Job URL validated

### Rule: `4.reasoning.K.1_company_job_title_extraction.qa_rows[3].check`
> Req number (if present)

### Rule: `4.reasoning.K.2.5_competitive_positioning_agent.qa_rows[0].check`
> Peer JDs found

### Rule: `4.reasoning.K.2.5_competitive_positioning_agent.qa_rows[1].check`
> Table stakes identified

### Rule: `4.reasoning.K.2.5_competitive_positioning_agent.qa_rows[2].check`
> Differentiators identified

### Rule: `4.reasoning.K.2.5_competitive_positioning_agent.qa_rows[3].check`
> Positioning strategy

### Rule: `4.reasoning.K.2_industry_classification.qa_rows[0].check`
> Category from GICS/SIC

### Rule: `4.reasoning.K.2_industry_classification.qa_rows[1].check`
> Sub-category aligned

### Rule: `4.reasoning.K.2_industry_classification.qa_rows[2].check`
> Self-consistency votes

### Rule: `4.reasoning.K.3_role_catalog_mapping.qa_rows[0].check`
> Role from catalog

### Rule: `4.reasoning.K.3_role_catalog_mapping.qa_rows[1].check`
> Single role only

### Rule: `4.reasoning.K.3_role_catalog_mapping.qa_rows[2].check`
> JD alignment

### Rule: `4.reasoning.K.4_professional_headline.qa_rows[0].check`
> 3-Axis Format Enforcement

### Rule: `4.reasoning.K.4_professional_headline.three_axis_framework.constraint`
> Strategic positioning - NOT tactical execution (avoid 'delivering', 'executing', 'managing')

### Rule: `4.reasoning.K.5_executive_summary.qa_rows[0].check`
> Token count

### Rule: `4.reasoning.K.5_executive_summary.qa_rows[0].on_fail.constraint`
> Output MUST be between 110 and 130 tokens.

### Rule: `4.reasoning.K.6_most_recent_experience.qa_rows[0].check`
> Intro Sentence Presence

### Rule: `4.reasoning.K.7_prior_experience.qa_rows[0].check`
> Intro Sentence Presence

### Rule: `4.reasoning.K.8_prior_career_foundation.qa_rows[0].check`
> Section Count

### Rule: `4.reasoning.K.8_prior_career_foundation.qa_rows[1].check`
> Bullet Count

### Rule: `4.reasoning.K.8_prior_career_foundation.qa_rows[2].check`
> Intro Sentence Presence

### Rule: `4.reasoning.K.9_leadership_competencies.qa_rows[0].check`
> Competency count

### Rule: `4.reasoning.K.9_leadership_competencies.qa_rows[10].check`
> Dedup vs K.7

### Rule: `4.reasoning.K.9_leadership_competencies.qa_rows[11].check`
> ASCII hygiene

### Rule: `4.reasoning.K.9_leadership_competencies.qa_rows[12].check`
> Overall score

### Rule: `4.reasoning.K.9_leadership_competencies.qa_rows[13].check`
> No target company products in competencies

### Rule: `4.reasoning.K.9_leadership_competencies.qa_rows[13].validation`
> validate_no_target_products_in_past_roles()

### Rule: `4.reasoning.K.9_leadership_competencies.qa_rows[1].check`
> Description length

### Rule: `4.reasoning.K.9_leadership_competencies.qa_rows[2].check`
> Keyword gap coverage

### Rule: `4.reasoning.K.9_leadership_competencies.qa_rows[3].check`
> Keyword density

### Rule: `4.reasoning.K.9_leadership_competencies.qa_rows[4].check`
> Authentic phrasing

### Rule: `4.reasoning.K.9_leadership_competencies.qa_rows[5].check`
> Credibility

### Rule: `4.reasoning.K.9_leadership_competencies.qa_rows[7].check`
> Dedup vs K.4

### Rule: `4.reasoning.K.9_leadership_competencies.qa_rows[8].check`
> Dedup vs K.5

### Rule: `4.reasoning.K.9_leadership_competencies.qa_rows[9].check`
> Dedup vs K.6

### Rule: `4.reasoning.execution_prerequisites.prerequisite_checks[0].check`
> approval_received == true

### Rule: `4.reasoning.node_schema.section_id.validation`
> Must be integer between 1-6

- **4.reasoning.visualization_pipeline.initialization.gate_1_mandatory:** `True`
### Rule: `5.output.execution_gate`
> Section 5 CANNOT begin until K.1-K.11 complete with PASS status

### Rule: `5.output.post_processing.remove_section_numbers.validation`
> Final output contains no K.1, K.2, etc. in body text

- **5.output.release_pipeline.enforcement_summary.retry_logic.max_retries_per_validation:** `3`
### Rule: `5.output.templates.resume_header_format.validation`
> Resume name appears on line 4, headline on line 6, no K.4 prefix in final output

### Rule: `6.conditions.validation_gates.V-SCHEMA-001.check`
> All generated field names MUST exist in App_Schema_v4.json's defined fields

### Rule: `6.conditions.validation_gates.bullet_punctuation.check_method`
> Regex: all bullets match pattern '.*\.$'

### Rule: `6.conditions.validation_gates.bullet_punctuation.gate_id`
> VG_BULLET_PUNCTUATION

### Rule: `6.conditions.validation_gates.bullet_punctuation.validation`
> All bullets must end with period '.' character

### Rule: `6.conditions.validation_gates.competency_bullet_ratio.gate_id`
> VG_COMP_BULLET_RATIO

### Rule: `6.conditions.validation_gates.competency_word_count_balance.check_method`
> Calculate word count per competency, compute variance, flag if CV > 0.25

### Rule: `6.conditions.validation_gates.competency_word_count_balance.gate_id`
> VG_COMPETENCY_BALANCE

### Rule: `6.conditions.validation_gates.competency_word_count_balance.validation`
> All 6 competencies must have word counts within 22-28 words. Coefficient of variation < 0.25

### Rule: `6.conditions.validation_gates.cross_section_redundancy.check_method`
> Tokenize all sections, compute n-gram overlap (n=3,4,5), flag duplicates

### Rule: `6.conditions.validation_gates.cross_section_redundancy.gate_id`
> VG_REDUNDANCY_CHECK

### Rule: `6.conditions.validation_gates.cross_section_redundancy.validation`
> Check for phrases appearing in 2+ sections (K.5, K.6, K.7, K.9, K.8). Target: <10% overlap

### Rule: `6.conditions.validation_gates.natural_hyphen_preservation.gate_id`
> VG_NATURAL_HYPHENS

### Rule: `6.conditions.validation_gates.natural_hyphen_preservation.validation`
> Scan for unnatural hyphens removed AND natural hyphens preserved based on external configuration file.

### Rule: `6.conditions.validation_gates.source_conflict_resolution_gate.gate_id`
> VG_SOURCE_CONFLICT_CHECK

### Rule: `7.post_submission.compile_app_schema_on_submission.prerequisites.check`
> FILE_EXISTS: App_Schema_v4.json


## 7. 📊 Top-Level Structure

```
├── metadata/ (13 keys)
├── 1.role/ (6 keys)
├── 2.task/ (1 keys)
├── 3.context/ (13 keys)
├── 3.config/ (1 keys)
├── 4.reasoning/ (28 keys)
├── 5.output/ (30 keys)
├── 6.conditions/ (6 keys)
├── 7.post_submission/ (1 keys)
```

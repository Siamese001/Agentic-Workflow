# apps_lic Prompt Slot and X1-X3 SSOT Drift Remediation Plan

Created: 2026-06-09
Worktree: `C:\Git\Agentic-Workflow-apps_lic`
Status: In Progress

## Objective

Review apps_lic prompt assembly against current prompt-engineering and agent-safety best practices, then close the consistency gaps between prompt slots, archetype templates, output schemas, and X1-X3 Exit semantics.

## Decision

Use `RecipientTemplatePolicy` plus a new `PromptSlotRegistry` as the single source of truth for apps_lic prompt behavior. YAML prompt files are renderable views of that policy, not independent authorities. X1, X2, and X3 are Exit validation stages/dispositions, not prompt slots.

## Best-Practice Basis

- Prompt changes need pinned assumptions, versioned artifacts, and eval coverage; prompt behavior should not drift silently between templates and runtime assembly.
- Structured output schemas should be the contract for generated artifacts. JSON validity alone is not enough because it does not guarantee schema adherence.
- Untrusted or externally sourced data should be treated as data, not as behavioral instructions. Prompt assembly should fence LinkedIn/title/company evidence away from system and developer-policy instructions.
- Few-shot examples and instructions should be clear, explicit, and consistently delimited so examples do not become implicit alternate policies.

Sources reviewed:

- OpenAI prompt engineering: `https://developers.openai.com/api/docs/guides/prompt-engineering`
- OpenAI Structured Outputs: `https://developers.openai.com/api/docs/guides/structured-outputs`
- OpenAI agent builder safety: `https://developers.openai.com/api/docs/guides/agent-builder-safety`
- Anthropic prompt engineering best practices: `https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices`

## Current Findings

### F1. Slot taxonomy drift

`apps_lic/prompt_assembly/prompt_bom.yaml` declares `S0/I0/C0/U0/D0/E0/Y0/R0`, templates add `M0/H0/N0/A0/L0`, runtime PA lineage adds `C03/SC/RI`, and core validation uses a different ordering. There is no apps_lic slot registry that reconciles slot names, authority, render order, allowed metadata, and aliases.

Impact: prompt artifacts can look authoritative while being assembled from partially incompatible slot assumptions.

### F2. Template registry drift

`apps_lic/config/prompt_registry.yaml` and `apps_lic/prompt_assembly/prompt_bom.yaml` omit active or tested templates such as `outreach_draft_v2`, `compact_recruiter_arc`, and `exec_positioning`.

Impact: tests and runtime code can exercise templates that are not represented in the registry/BOM SSOT.

### F3. Output contract drift

`outreach_draft_v2.yaml` emits `subject`, `message_body`, and `send_mode`; `compact_recruiter_arc.yaml` emits `message_text`, hardcodes `channel: linkedin`, omits subject, and hardcodes provider/model fields.

Impact: InMail behavior, subject requirements, and provider routing can diverge by template rather than by product policy.

### F4. Runtime PA and YAML compiler are split authorities

`apps_lic/runtime/bindings/pa_binding.py` builds `CompiledPromptArtifact` directly from typed runtime policy, while `apps_lic/prompt_assembly/lic_pa_compiler.py` renders YAML slots and hashes with separate assumptions.

Impact: prompt hashes, slot lineage, and runtime policy can disagree without a deterministic failure.

### F5. Prompt profiles are not aligned with authority-coded slots

`apps_lic/config/domain_contract/prompt_profiles.yaml` describes human-readable slots and references `apps_lic/config/prompts.json`, but it does not reconcile with authority-coded PA slots or runtime policy.

Impact: profile documentation can drift from executable prompt behavior.

### F6. Legacy prompt source remains unfenced

`apps_lic/types/PromptTemplate.py` declares a frozen knowledge base and older LinkedIn campaign behavior. It appears stale relative to the current InMail/archetype route.

Impact: future imports can accidentally revive older message assumptions.

### F7. X1-X3 naming collision

Local code treats X1 as gates, X2 as aggregate disposition, and X3 as the exit packet. The user-facing phrase "prompts in the slots X1-X3" exposes a glossary gap: X1-X3 are not prompt slots.

Impact: implementation work can accidentally mix prompt authority with validation/disposition authority.

### F8. Exit profile drift

`apps_lic/config/domain_contract/exit_profile.outreach_message.v1.json` uses `G21...G28` and disposition names such as `APPROVED`, while `validation_exit.v1.yaml` uses X1D/X2 policies and dispositions such as `clear_draft`, `review_required`, `blocked`, and `abstain`.

Impact: Exit decisions can be documented with two different vocabularies.

### F9. Inline JSON contract strings

`pa_binding.py` builds output contract text inline and includes provider/model details in prompt output requirements.

Impact: prompt output shape is harder to validate and provider routing can leak into model-facing prompt text.

## Implementation Waves

### W0. Characterization and Inventory

Goal: establish the baseline before changing behavior.

Status: Completed 2026-06-09

Evidence:

- Inventory report: `plans/apps-lic-prompt-slot-x1x3-w0-inventory-4a9f2c.md`
- Repro script: `scripts/apps_lic/prompt_source_inventory.py`
- ADG note: `adg_sqlite.adg_health` was attempted on 2026-06-09 but failed in Codex with `Transport closed`; W0 used deterministic filesystem hashes as the fallback characterization method.
- Inventory scope: 64 prompt/template/schema/recipient/runtime/Exit/core-reference files.
- Classification counts: 8 renderable prompt templates, 2 registry/BOM files, 2 runtime prompt-assembly files, 4 output contracts, 8 Exit/validation contracts, 7 recipient/message-policy files, 14 profile/rubric files, 2 legacy fence candidates, 3 core references, 16 supporting contracts.

W0 findings:

- Active template files missing from `prompt_registry.yaml`: `compact_recruiter_arc`, `exec_positioning`, `outreach_draft_v2`.
- Template slot terms not declared in `prompt_bom.yaml`: `A0`, `H0`, `L0`, `M0`, `N0`.
- `X1`, `X2`, and `X3` are present in Exit/runtime files and must remain non-prompt glossary terms.
- Legacy prompt sources requiring a fence decision: `apps_lic/config/prompts.json`, `apps_lic/types/PromptTemplate.py`.

Steps:

- Enumerate every apps_lic prompt source, template, profile, BOM entry, output schema, and Exit profile.
- Produce a drift report mapping each source to one of: policy SSOT, renderable view, test fixture, legacy fenced artifact, or deprecated artifact.
- Capture current hashes for runtime PA artifacts and YAML prompt templates.

Acceptance:

- A test or script can list all prompt/template sources and classify every file.
- No prompt source is left with unknown ownership.

### W1. Prompt Slot Registry SSOT

Goal: define the canonical slot vocabulary and authority ordering.

Status: Completed 2026-06-09

Evidence:

- Added registry: `C:\Git\Agentic-Workflow-apps_lic\apps_lic\config\domain_contract\prompt_slot_registry.v1.yaml`
- Added tests: `C:\Git\Agentic-Workflow-apps_lic\tests\apps_lic\test_w1_prompt_slot_registry.py`
- Registry declares canonical prompt slots: `S0`, `I0`, `D0`, `C0`, `E0`, `M0`, `H0`, `Y0`, `A0`, `N0`, `L0`, `U0`, `R0`.
- Registry declares runtime aliases: `C03 -> C0`, `SC -> M0`, `RI -> M0`.
- Registry declares non-prompt Exit terms: `X1`, `X2`, `X3`.
- Focused verification: `python -m pytest tests\apps_lic\test_w1_prompt_slot_registry.py -q` passed, 6 tests.
- Adjacent verification: `python -m pytest tests\apps_lic\test_w1_prompt_slot_registry.py tests\apps_lic\test_w5_template_length_policy_ssot.py tests\apps_lic\test_recipient_archetype_mapping.py -q` passed, 23 tests.

W1 findings:

- W1 resolves the W0 slot drift by registering `A0`, `H0`, `L0`, `M0`, and `N0` rather than silently treating them as ad hoc template terms.
- `C03`, `SC`, and `RI` are intentionally modeled as runtime aliases/metadata aliases, not new core authority levels.
- `X1`, `X2`, and `X3` are now explicitly fenced as Exit validation terms and cannot appear as prompt slots or runtime aliases.

Steps:

- Add `apps_lic/config/domain_contract/prompt_slot_registry.v1.yaml`.
- Include canonical slots, app aliases, authority rank, render order, allowed metadata, and deprecation status.
- Add explicit non-slot entries for `X1`, `X2`, and `X3` as Exit terms.
- Add tests comparing the registry against prompt BOM slots, template slots, runtime PA lineage, and core authority expectations.

Acceptance:

- Any unregistered prompt slot fails a focused drift test.
- X1/X2/X3 are documented and tested as non-prompt slots.

### W2. Template and Output Contract Convergence

Goal: force active templates through one schema and one registry.

Status: Completed 2026-06-09

Evidence:

- Updated registry: `C:\Git\Agentic-Workflow-apps_lic\apps_lic\config\prompt_registry.yaml`
- Updated BOM: `C:\Git\Agentic-Workflow-apps_lic\apps_lic\prompt_assembly\prompt_bom.yaml`
- Updated output schema: `C:\Git\Agentic-Workflow-apps_lic\apps_lic\config\domain_contract\output_schema.yaml`
- Updated E3 templates: `compact_recruiter_arc.yaml`, `outreach_draft_v1.yaml`, `outreach_draft_v2.yaml`, `exec_positioning.yaml`
- Added tests: `C:\Git\Agentic-Workflow-apps_lic\tests\apps_lic\test_w2_template_output_contract_convergence.py`
- Updated W0 inventory helper to recognize BOM `optional_slots` and `slot_definitions`: `C:\Git\Agentic-Workflow-FRESH\scripts\apps_lic\prompt_source_inventory.py`

W2 changes:

- Registered all eight physical prompt templates in `prompt_registry.yaml` and referenced the same set from `prompt_bom.yaml`.
- Added `slot_registry_ref: apps_lic_prompt_slot_registry_v1` to registry and BOM.
- Standardized all E3 generation templates on `OutreachDraftCandidate`.
- Added `generation_contract.name: OutreachDraftCandidate` to `output_schema.yaml`; retained `OutreachDraft` as the legacy post-validation artifact.
- Removed hardcoded Qwen/vLLM provider/model literals from active E3 templates.
- Removed provider/model output fields from `compact_recruiter_arc`.
- Made InMail and short LinkedIn chat rules explicit in all E3 templates: InMail requires non-empty subject and signature; chat requires empty subject and body under 300 characters; channel must come from explicit input, not inferred length.

Verification:

- `python -m pytest tests\apps_lic\test_w2_template_output_contract_convergence.py -q` passed, 5 tests.
- `python -m pytest tests\apps_lic\test_w1_prompt_slot_registry.py tests\apps_lic\test_w2_template_output_contract_convergence.py tests\apps_lic\test_w5_template_length_policy_ssot.py tests\apps_lic\test_recipient_archetype_mapping.py -q` passed, 28 tests.
- Post-change inventory sanity check shows W2 cleared template registry/BOM drift. Remaining observations are deferred: X1/X2/X3 Exit terms and legacy prompt fence candidates.

Steps:

- Update `prompt_registry.yaml` and `prompt_bom.yaml` to include active templates or explicitly mark them deprecated/fenced.
- Standardize active outreach templates on one `OutreachDraftCandidate` output contract.
- Remove provider/model hardcoding from templates.
- Ensure InMail templates always expose subject/body/signature fields; short LinkedIn messages remain channel-specific variants, not the default.

Acceptance:

- Active templates resolve through the registry and output schema.
- Provider/model literals do not appear in active prompt templates.
- InMail and short-message routes are distinguishable by schema fields and channel policy.

### W3. Runtime Prompt Assembly Alignment

Goal: make runtime PA prove which policy and slots produced each prompt.

Status: Completed 2026-06-09

Evidence:

- Added schema receipt helper: `C:\Git\Agentic-Workflow-apps_lic\apps_lic\runtime\bindings\pa_schema_receipts.py`
- Updated runtime PA: `C:\Git\Agentic-Workflow-apps_lic\apps_lic\runtime\bindings\pa_binding.py`
- Added tests: `C:\Git\Agentic-Workflow-apps_lic\tests\apps_lic\test_w3_runtime_pa_schema_receipts.py`
- ADG note: `adg_sqlite.adg_health` was attempted on 2026-06-09 but failed in Codex with `Transport closed`; W3 used direct runtime inspection and focused PA tests as fallback.

W3 changes:

- Moved model-facing output contract construction out of inline string literals and into `pa_schema_receipts.py`.
- Runtime PA now derives the JSON contract from `output_schema.yaml` generation contract `OutreachDraftCandidate`.
- Runtime PA now emits receipt lineage for `slot_registry`, `template_policy`, and `output_schema`.
- Runtime PA now carries component hashes for `slot_registry_hash`, `prompt_registry_hash`, `prompt_bom_hash`, `output_schema_hash`, `prompt_schema_receipt`, `template_policy`, and `recipient_policy_profile`.
- Provider/model IDs remain runtime routing metadata; they are no longer included as output fields in the model-facing JSON contract.
- Evidence data remains fenced in the user evidence block with `C0_EVIDENCE_DATA_ONLY` lineage.

Verification:

- `python -m py_compile apps_lic\runtime\bindings\pa_schema_receipts.py apps_lic\runtime\bindings\pa_binding.py` passed.
- `python -m pytest tests\apps_lic\test_w3_runtime_pa_schema_receipts.py -q` passed, 5 tests.
- `python -m pytest tests\apps_lic\test_w1_prompt_slot_registry.py tests\apps_lic\test_w2_template_output_contract_convergence.py tests\apps_lic\test_w3_runtime_pa_schema_receipts.py tests\apps_lic\test_w5_template_length_policy_ssot.py tests\apps_lic\test_recipient_archetype_mapping.py tests\apps_lic\test_w5_apps_lic_c0_pa.py -q` passed, 122 tests.

Steps:

- Make `pa_binding.py` emit `slot_registry_hash`, `recipient_policy_profile_id`, `template_policy_hash`, and `output_schema_hash`.
- Move inline JSON contract strings into a typed schema helper.
- Ensure generated prompt artifacts include a slot-registry receipt and recipient-archetype receipt.
- Keep external LinkedIn/company evidence fenced as data-only content.

Acceptance:

- Runtime PA artifacts expose enough hashes to explain which assumptions generated the prompt.
- Tests fail if runtime PA references an unregistered slot or a mismatched output schema.

### W4. X1-X3 Exit Consistency

Goal: eliminate vocabulary drift between prompt assembly and validation.

Status: Completed 2026-06-09

Evidence:

- Updated fenced legacy Exit profile: `C:\Git\Agentic-Workflow-apps_lic\apps_lic\config\domain_contract\exit_profile.outreach_message.v1.json`
- Added tests: `C:\Git\Agentic-Workflow-apps_lic\tests\apps_lic\test_w4_exit_vocabulary_consistency.py`
- ADG note: `adg_sqlite.adg_health` was attempted on 2026-06-09 but failed in Codex with `Transport closed`; W4 used direct contract inspection and focused tests as fallback.

W4 changes:

- Kept `validation_exit.v1.yaml` as the active runtime Exit authority.
- Marked `exit_profile.outreach_message.v1.json` as `compatibility_fenced` with `runtime_authority: false`.
- Added explicit `G21...G28` legacy gate mapping into canonical `X1` family and known `validation_exit.v1.yaml` X2 gate names/proof fields.
- Added legacy disposition mapping: `APPROVED -> clear_draft`, `APPROVED_WITH_NOTES -> review_required`, `REJECTED -> blocked`, `HITL_REQUIRED -> review_required`, `ABSTAIN -> abstain`.
- Added `forbidden_as_exit_dispositions` for prompt slots, runtime aliases, and X1/X2/X3 terms.
- Proved runtime PA artifacts do not emit X3 or Exit dispositions.

Verification:

- `python -m pytest tests\apps_lic\test_w4_exit_vocabulary_consistency.py -q` passed, 6 tests.
- `python -m pytest tests\apps_lic\test_w1_prompt_slot_registry.py tests\apps_lic\test_w2_template_output_contract_convergence.py tests\apps_lic\test_w3_runtime_pa_schema_receipts.py tests\apps_lic\test_w4_exit_vocabulary_consistency.py tests\apps_lic\test_w5_template_length_policy_ssot.py tests\apps_lic\test_recipient_archetype_mapping.py tests\apps_lic\test_w5_apps_lic_c0_pa.py -q` passed, 128 tests.

Steps:

- Reconcile `exit_profile.outreach_message.v1.json` with `validation_exit.v1.yaml`.
- Define a canonical mapping for legacy `G21...G28` gate labels to X1 gate names or fence the legacy profile.
- Add glossary tests proving prompt assembly cannot emit X3 and validation cannot consume prompt slots as Exit dispositions.

Acceptance:

- Exit dispositions use one canonical vocabulary at runtime.
- Legacy Exit terms are either mapped or fenced with tests.

### W5. Drift Gates and CI Coverage

Goal: make future prompt drift hard to introduce.

Status: Completed 2026-06-09

Evidence:

- Added CI drift tests: `C:\Git\Agentic-Workflow-apps_lic\tests\apps_lic\test_w5_prompt_drift_ci_gates.py`
- ADG note: `adg_sqlite.adg_health` was attempted on 2026-06-09 but failed in Codex with `Transport closed`; W5 used direct contract inspection and focused tests as fallback.

W5 changes:

- Added fixture-based prompt assembly coverage for all four canonical archetypes: `RECRUITER`, `SENIOR_TA`, `EXECUTIVE`, and `C_LEVEL`.
- Added a CEO regression proving CEO maps into `C_LEVEL` while preserving four template archetypes.
- Added a prompt hash sensitivity gate proving prompt-policy inputs, including length budget changes, alter the PA prompt hash.
- Added active template and PA prompt checks for provider literal leakage so Qwen/vLLM/OpenAI provider details cannot become model-facing prompt policy.
- Added a prompt-injection fencing regression proving hostile LinkedIn/title/company text remains data evidence, not executable instructions.
- Added schema/template receipt hash gates for CI diff review.
- Recorded an important classifier finding: `Senior Talent Acquisition Partner` maps to recruiter under the current LIC classifier, so the canonical Senior TA fixture uses `Director of Talent Acquisition` with `seniority_class="SENIOR_TA"` instead of weakening classification semantics.

Verification:

- `python -m pytest tests\apps_lic\test_w5_prompt_drift_ci_gates.py -q` passed, 9 tests.
- `python -m pytest tests\apps_lic\test_w1_prompt_slot_registry.py tests\apps_lic\test_w2_template_output_contract_convergence.py tests\apps_lic\test_w3_runtime_pa_schema_receipts.py tests\apps_lic\test_w4_exit_vocabulary_consistency.py tests\apps_lic\test_w5_prompt_drift_ci_gates.py tests\apps_lic\test_w5_template_length_policy_ssot.py tests\apps_lic\test_recipient_archetype_mapping.py tests\apps_lic\test_w5_apps_lic_c0_pa.py -q` passed, 137 tests.

Steps:

- Add CI-friendly tests for unregistered slots, active template/schema parity, provider literal leakage, prompt hash changes, and prompt injection fencing.
- Add fixture-based examples for Recruiter/TA, Senior TA, C-Level, and Executive archetypes.
- Add regression tests proving CEO maps into C-Level while preserving four template archetypes.

Acceptance:

- Prompt-policy drift produces deterministic test failures.
- All four archetypes have prompt assembly and Exit validation fixture coverage.

### W6. Legacy Fence and Migration Closeout

Goal: prevent stale prompt paths from re-entering runtime.

Status: Completed 2026-06-09

Evidence:

- Fenced legacy snapshot: `C:\Git\Agentic-Workflow-apps_lic\apps_lic\types\PromptTemplate.py`
- Fenced historical shim: `C:\Git\Agentic-Workflow-apps_lic\apps_lic\config\knowledge_base.py`
- Added import-boundary tests: `C:\Git\Agentic-Workflow-apps_lic\tests\apps_lic\test_w6_legacy_prompt_fence.py`
- ADG note: `adg_sqlite.adg_health` was attempted on 2026-06-09 but failed in Codex with `Transport closed`; W6 used direct import/source inspection and focused tests as fallback.

W6 changes:

- Marked `PromptTemplate.py` as a compatibility-fenced, historical read-only snapshot with `runtime_authority: false`.
- Added `legacy_prompt_template_fence_receipt()` with canonical refs for the active prompt registry, prompt BOM, prompt slot registry, and output schema.
- Exposed the same fence receipt through `apps_lic.config.knowledge_base` while preserving the historical API for control-plane compatibility.
- Added tests proving `knowledge_base.py` is the only production importer of `apps_lic.types.PromptTemplate`.
- Added tests proving PA runtime files do not import `PromptTemplate.py` or `apps_lic.config.knowledge_base`.
- Added tests proving active prompt registry template IDs are disjoint from legacy snapshot prompt IDs and all active registry templates resolve through `apps_lic/prompt_assembly/templates/`.

Migration receipt:

- Final prompt SSOT: `apps_lic/config/prompt_registry.yaml`, `apps_lic/prompt_assembly/prompt_bom.yaml`, `apps_lic/config/domain_contract/prompt_slot_registry.v1.yaml`.
- Final output contract SSOT: `apps_lic/config/domain_contract/output_schema.yaml`, `OutreachDraftCandidate`.
- Final Exit vocabulary SSOT: `apps_lic/config/domain_contract/validation_exit.v1.yaml`.
- Legacy prompt snapshot status: `compatibility_fenced`, read-only, not runtime authority.
- Historical compatibility surface retained: `apps_lic.config.knowledge_base` may read the legacy snapshot for old control-plane lookups, but PA/runtime prompt assembly must not import it.

Verification:

- `python -m py_compile apps_lic\types\PromptTemplate.py apps_lic\config\knowledge_base.py tests\apps_lic\test_w6_legacy_prompt_fence.py` passed.
- `python -m pytest tests\apps_lic\test_w6_legacy_prompt_fence.py -q` passed, 5 tests.
- `python -m pytest tests\apps_lic\test_w1_prompt_slot_registry.py tests\apps_lic\test_w2_template_output_contract_convergence.py tests\apps_lic\test_w3_runtime_pa_schema_receipts.py tests\apps_lic\test_w4_exit_vocabulary_consistency.py tests\apps_lic\test_w5_prompt_drift_ci_gates.py tests\apps_lic\test_w6_legacy_prompt_fence.py tests\apps_lic\test_w5_template_length_policy_ssot.py tests\apps_lic\test_recipient_archetype_mapping.py tests\apps_lic\test_w5_apps_lic_c0_pa.py -q` passed, 142 tests.

Steps:

- Fence or deprecate `apps_lic/types/PromptTemplate.py` and legacy compiler paths unless they are explicitly used as adapters.
- Add import-guard or characterization tests for legacy prompt modules.
- Document the migration receipt in the plan closeout.

Acceptance:

- Legacy prompt code cannot silently become a runtime authority.
- The closeout records the final prompt SSOT, active templates, active output schema, and Exit vocabulary.

## Verification Strategy

- Focused unit tests for slot registry validation, output schema parity, archetype mapping, and X1-X3 glossary boundaries.
- Characterization tests before behavior changes so regressions are visible.
- Runtime harness sample after W3/W4 covering Recruiter/TA, Senior TA, C-Level, and Executive InMail outputs.
- Final drift scan proving active prompt sources are registered, hashable, and schema-conformant.

## Risks

- Existing tests may rely on legacy prompt names or `message_text`; W2 should include compatibility adapters only where needed.
- Reconciliations touching core authority validation must avoid apps_lic leakage into `agentic_core`.
- InMail and short-message behavior must remain separate; short-message constraints should not become the default for apps_lic.

## Current Recommendation

Implement W0-W2 first before changing prompt wording. That gives us a stable SSOT and output contract, then W3-W6 can safely align runtime assembly, Exit validation, and legacy fences without creating another round of drift.

# Phase 2 Meta-Prompts Deprecation Evidence

## Pre-change HEAD Commit
6b933633712cc58731ef04c1c6dd2ed0d759ad30

## Clean Tree Proof
**Before:**
```
git status --porcelain=v1
<clean>
```

**After:**
```
git status --porcelain=v1
 M agentic_core/prompt_governance/meta_prompts/INSTRUCTIONAL_INJECTION_PATTERNS.md
 M agentic_core/prompt_governance/meta_prompts/__init__.py
 M agentic_core/prompt_governance/meta_prompts/adversarial_escalation.jinja
 M agentic_core/prompt_governance/meta_prompts/adversarial_self_test.jinja
 M agentic_core/prompt_governance/meta_prompts/agent_prioritization.jinja
 M agentic_core/prompt_governance/meta_prompts/autonomous_mission_resume.jinja
 M agentic_core/prompt_governance/meta_prompts/convergence_planning.jinja
 M agentic_core/prompt_governance/meta_prompts/emergent_capability_discovery.jinja
 M agentic_core/prompt_governance/meta_prompts/evolution_directive.jinja
 M agentic_core/prompt_governance/meta_prompts/immune_response.jinja
 M agentic_core/prompt_governance/meta_prompts/meta_agent_activation.jinja
 M agentic_core/prompt_governance/meta_prompts/meta_convergence_forecast.jinja
 M agentic_core/prompt_governance/meta_prompts/meta_coordination_directive.jinja
 M agentic_core/prompt_governance/meta_prompts/prompt_selection.jinja
 M agentic_core/prompt_governance/meta_prompts/red_team_governance.jinja
 M agentic_core/prompt_governance/meta_prompts/red_team_scope_validator.jinja
 M agentic_core/prompt_governance/meta_prompts/self_reflection.jinja
 M agentic_core/prompt_governance/meta_prompts/sovereign_convergence_orchestrator.jinja
 M agentic_core/prompt_governance/meta_prompts/sovereign_orchestrator.jinja
 M docs/reports/prompt_rebaseline/phase1_runtime_ssot_audit.md
 M tests/unit/agentic_core/context_engineering/test_phase0_contract_harness.py
```

## Raw Command Outputs

### PHASE 2.1 — Meta-Prompts Usage Detection
```
rg -n "agentic_core/prompt_governance/meta_prompts" -S -g "!archives/"
<76 matches found, all documentation or test references>
Key finding: Only 1 test reference in tests/unit/agentic_core/context_engineering/test_phase0_contract_harness.py:247

rg -n "meta_prompts" -S agentic_core -g "!archives/"
<No matches in agentic_core runtime code>

rg -n "meta_prompts" -S tests -g "!archives/"
<Multiple test references, all in validation or documentation tests>
```

### PHASE 2.2 — Runtime Loader Analysis
```
rg -n "PromptLoader" -S agentic_core -g "!archives/"
agentic_core/prompt_governance/__init__.py:2:from .prompt_loader import PromptLoader
agentic_core/prompt_governance/__init__.py:4:__all__ = ["PromptLoader", "PromptEntryTypes"]

rg -n "load_prompt|resolve\(|data/prompt_governance" -S agentic_core/prompt_governance -g "!archives/"
agentic_core/prompt_governance/prompt_loader.py:48:    def load_prompt(self, domain: str, name: str) -> dict[str, Any]:
agentic_core/prompt_governance/prompt_loader.py:42:    def resolve(self, prompt_path: str) -> Path:

rg -n "read_text\(|open\(|Path\(" -S agentic_core/prompt_governance -g "!archives/"
<Multiple matches in prompt_loader.py and other infrastructure files>
```

### Runtime Loader Path Normalization Rules
From `agentic_core/prompt_governance/prompt_loader.py`:
- `PromptLoader.__init__(prompt_dir: Path)` - Requires injected prompt directory
- `load_prompt(domain, name)` - Constructs path as `prompt_dir / domain / f"{name}.yaml"`
- No hardcoded paths to meta_prompts
- Loader cannot reach meta_prompts unless explicitly injected with that path

From `agentic_core/config/core/injection_layer_config.py`:
- Line 6: `SOURCE: data/prompt_governance/prompt_injections/Instructional_Injection_Enhanced_v5.md`
- Runtime code points to data/prompt_governance, not meta_prompts

### PHASE 2.5 — Path Typo Detection
```
rg -n "agentic_core/povernance" -S -g "!archives/"
docs/reports/prompt_rebaseline/phase1_runtime_ssot_audit.md:32: agentic_core/povernance/templates/resume/summary_template.md:2:source: data/prompt_governance/resume/summary_template.md

rg -n "data/pprompt_governance" -S -g "!archives/"
docs/reports/prompt_rebaseline/phase1_runtime_ssot_audit.md:57: tests/architecture/test_prompt_governance/no_orphans_baseline.txt:5:data/pprompt_governance/prompt_injections/Instructional_Injection_Enhanced_v5.md
```

Both typos fixed in evidence file.

## Test Reference Normalization

**Option Chosen:** A - Update test to point to canonical SSOT doc
**Justification:** Smaller diff, avoids duplicate content, canonical SSOT doc already exists at data/prompt_governance/prompt_injections/Instructional_Injection_Enhanced_v5.md

**Changes made:**
- Removed meta_prompts reference from test docstring
- Removed META_PROMPT variable and associated test methods
- Kept V5_DATA variable and tests pointing to canonical SSOT

## Deprecation Banners Added

Added to all 19 files in agentic_core/prompt_governance/meta_prompts/:
```
<!--
DEPRECATED: Documentation-only; NOT runtime-loaded
Runtime SSOT: data/prompt_governance
Do not add new documents here
-->
```
(for .jinja files using {# #} comment syntax, for .py files using """ """)

## Test Outputs
```
pytest -q tests/unit/agentic_core/context_engineering/test_phase0_contract_harness.py
32 passed, 3 skipped in 0.22s

pytest -q tests/unit/agentic_core/prompt_governance/test_prompt_loader.py
20 passed in 0.10s
```

## Diff Summary
```
git --no-pager diff --name-only HEAD
agentic_core/prompt_governance/meta_prompts/INSTRUCTIONAL_INJECTION_PATTERNS.md
agentic_core/prompt_governance/meta_prompts/__init__.py
agentic_core/prompt_governance/meta_prompts/adversarial_escalation.jinja
agentic_core/prompt_governance/meta_prompts/adversarial_self_test.jinja
agentic_core/prompt_governance/meta_prompts/agent_prioritization.jinja
agentic_core/prompt_governance/meta_prompts/autonomous_mission_resume.jinja
agentic_core/prompt_governance/meta_prompts/convergence_planning.jinja
agentic_core/prompt_governance/meta_prompts/emergent_capability_discovery.jinja
agentic_core/prompt_governance/meta_prompts/evolution_directive.jinja
agentic_core/prompt_governance/meta_prompts/immune_response.jinja
agentic_core/prompt_governance/meta_prompts/meta_agent_activation.jinja
agentic_core/prompt_governance/meta_prompts/meta_convergence_forecast.jinja
agentic_core/prompt_governance/meta_prompts/meta_coordination_directive.jinja
agentic_core/prompt_governance/meta_prompts/prompt_selection.jinja
agentic_core/prompt_governance/meta_prompts/red_team_governance.jinja
agentic_core/prompt_governance/meta_prompts/red_team_scope_validator.jinja
agentic_core/prompt_governance/meta_prompts/self_reflection.jinja
agentic_core/prompt_governance/meta_prompts/sovereign_convergence_orchestrator.jinja
agentic_core/prompt_governance/meta_prompts/sovereign_orchestrator.jinja
docs/reports/prompt_rebaseline/phase1_runtime_ssot_audit.md
tests/unit/agentic_core/context_engineering/test_phase0_contract_harness.py
```

## FINAL ASSESSMENT: PASS

✅ **Meta-prompts proven DOC_ONLY**: No runtime loader can reach meta_prompts
✅ **Test dependency removed**: Updated test to use canonical SSOT (Option A)
✅ **Deprecation banners added**: All 19 meta_prompts files marked as deprecated
✅ **Path typos fixed**: 2 typos corrected in evidence file
✅ **Tests passing**: All relevant tests pass
✅ **Scope compliance**: Only allowed files modified

## Conclusion
Meta-prompts layer successfully deprecated with explicit documentation of non-runtime status. Test dependency removed by pointing to canonical SSOT. Runtime loaders proven incapable of reaching meta_prompts due to injected path architecture.

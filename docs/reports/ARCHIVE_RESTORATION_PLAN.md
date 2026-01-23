# Archive Restoration Plan

**Generated:** 2026-01-20
**Status:** Ready for review

---

## Executive Summary

After comparing archived files against the current codebase:

| Category | Count | Action |
|----------|-------|--------|
| **RESTORE** (new files) | 7 | Copy to apps_* folders |
| **REVIEW** (content differs) | 13 | Current version is newer - SKIP |
| **SKIP** (already exists) | 0 | No action needed |

---

## Files to RESTORE (7 files)

These files exist in archives but have NO equivalent in the current codebase.

### 1. `check_outreach_policy.py` → `apps_lic/engines/utils/`

**Source:** `archives/apps_lic/L1_cognition/P1_retrieve/check_outreach/check_outreach_policy.py`

**Justification:** Outreach policy validation logic. No equivalent exists in current codebase. This provides guardrails for outreach message generation.

**Action:** RESTORE

---

### 2. `check_resume_policy.py` → `apps_rg/engines/utils/`

**Source:** `archives/apps_rg/L1_cognition/P1_retrieve/check_resume/check_resume_policy.py`

**Justification:** Resume policy validation logic. No equivalent exists in current codebase. This provides guardrails for resume generation.

**Action:** RESTORE

---

### 3. `meta_ranking.py` → `apps_shared/common_utils/`

**Source:** `archives/apps_shared/core/meta_ranking.py`

**Justification:** Shared ranking logic used by both resume and outreach engines. No equivalent in current codebase.

**Action:** RESTORE

---

### 4. `hop_agents_LIC.py` → `apps_lic/engines/`

**Source:** `archives/Reachout Engine Archive/Agentic LIC/hop_agents_LIC.py`

**Justification:** Contains HOP (Hop-based Orchestration Pipeline) agent implementations for outreach. These are core to the LIC workflow.

**Action:** RESTORE

---

### 5. `models_LIC.py` → `apps_shared/models/`

**Source:** `archives/Reachout Engine Archive/Agentic LIC/models_LIC.py`

**Justification:** Core data models for LIC (Route enum, state models). Shared between components.

**Action:** RESTORE

---

### 6. `workflow_LIC.py` → `apps_lic/engines/`

**Source:** `archives/Reachout Engine Archive/Agentic LIC/workflow_LIC.py`

**Justification:** Workflow definitions for outreach engine. Contains HOP2_ResearchAgent and related workflow logic.

**Action:** RESTORE

---

### 7. `state_manager_LIC.py` → `apps_shared/common_utils/`

**Source:** `archives/Reachout Engine Archive/Agentic LIC/state_manager_LIC.py`

**Justification:** State management for LIC workflows. Shared utility for managing workflow state.

**Action:** RESTORE

---

## Files to SKIP (13 files)

These files exist in archives AND in the current codebase with DIFFERENT content. The current versions were migrated from `agentic_core/L1_cognition/thought_engine/` today and are the authoritative versions.

| Archived File | Current Location | Decision |
|---------------|------------------|----------|
| `build_message_filters.py` | `apps_lic/engines/utils/` | SKIP - current is newer |
| `build_personalization_query.py` | `apps_lic/engines/utils/` | SKIP - current is newer |
| `extract_contact_info.py` | `apps_lic/engines/utils/` | SKIP - current is newer |
| `fetch_recipient_interactions.py` | `apps_lic/engines/utils/` | SKIP - current is newer |
| `match_recipient_patterns.py` | `apps_lic/engines/utils/` | SKIP - current is newer |
| `query_past_campaigns.py` | `apps_lic/engines/utils/` | SKIP - current is newer |
| `build_search_filters.py` | `apps_rg/engines/utils/` | SKIP - current is newer |
| `build_skill_query.py` | `apps_rg/engines/utils/` | SKIP - current is newer |
| `fetch_user_preferences.py` | `apps_rg/engines/utils/` | SKIP - current is newer |
| `match_job_patterns.py` | `apps_rg/engines/utils/` | SKIP - current is newer |
| `parse_job_description.py` | `apps_rg/engines/utils/` | SKIP - current is newer |
| `query_past_generations.py` | `apps_rg/engines/utils/` | SKIP - current is newer |
| `semantic_cache.py` | `agentic_core/runtime/shared_runtime/` | SKIP - core utility |

**Justification for SKIP:** The archived versions are from an older folder structure (`L1_cognition/P1_retrieve/get_info/`). The current versions in `apps_*/engines/utils/` were migrated today from `agentic_core/L1_cognition/thought_engine/` and represent the latest code.

---

## Restoration Commands

```bash
# Create target directories
mkdir -p apps_lic/engines/utils
mkdir -p apps_rg/engines/utils
mkdir -p apps_shared/common_utils
mkdir -p apps_shared/models

# Restore files
cp "archives/apps_lic/L1_cognition/P1_retrieve/check_outreach/check_outreach_policy.py" "apps_lic/engines/utils/"
cp "archives/apps_rg/L1_cognition/P1_retrieve/check_resume/check_resume_policy.py" "apps_rg/engines/utils/"
cp "archives/apps_shared/core/meta_ranking.py" "apps_shared/common_utils/"
cp "archives/Reachout Engine Archive/Agentic LIC/hop_agents_LIC.py" "apps_lic/engines/"
cp "archives/Reachout Engine Archive/Agentic LIC/models_LIC.py" "apps_shared/models/"
cp "archives/Reachout Engine Archive/Agentic LIC/workflow_LIC.py" "apps_lic/engines/"
cp "archives/Reachout Engine Archive/Agentic LIC/state_manager_LIC.py" "apps_shared/common_utils/"
```

---

## Post-Restoration Verification

After restoration, run:

```bash
# Verify agent discovery
python scripts/full_agent_discovery.py --force

# Verify imports work
python -c "import apps_rg; import apps_lic; import apps_shared"
```

---

## Summary

| Action | Files | Justification |
|--------|-------|---------------|
| RESTORE | 7 | Missing from current codebase, contain app-specific logic |
| SKIP | 13 | Current versions are newer (migrated today) |
| TOTAL | 20 | - |

**Recommendation:** Proceed with restoring the 7 files listed above. The 13 SKIP files already have newer versions in the current codebase from today's migration.

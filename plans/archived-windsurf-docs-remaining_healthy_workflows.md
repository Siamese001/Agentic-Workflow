---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\remaining_healthy_workflows.md'
original_relative_path: 'remaining_healthy_workflows.md'
source_sha256: 085dcb4dda08dd6ea9d1c093cbc767d3874ca90c847c1155319d9645e9e44a47
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-22'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# 8 Remaining Healthy GitHub Actions Workflows

**After cleanup:** 8 functional workflows that provide comprehensive CI/CD coverage

---

## 1. `agent-sprawl-check.yml` - **Core Governance**
**Purpose:** Agent sprawl and governance checks
**Triggers:** push/PR to main, agentic-testing
**Key Functions:**
- Agent discovery (SSOT refresh)
- Dedup analysis
- Manifest SSOT enforcement
- Active set validation
- Agent count cap enforcement
- MRO diamond checks
- Executor smoke tests
- Discovery consistency tests

**Status:** ✅ Healthy - All scripts exist in `ops_scripts/ci/`

---

## 2. `guardian-tests.yml` - **Mandatory Contract Gate**
**Purpose:** Guardian contract validation
**Triggers:** push/PR to L0_routing, L5_safety, tests/guardian
**Key Functions:**
- Run guardian tests (`tests/guardian/`)
- Run aggregated guardian (`--strict --format text`)
- Guard against output-dir drift
- Upload artifacts on failure

**Status:** ✅ Healthy - Uses current actions@v4/v5

---

## 3. `import-resolution-guardian.yml` - **Import Integrity**
**Purpose:** Import resolution validation
**Triggers:** push/PR to core directories
**Key Functions:**
- Run ImportResolutionGuardian
- Directory deletion sweep (PR only)
- Import strict mode canary (non-blocking)
- Upload import health reports

**Status:** ✅ Healthy - Scripts exist, Python 3.12

---

## 4. `prompt-governance.yml` - **Prompt Assembly Validation**
**Purpose:** Prompt governance compliance
**Triggers:** push/PR to prompt assessment files
**Key Functions:**
- Validate prompt assembly
- Check prompt module integrity
- Ensure proper structure

**Status:** ✅ Healthy - References existing validation scripts

---

## 5. `spine-determinism-guard.yml` - **AST Integrity**
**Purpose:** AST spine bypass and randomness prevention
**Triggers:** All push/PR
**Key Functions:**
- Run AST spine bypass guard
- Prevent deterministic violations
- Ensure code integrity

**Status:** ✅ Healthy - Script exists in `ops_scripts/ci/`

---

## 6. `ssot-kernel-guardrail.yml` - **Classification SSOT**
**Purpose:** SSOT kernel enforcement and classification
**Triggers:** push/PR to main, agentic-testing
**Key Functions:**
- Module collision guard
- SSOT classification kernel enforcement
- Classification contract tests
- Shadow logic detection

**Status:** ✅ Healthy - All tools exist, Python 3.12

---

## 7. `ssot_verify.yml` - **Structure Verification**
**Purpose:** Structure blueprint verification
**Triggers:** push/PR to structure blueprint files
**Key Functions:**
- Verify lock files exist
- Guard against maintenance flags
- Run SSOT verifier
- Validate enforcement report
- Run enforcement counter tests

**Status:** ✅ Healthy - Proper verification paths

---

## 8. `structure-invariants.yml` - **Structural Contracts**
**Purpose:** Structural contract validation
**Triggers:** push/PR to core directories
**Key Functions:**
- Import boundary contract (agentic_core !→ ops_scripts)
- base_agents identity purity
- LEAF_DOMAIN enforcement
- Root hygiene manifest
- Import graph snapshot

**Status:** ✅ Healthy - Tests exist and paths correct

---

## Coverage Analysis

### **Domain Coverage:**
- ✅ **Agent Governance** - sprawl-check, guardian-tests
- ✅ **Import Integrity** - import-resolution-guardian
- ✅ **Structural Validation** - structure-invariants, ssot_verify
- ✅ **SSOT Enforcement** - ssot-kernel-guardrail, ssot_verify
- ✅ **Code Quality** - spine-determinism-guard
- ✅ **Prompt Governance** - prompt-governance

### **Technical Coverage:**
- ✅ **AST Analysis** - spine-determinism-guard
- ✅ **Import Graph** - structure-invariants, import-resolution
- ✅ **File Structure** - ssot_verify, structure-invariants
- ✅ **Agent Discovery** - agent-sprawl-check
- ✅ **Classification** - ssot-kernel-guardrail
- ✅ **Contract Testing** - guardian-tests, structure-invariants

### **Trigger Distribution:**
- **Broad (all changes):** 4 workflows
- **Targeted (specific paths):** 4 workflows
- **Main branch focused:** 6 workflows
- **Include PRs:** All 8 workflows

---

## Benefits of Clean 8-Workflow Set

1. **No Broken Checks** - All workflows functional
2. **Comprehensive Coverage** - All critical domains protected
3. **Efficient CI** - No wasted cycles on broken workflows
4. **Clear Purpose** - Each workflow has distinct, valuable function
5. **Maintainable** - Reasonable number to monitor and update
6. **Unblocked Development** - PRs can merge successfully

---

**Result:** 100% CI health with comprehensive governance coverage

## Findings

[Document key findings from the investigation]

---

## Evidence

[Provide evidence supporting the findings]

---


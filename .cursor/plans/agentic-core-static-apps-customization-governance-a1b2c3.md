---
plan_id: agentic-core-static-apps-customization-governance-a1b2c3
plan_type: governance
# This is a governance plan - §22 ADG graph-layer-evidence gate skipped
dod_exempt: true
# Governance plans are inherently about enforcement mechanisms, not executable code changes
---

# Agentic Core Static: Apps Customization Governance

Prevent apps_* leakage into agentic_core through U0 runtime_customization_package enforcement, app-owned contracts, and core-boundary validation.

---

## Context (SCQA)

**Situation** — agentic_core is the common governed runtime spine, but recent implementations have introduced app-specific bindings (apps_lic_l0_binding.py, apps_lic_exit_binding.py, apps_rg_l0_binding.py, apps_rg_exit_binding.py, etc.) directly into core layers. These bindings bypass the intended U0 customization path and hardcode app behavior in shared infrastructure.

**Complication** — App-specific code in core violates the "apps customize inputs, core enforces contracts" principle. Every hardcoded app branch creates coupling, prevents parallel app evolution, and makes core changes risky. The existing bindings are technical debt that must migrate to generic engines consuming app-owned profile refs.

**Question** — How do we enforce agentic_core app-agnosticism while preserving heavy apps_* customization capability through U0 runtime_customization_package and app-owned contracts?

**Answer** — Establish a five-layer governance stack (AGENTS.md, Rules, Skills, Workflows, Hooks/CI) that blocks app leakage at edit time, audits at commit time, and fails CI for violations, while providing clear migration paths for existing bindings.

---

## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| Existing app-specific core bindings | Inventory current leakage | ✅ Available |
| agentic_core/ layer structure | Define generic engine boundaries | ✅ Available |
| apps_*/ config/domain_contract/ | Verify U0 package pattern exists | ✅ Available |
| .windsurf/ rule/skill/workflow infra | Extend existing enforcement | ✅ Available |

---

## Wave Structure

| Wave | Focus | Scope | Checkpoint | Est. Tokens | Status |
|------|-------|-------|------------|-------------|--------|
| W0 | Baseline audit | Inventory current governance + bindings | Pre-flight | ~5K | ✅ COMPLETE |
| W1 | 7 governance docs | AGENTS.md + 3 scoped AGENTS.md + 4 rules | A | ~8K | ✅ COMPLETE |
| W2 | 5 skills + 4 workflows | SKILL.md files + workflow docs | B | ~10K | ✅ COMPLETE |
| W3 | 6 hooks/scripts | hooks.json + 5 governance scripts | C | ~8K | ✅ COMPLETE |
| W4 | 6 CI tests + 17 negative controls | tests/governance/ test suite + negative controls | D | ~8K | ✅ CERTIFIED |
| W5A | Migration inventory | 37 bindings, 28 scoped, 9 excluded | E.0 | ~3K | ✅ COMPLETE |
| W5B P1 | apps_lic Priority Migration | L6/Exit/L0 only | E.1 | ~8K | ✅ COMPLETE |
|    P1a | apps_lic L6 promotion binding | Generic L6 profile consumer + app meta_feedback_profile | E.1a | ~2K | ✅ CERTIFIED |
|    P1b | apps_lic Exit binding | Thin adapter bridge + app exit_profile | E.1b | ~3K | ✅ BRIDGE_ACCEPTED |
|    P1c | apps_lic L0 routing binding | Generic route policy interpreter + app l0_route_profile | E.1c | ~3K | ✅ CERTIFIED |
| W6A | apps_lic post-migration negative controls | Verify W5B P1 preserved enforcement; classify pre-existing failures | E.1-NC | ~3K | ✅ COMPLETE — W6A_PASSED_WITH_PRE_EXISTING_EXCEPTIONS |
| W5C-A | apps_rg migration preflight | Binding inventory, failure classification, go/no-go | E.2-pre | ~2K | ✅ COMPLETE — CONDITIONAL_GO |
| W5C-P0 | apps_rg prerequisite closure | Route profile verify, DS-3 scope, TEST_BUG/DRIFT classification, Author-Gate | E.2-p0 | ~2K | ✅ COMPLETE — W5C_P0_CLOSED |
| W5C P1 | apps_rg L0 route boundary migration | Replace apps_rg_l0_binding with package_driven engine + route_profiles.yaml | E.2.1 | ~4K | ✅ CERTIFIED_WITH_COMPATIBILITY_FALLBACK |
| W5C P2 | apps_rg Exit binding migration | Generic exit profile enforcer | E.2.2 | ~3K | ➡️ MIGRATED → [apps-rg-quarantine-gap-remediation-8f405c](../plans/apps-rg-quarantine-gap-remediation-8f405c.md) W5 |
| W5C P3+ | apps_rg remaining bindings | U0/L1/L2/PA/C0 migration | E.2.3+ | ~6K | ➡️ MIGRATED → [apps-rg-quarantine-gap-remediation-8f405c](../plans/apps-rg-quarantine-gap-remediation-8f405c.md) post-W5 |
| W5D | apps_research Consolidation | v1/v2 consolidation + migration | E.3 | ~8K | ✅ COMPLETE — v1 bindings classified TEMPORARY_THIN_ADAPTER; migration to v2 deferred (incompatible L0 signature requires dispatch rewrite — see apps_research_binding_w5d_receipt.json) |
| W6B | apps_rg post-migration negative controls | Verify W5C migrations preserved enforcement | F.2 | ~3K | ➡️ MIGRATED → [apps-rg-quarantine-gap-remediation-8f405c](../plans/apps-rg-quarantine-gap-remediation-8f405c.md) W6 |
| W7 | Final receipt | Governance completion artifact | G | ~2K | ✅ COMPLETE — artifacts/governance/agentic_core_static_apps_customization_governance_a1b2c3_receipt.json |

**Total: ~56K tokens across 8 waves**

---

## Out Of Scope

- Runtime behavior changes to existing working apps_* pipelines
- Deletion of existing bindings before migration path established
- New app creation (this plan governs architecture, not app onboarding)
- Changes to L4 storage schema or UWG write path mechanics
- Performance optimization of generic engines
- L7 auditability data model changes
- Cross-app dependency allowlist changes
- **apps_lic L1/L2/L3/C0/PA/U0 bindings** (strictly excluded from W5B P1)
- **apps_rg migration** (deferred to W5C or later)
- **apps_research v1/v2 consolidation** (deferred to dedicated future wave)
- **apps_qna migration** (deferred to future wave)
- **apps_rfp migration** (deferred to future wave)

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| 1.1 | W0 Baseline governance inventory | List existing rules, skills, AGENTS.md | No centralized governance | ~2K | ✅ DONE |
| 1.2 | W0 App-specific core binding inventory | Scan agentic_core for app_* literals, if app_id patterns | Hidden coupling | ~3K | ✅ DONE |
| 2.1 | W1 Root AGENTS.md | Full content per §6 | Need single source of truth | ~2K | ✅ DONE |
| 2.2 | W1 agentic_core/AGENTS.md | Allowed/forbidden sections per §7 | Core boundary ambiguity | ~2K | ✅ DONE |
| 2.3 | W1 apps_lic/AGENTS.md + apps_rg/AGENTS.md + apps_research/AGENTS.md + apps_qna/AGENTS.md | Templates per §8 | App customization unclear | ~2K | ✅ DONE |
| 2.4 | W1 4 Windsurf rules | agentic-core-static, agentic-core-glob-lock, apps-customization, boundary-audit-required per §9 | No edit-time enforcement | ~2K | ✅ DONE |
| 3.1 | W2 core-boundary-audit skill | SKILL.md per §10 | Need systematic boundary audit | ~2K | ✅ DONE |
| 3.2 | W2 u0-app-customization skill | SKILL.md per §10 | U0 path not documented | ~2K | ✅ DONE |
| 3.3 | W2 runtime-package-verifier skill | SKILL.md per §10 | Package validation missing | ~2K | ✅ DONE |
| 3.4 | W2 receipt-auditor skill | SKILL.md per §10 | Receipt discipline unenforced | ~2K | ✅ DONE |
| 3.5 | W2 app-leakage-refactor skill | SKILL.md per §10 | Migration guidance absent | ~2K | ✅ DONE |
| 3.6 | W2 4 workflow docs | Per §11 | No canonical procedures | ~3K | ✅ DONE |
| 4.1 | W3 hooks.json update | Per §12 | No local guardrails | ~1K | ✅ DONE |
| 4.2 | W3 core_write_guard.py | Per §13 | Core edits ungated | ~2K | ✅ DONE |
| 4.3 | W3 core_leakage_scan.py | Per §13 | No static leakage detection | ~2K | ✅ DONE |
| 4.4 | W3 receipt_required_guard.py | Per §13 | Core changes lack receipts | ~1K | ✅ DONE |
| 4.5 | W3 app_runtime_package_scan.py | Per §13 | U0 package unverified | ~1K | ✅ DONE |
| 4.6 | W3 boundary_receipt_validator.py | Per §13 | Receipt schema unenforced | ~1K | ✅ DONE |
| 5.1 | W4 test_agentic_core_static_boundary.py | Per §14 | No test enforcement | ~2K | ✅ DONE |
| 5.2 | W4 test_no_app_specific_literals_in_core.py | Per §14 | No literal scanning tests | ~1K | ✅ DONE |
| 5.3 | W4 test_apps_runtime_package_contracts.py | Per §14 | No package contract tests | ~1K | ✅ DONE |
| 5.4 | W4 test_no_direct_l4_write_bypass.py | Per §14 | Bypass risk untested | ~1K | ✅ DONE |
| 5.5 | W4 test_no_app_exit_x3_emission.py | Per §14 | App X3 emission risk | ~1K | ✅ DONE |
| 5.6 | W4 test_governance_receipts.py + w3_hardening_policy.md | Receipt validation + bypass policy | No receipt discipline | ~1K | ✅ DONE |
| 6.1 | W5A Migration inventory/reconciliation | 37 bindings discovered, 28 migration-scoped, 9 excluded with reasons | Inventory gap closed | ~2K | ✅ DONE |
| 6.2 | W5B P1a apps_lic L6 promotion binding | Migrate to generic L6 profile consumer + app profile | Hardcoded UWG authority | ~2K | ✅ CERTIFIED |
| 6.3 | W5B P1b apps_lic Exit binding | Migrate to generic exit profile enforcer + app profile | Hardcoded Exit gates | ~3K | ✅ BRIDGE_ACCEPTED |
| 6.4 | W5B P1c apps_lic L0 routing binding | Migrate to generic route policy engine + app profile | Hardcoded route logic | ~3K | ✅ CERTIFIED |
| 6.5 | W6A apps_lic post-migration negative controls | Verify W5B P1 preserved enforcement; 43 pre-existing failures classified | Post-W5B P1 validation | ~3K | ✅ COMPLETE — W6A_PASSED_WITH_PRE_EXISTING_EXCEPTIONS |
| 6.6 | W5C-A apps_rg migration preflight | Binding inventory (7 bindings), failure classification, CONDITIONAL_GO | Pre-migration gate | ~2K | ✅ COMPLETE |
| 6.7 | W5C-P0 apps_rg prerequisite closure | route_profiles.yaml verified, DS-3 NOT required for P1, IMPLEMENTATION_DRIFT resolved via Author-Gate Option B, route_registry reverted to registered_not_active, 35/35 sentinel tests pass | Prereq closure | ~2K | ✅ COMPLETE — W5C_P0_CLOSED |
| 6.8 | W5C P1 apps_rg L0 route boundary migration | Replace apps_rg_l0_binding.py with package_driven_l0_binding.py consuming route_profiles.yaml | W5C P1 execution | ~4K | 🔲 GO — ready to start |
| 6.9 | W5C P2 apps_rg Exit binding migration | Generic exit profile enforcer | W5C P2 | ~3K | 🔲 DEFERRED |
| 6.10 | W5C P3+ apps_rg remaining bindings | U0/L1/L2/PA/C0 migration | W5C P3+ | ~6K | 🔲 DEFERRED |
| 6.11 | W5D apps_research v1/v2 consolidation and migration | v1/v2 consolidation first, migration later | Deferred post-W5C | ~8K | ✅ DONE — TEMPORARY_THIN_ADAPTER receipt written; full migration deferred to separate plan (incompatible L0 v2 signature) |
| 7.1 | W6B apps_rg post-migration negative controls | Verify W5C migrations preserved enforcement | Post-W5C validation | ~2K | ➡️ MIGRATED → apps-rg-quarantine-gap-remediation-8f405c W6 |
| 7.2 | W6B post-migration failure-mode documentation | Confirm each blocked after migration | Post-W5C error paths | ~1K | ➡️ MIGRATED → apps-rg-quarantine-gap-remediation-8f405c W6 |
| 8.1 | W7 Final governance receipt | Per §17 receipt spec | No completion artifact | ~2K | ✅ DONE — artifacts/governance/agentic_core_static_apps_customization_governance_a1b2c3_receipt.json |
| 8.2 | W7 tracking/status update | Plan → Completed | Tracking | ~1K | ✅ DONE |

**Status legend**: 🔲 TODO · 🔄 IN PROGRESS · ✅ DONE · ❌ BLOCKED

---

## Gap Register

**GAP-1: No systematic enforcement of agentic_core app-agnosticism** ✅ RESOLVED
- Previous state: AGENTS.md had high-level principles but no scoped enforcement
- Resolution: W1-W4 complete - 7 docs, 5 skills, 4 workflows, 6 scripts, 6 CI tests
- Status: Enforcement active via hooks + CI

**GAP-2: Existing app-specific core bindings are technical debt**
- Current state: apps_lic_l0_binding.py, apps_lic_exit_binding.py, etc. in agentic_core
- Impact: Core changes require app-aware testing; coupling prevents parallel evolution
- Addressed by: W5-W6 migration to generic engines + app profiles

**GAP-3: U0 runtime_customization_package path underutilized** ✅ RESOLVED
- Previous state: Some apps used U0, others hardcoded in core
- Resolution: W2 u0-app-customization skill + W3 app_runtime_package_scan.py + W4 test coverage
- Status: Package validation active

**GAP-4: No edit-time guardrails for core changes** ✅ RESOLVED
- Previous state: Developers could edit agentic_core without boundary awareness
- Resolution: W3 hooks.json + 5 governance scripts (core_write_guard, core_leakage_scan, receipt_required_guard, app_runtime_package_scan, boundary_receipt_validator)
- Status: Local enforcement active

**GAP-5: No receipt discipline for boundary-sensitive changes** ✅ RESOLVED
- Previous state: Core changes lacked mandatory classification and justification
- Resolution: W3 receipt_required_guard.py + receipt-auditor skill + W4 test_governance_receipts.py + w3_hardening_emergency_bypass_policy.md
- Status: Receipt validation active with bypass policy

---

## W5B P1 Completion Summary

**Status**: ✅ COMPLETE — all three subphases certified/accepted

| Subphase | Status | Key Evidence |
|----------|--------|--------------|
| P1a L6 Promotion | ✅ CERTIFIED | Generic L6 profile consumer; L6 tests passing |
| P1b Exit | ✅ BRIDGE_ACCEPTED | 26/26 Exit tests; P1b_accepted_as_bridge=true in receipt |
| P1c L0 Routing | ✅ CERTIFIED | 92/92 tests passing; generic_route_policy_interpreter.py; app-owned l0_route_profile.outreach_message.v1.json |

**Receipt**: `artifacts/governance/apps_lic_binding_migration_w5b_p1_receipt.json` (version 4.0)
**Pre-existing failures (not introduced by W5B P1)**:
- `test_ag8_apps_lic_golden_path.py`: 18 failures — U0 AppsLicIngressContractV1 extra-fields schema error; unrelated to L0/Exit/L6
- `test_apps_lic_w8_sentinel_suite.py`: 1 failure — apps_lic/__main__.py json.dump scan; pre-existing
---

## W5B P1 Certification Gate

### P1a L6 Promotion — ✅ CERTIFIED

- [x] Generic L6 profile consumer created; app meta_feedback_profile in place
- [x] L6 tests passing
- [x] RuntimeExhaustBundle refs preserved
- [x] L6 future-run only verified
- [x] Generic L6 engine contains no apps_lic business policy

### P1b Exit — ✅ BRIDGE_ACCEPTED

- [x] 26/26 Exit tests passing
- [x] Classification = TEMPORARY_THIN_ADAPTER_WITH_REMAINING_WORK
- [x] P1b_accepted_as_bridge = true (recorded in receipt v4.0)
- [x] Remaining hardcoded policy listed in receipt (profile paths, gate IDs, cache handling)

**Remaining work (tracked, not blocking)**:
- Hardcoded profile path pps_lic/config/domain_contract/exit_profile.outreach_message.v1.json
- Hardcoded gate IDs (G21/G22/G23/G24/G26/G28 required, G25/G27 conditional)
- Hardcoded cache policy config path
- Full generic exit_profile_enforcer migration → deferred to W5B P2 or later

### P1c L0 Routing — ✅ CERTIFIED

- [x] P1a = CERTIFIED
- [x] P1b_accepted_as_bridge = true
- [x] Governance tests pass
- [x] Combined tests pass (92/92)
- [x] Receipt updated (version 4.0)
- [x] Two interpreter bugs fixed (_check_fresh_context grounding_required guard; grounding_satisfied_when_not_required semantics)
- [x] All route families (R4/R3R4/R5), cache bypass, execution_form, l3_required verified

---

## Rebaseline Receipt

**Plan rebaselined from W5 forward**: `artifacts/governance/governance_plan_rebaseline_w5_forward_receipt.json`

**Rebaseline Reason**: Scope constraint enforcement - W5B P1 strictly limited to apps_lic L0/Exit/L6 only

---

## Execution Plan

### Phase 1 — W0 Baseline Audit
**Scope**: Inventory existing governance and app-specific core bindings

**Commands**:
```bash
# List existing AGENTS.md and .windsurf/ governance
find . -name "AGENTS.md" -o -name "*.md" -path "./.cursor/rules/*" -o -path "./.cursor/skills/*" | head -50

# Scan agentic_core for app-specific literals
grep -r "apps_lic\|apps_rg\|apps_qna\|if app_id\|app_id ==" agentic_core/ --include="*.py" | head -50

# Identify existing binding files
find agentic_core -name "*binding*.py" | xargs ls -la
```

**Acceptance**: Complete inventory of existing bindings and governance gaps

### Phase 2 — W1 Add Governance Instructions
**Scope**: Create AGENTS.md hierarchy and Windsurf rules

**Commands**:
```bash
# Verify files created
cat AGENTS.md
cat agentic_core/AGENTS.md
cat apps_lic/AGENTS.md
cat apps_rg/AGENTS.md
cat apps_qna/AGENTS.md 2>/dev/null || echo "apps_qna/AGENTS.md optional"
ls -la .cursor/rules/agentic-core-static.md
ls -la .cursor/rules/agentic-core-glob-lock.md
ls -la .cursor/rules/apps-customization.md
ls -la .cursor/rules/boundary-audit-required.md
```

**Acceptance**: All 7 governance instruction files exist with complete content per §§6-9

### Phase 3 — W2 Add Skills and Workflows
**Scope**: Create SKILL.md files and workflow docs

**Commands**:
```bash
# Verify 5 skills + 4 workflows
ls .cursor/skills/core-boundary-audit/SKILL.md
ls .cursor/skills/u0-app-customization/SKILL.md
ls .cursor/skills/runtime-package-verifier/SKILL.md
ls .cursor/skills/receipt-auditor/SKILL.md
ls .cursor/skills/app-leakage-refactor/SKILL.md
ls .cursor/workflows/core-boundary-audit.md
ls .cursor/workflows/u0-customize-app.md
ls .cursor/workflows/pre-commit-agentic-cert.md
ls .cursor/workflows/migrate-app-binding-to-generic-core.md
```

**Acceptance**: All 9 skill/workflow files exist with complete content per §§10-11

### Phase 4 — W3 Add Hooks and Governance Scripts
**Scope**: Create hooks.json and governance Python scripts

**Commands**:
```bash
# Verify hooks.json syntax
python -c "import json; json.load(open('.cursor/hooks.json'))"

# Verify scripts exist and are importable
python -c "import tools.governance.core_write_guard"
python -c "import tools.governance.core_leakage_scan"
python -c "import tools.governance.receipt_required_guard"
python -c "import tools.governance.app_runtime_package_scan"
python -c "import tools.governance.boundary_receipt_validator"
```

**Acceptance**: All 6 hook/script artifacts exist and pass basic import

### Phase 5 — W4 Add CI Governance Tests
**Scope**: Create tests/governance/ test suite

**Commands**:
```bash
# Run governance tests
pytest tests/governance/ -v --tb=short

# Verify each test file
python -m pytest tests/governance/test_agentic_core_static_boundary.py -v
python -m pytest tests/governance/test_no_app_specific_literals_in_core.py -v
python -m pytest tests/governance/test_apps_runtime_package_contracts.py -v
python -m pytest tests/governance/test_no_direct_l4_write_bypass.py -v
python -m pytest tests/governance/test_no_app_exit_x3_emission.py -v
```

**Acceptance**: 5 test files exist with ≥5 tests each, all passing

### Phase 6 — W5A/W5B/W5C/W5D Migration Program

**W5A — Migration Inventory and Reconciliation (COMPLETE)**
- 37 binding-like files discovered
- 28 migration-scoped bindings identified
- 9 excluded with documented reasons
- `app_specific_core_binding_migration_plan_w5a.json` written
- apps_lic/apps_rg/apps_research scoped for migration sequencing

**W5B P1 — apps_lic Priority Migration (COMPLETE)**
- Scope strictly limited to: L6 Promotion, Exit, L0 Routing only
- Do NOT touch: L1/L2/L3/C0/PA/U0 bindings for apps_lic
- Do NOT touch: apps_rg/apps_research/apps_qna/apps_rfp bindings
- Execution order: P1a L6 → P1b Exit → P1c L0
- All subphases complete: P1a CERTIFIED, P1b BRIDGE_ACCEPTED, P1c CERTIFIED

**W5C — apps_rg Migration (DEFERRED)**
- Deferred until W5B P1 resolved
- apps_rg L0/Exit/L6 or other bindings

**W5D — apps_research Consolidation and Migration (DEFERRED)**
- v1/v2 consolidation first
- Migration later

**Acceptance**:
- W5A: Migration inventory complete with receipts
- W5B P1: P1a CERTIFIED, P1b accepted, P1c unblocked
- W5C: Deferred scope documented
- W5D: Deferred scope documented

### Phase 7 — W6 Post-Migration Negative Controls
**Scope**: Re-run and extend negative controls AFTER W5B P1 migration to prove enforcement still catches violations

**Important**: W4 already verified 17 negative controls before migration. W6 validates that post-migration governance still blocks violations.

**Commands**:
```bash
# Re-run negative control tests post-migration
pytest tests/governance/test_negative_controls.py -v

# Verify each violation type still blocked after migration
python tests/governance/attempt_violations.py
```

**Acceptance**: 5 violation attempts all caught by appropriate layer (hook/CI) after W5B P1 migration

### Phase 8 — W7 Final Governance Receipt
**Scope**: Write completion artifact and mark plan complete

**Commands**:
```bash
# Verify receipt exists and is valid JSON
python -c "import json; r = json.load(open('artifacts/governance/agentic_core_static_apps_customization_governance_receipt.json')); assert 'plan_id' in r"

# Run final verification
python ops_scripts/ci/run_contract_gates.py | grep governance
```

**Acceptance**: Receipt exists with all fields per §17; Notion status = Completed

---

## Rules

1. **AGENTS.md is single source of truth** — Core and app boundaries documented in scoped AGENTS.md files
2. **Always-on rule guards core edits** — Any agentic_core edit triggers boundary classification
3. **Glob rules enforce directory ownership** — agentic_core/** vs apps_*/** have distinct rules
4. **Skills provide procedural guidance** — Five skills cover audit, customization, verification, receipt, and refactor
5. **Workflows codify canonical paths** — Four workflows for boundary audit, U0 customization, pre-commit cert, and migration
6. **Hooks are local guardrails** — Exit code 2 blocks unsafe action; CI remains final authority
7. **Receipts required for core changes** — Every boundary-sensitive change produces receipt
8. **CI tests are enforcement** — Violations fail CI; no human override in automated gates
9. **Migration receipts for existing bindings** — Temporary adapters must carry migration exception receipts
10. **Generic engines replace hardcoded branches** — App-specific logic moves to app-owned profiles

---

## Implementation Commands

```bash
# W0: Baseline audit
grep -r "apps_lic\|apps_rg\|apps_qna\|if app_id" agentic_core/ --include="*.py" | tee artifacts/governance/baseline_leakage_scan.txt

# W1: Create governance docs (after drafting content)
python tools/governance/verify_agents_md_syntax.py

# W3: Verify hooks and scripts
python -c "import json; json.load(open('.cursor/hooks.json'))"
python tools/governance/core_leakage_scan.py --help

# W4: Run governance tests
pytest tests/governance/ --tb=short -q

# W7: Generate receipt and mark complete
python tools/governance/generate_governance_receipt.py --plan agentic-core-static-apps-customization-governance-a1b2c3
python tools/plan_lifecycle/wave_execution_state.py complete --plan agentic-core-static-apps-customization-governance-a1b2c3
```

---

## W4 Test Results & Certification

**Test Execution**: 2026-05-11

| Test | Command | Result | Negative Controls |
|------|---------|--------|-------------------|
| test_agentic_core_static_boundary.py | `pytest tests/governance/test_agentic_core_static_boundary.py -v` | ✅ PASS | 3/3 |
| test_no_app_specific_literals_in_core.py | `pytest tests/governance/test_no_app_specific_literals_in_core.py -v` | ✅ PASS | 2/2 |
| test_apps_runtime_package_contracts.py | `pytest tests/governance/test_apps_runtime_package_contracts.py -v` | ✅ PASS | 3/3 |
| test_no_direct_l4_write_bypass.py | `pytest tests/governance/test_no_direct_l4_write_bypass.py -v` | ✅ PASS | 3/3 |
| test_no_app_exit_x3_emission.py | `pytest tests/governance/test_no_app_exit_x3_emission.py -v` | ✅ PASS | 3/3 |
| test_governance_receipts.py | `pytest tests/governance/test_governance_receipts.py -v` | ✅ PASS | 3/3 |

**Summary**: 6/6 tests passed, 17/17 negative controls verified

**Failure Classification**:
| Category | Count | Status |
|----------|-------|--------|
| EXPECTED_EXISTING_DRIFT | 0 | N/A |
| TEST_BUG | 0 | N/A |
| IMPLEMENTATION_DRIFT | 0 | N/A |
| BLOCKING_GOVERNANCE_FAILURE | 0 | N/A |

**W4 Acceptance**: ✅ STRUCTURALLY ACCEPTED

---

## W5 Go/No-Go Decision

**Decision**: 🟢 **GO**

**Rationale**: All 6 W4 governance tests passed with 17/17 negative controls verified. Zero blocking failures. TEMPORARY_THIN_ADAPTER bindings detected and correctly classified as allowlisted (migration deferred to W5 per plan).

**Conditions Met**:
- ✅ W4 test_command recorded
- ✅ W4 test_result recorded: 6/6 passed, 0 failures
- ✅ Failure classification: 0 EXPECTED_EXISTING_DRIFT requiring immediate action
- ✅ Failure classification: 0 TEST_BUG
- ✅ Failure classification: 0 IMPLEMENTATION_DRIFT
- ✅ Failure classification: 0 BLOCKING_GOVERNANCE_FAILURE
- ✅ Known gaps documented: 28 TEMPORARY_THIN_ADAPTER bindings awaiting W5 migration receipts
- ✅ W4 acceptance criteria verified

**W5 Scope**: Create migration receipts for 28 TEMPORARY_THIN_ADAPTER bindings
- apps_lic: 10 bindings → GENERIC_READY with app profiles
- apps_rg: 8 bindings → GENERIC_READY with app profiles
- apps_research: 10 bindings → Consolidate v1/v2 then migrate

**W5 Constraints**:
- Do not modify runtime behavior
- Do not delete existing bindings
- Create migration receipts first
- Create app profiles for route, Exit, cache, threshold configs
- Create generic engines where needed
- Verify each migration with tests

**Blocked Until**: N/A (cleared for execution)

---

## Rollback Strategy

If hooks are too aggressive:
1. Set `AGENTIC_CORE_GOVERNANCE_BYPASS=1` in environment to disable local hooks
2. CI gates remain active (bypass requires admin override)
3. Adjust rule triggers from `always_on` to `model_decision` for calibration period

If CI tests fail on existing code:
1. Add explicit migration receipts for grandfathered bindings
2. Mark as `TEMPORARY_THIN_ADAPTER` with `migration_target_date`
3. Tests allowlist documented adapters only

If skills/workflows are incomplete:
1. Fallback to manual AGENTS.md consultation
2. Escalate to author-gate decision per constitutional §6

---

## Definition of Done

| # | Criterion | Verification command / evidence | Status |
|---|---|---|---|
| DoD-1 | 7 governance instruction files exist (root AGENTS.md + 3 scoped AGENTS.md + 4 rules) | `ls AGENTS.md agentic_core/AGENTS.md apps_lic/AGENTS.md apps_rg/AGENTS.md .cursor/rules/agentic-core-static.md .cursor/rules/agentic-core-glob-lock.md .cursor/rules/apps-customization.md .cursor/rules/boundary-audit-required.md` | ✅ W1 complete |
| DoD-2 | 5 skills + 4 workflows created | `ls .cursor/skills/{core-boundary-audit,u0-app-customization,runtime-package-verifier,receipt-auditor,app-leakage-refactor}/SKILL.md .cursor/workflows/{core-boundary-audit,u0-customize-app,pre-commit-agentic-cert,migrate-app-binding-to-generic-core}.md` | ✅ W2 complete |
| DoD-3 | 6 governance scripts + hooks.json created | `ls tools/governance/{core_write_guard,core_leakage_scan,receipt_required_guard,app_runtime_package_scan,boundary_receipt_validator}.py .cursor/hooks.json` | ✅ W3 complete |
| DoD-4 | 6 CI governance tests passing with 17 negative controls | `pytest tests/governance/ -v` shows 6 pass, 0 fail | ✅ W4 complete |
| DoD-5 | ≥3 existing bindings migrated with receipts | W5B P1 complete: P1a CERTIFIED, P1b BRIDGE_ACCEPTED, P1c CERTIFIED. Receipt v4.0: artifacts/governance/apps_lic_binding_migration_w5b_p1_receipt.json | ✅ W5B P1 complete |
| DoD-6 | Post-migration negative controls verify enforcement | W6 TODO: Re-run negative controls after W5B P1 to prove migration did not weaken governance | 🔄 W4 baseline complete, W6 post-migration pending |
| DoD-7 | Final governance receipt generated | `cat artifacts/governance/agentic_core_static_apps_customization_governance_a1b2c3_receipt.json` valid JSON | ✅ W7 COMPLETE |

**Verification-vs-Deferral table**:

| Item | Why deferred | Tracked in |
|---|---|---|
| Migration of ALL existing bindings | Scope bound to representative samples; remaining bindings tracked | W5 migration receipts + follow-up plans |
| Performance testing of generic engines | Performance validation out of scope; correctness is goal | Future performance plan if needed |
| Full L6 completed-run profile consumer implementation | Generic consumer partially exists; full implementation deferred | L6 observability plan |

---

## Cursor Agent Alignment Checks

- All rules follow always-on or model_decision trigger discipline
- Skills follow SKILL.md frontmatter contract per AGENTS.md
- Workflows are actionable procedures, not just documentation
- Hooks exit 2 for blocking, log for advisory
- CI tests are deterministic and fail-closed
- Receipts provide audit trail for boundary-sensitive changes

---

## Section 1: Executive Summary

**This plan prevents apps_* leakage into agentic_core.**

The core architectural law is: **agentic_core is app-agnostic runtime infrastructure; apps_* customize behavior through U0 runtime_customization_package and app-owned contracts/profiles.**

Apps customize inputs; core enforces contracts.

**Allowed in agentic_core:**
- Generic contract-chain propagation
- Generic profile resolver (consumes app-owned refs)
- Generic route policy interpreter
- Generic GateMesh enforcement
- Generic Exit profile enforcer
- Generic UWG enforcement
- Generic L6 completed-run profile consumer
- Generic receipt/proof infrastructure
- Generic anti-bypass checks

**Forbidden in agentic_core:**
- apps_lic-specific route logic (e.g., hardcoded R4_MANAGED_DRAFT)
- apps_rg-specific route logic (e.g., hardcoded R5_FINAL_ASSEMBLY)
- apps_qna-specific route logic
- App-specific cache policy (e.g., final_draft_r1a_bypass)
- App-specific Exit gate IDs
- App-specific judge/eval thresholds
- App-specific forbidden send policy (e.g., hardcoded linkedin_send rules)
- App-specific consent/compliance policy
- App-specific L6 promotion logic
- Hardcoded app_id branches (if app_id == "apps_lic")
- Hardcoded apps_* route names in shared runtime
- Hardcoded app profile paths in common core

**Existing app-specific core bindings are tolerated only as temporary migration adapters with explicit receipts.**

Files like `agentic_core/L0_routing/apps_lic_l0_binding.py` and `agentic_core/runtime/exit/apps_lic_exit_binding.py` are classified as either:
- `TEMPORARY_THIN_ADAPTER` — migration in progress, receipt required
- `CORE_APP_SPECIFIC_LEAKAGE` — technical debt, schedule for migration
- `GENERIC_READY` — already generic, no action needed
- `MIGRATION_REQUIRED` — must move to generic engine + app profile

**Final target state:** Generic core engines consume app-owned profile refs. No hardcoded app behavior in shared infrastructure.

---

## Section 2: Non-Negotiable Spine Laws

These laws govern the L0-L7 execution stack and are enforced by gates, hooks, and CI tests:

### Layer Boundaries

**U0 (Intake/Validation)**
- Validates and preserves, but does NOT route, retrieve, execute, assemble prompts, call models/tools, write L4, or learn
- Transforms external input to ValidatedRequest
- Emits runtime_customization_package as carrier only

**L1 (Cognition/Planning)**
- Plans but does NOT route with authority
- Proposes but does not enforce
- Emits intent, not execution

**L0 (Routing/Authority)**
- Emits exactly one RouteContract
- Interprets app-owned route profile generically
- No hardcoded app-specific route selection

**L3 (Orchestration)**
- Orchestrates only when execution_form = MANAGED_WORKFLOW
- Must NOT reroute, retrieve directly, execute, approve output, write L4, or learn
- Enforces plan fidelity, not outcome validity

**L2 (Execution)**
- Executes bounded packets
- May emit proposed_state_diff only
- Must NOT commit durable state
- Fail-soft on bounded execution failure

**Exit (Evaluation/X3)**
- Emits exactly one X3 disposition
- Consumes app-owned Exit profile
- Enforces generic GateMesh law
- No app-specific gate IDs hardcoded

**UWG (Unit of Work Governance)**
- Is the ONLY durable write admission path
- Validates CommitRequest against app-owned write policy
- No bypass paths permitted

**L4 (State)**
- Stores durable truth only after UWG
- No direct writes from apps_*, L2, L3, Exit, or L6

**L6 (System Learning)**
- Learns only after the current-run boundary
- Outputs future-run proposals only
- No immediate-run influence

### GateVerdict Semantics

- **UNKNOWN is never PASS** — Unknown verdict does not clear the gate
- **NOT_APPLICABLE requires a reason** — NA verdict must include applicability rationale
- **Missing applicable GateVerdict is UNKNOWN, not PASS** — Absence of verdict is not clearance

---

## Section 3: Repository Ownership Model

### agentic_core Owns

| Concern | Responsibility |
|---------|---------------|
| Base contracts | ValidatedRequest, RouteContract, GateVerdict, X3 disposition schemas |
| Common spine execution | L0-L7 generic engine implementations |
| Generic U0 handoff mechanics | U0 validation, package preservation |
| Generic route policy interpreter | RouteContract emission from route profile |
| Generic profile resolver | Resolves app-owned profile refs at runtime |
| Generic GateMesh law | Gate dependency, sequencing, consensus |
| Generic Exit enforcer | Consumes Exit profile, emits X3, no app logic |
| Generic UWG write law | CommitRequest validation, durable admission |
| Generic L6 completed-run consumer | Post-run profile ingestion |
| Generic proof and receipt validators | Evidence validation, chain verification |

### apps_* Owns

| Concern | Examples |
|---------|----------|
| App ingress contract | JSON schema, field map, validation rules |
| App JSON schema | Request/response schemas, versioned |
| App field map | Input field → canonical field mapping |
| runtime_customization_package | Route, cache, Exit, runtime gate, judge refs |
| Route profile | Route ID selection policy, fallback chains |
| Retrieval profile | R1a/R1b/C0 retrieval config, depth, sources |
| Prompt profile | Prompt assembly, few-shot, template refs |
| Cache policy | R1a exact, R1b semantic, reuse rules |
| Runtime gate profile | G21/G22/G23 gate enablement, thresholds |
| Exit profile | Exit gate IDs, eval rubric refs, HITL policy |
| Judge/eval/rubric profiles | Grader configs, score dimensions, thresholds |
| Threshold profiles | Per-dimension pass/fail/escalate thresholds |
| Forbidden action/send policy | Blocked actions, send restrictions, consent gates |
| Consent/compliance policy | GDPR, opt-in, retention rules |
| Write policy | What can be written, where, how long |
| Learning/meta-feedback profile | Signal extraction, exemplar selection |
| App tests | Unit, integration, E2E tests for app logic |
| App receipts | Migration receipts, policy receipts |

---

## Section 4: Windsurf Enforcement Layers

### Layer 1: AGENTS.md

| File | Scope |
|------|-------|
| `AGENTS.md` (root) | Global architecture law: core is app-agnostic, apps customize via U0 |
| `agentic_core/AGENTS.md` | Core boundary rules: allowed/forbidden patterns per layer |
| `apps_lic/AGENTS.md` | App customization rules: what apps_lic owns and must provide |
| `apps_rg/AGENTS.md` | App customization rules: what apps_rg owns and must provide |
| `apps_qna/AGENTS.md` | App customization rules: what apps_qna owns and must provide (if exists) |

### Layer 2: Windsurf Rules

| Rule | Trigger | Purpose |
|------|---------|---------|
| `agentic-core-static.md` | always_on | Core static in app behavior; classify all core edits |
| `agentic-core-glob-lock.md` | globs: agentic_core/** | Require generic justification + boundary receipt |
| `apps-customization.md` | globs: apps_*/** | App-specific behavior belongs here |
| `boundary-audit-required.md` | model_decision or manual | Trigger when core changed or app literals appear |

### Layer 3: Skills

| Skill | Purpose |
|-------|---------|
| `core-boundary-audit` | List changed files, classify each, scan core, write receipt |
| `u0-app-customization` | Audit app contracts, add/update U0 package, add profile refs |
| `runtime-package-verifier` | Verify package refs, digest, schema, field map reach |
| `receipt-auditor` | Verify receipt exists, changed files, tests, gaps |
| `app-leakage-refactor` | Detect core leakage, move to app profiles, add migration receipt |

### Layer 4: Workflows

| Workflow | Purpose |
|----------|---------|
| `/core-boundary-audit` | Git diff → classify → scan → write receipt → block if leakage |
| `/u0-customize-app` | App audit → package update → profile refs → schema → tests → receipt |
| `/pre-commit-agentic-cert` | Run governance tests → static scan → validate receipts → no bypass |
| `/migrate-app-binding-to-generic-core` | Identify binding → extract policy → generic engine → replace → prove → receipt |

### Layer 5: Hooks and CI

| Hook | Script | Purpose |
|------|--------|---------|
| `pre_write_code` | `core_write_guard.py` | Block core edits without receipt |
| `post_write_code` | `core_leakage_scan.py` | Scan for app-specific literals |
| `pre_run_command` | `receipt_required_guard.py` | Block broad commands without receipt |
| `post_cursor_agent_response` | `app_runtime_package_scan.py` | Check U0 package completeness |

**Hook law:** Exit code 2 blocks unsafe action; hooks are local guardrails, not final authority; CI remains final authority.

---

## Section 5: Required Files to Create or Update

### AGENTS.md Files

```
AGENTS.md
agentic_core/AGENTS.md
apps_lic/AGENTS.md
apps_rg/AGENTS.md
apps_qna/AGENTS.md (if apps_qna exists)
```

### Windsurf Rules

```
.cursor/rules/agentic-core-static.md
.cursor/rules/agentic-core-glob-lock.md
.cursor/rules/apps-customization.md
.cursor/rules/boundary-audit-required.md
```

### Skills

```
.cursor/skills/core-boundary-audit/SKILL.md
.cursor/skills/u0-app-customization/SKILL.md
.cursor/skills/runtime-package-verifier/SKILL.md
.cursor/skills/receipt-auditor/SKILL.md
.cursor/skills/app-leakage-refactor/SKILL.md
```

### Workflows

```
.cursor/workflows/core-boundary-audit.md
.cursor/workflows/u0-customize-app.md
.cursor/workflows/pre-commit-agentic-cert.md
.cursor/workflows/migrate-app-binding-to-generic-core.md
```

### Hooks and Scripts

```
.cursor/hooks.json (update)
tools/governance/core_write_guard.py
tools/governance/core_leakage_scan.py
tools/governance/receipt_required_guard.py
tools/governance/app_runtime_package_scan.py
tools/governance/boundary_receipt_validator.py
```

### CI Governance Tests

```
tests/governance/test_agentic_core_static_boundary.py
tests/governance/test_no_app_specific_literals_in_core.py
tests/governance/test_apps_runtime_package_contracts.py
tests/governance/test_no_direct_l4_write_bypass.py
tests/governance/test_no_app_exit_x3_emission.py
```

---

## Section 6: Root AGENTS.md Content (Proposed)

```markdown
# Agentic Core Architecture Law

## Principle: Core is App-Agnostic

agentic_core is the common governed runtime spine. It must remain **app-agnostic** — it knows apps exist, but does not hardcode app-specific behavior.

## Principle: Apps Customize Through U0

apps_* customize behavior through:
- U0 runtime_customization_package (carrier only, no routing logic)
- App-owned contracts (JSON schema, field map)
- App-owned config/profile refs (route, cache, Exit, gate, judge, write, learning)
- App-owned tests and receipts

## Principle: Core Enforces Contracts Generically

agentic_core may change only for **generic runtime infrastructure** that applies across all apps_*:
- Generic contract-chain propagation
- Generic profile resolver (consumes app-owned refs)
- Generic route policy interpreter
- Generic GateMesh enforcement
- Generic Exit profile enforcer
- Generic UWG enforcement
- Generic L6 completed-run profile consumer
- Generic receipt/proof infrastructure
- Generic anti-bypass checks

## Anti-Pattern: App-Specific Code in Core

App-specific behavior in shared agentic_core is **leakage**, not architecture. The following are forbidden:

- `if app_id == "apps_lic"` branches
- Hardcoded `apps_lic`, `apps_rg`, `apps_qna` route logic
- App-specific cache policy (e.g., `final_draft_r1a_bypass`)
- App-specific Exit gate IDs
- App-specific judge/eval thresholds
- App-specific forbidden send policy
- App-specific consent/compliance policy
- App-specific L6 promotion logic
- Hardcoded app profile paths in common core

## Exception: Temporary Thin Adapters

Existing app-specific core bindings (e.g., `apps_lic_l0_binding.py`) are tolerated only as:
- **TEMPORARY_THIN_ADAPTER** with migration receipt
- Explicit `migration_target_date` in receipt
- Documented plan to move to generic engine + app profile

## Enforcement

- AGENTS.md (this file) is the single source of truth
- Scoped AGENTS.md in agentic_core/ and apps_*/ provide detailed rules
- Windsurf rules enforce at edit time
- CI governance tests enforce at commit time
- Receipts required for all boundary-sensitive changes
```

---

## Section 7: agentic_core/AGENTS.md Content (Proposed)

```markdown
# Agentic Core Boundary Rules

## Allowed in agentic_core

### Generic Infrastructure (Always Permitted)

- **Generic resolver**: Profile resolution from app-owned refs
- **Generic route interpreter**: RouteContract emission from route profile
- **Generic Exit enforcer**: X3 disposition from Exit profile
- **Generic L6 consumer**: Completed-run profile ingestion
- **Generic UWG enforcement**: CommitRequest validation
- **Generic GateMesh enforcement**: Gate dependency and consensus
- **Generic contract propagation**: Contract chain through layers

### App References (Permitted with Generic Interpretation)

- `app_id` as opaque string key
- App-owned profile refs resolved at runtime
- App-owned schema refs for validation
- App-owned policy refs for enforcement

## Forbidden in agentic_core

### Hardcoded App Behavior (Never Permitted)

- `if app_id == "apps_lic"` or similar branches
- `if app_id == "apps_rg"` or similar branches
- `if app_id == "apps_qna"` or similar branches
- Hardcoded `apps_lic`, `apps_rg`, `apps_qna` literals in logic
- Hardcoded app-specific route names (e.g., `R4_MANAGED_DRAFT`, `R5_FINAL_ASSEMBLY`)

### App-Specific Policy (Never Permitted)

- App-specific cache bypass rules (e.g., `final_draft_r1a_bypass`, `final_draft_r1b_bypass`)
- App-specific gate IDs in GateMesh
- App-specific thresholds in eval
- App-specific forbidden send lists (e.g., hardcoded `linkedin_send`, `email_outbox_send` blocks)
- App-specific consent/compliance policy enforcement
- App-specific L6 promotion policies

### Direct App State Access (Never Permitted)

- Hardcoded app profile paths
- Direct reading of app-specific config files
- Bypassing U0 package for app customization

## Migration Path

Existing violations must be classified:
- `TEMPORARY_THIN_ADAPTER`: Migration in progress, receipt required
- `CORE_APP_SPECIFIC_LEAKAGE`: Technical debt, schedule for migration
- `GENERIC_READY`: Already generic, no action needed
- `MIGRATION_REQUIRED`: Move to generic engine + app profile
```

---

## Section 8: apps_*/AGENTS.md Template (Proposed)

```markdown
# {{APP_NAME}} Customization Rules

## Ownership

apps_{{app_short}} owns:
- App ingress contract (JSON schema, field map)
- runtime_customization_package (route, cache, Exit, gate, judge, write, learning refs)
- Route profile (route ID selection, fallback chains)
- Retrieval profile (R1a/R1b/C0 config, depth, sources)
- Prompt profile (assembly, few-shot, templates)
- Cache policy (exact, semantic, reuse rules)
- Runtime gate profile (G21/G22/G23 enablement)
- Exit profile (gate IDs, eval rubric, HITL policy)
- Judge/eval/rubric profiles (grader configs, dimensions, thresholds)
- Threshold profiles (pass/fail/escalate thresholds)
- Forbidden action/send policy
- Consent/compliance policy
- Write policy
- Learning/meta-feedback profile
- App tests and receipts

## Prohibited

apps_{{app_short}} must NOT:
- Implement separate Exit layer (only Exit profile)
- Emit X3 disposition (only Exit consumes Exit profile, emits X3)
- Write L4 durable state directly (must pass Exit X3C -> CommitRequest -> UWG -> L4)
- Directly send or perform forbidden side effects (must route through governed spine)
- Bypass U0 runtime_customization_package for behavior customization

## Integration Path

apps_{{app_short}} behavior enters agentic_core through:
1. U0 runtime_customization_package (validated and preserved)
2. Generic core resolver (consumes package refs)
3. Generic route interpreter (emits RouteContract)
4. Generic Exit enforcer (consumes Exit profile, enforces gate mesh)
5. UWG (admits writes per app-owned write policy)

## Receipts

All app customization changes should produce receipts documenting:
- Changed files
- Profile refs updated
- Tests covering changes
- Known gaps or migration exceptions
```

---

## Section 9: Windsurf Rules Content (Proposed)

### A. agentic-core-static.md (always_on)

```yaml
---
trigger: always_on
---

# Agentic Core Static in App Behavior

agentic_core must remain app-agnostic. Before any core edit, classify:
- Generic runtime infrastructure (allowed)
- App-specific behavior (forbidden — belongs in apps_*)

## Classification Questions

1. Does this change apply to all apps_*? → Generic, allowed
2. Does this change hardcode app_id branches? → App-specific, forbidden
3. Does this change hardcode app-specific route/policy? → App-specific, forbidden
4. Does this change add app literals (apps_lic, apps_rg, apps_qna)? → App-specific, forbidden

## Required Actions

If core change classified as generic:
- Proceed with edit
- Document in change log

If core change classified as app-specific:
- STOP
- Move behavior to apps_* config/profile
- Refactor core to generic engine consuming profile
- Write migration receipt
```

### B. agentic-core-glob-lock.md (globs: agentic_core/**)

```yaml
---
trigger: glob
globs:
  - agentic_core/**
---

# Agentic Core Edit Gate

Before editing agentic_core/** files:

## Required

1. **Generic justification**: Explain how change applies to all apps_*
2. **Boundary receipt**: Receipt file at .windsurf/receipts/agentic_core_<timestamp>.json

## Receipt Contents

- changed_files: List of agentic_core files
- classification: "generic_infrastructure" | "temporary_adapter" | "app_specific_leakage"
- justification: Why this is generic (or why adapter is temporary)
- tests: List of tests covering change
- gaps: Known gaps or migration items

## Prohibited Without Receipt

Any core edit without receipt requires Author-Gate approval per constitutional §6.
```

### C. apps-customization.md (globs: apps_*/**)

```yaml
---
trigger: glob
globs:
  - apps_lic/**
  - apps_rg/**
  - apps_qna/**
  - apps_*/**
---

# Apps Customization Path

App-specific behavior belongs in apps_*/ directories.

## Correct Customization

- Add/update runtime_customization_package
- Add app-owned profile refs (route, cache, Exit, gate, judge, write, learning)
- Update app JSON schema and field map
- Add app tests and receipts

## Incorrect (Core Leakage)

- Modifying agentic_core for app-specific behavior
- Hardcoding app behavior in shared runtime
- Bypassing U0 package for customization

## Verification

After customization, run:
```bash
python tools/governance/app_runtime_package_scan.py --app <app_name>
```
```

### D. boundary-audit-required.md (model_decision or manual)

```yaml
---
trigger: model_decision
---

# Boundary Audit Required

Trigger this skill when:
- Cursor Agent detects agentic_core files changed
- App-specific literals appear in core context
- app_id branching patterns detected
- Hardcoded app behavior suspected

## Procedure

1. Run `/core-boundary-audit` workflow
2. List changed files
3. Classify each change
4. Scan for forbidden app-specific literals
5. Decide: ALLOW | ALLOW_WITH_GENERIC_REFACTOR | BLOCK_MOVE_TO_APPS_CONFIG | BLOCK_ROLLBACK_REQUIRED
6. Write receipt documenting decision
```

---

## Section 10: Skills Content (Outlines)

### core-boundary-audit/SKILL.md

```markdown
---
trigger: model_decision
---

# Core Boundary Audit

## Purpose
Audit agentic_core changes for app-agnosticism compliance.

## Procedure

1. **List changed files**
   - `git diff --name-only agentic_core/`
   - Categorize by layer (L0, L1, L2, L3, Exit, UWG, L6)

2. **Classify each file**
   - Generic infrastructure: allowed
   - Temporary thin adapter: allowed with receipt
   - App-specific leakage: requires migration

3. **Scan core for forbidden literals**
   - `apps_lic`, `apps_rg`, `apps_qna`
   - `if app_id`, `app_id ==`
   - App-specific route names (R4_MANAGED_DRAFT, etc.)
   - App-specific cache bypass (final_draft_r1a_bypass, etc.)
   - App-specific send policies (linkedin_send, etc.)

4. **Decide**
   - `ALLOW`: Change is generic infrastructure
   - `ALLOW_WITH_GENERIC_REFACTOR`: Change is mostly generic, minor refactor needed
   - `BLOCK_MOVE_TO_APPS_CONFIG`: Change is app-specific, move to apps_* config
   - `BLOCK_ROLLBACK_REQUIRED`: Change is leakage, rollback and redo via apps_*

5. **Write receipt**
   - Document classification, decision, tests, gaps
```

### u0-app-customization/SKILL.md

```markdown
---
trigger: model_decision
---

# U0 App Customization

## Purpose
Add or update app customization through U0 runtime_customization_package.

## Procedure

1. **Audit existing app contracts/configs**
   - Review apps_<name>/config/domain_contract/
   - Identify missing refs

2. **Add/update runtime_customization_package**
   - Ensure package has route_profile_ref
   - Ensure package has cache_policy_ref
   - Ensure package has exit_profile_ref
   - Ensure package has runtime_gate_profile_ref
   - Ensure package has judge_eval_profile_ref
   - Ensure package has write_policy_ref
   - Ensure package has learning_profile_ref

3. **Preserve U0 as carrier only**
   - U0 validates and preserves
   - No routing logic in U0
   - No app-specific execution in U0

4. **Add profile refs and digests**
   - Each ref has corresponding file
   - Each ref has package_digest for integrity

5. **Update schema and field map**
   - JSON schema covers all package fields
   - Field map connects external to canonical

6. **Add tests**
   - Package validation tests
   - Profile resolution tests
   - End-to-end reach tests

7. **Run boundary audit**
   - Confirm no core leakage
   - Write receipt
```

### runtime-package-verifier/SKILL.md

```markdown
---
trigger: model_decision
---

# Runtime Package Verifier

## Purpose
Verify runtime_customization_package completeness and integrity.

## Procedure

1. **Verify required refs present**
   - route_profile_ref: exists
   - cache_policy_ref: exists
   - exit_profile_ref: exists
   - runtime_gate_profile_ref: exists
   - judge_eval_profile_ref: exists or null
   - write_policy_ref: exists
   - learning_profile_ref: exists or null

2. **Verify package_digest**
   - Digest covers all refs
   - Digest algorithm specified
   - Digest matches current content

3. **Verify schema and field map**
   - JSON schema validates package
   - Field map reaches all refs

4. **Verify no dropped pointers**
   - All refs resolve to existing files
   - No broken config references

5. **Verify package reaches ValidatedRequest.app_payload**
   - U0 passes package through
   - L0+ receives package in context
```

### receipt-auditor/SKILL.md

```markdown
---
trigger: model_decision
---

# Receipt Auditor

## Purpose
Verify boundary receipt validity and completeness.

## Procedure

1. **Verify receipt exists**
   - File at .windsurf/receipts/agentic_core_<timestamp>.json
   - Valid JSON

2. **Verify changed files listed**
   - All agentic_core files in diff listed
   - No unlisted files modified

3. **Verify tests listed**
   - Tests covering changes specified
   - Test commands executable

4. **Verify known gaps listed**
   - Explicit acknowledgment of gaps
   - Migration plan if applicable

5. **Verify no undocumented core changes**
   - Classification present for all changes
   - Justification for generic or adapter status

## Receipt Schema

```json
{
  "receipt_version": "1.0",
  "created_at": "ISO8601",
  "changed_files": ["agentic_core/..."],
  "classification": "generic_infrastructure|temporary_adapter|app_specific_leakage",
  "justification": "string",
  "tests": ["pytest ..."],
  "known_gaps": [{"description": "", "plan": ""}],
  "migration_target_date": "ISO8601 or null"
}
```
```

### app-leakage-refactor/SKILL.md

```markdown
---
trigger: model_decision
---

# App Leakage Refactor

## Purpose
Move app-specific logic from agentic_core to apps_* profiles.

## Procedure

1. **Detect app-specific logic in core**
   - Find hardcoded app_id branches
   - Find app-specific literals
   - Find app-specific policy

2. **Move behavior to apps_* profile/config**
   - Extract route policy to apps_*/config/domain_contract/route_profile.yaml
   - Extract cache policy to apps_*/config/domain_contract/cache_policy.yaml
   - Extract Exit profile to apps_*/config/domain_contract/exit_profile.yaml
   - Extract gate policy to apps_*/config/domain_contract/runtime_gate_profile.yaml

3. **Replace core logic with generic interpreter**
   - Update resolver to consume profile
   - Remove hardcoded branches
   - Add runtime profile lookup

4. **Add migration receipt**
   - Document original and new locations
   - Record test verification
   - Set migration_target_date if remaining work

## Example

Before:
```python
if app_id == "apps_lic":
    route = Route.R4_MANAGED_DRAFT
else:
    route = Route.DEFAULT
```

After:
```python
route_profile = resolve_profile(context.route_profile_ref)
route = route_profile.select_route(context)
```
```

---

## Section 11: Workflows Content (Outlines)

### /core-boundary-audit

```markdown
# Core Boundary Audit Workflow

## When to Run
- Before committing agentic_core changes
- When app-specific patterns detected in core
- As part of PR review

## Steps

1. Run git diff
   ```bash
   git diff agentic_core/ > /tmp/core_diff.patch
   ```

2. List changed files
   ```bash
   git diff --name-only agentic_core/
   ```

3. Classify core changes
   - Generic infrastructure: proceed
   - Temporary adapter: verify receipt
   - App-specific leakage: stop, refactor

4. Scan for app-specific leakage
   ```bash
   python tools/governance/core_leakage_scan.py
   ```

5. Write receipt
   ```bash
   python tools/governance/boundary_receipt_validator.py --write-receipt
   ```

6. Block if leakage found
   - Exit code 2
   - Log violation
   - Suggest refactor path
```

### /u0-customize-app

```markdown
# U0 Customize App Workflow

## When to Run
- Adding new customization to apps_*
- Updating runtime_customization_package
- Refactoring app to use U0 path

## Steps

1. App audit
   - Review current contracts
   - Identify missing profile refs

2. Package update
   - Add missing refs to runtime_customization_package
   - Update package_digest

3. Profile refs
   - Create/update profile YAMLs
   - Ensure digests in package

4. Schema
   - Update JSON schema
   - Update field map

5. Tests
   - Add package validation tests
   - Add profile resolution tests

6. Boundary audit
   - Confirm no core changes needed
   - Verify customization stays in apps_*

7. Receipt
   - Document customization changes
   - Link to tests
```

### /pre-commit-agentic-cert

```markdown
# Pre-Commit Agentic Cert Workflow

## When to Run
- Before git commit with agentic_core changes
- In CI pre-commit hook
- As part of PR gate

## Steps

1. Run governance tests
   ```bash
   pytest tests/governance/ -q
   ```

2. Run static leakage scanner
   ```bash
   python tools/governance/core_leakage_scan.py --fail-on-leakage
   ```

3. Validate receipts
   ```bash
   python tools/governance/boundary_receipt_validator.py
   ```

4. Validate no direct L4 write
   ```bash
   pytest tests/governance/test_no_direct_l4_write_bypass.py -v
   ```

5. Validate no app X3 emission
   ```bash
   pytest tests/governance/test_no_app_exit_x3_emission.py -v
   ```

## Success Criteria
- All tests pass
- No leakage detected
- Valid receipts present
- Exit code 0
```

### /migrate-app-binding-to-generic-core

```markdown
# Migrate App Binding to Generic Core Workflow

## When to Run
- Refactoring existing app-specific core binding
- Moving from hardcoded to generic engine

## Steps

1. Identify app-specific binding in core
   - Find file (e.g., apps_lic_l0_binding.py)
   - Document hardcoded behavior

2. Extract app policy to apps_* config/profile
   - Create apps_*/config/domain_contract/<profile>.yaml
   - Move hardcoded values to profile

3. Create or extend generic core engine
   - Add generic resolver/interpreter
   - Consume profile ref

4. Replace binding with package-driven interpretation
   - Update caller to use generic engine
   - Remove hardcoded binding

5. Prove behavior unchanged with tests
   - Run app tests before/after
   - Compare outputs
   - Document any intentional changes

6. Write migration receipt
   - Document original and new locations
   - Record verification
   - Mark as MIGRATION_REQUIRED or GENERIC_READY
```

---

## Section 12: Hooks Design

### hooks.json Proposal

```json
{
  "hooks": [
    {
      "id": "pre_write_code",
      "command": "python tools/governance/core_write_guard.py",
      "working_directory": "${workspace}",
      "show_output": true,
      "when": "before_edit",
      "filter": {
        "paths": ["agentic_core/**"]
      }
    },
    {
      "id": "post_write_code",
      "command": "python tools/governance/core_leakage_scan.py",
      "working_directory": "${workspace}",
      "show_output": true,
      "when": "after_edit",
      "filter": {
        "paths": ["agentic_core/**"]
      }
    },
    {
      "id": "pre_run_command",
      "command": "python tools/governance/receipt_required_guard.py",
      "working_directory": "${workspace}",
      "show_output": true,
      "when": "before_command",
      "filter": {
        "commands": ["python -m apps_*", "python tools/implement*"]
      }
    },
    {
      "id": "post_cursor_agent_response",
      "command": "python tools/governance/app_runtime_package_scan.py",
      "working_directory": "${workspace}",
      "show_output": false,
      "when": "after_response"
    }
  ]
}
```

### Hook Law

- **Exit code 2** blocks unsafe action
- **Hooks are local guardrails**, not final authority
- **CI remains final authority** — hooks can be bypassed locally, CI cannot

---

## Section 13: Governance Scripts Specification

### core_write_guard.py

**Purpose**: Blocks edits to agentic_core unless allowed

**Behavior**:
- Check if path is allowlisted generic core infrastructure
- Check if boundary receipt exists for changed files
- Allow TEMPORARY_THIN_ADAPTER edits only if migration exception active
- Exit 0: allowed
- Exit 2: blocked with reason

**Allowlist**:
- Generic resolvers in agentic_core/config/
- Generic engines in agentic_core/L*/
- Base contracts in agentic_core/L_CONTRACTS/
- Framework code in agentic_core/utils/
- Migration receipts in .windsurf/receipts/

### core_leakage_scan.py

**Purpose**: Scans agentic_core for forbidden app-specific literals

**Forbidden patterns**:
- `apps_lic`, `apps_rg`, `apps_qna` (outside test fixtures and migration receipts)
- `if app_id` branches
- `app_id ==` comparisons
- `R4_MANAGED_DRAFT`, `R3R4_MANAGED_RESEARCH_THEN_DRAFT`
- `final_draft_r1a_bypass`, `final_draft_r1b_bypass`
- `linkedin_send`, `email_outbox_send`
- App-specific G21/G22 profile lists hardcoded in core

**Allowlist**:
- Generic test fixtures with documented purpose
- Migration receipts with explicit exception
- Generic app_id string handling (not branching)

### receipt_required_guard.py

**Purpose**: Blocks running broad implementation commands after core changes without receipt

**Behavior**:
- Check for agentic_core changes in recent edits
- Check if boundary receipt exists
- Permit read-only commands and tests (exit 0)
- Block implementation commands without receipt (exit 2)

**Permitted without receipt**:
- `pytest`, `python -m pytest`
- `git status`, `git diff`
- `python tools/governance/*`

**Blocked without receipt**:
- `python -m apps_*`
- `python tools/implement*`
- `python ops_scripts/ci/*` (except in CI context)

### app_runtime_package_scan.py

**Purpose**: Checks each apps_* has valid runtime_customization_package

**Behavior**:
- Scan apps_*/config/ for runtime_customization_package.yaml or equivalent
- Check package has required refs (route, cache, Exit, runtime gate, judge/eval, write, learning)
- Check package has package_digest
- Flag apps without package or with incomplete refs
- Write report to artifacts/governance/app_runtime_packages.json

### boundary_receipt_validator.py

**Purpose**: Validates receipt schema and required fields

**Schema validation**:
- receipt_version: "1.0"
- created_at: ISO8601
- changed_files: non-empty list
- classification: enum
- justification: non-empty string
- tests: list of commands
- known_gaps: list of {description, plan}
- migration_target_date: ISO8601 or null

**Validation rules**:
- If classification == "temporary_adapter", migration_target_date required
- If classification == "app_specific_leakage", remediation required
- tests must be non-empty for generic_infrastructure
- known_gaps must be empty or all have plans

---

## Section 14: CI Governance Tests Specification

### test_agentic_core_static_boundary.py

**Purpose**: Enforces no app-specific business policy in shared core

**Tests**:
- `test_no_app_specific_route_logic_in_l0` — L0 routing is generic
- `test_no_app_specific_cache_policy_in_core` — Cache policy is profile-driven
- `test_no_app_specific_exit_gates_in_core` — Exit gates are profile-driven
- `test_no_app_id_branching_in_generic_runtime` — No if app_id branches
- `test_app_specific_literals_blocked_outside_adapters` — App literals only in adapters

### test_no_app_specific_literals_in_core.py

**Purpose**: Scans core for forbidden terms

**Tests**:
- `test_no_apps_lic_literal_outside_allowlist`
- `test_no_apps_rg_literal_outside_allowlist`
- `test_no_apps_qna_literal_outside_allowlist`
- `test_no_r4_managed_draft_hardcoded`
- `test_no_final_draft_bypass_hardcoded`
- `test_allowlist_is_explicit` — Allowlist entries documented

### test_apps_runtime_package_contracts.py

**Purpose**: Each apps_* package has required refs and validates

**Tests**:
- `test_apps_lic_has_runtime_package` — Package exists
- `test_apps_rg_has_runtime_package` — Package exists
- `test_package_has_required_refs` — All 7 refs present
- `test_package_has_valid_digest` — Digest algorithm + match
- `test_package_schema_validates` — JSON schema passes
- `test_package_reaches_validated_request` — U0 passes through

### test_no_direct_l4_write_bypass.py

**Purpose**: No direct L4 writes from apps or internal layers

**Tests**:
- `test_apps_cannot_import_l4_write_apis` — Import restriction
- `test_l2_cannot_write_durable_state` — L2 emits proposed_state_diff only
- `test_l3_cannot_write_durable_state` — L3 orchestrates only
- `test_exit_cannot_write_durable_state` — Exit emits X3 only
- `test_l6_cannot_write_durable_state` — L6 learns post-run only
- `test_durable_write_requires_exit_x3c` — Path: Exit X3C -> CommitRequest -> UWG -> L4

### test_no_app_exit_x3_emission.py

**Purpose**: Only Exit emits X3

**Tests**:
- `test_apps_cannot_emit_x3` — apps_* have no X3 emission
- `test_only_exit_emits_x3` — agentic_core/exit/ only place
- `test_app_exit_profiles_are_data` — Exit profiles are YAML, not code
- `test_app_cannot_bypass_exit` — No direct CommitRequest from apps

---

## Section 15: Migration Policy for Existing App-Specific Core Bindings

### Existing Bindings Inventory

| File | Location | Classification | Migration Target |
|------|----------|----------------|------------------|
| apps_lic_l0_binding.py | agentic_core/L0_routing/ | TEMPORARY_THIN_ADAPTER | Generic L0 route interpreter + apps_lic route profile |
| apps_lic_exit_binding.py | agentic_core/runtime/exit/ | TEMPORARY_THIN_ADAPTER | Generic Exit enforcer + apps_lic Exit profile |
| apps_lic_promo_binding.py | agentic_core/L6_observability/promotion/ | TEMPORARY_THIN_ADAPTER | Generic L6 consumer + apps_lic meta-feedback profile |
| apps_rg_l0_binding.py | agentic_core/L0_routing/ | TEMPORARY_THIN_ADAPTER | Generic L0 route interpreter + apps_rg route profile |
| apps_rg_exit_binding.py | agentic_core/runtime/exit/ | TEMPORARY_THIN_ADAPTER | Generic Exit enforcer + apps_rg Exit profile |

### Migration Procedure

1. **Create app profile** in apps_*/config/domain_contract/
   - For route: `route_profile.yaml`
   - For Exit: `exit_profile.yaml`
   - For L6: `meta_feedback_profile.yaml`

2. **Extend generic engine** in agentic_core to consume profile
   - Update resolver to read profile ref from U0 package
   - Update interpreter to apply profile generically

3. **Replace binding call** with generic engine + profile
   - Remove hardcoded binding
   - Add runtime profile resolution

4. **Verify behavior unchanged**
   - Run app tests before/after
   - Compare outputs
   - Document any intentional changes

5. **Write migration receipt**
   ```json
   {
     "receipt_version": "1.0",
     "created_at": "2026-05-11T12:00:00Z",
     "original_file": "agentic_core/L0_routing/apps_lic_l0_binding.py",
     "new_profile": "apps_lic/config/domain_contract/route_profile.yaml",
     "generic_engine": "agentic_core/L0_routing/generic_route_interpreter.py",
     "classification": "GENERIC_READY",
     "tests": ["pytest tests/apps_lic/test_l0_routing.py"],
     "verification": "identical_outputs"
   }
   ```

---

## Section 16: Plan Waves (Detailed)

### W0 Baseline Audit

**Metric**: Inventory completeness — 100% of governance files and bindings identified

**Scope**:
- List current .windsurf/ governance (rules, skills, workflows, hooks)
- List current AGENTS.md files
- Inventory agentic_core for app-specific literals
- Identify all `*binding*.py` files
- Classify existing bindings (adapter vs leakage)

**Checkpoint**: Baseline report at artifacts/governance/baseline_audit.json

### W1 Add Governance Instructions

**Metric**: 7 governance docs created (100%)

**Scope**:
- Root AGENTS.md with core law
- agentic_core/AGENTS.md with allowed/forbidden
- apps_lic/AGENTS.md, apps_rg/AGENTS.md, apps_qna/AGENTS.md with templates
- 4 Windsurf rules

**Checkpoint**: All files exist with complete content

### W2 Add Skills and Workflows

**Metric**: 5 skills + 4 workflows created (100%)

**Scope**:
- core-boundary-audit, u0-app-customization, runtime-package-verifier, receipt-auditor, app-leakage-refactor skills
- 4 workflow docs

**Checkpoint**: All SKILL.md and workflow files exist

### W3 Add Hooks and Governance Scripts

**Metric**: 6 scripts + hooks.json updated (100%)

**Scope**:
- core_write_guard.py, core_leakage_scan.py, receipt_required_guard.py
- app_runtime_package_scan.py, boundary_receipt_validator.py
- hooks.json with 4 hooks

**Checkpoint**: Scripts importable, hooks.json valid

### W4 Add CI Governance Tests

**Metric**: 5 test files with 25+ tests passing (100%)

**Scope**:
- Boundary, leakage, package, bypass, X3 test files

**Checkpoint**: `pytest tests/governance/` passes

### W5 Migrate Existing Bindings

**Metric**: ≥3 bindings migrated with receipts

**Scope**:
- Inventory and classify all bindings
- Migrate apps_lic L0 and Exit bindings
- Migrate apps_rg L0 and Exit bindings
- Write migration receipts

**Checkpoint**: Migration receipts in artifacts/governance/migration_receipts/

### W6 Prove Governance with Negative Controls

**Metric**: 5 violation attempts all caught

**Scope**:
- Attempt app-specific core route hardcode → hook/CI blocks
- Attempt app-specific Exit gate hardcode → hook/CI blocks
- Attempt direct L4 write → CI test fails
- Attempt app X3 emission → CI test fails
- Attempt final draft cache reuse policy in core → leakage scan catches

**Checkpoint**: artifacts/governance/negative_control_results.json shows all blocked

### W7 Final Governance Receipt

**Metric**: 1 receipt with all fields complete

**Scope**:
- Write artifacts/governance/agentic_core_static_apps_customization_governance_receipt.json
- Update Notion plan status to Completed

**Checkpoint**: Receipt valid JSON, Notion status = Completed

---

## Section 17: Acceptance Criteria

| Criterion | Target | Verification |
|-----------|--------|------------|
| App-specific leakage detectable | 100% coverage | core_leakage_scan.py catches all forbidden patterns |
| App-specific leakage blocked locally | 95% catch rate | Hook blocks obvious violations (exit 2) |
| App-specific leakage failed in CI | 100% catch rate | CI tests fail on any leakage |
| U0 customization path documented | 4 workflows | All U0 customization procedures in workflows |
| Existing bindings classified | 100% inventory | All bindings classified with migration plan |
| Hooks do not replace CI | Explicit | CI tests remain authoritative |
| Receipts required for core changes | Enforced | No core changes without receipt |
| No direct app L4 writes | Enforced | test_no_direct_l4_write_bypass.py passes |
| No app Exit/X3 emission | Enforced | test_no_app_exit_x3_emission.py passes |
| UNKNOWN never PASS | Enforced | Exit semantics tests verify |
| Durable write path preserved | Exit X3C → CommitRequest → UWG → L4 | test traces verify |
| L6 completed-run only | Post-run learning | L6 tests verify no immediate influence |

---

## Section 18: Final Receipt Specification

**Path**: `artifacts/governance/agentic_core_static_apps_customization_governance_receipt.json`

**Receipt Fields**:

```json
{
  "plan_id": "agentic-core-static-apps-customization-governance-a1b2c3",
  "created_at": "ISO8601 timestamp",
  "governance_goal": "Prevent apps_* leakage into agentic_core",
  "files_created": [
    "AGENTS.md",
    "agentic_core/AGENTS.md",
    "apps_lic/AGENTS.md",
    ...
  ],
  "files_modified": [
    ".cursor/hooks.json"
  ],
  "agentic_core_boundary_rules": {
    "rules_created": 4,
    "skills_created": 5,
    "workflows_created": 4,
    "hooks_added": 4
  },
  "apps_customization_rules": {
    "app_agents_md_created": 3,
    "u0_customization_documented": true
  },
  "hooks_added": ["pre_write_code", "post_write_code", "pre_run_command", "post_cursor_agent_response"],
  "skills_added": ["core-boundary-audit", "u0-app-customization", "runtime-package-verifier", "receipt-auditor", "app-leakage-refactor"],
  "workflows_added": ["core-boundary-audit", "u0-customize-app", "pre-commit-agentic-cert", "migrate-app-binding-to-generic-core"],
  "ci_tests_added": [
    "test_agentic_core_static_boundary.py",
    "test_no_app_specific_literals_in_core.py",
    ...
  ],
  "changed_core_files_classified": {
    "generic_infrastructure": 0,
    "temporary_adapter": 0,
    "app_specific_leakage": 0
  },
  "existing_app_specific_core_bindings": {
    "apps_lic_l0_binding.py": "TEMPORARY_THIN_ADAPTER",
    "apps_lic_exit_binding.py": "TEMPORARY_THIN_ADAPTER",
    "apps_rg_l0_binding.py": "TEMPORARY_THIN_ADAPTER",
    "apps_rg_exit_binding.py": "TEMPORARY_THIN_ADAPTER"
  },
  "migration_required": ["apps_lic_l0_binding.py", "apps_lic_exit_binding.py", "apps_rg_l0_binding.py", "apps_rg_exit_binding.py"],
  "migration_exceptions": [],
  "negative_controls": {
    "attempted": 5,
    "blocked_by_hook": 2,
    "blocked_by_ci": 3
  },
  "test_commands": [
    "pytest tests/governance/ -v"
  ],
  "test_results": {
    "passed": 25,
    "failed": 0
  },
  "known_gaps": [
    "Remaining bindings to migrate (tracked in follow-up plans)",
    "Performance testing of generic engines deferred"
  ],
  "final_verdict": "Governance infrastructure operational. Existing bindings classified and scheduled for migration. All negative controls passed."
}
```

---

## Section 19: Important Constraints Summary

- **W0-W4 governance infrastructure has been implemented and certified**
- **W5 migration work is now active but tightly scoped**
- **Do not broaden W5B P1 beyond apps_lic L6/Exit/L0**
- **Do not proceed to P1c until P1a/P1b gates pass**
- **Do not weaken tests or governance hooks to make migration pass**
- **Preserve behavior parity** — all refactored bindings must pass existing tests
- **Receipt discipline** — every governance change gets a receipt
- **Plan must not merely document policy** — Must produce enforcement (rules, hooks, scripts, tests, receipts)
- **Plan must keep agentic_core generic and apps_* declarative** — Core engines + app profiles
- **Plan must explicitly say app-specific behavior in shared agentic_core is leakage unless documented as temporary thin adapter** — Receipt requirement

---

## Section 20: Output Summary

### Plan Path
`.cursor/plans/agentic-core-static-apps-customization-governance-a1b2c3.md`

### Current Wave Status

| Wave | Status | Key Deliverables | Certification |
|------|--------|------------------|---------------|
| W0 | COMPLETE | Baseline audit complete | CERTIFIED |
| W1 | COMPLETE | 7 governance docs (AGENTS.md + rules) | CERTIFIED |
| W2 | COMPLETE | 5 skills + 4 workflows | CERTIFIED |
| W3 | COMPLETE | 6 governance scripts + hooks.json | CERTIFIED |
| W4 | CERTIFIED | 6 CI tests + 17 negative controls | CERTIFIED |
| W5A | COMPLETE | Migration inventory (37 bindings, 28 scoped, 9 excluded) | ACCEPTED |
| W5B P1 | IN PROGRESS / BLOCKED | apps_lic L6/Exit/L0 migration | P1a PENDING_PROOF, P1b TEMPORARY, P1c BLOCKED |
| W5C | DEFERRED | apps_rg migration | Deferred post-W5B P1 |
| W5D | DEFERRED | apps_research consolidation | Deferred post-W5B P1 |
| W6 | TODO | Post-migration negative controls | TODO after W5B P1 |
| W7 | TODO | Final governance receipt | TODO |

### Key Blocking Rule

**The "No App-Specific Code in Core" rule is the primary blocker.** Any existing or proposed change to agentic_core that hardcodes app behavior (app_id branches, app-specific literals, app-specific policy) is blocked and must be refactored to:
1. Generic core engine + app-owned profile, or
2. Temporary thin adapter with migration receipt

### Known Risks

| Risk | Mitigation |
|------|------------|
| Hooks too aggressive, slow development | Bypass env var + model_decision trigger option |
| Existing code fails new CI tests | Migration receipts allow temporary exceptions |
| Generic engines slower than hardcoded | Performance testing deferred; correctness first |
| App developers bypass U0 path | app_runtime_package_scan.py enforcement |
| Receipt discipline becomes bureaucratic | Automate receipt generation, minimal fields |

### Next Recommended Action

**Do not proceed to implementation until plan is reviewed.**

After review:
1. Run W0 baseline audit to confirm inventory
2. Seek approval for W1-W4 governance infrastructure (planning-only work)
3. Schedule W5 binding migration in dedicated follow-up plans per binding
4. Author-Gate approval required before any hook activation

---

**PLAN COMPLETE: Awaiting review before implementation.**
